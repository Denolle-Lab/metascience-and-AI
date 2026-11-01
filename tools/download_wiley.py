#!/usr/bin/env python3
"""Download Wiley article PDFs from a TXT/CSV DOI list (Python 3.10+, no packages).

Usage: python3 tools/download_wiley.py private/dois.txt --limit 1
Token: WILEY_TDM_TOKEN or TDM_API_TOKEN environment variable, or hidden prompt.
Instructions: https://onlinelibrary.wiley.com/library-info/resources/text-and-datamining
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
from urllib.parse import quote, unquote, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


API = "https://api.wiley.com/onlinelibrary/tdm/v1/articles/"
MIN_INTERVAL = 10.1  # 60 API requests per 10 minutes, with a small margin.
RETRYABLE = {408, 429, 500, 502, 503, 504}
FIELDS = ["time_utc", "doi", "status", "http_status", "path", "bytes", "attempts", "message"]


def normalize_doi(value: str) -> str:
    value = value.strip()
    if re.match(r"https?://(?:dx\.)?doi\.org/", value, re.I):
        # Decode DOI URLs; do not strip punctuation that might belong to a DOI.
        value = unquote(urlsplit(value).path.lstrip("/"))
    value = re.sub(r"^doi:\s*", "", value, flags=re.I).strip()
    if not re.fullmatch(r"10\.\d{4,9}/[^\s\x00-\x1f\x7f]+", value):
        raise ValueError(f"Not a DOI or DOI URL: {value!r}")
    return value.lower()


def read_dois(path: Path, column: str = "doi") -> list[str]:
    """Read one DOI per line, or a CSV with a DOI column; preserve input order."""
    with path.open(encoding="utf-8-sig", newline="") as handle:
        if path.suffix.lower() == ".csv":
            reader = csv.DictReader(handle)
            headers = {key.strip().lower(): key for key in (reader.fieldnames or [])}
            if column.lower() not in headers:
                raise ValueError(f"CSV needs a {column!r} column. Use --doi-column for another name.")
            values = [(i, row.get(headers[column.lower()], "") or "")
                      for i, row in enumerate(reader, 2)]
        else:
            values = [(i, line) for i, line in enumerate(handle, 1)
                      if line.strip() and not line.lstrip().startswith("#")]
    result, seen, errors = [], set(), []
    for line, value in values:
        if not value.strip():
            continue
        try:
            doi = normalize_doi(value)
        except ValueError as exc:
            errors.append(f"line {line}: {exc}")
            continue
        if doi not in seen:
            result.append(doi)
            seen.add(doi)
    if errors:
        raise ValueError("Fix these input entries before downloading:\n" + "\n".join(errors[:10]))
    if not result:
        raise ValueError("No DOIs found in the input file.")
    return result


def pdf_path(output: Path, doi: str) -> Path:
    # A flat, portable filename, even for long DOIs or DOIs containing slashes.
    digest = hashlib.sha256(doi.encode()).hexdigest()[:12]
    return output / f"{quote(doi, safe='')[:160]}--{digest}.pdf"


def is_pdf(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            return handle.read(5) == b"%PDF-" and path.stat().st_size > 5
    except OSError:
        return False


class SafeRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urlsplit(newurl).scheme != "https":
            raise URLError("Refusing a redirect to a non-HTTPS download URL")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class RateLimiter:
    def __init__(self, interval: float):
        self.interval = interval
        self.next_request = 0.0

    def wait(self):
        delay = self.next_request - time.monotonic()
        if delay > 0:
            time.sleep(delay)
        self.next_request = time.monotonic() + self.interval


def retry_delay(headers, attempt: int, status: int | None) -> float:
    value = headers.get("Retry-After") if headers else None
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
            return max(MIN_INTERVAL, seconds)
    return 600.0 if status == 429 else max(MIN_INTERVAL, 30.0 * 2 ** (attempt - 1))


def http_message(code: int) -> str:
    return {
        400: "Wiley rejected the request; check the DOI and TDM token.",
        401: "Authentication failed; check the TDM token.",
        403: "Token or access rejected; check token and institutional access.",
        404: "Article unavailable, or the script's public IP lacks subscription access.",
        429: "Wiley rate limit reached; retry later or reduce shared usage.",
    }.get(code, f"HTTP {code}; see Wiley's TDM documentation.")


def download_pdf(doi, output, token, opener, limiter, timeout=120, retries=3):
    target = pdf_path(output, doi)
    result = dict(doi=doi, status="failed", http_status="", path=str(target),
                  bytes=0, attempts=0, message="")
    if is_pdf(target):
        return {**result, "status": "existing", "bytes": target.stat().st_size}
    partial = target.with_suffix(".pdf.part")
    for attempt in range(1, retries + 2):
        result["attempts"] = attempt
        result["http_status"] = ""
        limiter.wait()
        request = Request(API + quote(doi, safe=""), headers={
            "Accept": "application/pdf", "User-Agent": "WileyDOIDownloader/1.0"})
        # Wiley authenticates the initial API call. Never forward the secret to
        # the redirected file server, and never put it in a URL or results log.
        request.add_unredirected_header("Wiley-TDM-Client-Token", token)
        should_retry, delay = False, 0.0
        try:
            with opener.open(request, timeout=timeout) as response:
                result["http_status"] = response.status
                if response.status != 200:
                    result["message"] = f"Unexpected HTTP {response.status}; no file saved."
                    return result
                with partial.open("wb") as handle:
                    first = response.read(1024)
                    if not first.startswith(b"%PDF-") or len(first) <= 5:
                        result["message"] = "Response was not a PDF; no file saved."
                        return result
                    handle.write(first)
                    while chunk := response.read(1024 * 1024):
                        handle.write(chunk)
                actual = partial.stat().st_size
                length = response.headers.get("Content-Length")
                if length and length.isdecimal() and actual != int(length):
                    raise IncompleteRead(b"", int(length) - actual)
                os.replace(partial, target)
                return {**result, "status": "downloaded", "bytes": actual, "message": ""}
        except HTTPError as exc:
            result["http_status"] = exc.code
            result["message"] = http_message(exc.code)
            should_retry = exc.code in RETRYABLE and attempt <= retries
            if should_retry:
                delay = retry_delay(exc.headers, attempt, exc.code)
            exc.close()
        except (URLError, TimeoutError, ConnectionError, HTTPException) as exc:
            # Do not log exception text: URLs or server messages could contain secrets.
            result["message"] = f"Network error ({type(exc).__name__})."
            should_retry = attempt <= retries
            delay = retry_delay(None, attempt, None)
        except OSError:
            result["message"] = "File write or incomplete download error; check disk space and permissions."
            return result
        finally:
            partial.unlink(missing_ok=True)
        if not should_retry:
            return result
        print(f"Retrying {doi} in {delay:.0f}s ...", flush=True)
        time.sleep(delay)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", type=Path, help="TXT: one DOI per line; CSV: a DOI column")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "private" / "pdfs" / "wiley",
                        help="Destination (default: repository private/pdfs/wiley)")
    parser.add_argument("--doi-column", default="doi", help="CSV column name (default: doi)")
    parser.add_argument("--limit", type=int, help="Process only the first N unique DOIs")
    parser.add_argument("--interval", type=float, default=MIN_INTERVAL, help="Seconds between API calls (minimum 10.1)")
    parser.add_argument("--timeout", type=float, default=120, help="Network timeout in seconds")
    parser.add_argument("--retries", type=int, default=3, help="Retries for transient failures (default: 3)")
    parser.add_argument("--dry-run", action="store_true", help="Validate inputs and show filenames; no network or token needed")
    args = parser.parse_args(argv)
    if not math.isfinite(args.interval) or args.interval < MIN_INTERVAL:
        parser.error("--interval must be at least 10.1 seconds to respect Wiley's sustained rate limit.")
    if not math.isfinite(args.timeout) or args.timeout <= 0 or args.retries < 0 or (args.limit is not None and args.limit < 1):
        parser.error("--timeout and --limit must be positive; --retries must be nonnegative.")
    try:
        dois = read_dois(args.input, args.doi_column)
    except (OSError, ValueError, csv.Error) as exc:
        parser.error(str(exc))
    if args.limit:
        dois = dois[:args.limit]
    if args.dry_run:
        for doi in dois:
            print(f"{doi} -> {pdf_path(args.output, doi)}")
        print(f"{len(dois)} unique DOI(s); no requests sent.")
        return 0
    token = (os.environ.get("WILEY_TDM_TOKEN") or os.environ.get("TDM_API_TOKEN") or "").strip()
    if not token:
        try:
            token = getpass.getpass("Wiley TDM token (hidden): ").strip()
        except EOFError:
            parser.error("Provide WILEY_TDM_TOKEN, TDM_API_TOKEN, or run interactively to enter the token.")
    if not token or re.search(r"[\r\n]", token):
        parser.error("A nonempty TDM token without line breaks is required.")
    output = args.output.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    log = output / "results.csv"
    new_log = not log.exists() or log.stat().st_size == 0
    opener, limiter = build_opener(SafeRedirects()), RateLimiter(args.interval)
    failures = 0
    with log.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        if new_log:
            writer.writeheader()
        for index, doi in enumerate(dois, 1):
            result = download_pdf(doi, output, token, opener, limiter, args.timeout, args.retries)
            writer.writerow({"time_utc": datetime.now(timezone.utc).isoformat(), **result})
            handle.flush()
            print(f"[{index}/{len(dois)}] {result['status']}: {doi} {result['message']}", flush=True)
            failures += result["status"] == "failed"
            if result["http_status"] in (401, 403) and result["status"] == "failed":
                print("Stopping to avoid repeating token/access failures. Fix access and rerun.")
                break
    print(f"Results: {log}")
    return 1 if failures else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupted. Rerun the same command to skip existing PDFs.", file=sys.stderr)
        sys.exit(130)
