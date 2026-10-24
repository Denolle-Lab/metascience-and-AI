"""Synthetic integration fixtures only; no retrieval, model use, or actual study claims."""
import argparse, copy, json, math, socket, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from ai_readiness import adapter, core
from ai_readiness.__main__ import comparison, main
import test_pipeline

class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def write(self,name,value,jsonl=False):
        p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True)
        (core.write_jsonl(p,value) if jsonl else core.atomic_json(p,value));return p
    def rows(self):
        return [{'key':'w1','id':'https://openalex.org/W1','doi':'10.9999/a','year':2020,'title':'Synthetic transformer GNSS seismic'},
                {'key':'w2','id':'https://openalex.org/W2','doi':'10.9999/b','year':2021,'title':'Synthetic observation only'}]
    def imported(self,rows=None):
        source=self.write('cohort.jsonl',rows or self.rows(),True);run=self.root/'run'
        adapter.import_metadata(argparse.Namespace(input=str(source),out=str(run),cohort='fixture',ontology='earth_measurement_families'))
        return source,run
    def randommeta(self,source):
        return self.write('cohort.meta.json',{'method':'random','selected_count':2,'candidate_count':10,'query':{'filter':'type:article'}})
    def test_import_corpus_uses_doi_identity_not_fake_openalex(self):
        rows=[{'key':'smith2020','doi':'https://doi.org/10.9999/A','year':2020,'title':'Fixture'}]
        source,run=self.imported(rows);w=core.read_jsonl(run/'works.jsonl')[0]
        self.assertEqual(w['id'],'doi:10.9999/a');self.assertFalse(core.read_json(run/'import.json')['frame_complete'])
    def test_duplicate_doi_key_and_bad_year_rejected(self):
        rows=self.rows();rows[1]['doi']='https://doi.org/10.9999/A'
        with self.assertRaisesRegex(ValueError,'Duplicate'):adapter.normalize_rows(rows)
        rows=self.rows();rows[1]['key']='w1'
        with self.assertRaisesRegex(ValueError,'Duplicate legacy'):adapter.normalize_rows(rows)
        rows=self.rows();rows[0]['year']=True
        with self.assertRaisesRegex(ValueError,'integer'):adapter.normalize_rows(rows)
    def test_import_existing_folder_is_not_overwritten(self):
        source,run=self.imported()
        with self.assertRaisesRegex(ValueError,'not overwritten'):adapter.import_metadata(argparse.Namespace(input=str(source),out=str(run),cohort='x',ontology='x'))
    def test_random_design_binds_exact_original_ids(self):
        source,run=self.imported();meta=self.randommeta(source);out=self.root/'design.json'
        d=adapter.bind_selection(argparse.Namespace(run=run,metadata=meta,out=out))
        self.assertEqual(d['strata'][0]['N'],10);self.assertEqual(d['sample_assignments'][0]['inclusion_probability'],.2)
        self.assertIn('no manifest SHA',d['provenance']['legacy_draw_proof_limitation'])
    def test_optional_random_weights_cannot_be_silently_replaced(self):
        rows=self.rows();rows[0]['sampling_probability']=.9
        with self.assertRaisesRegex(ValueError,'random-sample probability'):
            adapter._selector_design(adapter.normalize_rows(rows),{'method':'random','selected_count':2,'candidate_count':10})
        rows=self.rows();rows[0]['inverse_probability_weight']=2
        with self.assertRaisesRegex(ValueError,'random-sample weight'):
            adapter._selector_design(adapter.normalize_rows(rows),{'method':'random','selected_count':2,'candidate_count':10})
    def test_wrong_metadata_same_counts_rejected(self):
        source,run=self.imported();meta=self.write('unrelated.meta.json',{'method':'random','selected_count':2,'candidate_count':10})
        with self.assertRaisesRegex(ValueError,'basename sibling'):adapter.bind_selection(argparse.Namespace(run=run,metadata=meta,out=self.root/'d'))
    def test_legacy_and_ranked_are_not_probability_samples(self):
        source,run=self.imported()
        for meta in [{'pool':100,'drawn':2},{'method':'most-cited','selected_count':2,'candidate_count':100}]:
            path=self.write('cohort.meta.json',meta)
            with self.assertRaises(ValueError):adapter.bind_selection(argparse.Namespace(run=run,metadata=path,out=self.root/'d'))
    def test_changed_original_or_import_rejected(self):
        source,run=self.imported();meta=self.randommeta(source)
        source.write_text(source.read_text()+'\n')
        with self.assertRaisesRegex(ValueError,'original selector manifest'):adapter.bind_selection(argparse.Namespace(run=run,metadata=meta,out=self.root/'d'))
    def test_attach_cannot_subset_or_change_year(self):
        rows=[{'paper_id':'a','year':2020}];design={'sample_assignments':[{'paper_id':'a','year':2020,'sampling_stratum':'s','inclusion_probability':.5},{'paper_id':'b','year':2021,'sampling_stratum':'s','inclusion_probability':.5}]}
        inp=self.write('screen.jsonl',rows,True);d=self.write('design.json',design)
        with self.assertRaisesRegex(ValueError,'every original'):adapter.attach_design(argparse.Namespace(input=inp,design=d,out=self.root/'out'))
    def test_bridge_keeps_api_codings_unreviewed_and_ignores_review_steps(self):
        source,run=self.imported();pdf=self.root/'paper.pdf';pdf.write_bytes(b'synthetic not a real PDF')
        queue=self.write('queue.json',{'w1':{'doi':'10.9999/a','status':'have','file':str(pdf)}})
        codings=self.root/'codings';codings.mkdir()
        self.write('codings/w1.json',{'key':'w1','doi':'10.9999/a','coder':'api','codebook_version':'1.2.0','sequences':[{'kind':'final_paper','source_document':'fixture','steps':[{'node':'O','mode':'simulation','page':'2','quote':'Synthetic','move':'cited'}]},{'kind':'review','steps':[{'mode':'observation'}]}]})
        out=self.root/'bridge.jsonl'
        with patch.object(socket,'socket',side_effect=AssertionError('Network forbidden')):
            result=adapter.bridge(argparse.Namespace(run=run,repo=self.root,queue=queue,codings=codings,assets=None,out=out,semantic_manifest=self.root/'semantic.jsonl'))
        r=result[0];self.assertEqual(r['review_status'],'not_reviewed');self.assertEqual(r['ai_actual_use'],'uncertain');self.assertIsNone(r['actual_modality_families'])
        self.assertEqual(len(r['semantic_candidates']),1);self.assertFalse(r['semantic_candidates'][0]['actual_use_evidence'])
        self.assertTrue(r['semantic_candidates'][0]['mention_only_or_inherited'])
    def test_bridge_quarantines_wrong_doi_and_missing_pdf_is_not_have(self):
        source,run=self.imported();queue=self.write('queue.json',{'w1':{'doi':'10.9999/WRONG','status':'have','file':'missing.pdf'},'w2':{'doi':'10.9999/b','status':'have','file':'missing.pdf'}})
        out=self.root/'b.jsonl'
        r=adapter.bridge(argparse.Namespace(run=run,repo=self.root,queue=queue,codings=None,assets=None,out=out,semantic_manifest=None))
        self.assertEqual(len(r),1);self.assertEqual(r[0]['full_text_status'],'not_verified');self.assertEqual(len(core.read_json(str(out)+'.receipt.json')['quarantined']),1)
    def test_asset_manifest_reference_never_becomes_review(self):
        source,run=self.imported();asset=self.root/'article.xml';asset.write_text('<article/>')
        assets=self.write('assets.jsonl',[{'doi':'10.9999/a','status':'existing','path':str(asset)}],True)
        r=adapter.bridge(argparse.Namespace(run=run,repo=self.root,queue=None,codings=None,assets=assets,out=self.root/'b',semantic_manifest=None))
        self.assertTrue(r[0]['local_assets'][0]['usable_candidate']);self.assertEqual(r[0]['review_status'],'not_reviewed')
    def test_balanced_bins_validate_real_counts_weights(self):
        rows=[];bins=[]
        for i in range(10):
            rows.append({'id':f'W{i}','doi':f'10.9999/{i}','year':2020+i%2,'cnp':(i+.5)/10,'citation_decile':i+1,'sampling_probability':.1,'inverse_probability_weight':10})
            bins.append({'decile':i+1,'lower':i/10,'upper':(i+1)/10,'upper_inclusive':i==9,'quota':1,'eligible_count':10,'selected_count':1,'sampling_probability':.1})
        meta={'method':'balanced','candidate_count':100,'selected_count':10,'citation_bins':bins,'excluded_missing_or_out_of_range_percentile':0}
        works=adapter.normalize_rows(rows);a,s=adapter._selector_design(works,meta)
        self.assertEqual(len(a),10);self.assertTrue(all(h['year'] is None for h in s))
        rows[0]['sampling_probability']=.5
        with self.assertRaisesRegex(ValueError,'probability/weight'):adapter._selector_design(adapter.normalize_rows(rows),meta)
    def reviewed(self,paper,year,ai,stratum='s',prob=.25):
        r=test_pipeline.PipelineTests().reviewed(paper,[],ai,stratum,prob);r['year']=year;return r
    def test_annual_domain_keeps_all_original_strata(self):
        rows=[self.reviewed('a',2020,'yes','h1',.5),self.reviewed('b',2021,'no','h1',.5),self.reviewed('c',2020,'no','h2',.1),self.reviewed('d',2021,'yes','h2',.1)]
        strata=[{'sampling_stratum':'h1','N':4,'n':2,'year':None},{'sampling_stratum':'h2','N':20,'n':2,'year':None}]
        assignments=[{k:r[k] for k in ['paper_id','year','sampling_stratum','inclusion_probability']} for r in rows]
        d=adapter.bound_design(assignments,strata,'fixture','f','earth_measurement_families',{})
        result=core.make_report(rows,d);annual=result['years'][0]['metrics']['ai_actual_use']['population_estimate']
        self.assertAlmostEqual(annual['proportion'],1/6);self.assertAlmostEqual(annual['eligible_population_total_estimate'],12)
        # Year2020 contributes estimated2 positives/(2+10), not unweighted1/2.
        self.assertAlmostEqual(result['pooled']['metrics']['ai_actual_use']['population_estimate']['proportion'],.5)
    def test_missing_other_year_draw_suppresses_annual_domain(self):
        rows=[self.reviewed('a',2020,'yes'),self.reviewed('b',2021,'no')]
        a=[{k:r[k] for k in ['paper_id','year','sampling_stratum','inclusion_probability']} for r in rows]
        d=adapter.bound_design(a,[{'sampling_stratum':'s','N':8,'n':2,'year':None}],'f','f','x',{})
        result=core.make_report(rows[:1],d)
        self.assertFalse(result['years'][0]['metrics']['ai_actual_use']['population_estimate']['available'])
    def test_training_and_author_hypothesis_evidence_gates(self):
        r=self.reviewed('a',2020,'yes');r['training_regimes']=['self_supervised']
        with self.assertRaisesRegex(ValueError,'supporting evidence'):core.validate_review(r)
        r['evidence'][0]['supports'].append('training_regime:self_supervised');self.assertTrue(core.validate_review(r))
        r['adoption_explanations']=[{'origin':'explicit_author_statement','reason':'labels','evidence_ids':[]}]
        with self.assertRaisesRegex(ValueError,'locatable evidence IDs'):core.validate_review(r)
        r['adoption_explanations'][0]['origin']='assessor_hypothesis';self.assertTrue(core.validate_review(r))
    def test_comparison_without_protocol_is_not_authorized_claim(self):
        e=self.write('e.json',{'modality_ontology':'earth_measurement_families','years':[]})
        c=self.write('c.json',{'modality_ontology':'cs_information_channels','years':[]})
        out=self.root/'comparison.json';comparison(argparse.Namespace(earth=e,cs=c,protocol=None,out=out))
        r=core.read_json(out);self.assertFalse(r['comparison_ready']);self.assertFalse(r['modality_definitions_comparable'])
    def test_cli_end_to_end_templates_produce_no_actual_results(self):
        source,run=self.imported();meta=self.randommeta(source)
        paths={n:self.root/n for n in ['screen.jsonl','design.json','sample.jsonl','blank.jsonl','report.json']}
        commands=[['screen','--input',str(run/'works.jsonl'),'--out',str(paths['screen.jsonl'])],
            ['bind-selection','--run',str(run),'--metadata',str(meta),'--out',str(paths['design.json'])],
            ['attach-design','--input',str(paths['screen.jsonl']),'--design',str(paths['design.json']),'--out',str(paths['sample.jsonl'])],
            ['template','--input',str(paths['sample.jsonl']),'--out',str(paths['blank.jsonl'])],
            ['report','--input',str(paths['blank.jsonl']),'--design',str(paths['design.json']),'--out',str(paths['report.json'])]]
        with patch.object(socket,'socket',side_effect=AssertionError('Network forbidden')):
            for command in commands:self.assertEqual(main(command),0)
        report=core.read_json(paths['report.json'])
        self.assertEqual(report['human_reviewed_full_text_rows'],0)
        self.assertEqual(report['cohort_id'],'fixture')
        self.assertTrue(report['sample_binding_verified'])
        self.assertTrue(all(not m['population_estimate']['available'] for m in report['pooled']['metrics'].values()))
        self.assertEqual(main(commands[-1]),2)  # report output is protected too.
    def test_nature_parent_protocol_and_manifest_hashes_checked(self):
        source,run=self.imported();protocol={'name':'fixture','journals':['synthetic']}
        # Preserve the input's raw hash while supplying legitimate journal labels.
        rows=self.rows()
        for r in rows:r['journal_slug']='synthetic'
        source.write_text(''.join(json.dumps(r)+'\n' for r in rows))
        # Reimport into a fresh run, since the original imported hash must be immutable.
        run=self.root/'nature-run'
        adapter.import_metadata(argparse.Namespace(input=source,out=run,cohort='nature-fixture',ontology='earth_measurement_families'))
        canonical=json.dumps(protocol,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
        metadata={'schema_version':1,'protocol':protocol,'protocol_sha256':__import__('hashlib').sha256(canonical).hexdigest(),
            'selected_count':2,'sha256':{'manifest.jsonl':adapter.sha(source)}}
        meta=self.write('study.json',metadata)
        self.write('cohorts/synthetic.meta.json',{'method':'random','selected_count':2,'candidate_count':10})
        d=adapter.bind_selection(argparse.Namespace(run=run,metadata=meta,out=self.root/'nature-design.json'))
        self.assertEqual(d['strata'][0]['sampling_stratum'],'synthetic|random')
        metadata['protocol_sha256']='wrong';core.atomic_json(meta,metadata)
        with self.assertRaisesRegex(ValueError,'protocol hash'):adapter.bind_selection(argparse.Namespace(run=run,metadata=meta,out=self.root/'bad-design.json'))
    def test_different_cohort_ontologies_cannot_be_silently_pooled(self):
        a=self.reviewed('a',2020,'no');a.update(cohort_id='earth',modality_ontology='earth_measurement_families')
        b=self.reviewed('b',2020,'no');b.update(cohort_id='cs',modality_ontology='cs_information_channels')
        with self.assertRaisesRegex(ValueError,'separate reports'):core.make_report([a,b])
        a['actual_modality_families']=['cs_text_language']
        with self.assertRaisesRegex(ValueError,'CS information'):core.make_report([a])
    def test_cli_exposes_no_retrieval_or_execution_commands(self):
        with self.assertRaises(SystemExit):main(['harvest'])

if __name__=='__main__':unittest.main()
