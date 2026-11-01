#!/usr/bin/env python3
"""Select a reproducible DOI cohort from OpenAlex and append citation snapshots.

Python 3.10+; standard library only. Run ``python3 tools/select_dois.py --help``.
Publisher download tokens are separate from the OpenAlex key used here.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
from email.utils import parsedate_to_datetime
import getpass
import json
import os
from pathlib import Path
import re
import sys
import time
from typing import Any
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.openalex.org"
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "private" / "corpus"
WORK_FIELDS = (
    "id,doi,title,publication_year,publication_date,primary_location,cited_by_count,"
    "citation_normalized_percentile,cited_by_percentile_year,fwci,primary_topic,"
    "counts_by_year,updated_date,open_access,referenced_works_count,type"
)
# Electronic ISSNs verified against each publisher's journal information page.
# One ISSN identifies each source; OpenAlex matches the source's ISSN list.
JOURNAL_PRESETS = {
    "nature-geoscience": {"title": "Nature Geoscience", "issn": "1752-0908", "launch_year": 2008,
                          "information_url": "https://www.nature.com/ngeo/journal-information"},
    "nature-communications": {"title": "Nature Communications", "issn": "2041-1723", "launch_year": 2010,
                              "information_url": "https://www.nature.com/ncomms/journal-information"},
    "communications-earth-environment": {"title": "Communications Earth & Environment", "issn": "2662-4435", "launch_year": 2020,
                                         "information_url": "https://www.nature.com/commsenv/journal-information"},
    "nature-reviews-earth-environment": {"title": "Nature Reviews Earth & Environment", "issn": "2662-138X", "launch_year": 2020,
                                         "information_url": "https://www.nature.com/natrevearthenviron/journal-information"},
    "nature-water": {"title": "Nature Water", "issn": "2731-6084", "launch_year": 2023,
                     "information_url": "https://www.nature.com/natwater/journal-information"},
    "nature-sustainability": {"title": "Nature Sustainability", "issn": "2398-9629", "launch_year": 2018,
                              "information_url": "https://www.nature.com/natsustain/journal-information"},
}
JOURNAL_GROUPS = {"nature-earth-environment": tuple(JOURNAL_PRESETS)}


class OpenAlexError(RuntimeError):
    """A sanitized API failure that does not include request headers or keys."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def retry_seconds(value: str | None, fallback: float) -> float:
    if value:
        try:
            return max(0.0, float(value))
        except ValueError:
            try:
                return max(0.0, (parsedate_to_datetime(value) - datetime.now(timezone.utc)).total_seconds())
            except (ValueError, TypeError, OverflowError):
                pass
    return fallback


class OpenAlexClient:
    def __init__(self, key: str | None = None, interval: float = 1.0):
        if key and not re.fullmatch(r"[!-~]+", key):
            raise OpenAlexError("The OpenAlex key contains unsupported whitespace or characters.")
        self.key = key
        self.interval = interval
        self.last_request = 0.0

    def get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict:
        url = API + "/" + endpoint.lstrip("/")
        if params:
            url += "?" + urllib.parse.urlencode(params)
        headers = {"User-Agent": "metascience-doi-cohort/1.0", "Accept": "application/json"}
        for attempt in range(6):
            time.sleep(max(0.0, self.interval - (time.monotonic() - self.last_request)))
            self.last_request = time.monotonic()
            try:
                request = urllib.request.Request(url, headers=headers)
                if self.key:
                    # Authenticate only the initial API request, never a redirect.
                    request.add_unredirected_header("Authorization", "Bearer " + self.key)
                with urllib.request.urlopen(request, timeout=90) as response:
                    data = json.load(response)
                if not isinstance(data, dict):
                    raise OpenAlexError("OpenAlex returned an unexpected response format.")
                if (data.get("meta") or {}).get("timed_out"):
                    raise OpenAlexError("OpenAlex reported a timed-out partial result; retry later.")
                return data
            except urllib.error.HTTPError as exc:
                if (exc.code == 429 or 500 <= exc.code < 600) and attempt < 5:
                    delay = retry_seconds(exc.headers.get("Retry-After"), min(60.0, 2 ** attempt * 3.0))
                    time.sleep(delay)
                    continue
                raise OpenAlexError(f"OpenAlex request failed (HTTP {exc.code}).") from None
            except (urllib.error.URLError, TimeoutError, OSError):
                if attempt == 5:
                    raise OpenAlexError("OpenAlex could not be reached after retries.") from None
                time.sleep(min(60.0, 2 ** attempt * 3.0))
            except (json.JSONDecodeError, UnicodeDecodeError):
                raise OpenAlexError("OpenAlex returned invalid JSON.") from None
        raise OpenAlexError("OpenAlex request failed after retries.")


