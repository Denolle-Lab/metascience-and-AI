"""Local-only adapters for existing corpus, selector, JATS/PDF and coding files.

Never imports legacy acquisition/coder modules: those may load keys or clients.
"""
from __future__ import annotations
from collections import Counter
import hashlib
import csv
import json
import math
from pathlib import Path
import re
from . import core


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def records(path):
    p = Path(path)
    if p.suffix == '.jsonl':
        return core.read_jsonl(p)
    value = core.read_json(p)
    if isinstance(value, dict) and isinstance(value.get('results'), list):
        return value['results']
    if isinstance(value, list):
        return value
    raise ValueError('Metadata must be JSONL, a JSON array, or an OpenAlex results envelope.')


def normalize_rows(rows):
    """Normalize known manifest formats; do not invent text or OpenAlex identities."""
    works, seen_ids, seen_dois, seen_keys = [], set(), set(), set()
    for row in rows:
        doi = core.normalized_doi(row.get('doi'))
        original_id = row.get('id') or row.get('paper_id')
        # DOI identities allow ID-less corpus.py output without fabricated W IDs.
        wid = original_id or ('doi:' + doi if doi else None)
        if not wid or (doi and not re.match(r'^10\.\d{4,9}/\S+$', doi)):
            raise ValueError('Each metadata record needs a valid DOI or stable original paper ID.')
        if wid in seen_ids or (doi and doi in seen_dois):
            raise ValueError('Duplicate/aliased paper identities need adjudication before import.')
        key = row.get('key')
        if key and key in seen_keys:
            raise ValueError('Duplicate legacy keys need adjudication before import.')
        year = row.get('publication_year', row.get('year'))
        if isinstance(year, bool) or not isinstance(year, int):
            raise ValueError('Each paper needs an integer publication year.')
        source = ((row.get('primary_location') or {}).get('source') or {})
        sid = source.get('id') or row.get('source_id')
        abstract_index = row.get('abstract_inverted_index')
        if abstract_index is None and row.get('abstract'):
            abstract_index = {}
            for i, token in enumerate(row['abstract'].split()):
                abstract_index.setdefault(token, []).append(i)
        works.append({'id': wid, 'doi': doi, 'title': row.get('title') or row.get('display_name') or '',
            'publication_year': year, 'abstract_inverted_index': abstract_index,
            'primary_location': {'source': {'id': sid, 'display_name': source.get('display_name') or row.get('venue')}},
            'legacy_key': key, 'original_record': row})
        seen_ids.add(wid)
        if doi: seen_dois.add(doi)
        if key: seen_keys.add(key)
    return works


def import_metadata(args):
    target = Path(args.out)
    if target.exists():
        raise ValueError('Choose a new import output folder; frozen runs are not overwritten.')
    works = normalize_rows(records(args.input))
    for work in works: work.update(cohort_id=args.cohort, modality_ontology=args.ontology)
    target.mkdir(parents=True)
    core.write_jsonl(target/'works.jsonl', works)
    receipt = {'schema_version': 1, 'cohort_id': args.cohort,
        'modality_ontology': args.ontology, 'input_path': str(Path(args.input).resolve()),
        'input_sha256': sha(args.input), 'unique_works': len(works),
        'paper_ids_sha256': core.paper_ids_digest([r['id'] for r in works]),
        'works_jsonl_sha256': sha(target/'works.jsonl'), 'frame_complete': False,
        'scope': 'Imported existing metadata/cohort only. No probability design inferred from corpus.py or selected counts.',
        'network_requests': 0, 'model_calls': 0}
    core.atomic_json(target/'import.json', receipt)
    return receipt


def bound_design(assignments, strata, scope, cohort, ontology, provenance):
    design = {'design': 'stratified_simple_random_without_replacement', 'frame_complete': True,
        'cohort_id': cohort, 'modality_ontology': ontology, 'scope': scope,
        'sample_assignments': assignments, 'strata': strata,
        'sample_ids_sha256': core.paper_ids_digest([r['paper_id'] for r in assignments]),
        'provenance': provenance}
    core.validate_annotation_design(assignments, design)
    return design


