"""Synthetic evidence guards for added DL/FM measurements; no live data."""
import unittest
from ai_readiness import core as study
import test_pipeline

class TrainingLabels(unittest.TestCase):
    def row(self):
        return test_pipeline.PipelineTests().reviewed('synthetic', ['seismic_elastic'], 'yes')
    def test_legacy_is_unknown_not_zero(self):
        r=self.row()
        for name in ['deep_learning_actual_use','foundation_model_actual_use','foundation_model_pretraining']:
            self.assertIsNone(study.metric(r,name))
    def test_fm_use_is_not_pretraining(self):
        r=self.row();r.update(foundation_model_actual_use='yes',foundation_model_pretraining='no')
        self.assertEqual(study.metric(r,'foundation_model_actual_use'),(1,1))
        self.assertEqual(study.metric(r,'foundation_model_pretraining'),(0,1))
    def test_extended_positive_needs_specific_evidence(self):
        r=self.row();r['deep_learning_actual_use']='yes'
        with self.assertRaisesRegex(ValueError,'lack evidence'):
            study.validate_review(r)
        r['evidence'][0]['supports'].append('deep_learning_actual_use')
        self.assertTrue(study.validate_review(r))
    def test_pretraining_requires_fm_use(self):
        r=self.row();r.update(foundation_model_pretraining='yes',foundation_model_actual_use='no')
        with self.assertRaisesRegex(ValueError,'requires verified foundation-model'):
            study.validate_review(r)
    def test_conditional_denominator_excludes_non_ai(self):
        r=self.row();r['ai_actual_use']='no';r['deep_learning_actual_use']='no'
        self.assertEqual(study.metric(r,'deep_learning_given_ai'),(0,0))
        r['ai_actual_use']='yes'
        self.assertEqual(study.metric(r,'deep_learning_given_ai'),(0,1))
    def test_new_unknown_suppresses_population_estimate(self):
        rows=[self.row(),self.row()];rows[1]['paper_id']='second'
        result=study.estimate_stratified(rows,[{'sampling_stratum':'s','N':4,'n':2}],'foundation_model_actual_use')
        self.assertFalse(result['available'])

if __name__=='__main__':unittest.main()