def api_key() -> str:
    value = os.environ.get("OPENALEX_API_KEY", "").strip()
    if not value:
        if not sys.stdin.isatty():
            raise ValueError("Set OPENALEX_API_KEY, or run interactively for a private key prompt.")
        value = getpass.getpass("OpenAlex API key (hidden): ").strip()
    if not value:
        raise ValueError("An OpenAlex API key is required for selection and refresh.")
    return value


def positive_n(value: str) -> int:
    try:
        n = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("N must be an integer.") from None
    if not 1 <= n <= 10000:
        raise argparse.ArgumentTypeError("N must be between 1 and 10000.")
    return n


def nonnegative(value: str) -> int:
    try:
        n = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("Citation counts must be integers.") from None
    if n < 0:
        raise argparse.ArgumentTypeError("Citation counts cannot be negative.")
    return n


def iso_date(value: str) -> str:
    try:
        if date.fromisoformat(value).isoformat() != value:
            raise ValueError
    except ValueError:
        raise argparse.ArgumentTypeError("Use an ISO date: YYYY-MM-DD.") from None
    return value


def cohort_name(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", value):
        raise argparse.ArgumentTypeError("Name must use 1–80 letters, digits, underscores or hyphens.")
    return value


def identifier(value: str, kind: str) -> str:
    value = value.strip().rstrip("/").rsplit("/", 1)[-1]
    pattern = r"S\d+" if kind == "source" else r"\d+"
    if not re.fullmatch(pattern, value):
        raise ValueError(f"Invalid {kind} ID. Use lookup to find an exact ID.")
    return value


def journal_selection(args: argparse.Namespace) -> dict:
    """Resolve journal presets and manual ISSNs into an explicit OR selection."""
    presets = list(dict.fromkeys(getattr(args, "journal_set", None) or []))
    manual_issns = getattr(args, "issn", None) or []
    if args.source and (presets or manual_issns):
        raise ValueError("Use --source or --journal-set/--issn, not both. Repeat the chosen option to OR journals.")
    slugs: list[str] = []
    for preset in presets:
        if preset in JOURNAL_GROUPS:
            slugs.extend(JOURNAL_GROUPS[preset])
        elif preset in JOURNAL_PRESETS:
            slugs.append(preset)
        else:
            raise ValueError(f"Unknown journal preset: {preset}.")
    journals = [{"slug": slug, **JOURNAL_PRESETS[slug]} for slug in dict.fromkeys(slugs)]
    issns = [journal["issn"] for journal in journals]
    for value in manual_issns:
        value = value.strip().upper()
        if not re.fullmatch(r"\d{4}-\d{3}[\dX]", value):
            raise ValueError("Invalid ISSN. Use XXXX-XXXX, with X allowed as the final check digit.")
        digits = value.replace("-", "")
        if sum((10 if digit == "X" else int(digit)) * weight for digit, weight in zip(digits, range(8, 0, -1))) % 11:
            raise ValueError(f"Invalid ISSN check digit: {value}.")
        issns.append(value)
    return {"presets": presets, "journals": journals, "issns": list(dict.fromkeys(issns)),
            "pooling": "union", "equal_journal_quotas": False}


def work_types(args: argparse.Namespace) -> list[str]:
    values = list(dict.fromkeys(getattr(args, "work_type", None) or ["article"]))
    if any(value not in {"article", "review"} for value in values):
        raise ValueError("--work-type must be article or review.")
    return values


def selection_params(args: argparse.Namespace) -> dict[str, Any]:
    """Build public, key-free API parameters; filters are ANDed, repeated IDs ORed."""
    if args.date_from > args.date_to:
        raise ValueError("--from must be on or before --to.")
    if args.min_citations is not None and args.max_citations is not None and args.min_citations > args.max_citations:
        raise ValueError("--min-citations must not exceed --max-citations.")
    journals = journal_selection(args)
    filters = ["has_doi:true", "type:" + "|".join(work_types(args)), "is_retracted:false",
               f"from_publication_date:{args.date_from}", f"to_publication_date:{args.date_to}"]
    if journals["issns"]:
        filters.append("primary_location.source.issn:" + "|".join(journals["issns"]))
    for values, field, kind in (
        (args.source, "primary_location.source.id", "source"),
        (args.field, "primary_topic.field.id", "field"),
        (args.subfield, "primary_topic.subfield.id", "subfield"),
    ):
        if values:
            filters.append(field + ":" + "|".join(dict.fromkeys(identifier(v, kind) for v in values)))
    low, high = args.min_citations, args.max_citations
    if low is not None and high is not None:
        filters.append(f"cited_by_count:{low}-{high}")
    elif low is not None:
        filters.append(f"cited_by_count:>{low - 1}")
    elif high is not None:
        filters.append(f"cited_by_count:<{high + 1}")
    if args.top_10_percent:
        filters.append("citation_normalized_percentile.is_in_top_10_percent:true")
    params: dict[str, Any] = {"filter": ",".join(filters), "select": WORK_FIELDS, "per_page": min(100, args.n)}
    if args.query:
        params["search.title_and_abstract" if args.search_scope == "title-abstract" else "search"] = args.query
    if args.method == "random":
        params.update(sample=args.n, seed=args.seed)
    elif args.method == "most-cited":
        params["sort"] = "cited_by_count:desc"
    return params


def normalize_doi(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    value = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", value.strip(), flags=re.I)
    return value.lower() if re.fullmatch(r"10\.\d{4,9}/\S+", value, re.I) else None


def work_id(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("Missing OpenAlex work ID.")
    short = value.rstrip("/").rsplit("/", 1)[-1]
    if not re.fullmatch(r"W\d+", short):
        raise ValueError("Invalid OpenAlex work ID in cohort.")
    return short


def work_record(work: dict, observed_at: str) -> dict:
    wid = work_id(work.get("id"))
    doi = normalize_doi(work.get("doi"))
    if not doi:
        raise ValueError("OpenAlex work has no valid DOI.")
    location = (work.get("primary_location") or {}).get("source") or {}
    percentile = work.get("citation_normalized_percentile") or {}
    topic = work.get("primary_topic") or {}
    oa = work.get("open_access") or {}
    return {
        "key": wid.lower(), "id": work["id"], "doi": doi, "title": work.get("title"),
        "year": work.get("publication_year"), "type": work.get("type"), "publication_date": work.get("publication_date"),
        "venue": location.get("display_name"), "source_id": (location.get("id") or "").rsplit("/", 1)[-1],
        "cited_by_count": work.get("cited_by_count"), "cnp": percentile.get("value"),
        "fwci": work.get("fwci"), "subfield": (topic.get("subfield") or {}).get("display_name"),
        "primary_topic": work.get("primary_topic"), "counts_by_year": work.get("counts_by_year"),
        "citation_normalized_percentile": work.get("citation_normalized_percentile"),
        "cited_by_percentile_year": work.get("cited_by_percentile_year"),
        "updated_date": work.get("updated_date"), "observed_at_utc": observed_at,
        "referenced_works_count": work.get("referenced_works_count"),
        "is_oa": oa.get("is_oa"), "oa_url": oa.get("oa_url"),
    }


def citation_record(record: dict, observed_at: str | None = None) -> dict:
    return {"status": "ok", "source": "OpenAlex", **{field: record.get(field) for field in (
        "key", "id", "doi", "type", "year", "publication_date", "cited_by_count", "cnp", "fwci", "counts_by_year", "primary_topic",
        "citation_normalized_percentile", "cited_by_percentile_year", "updated_date")},
        "observed_at_utc": observed_at or record.get("observed_at_utc")}


def count_parameters(params: dict[str, Any]) -> dict[str, Any]:
    """Turn a selection query into a lightweight unsampled population count."""
    count_params = {k: v for k, v in params.items() if k not in {"sample", "seed", "sort", "select", "per_page"}}
    return {**count_params, "per_page": 1, "select": "id"}


def candidate_count(client: OpenAlexClient, params: dict[str, Any]) -> int:
    response = client.get("works", count_parameters(params))
    if (response.get("meta") or {}).get("timed_out"):
        raise OpenAlexError("OpenAlex reported a timed-out partial count; retry later.")
    count = (response.get("meta") or {}).get("count")
    if not isinstance(count, int) or count < 0:
        raise OpenAlexError("OpenAlex did not report a valid candidate count.")
    return count


def collect_selection(client: OpenAlexClient, args: argparse.Namespace, params: dict[str, Any],
                      known_count: int | None = None) -> tuple[list[dict], int]:
    """Fetch an API sample or citation-ranked prefix, rejecting duplicate/short cohorts."""
    picked: list[dict] = []
    seen_dois: set[str] = set()
    seen_ids: set[str] = set()
    # Sample response meta.count can describe the sample, so count without sampling.
    count = candidate_count(client, params) if known_count is None else known_count
    if count < args.n:
        raise ValueError(f"Only {count} candidate works match; requested {args.n}. Broaden filters or reduce N.")
    page, cursor = 1, "*"
    while len(picked) < args.n:
        paging = {"page": page} if args.method == "random" else {"cursor": cursor}
        response = client.get("works", {**params, **paging})
        meta = response.get("meta") or {}
        if meta.get("timed_out"):
            raise OpenAlexError("OpenAlex reported a timed-out partial page; retry later.")
        works = response.get("results")
        if not isinstance(works, list):
            raise OpenAlexError("OpenAlex response has no valid results list.")
        for work in works:
            try:
                doi, wid = normalize_doi(work.get("doi")), work_id(work.get("id"))
            except (AttributeError, ValueError):
                continue
            if not doi or doi in seen_dois or wid in seen_ids:
                continue
            seen_dois.add(doi); seen_ids.add(wid); picked.append(work)
            if len(picked) == args.n:
                break
        if args.method == "random":
            # Sampling supports numbered pages, keeping the same sample size and seed.
            if not works or page * params["per_page"] >= args.n:
                break
            page += 1
        else:
            next_cursor = meta.get("next_cursor")
            if not works or not next_cursor or next_cursor == cursor:
                break
            cursor = next_cursor
    if len(picked) != args.n:
        raise ValueError(f"Received {len(picked)} unique valid DOI works; requested {args.n}. No cohort was saved.")
    return picked, count


def balanced_plan(args: argparse.Namespace, params: dict[str, Any]) -> list[dict]:
    """Ten disjoint normalized-percentile bins with exactly equal quotas."""
    if args.n < 10 or args.n % 10:
        raise ValueError("Balanced selection requires N >= 10 divisible by 10, for exactly equal decile groups.")
    if args.top_10_percent:
        raise ValueError("--top-10-percent conflicts with ten-decile balance; use --method random for that restricted group.")
    plan = []
    field = "citation_normalized_percentile.value"
    for index in range(10):
        low = "0" if index == 0 else f"0.{index}"
        high = "1" if index == 9 else f"0.{index + 1}"
        # OpenAlex supports inclusive trailing ranges and ANDed repeated numeric filters.
        clause = f"{field}:{low}-1" if index == 9 else f"{field}:{low}-,{field}:<{high}"
        quota = args.n // 10
        query = {**params, "filter": params["filter"] + "," + clause,
                 "sample": quota, "seed": args.seed + index, "per_page": min(100, quota)}
        plan.append({"decile": index + 1, "lower": low, "upper": high,
                     "upper_inclusive": index == 9, "quota": quota, "params": query})
    return plan


def balanced_counts(client: OpenAlexClient, args: argparse.Namespace,
                    params: dict[str, Any]) -> tuple[int, list[dict], int]:
    """Count the base pool and ten fixed deciles without requesting samples."""
    plan = balanced_plan(args, params)
    total = candidate_count(client, params)
    for cell in plan:
        cell["eligible_count"] = candidate_count(client, cell["params"])
    missing = total - sum(cell["eligible_count"] for cell in plan)
    if missing < 0:
        raise OpenAlexError("Percentile-bin counts exceed the base pool. OpenAlex may have changed during counting; retry.")
    return total, plan, missing


def collect_balanced(client: OpenAlexClient, args: argparse.Namespace,
                     params: dict[str, Any]) -> tuple[list[dict], int, list[dict], int]:
    total, plan, missing = balanced_counts(client, args, params)
    if any(cell["eligible_count"] < cell["quota"] for cell in plan):
        table = "\n".join(f"  Decile {c['decile']}: {c['eligible_count']} eligible; {c['quota']} required" for c in plan)
        raise ValueError("Cannot fill a balanced cohort; no cohort was saved.\n" + table +
                         f"\n  Missing/out-of-range percentile: {missing}. Broaden filters or reduce N.")
    selected: list[dict] = []
    seen: set[str] = set()
    for cell in plan:
        sample_args = argparse.Namespace(**vars(args))
        sample_args.n = cell["quota"]
        sample_args.method = "random"
        works, _ = collect_selection(client, sample_args, cell["params"], cell["eligible_count"])
        for work in works:
            value = (work.get("citation_normalized_percentile") or {}).get("value")
            low, high = float(cell["lower"]), float(cell["upper"])
            in_bin = isinstance(value, (int, float)) and low <= value and (value <= high if cell["upper_inclusive"] else value < high)
            doi = normalize_doi(work.get("doi"))
            if not in_bin or doi in seen:
                raise OpenAlexError("OpenAlex returned overlapping or changed percentile strata. No cohort was saved; retry.")
            seen.add(doi)
            work["_citation_decile"] = cell["decile"]
            selected.append(work)
        cell["selected_count"] = len(works)
        cell["selected_uncited_count"] = sum(w.get("cited_by_count") == 0 for w in works)
        cell["sampling_probability"] = cell["quota"] / cell["eligible_count"]
        cell["inverse_probability_weight"] = cell["eligible_count"] / cell["quota"]
    return selected, total, plan, missing


def report_availability(client: OpenAlexClient, args: argparse.Namespace, params: dict[str, Any]) -> int:
    """Report feasibility only: never sample, create folders, or save a cohort."""
    print(f"Availability: {args.name}")
    if args.method == "balanced":
        total, plan, missing = balanced_counts(client, args, params)
        print(f"Matching candidate works: {total}")
        for cell in plan:
            print(f"  Decile {cell['decile']}: {cell['eligible_count']} eligible; {cell['quota']} required")
        print(f"Missing/out-of-range percentile: {missing}")
        possible = all(cell["eligible_count"] >= cell["quota"] for cell in plan)
        print(f"Exact citation-balanced sample of {args.n} possible: {'yes' if possible else 'no'}")
    else:
        total = candidate_count(client, params)
        print(f"Matching candidate works: {total}; {args.n} required")
        print(f"Sample of {args.n} possible: {'yes' if total >= args.n else 'no'}")
    print("Journals are pooled; equal numbers per journal are not required.")
    print("Availability report only; no sample drawn and no cohort files saved.")
    return 0


def json_line(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, allow_nan=False) + "\n"


def select_cohort(args: argparse.Namespace, client: OpenAlexClient | None = None) -> int:
    params = selection_params(args)
    plan = balanced_plan(args, params) if args.method == "balanced" else None
    paths = {kind: args.output / (args.name + suffix) for kind, suffix in (
        ("manifest", ".jsonl"), ("dois", ".dois.txt"), ("meta", ".meta.json"), ("citations", ".citations.jsonl"))}
    if args.dry_run:
        display_plan = plan
        if args.availability_only and plan:
            display_plan = [{**cell, "params": count_parameters(cell["params"])} for cell in plan]
        print(json.dumps({"endpoint": API + "/works", "params": count_parameters(params) if args.availability_only else params,
                          "availability_only": args.availability_only,
                          "journal_selection": journal_selection(args), "work_types": work_types(args),
                          "balanced_plan": display_plan,
                          "pagination": "none" if args.availability_only else "cursor" if args.method == "most-cited" else "page",
                          "outputs": {} if args.availability_only else {k: str(v) for k, v in paths.items()}}, indent=2))
        return 0
    if args.availability_only:
        return report_availability(client or OpenAlexClient(api_key()), args, params)
    if any(path.exists() for path in paths.values()):
        raise ValueError("A cohort output already exists. Choose a new --name; use refresh for citation updates.")
    client = client or OpenAlexClient(api_key())
    if args.method == "balanced":
        works, count, plan, missing_percentile = collect_balanced(client, args, params)
    else:
        works, count = collect_selection(client, args, params)
        missing_percentile = None
    observed_at = utc_now()
    records = [work_record(work, observed_at) for work in works]
    if plan:
        by_decile = {cell["decile"]: cell for cell in plan}
        for work, record in zip(works, records):
            cell = by_decile[work["_citation_decile"]]
            record.update(stratum=f"citation decile {cell['decile']}", citation_decile=cell["decile"],
                          sampling_probability=cell["sampling_probability"],
                          inverse_probability_weight=cell["inverse_probability_weight"])
    metadata = {"name": args.name, "source": "OpenAlex", "observed_at_utc": observed_at,
                "candidate_count": count, "selected_count": len(records), "method": args.method,
                "seed": args.seed if args.method != "most-cited" else None,
                "query": params, "search_scope": args.search_scope,
                "journal_selection": journal_selection(args), "work_types": work_types(args),
                "citation_bins": plan, "excluded_missing_or_out_of_range_percentile": missing_percentile,
                "selected_uncited_count": sum(r["cited_by_count"] == 0 for r in records),
                "notes": ["Citation filters and ranking use the counts observed at selection time.",
                          "Dates are inclusive; primary journal and primary-topic classifications are used.",
                          "Journal presets are pooled; selection does not require equal numbers per journal.",
                          "Citation percentile uses OpenAlex normalization by publication year, type and subfield.",
                          "A fixed seed does not freeze future changes to OpenAlex; retain this manifest."]}
    if plan:
        metadata["notes"].append("Balanced selection is intentionally enriched; stratum sampling weights apply only to the eligible population with known normalized percentiles.")
    content = {"manifest": "".join(json_line(r) for r in records),
               "dois": "".join(r["doi"] + "\n" for r in records),
               "meta": json.dumps(metadata, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
               "citations": "".join(json_line(citation_record(r)) for r in records)}
    args.output.mkdir(parents=True, exist_ok=True)
    # Exclusive creation protects frozen cohorts even if another process starts concurrently.
    created: list[Path] = []
    try:
        for kind, path in paths.items():
            with path.open("x", encoding="utf-8") as handle:
                created.append(path)
                handle.write(content[kind])
    except Exception:
        for path in created:
            path.unlink(missing_ok=True)
        raise
    print(f"Saved {len(records)} unique DOI works from {count} matching candidates to {paths['manifest']}")
    print(f"DOI list: {paths['dois']}\nCitation snapshots: {paths['citations']}")
    return 0


def refresh_cohort(args: argparse.Namespace, client: OpenAlexClient | None = None) -> int:
    manifest = args.manifest
    if not manifest.is_file() or manifest.suffix != ".jsonl" or manifest.name.endswith(".citations.jsonl"):
        raise ValueError("Pass an existing cohort NAME.jsonl manifest.")
    records = [json.loads(line) for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not records:
        raise ValueError("The cohort manifest is empty.")
    # Validate all IDs before making requests or creating an output file.
    ids = [work_id(record.get("id")) for record in records]
    client = client or OpenAlexClient(api_key())
    output = manifest.with_name(manifest.stem + ".citations.jsonl")
    failures = 0
    with output.open("a", encoding="utf-8") as handle:
        for original, wid in zip(records, ids):
            observed_at = utc_now()
            try:
                work = client.get("works/" + wid, {"select": WORK_FIELDS})
                updated = work_record(work, observed_at)
                # Keep the frozen cohort identity as well as the API's current identity.
                snapshot = citation_record(updated)
                snapshot.update(key=original.get("key"), cohort_id=original.get("id"), cohort_doi=original.get("doi"))
            except (OpenAlexError, ValueError, TypeError):
                failures += 1
                snapshot = {"status": "error", "source": "OpenAlex", "key": original.get("key"),
                            "id": original.get("id"), "doi": original.get("doi"), "observed_at_utc": observed_at,
                            "error": "Could not retrieve a valid current OpenAlex record; retry later."}
                print(f"Could not refresh {wid}; recorded as a failure.", file=sys.stderr)
            handle.write(json_line(snapshot))
            handle.flush()
    print(f"Appended {len(records) - failures} successful snapshots and {failures} failures to {output}")
    return 1 if failures else 0


def lookup(args: argparse.Namespace, client: OpenAlexClient | None = None) -> int:
    client = client or OpenAlexClient(os.environ.get("OPENALEX_API_KEY", "").strip() or None)
    fields = "id,display_name,issn,issn_l" if args.kind == "sources" else "id,display_name"
    response = client.get(args.kind, {"search": args.query, "per_page": 25, "select": fields})
    print("ID\tName" + ("\tISSNs" if args.kind == "sources" else ""))
    for row in response.get("results", []):
        name = " ".join(str(row.get("display_name", "")).split())
        columns = [(row.get("id") or "").rsplit("/", 1)[-1], name]
        if args.kind == "sources":
            columns.append(", ".join(row.get("issn") or ([row["issn_l"]] if row.get("issn_l") else [])))
        print("\t".join(columns))
    return 0


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__)
    commands = ap.add_subparsers(dest="command", required=True)
    look = commands.add_parser("lookup", help="Find exact journal, field or subfield IDs.")
    look.add_argument("--kind", choices=("sources", "fields", "subfields"), required=True)
    look.add_argument("--query", required=True)
    look.set_defaults(func=lookup)
    select = commands.add_parser("select", help="Freeze exactly N unique DOI works and initial citation snapshots.")
    select.add_argument("--name", required=True, type=cohort_name)
    select.add_argument("--n", required=True, type=positive_n)
    select.add_argument("--query", help="Keyword expression understood by OpenAlex search.")
    select.add_argument("--search-scope", choices=("title-abstract", "all"), default="title-abstract")
    select.add_argument("--source", action="append", default=[], help="Journal source ID; repeat to OR journals.")
    select.add_argument("--journal-set", action="append", default=[],
                        choices=tuple(JOURNAL_GROUPS) + tuple(JOURNAL_PRESETS),
                        help="Named journal/group preset; repeat to OR presets. Cannot combine with --source.")
    select.add_argument("--issn", action="append", default=[],
                        help="Journal ISSN; repeat to OR with other ISSNs and presets. Cannot combine with --source.")
    select.add_argument("--work-type", action="append", choices=("article", "review"),
                        help="OpenAlex work type; repeat to include both. Default: article only.")
    select.add_argument("--field", action="append", default=[], help="Primary field numeric ID; repeat to OR fields.")
    select.add_argument("--subfield", action="append", default=[], help="Primary subfield numeric ID; repeat to OR subfields.")
    select.add_argument("--from", dest="date_from", type=iso_date, required=True)
    select.add_argument("--to", dest="date_to", type=iso_date, required=True)
    select.add_argument("--method", choices=("balanced", "random", "most-cited"), default="balanced",
                        help="Default: equal normalized citation deciles (N >= 10 and divisible by 10).")
    select.add_argument("--seed", type=int, default=2026)
    select.add_argument("--min-citations", type=nonnegative)
    select.add_argument("--max-citations", type=nonnegative)
    select.add_argument("--top-10-percent", action="store_true", help="Require OpenAlex normalized top-decile flag.")
    select.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    select.add_argument("--dry-run", action="store_true", help="Show query and destinations; no key or network required.")
    select.add_argument("--availability-only", action="store_true",
                        help="Count eligible works and citation bins only; no sampling or cohort files. Requires an OpenAlex key.")
    select.set_defaults(func=select_cohort)
    refresh = commands.add_parser("refresh", help="Append citation snapshots without changing the cohort.")
    refresh.add_argument("manifest", type=Path, help="Path to frozen NAME.jsonl cohort.")
    refresh.set_defaults(func=refresh_cohort)
    return ap


def main(argv: list[str] | None = None) -> int:
    ap = parser()
    args = ap.parse_args(argv)
    try:
        return args.func(args)
    except (OpenAlexError, ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Interrupted. Any completed refresh snapshots remain saved.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
