import argparse, contextlib, hashlib, io, json
from pathlib import Path
import tempfile, unittest
from ai_readiness import core as study

class PipelineTests(unittest.TestCase):
    def setUp(self):
            self.works = study.read_jsonl(Path(__file__).parent / "fixtures" / "works.jsonl")

    def reviewed(self, paper_id, families, ai="no", stratum="s", probability=0.5):
            labels = list(families) + (["ai_actual_use"] if ai == "yes" else [])
            return {"paper_id": paper_id, "year": 2020, "review_status": "reviewed", "reviewer_id": "fixture-reviewer",
                    "evidence_level": "full_text", "full_text_status": "available_open", "eligibility": "yes", "actual_modality_families": families,
                    "ai_actual_use": ai, "fusion_labels": [], "sampling_stratum": stratum,
                    "inclusion_probability": probability, "evidence": [{"url": "https://example.org/fixture", "section_or_page": "Methods",
                    "excerpt": "Synthetic fixture evidence only.", "supports": labels}]}

    def test_dedup_connects_id_and_normalized_doi_transitively(self):
            works = [{"id": "W1", "doi": "https://doi.org/10.TEST/A"}, {"id": "W2", "doi": "doi:10.test/a"}, {"id": "W2", "doi": "10.test/b"}, {"id": "W3", "doi": "10.test/c"}]
            result = study.deduplicate(works)
            self.assertEqual(len(result), 2)
            self.assertIn(["W1", "W2"], [row["dedup_openalex_ids"] for row in result])

    def test_screen_mentions_never_become_actual_use(self):
            row = study.screen_work(self.works[0])
            self.assertTrue(row["ai_candidate"])
            self.assertEqual(set(row["modality_candidates"]), {"seismic_elastic", "geodetic_position_displacement"})
            self.assertIsNone(row["actual_ai_use"])
            self.assertIsNone(row["actual_modality_use"])
            self.assertTrue(row["screen_only"])
            evidence = row["ai_evidence"][0]
            self.assertEqual(row[evidence["field"]][evidence["start"]:evidence["end"]], evidence["matched_text"])

    def test_missing_abstract_not_negative_actual_label(self):
            row = study.screen_work(self.works[1])
            self.assertEqual(row["abstract_status"], "missing")
            self.assertIsNone(study.annotation_template(row)["actual_modality_families"])

    def test_abstract_index_reconstruction_and_conflict(self):
            self.assertEqual(study.reconstruct_abstract({"B": [1], "A": [0]}), "A B")
            with self.assertRaises(ValueError):
                study.reconstruct_abstract({"B": [0], "A": [0]})

    def test_sampling_includes_negatives_and_is_order_independent(self):
            rows = [study.screen_work(work) for work in self.works]
            sample, strata = study.sample_rows(rows, 2, "seed")
            repeat, _ = study.sample_rows(list(reversed(rows)), 2, "seed")
            self.assertEqual(sample, repeat)
            self.assertTrue(any(not row["ai_candidate"] for row in sample))
            self.assertTrue(all(0 < row["inclusion_probability"] <= 1 for row in sample))

    def test_sampler_rejects_positive_only_or_duplicate_screen_with_complete_manifest(self):
            with tempfile.TemporaryDirectory() as temporary:
                temporary = Path(temporary)
                works_path, screen_path = temporary / "works.jsonl", temporary / "screen.jsonl"
                manifest_path = temporary / "manifest.json"
                study.write_jsonl(works_path, self.works)
                study.screen(argparse.Namespace(input=str(works_path), out=str(screen_path)))
                rows = study.read_jsonl(screen_path)
                manifest = {"frame_complete": True, "unique_works": len(self.works),
                            "paper_ids_sha256": study.paper_ids_digest([work["id"] for work in self.works]),
                            "works_jsonl_sha256": hashlib.sha256(works_path.read_bytes()).hexdigest()}
                study.atomic_json(manifest_path, manifest)
                study.validate_sample_frame(rows, manifest)
                positives = [row for row in rows if row["ai_candidate"]]
                study.write_jsonl(screen_path, positives)
                args = argparse.Namespace(input=str(screen_path), manifest=str(manifest_path), out=str(temporary / "sample.jsonl"), design=str(temporary / "design.json"), n_per_stratum=2, seed="fixture")
                with self.assertRaisesRegex(ValueError, "count/unique IDs"):
                    study.sample(args)
                with self.assertRaisesRegex(ValueError, "count/unique IDs"):
                    study.validate_sample_frame([rows[0], rows[0], rows[1]], manifest)

    def test_sampler_rejects_replaced_ids_or_wrong_source_hash(self):
            rows = [dict(study.screen_work(work), source_works_jsonl_sha256="original-hash") for work in self.works]
            manifest = {"unique_works": len(rows), "paper_ids_sha256": study.paper_ids_digest([row["paper_id"] for row in rows]), "works_jsonl_sha256": "original-hash"}
            rows[0]["source_works_jsonl_sha256"] = "other-file"
            with self.assertRaisesRegex(ValueError, "provenance"):
                study.validate_sample_frame(rows, manifest)
            rows[0]["source_works_jsonl_sha256"] = "original-hash"
            rows[0]["paper_id"] = "https://openalex.org/W999999999"
            with self.assertRaisesRegex(ValueError, "paper IDs differ"):
                study.validate_sample_frame(rows, manifest)

    def test_positive_labels_need_locatable_evidence(self):
            row = self.reviewed("p1", ["seismic_elastic"], "yes")
            self.assertTrue(study.validate_review(row))
            row["evidence"] = []
            with self.assertRaises(ValueError):
                study.validate_review(row)

    def test_full_text_review_cannot_contradict_access_status(self):
            for status in ["unavailable", "inaccessible", "parse_failed", "partial", "not_attempted", None]:
                row = self.reviewed("p1", [])
                row["full_text_status"] = status
                with self.subTest(status=status), self.assertRaisesRegex(ValueError, "full_text_status"):
                    study.validate_review(row)

    def test_uncertain_is_not_reclassified_as_no(self):
            row = self.reviewed("p1", ["seismic_elastic"])
            row["ai_actual_use"] = "uncertain"
            self.assertIsNone(study.metric(row, "ai_actual_use"))
            result = study.estimate_stratified([row, self.reviewed("p2", [])], [{"sampling_stratum": "s", "N": 4, "n": 2}], "ai_actual_use")
            self.assertFalse(result["available"])

    def test_design_estimator_with_known_synthetic_values(self):
            rows = [self.reviewed("p1", ["seismic_elastic", "geodetic_position_displacement"]), self.reviewed("p2", ["seismic_elastic"])]
            result = study.estimate_stratified(rows, [{"sampling_stratum": "s", "N": 4, "n": 2}], "multimodal_actual_use")
            self.assertEqual(result["proportion"], 0.5)
            self.assertEqual(result["eligible_population_total_estimate"], 4)
            self.assertAlmostEqual(result["standard_error"], (0.125) ** 0.5)

    def test_incomplete_review_blocks_population_estimate(self):
            result = study.estimate_stratified([self.reviewed("p1", [])], [{"sampling_stratum": "s", "N": 4, "n": 2}], "multimodal_actual_use")
            self.assertFalse(result["available"])

    def test_conditional_metrics_use_correct_denominators(self):
            multi_ai = self.reviewed("p1", ["seismic_elastic", "geodetic_position_displacement"], "yes")
            one_ai = self.reviewed("p2", ["seismic_elastic"], "yes")
            multi_no_ai = self.reviewed("p3", ["seismic_elastic", "geodetic_position_displacement"], "no")
            self.assertEqual([study.metric(r, "multimodal_given_ai") for r in [multi_ai, one_ai, multi_no_ai]], [(1, 1), (0, 1), (0, 0)])
            self.assertEqual([study.metric(r, "ai_given_multimodal") for r in [multi_ai, one_ai, multi_no_ai]], [(1, 1), (0, 0), (0, 1)])

    def test_boundary_non_census_does_not_claim_zero_width_ci(self):
            result = study.estimate_stratified([self.reviewed("p1", []), self.reviewed("p2", [])], [{"sampling_stratum": "s", "N": 4, "n": 2}], "multimodal_actual_use")
            self.assertTrue(result["available"])
            self.assertIsNone(result["ci95_normal_approximation"])

    def test_template_only_report_has_no_actual_use_counts(self):
            with tempfile.TemporaryDirectory() as temporary:
                path = Path(temporary) / "annotations.jsonl"
                output = Path(temporary) / "report.json"
                study.write_jsonl(path, [study.annotation_template(study.screen_work(work)) for work in self.works])
                with contextlib.redirect_stdout(io.StringIO()):
                    study.report(argparse.Namespace(input=str(path), out=str(output), design=None))
                report = study.read_json(output)
                self.assertEqual(report["human_reviewed_full_text_rows"], 0)
                self.assertIsNone(report["years"][0]["metrics"]["ai_actual_use"]["reviewed_subset_proportion"])

    def test_report_preserves_year_with_all_annotations_missing(self):
            with tempfile.TemporaryDirectory() as temporary:
                temporary = Path(temporary)
                input_path, design_path, output = temporary / "annotations.jsonl", temporary / "design.json", temporary / "report.json"
                rows = [self.reviewed("p1", [], probability=1), self.reviewed("p2", [], probability=1)]
                study.write_jsonl(input_path, rows)
                study.atomic_json(design_path, {"design": "stratified_simple_random_without_replacement", "frame_complete": True,
                    "strata": [{"sampling_stratum": "s", "year": 2020, "N": 2, "n": 2}, {"sampling_stratum": "missing-year", "year": 2021, "N": 4, "n": 2}]})
                with contextlib.redirect_stdout(io.StringIO()):
                    study.report(argparse.Namespace(input=str(input_path), out=str(output), design=str(design_path)))
                report = study.read_json(output)
                self.assertEqual([year["year"] for year in report["years"]], [2020, 2021])
                missing = report["years"][1]
                self.assertEqual(missing["annotation_rows"], 0)
                self.assertEqual(missing["missing_annotation_rows"], 2)
                self.assertTrue(all(not result["population_estimate"]["available"] for result in missing["metrics"].values()))
