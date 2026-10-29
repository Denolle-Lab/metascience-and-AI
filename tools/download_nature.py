#!/usr/bin/env python3
"""Download Springer Nature JATS XML by DOI using a provisioned OA or TDM key.

Python 3.10+, standard library only. Default: Open Access API. Licensed content:
--service tdm requires a Full Text API KEY/METRIC credential and entitlements.
Usage: python3 tools/download_nature.py private/corpus/sample.dois.txt --limit 1
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import getpass
import hashlib
from http.client import HTTPException, IncompleteRead
import math
import os
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
import xml.etree.ElementTree as ET

ENDPOINTS = {
    "oa": "https://api.springernature.com/openaccess/jats",
    "tdm": "https://api.springernature.com/xmldata/jats",
}
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "private" / "xml" / "nature"
MAX_RESPONSE_BYTES = 50 * 1024 * 1024
RETRYABLE = {408, 429, 500, 502, 503, 504}
FIELDS = ["time_utc", "doi", "status", "service", "http_status", "path", "bytes", "attempts", "message"]


def normalize_doi(value: str) -> str:
    value = value.strip()
    if re.match(r"https?://(?:dx\.)?doi\.org/", value, re.I):
        value = unquote(urlsplit(value).path.lstrip("/"))
    value = re.sub(r"^doi:\s*", "", value, flags=re.I).strip()
    if not re.fullmatch(r"10\.\d{4,9}/[^\s\x00-\x1f\x7f]+", value):
        raise ValueError("Invalid DOI or DOI URL in input.")
    return value.lower()


def read_dois(path: Path, column: str = "doi") -> list[str]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        if path.suffix.lower() == ".csv":
            reader = csv.DictReader(handle)
            headers = {key.strip().lower(): key for key in (reader.fieldnames or [])}
            if column.lower() not in headers:
                raise ValueError(f"CSV needs a {column!r} column; use --doi-column to choose another.")
            values = [(i, row.get(headers[column.lower()], "") or "") for i, row in enumerate(reader, 2)]
        else:
            values = [(i, line) for i, line in enumerate(handle, 1)
                      if line.strip() and not line.lstrip().startswith("#")]
    unique, seen = [], set()
    for number, value in values:
        if not value.strip():
            continue
        try:
            doi = normalize_doi(value)
        except ValueError:
            raise ValueError(f"Invalid DOI on input line {number}; fix the list before downloading.") from None
        if doi not in seen:
            unique.append(doi)
            seen.add(doi)
    if not unique:
        raise ValueError("No DOIs found in the input.")
    return unique


def xml_path(output: Path, doi: str) -> Path:
    digest = hashlib.sha256(doi.encode()).hexdigest()[:12]
    return output / f"{quote(doi, safe='')[:160]}--{digest}.xml"


class ContentError(ValueError):
    """Sanitized validation error; never include the API response or request URL."""


class NoRecord(ContentError):
    pass


def local_name(element: ET.Element) -> str:
    return element.tag.rsplit("}", 1)[-1] if isinstance(element.tag, str) else ""


def extract_article(payload: bytes, doi: str) -> bytes:
    """Accept only the requested JATS article with a nonempty full-text body."""
    if b"<!ENTITY" in payload.upper():
        raise ContentError("XML entity declarations are not supported; no file saved.")
    try:
        root = ET.fromstring(payload)
    except ET.ParseError:
        raise ContentError("Response is not valid XML; no file saved.") from None
    articles = [element for element in root.iter() if local_name(element) == "article"]
    if not articles:
        # Restrict 'unavailable' to recognized empty API responses, not arbitrary
        # XML errors that could otherwise be mistaken for a paywalled article.
        totals = [e for e in root.iter() if local_name(e) == "total"]
        if any((e.text or "").strip() == "0" for e in totals):
            raise NoRecord("No article returned by this API; coverage or entitlement may be missing.")
        raise ContentError("Response has no JATS article; it may be an API error or metadata only.")
    matches = []
    for article in articles:
        fronts = [e for e in article if local_name(e) == "front"]
        identities = []
        for front in fronts:
            for meta in front:
                if local_name(meta) != "article-meta":
                    continue
                for item in meta:
                    if local_name(item) == "article-id" and item.get("pub-id-type", "").lower() == "doi":
                        try:
                            identities.append(normalize_doi("".join(item.itertext())))
                        except ValueError:
                            pass
        if doi not in identities:
            continue
        body = next((e for e in article if local_name(e) == "body"), None)
        if body is None or not "".join(body.itertext()).strip():
            raise ContentError("Requested article has no full-text body; no file saved.")
        matches.append(article)
    if len(matches) != 1:
        raise ContentError("Response DOI does not uniquely match the requested article; no file saved.")
    # Save just the JATS article; the API envelope can contain request metadata.
    # Omit external DTD declarations. Preserve article attributes and namespaces.
    return ET.tostring(matches[0], encoding="utf-8", xml_declaration=True)


def existing_article(path: Path, doi: str) -> bool:
    try:
        if path.stat().st_size > MAX_RESPONSE_BYTES:
            return False
        extract_article(path.read_bytes(), doi)
        return True
    except (OSError, ContentError):
        return False


class BudgetExceeded(RuntimeError):
    pass


class RequestBudget:
    """Count attempts, including retries; this is a per-run, not account-wide quota."""
    def __init__(self, maximum: int):
        self.maximum, self.used = maximum, 0

    def reserve(self):
        if self.used >= self.maximum:
            raise BudgetExceeded("Per-run request budget reached; rerun when quota permits.")
        self.used += 1


class RateLimiter:
    def __init__(self, interval: float):
        self.interval, self.next_request = interval, 0.0

    def wait(self):
        delay = self.next_request - time.monotonic()
        if delay > 0:
            time.sleep(delay)
        self.next_request = time.monotonic() + self.interval


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Authentication is in the query URL. Require the documented endpoint
        # rather than following a redirect that might include a credential.
        raise URLError("API redirects are not followed")


def retry_delay(value, attempt):
    if value:
        try:
            seconds = float(value)
        except ValueError:
            try:
                when = parsedate_to_datetime(value)
                if when.tzinfo is None:
                    when = when.replace(tzinfo=timezone.utc)
                seconds = (when - datetime.now(timezone.utc)).total_seconds()
            except (TypeError, ValueError, OverflowError):
                seconds = float("nan")
        if math.isfinite(seconds):
            return max(1.0, seconds)
    return min(300.0, 30.0 * 2 ** (attempt - 1))


def download_xml(doi, output, service, credential, opener, limiter, budget, timeout=120, retries=3):
    target = xml_path(output, doi)
    result = dict(doi=doi, status="failed", service=service, http_status="", path=str(target),
                  bytes=0, attempts=0, message="")
    if existing_article(target, doi):
        return {**result, "status": "existing", "bytes": target.stat().st_size}
    partial = target.with_suffix(".xml.part")
    query = urlencode({"q": "doi:" + doi, "p": 1, "s": 1, "api_key": credential})
    request = Request(ENDPOINTS[service] + "?" + query, headers={
        "Accept": "application/xml", "User-Agent": "TextDataMining/MetascienceNatureDownloader/1.0"})
    for attempt in range(1, retries + 2):
        try:
            budget.reserve()
        except BudgetExceeded as exc:
            return {**result, "status": "budget_exhausted", "message": str(exc)}
        result.update(attempts=attempt, http_status="")
        limiter.wait()
        should_retry, delay = False, 0.0
        try:
            with opener.open(request, timeout=timeout) as response:
                result["http_status"] = response.status
                if response.status != 200:
                    raise ContentError(f"Unexpected HTTP {response.status}; no file saved.")
                payload = response.read(MAX_RESPONSE_BYTES + 1)
                if len(payload) > MAX_RESPONSE_BYTES:
                    raise ContentError("XML response exceeds the 50 MB safety limit; no file saved.")
                expected = response.headers.get("Content-Length")
                if expected and expected.isdecimal() and len(payload) != int(expected):
                    raise IncompleteRead(b"", max(0, int(expected) - len(payload)))
            article = extract_article(payload, doi)
            with partial.open("wb") as handle:
                handle.write(article)
            os.replace(partial, target)
            return {**result, "status": "downloaded", "bytes": len(article)}
        except HTTPError as exc:
            result["http_status"] = exc.code
            result["message"] = {
                400: "Request rejected; check DOI and API plan.",
                401: "Credential rejected; check the API key and activated service.",
                403: "Service or content access denied; check API entitlements.",
                404: "No article returned by this API; coverage or entitlement may be missing.",
                429: "API quota/rate limit reached; check your allowance before retrying.",
            }.get(exc.code, f"HTTP {exc.code}; consult Springer Nature API support.")
            if exc.code == 404:
                result["status"] = "unavailable"
            should_retry = exc.code in RETRYABLE and attempt <= retries
            if should_retry:
                delay = retry_delay(exc.headers.get("Retry-After"), attempt)
            exc.close()
        except NoRecord as exc:
            return {**result, "status": "unavailable", "message": str(exc)}
        except ContentError as exc:
            return {**result, "message": str(exc)}
        except (URLError, TimeoutError, ConnectionError, HTTPException) as exc:
            # urllib exceptions can contain the secret URL; never format them.
            result["message"] = f"Network error ({type(exc).__name__}); no response or URL logged."
            should_retry = attempt <= retries
            delay = retry_delay(None, attempt)
        except OSError:
            return {**result, "message": "Could not write the XML file; check disk space and permissions."}
        finally:
            partial.unlink(missing_ok=True)
        if not should_retry:
            return result
        print(f"Retrying {doi} in {delay:.0f}s ...", flush=True)
        time.sleep(delay)
    return result


def get_credential(service):
    if service == "oa":
        value = os.environ.get("SPRINGER_OA_API_KEY") or os.environ.get("SPRINGER_API_KEY") or ""
        prompt = "Springer Nature Open Access API key (hidden): "
    else:
        value = os.environ.get("SPRINGER_TDM_API_KEY") or ""
        metric = os.environ.get("SPRINGER_TDM_METRIC", "").strip()
        if value and metric and "/" not in value:
            value += "/" + metric
        prompt = "Springer Nature Full Text API credential (KEY/METRIC; hidden): "
    value = value.strip()
    if not value:
        if not sys.stdin.isatty():
            raise ValueError("Set the matching API credential in the environment, or run in a terminal for a hidden prompt.")
        try:
            value = getpass.getpass(prompt).strip()
        except EOFError:
            raise ValueError("Supply the matching API credential through the environment or a private interactive prompt.") from None
    if not value or not re.fullmatch(r"[!-~]+", value):
        raise ValueError("The API credential is missing or contains unsupported whitespace/characters.")
    if service == "tdm" and (value.count("/") != 1 or not all(value.split("/"))):
        raise ValueError("Full Text API needs the provisioned KEY/METRIC credential, not a metadata/OA key alone.")
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", type=Path, help="TXT DOI list or CSV with a DOI column")
    parser.add_argument("--service", choices=("oa", "tdm"), default="oa")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--doi-column", default="doi")
    parser.add_argument("--limit", type=int, help="Process the first N unique DOIs")
    parser.add_argument("--interval", type=float, default=1.1, help="Seconds between calls; minimum 1")
    parser.add_argument("--timeout", type=float, default=120)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--max-requests", type=int, default=450, help="Per-run request budget, including retries (default: 450)")
    parser.add_argument("--dry-run", action="store_true", help="Validate input and show destinations; no key or network")
    args = parser.parse_args(argv)
    if not math.isfinite(args.interval) or args.interval < 1:
        parser.error("--interval must be finite and at least 1 second.")
    if not math.isfinite(args.timeout) or args.timeout <= 0 or args.retries < 0 or args.max_requests < 1 or (args.limit is not None and args.limit < 1):
        parser.error("Timeout, request budget and optional limit must be positive; retries must be nonnegative.")
    try:
        dois = read_dois(args.input, args.doi_column)
    except (OSError, ValueError, csv.Error) as exc:
        parser.error(str(exc))
    if args.limit is not None:
        dois = dois[:args.limit]
    output = args.output.expanduser().resolve()
    if args.dry_run:
        for doi in dois:
            print(f"{doi} -> {xml_path(output, doi)}")
        print(f"{len(dois)} unique DOI(s); service={args.service}; no requests sent.")
        return 0
    try:
        credential = get_credential(args.service)
    except ValueError as exc:
        parser.error(str(exc))
    output.mkdir(parents=True, exist_ok=True)
    log = output / "results.csv"
    new_log = not log.exists() or log.stat().st_size == 0
    opener, limiter = build_opener(NoRedirects()), RateLimiter(args.interval)
    budget, failures = RequestBudget(args.max_requests), 0
    with log.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        if new_log:
            writer.writeheader()
        for index, doi in enumerate(dois, 1):
            result = download_xml(doi, output, args.service, credential, opener, limiter, budget, args.timeout, args.retries)
            writer.writerow({"time_utc": datetime.now(timezone.utc).isoformat(), **result})
            handle.flush()
            print(f"[{index}/{len(dois)}] {result['status']}: {doi} {result['message']}", flush=True)
            failures += result["status"] not in ("downloaded", "existing")
            if result["status"] == "budget_exhausted" or result["http_status"] in (401, 403, 429):
                print("Stopped; resolve quota or access before rerunning.")
                break
    print(f"Results: {log}; API attempts this run: {budget.used}/{budget.maximum}")
    return 1 if failures else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupted. Rerun the same command to skip validated XML files.", file=sys.stderr)
        sys.exit(130)
