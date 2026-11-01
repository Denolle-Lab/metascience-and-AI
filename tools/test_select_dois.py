"""Offline checks for exact citation balance, frozen cohorts, and snapshots."""
import contextlib
import copy
from collections import Counter
import io
import json
from pathlib import Path
import random
import re
import tempfile
import unittest
from unittest.mock import Mock, patch
from urllib.request import HTTPRedirectHandler

import select_dois as sd


def work(number, percentile, citations=None):
    return {
        "id": f"https://openalex.org/W{number}", "doi": f"https://doi.org/10.1111/test{number}",
        "title": f"Paper {number}", "publication_year": 2020, "publication_date": "2020-01-02",
        "type": "article", "cited_by_count": number if citations is None else citations,
        "citation_normalized_percentile": None if percentile is None else {"value": percentile},
        "fwci": None, "primary_topic": {"subfield": {"id": "https://openalex.org/subfields/1908", "display_name": "Geophysics"}},
        "primary_location": {"source": {"id": "https://openalex.org/S123", "display_name": "Test Journal"}},
        "counts_by_year": [{"year": 2025, "cited_by_count": 2}], "updated_date": "2026-10-22",
    }


class FakeOpenAlex:
    """An index fixture with API-like samples and population counts."""
    def __init__(self, works):
        self.works = copy.deepcopy(works)
        self.calls = []
        self.failed_ids = set()

    def get(self, endpoint, params):
        self.calls.append((endpoint, dict(params)))
        if endpoint.startswith("works/"):
            wid = endpoint.rsplit("/", 1)[-1]
            if wid in self.failed_ids:
                raise sd.OpenAlexError("fixture failure")
            return copy.deepcopy(next(w for w in self.works if w["id"].endswith("/" + wid)))
        eligible = self.works
        for bound in re.findall(r"citation_normalized_percentile.value:([^,]+)", params.get("filter", "")):
            def matches(w):
                value = (w.get("citation_normalized_percentile") or {}).get("value")
                if value is None:
                    return False
                if bound.startswith("<"):
                    return value < float(bound[1:])
                left, right = bound.split("-", 1)
                return (not left or value >= float(left)) and (not right or value <= float(right))
            eligible = list(filter(matches, eligible))
        total = len(eligible)
        if "sample" in params:
            selected = random.Random(params["seed"]).sample(eligible, min(params["sample"], total))
            count = len(selected)  # Actual API sample meta.count is sample size.
            offset = (params.get("page", 1) - 1) * params["per_page"]
        else:
            selected, count, offset = eligible, total, 0
            if "sort" in params:
                selected = sorted(selected, key=lambda w: w["cited_by_count"], reverse=True)
        rows = selected[offset:offset + params["per_page"]]
        return {"meta": {"count": count, "next_cursor": None}, "results": copy.deepcopy(rows)}


class SelectionChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)
        # Unequal pool sizes ensure weights cannot be mistaken for equal sampling.
        self.works = [work(1000 * b + i + 1, b / 10 + .05, 0 if b == 0 else None)
                      for b in range(10) for i in range(b + 3)]
        self.works.extend([work(99001, None), work(99002, None)])

    def tearDown(self):
        self.temp.cleanup()

    def args(self, *extra):
        return sd.parser().parse_args([
            "select", "--name", "example", "--n", "20", "--from", "2018-01-01", "--to", "2022-12-31",
            "--output", str(self.folder / "corpus"), *extra])

    def test_exact_equal_deciles_and_population_sampling_weights(self):
        args, client = self.args(), FakeOpenAlex(self.works)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(sd.select_cohort(args, client), 0)
        records = [json.loads(line) for line in (args.output / "example.jsonl").read_text().splitlines()]
        meta = json.loads((args.output / "example.meta.json").read_text())
        self.assertEqual(Counter(row["citation_decile"] for row in records), {i: 2 for i in range(1, 11)})
        self.assertEqual(meta["candidate_count"], len(self.works))
        self.assertEqual(meta["excluded_missing_or_out_of_range_percentile"], 2)
        for row in records:
            population = row["citation_decile"] + 2
            self.assertAlmostEqual(row["sampling_probability"], 2 / population)
            self.assertAlmostEqual(row["inverse_probability_weight"], population / 2)
        sampled = [p for _, p in client.calls if "sample" in p]
        self.assertEqual(len(sampled), 10)
        self.assertTrue(all(p["sample"] == 2 and "sort" not in p and "cursor" not in p for p in sampled))
        self.assertTrue(all("sample" not in p for _, p in client.calls[:11]))

    def test_boundaries_zero_tenths_and_one_each_belong_to_one_bin(self):
        fixtures = [work(100 + i, i / 10) for i in range(11)]
        client = FakeOpenAlex(fixtures)
        args = self.args("--n", "10")
        plan = sd.balanced_plan(args, sd.selection_params(args))
        counts = [sd.candidate_count(client, cell["params"]) for cell in plan]
        self.assertEqual(counts, [1] * 9 + [2])
        self.assertEqual(sum(counts), 11)

    def test_sparse_bin_aborts_before_any_sampling_or_output(self):
        fixtures = [w for w in self.works if (w["citation_normalized_percentile"] or {}).get("value") != .55]
        client, args = FakeOpenAlex(fixtures), self.args()
        with self.assertRaisesRegex(ValueError, "Decile 6: 0 eligible"):
            sd.select_cohort(args, client)
        self.assertFalse(args.output.exists())
        self.assertTrue(all("sample" not in params for _, params in client.calls))

    def test_nonmultiple_n_and_contradictory_top_decile_fail_early(self):
        for args in [self.args("--n", "21"), self.args("--top-10-percent")]:
            client = FakeOpenAlex(self.works)
            with self.assertRaises(ValueError):
                sd.select_cohort(args, client)
            self.assertFalse(client.calls)

    def test_random_paging_keeps_sample_seed_and_true_candidate_count(self):
        fixtures = [work(i + 1, .5) for i in range(220)]
        args = self.args("--method", "random", "--n", "105")
        client = FakeOpenAlex(fixtures)
        selected, total = sd.collect_selection(client, args, sd.selection_params(args))
        self.assertEqual((len(selected), total), (105, 220))
        pages = [p for _, p in client.calls if "sample" in p]
        self.assertEqual([p["page"] for p in pages], [1, 2])
        self.assertTrue(all(p["sample"] == 105 and p["per_page"] == 100 and p["seed"] == 2026 for p in pages))

    def test_keywords_journals_field_and_dates_are_combined(self):
        args = self.args("--query", '"machine learning" AND seismic', "--source", "S123", "--source", "S456",
                         "--field", "19", "--min-citations", "50", "--max-citations", "200")
        params = sd.selection_params(args)
        self.assertEqual(params["search.title_and_abstract"], '"machine learning" AND seismic')
        self.assertIn("primary_location.source.id:S123|S456", params["filter"])
        self.assertIn("primary_topic.field.id:19", params["filter"])
        self.assertIn("cited_by_count:50-200", params["filter"])
        self.assertIn("from_publication_date:2018-01-01", params["filter"])

    def test_nature_group_resolves_exact_six_journals_and_issns(self):
        args = self.args("--journal-set", "nature-earth-environment")
        journals = sd.journal_selection(args)
        self.assertEqual(journals["presets"], ["nature-earth-environment"])
        self.assertEqual([j["title"] for j in journals["journals"]], [
            "Nature Geoscience", "Nature Communications", "Communications Earth & Environment",
            "Nature Reviews Earth & Environment", "Nature Water", "Nature Sustainability"])
        self.assertEqual(journals["issns"], ["1752-0908", "2041-1723", "2662-4435", "2662-138X", "2731-6084", "2398-9629"])
        self.assertIn("primary_location.source.issn:" + "|".join(journals["issns"]), sd.selection_params(args)["filter"])
        self.assertEqual([j["launch_year"] for j in journals["journals"]], [2008, 2010, 2020, 2020, 2023, 2018])

    def test_individual_presets_and_manual_issns_union_and_deduplicate(self):
        args = self.args("--journal-set", "nature-geoscience", "--journal-set", "nature-water",
                         "--issn", "1752-0908", "--issn", "2662-138x")
        self.assertEqual(sd.journal_selection(args)["issns"], ["1752-0908", "2731-6084", "2662-138X"])
        self.assertIn("primary_location.source.issn:1752-0908|2731-6084|2662-138X", sd.selection_params(args)["filter"])
        self.assertNotIn("primary_location.source.id:", sd.selection_params(args)["filter"])

    def test_review_articles_are_opt_in_and_types_are_ored(self):
        self.assertIn("type:article,", sd.selection_params(self.args())["filter"])
        self.assertIn("type:review,", sd.selection_params(self.args("--work-type", "review"))["filter"])
        args = self.args("--work-type", "article", "--work-type", "review", "--work-type", "article")
        self.assertIn("type:article|review,", sd.selection_params(args)["filter"])
        self.assertEqual(sd.work_types(args), ["article", "review"])

    def test_source_id_filters_reject_issn_or_preset_combinations(self):
        for flags in [("--issn", "1752-0908"), ("--journal-set", "nature-earth-environment")]:
            with self.assertRaisesRegex(ValueError, "Use --source or"):
                sd.selection_params(self.args("--source", "S123", *flags))

    def test_invalid_issns_and_unknown_presets_are_rejected(self):
        for invalid in ["17520908", "1752-0909", "1752-0908|2662-4435"]:
            with self.assertRaisesRegex(ValueError, "Invalid ISSN"):
                sd.selection_params(self.args("--issn", invalid))
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            self.args("--journal-set", "nature-unknown")
        args = self.args()
        args.journal_set = ["nature-unknown"]
        with self.assertRaisesRegex(ValueError, "Unknown journal preset"):
            sd.selection_params(args)

    def test_nature_dry_run_records_explicit_journals_and_article_types(self):
        args = self.args("--journal-set", "nature-earth-environment", "--work-type", "article",
                         "--work-type", "review", "--dry-run")
        output = io.StringIO()
        with patch.object(sd, "api_key") as key, contextlib.redirect_stdout(output):
            self.assertEqual(sd.select_cohort(args), 0)
        key.assert_not_called()
        plan = json.loads(output.getvalue())
        self.assertEqual(plan["journal_selection"], sd.journal_selection(args))
        self.assertEqual(plan["work_types"], ["article", "review"])
        self.assertEqual(len(plan["balanced_plan"]), 10)
        self.assertTrue(all("type:article|review," in cell["params"]["filter"] for cell in plan["balanced_plan"]))
        self.assertFalse(args.output.exists())

    def test_saved_selection_retains_resolved_journals_types_and_query(self):
        args = self.args("--journal-set", "nature-geoscience", "--work-type", "article", "--work-type", "review")
        with contextlib.redirect_stdout(io.StringIO()):
            sd.select_cohort(args, FakeOpenAlex(self.works))
        metadata = json.loads((args.output / "example.meta.json").read_text())
        self.assertEqual(metadata["journal_selection"], sd.journal_selection(args))
        self.assertEqual(metadata["work_types"], ["article", "review"])
        self.assertEqual(metadata["query"], sd.selection_params(args))
        self.assertEqual(metadata["journal_selection"]["pooling"], "union")
        self.assertFalse(metadata["journal_selection"]["equal_journal_quotas"])

    def test_availability_short_bin_reports_all_counts_without_sampling_or_writes(self):
        fixtures = [w for w in self.works if (w["citation_normalized_percentile"] or {}).get("value") != .55]
        args = self.args("--availability-only")
        client, output = FakeOpenAlex(fixtures), io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(sd.select_cohort(args, client), 0)
        self.assertEqual(len(client.calls), 11)
        self.assertTrue(all("sample" not in p and "seed" not in p and "sort" not in p for _, p in client.calls))
        self.assertTrue(all(p["per_page"] == 1 and p["select"] == "id" for _, p in client.calls))
        self.assertIn("Decile 6: 0 eligible; 2 required", output.getvalue())
        self.assertIn("Missing/out-of-range percentile: 2", output.getvalue())
        self.assertIn("Exact citation-balanced sample of 20 possible: no", output.getvalue())
        self.assertFalse(args.output.exists())

    def test_availability_sufficient_pool_reports_possible_and_ignores_existing_cohort(self):
        args = self.args("--availability-only")
        args.output.mkdir()
        existing = args.output / "example.jsonl"
        existing.write_text("frozen cohort\n")
        client, output = FakeOpenAlex(self.works), io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(sd.select_cohort(args, client), 0)
        self.assertIn("Exact citation-balanced sample of 20 possible: yes", output.getvalue())
        self.assertEqual(existing.read_text(), "frozen cohort\n")
        self.assertEqual(list(args.output.iterdir()), [existing])
        self.assertEqual(len(client.calls), 11)
        self.assertTrue(all("sample" not in p for _, p in client.calls))

    def test_availability_other_methods_only_count_candidates(self):
        for method in ("random", "most-cited"):
            args = self.args("--method", method, "--availability-only", "--n", "100")
            client, output = FakeOpenAlex(self.works), io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(sd.select_cohort(args, client), 0)
            self.assertEqual(len(client.calls), 1)
            self.assertTrue(all("sample" not in p and "seed" not in p and "sort" not in p for _, p in client.calls))
            self.assertIn("Sample of 100 possible: no", output.getvalue())
            self.assertFalse(args.output.exists())

    def test_availability_dry_run_has_no_network_key_or_output_destinations(self):
        args = self.args("--availability-only", "--dry-run")
        output = io.StringIO()
        with patch.object(sd, "api_key") as key, patch.object(sd, "candidate_count") as count, contextlib.redirect_stdout(output):
            self.assertEqual(sd.select_cohort(args), 0)
        key.assert_not_called()
        count.assert_not_called()
        plan = json.loads(output.getvalue())
        self.assertTrue(plan["availability_only"])
        self.assertEqual(plan["outputs"], {})
        self.assertEqual(plan["pagination"], "none")
        for params in [plan["params"], *(cell["params"] for cell in plan["balanced_plan"])]:
            self.assertNotIn("sample", params)
            self.assertNotIn("seed", params)
            self.assertEqual(params["per_page"], 1)
        self.assertFalse(args.output.exists())

    def test_null_metrics_preserved_and_zero_percentile_valid(self):
        record = sd.work_record(work(1, 0, citations=0), "date")
        self.assertEqual(record["cnp"], 0)
        self.assertEqual(record["cited_by_count"], 0)
        self.assertIsNone(record["fwci"])
        self.assertIsNone(sd.work_record(work(2, None), "date")["cnp"])

    def test_refresh_appends_history_without_reselecting_or_changing_manifest(self):
        args, client = self.args(), FakeOpenAlex(self.works)
        with contextlib.redirect_stdout(io.StringIO()):
            sd.select_cohort(args, client)
        path = args.output / "example.jsonl"
        frozen = path.read_bytes()
        selected = [json.loads(line) for line in frozen.splitlines()]
        client.failed_ids.add(sd.work_id(selected[0]["id"]))
        for item in client.works:
            item["cited_by_count"] += 5
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            status = sd.refresh_cohort(sd.parser().parse_args(["refresh", str(path)]), client)
        self.assertEqual(status, 1)
        self.assertEqual(path.read_bytes(), frozen)
        history = [json.loads(line) for line in (args.output / "example.citations.jsonl").read_text().splitlines()]
        self.assertEqual(len(history), 40)
        self.assertEqual(history[20]["status"], "error")
        self.assertNotIn("cited_by_count", history[20])
        self.assertEqual(history[21]["cited_by_count"], history[1]["cited_by_count"] + 5)
        self.assertEqual(history[21]["publication_date"], "2020-01-02")

    def test_existing_cohort_cannot_be_overwritten(self):
        args, client = self.args(), FakeOpenAlex(self.works)
        with contextlib.redirect_stdout(io.StringIO()):
            sd.select_cohort(args, client)
        calls = len(client.calls)
        with self.assertRaisesRegex(ValueError, "already exists"):
            sd.select_cohort(args, client)
        self.assertEqual(len(client.calls), calls)

    def test_dry_run_needs_no_key_and_sends_no_requests(self):
        args = self.args("--dry-run")
        with patch.object(sd, "api_key") as key, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(sd.select_cohort(args), 0)
        key.assert_not_called()
        self.assertFalse(args.output.exists())

    def test_api_token_is_never_in_url_or_redirect(self):
        response = io.BytesIO(b'{"meta":{"count":0},"results":[]}')
        with patch.object(sd.urllib.request, "urlopen", return_value=response) as request, patch.object(sd.time, "sleep"):
            sd.OpenAlexClient("secret-token").get("works", {"per_page": 1})
        req = request.call_args.args[0]
        self.assertNotIn("secret-token", req.full_url)
        self.assertEqual(req.get_header("Authorization"), "Bearer secret-token")
        redirected = HTTPRedirectHandler().redirect_request(req, None, 302, "Found", {}, "https://elsewhere.example/resource")
        self.assertIsNone(redirected.get_header("Authorization"))

    def test_partial_api_count_rejected(self):
        client = Mock()
        client.get.return_value = {"meta": {"count": 999, "timed_out": True}, "results": []}
        with self.assertRaises(sd.OpenAlexError):
            sd.select_cohort(self.args(), client)


if __name__ == "__main__":
    unittest.main()
