"""OLMo hand-off package: freeze the fixed paper set and the task definitions, so an open-weight model reruns the same tasks.

Decided by the PI on October 28, 2026 (DECISIONS.md): keep a fixed paper set and fixed task definitions (prompts,
schemas, inputs with hashes) so that the same tasks can be rerun with OLMo later (tools/code_papers_open.py). This
script writes, per task, what an open model reads, with sha256 of every input, the versions and commits of the
instruments, and an index of the Claude outputs it will be compared with. It makes no model call.

Tasks
  inquiry  codebook coding (agents/coder/CODEBOOK.md, coding.schema.json; validator tools/check_coding.py). Papers: every
           paper of the round-1 and round-2 manifests (derived/calc1, derived/r2calc) sent to Claude under tag calc1 or
           r2. Claude outputs: calc1, r2; the test-retest replicate gold-r2 (E2).
  review   the review coding of the reconstruction plan (tools/roadmap/g34_reconstruction.py): the inquiry call with the
           open-review record, the author-responses document and the review addendum attached (code_papers.py
           --review-dir private/data/roadmap/review; agents/coder/REVIEW_ADDENDUM.md 1.0.0, review_addendum.schema.json;
           max_tokens code_papers.REVIEW_MAX_TOKENS). Papers: Copernicus papers (DOI prefix 10.5194) of the round-1 and
           round-2 manifests and of the cop22 draw (derived/cop22/draw_manifest.jsonl) with review/<key>/discussion.txt
           over 400 bytes (code_papers.review_text_for) and full text on disk, whether or not sent to Claude yet, so the
           set is fixed before the v2 run. Claude outputs: the g34 review tags (calc1-review-v2, r2-review-v2,
           cop22-review-v2). The E3 codings (calc1-review) were made without the addendum and are not this task.
  inquiry-cop22  the inquiry task on the Copernicus papers of the cop22 draw with full text on disk, fixed before they
           are coded. Claude outputs: cop22.
  advance  blind advance coding (agents/advance/RUBRIC.md, advance.schema.json; validator tools/check_advance.py) on the
           blinded text read from the cache private/data/roadmap/blind/<key>.txt, which must be at the current
           tools/blind_text.py BLIND_VERSION (this script never rebuilds it). Papers: every paper with a valid inquiry
           coding under calc1 or r2 (the g24 full-run population). Claude outputs: every *-advance folder.

What the open model reads
  system   the Claude system prompt of the task, byte for byte (code_papers.system_blocks()).
  user     inquiry and review: tools/code_papers_open.py user_text(), text only: the located publisher XML text
           (<key>.xml.txt) when there is one, else pdftotext -layout page text (code_papers_open.pdf_text; papers under
           5,000 characters are skipped), plus the review record for the review task. Claude read the PDF (text and page
           images) as well, and the XML text when there was one: claude_content in papers.jsonl lists each block it
           received with its sha256 and the exact instruction line. advance: 'DOCUMENT 1. ' + the title Claude's
           document block carried + the blinded text + Claude's instruction line, unchanged (opaque key P + 10 hex of
           the blinded text's sha256).
  model    every user file is written with coder = "<model>" (MODEL_SLOT); the runner puts the model name there, as
           code_papers_open does. Hashes are of the files as written.
  request  temperature 0, response_format json_object, max_tokens 32,000 (inquiry, review; code_papers_open default)
           or ADVANCE_MAX_TOKENS (advance). Claude's settings are recorded beside them.

Per task, private/data/roadmap/handoff/<task>/ (private: it holds paper text)
  handoff.json         task definition: versions, sha256 and last commit of every instrument file, system sha256,
                       request settings, validator and comparison commands, counts, exclusions with reasons, the Claude
                       batches with the system prompt their commit builds, set hashes
  system.txt           the system prompt
  user/<key>.user.txt  the user message per paper
  papers.jsonl         per paper: key, doi, round, OpenAlex id, in_gold, text route, sha256 of every input text (paper
                       text, PDF, XML text, review record, blinded text), user sha256 and length, estimated input tokens
                       (characters / 2.7: the 10,884-token inquiry prefix is 29,600 characters), Claude's content blocks
  claude_outputs.jsonl one row per Claude coding file of the task's papers: tag, folder, file, sha256, status (valid /
                       invalid as validated now for inquiry and review; as collected for advance), coder, answering model
                       when recorded, batch, submission time, usage, cost, and drift checks (PDF sha256 against the
                       uploaded file; XML text and review record modified after submission; blinded text as sent)
  SHA256SUMS           sha256 of every file above (shasum -a 256 -c SHA256SUMS)
Public: preregistration/handoff-manifest.json, versions and hashes only (no keys, DOIs, paper text or abstracts; the
gold papers under embargo, g22_release.py, are not named), one block per frozen task.

Freeze rule. A task folder with handoff.json is frozen. Rerunning `freeze` compares the input definition (system.txt and
papers.jsonl hashes): identical, it reports so and writes nothing (with --update-outputs it rewrites the Claude output
index, the instrument file hashes (the frozen ones kept as files_at_freeze), SHA256SUMS and the public manifest);
different, it refuses and counts the changed papers. --refreeze moves the
old folder to handoff/_superseded/<task>-<frozen date>-<papers sha256 prefix>/ and writes a new one. --dry-run builds
everything in memory, prints what would be written, and writes nothing (no MANIFEST line).

verify    recomputes the inputs from the sources and compares them with the frozen hashes (source drift: a refetched
          XML, a different pdftotext); with --open-tag TAG also compares the prompt and per-paper text hashes of
          private/analysis/codings/open/<TAG>/run.json (code_papers_open run) with the frozen ones.
requests  writes an OpenAI batch file (vLLM run_batch format: custom_id, method, url, body) from the frozen folder for a
          given model name, after checking every user file against its sha256: the route for the advance task, which
          code_papers_open does not run.

Inputs   private/download-queue.json; derived/{calc1,r2calc}/manifest.jsonl; pdfs (PDF, <key>.xml.txt);
         review/<key>/discussion.txt; blind/<key>.{txt,json}; derived/advance/pilot_keys.json;
         derived/gold/human_assignment.json and derived/entry/audit_sample.json (embargo, public manifest only);
         private/analysis/codings/api/<tag>/ and state.json (read only); git history of the public repository
Outputs  private/data/roadmap/handoff/<task>/; preregistration/handoff-manifest.json; a MANIFEST.md row per write
Run:     python tools/roadmap/g33_handoff.py freeze --task inquiry [--dry-run] [--refreeze] [--update-outputs]
         python tools/roadmap/g33_handoff.py verify --task inquiry [--open-tag olmo-r1]
         python tools/roadmap/g33_handoff.py requests --task advance --model allenai/<olmo> --out <file.jsonl>
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

from common import ROOT, PRIVATE, DATA, DERIVED, TODAY, write_json, read_json, log, rel

import code_papers as cp
import code_papers_open as cpo
from check_coding import validate, DISCLOSURE_CHECKS

HANDOFF = DATA / 'handoff'
PUBLIC = ROOT / 'preregistration' / 'handoff-manifest.json'
API = PRIVATE / 'analysis' / 'codings' / 'api'
OPEN = PRIVATE / 'analysis' / 'codings' / 'open'
MODEL_SLOT = '<model>'
CHARS_PER_TOKEN = 2.7          # inquiry prefix: 29,600 characters, 10,884 tokens (EXPERIMENTS.md E7)
OPEN_MAX_CHARS = 200000        # code_papers_open --max-chars default: longer papers are skipped by the runner
COPERNICUS = '10.5194/'
MINUTE = dt.timedelta(minutes=1)  # state.json submission times have minute resolution: a file written in that minute is not later
ADVANCE_TITLE = None           # set from code_papers.params: the title of Claude's document block
TASKS = {
    'inquiry': {'claude_tags': ['calc1', 'r2'], 'replicate_tags': ['gold-r2'], 'effort': 'high', 'max_tokens': 32000,
                'files': ['agents/coder/CODEBOOK.md', 'agents/coder/coding.schema.json', 'agents/coder/definitions.json',
                          'tools/check_coding.py', 'tools/code_papers.py', 'tools/code_papers_open.py', 'tools/jats_text.py'],
                'validator': 'python tools/check_coding.py validate <coding.json>',
                'compare': 'python tools/check_coding.py agree-dir private/analysis/codings/api/<calc1|r2> private/analysis/codings/open/<tag>'},
    'review': {'claude_tags': ['calc1-review-v2', 'r2-review-v2', 'cop22-review-v2'], 'replicate_tags': [], 'effort': 'high',
               'max_tokens': cp.REVIEW_MAX_TOKENS,
               'files': ['agents/coder/CODEBOOK.md', 'agents/coder/coding.schema.json', 'agents/coder/definitions.json',
                         'agents/coder/REVIEW_ADDENDUM.md', 'agents/coder/review_addendum.schema.json',
                         'tools/check_coding.py', 'tools/code_papers.py', 'tools/code_papers_open.py', 'tools/jats_text.py',
                         'tools/roadmap/g15_open_review.py', 'tools/roadmap/g27_author_responses.py',
                         'tools/roadmap/g34_reconstruction.py'],
               'validator': 'check_coding.validate(coding, review=True, texts=code_papers.review_texts(key), '
                            'checks=check_coding.DISCLOSURE_CHECKS) with code_papers.REVIEW_DIR = private/data/roadmap/review; '
                            'then check_coding.kept_disclosures(coding, texts) (rule item: a disclosure failing a quote check is '
                            'dropped and counted, the coding stays valid); g34 adds the C2 checks (review_addendum_version '
                            '1.0.0, >= 1 review step by a referee, editor or commenter)',
               'compare': 'python tools/check_coding.py agree-dir private/analysis/codings/api/<review tag> private/analysis/codings/open/<tag>; '
                          'disclosures: tools/roadmap/g30_disclosure_agreement.py --codings private/analysis/codings/open/<tag>; '
                          'the plan: tools/roadmap/g34_reconstruction.py features --set NAME=<inquiry>,<tag>,plan,open'},
    'inquiry-cop22': {'claude_tags': ['cop22'], 'replicate_tags': [], 'effort': 'high', 'max_tokens': 32000,
                      'files': ['agents/coder/CODEBOOK.md', 'agents/coder/coding.schema.json', 'agents/coder/definitions.json',
                                'tools/check_coding.py', 'tools/code_papers.py', 'tools/code_papers_open.py', 'tools/jats_text.py'],
                      'validator': 'python tools/check_coding.py validate <coding.json>',
                      'compare': 'python tools/check_coding.py agree-dir private/analysis/codings/api/cop22 private/analysis/codings/open/<tag>'},
    'advance': {'claude_tags': None, 'replicate_tags': [], 'effort': cp.ADVANCE_EFFORT, 'max_tokens': cp.ADVANCE_MAX_TOKENS,
                'files': ['agents/advance/RUBRIC.md', 'agents/advance/advance.schema.json', 'tools/check_advance.py',
                          'tools/blind_text.py', 'tools/jats_text.py', 'tools/code_papers.py', 'tools/roadmap/g24_advance.py'],
                'validator': 'check_advance.normalize then check_advance.validate(coding, text=<blinded text>, key=<key>), after '
                             'mapping the opaque key back (code_papers.write_advance with TASK = "advance")',
                'compare': 'python tools/roadmap/g24_advance.py pilot --tags <claude tag>,<open tag> (test-retest block: verdict and '
                           'score alpha between the two tags)'},
}


def sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def sha_file(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def git(*a, cwd=ROOT) -> str:
    return subprocess.run(['git', '-C', str(cwd), *a], capture_output=True, text=True).stdout.strip()


def set_task(task: str) -> None:
    cp.TASK = 'advance' if task == 'advance' else 'inquiry'
    cp.NO_XML = False
    cp.REVIEW_DIR = str(DATA / 'review') if task == 'review' else None


ROUND_TAG = {'inquiry': {'round1': 'calc1', 'round2': 'r2'}, 'inquiry-cop22': {'cop22': 'cop22'},
             'review': {'round1': 'calc1-review-v2', 'round2': 'r2-review-v2', 'cop22': 'cop22-review-v2'}}


# ------------------------------------------------------------------------------------------------ papers
def manifests(task: str = 'inquiry') -> dict:
    """The round-1 and round-2 manifests; for the review and inquiry-cop22 tasks also the cop22 draw (round 'cop22')."""
    out = {}
    srcs = [('round1', DERIVED / 'calc1' / 'manifest.jsonl'), ('round2', DERIVED / 'r2calc' / 'manifest.jsonl')]
    if task in ('review', 'inquiry-cop22'):
        srcs.append(('cop22', DERIVED / 'cop22' / 'draw_manifest.jsonl'))
    for rnd, p in srcs:
        for l in (p.read_text().splitlines() if p.is_file() else []):
            if l.strip():
                r = json.loads(l)
                out.setdefault(r['key'], {**r, 'round': rnd})
    return out


def pilot_keys() -> list[str]:
    f = DERIVED / 'advance' / 'pilot_keys.json'
    return read_json(f)['keys'] if f.is_file() else []


def embargoed() -> set:
    D = DERIVED
    ha = json.loads((D / 'gold' / 'human_assignment.json').read_text())['data']['papers']
    au = json.loads((D / 'entry' / 'audit_sample.json').read_text())['data']['rows']
    return {p['key'] for p in ha} | {r['key'] for r in au}


def population(task: str, st: dict, man: dict, queue: dict) -> tuple[list[str], list[dict]]:
    """(keys of the task's paper set, excluded manifest papers with reasons)."""
    have = {k for k, v in queue.items() if v.get('status') == 'have' and v.get('file') and cp.queue_file(v['file']).exists()}
    sent = {k for b in st['batches'] if b['tag'] in ('calc1', 'r2') for k in b['keys']}
    excl = []
    if task == 'inquiry':
        keys = sorted(k for k in man if k in sent and k in have)
        excl += [{'key': k, 'reason': 'no full text on disk' if k not in have else 'not sent to Claude'} for k in sorted(set(man) - set(keys))]
    elif task == 'inquiry-cop22':
        cop = sorted(k for k in man if man[k]['round'] == 'cop22' and (man[k].get('doi') or '').lower().startswith(COPERNICUS))
        keys = [k for k in cop if k in have]
        excl += [{'key': k, 'reason': 'no full text on disk'} for k in cop if k not in keys]
    elif task == 'review':
        cop = sorted(k for k in man if (man[k].get('doi') or '').lower().startswith(COPERNICUS))
        keys = [k for k in cop if k in have and cp.review_text_for(k)]
        excl += [{'key': k, 'reason': 'no full text on disk' if k not in have else
                  'no open-review record on disk (g15_open_review.py not run for it)' if not (DATA / 'review' / k).is_dir() else
                  'review record of 400 bytes or less'} for k in cop if k not in keys]
    else:
        valid = set()
        for tag in ('calc1', 'r2'):
            for f in sorted((API / tag).glob('g22_*.json')):
                c = json.loads(f.read_text())
                if not validate(c):
                    valid.add(c['key'])
        keys = sorted(k for k in man if k in valid and k in have)
        excl += [{'key': k, 'reason': 'no valid inquiry coding (calc1 or r2)'} for k in sorted(set(man) - set(keys)) if k in have]
    return keys, excl


def responses_readonly(k: str) -> str | None:
    """code_papers.author_responses_for without its cache write: the cached text when its source hashes are current,
    else the g27 AR units computed here and not stored. None when the function does not exist (before the addendum)."""
    if not hasattr(cp, 'author_responses_for') or not cp.review_text_for(k):
        return None
    rd = Path(cp.REVIEW_DIR)
    srcs = [rd / k / 'discussion.txt'] + sorted(rd.joinpath(k).glob('*-AR*.pdf'), key=lambda p: int(p.stem.rsplit('-AR', 1)[1]))
    if len(srcs) == 1:
        return None
    head = '# sources: ' + ' '.join(f'{p.name}={sha_file(p)[:16]}' for p in srcs)
    cache = DERIVED / 'review' / 'author_responses' / f'{k}.txt'
    if cache.is_file() and cache.read_text().split('\n', 2)[1] == head:
        return cache.read_text().split('\n', 2)[2] or None
    import g27_author_responses as g27
    ac = g27.ac_units(k, review=rd)
    ar, _ = g27.ar_units(k, ' '.join(u['text'] for u in ac), review=rd)
    return ''.join(f'[{u["unit"]}] {u["text"]}\n' for u in ar) or None


def claude_content(p: dict) -> list[dict]:
    """Claude's user content blocks with document texts replaced by their sha256 (the PDF by the queue file's sha256)."""
    out = []
    for b in p['messages'][0]['content']:
        if b['type'] == 'document' and b['source']['type'] == 'file':
            out.append({'block': 'document', 'source': 'pdf (Files API upload)'})
        elif b['type'] == 'document':
            out.append({'block': 'document', 'title': b.get('title'), 'source': 'text', 'sha256': sha(b['source']['data']),
                        'chars': len(b['source']['data'])})
        else:
            out.append({'block': 'text', 'text': b['text']})
    return out


def build_paper(task: str, k: str, m: dict, queue: dict, sent_at: dt.datetime | None = None) -> tuple[dict | None, str | None, str | None]:
    """(row, user text, skip reason) for one paper. sent_at: submission time of the batch behind the paper's Claude coding
    under the task's main tag; an XML text written after it was not in Claude's request (the Elsevier XML fetched on
    October 27, 2026, after the first calc1 and r2 batches), so claude_content leaves it out and claude_read_xml is false."""
    global ADVANCE_TITLE
    pdf = cp.queue_file(queue[k]['file'])
    row = {'key': k, 'doi': m.get('doi'), 'round': m['round'], 'openalex': m.get('openalex'), 'in_gold': bool(m.get('in_gold')),
           'pdf_sha256': sha_file(pdf)}
    xml = cp.xml_text_for(pdf)
    xml_claude = xml
    if xml is not None:
        row['xml_txt_sha256'] = sha(xml)
        x = pdf.with_suffix('.xml.txt')
        if sent_at and dt.datetime.fromtimestamp(x.stat().st_mtime, sent_at.tzinfo) > sent_at + MINUTE:
            xml_claude = None
    if task == 'advance':
        import blind_text
        text, f = blind_text.cached(k), blind_text.CACHE / f'{k}.json'
        meta = json.loads(f.read_text()) if f.is_file() else {}
        if text is None or meta.get('blind_version') != blind_text.BLIND_VERSION or meta.get('output_sha256') != sha(text):
            return None, None, (f'blinded text not at blind {blind_text.BLIND_VERSION} in the cache (found '
                                f'{meta.get("blind_version") or "none"}); build it with tools/blind_text.py')
        p = cp.params(k, m.get('doi'), None, TASKS['advance']['effort'], TASKS['advance']['max_tokens'], blind=text)
        doc, instr = p['messages'][0]['content']
        ADVANCE_TITLE = doc['title']
        user = f'DOCUMENT 1. {doc["title"]}.\n\n{text}\n\n' + instr['text'].replace(f'coder = "{cp.MODEL}"', f'coder = "{MODEL_SLOT}"')
        row.update({'text_source': meta.get('source'), 'paper_text_sha256': sha(text), 'paper_text_chars': len(text),
                    'blind_version': meta.get('blind_version'), 'blind_input_sha256': meta.get('input_sha256'),
                    'opaque_key': cp.opaque_key(text)})
    else:
        text, src = (xml, 'xml') if xml else (cpo.pdf_text(pdf), 'pdftotext')
        if not text:
            return None, None, 'no XML text and pdftotext gave under 5,000 characters'
        review = cp.review_text_for(k) if task == 'review' else None
        resp = responses_readonly(k) if task == 'review' else None
        open_kw = {'responses_text': resp} if 'responses_text' in cpo.user_text.__code__.co_varnames else {}
        user = cpo.user_text(k, m.get('doi'), text, review, MODEL_SLOT, src, **open_kw)
        kw = {'responses_text': resp} if resp and 'responses_text' in cp.params.__code__.co_varnames else {}
        p = cp.params(k, m.get('doi'), 'file-placeholder', TASKS[task]['effort'], TASKS[task]['max_tokens'], xml_text=xml_claude,
                      review_text=review, **kw)
        if task == 'review' and not open_kw:
            # a code_papers_open without the review addendum: add the author-responses document and the disclosure sentence
            # of Claude's instruction here
            body, instr = user.rsplit('\n\n', 1)
            claude_instr = p['messages'][0]['content'][-1]['text']
            i = claude_instr.find(' Code the disclosures')
            add = claude_instr[i:claude_instr.find('published paper.', i) + len('published paper.')] if i >= 0 else ''
            if resp:
                body += ('\n\nDOCUMENT 3. Author responses filed with the revisions (AR files), pages not already in the open review '
                         'record, with [ARn p.k] locators.\n\n' + resp)
            user = body + '\n\n' + instr + add
        row.update({'text_source': src, 'paper_text_sha256': sha(text), 'paper_text_chars': len(text),
                    'claude_read_xml': xml_claude is not None})
        if review:
            row['review_sha256'] = sha(review)
            row['review_chars'] = len(review)
        if resp:
            row['author_responses_sha256'] = sha(resp)
            row['author_responses_chars'] = len(resp)
    row['claude_content'] = claude_content(p)
    row.update({'user_file': f'user/{k}.user.txt', 'user_sha256': sha(user), 'user_chars': len(user),
                'over_open_max_chars': row['paper_text_chars'] > OPEN_MAX_CHARS})
    return row, user, None


# ------------------------------------------------------------------------------------------------ Claude runs
_COMMITS = None


def sent_at(task: str, k: str, st: dict, man: dict) -> dt.datetime | None:
    """Submission time of the batch behind the paper's coding under the task's main Claude tag (inquiry: calc1 or r2 by
    round; review: calc1-review); None for advance and for papers never submitted."""
    tag = ROUND_TAG.get(task, {}).get(man[k]['round'])
    if not tag:
        return None
    bid = (st['done'].get(f'{tag}:{k}') or {}).get('batch') or \
        next((b['id'] for b in reversed(st['batches']) if b['tag'] == tag and k in b['keys']), None)
    b = next((b for b in st['batches'] if b['id'] == bid), None)
    return local_time(b['submitted']) if b else None


def local_time(s: str) -> dt.datetime:
    """A state.json time ('YYYY-MM-DD HH:MM', local at submission) made timezone-aware with the offset of the last public
    commit made before that local time (the laptop moved between UTC-7 and UTC-6 on October 26, 2026)."""
    global _COMMITS
    if _COMMITS is None:
        _COMMITS = sorted(dt.datetime.fromisoformat(x) for x in git('log', '--all', '--format=%cI').splitlines() if x)
    naive = dt.datetime.strptime(s, '%Y-%m-%d %H:%M')
    tz = next((c.tzinfo for c in reversed(_COMMITS) if c.replace(tzinfo=None) <= naive), None) or dt.datetime.now().astimezone().tzinfo
    return naive.replace(tzinfo=tz)


_SYS_AT = {}


def system_at(rev: str, task: str) -> str | None:
    """The system prompt that tools/code_papers.py at commit rev builds for the task, from that commit's files."""
    if (rev, task) in _SYS_AT:
        return _SYS_AT[rev, task]
    files = ['tools/code_papers.py', 'tools/check_coding.py', 'agents/coder/CODEBOOK.md', 'agents/coder/coding.schema.json',
             'agents/coder/REVIEW_ADDENDUM.md', 'agents/coder/review_addendum.schema.json', 'agents/advance/RUBRIC.md',
             'agents/advance/advance.schema.json', 'tools/ai_readiness/README.md', 'tools/ai_readiness/annotation.schema.json']
    out = None
    with tempfile.TemporaryDirectory() as d:
        for f in files:
            r = subprocess.run(['git', '-C', str(ROOT), 'show', f'{rev}:{f}'], capture_output=True)
            if r.returncode == 0:
                (Path(d) / f).parent.mkdir(parents=True, exist_ok=True)
                (Path(d) / f).write_bytes(r.stdout)
        spec = importlib.util.spec_from_file_location(f'code_papers_at_{rev}', Path(d) / 'tools' / 'code_papers.py')
        mod = importlib.util.module_from_spec(spec)
        path0 = list(sys.path)
        try:
            spec.loader.exec_module(mod)
            mod.TASK = 'advance' if task == 'advance' else 'inquiry'
            if task == 'review' and hasattr(mod, 'REVIEW_ADDENDUM_PATH'):   # the addendum rides in the review system prompt
                mod.REVIEW_DIR = str(DATA / 'review')
            out = mod.system_blocks()[0]['text']
        except Exception as e:  # noqa: BLE001  (an old module that cannot build the prompt)
            out = None
            print(f'note: system prompt at {rev} not rebuilt ({type(e).__name__}: {e})')
        finally:
            sys.path[:] = path0
    _SYS_AT[rev, task] = out
    return out


def batches(task: str, st: dict, tags: list[str], system: str) -> list[dict]:
    """The Claude batches of the task's tags, each with the commit before submission and whether the system prompt that
    commit builds equals the frozen one. Uncommitted edits at submission time are not recoverable."""
    out = []
    for b in st['batches']:
        if b['tag'] not in tags:
            continue
        t = local_time(b['submitted'])
        rev = git('rev-list', '-1', f'--before={t.isoformat()}', 'HEAD')[:7]
        s = system_at(rev, task) if rev else None
        out.append({'id': b['id'], 'tag': b['tag'], 'submitted': b['submitted'], 'submitted_iso': t.isoformat(), 'n': len(b['keys']),
                    'codebook': b.get('codebook'), 'rubric': b.get('rubric'), 'effort': b.get('effort'), 'max_tokens': b.get('max_tokens'),
                    'collected': b.get('collected'), 'commit_before_submission': rev,
                    'system_sha256_at_commit': sha(s) if s else None, 'system_same_as_frozen': (s == system) if s else None})
    return out


def advance_tags() -> list[str]:
    return sorted(d.name for d in API.glob('*-advance') if d.is_dir())


def review_changed_after(k: str, t: dt.datetime) -> bool | None:
    """True when the review record on disk was written after submission or differs from its first committed version in
    the private repository (the commit time itself says nothing: the 61 records were committed a minute after E3 went in)."""
    f = DATA / 'review' / k / 'discussion.txt'
    if not f.is_file():
        return None
    p = rel(f)[len('private/'):]
    first = (git('log', '--diff-filter=A', '--format=%h', '--', p, cwd=PRIVATE).splitlines() or [None])[-1]
    if first:
        r = subprocess.run(['git', '-C', str(PRIVATE), 'show', f'{first}:{p}'], capture_output=True)
        if r.returncode == 0 and r.stdout != f.read_bytes():
            return True
    return dt.datetime.fromtimestamp(f.stat().st_mtime, t.tzinfo) > t + MINUTE


def outputs(task: str, keys: list[str], rows: dict, st: dict, tags: list[str], queue: dict) -> list[dict]:
    """Index of every Claude coding file of the task's papers under the task's tags (read only)."""
    bmeta = {b['id']: b for b in st['batches']}
    out = []
    for tag in tags:
        d = API / tag
        files = [(f, 'collected') for f in sorted(d.glob('g22_*.json'))] + \
                [(f, 'invalid at collection') for f in sorted((d / '_invalid').glob('g22_*'))] if d.is_dir() else []
        for f, where in files:
            k = f.stem
            if k not in rows:
                continue
            r = {'tag': tag, 'key': k, 'folder': rel(d), 'file': rel(f), 'sha256': sha_file(f)}
            try:
                c = json.loads(f.read_text())
            except Exception:  # noqa: BLE001
                c = None
            if task == 'advance':
                rec = (c or {}).get('coding') if where != 'collected' and isinstance(c, dict) else c
                run = (c or {}).get('run') or {} if isinstance(c, dict) else {}
                r.update({'status': 'valid as collected' if where == 'collected' else 'invalid' if f.suffix == '.json' else 'invalid JSON',
                          'coder': (rec or {}).get('coder') if isinstance(rec, dict) else None, 'model': run.get('model'),
                          'rubric_version': (rec or {}).get('rubric_version') if isinstance(rec, dict) else None})
            else:
                errs = (['not JSON'] if not isinstance(c, dict) else
                        validate(c, review=True, texts=cp.review_texts(k, store=False), checks=DISCLOSURE_CHECKS) if task == 'review'
                        else validate(c))
                r.update({'status': 'valid' if not errs else 'invalid', 'n_errors': len(errs), 'coder': (c or {}).get('coder'),
                          'codebook_version': (c or {}).get('codebook_version'), 'model': None})
            done = st['done'].get(f'{tag}:{k}')
            spent = st.get('spent', {}).get(f'{tag}:{k}') or []
            bid = (done or {}).get('batch') or (run.get('batch') if task == 'advance' else None) or \
                next((b['id'] for b in reversed(st['batches']) if b['tag'] == tag and k in b['keys']), None)
            if task != 'advance' and spent:
                r['model'] = spent[-1].get('model')
            if done and done.get('batch') is None:
                r['note'] = 'synchronous run (code_papers.py one): server-side fallback was on, answering model not recorded'
            b = bmeta.get(bid)
            r.update({'batch': bid, 'submitted': b['submitted'] if b else None, 'usage': (done or {}).get('usage'),
                      'usd': (done or {}).get('usd') if done else round(sum(x.get('usd') or 0 for x in spent), 4) or None,
                      'attempts': len(spent) or None})
            drift = {}
            if b:
                t = local_time(b['submitted'])
                if task == 'advance':
                    sent = (b.get('blind') or {}).get(k)
                    drift['blind_same_as_frozen'] = (sent == rows[k]['paper_text_sha256']) if sent else None
                else:
                    up = st['files'].get(k, {}).get('sha256')
                    drift['pdf_same_as_uploaded'] = (up == rows[k]['pdf_sha256']) if up else None
                    x = cp.queue_file(queue[k]['file']).with_suffix('.xml.txt')
                    if x.is_file():
                        drift['xml_txt_modified_after_submission'] = dt.datetime.fromtimestamp(x.stat().st_mtime, t.tzinfo) > t + MINUTE
                    if task == 'review':
                        drift['review_changed_after_submission'] = review_changed_after(k, t)
            r['drift'] = drift
            out.append(r)
    return out


# ------------------------------------------------------------------------------------------------ package
def package(task: str) -> dict:
    set_task(task)
    st = json.loads((API / 'state.json').read_text())
    queue = json.loads(cp.QUEUE.read_text())
    man = manifests(task)
    keys, excl = population(task, st, man, queue)
    system = cp.system_blocks()[0]['text']
    pk = set(pilot_keys())
    rows, users, skipped = {}, {}, []
    for k in keys:
        row, user, why = build_paper(task, k, man[k], queue, sent_at(task, k, st, man))
        if why:
            skipped.append({'key': k, 'reason': why}); continue
        if k in pk:
            row['advance_pilot'] = True
            row['confirmatory_exclude'] = 'advance pilot paper: its advance codings have been seen (g24 exclusion)'
        row['est_input_tokens'] = round((len(system) + row['user_chars']) / CHARS_PER_TOKEN)
        rows[k], users[k] = row, user
    tags = TASKS[task]['claude_tags'] or advance_tags()
    all_tags = tags + TASKS[task]['replicate_tags']
    outs = outputs(task, list(rows), rows, st, all_tags, queue)
    papers_jsonl = ''.join(json.dumps(rows[k], ensure_ascii=False, sort_keys=True) + '\n' for k in sorted(rows))
    return {'task': task, 'system': system, 'rows': rows, 'users': users, 'excluded': excl, 'skipped': skipped,
            'outputs': outs, 'batches': batches(task, st, all_tags, system), 'tags': tags, 'all_tags': all_tags,
            'papers_jsonl': papers_jsonl, 'emb': embargoed() & set(rows)}


def definition(P: dict) -> dict:
    task, rows = P['task'], P['rows']
    T = TASKS[task]
    import blind_text
    import check_advance as ca
    tok = sorted(r['est_input_tokens'] for r in rows.values())
    q = lambda f: tok[min(len(tok) - 1, int(f * len(tok)))] if tok else None
    st_out = Counter((o['tag'], o['status']) for o in P['outputs'])
    vers = {'codebook_version': cp.codebook_version()} if task != 'advance' else \
        {'rubric_version': ca.rubric_version(), 'blind_version': blind_text.BLIND_VERSION}
    return {
        'task': task, **vers,
        'decided_by': 'Marine Denolle (PI), October 28, 2026 (DECISIONS.md): fixed paper set and task definitions for an OLMo rerun',
        'files': {f: {'sha256': sha_file(ROOT / f), 'last_commit': git('log', '-1', '--format=%h', '--', f) or 'untracked',
                      'modified_since_commit': bool(git('status', '--porcelain', '--', f))} for f in T['files']},
        'system_sha256': sha(P['system']), 'system_chars': len(P['system']),
        'model_slot': MODEL_SLOT,
        'open_request': {'temperature': 0, 'max_tokens': T['max_tokens'], 'response_format': {'type': 'json_object'},
                         'messages': ['system: system.txt', f'user: user/<key>.user.txt with coder = "{MODEL_SLOT}" replaced by the model name']},
        'claude_request': {'model': cp.MODEL, 'api': 'Message Batches', 'effort': T['effort'], 'max_tokens': T['max_tokens'],
                           'retries_max_tokens': 64000, 'system_cache': '1 hour (from batch msgbatch_01HTgc7EkMN55Gd8gzUtQPjm on)',
                           'structured_output': False,
                           'reads': 'the PDF as a document (text and page images), the located XML text when there is one'
                           + (', the open-review record, the author-responses document (AR pages not in the record) and the '
                              'review addendum in the system prompt' if task == 'review' else '') if task != 'advance' else
                           'the blinded text only (no PDF, no DOI), named by its opaque key'},
        'validator': T['validator'], 'compare': T['compare'],
        'claude_tags': P['tags'], 'replicate_tags': T['replicate_tags'],
        'n_papers': len(rows), 'text_source': dict(Counter(r['text_source'] for r in rows.values())),
        'over_open_max_chars': sorted(k for k, r in rows.items() if r['over_open_max_chars']),
        'xml_for_open_model_not_for_claude': sorted(k for k, r in rows.items() if r['text_source'] == 'xml' and r.get('claude_read_xml') is False),
        'est_input_tokens': {'median': q(0.5), 'p90': q(0.9), 'max': tok[-1] if tok else None,
                             'over_65536': sum(t > 65536 for t in tok), 'over_131072': sum(t > 131072 for t in tok),
                             'note': f'(system + user characters) / {CHARS_PER_TOKEN}; add max_tokens for the context window'},
        'confirmatory_exclude': {k: r['confirmatory_exclude'] for k, r in rows.items() if r.get('confirmatory_exclude')},
        'embargoed_keys': sorted(P['emb']),
        'excluded': P['excluded'], 'skipped': P['skipped'],
        'claude_outputs': {f'{t}:{s}': n for (t, s), n in sorted(st_out.items())},
        'batches': P['batches'],
        'papers_jsonl_sha256': sha(P['papers_jsonl']),
        'set_sha256': sha(''.join(f"{k}\t{rows[k]['user_sha256']}\n" for k in sorted(rows)) + sha(P['system'])),
        'set_sha256_rule': 'sha256 of the lines "<key>\\t<user sha256>\\n" sorted by key, followed by the system sha256 (hex)',
    }


def outputs_jsonl(P: dict) -> str:
    return ''.join(json.dumps(o, ensure_ascii=False, sort_keys=True) + '\n' for o in P['outputs'])


def write_sums(d: Path) -> None:
    lines = [f'{sha_file(f)}  {f.relative_to(d).as_posix()}' for f in sorted(d.rglob('*')) if f.is_file() and f.name != 'SHA256SUMS']
    (d / 'SHA256SUMS').write_text('\n'.join(lines) + '\n')


def size(d: Path) -> int:
    return sum(f.stat().st_size for f in d.rglob('*') if f.is_file())


def summary(P: dict, D: dict) -> str:
    users = sum(len(u.encode()) for u in P['users'].values())
    out = [f"task {P['task']}: {D['n_papers']} papers ({D['text_source']}); system {D['system_chars']:,} chars, sha256 {D['system_sha256'][:12]}",
           f"  user files {len(P['users'])}, {users / 1e6:.1f} MB; est. input tokens median {D['est_input_tokens']['median']}, "
           f"p90 {D['est_input_tokens']['p90']}, max {D['est_input_tokens']['max']}, over 65,536: {D['est_input_tokens']['over_65536']}",
           f"  excluded from the manifests {len(P['excluded'])} ({dict(Counter(e['reason'] for e in P['excluded']))}); skipped {len(P['skipped'])}"
           + (f" ({dict(Counter(s['reason'] for s in P['skipped']))})" if P['skipped'] else ''),
           f"  over {OPEN_MAX_CHARS:,} chars (code_papers_open skips): {D['over_open_max_chars']}",
           f"  XML text for the open model, PDF only for Claude (XML fetched after submission): {len(D['xml_for_open_model_not_for_claude'])}",
           f"  confirmatory exclusions {len(D['confirmatory_exclude'])}; embargoed keys {len(D['embargoed_keys'])}",
           f"  Claude outputs {D['claude_outputs']}",
           f"  batches {len(D['batches'])}; system prompt at the commit before submission equals the frozen one: "
           f"{dict(Counter(str(b['system_same_as_frozen']) for b in D['batches']))}"]
    dr = Counter()
    for o in P['outputs']:
        for k, v in o['drift'].items():
            dr[f'{k}={v}'] += 1
    out.append(f'  drift checks over the output rows: {dict(sorted(dr.items()))}')
    out.append(f"  papers.jsonl sha256 {D['papers_jsonl_sha256'][:12]}; set sha256 {D['set_sha256'][:12]}")
    return '\n'.join(out)


def public_manifest() -> None:
    """preregistration/handoff-manifest.json from every frozen task folder: versions and hashes only."""
    tasks = {}
    for t in TASKS:
        f = HANDOFF / t / 'handoff.json'
        if not f.is_file():
            tasks[t] = {'status': 'not frozen'}
            continue
        whole = json.loads(f.read_text())
        D = whole['data']
        tasks[t] = {'status': 'frozen', 'frozen': whole['_provenance']['date'], 'frozen_by_commit': whole['_provenance']['commit'],
                    **{k: D[k] for k in ('codebook_version', 'rubric_version', 'blind_version') if k in D},
                    'files': D['files'], 'system_sha256': D['system_sha256'], 'system_chars': D['system_chars'],
                    'open_request': D['open_request'], 'claude_request': D['claude_request'], 'validator': D['validator'],
                    'compare': D['compare'], 'n_papers': D['n_papers'], 'text_source': D['text_source'],
                    'n_over_open_max_chars': len(D['over_open_max_chars']),
                    'n_xml_for_open_model_not_for_claude': len(D['xml_for_open_model_not_for_claude']), 'est_input_tokens': D['est_input_tokens'],
                    'n_confirmatory_exclude': len(D['confirmatory_exclude']), 'n_excluded': len(D['excluded']),
                    'n_skipped': len(D['skipped']), 'claude_outputs': D['claude_outputs'],
                    'batches': [{k: b[k] for k in ('id', 'tag', 'n', 'codebook', 'rubric', 'effort', 'max_tokens',
                                                    'commit_before_submission', 'system_same_as_frozen')} for b in D['batches']],
                    'papers_jsonl_sha256': D['papers_jsonl_sha256'], 'set_sha256': D['set_sha256'], 'set_sha256_rule': D['set_sha256_rule'],
                    'sha256sums_sha256': sha_file(HANDOFF / t / 'SHA256SUMS')}
    data = {'what': 'OLMo hand-off: frozen paper sets and task definitions (tools/roadmap/g33_handoff.py). Paper texts, keys '
                    'and DOIs stay in the private tree (private/data/roadmap/handoff/<task>/); this file carries versions and hashes.',
            'tasks': tasks}
    write_json(PUBLIC, data, [rel(HANDOFF / t / 'handoff.json') for t in TASKS if (HANDOFF / t / 'handoff.json').is_file()])


def freeze(args) -> None:
    P = package(args.task)
    D = definition(P)
    d = HANDOFF / args.task
    print(summary(P, D))
    if args.dry_run:
        print(f'dry run: would write {rel(d)}/ (handoff.json, system.txt, papers.jsonl, claude_outputs.jsonl, SHA256SUMS, '
              f'user/ with {len(P["users"])} files) and update {rel(PUBLIC)}; nothing written')
        return
    if (d / 'handoff.json').is_file():
        old = read_json(d / 'handoff.json')
        same = old['papers_jsonl_sha256'] == D['papers_jsonl_sha256'] and old['system_sha256'] == D['system_sha256']
        if same and not args.refreeze:
            if args.update_outputs:
                (d / 'claude_outputs.jsonl').write_text(outputs_jsonl(P))
                whole = json.loads((d / 'handoff.json').read_text())
                # the instrument files may have new commits that leave every request byte-identical (the inputs are
                # unchanged, checked above): their current hashes replace the block, the frozen block is kept once
                whole['data'].setdefault('files_at_freeze', whole['data']['files'])
                whole['data'].update({k: D[k] for k in ('claude_outputs', 'batches', 'claude_tags', 'files')})
                whole['_provenance']['outputs_updated'] = TODAY
                (d / 'handoff.json').write_text(json.dumps(whole, indent=1, ensure_ascii=False))
                write_sums(d)
                public_manifest()
                log(f'g33_handoff.py freeze --task {args.task} --update-outputs', 'hand-off Claude output index updated', len(P['outputs']),
                    f"inputs unchanged (set {D['set_sha256'][:12]})")
                print(f'{rel(d)}: inputs unchanged; Claude output index updated ({len(P["outputs"])} rows)')
            else:
                print(f'{rel(d)} is frozen and its inputs are identical (set sha256 {D["set_sha256"][:12]}); nothing written. '
                      '--update-outputs rewrites the Claude output index only.')
            return
        if not args.refreeze:
            oldrows = {json.loads(l)['key']: json.loads(l) for l in (d / 'papers.jsonl').read_text().splitlines() if l.strip()}
            changed = sum(oldrows.get(k) != r for k, r in json.loads(json.dumps(P['rows'])).items())
            sys.exit(f'refusing to overwrite the frozen {rel(d)}: system prompt {"changed" if old["system_sha256"] != D["system_sha256"] else "unchanged"}; '
                     f'{changed} paper rows differ, {len(set(oldrows) - set(P["rows"]))} papers dropped, '
                     f'{len(set(P["rows"]) - set(oldrows))} added. Pass --refreeze to supersede it.')
        sup = HANDOFF / '_superseded' / f"{args.task}-{json.loads((d / 'handoff.json').read_text())['_provenance']['date']}-{old['papers_jsonl_sha256'][:8]}"
        sup.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(d), str(sup))
        print(f'previous package moved to {rel(sup)}')
    tmp = HANDOFF / f'.{args.task}.tmp'
    if tmp.exists():
        shutil.rmtree(tmp)
    (tmp / 'user').mkdir(parents=True)
    (tmp / 'system.txt').write_text(P['system'])
    for k, u in P['users'].items():
        (tmp / 'user' / f'{k}.user.txt').write_text(u)
    (tmp / 'papers.jsonl').write_text(P['papers_jsonl'])
    (tmp / 'claude_outputs.jsonl').write_text(outputs_jsonl(P))
    inputs = ['private/download-queue.json', 'derived/calc1/manifest.jsonl', 'derived/r2calc/manifest.jsonl',
              'private/analysis/codings/api/state.json (read only)'] + [f'private/analysis/codings/api/{t}' for t in P['all_tags']]
    write_json(tmp / 'handoff.json', D, inputs, {'chars_per_token': CHARS_PER_TOKEN, 'open_max_chars': OPEN_MAX_CHARS, 'model_slot': MODEL_SLOT})
    write_sums(tmp)
    tmp.rename(d)
    public_manifest()
    log(f'g33_handoff.py freeze --task {args.task}', f'OLMo hand-off package frozen ({args.task})', D['n_papers'],
        f"set sha256 {D['set_sha256'][:12]}, system {D['system_sha256'][:12]}, {size(d) / 1e6:.1f} MB; {len(P['outputs'])} Claude output rows")
    print(f'wrote {rel(d)}/ ({size(d) / 1e6:.1f} MB) and {rel(PUBLIC)}')


