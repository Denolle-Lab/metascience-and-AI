"""Phase 2b: collect the open review record of the coded Copernicus (EGU) papers.

For each eligible paper with a 10.5194 DOI, Crossref gives the article landing page and the discussion
preprint. The article's <stem>-discussion.html page carries every referee comment (RC), author comment (AC),
community comment (CC) and editor comment (EC) in full, and links the files of the review process:
the discussion preprint, author responses (AR), track-changes manuscripts (ATC), revised manuscript versions,
and comment supplements.

Outputs, per paper, in private/data/roadmap/review/<key>/
  discussion.txt      every comment as located paragraphs, "[RC1 ¶3] text"; comment supplements appended as "[RC1-S p.2] text"
  *.pdf               preprint, AR, ATC, manuscript versions, comment supplements
and the index private/data/roadmap/derived/review/open_review_index.json

Run:  python tools/roadmap/g15_open_review.py [--limit N]
"""
import html, json, re, subprocess, sys, time, urllib.request
from pathlib import Path
from common import ROOT, PRIVATE, DATA, DERIVED, write_json, log

UA = {'User-Agent': 'Mozilla/5.0 (metascience seminar, University of Washington)'}
OUT = DATA / 'review'
CODED = PRIVATE / 'analysis' / 'codings' / 'api' / 'calc1'
PAUSE = 1.5


def get(url, binary=False):
    time.sleep(PAUSE)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
        return data if binary else data.decode('utf-8', 'replace')


def text_of(fragment):
    paras = re.findall(r'<p[^>]*>(.*?)</p>', fragment, flags=re.S) or [fragment]
    out = []
    for p in paras:
        s = html.unescape(re.sub(r'<[^>]+>', ' ', p))
        s = re.sub(r'\s+', ' ', s).strip()
        if s:
            out.append(s)
    return out


def parse(page):
    """Comments in either format: inline text (newer discussions) or one PDF per comment (older ones)."""
    comments = []
    heads = list(re.finditer(r'<strong>((?:RC|AC|CC|EC)\d+)</strong>:', page))
    for i, m in enumerate(heads):
        cid = m.group(1)
        seg = page[m.end(): heads[i + 1].start() if i + 1 < len(heads) else m.end() + 300000]
        head = re.search(r'</a>,\s*([^<]+)', seg)
        pdf = re.search(r'href="(https://[^"]+[/-]' + cid + r'\.pdf)"', seg[:3000])
        body = re.search(r'id="comment-body-\d+"', seg)
        paras = []
        if body:
            frag = re.split(r'<div class="[^"]*citation', seg[body.start():])[0]
            paras = text_of(frag)
        supp = sorted(set(re.findall(r'href="(https://[^"]+-' + cid + r'-supplement\.pdf)"', seg)))
        comments.append({'id': cid, 'header': re.sub(r'\s+', ' ', head.group(1)).strip() if head else '',
                         'paras': paras, 'pdf': pdf.group(1) if pdf and not paras else None, 'supplements': supp})
    return comments


def pdf_lines(f, tag):
    pages = subprocess.run(['pdftotext', '-layout', str(f), '-'], capture_output=True, text=True).stdout.split('\f')
    return [f'[{tag} p.{n}] ' + re.sub(r'\s+', ' ', pg).strip() for n, pg in enumerate(pages, 1) if pg.strip()]


def main():
    limit = int(sys.argv[sys.argv.index('--limit') + 1]) if '--limit' in sys.argv else None
    man = [json.loads(l) for l in (DERIVED / 'calc1' / 'manifest.jsonl').read_text().splitlines()]
    coded = {p.stem for p in CODED.glob('*.json')}
    todo = [m for m in man if m['doi'].lower().startswith('10.5194/') and m['key'] in coded][:limit]
    index = []
    for m in todo:
        key, doi = m['key'], m['doi']
        d = OUT / key
        rec = {'key': key, 'doi': doi}
        try:
            cr = json.loads(get('https://api.crossref.org/works/' + doi))['message']
            land = cr['resource']['primary']['URL'].rstrip('/') + '/'
            pre = [x['id'] for x in cr.get('relation', {}).get('has-preprint', [])]
            rec['preprint_doi'] = pre[0] if pre else None
            rec['crossref_reviews'] = len({x['id'] for x in cr.get('relation', {}).get('has-review', [])})
            if not pre:
                rec['no_open_discussion'] = True
                index.append(rec); print(key, 'no open discussion'); continue
            stem = doi.split('/', 1)[1]
            page = get(land + stem + '-discussion.html')
        except Exception as e:
            rec['error'] = f'{type(e).__name__}: {e}'
            index.append(rec); print(key, rec['error']); continue
        d.mkdir(parents=True, exist_ok=True)
        comments = parse(page)
        files = sorted(u for u in set(re.findall(r'href="(https://[^"]+/preprints/[^"]+\.pdf)"', page)) if not u.endswith('-print.pdf'))
        files += [s for c in comments for s in c['supplements']]
        got = []
        for url in dict.fromkeys(files):
            name = url.rsplit('/', 1)[1]
            f = d / name
            if not f.exists():
                try:
                    data = get(url, binary=True)
                    if data[:4] != b'%PDF':
                        continue
                    f.write_bytes(data)
                except Exception:
                    continue
            got.append(name)
        lines = [f'# Open discussion of {doi} (preprint {rec.get("preprint_doi")})', '# Locators: [ID ¶n] for inline comment paragraphs; [ID p.n] for comments posted as PDF; [ID-S p.n] for comment supplements.', '']
        for c in comments:
            lines.append(f'## {c["id"]}: {c["header"]}')
            lines += [f'[{c["id"]} ¶{i}] {p}' for i, p in enumerate(c['paras'], 1)]
            if c['pdf'] and (d / c['pdf'].rsplit('/', 1)[1]).exists():
                lines += pdf_lines(d / c['pdf'].rsplit('/', 1)[1], c['id'])
            for s in c['supplements']:
                f = d / s.rsplit('/', 1)[1]
                if f.exists():
                    lines += pdf_lines(f, c['id'] + '-S')
            lines.append('')
        (d / 'discussion.txt').write_text('\n'.join(lines))
        kinds = {}
        for c in comments:
            k = re.match(r'[A-Z]+', c['id']).group(0)
            kinds[k] = kinds.get(k, 0) + 1
        rec.update({'comments': kinds, 'words': len(' '.join(lines).split()),
                    'supplements': sum(len(c['supplements']) for c in comments), 'files': got,
                    'has_track_changes': any('ATC' in g or 'track' in g.lower() for g in got),
                    'manuscript_versions': sum('manuscript-version' in g for g in got)})
        index.append(rec)
        print(key, kinds, len(got), 'files')
    write_json(DERIVED / 'review' / 'open_review_index.json', index, ['derived/calc1/manifest.jsonl', 'Crossref relation has-preprint/has-review', 'Copernicus discussion pages'],
               {'pause_s': PAUSE})
    ok = [r for r in index if 'comments' in r]
    log('g15_open_review.py', 'open review records of coded Copernicus papers', len(ok),
        f'{sum(r["comments"].get("RC", 0) for r in ok)} referee comments; {sum(r["has_track_changes"] for r in ok)} with track changes')


if __name__ == '__main__':
    main()
