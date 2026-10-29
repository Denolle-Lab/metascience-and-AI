#!/usr/bin/env python3
"""Code papers with any model behind an OpenAI-compatible chat endpoint (OLMo on vLLM, Ai2 or other hosts).

Same protocol as tools/code_papers.py (Claude): the same system prompt (codebook + JSON schema, plus the review addendum
with --review-dir), the same user instruction, the same located publisher text, the same validator. Differences, by design:
  - text only: the model reads the located XML text (tools/jats_text.py, <key>.xml.txt beside the PDF), not the PDF
    images. Papers without XML text are skipped and listed. (On Claude, XML-only and PDF codings agreed within noise:
    private/data/roadmap/derived/format_test.)
  - no batch API: requests run concurrently against the endpoint.

Configuration (keys.env or the shell):
  OPEN_LLM_BASE_URL   e.g. http://localhost:8000/v1   (vLLM: `vllm serve <model>` serves this)
  OPEN_LLM_MODEL      the model name the endpoint expects, e.g. allenai/<olmo model>
  OPEN_LLM_API_KEY    if the endpoint needs one

Commands
  export   write exactly what the model sees, for hand-off: <out>/system.txt, <out>/papers/<key>.user.txt,
           <out>/requests.jsonl (one OpenAI chat request per paper) and <out>/inputs.json (key, doi, licence,
           sha256 of every input text). No endpoint needed.
  run      send the requests, validate each reply, write codings to private/analysis/codings/open/<tag>/<key>.json
           and a run log to private/analysis/codings/open/<tag>/run.json (model, endpoint, prompt sha256, per-paper
           status, tokens, seconds).
  status   counts of ok / invalid / failed for a tag.

Examples
  python tools/code_papers_open.py export --manifest private/data/roadmap/derived/calc1/manifest.jsonl --out /tmp/handoff
  python tools/code_papers_open.py run --manifest private/data/roadmap/derived/r2calc/manifest.jsonl --tag olmo-r2 --workers 4
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import code_papers as cp  # noqa: E402  (loads keys.env; reuses prompt, codebook, validator)

OPEN = cp.PRIVATE / 'analysis' / 'codings' / 'open'


def sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def system_text() -> str:
    return cp.system_blocks()[0]['text']


def user_text(key: str, doi: str, xml_text: str, review_text: str | None, model: str, source: str = 'xml',
              responses_text: str | None = None) -> str:
    head = ('DOCUMENT 1. Publisher full text from XML, with section and paragraph locators.' if source == 'xml'
            else 'DOCUMENT 1. Full text extracted from the PDF, each page headed [p. N].')
    parts = [head + '\n\n' + xml_text]
    if review_text:
        parts.append('DOCUMENT 2. Open review record: referee, author, community and editor comments, with [ID ¶n] or [ID p.n] locators.\n\n' + review_text)
        if responses_text:
            parts.append('DOCUMENT 3. Author responses filed with the revisions (AR files), pages not already in the open review record, '
                         'with [ARn p.k] locators.\n\n' + responses_text)
    instr = (f'Code this paper. key = {key}; doi = {doi}; coder = "{model}"; codebook_version = "{cp.codebook_version()}". '
             + ('Document 1 is the published paper as located text: quote from it and cite its §-locators (codebook section 1).'
                if source == 'xml' else 'Document 1 is the published paper as page text: quote from it and cite PDF pages as "p. N".'))
    if review_text:
        instr += (' Document 2 is its open review record: code a review sequence too, citing the record\'s own locators '
                  '(for example "RC1 ¶4" or "AC2 p.3").')
        instr += (f' Code the disclosures in the authors\' own replies under the review addendum (review_addendum_version = '
                  f'"{cp.review_addendum_version()}"), citing AC' + (' or AR (document 3)' if responses_text else '')
                  + ' locators, and check each against document 1.')
    return '\n\n'.join(parts + [instr])


def pdf_text(pdf: Path) -> str | None:
    """Fallback when there is no publisher XML: pdftotext page by page, each page headed [p. N] (PDF page numbers)."""
    import subprocess
    try:
        raw = subprocess.run(['pdftotext', '-layout', str(pdf), '-'], capture_output=True, text=True, timeout=120).stdout
    except Exception:
        return None
    pages = raw.split('\f')
    txt = '\n\n'.join(f'[p. {i}]\n{pg.strip()}' for i, pg in enumerate(pages, 1) if pg.strip())
    return txt if len(txt) > 5000 else None


def inputs(args) -> tuple[list, list]:
    cands = cp.candidates(args)
    rows, skipped = [], []
    for k in sorted(cands):
        x, src = cp.xml_text_for(cp.queue_file(cands[k]['file'])), 'xml'
        if not x and getattr(args, 'pdf_text', False):
            x, src = pdf_text(cp.queue_file(cands[k]['file'])), 'pdftotext'
        if not x:
            skipped.append(k); continue
        if len(x) > getattr(args, 'max_chars', 200000):
            skipped.append(k + ' (too long: %d chars)' % len(x)); continue
        rows.append({'key': k, 'doi': cands[k]['doi'], 'xml': x, 'source': src, 'review': cp.review_text_for(k),
                     'responses': cp.author_responses_for(k)})
    return rows, skipped


def request(r: dict, model: str, max_tokens: int) -> dict:
    return {'model': model, 'max_tokens': max_tokens, 'temperature': 0,
            'response_format': {'type': 'json_object'},
            'messages': [{'role': 'system', 'content': system_text()},
                         {'role': 'user', 'content': user_text(r['key'], r['doi'], r['xml'], r['review'], model, r['source'], r['responses'])}]}


def cmd_export(args) -> None:
    rows, skipped = inputs(args)
    out = Path(args.out); (out / 'papers').mkdir(parents=True, exist_ok=True)
    (out / 'system.txt').write_text(system_text())
    model = os.environ.get('OPEN_LLM_MODEL', '<model>')
    meta = []
    with open(out / 'requests.jsonl', 'w') as f:
        for r in rows:
            u = user_text(r['key'], r['doi'], r['xml'], r['review'], model, r['source'], r['responses'])
            (out / 'papers' / f"{r['key']}.user.txt").write_text(u)
            f.write(json.dumps({'custom_id': r['key'], 'body': request(r, model, args.max_tokens)}, ensure_ascii=False) + '\n')
            meta.append({'key': r['key'], 'doi': r['doi'], 'text_source': r['source'], 'xml_sha256': sha(r['xml']),
                         'review_sha256': sha(r['review']) if r['review'] else None,
                         'responses_sha256': sha(r['responses']) if r['responses'] else None, 'user_chars': len(u)})
    (out / 'inputs.json').write_text(json.dumps({'codebook_version': cp.codebook_version(), 'system_sha256': sha(system_text()),
                                                'review_addendum': cp.review_addendum_version() if cp.REVIEW_DIR else None,
                                                'papers': meta, 'skipped_no_xml': skipped}, indent=1))
    print(f'{len(rows)} papers exported to {out} ({len(skipped)} skipped: no text, or too long). '
          'Before sharing, check each paper\'s licence: subscription full text may not be redistributed.')


def call(base: str, key: str | None, body: dict, timeout: int) -> dict:
    req = urllib.request.Request(base.rstrip('/') + '/chat/completions', data=json.dumps(body).encode(),
                                 headers={'Content-Type': 'application/json', **({'Authorization': f'Bearer {key}'} if key else {})})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def cmd_run(args) -> None:
    base, model = os.environ.get('OPEN_LLM_BASE_URL'), os.environ.get('OPEN_LLM_MODEL')
    if not base or not model:
        sys.exit('set OPEN_LLM_BASE_URL and OPEN_LLM_MODEL (keys.env or shell)')
    apikey = os.environ.get('OPEN_LLM_API_KEY')
    out = OPEN / args.tag; out.mkdir(parents=True, exist_ok=True)
    logf = out / 'run.json'
    log = json.loads(logf.read_text()) if logf.is_file() else {'model': model, 'endpoint': base, 'codebook_version': cp.codebook_version(),
                                                              'system_sha256': sha(system_text()), 'papers': {}}
    rows, skipped = inputs(args)
    todo = [r for r in rows if log['papers'].get(r['key'], {}).get('status') != 'ok'][: args.limit or None]
    print(f'{len(todo)} to code with {model} at {base}; {len(skipped)} skipped (no text, or too long)')

    def one(r):
        t0 = time.time()
        try:
            resp = call(base, apikey, request(r, model, args.max_tokens), args.timeout)
            text = resp['choices'][0]['message']['content']
            ok, why = cp.write_coding(r['key'], text, out)
            rec = {'status': 'ok' if ok else 'invalid', 'why': why, 'usage': resp.get('usage'),
                   'finish_reason': resp['choices'][0].get('finish_reason')}
        except Exception as e:  # network, HTTP, malformed response
            rec = {'status': 'failed', 'why': repr(e)[:300]}
        rec.update({'text_source': r['source'], 'seconds': round(time.time() - t0, 1), 'xml_sha256': sha(r['xml']),
                    'review_sha256': sha(r['review']) if r['review'] else None,
                    'responses_sha256': sha(r['responses']) if r['responses'] else None, 'date': time.strftime('%Y-%m-%d %H:%M')})
        return r['key'], rec

    with ThreadPoolExecutor(args.workers) as ex:
        for k, rec in ex.map(one, todo):
            log['papers'][k] = rec
            logf.write_text(json.dumps(log, indent=1))
            print(k, rec['status'], rec.get('why', '')[:100])
    cmd_status(args)


def cmd_status(args) -> None:
    logf = OPEN / args.tag / 'run.json'
    if not logf.is_file():
        sys.exit(f'no run log for tag {args.tag}')
    from collections import Counter
    log = json.loads(logf.read_text())
    print(args.tag, log['model'], dict(Counter(p['status'] for p in log['papers'].values())))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    for name in ('export', 'run', 'status'):
        s = sub.add_parser(name)
        s.add_argument('--manifest'); s.add_argument('--keys')
        s.add_argument('--review-dir', help='attach <dir>/<key>/discussion.txt and the author-responses document; code a review '
                       'sequence and disclosures (review addendum)')
        s.add_argument('--max-tokens', type=int, default=32000)
        s.add_argument('--tag', default='open-run1')
        s.add_argument('--pdf-text', action='store_true', help='use pdftotext page text when a paper has no publisher XML')
        s.add_argument('--max-chars', type=int, default=200000, help='skip papers whose text is longer (context limit)')
    sub.choices['export'].add_argument('--out', required=True)
    sub.choices['run'].add_argument('--workers', type=int, default=4)
    sub.choices['run'].add_argument('--limit', type=int, default=0)
    sub.choices['run'].add_argument('--timeout', type=int, default=1800)
    a = ap.parse_args()
    cp.REVIEW_DIR = a.review_dir
    {'export': cmd_export, 'run': cmd_run, 'status': cmd_status}[a.cmd](a)


if __name__ == '__main__':
    main()