def verify(args) -> None:
    d = HANDOFF / args.task
    if not (d / 'handoff.json').is_file():
        sys.exit(f'{rel(d)} is not frozen')
    D = read_json(d / 'handoff.json')
    rows = {json.loads(l)['key']: json.loads(l) for l in (d / 'papers.jsonl').read_text().splitlines() if l.strip()}
    bad_files = [l for l in subprocess.run(['shasum', '-a', '256', '-c', 'SHA256SUMS'], cwd=d, capture_output=True, text=True).stdout.splitlines()
                 if not l.endswith(': OK')]
    P = package(args.task)
    now = P['rows']
    diff = Counter()
    for k, r in rows.items():
        n = now.get(k)
        if n is None:
            diff['paper no longer buildable'] += 1; continue
        for f in ('paper_text_sha256', 'pdf_sha256', 'xml_txt_sha256', 'review_sha256', 'author_responses_sha256', 'user_sha256'):
            if r.get(f) != n.get(f):
                diff[f'{f} differs'] += 1
    res = {'package_files_failing_sha256sums': len(bad_files), 'system_same': sha(P['system']) == D['system_sha256'],
           'papers': len(rows), 'source_drift': dict(diff)}
    if args.open_tag:
        f = OPEN / args.open_tag / 'run.json'
        run = json.loads(f.read_text())
        pr = run.get('papers', {})
        res['open_run'] = {'tag': args.open_tag, 'model': run.get('model'), 'system_same': run.get('system_sha256') == D['system_sha256'],
                           'papers': len(pr), 'not_in_frozen_set': len(set(pr) - set(rows)),
                           'paper_text_same': sum(rows[k]['paper_text_sha256'] == v.get('xml_sha256') for k, v in pr.items() if k in rows),
                           'paper_text_differs': sorted(k for k, v in pr.items() if k in rows and rows[k]['paper_text_sha256'] != v.get('xml_sha256')),
                           'status': dict(Counter(v.get('status') for v in pr.values()))}
    print(json.dumps(res, indent=1))
    log(f'g33_handoff.py verify --task {args.task}' + (f' --open-tag {args.open_tag}' if args.open_tag else ''),
        'hand-off package checked against its sources', len(rows), json.dumps(res['source_drift'] or 'no source drift'))