def _selector_design(works, meta, prefix=''):
    """Translate original random/balanced selector weights; never post-stratify years."""
    if meta.get('method') not in ('random', 'balanced'):
        raise ValueError('Only documented random/balanced select_dois samples support design binding; ranked/legacy cohorts are descriptive.')
    if meta.get('selected_count') != len(works):
        raise ValueError('Selector metadata selected_count does not match imported identities.')
    # The selected eligibility population (possibly query-restricted) remains the target.
    N = meta.get('candidate_count')
    if isinstance(N, bool) or not isinstance(N, int) or N < len(works):
        raise ValueError('Invalid selector candidate population count.')
    strata, assignment = [], []
    if meta['method'] == 'random':
        n = len(works)
        if not n: raise ValueError('Cannot bind an empty cohort.')
        for work in works:
            record=work['original_record']
            if 'sampling_probability' in record and not math.isclose(record.get('sampling_probability') or 0,n/N,rel_tol=1e-9):
                raise ValueError('Recorded random-sample probability contradicts selection counts.')
            if 'inverse_probability_weight' in record and not math.isclose(record.get('inverse_probability_weight') or 0,N/n,rel_tol=1e-9):
                raise ValueError('Recorded random-sample weight contradicts selection counts.')
        name = prefix+'random'
        strata.append({'sampling_stratum': name, 'N': N, 'n': n, 'year': None})
        assignment = [{'paper_id': w['id'], 'year': w['publication_year'], 'sampling_stratum': name,
                       'inclusion_probability': n/N} for w in works]
    else:
        bins = meta.get('citation_bins')
        if not isinstance(bins, list) or len(bins) != 10 or {b.get('decile') for b in bins} != set(range(1,11)):
            raise ValueError('Balanced design requires all ten original disjoint citation bins.')
        if sum(b['eligible_count'] for b in bins) + (meta.get('excluded_missing_or_out_of_range_percentile') or 0) != N:
            raise ValueError('Citation-bin counts do not reconcile with candidate_count.')
        for b in bins:
            group = [w for w in works if w['original_record'].get('citation_decile') == b['decile']]
            n, total = b.get('quota'), b.get('eligible_count')
            if not isinstance(n,int) or not isinstance(total,int) or not 1 <= n <= total or len(group)!=n or b.get('selected_count')!=n:
                raise ValueError('Citation-bin draw/count mismatch.')
            prob = n/total
            if not math.isclose(b.get('sampling_probability') or 0,prob,rel_tol=1e-9):
                raise ValueError('Bin inclusion probability differs from original counts.')
            name = prefix+f"citation_decile_{b['decile']}"
            strata.append({'sampling_stratum':name,'N':total,'n':n,'year':None})
            for w in group:
                record = w['original_record']
                if not math.isclose(record.get('sampling_probability') or 0,prob,rel_tol=1e-9) or not math.isclose(record.get('inverse_probability_weight') or 0,1/prob,rel_tol=1e-9):
                    raise ValueError('Manifest probability/weight contradicts original selection counts.')
                cnp = record.get('cnp')
                if cnp is None: cnp=(record.get('citation_normalized_percentile') or {}).get('value')
                if not isinstance(cnp,(int,float)) or not float(b['lower']) <= cnp or not (cnp <= float(b['upper']) if b['upper_inclusive'] else cnp < float(b['upper'])):
                    raise ValueError('A selected work lies outside its recorded citation bin.')
                assignment.append({'paper_id':w['id'],'year':w['publication_year'],'sampling_stratum':name,'inclusion_probability':prob})
    return assignment,strata


