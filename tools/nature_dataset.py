#!/usr/bin/env python3
"""Freeze equal-size, citation-balanced Nature journal datasets and download JATS XML.

Python 3.10+, standard library only. Run ``nature_dataset.py plan --config ...``
first; selection requires OpenAlex, and XML retrieval uses separate publisher keys.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import redirect_stdout
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
from typing import Any

import download_nature as dn
import select_dois as sd

DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "private" / "datasets"
PROTOCOL_KEYS = {"name", "journals", "n_per_journal", "publication_start", "publication_end",
                 "query", "fields", "subfields", "work_types", "seed"}
DEFAULTS = {"name": "nature-balanced", "journals": list(sd.JOURNAL_PRESETS),
            "n_per_journal": 100, "query": "", "fields": [], "subfields": [],
            "work_types": ["article", "review"], "seed": 2026}
CITATION_NOTE = ("Citation percentiles are OpenAlex values observed at selection time, normalized "
                 "by publication year, work type and subfield. The publication end date does not "
                 "set a historical citation cutoff. Each journal has ten equal citation deciles.")


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def validate_protocol(value: dict) -> dict:
    if not isinstance(value, dict):
        raise ValueError("The configuration must be a JSON object.")
    if set(value) - PROTOCOL_KEYS:
        raise ValueError("Configuration contains unknown keys; only study parameters are allowed. "
                         "Keep all API credentials outside configuration files.")
    p = {**DEFAULTS, **value}
    if not isinstance(p["name"], str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,49}", p["name"]):
        raise ValueError("Study name must use 1–50 letters, digits, underscores or hyphens.")
    n = p["n_per_journal"]
    if type(n) is not int or not 10 <= n <= 10000 or n % 10:
        raise ValueError("n_per_journal must be an integer from 10 to 10000 divisible by 10.")
    if type(p["seed"]) is not int or not 0 <= p["seed"] <= 2147480000:
        raise ValueError("seed must be a nonnegative integer no larger than 2147480000.")
    for key in ("publication_start", "publication_end"):
        if key not in p or not isinstance(p[key], str):
            raise ValueError("Set publication_start and publication_end (YYYY-MM-DD), or --from and --to.")
        try:
            sd.iso_date(p[key])
        except argparse.ArgumentTypeError:
            raise ValueError(f"{key} must use YYYY-MM-DD.") from None
    if p["publication_start"] > p["publication_end"]:
        raise ValueError("Publication start must be on or before publication end.")
    if not isinstance(p["query"], str):
        raise ValueError("query must be a keyword expression string.")
    for key in ("journals", "fields", "subfields", "work_types"):
        if not isinstance(p[key], list) or any(not isinstance(v, str) for v in p[key]):
            raise ValueError(f"{key} must be a list of strings.")
        p[key] = list(dict.fromkeys(p[key]))
    if not p["journals"] or any(slug not in sd.JOURNAL_PRESETS for slug in p["journals"]):
        raise ValueError("journals must contain one or more individual Nature journal preset slugs; see --help.")
    if not p["work_types"] or any(t not in {"article", "review"} for t in p["work_types"]):
        raise ValueError("work_types must contain article, review, or both.")
    for key, kind in (("fields", "field"), ("subfields", "subfield")):
        p[key] = list(dict.fromkeys(sd.identifier(v, kind) for v in p[key]))
    return p


def load_protocol(args: argparse.Namespace) -> dict:
    value: dict = {}
    if getattr(args, "config", None):
        value = json.loads(Path(args.config).read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError("The configuration must be a JSON object.")
    overrides = {"query": "query", "date_from": "publication_start", "date_to": "publication_end",
                 "n_per_journal": "n_per_journal", "journal": "journals"}
    for option, key in overrides.items():
        override = getattr(args, option, None)
        if override is not None:
            value[key] = override
    return validate_protocol(value)


def journal_args(protocol: dict, slug: str, output: Path) -> argparse.Namespace:
    # Parse through the existing selector so its future defaults are not omitted.
    argv = ["select", "--name", slug, "--journal-set", slug,
            "--n", str(protocol["n_per_journal"]), "--from", protocol["publication_start"],
            "--to", protocol["publication_end"], "--method", "balanced", "--seed", str(protocol["seed"]),
            "--output", str(output)]
    if protocol["query"]:
        argv += ["--query", protocol["query"]]
    for key, flag in (("fields", "--field"), ("subfields", "--subfield"), ("work_types", "--work-type")):
        for value in protocol[key]:
            argv += [flag, value]
    return sd.parser().parse_args(argv)


class CountCache:
    """Share preflight counts across selection without caching sampled works."""
    def __init__(self, client):
        self.client, self.cache = client, {}
        self.source_issns: dict[str, list[str]] = {}

    def get(self, endpoint: str, params: dict | None = None):
        count = endpoint == "works" and params and params.get("select") == "id" and params.get("per_page") == 1
        key = (endpoint, canonical(params)) if count else None
        if key is not None and key in self.cache:
            return self.cache[key]
        result = self.client.get(endpoint, params)
        if not count and endpoint == "works":
            for work in result.get("results", []):
                if not isinstance(work, dict):
                    continue
                try:
                    wid = sd.work_id(work.get("id"))
                except ValueError:
                    continue
                source = (work.get("primary_location") or {}).get("source") or {}
                issns = source.get("issn")
                self.source_issns[wid] = [v.upper() for v in issns if isinstance(v, str)] if isinstance(issns, list) else []
        if key is not None:
            self.cache[key] = result
        return result


def plan(args: argparse.Namespace) -> int:
    protocol = load_protocol(args)
    plans = []
    citation_bins = None
    for slug in protocol["journals"]:
        child = journal_args(protocol, slug, Path("cohorts"))
        params = sd.selection_params(child)
        bins = sd.balanced_plan(child, params)
        if citation_bins is None:
            citation_bins = [{key: cell[key] for key in ("decile", "lower", "upper", "upper_inclusive", "quota")} for cell in bins]
        journal = {"journal": slug, "title": sd.JOURNAL_PRESETS[slug]["title"],
                   "issn": sd.JOURNAL_PRESETS[slug]["issn"], "sample_size": protocol["n_per_journal"]}
        if getattr(args, "show_api_queries", False):
            journal.update(params=params, citation_bins=bins)
        plans.append(journal)
    print(json.dumps({"protocol": protocol, "protocol_sha256": digest(canonical(protocol)),
                      "total_sample_size": protocol["n_per_journal"] * len(protocol["journals"]),
                      "citation_timing": CITATION_NOTE, "citation_bins": citation_bins, "journal_plans": plans,
                      "network_requests": 0, "files_created": 0}, ensure_ascii=False, indent=2))
    return 0


def preflight(protocol: dict, client) -> list[dict]:
    reports = []
    for slug in protocol["journals"]:
        child = journal_args(protocol, slug, Path("cohorts"))
        total, bins, missing = sd.balanced_counts(client, child, sd.selection_params(child))
        possible = all(cell["eligible_count"] >= cell["quota"] for cell in bins)
        reports.append({"journal": slug, "title": sd.JOURNAL_PRESETS[slug]["title"],
                        "candidate_count": total, "missing_percentile": missing,
                        "feasible": possible, "citation_bins": bins})
        print(f"{slug}: {total} candidates; {missing} missing/out-of-range percentiles; "
              f"balanced N={protocol['n_per_journal']}: {'yes' if possible else 'no'}")
        for cell in bins:
            print(f"  Decile {cell['decile']:2}: {cell['eligible_count']} eligible; {cell['quota']} required")
    return reports


def availability(args: argparse.Namespace, client=None) -> int:
    protocol = load_protocol(args)
    client = CountCache(client or sd.OpenAlexClient(sd.api_key()))
    reports = preflight(protocol, client)
    print("Availability only; no samples drawn or files saved. " + CITATION_NOTE)
    return 0 if all(row["feasible"] for row in reports) else 1


def read_records(path: Path) -> list[dict]:
    values = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if any(not isinstance(value, dict) for value in values):
        raise ValueError("Manifest must contain JSON objects.")
    return values


def validate_records(protocol: dict, records: list[dict]) -> None:
    n = protocol["n_per_journal"]
    if len(records) != n * len(protocol["journals"]):
        raise ValueError("Manifest does not have the exact expected total sample size.")
    dois, ids, cells = set(), set(), Counter()
    for record in records:
        doi, wid = sd.normalize_doi(record.get("doi")), sd.work_id(record.get("id"))
        if not doi or doi != record["doi"] or doi in dois or wid in ids:
            raise ValueError("Manifest has an invalid or duplicate DOI/OpenAlex work ID.")
        dois.add(doi); ids.add(wid)
        slug = record.get("journal_slug")
        if slug not in protocol["journals"] or record.get("journal_name") != sd.JOURNAL_PRESETS[slug]["title"]:
            raise ValueError("Manifest has an unexpected journal identity.")
        issns = record.get("source_issns")
        if (not isinstance(issns, list) or any(not isinstance(v, str) for v in issns)
                or sd.JOURNAL_PRESETS[slug]["issn"] not in issns):
            raise ValueError("A paper's actual source ISSNs do not match its selected journal.")
        decile, value = record.get("citation_decile"), record.get("cnp")
        if type(decile) is not int or not 1 <= decile <= 10 or type(value) not in (float, int) or not math.isfinite(value):
            raise ValueError("Manifest has invalid citation strata.")
        if not ((decile - 1) / 10 <= value and (value <= 1 if decile == 10 else value < decile / 10)):
            raise ValueError("Citation percentile does not match its saved decile.")
        publication = record.get("publication_date")
        if not isinstance(publication, str) or not protocol["publication_start"] <= publication <= protocol["publication_end"]:
            raise ValueError("Manifest includes a paper outside the fixed publication window.")
        try:
            sd.iso_date(publication)
        except argparse.ArgumentTypeError:
            raise ValueError("Manifest includes an invalid publication date.") from None
        if type(record.get("year")) in (int, float) and record["year"] != int(publication[:4]):
            raise ValueError("A paper's publication year and date disagree.")
        if record.get("type") not in protocol["work_types"]:
            raise ValueError("Manifest includes a work type outside the protocol.")
        probability, weight = record.get("sampling_probability"), record.get("inverse_probability_weight")
        if (type(probability) not in (int, float) or type(weight) not in (int, float)
                or not 0 < probability <= 1 or not math.isfinite(weight) or weight < 1
                or not math.isclose(probability * weight, 1, rel_tol=1e-8)):
            raise ValueError("Manifest has invalid sampling weights.")
        cells[slug, decile] += 1
    if any(cells[slug, decile] != n // 10 for slug in protocol["journals"] for decile in range(1, 11)):
        raise ValueError("Manifest does not meet every journal's exact citation-decile quota.")


def select(args: argparse.Namespace, client=None) -> int:
    protocol = load_protocol(args)
    root = Path(getattr(args, "output_root", None) or DEFAULT_OUTPUT).expanduser().resolve()
    target = root / protocol["name"]
    if target.exists() or target.is_symlink():
        raise ValueError("Study already exists. Choose a new name; use refresh to update citations.")
    client = CountCache(client or sd.OpenAlexClient(sd.api_key()))
    started = sd.utc_now()
    reports = preflight(protocol, client)
    if not all(row["feasible"] for row in reports):
        raise ValueError("At least one journal cannot fill every citation band. No study was selected or saved. "
                         "Broaden the common topic/date filters or reduce N for every journal.")
    root.mkdir(parents=True, exist_ok=True)
    lock = root / ("." + protocol["name"] + ".selection.lock")
    try:
        handle = lock.open("x", encoding="utf-8")
    except FileExistsError:
        raise ValueError("This study is being selected by another process (selection lock exists).") from None
    temporary = None
    try:
        handle.close()
        if target.exists() or target.is_symlink():
            raise ValueError("Study already exists; no files replaced.")
        temporary = Path(tempfile.mkdtemp(prefix="." + protocol["name"] + "-", dir=root))
        records = []
        for slug in protocol["journals"]:
            child = journal_args(protocol, slug, temporary / "cohorts")
            with redirect_stdout(io.StringIO()):
                result = sd.select_cohort(child, client)
            if result:
                raise ValueError("A journal selection failed; no combined study was saved.")
            journal_records = read_records(child.output / (slug + ".jsonl"))
            if len(journal_records) != protocol["n_per_journal"]:
                raise ValueError("A journal returned the wrong number of papers; no study was saved.")
            records.extend({**row, "journal_slug": slug, "journal_name": sd.JOURNAL_PRESETS[slug]["title"],
                            "source_issns": client.source_issns.get(sd.work_id(row.get("id")), [])}
                           for row in journal_records)
        validate_records(protocol, records)
        manifest = "".join(sd.json_line(row) for row in records).encode("utf-8")
        dois = "".join(row["doi"] + "\n" for row in records).encode("utf-8")
        (temporary / "manifest.jsonl").write_bytes(manifest)
        (temporary / "dois.txt").write_bytes(dois)
        (temporary / "manifest.citations.jsonl").write_text(
            "".join(sd.json_line({**sd.citation_record(row), "journal_slug": row["journal_slug"],
                                  "journal_name": row["journal_name"]}) for row in records), encoding="utf-8")
        metadata = {"schema_version": 1, "protocol": protocol, "protocol_sha256": digest(canonical(protocol)),
                    "selection_started_at_utc": started, "selection_completed_at_utc": sd.utc_now(),
                    "selected_count": len(records), "journal_seeds": {slug: protocol["seed"] for slug in protocol["journals"]},
                    "sha256": {"manifest.jsonl": digest(manifest), "dois.txt": digest(dois)},
                    "citation_timing": CITATION_NOTE, "preflight": reports,
                    "citation_history": "manifest.citations.jsonl",
                    "notes": ["All journal availability was checked before sampling; no replacement of unavailable XML.",
                              "Original per-journal manifests and baseline histories are retained in cohorts/.",
                              "Sampling weights describe eligible works with known normalized citation percentiles.",
                              "Saved DOI and work identities are fixed; citation refresh does not resample."]}
        (temporary / "study.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        if target.exists() or target.is_symlink():
            raise ValueError("Study appeared during selection; no files replaced.")
        os.rename(temporary, target)
        temporary = None
    finally:
        if temporary is not None:
            shutil.rmtree(temporary)
        lock.unlink(missing_ok=True)
    print(f"Saved {len(records)} papers ({protocol['n_per_journal']} per journal): {target}")
    print(f"Frozen DOI list: {target / 'dois.txt'}\nCitation history: {target / 'manifest.citations.jsonl'}")
    return 0


def verify_study(path: Path) -> tuple[dict, list[dict]]:
    path = Path(path).expanduser().resolve()
    metadata = json.loads((path / "study.json").read_text(encoding="utf-8"))
    if not isinstance(metadata, dict) or metadata.get("schema_version") != 1:
        raise ValueError("Unsupported or invalid study metadata.")
    protocol = validate_protocol(metadata.get("protocol"))
    if protocol != metadata["protocol"] or digest(canonical(protocol)) != metadata.get("protocol_sha256"):
        raise ValueError("Frozen study protocol failed its integrity check.")
    for name in ("manifest.jsonl", "dois.txt"):
        if digest((path / name).read_bytes()) != (metadata.get("sha256") or {}).get(name):
            raise ValueError(f"Frozen {name} failed its integrity check; do not edit a selected study.")
    records = read_records(path / "manifest.jsonl")
    validate_records(protocol, records)
    if metadata.get("selected_count") != len(records):
        raise ValueError("Study metadata and manifest sample sizes differ.")
    if (path / "dois.txt").read_text(encoding="utf-8") != "".join(row["doi"] + "\n" for row in records):
        raise ValueError("Frozen DOI list and manifest disagree.")
    return metadata, records


def download(args: argparse.Namespace) -> int:
    study = Path(args.study).expanduser().resolve()
    verify_study(study)
    argv = [str(study / "dois.txt"), "--output", str(study / "xml"), "--service", args.service]
    for name in ("limit", "max_requests", "interval", "retries"):
        if getattr(args, name, None) is not None:
            argv += ["--" + name.replace("_", "-"), str(getattr(args, name))]
    if getattr(args, "dry_run", False):
        argv += ["--dry-run"]
    # One invocation shares one request budget across every journal, including retries.
    return dn.main(argv)


def refresh(args: argparse.Namespace, client=None) -> int:
    study = Path(args.study).expanduser().resolve()
    verify_study(study)
    return sd.refresh_cohort(argparse.Namespace(manifest=study / "manifest.jsonl"), client)


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = ap.add_subparsers(dest="command", required=True)
    for name, func in (("plan", plan), ("availability", availability), ("select", select)):
        child = commands.add_parser(name)
        child.add_argument("--config", type=Path, help="JSON study parameters; never put keys here.")
        child.add_argument("--query", help="Common title/abstract keyword expression; overrides configuration.")
        child.add_argument("--from", dest="date_from", help="Inclusive publication start, YYYY-MM-DD.")
        child.add_argument("--to", dest="date_to", help="Inclusive publication end, YYYY-MM-DD.")
        child.add_argument("--n-per-journal", type=int, help="Same N for each journal; a multiple of ten.")
        child.add_argument("--journal", action="append", choices=tuple(sd.JOURNAL_PRESETS),
                           help="Repeat to choose individual journals; default all six.")
        child.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
        if name == "plan":
            child.add_argument("--show-api-queries", action="store_true", help="Include the full per-journal API queries.")
        child.set_defaults(func=func)
    child = commands.add_parser("download", help="Fetch XML for the fixed cohort, without resampling.")
    child.add_argument("--study", type=Path, required=True)
    child.add_argument("--service", choices=("oa", "tdm"), default="oa")
    child.add_argument("--limit", type=int)
    child.add_argument("--max-requests", type=int, default=450, help="One budget across all journals, counting retries.")
    child.add_argument("--interval", type=float, default=1.1)
    child.add_argument("--retries", type=int, default=3)
    child.add_argument("--dry-run", action="store_true")
    child.set_defaults(func=download)
    child = commands.add_parser("refresh", help="Append current citations for the exact frozen cohort.")
    child.add_argument("--study", type=Path, required=True)
    child.set_defaults(func=refresh)
    return ap


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        return args.func(args)
    except (ValueError, OSError, sd.OpenAlexError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Interrupted. The frozen sample is unchanged; completed citation snapshots remain saved.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
