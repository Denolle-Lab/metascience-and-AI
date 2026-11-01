"""Synthetic extraction guards; no model, network, or matplotlib dependency."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from ai_readiness import plot_report


class PlotReportTests(unittest.TestCase):
    def report(self, n=4, k=1):
        return {"screen_labels_used_as_actual_use": False, "sample_binding_verified": False,
                "scope": "Synthetic fixture only", "years": [{"year": 2020, "reviewed_rows": 10,
                "metrics": {"ai_actual_use": {"reviewed_eligible_known_denominator": n,
                "reviewed_positive_count": k, "reviewed_subset_proportion": k / n if n else None,
                "unknown_or_inaccessible_labels": 6, "population_estimate": {"available": False}}}}]}

    def test_extraction_preserves_known_denominator(self):
        point = plot_report.extract_plot_data(self.report())[0]["points"][0]
        self.assertEqual((point["positive"], point["denominator"], point["proportion"], point["unknown"]), (1, 4, .25, 6))
        self.assertIsNone(point["ci"])

    def test_no_data_refuses_to_make_a_figure(self):
        with tempfile.TemporaryDirectory() as td:
            source = Path(td) / "empty.json"
            source.write_text(json.dumps(self.report(n=0, k=0)))
            with patch.object(plot_report, "render") as render, self.assertRaises(SystemExit) as stopped:
                plot_report.main([str(source), "--outprefix", str(Path(td) / "figure")])
            self.assertEqual(stopped.exception.code, 2)
            render.assert_not_called()
            self.assertEqual(list(Path(td).glob("figure.*")), [])

    def test_unavailable_population_is_not_plotted(self):
        r = self.report()
        r["years"][0]["metrics"]["ai_actual_use"]["population_estimate"].update(proportion=.9)
        self.assertEqual(len(plot_report.extract_plot_data(r)[0]["points"]), 1)

    def test_population_needs_binding_and_provided_ci_only(self):
        r = self.report()
        population = {"available": True, "proportion": .3, "eligible_population_total_estimate": 100,
                      "positive_population_total_estimate": 30, "ci95_normal_approximation": [.1, .5]}
        r["years"][0]["metrics"]["ai_actual_use"]["population_estimate"] = population
        with self.assertRaisesRegex(ValueError, "binding"):
            plot_report.extract_plot_data(r)
        r["sample_binding_verified"] = True
        point = plot_report.extract_plot_data(r)[0]["points"][1]
        self.assertEqual((point["positive"], point["denominator"], point["ci"]), (30., 100., [.1, .5]))
        population["ci95_normal_approximation"] = None
        self.assertIsNone(plot_report.extract_plot_data(r)[0]["points"][1]["ci"])

    def test_inconsistent_counts_and_intervals_reject(self):
        r = self.report()
        r["years"][0]["metrics"]["ai_actual_use"]["reviewed_subset_proportion"] = .8
        with self.assertRaisesRegex(ValueError, "supplied counts"):
            plot_report.extract_plot_data(r)
        r = self.report()
        r["sample_binding_verified"] = True
        r["years"][0]["metrics"]["ai_actual_use"]["population_estimate"] = {
            "available": True, "proportion": .3, "eligible_population_total_estimate": 100,
            "positive_population_total_estimate": 30, "ci95_normal_approximation": [.4, .5]}
        with self.assertRaisesRegex(ValueError, "does not enclose"):
            plot_report.extract_plot_data(r)

    def test_conditionals_keep_their_own_denominator(self):
        r = self.report()
        metric = copy.deepcopy(r["years"][0]["metrics"]["ai_actual_use"])
        metric.update(reviewed_eligible_known_denominator=2, reviewed_positive_count=1, reviewed_subset_proportion=.5)
        r["years"][0]["metrics"]["foundation_model_given_ai"] = metric
        self.assertEqual(len(plot_report.extract_plot_data(r)), 1)
        panels = plot_report.extract_plot_data(r, include_conditionals=True)
        conditional = next(p for p in panels if p["metric"] == "foundation_model_given_ai")
        self.assertEqual(conditional["points"][0]["denominator"], 2)
        self.assertIn("AI users", conditional["denominator_label"])

    def test_screening_and_missing_years_not_actual_data(self):
        r = self.report()
        r["screen_labels_used_as_actual_use"] = True
        with self.assertRaisesRegex(ValueError, "separating screening"):
            plot_report.extract_plot_data(r)
        r = self.report()
        r["years"].append({"year": 2022, "reviewed_rows": 0, "metrics": {}})
        points = plot_report.extract_plot_data(r)[0]["points"]
        self.assertEqual([point["year"] for point in points], [2020])


if __name__ == "__main__":
    unittest.main()