def bind_selection(args):
    imported = Path(args.run)
    receipt = core.read_json(imported/'import.json')
    works = core.read_jsonl(imported/'works.jsonl')
    if sha(imported/'works.jsonl') != receipt['works_jsonl_sha256']:
        raise ValueError('Imported works changed after freezing.')
    source = Path(args.metadata)
    meta = core.read_json(source)
    provenance = {'metadata_path':str(source.resolve()),'metadata_sha256':sha(source),
        'import_receipt_sha256':sha(imported/'import.json'), 'design_source':'existing selector metadata',
        'assumption':'OpenAlex random selection within recorded bins is treated as SRS without replacement; indexing errors and changing API frames are not sampling uncertainty.'}
    if 'method' in meta:
        original=Path(receipt['input_path'])
        if source.resolve()!=original.with_suffix('.meta.json').resolve():
            raise ValueError('Selector metadata must be the original cohort basename sibling (.jsonl / .meta.json); unrelated same-size cohorts cannot be paired.')
        if not original.is_file() or sha(original)!=receipt['input_sha256']:
            raise ValueError('The original selector manifest changed or is unavailable for binding.')
        provenance['legacy_draw_proof_limitation']='Legacy select_dois metadata contains no manifest SHA. Sibling pairing, current import hashes, bin membership and weights guard accidental pairing; they cannot establish a historic cryptographic draw proof.'
        assignments,strata = _selector_design(works,meta)
        query = meta.get('query')
    elif meta.get('schema_version')==1 and isinstance(meta.get('protocol'),dict):
        protocol_bytes=json.dumps(meta['protocol'],ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
        if hashlib.sha256(protocol_bytes).hexdigest()!=meta.get('protocol_sha256'):
            raise ValueError('Nature frozen protocol hash mismatch.')
        if meta.get('sha256',{}).get('manifest.jsonl') != receipt['input_sha256']:
            raise ValueError('Nature study manifest hash does not match the imported original.')
        if meta.get('selected_count') != len(works): raise ValueError('Nature selected_count mismatch.')
        assignments,strata=[],[]
        groups=Counter(w['original_record'].get('journal_slug') for w in works)
        journals=meta['protocol'].get('journals') or []
        if set(groups)!=set(journals): raise ValueError('Nature journal groups mismatch protocol.')
        for slug in journals:
            child=source.parent/'cohorts'/f'{slug}.meta.json'
            if not child.is_file(): raise ValueError('Nature child selection metadata is required.')
            a,s=_selector_design([w for w in works if w['original_record'].get('journal_slug')==slug],core.read_json(child),prefix=slug+'|')
            assignments.extend(a);strata.extend(s)
            provenance.setdefault('child_metadata',[]).append({'path':str(child.resolve()),'sha256':sha(child)})
        query=meta['protocol']
    else:
        raise ValueError('Legacy corpus metadata cannot establish a probability design. Use descriptive reporting or a complete verified frame.')
    scope='Frozen selector eligibility frame only; citation-balanced populations exclude missing/out-of-range normalized percentiles. Original query: '+json.dumps(query,sort_keys=True)
    design=bound_design(assignments,strata,scope,receipt['cohort_id'],receipt['modality_ontology'],provenance)
    core.atomic_json(args.out,design)
    return design


def attach_design(args):
    """Join saved sample assignments to screens without changing the original draw."""
    rows=core.read_jsonl(args.input); design=core.read_json(args.design)
    lookup={r['paper_id']:r for r in design['sample_assignments']}
    if set(lookup)!={r['paper_id'] for r in rows} or len(rows)!=len(lookup):
        raise ValueError('Screens must match every original sampled identity exactly; no replacement/subsetting.')
    result=[]
    for r in rows:
        a=lookup[r['paper_id']]
        if r['year']!=a['year']: raise ValueError('Screen year differs from saved draw.')
        result.append(dict(r, sampling_stratum=a['sampling_stratum'],inclusion_probability=a['inclusion_probability']))
    core.write_jsonl(args.out,result)


def _local_file(value, root):
    if not value: return None
    p=Path(value).expanduser()
    if not p.is_absolute(): p=root/p
    return {'path':str(p.resolve()),'exists':p.is_file(),'sha256':sha(p) if p.is_file() else None}


def bridge(args):
    """Produce sidecars compatible with current queue keys; never change queue/codings."""
    run=Path(args.run); works=core.read_jsonl(run/'works.jsonl')
    receipt=core.read_json(run/'import.json')
    if sha(run/'works.jsonl')!=receipt['works_jsonl_sha256']: raise ValueError('Frozen imported works were modified.')
    root=Path(args.repo).resolve(); queue=core.read_json(args.queue) if args.queue else {}
    assets={}
    if getattr(args,'assets',None):
        assetpath=Path(args.assets)
        if assetpath.suffix.lower()=='.csv':
            with assetpath.open(encoding='utf-8-sig',newline='') as f: assetrows=list(csv.DictReader(f))
        else: assetrows=records(assetpath)
        # Downloader histories can contain retries. Retain every matching local asset record.
        for asset in assetrows:
            d=core.normalized_doi(asset.get('doi'))
            if d: assets.setdefault(d,[]).append(asset)
    output=[]; quarantined=[]; semantic_manifest=[]
    for w in works:
        key=w.get('legacy_key'); doi=core.normalized_doi(w.get('doi'))
        q=queue.get(key,{}) if key else {}
        if q and core.normalized_doi(q.get('doi'))!=doi:
            quarantined.append({'paper_id':w['id'],'legacy_key':key,'reason':'Download queue DOI mismatch or absent DOI; no join attempted.'});continue
        pdf=_local_file(q.get('file'),root)
        have=bool(q.get('status')=='have' and pdf and pdf['exists'])
        record={'paper_id':w['id'],'doi':doi,'legacy_key':key,'title':w['title'],'year':w['publication_year'],
            'review_status':'not_reviewed','ai_actual_use':'uncertain','actual_modality_families':None,
            'queue_status':q.get('status'),'local_pdf':pdf,'full_text_status':'available_local_unreviewed' if have else 'not_verified',
            'semantic_candidates':[],'screen_interpretation':'Candidates require human full-text review; semantic inquiry codes do not establish actual use.'}
        if args.codings and key:
            cp=Path(args.codings)/(key+'.json')
            if cp.is_file():
                coding=core.read_json(cp)
                if coding.get('key')!=key or core.normalized_doi(coding.get('doi'))!=doi:
                    quarantined.append({'paper_id':w['id'],'legacy_key':key,'reason':'Coding DOI/key mismatch.'});continue
                record['coding_source']={'path':str(cp.resolve()),'sha256':sha(cp),'coder':coding.get('coder'),'codebook_version':coding.get('codebook_version'),'pages_convention':coding.get('pages_convention')}
                for sequence in coding.get('sequences',[]):
                    if sequence.get('kind')!='final_paper':continue
                    for step in sequence.get('steps',[]):
                        record['semantic_candidates'].append({'source_document':sequence.get('source_document'),**{k:step.get(k) for k in ['node','mode','action','page','quote','move','trigger']},'actual_use_evidence':False,'mention_only_or_inherited':step.get('move') in ['cited','inherited','declined']})
                record['imports_for_review']=coding.get('imports',[])
        record['local_assets']=[]
        for asset in assets.get(doi,[]):
            ref=_local_file(asset.get('path'),root)
            record['local_assets'].append({'status':asset.get('status'),'file':ref,
                'usable_candidate':bool(asset.get('status') in ('downloaded','existing','have') and ref and ref['exists']),
                'actual_use_evidence':False})
        if have and key:
            semantic_manifest.append({'key':key,'doi':doi,'title':w['title'],'year':w['publication_year'],'paper_id':w['id']})
        output.append(record)
    core.write_jsonl(args.out,output)
    core.atomic_json(str(args.out)+'.receipt.json',{'network_requests':0,'model_calls':0,'queue_rows':len(output),'quarantined':quarantined,'import_sha256':sha(run/'import.json')})
    if args.semantic_manifest:core.write_jsonl(args.semantic_manifest,semantic_manifest)
    return output
