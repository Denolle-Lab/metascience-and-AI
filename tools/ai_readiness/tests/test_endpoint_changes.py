import copy,unittest
from ai_readiness import core
import test_pipeline

class EndpointTests(unittest.TestCase):
 def report(self):
  a=test_pipeline.PipelineTests().reviewed('a',[],'no');a['year']=2020
  b=test_pipeline.PipelineTests().reviewed('b',[],'yes');b['year']=2021
  return core.make_report([a,b])
 def protocol(self):
  return {'years':[2020,2021],'comparability':{k:{'confirmed':True,'evidence':'Synthetic audit only.'} for k in ['complete_publication_years','identical_source_frame','matched_eligibility','matched_codebook','comparable_full_text_coverage']}}
 def test_no_protocol_no_growth_claim(self):self.assertFalse(core.endpoint_changes(self.report())['available'])
 def test_zero_baseline_has_no_finite_ratio(self):
  r=core.endpoint_changes(self.report(),self.protocol())['metrics']['ai_actual_use']
  self.assertEqual(r['percentage_point_change'],100);self.assertIsNone(r['last_to_first_ratio']);self.assertIn('descriptive',r['basis'])
 def test_missing_year_or_partial_review_suppresses(self):
  r=self.report();p=self.protocol();p['years']=[2019,2021]
  self.assertFalse(core.endpoint_changes(r,p)['available'])
  p=self.protocol();r['years'][0]['annotation_rows']=2
  self.assertFalse(core.endpoint_changes(r,p)['available'])
 def test_unresolved_frame_gate_suppresses(self):
  p=self.protocol();p['comparability']['identical_source_frame']['confirmed']=False
  self.assertFalse(core.endpoint_changes(self.report(),p)['available'])
 def test_two_verified_population_points_take_precedence(self):
  r=self.report();r['sample_binding_verified']=True
  for year,value in zip(r['years'],[.2,.3]):year['metrics']['ai_actual_use']['population_estimate']={'available':True,'proportion':value}
  out=core.endpoint_changes(r,self.protocol())['metrics']['ai_actual_use']
  self.assertAlmostEqual(out['percentage_point_change'],10);self.assertAlmostEqual(out['last_to_first_ratio'],1.5);self.assertIn('population',out['basis'])

if __name__=='__main__':unittest.main()
