"""Offline study-level tests: fixed parameters, quotas, transactions and follow-up."""
from collections import Counter
import contextlib
import copy
import io
import json
from pathlib import Path
import random
import re
import tempfile
import unittest
from unittest.mock import patch

import nature_dataset as nd
import select_dois as sd


class IndexFixture:
    def __init__(self):
        self.calls, self.works = [], []
        self.fail_source = None
        self.wrong_source = False
        self.failed_ids = set()
        for journal_index, (slug, journal) in enumerate(sd.JOURNAL_PRESETS.items()):
            for band in range(10):
                for item in range(3):
                    number = (journal_index + 1) * 100000 + band * 100 + item
                    self.works.append({
                        "id": f"https://openalex.org/W{number}", "doi": f"https://doi.org/10.1038/test-{number}",
                        "title": f"Climate paper {number}", "publication_year": 2024,
                        "publication_date": "2024-05-06", "type": "review" if item == 0 else "article",
                        "cited_by_count": band * 30 + item,
                        "citation_normalized_percentile": {"value": band / 10 + .05},
                        "fwci": None, "counts_by_year": [{"year": 2025, "cited_by_count": 2}],
                        "updated_date": "2026-10-22", "primary_topic": {
                            "field": {"id": "https://openalex.org/fields/19"},
                            "subfield": {"id": "https://openalex.org/subfields/1908", "display_name": "Geophysics"}},
                        "primary_location": {"source": {"id": f"https://openalex.org/S{journal_index+100}",
                            "display_name": journal["title"], "issn": [journal["issn"]]}},
                    })

    def get(self, endpoint, params):
        self.calls.append((endpoint, copy.deepcopy(params)))
        if endpoint.startswith("works/"):
            wid = endpoint.rsplit("/", 1)[-1]
            if wid in self.failed_ids:
                raise sd.OpenAlexError("Fixture refresh failed")
            return copy.deepcopy(next(w for w in self.works if w["id"].endswith("/" + wid)))
        source = re.search(r"primary_location.source.issn:([^,]+)", params["filter"]).group(1)
        eligible = [w for w in self.works if source in w["primary_location"]["source"]["issn"]]
        for bound in re.findall(r"citation_normalized_percentile.value:([^,]+)", params["filter"]):
            def matches(w):
                v = (w.get("citation_normalized_percentile") or {}).get("value")
                if v is None:
                    return False
                if bound.startswith("<"):
                    return v < float(bound[1:])
                low, high = bound.split("-", 1)
                return (not low or v >= float(low)) and (not high or v <= float(high))
            eligible = list(filter(matches, eligible))
        count = len(eligible)
        if "sample" in params:
            if source == self.fail_source:
                raise sd.OpenAlexError("Fixture late failure")
            selected = random.Random(params["seed"]).sample(eligible, min(params["sample"], count))
            count = len(selected)
            start = (params.get("page", 1) - 1) * params["per_page"]
            selected = copy.deepcopy(selected[start:start + params["per_page"]])
            if self.wrong_source:
                for work in selected:
                    work["primary_location"]["source"]["issn"] = ["0000-0000"]
        else:
            selected = copy.deepcopy(eligible[:params["per_page"]])
        return {"meta": {"count": count}, "results": selected}


class StudyChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name).resolve()
        self.config = self.folder / "config.json"
        self.protocol = {
            "name": "tiny-study", "journals": list(sd.JOURNAL_PRESETS), "n_per_journal": 10,
            "publication_start": "2023-01-01", "publication_end": "2025-12-31",
            "query": '"climate change" AND water', "fields": ["19"], "subfields": [],
            "work_types": ["article", "review"], "seed": 2026,
        }
        self.config.write_text(json.dumps(self.protocol))
        self.output = self.folder / "studies"
        self.study = self.output / "tiny-study"
        self.client = IndexFixture()

    def tearDown(self):
        self.temp.cleanup()

    def args(self, command="select", *extra):
        return nd.parser().parse_args([command, "--config", str(self.config), "--output-root", str(self.output), *extra])

    def select(self):
        with contextlib.redirect_stdout(io.StringIO()):
            return nd.select(self.args(), self.client)

    def test_plan_overrides_are_explicit_and_need_no_network(self):
        args = self.args("plan", "--query", "ecosystem OR hydrology", "--from", "2020-01-01", "--n-per-journal", "20")
        with patch.object(sd, "api_key") as key, contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(nd.plan(args), 0)
        plan = json.loads(out.getvalue())
        self.assertEqual(plan["protocol"]["query"], "ecosystem OR hydrology")
        self.assertEqual(plan["protocol"]["publication_start"], "2020-01-01")
        self.assertEqual(plan["total_sample_size"], 120)
        self.assertEqual(plan["network_requests"], 0)
        self.assertNotIn("params", plan["journal_plans"][0])
        self.assertEqual(len(plan["citation_bins"]), 10)
        key.assert_not_called()
        self.assertFalse(self.output.exists())

    def test_detailed_plan_exposes_reproducible_api_queries_on_request(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            nd.plan(self.args("plan", "--show-api-queries"))
        plan = json.loads(out.getvalue())
        self.assertEqual(len(plan["journal_plans"]), 6)
        self.assertEqual(plan["journal_plans"][0]["params"]["search.title_and_abstract"], self.protocol["query"])
        self.assertEqual(len(plan["journal_plans"][0]["citation_bins"]), 10)

    def test_all_six_preflight_before_sampling_and_exact_crossed_quotas(self):
        self.assertEqual(self.select(), 0)
        metadata, records = nd.verify_study(self.study)
        self.assertEqual(len(records), 60)
        self.assertTrue(all("sample" not in p for _, p in self.client.calls[:66]))
        self.assertTrue(all("sample" in p for _, p in self.client.calls[66:]))
        self.assertEqual(len(self.client.calls), 126)  # 66 counts +60 singleton samples.
        self.assertEqual(Counter(r["journal_slug"] for r in records), {s: 10 for s in self.protocol["journals"]})
        self.assertEqual(Counter((r["journal_slug"], r["citation_decile"]) for r in records),
                         {(s, b): 1 for s in self.protocol["journals"] for b in range(1, 11)})
        self.assertEqual(metadata["protocol"], self.protocol)
        for record in records:
            self.assertIn(sd.JOURNAL_PRESETS[record["journal_slug"]]["issn"], record["source_issns"])
        for _, params in self.client.calls:
            self.assertEqual(params["search.title_and_abstract"], self.protocol["query"])
            self.assertIn("from_publication_date:2023-01-01", params["filter"])
            self.assertIn("to_publication_date:2025-12-31", params["filter"])

    def test_shortage_in_one_journal_prevents_every_sample_and_final_output(self):
        last_issn = list(sd.JOURNAL_PRESETS.values())[-1]["issn"]
        self.client.works = [w for w in self.client.works if not (
            last_issn in w["primary_location"]["source"]["issn"] and w["citation_normalized_percentile"]["value"] < .1)]
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(ValueError, "cannot fill"):
            nd.select(self.args(), self.client)
        self.assertFalse(self.output.exists())
        self.assertFalse(any("sample" in params for _, params in self.client.calls))

    def test_late_api_failure_cleans_temporary_study_and_lock(self):
        self.client.fail_source = list(sd.JOURNAL_PRESETS.values())[-1]["issn"]
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(sd.OpenAlexError):
            nd.select(self.args(), self.client)
        self.assertFalse(self.study.exists())
        self.assertEqual(list(self.output.iterdir()), [])

    def test_actual_journal_identity_is_verified_before_publish(self):
        self.client.wrong_source = True
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(ValueError):
            nd.select(self.args(), self.client)
        self.assertFalse(self.study.exists())
        self.assertEqual(list(self.output.iterdir()), [])

    def test_duplicate_doi_across_journals_cannot_publish_study(self):
        for work in self.client.works:
            band = work["citation_normalized_percentile"]["value"]
            work["doi"] = f"https://doi.org/10.1038/shared-band-{band}"
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(ValueError, "duplicate"):
            nd.select(self.args(), self.client)
        self.assertFalse(self.study.exists())
        self.assertEqual(list(self.output.iterdir()), [])

    def test_availability_returns_shortage_but_never_creates_files(self):
        self.client.works = []
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(nd.availability(self.args("availability"), self.client), 1)
        self.assertFalse(self.output.exists())
        self.assertEqual(len(self.client.calls), 66)
        self.assertFalse(any("sample" in p for _, p in self.client.calls))

    def test_existing_study_refused_before_any_new_api_calls(self):
        self.select()
        calls = len(self.client.calls)
        with self.assertRaisesRegex(ValueError, "already exists"):
            nd.select(self.args(), self.client)
        self.assertEqual(len(self.client.calls), calls)

    def test_credential_keys_and_invalid_dates_or_quotas_rejected(self):
        for change in [{"api_key": "SECRET"}, {"n_per_journal": 11},
                       {"publication_start": "2026-01-01"}, {"publication_end": "2025-02-30"}]:
            with self.subTest(change=change), self.assertRaises(ValueError) as exc:
                nd.validate_protocol({**self.protocol, **change})
            self.assertNotIn("SECRET", str(exc.exception))

    def test_download_uses_one_combined_list_and_one_request_budget(self):
        self.select()
        args = nd.parser().parse_args(["download", "--study", str(self.study), "--service", "tdm", "--max-requests", "17", "--limit", "2"])
        with patch.object(nd.dn, "main", return_value=0) as download:
            self.assertEqual(nd.download(args), 0)
        download.assert_called_once()
        argv = download.call_args.args[0]
        self.assertEqual(argv[0], str(self.study / "dois.txt"))
        self.assertEqual(len(Path(argv[0]).read_text().splitlines()), 60)
        self.assertEqual(argv[argv.index("--max-requests") + 1], "17")
        self.assertEqual(argv[argv.index("--output") + 1], str(self.study / "xml"))

    def test_tampered_doi_list_blocked_before_download(self):
        self.select()
        with (self.study / "dois.txt").open("a") as handle:
            handle.write("10.1038/unselected-paper\n")
        args = nd.parser().parse_args(["download", "--study", str(self.study)])
        with patch.object(nd.dn, "main") as download, self.assertRaisesRegex(ValueError, "integrity"):
            nd.download(args)
        download.assert_not_called()

    def test_refresh_keeps_frozen_manifest_and_appends_current_counts(self):
        self.select()
        before = (self.study / "manifest.jsonl").read_bytes()
        first_id = json.loads(before.splitlines()[0])["id"].rsplit("/", 1)[-1]
        self.client.failed_ids.add(first_id)
        for work in self.client.works:
            work["cited_by_count"] += 7
        args = nd.parser().parse_args(["refresh", "--study", str(self.study)])
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(nd.refresh(args, self.client), 1)
        self.assertEqual((self.study / "manifest.jsonl").read_bytes(), before)
        history = [json.loads(line) for line in (self.study / "manifest.citations.jsonl").read_text().splitlines()]
        self.assertEqual(len(history), 120)
        self.assertEqual(history[60]["status"], "error")
        self.assertNotIn("cited_by_count", history[60])
        self.assertEqual(history[61]["cited_by_count"], history[1]["cited_by_count"] + 7)
        nd.verify_study(self.study)


if __name__ == "__main__":
    unittest.main()