def requests(args) -> None:
    d = HANDOFF / args.task
    D = read_json(d / 'handoff.json')
    system = (d / 'system.txt').read_text()
    if sha(system) != D['system_sha256']:
        sys.exit('system.txt does not match its frozen sha256')
    out, n = Path(args.out), 0
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('w') as f:
        for l in (d / 'papers.jsonl').read_text().splitlines():
            r = json.loads(l)
            u = (d / r['user_file']).read_text()
            if sha(u) != r['user_sha256']:
                sys.exit(f"{r['user_file']} does not match its frozen sha256")
            u = u.replace(f'coder = "{MODEL_SLOT}"', f'coder = "{args.model}"')
            body = {'model': args.model, **{k: v for k, v in D['open_request'].items() if k != 'messages'},
                    'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': u}]}
            f.write(json.dumps({'custom_id': r['key'], 'method': 'POST', 'url': '/v1/chat/completions', 'body': body}, ensure_ascii=False) + '\n')
            n += 1
    log(f'g33_handoff.py requests --task {args.task}', f'OpenAI batch requests for {args.model}', n, f'set {D["set_sha256"][:12]}; {rel(out)}')
    print(f'{n} requests written to {out}')


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    for name in ('freeze', 'verify', 'requests'):
        s = sub.add_parser(name)
        s.add_argument('--task', required=True, choices=list(TASKS))
    f = sub.choices['freeze']
    f.add_argument('--dry-run', action='store_true'); f.add_argument('--refreeze', action='store_true')
    f.add_argument('--update-outputs', action='store_true')
    sub.choices['verify'].add_argument('--open-tag')
    r = sub.choices['requests']
    r.add_argument('--model', required=True); r.add_argument('--out', required=True)
    a = ap.parse_args()
    {'freeze': freeze, 'verify': verify, 'requests': requests}[a.cmd](a)


if __name__ == '__main__':
    main()
