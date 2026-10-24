"""Protect inference from substituted paper IDs. All records synthetic."""
import unittest
from ai_readiness import core as s

class SampleBinding(unittest.TestCase):
 def design(self):
  return {'strata':[{'sampling_stratum':'h','year':2020,'N':10,'n':2}],
   'sample_ids_sha256':s.paper_ids_digest(['a','b']),
   'sample_assignments':[{'paper_id':x,'year':2020,'sampling_stratum':'h','inclusion_probability':.2} for x in ['a','b']]}
 def test_substitute_in_same_stratum_rejected(self):
  r={'paper_id':'c','year':2020,'sampling_stratum':'h','inclusion_probability':.2}
  with self.assertRaisesRegex(ValueError,'not in the saved'):
   s.validate_annotation_design([r],self.design())
 def test_changed_year_or_probability_rejected(self):
  r=dict(self.design()['sample_assignments'][0]);r['year']=2021
  with self.assertRaisesRegex(ValueError,'year/stratum'):
   s.validate_annotation_design([r],self.design())
  r['year']=2020;r['inclusion_probability']=.5
  with self.assertRaisesRegex(ValueError,'probability differs'):
   s.validate_annotation_design([r],self.design())
 def test_missing_rows_allowed_but_estimation_remains_incomplete(self):
  d=self.design();r=d['sample_assignments'][0]
  self.assertTrue(s.validate_annotation_design([r],d))
 def test_legacy_design_not_bound(self):
  self.assertFalse(s.validate_annotation_design([],{'strata':[]}))
 def test_digest_or_sample_count_mismatch_rejected(self):
  d=self.design();d['sample_ids_sha256']='wrong'
  with self.assertRaisesRegex(ValueError,'digest'):
   s.validate_annotation_design([],d)
 def test_fm_incompatible_with_dl_no(self):
  import test_pipeline
  r=test_pipeline.PipelineTests().reviewed('a',[],'yes')
  r.update(foundation_model_actual_use='yes',deep_learning_actual_use='no')
  with self.assertRaisesRegex(ValueError,'deep-learning'):
   s.validate_review(r)

if __name__=='__main__':unittest.main()
