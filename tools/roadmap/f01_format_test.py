#!/usr/bin/env python3
"""Format test, step 1: does the full-text format change a coding? Agreement, quote fidelity, locator validity.

Input : derived/format_test/codings/<key>.<X|T><rep>.json   subagent codings from located XML text (X) or pdftotext text (T)
        private/analysis/codings/api/fmt-<P|PX><rep>/<key>.json  batch-API codings from the PDF (P) or PDF + XML text (PX)
        derived/format_test/inputs/<key>.xml.txt and .pdf.txt  the sources
Output: derived/format_test/results.json and report.md
Measures:
  agreement   tools/check_coding.py agree() for every pair of codings of a paper; mean over papers of
              within-arm pairs (replicate 1 vs 2: the noise floor) and between-arm pairs (all cross pairs of two arms)
  fidelity    share of quotes (entry evidence, step quotes, novelty claims, disagreement quotes) found in the source after
              light normalization (case, whitespace, quote marks, dashes, ligatures, line-end hyphenation); checked against
              the XML text, which serves as the canonical text, and against the PDF text
  locators    share of location fields that point to something that exists: a §-locator or figure/table label in the XML
              text, or a page number within the PDF's page count or within the article's printed page range (XML fpage-lpage)
Run   : python tools/roadmap/f01_format_test.py
"""
from __future__ import annotations
import itertools
import json
import re
import sys
from collections import defaultdict
from statistics import mean
from common import DERIVED, ROOT, log, read_json, write_json

sys.path.insert(0, str(ROOT / 'tools'))
from check_coding import agree  # noqa: E402

FT = DERIVED / 'format_test'
API = ROOT / 'private' / 'analysis' / 'codings' / 'api'
ARMS = ['X', 'T', 'P', 'PX']
NUM = ['node_set_jaccard', 'mode_set_jaccard', 'node_seq_similarity', 'mode_seq_similarity']
BOOL = ['entry_node', 'entry_state', 'outcome', 'decisive_mode']


def norm(s: str) -> str:
    s = s.replace('­', '').replace('ﬁ', 'fi').replace('ﬂ', 'fl').replace('ﬀ', 'ff')
    s = re.sub(r'-\s*\n\s*', '', s)
    s = s.translate(str.maketrans({'‘': "'", '’': "'", '“': '"', '”': '"', '–': '-', '—': '-', '−': '-'}))
    s = re.sub(r'\[§[^\]]*\]|\[(Figure|Table|Fig\.)[^\]]*\]', ' ', s)   # drop the locator prefixes of the XML text
    return re.sub(r'\s+', ' ', s).strip().lower()


def quotes(c: dict) -> list[str]:
    q = [c['entry'].get('evidence', '')]
    for s in c['sequences']:
        q += [st.get('quote', '') for st in s['steps']]
    q += [x.get('quote', '') for x in c.get('novelty_claims', [])] + [x.get('quote', '') for x in c.get('disagreements', [])]
    return [x for x in q if x and x.strip()]


def locations(c: dict) -> list[str]:
    loc = [c['entry'].get('page', ''), c['end'].get('page', ''), c['decisive_move'].get('page', '')]
    for s in c['sequences']:
        loc += [st.get('page', '') for st in s['steps']]
    for f in ('imports', 'novelty_claims', 'disagreements', 'alternatives_considered'):
        loc += [x.get('page', '') for x in c.get(f, [])]
    return [x for x in loc if x is not None]


def printed_range(key: str) -> tuple[int, int] | None:
    """First and last printed page from the publisher XML (<fpage>, <lpage>), for codings that cite printed journal pages."""
    x = ROOT / 'private' / 'data' / 'roadmap' / 'pdfs' / 'gold' / f'{key}.xml'
    if not x.is_file():
        return None
    t = x.read_text(errors='replace')
    f, l = re.search(r'<fpage[^>]*>(\d+)</fpage>', t), re.search(r'<lpage[^>]*>(\d+)</lpage>', t)
    return (int(f.group(1)), int(l.group(1))) if f and l else None


def loc_ok(v: str, xml_locs: set, figs: set, npages: int, printed: tuple | None = None) -> bool:
    v = v.strip()
    parts = [x.strip() for x in re.split(r'[;,]', v) if x.strip()]
    if len(parts) > 1:  # a compound location is valid when every part is
        return all(loc_ok(x, xml_locs, figs, npages, printed) for x in parts)
    m = re.search(r'§\s*([0-9A-Za-z.]+)\s*¶\s*(\d+)', v)
    if m:
        return f'§{m.group(1)} ¶{m.group(2)}' in xml_locs
    m = re.search(r'\b(Fig(?:ure)?\.?|Table)\s*([A-Z]?\d+)', v, re.I)
    if m and not re.fullmatch(r'\d+', v):
        kind = 'Table' if m.group(1).lower().startswith('tab') else 'Figure'
        return (f'{kind} {m.group(2)}' in figs) if figs else True  # without captions in the XML, a figure number cannot be checked
    m = re.fullmatch(r'(?:pp?\.?\s*)?(\d+)(?:\s*[-–]\s*(\d+))?', v)
    if m:
        n = int(m.group(1))
        return 1 <= n <= max(npages, 1) or bool(printed and printed[0] <= n <= printed[1])
    return bool(re.fullmatch(r'S\d+(?:\s*[-–]\s*S?\d+)?', v))


def main() -> None:
    design = read_json(FT / 'design.json')
    keys = [p['key'] for p in design['papers']]
    cod = defaultdict(dict)
    for k in keys:
        for arm in ARMS:
            for rep in (1, 2):
                f = (FT / 'codings' / f'{k}.{arm}{rep}.json') if arm in ('X', 'T') else (API / f'fmt-{arm}{rep}' / f'{k}.json')
                if f.is_file():
                    cod[k][f'{arm}{rep}'] = json.loads(f.read_text())
    # same version? the PDF text must print the paper's DOI (a discussion preprint prints its own DOI instead)
    dois = {r['key']: r['doi'].lower() for r in read_json(DERIVED / 'gold' / 'gold_set.json')}
    same = [k for k in keys if dois[k] in (FT / 'inputs' / f'{k}.pdf.txt').read_text().lower().replace('\n', '').replace(' ', '')]
    per_pair, per_pair_same = defaultdict(list), defaultdict(list)
    for k in keys:
        for a, b in itertools.combinations(sorted(cod[k]), 2):
            ga, gb = re.sub(r'\d', '', a), re.sub(r'\d', '', b)
            label = f'{ga} within' if ga == gb else '-'.join(sorted([ga, gb]))
            m = agree(cod[k][a], cod[k][b])
            per_pair[label].append((k, m))
            if k in same:
                per_pair_same[label].append((k, m))

    def summarize(pp):
        out = {}
        for label, rows in sorted(pp.items()):
            by_paper = defaultdict(list)
            for k, m in rows:
                by_paper[k].append(m)
            pm = [{f: mean(float(m[f]) for m in ms) for f in NUM + BOOL} for ms in by_paper.values()]
            out[label] = {'papers': len(pm), 'pairs': len(rows), **{f: round(mean(p[f] for p in pm), 3) for f in NUM + BOOL}}
        return out
    agreement_same = summarize(per_pair_same)
    agreement = {}
    for label, rows in sorted(per_pair.items()):
        by_paper = defaultdict(list)
        for k, m in rows:
            by_paper[k].append(m)
        paper_means = [{f: mean(float(m[f]) for m in ms) for f in NUM + BOOL} for ms in by_paper.values()]
        agreement[label] = {'papers': len(paper_means), 'pairs': len(rows), **{f: round(mean(p[f] for p in paper_means), 3) for f in NUM + BOOL}}
    fidelity, locs, shape = defaultdict(list), defaultdict(list), defaultdict(list)
    for k in keys:
        xml_raw = (FT / 'inputs' / f'{k}.xml.txt').read_text()
        pdf_raw = (FT / 'inputs' / f'{k}.pdf.txt').read_text()
        xml_n, pdf_n = norm(xml_raw), norm(pdf_raw)
        xml_locs = set(re.findall(r'\[(§[^ \]]+ ¶\d+)\]', xml_raw))
        figs = set(m.strip() for m in re.findall(r'^\[((?:Figure|Table)[^\]]*)\]', xml_raw, re.M))
        npages = pdf_raw.count('\f') + 1
        printed = printed_range(k)
        for name, c in cod[k].items():
            arm = re.sub(r'\d', '', name)
            qs = quotes(c)
            fx = [norm(q) in xml_n for q in qs]
            fp = [norm(q) in pdf_n for q in qs]
            lv = [loc_ok(v, xml_locs, figs, npages, printed) for v in locations(c) if str(v).strip()]
            fidelity[arm].append({'key': k, 'name': name, 'quotes': len(qs), 'in_xml': sum(fx), 'in_pdf': sum(fp)})
            locs[arm].append({'key': k, 'name': name, 'locations': len(lv), 'valid': sum(lv)})
            fp_steps = next(s for s in c['sequences'] if s['kind'] == 'final_paper')['steps']
            shape[arm].append({'key': k, 'name': name, 'steps': len(fp_steps), 'entry': c['entry']['state'], 'outcome': c['end']['outcome'],
                               'composition': c['composition'], 'pages_convention': c['pages_convention'],
                               'figure_steps': sum(1 for s in fp_steps if re.search(r'fig', str(s.get('page', '')), re.I))})
    summary = {}
    for arm in ARMS:
        F, L, S = fidelity[arm], locs[arm], shape[arm]
        if not F:
            continue
        nq = sum(x['quotes'] for x in F)
        summary[arm] = {'codings': len(F), 'quotes': nq,
                        'quotes_in_xml_text': round(sum(x['in_xml'] for x in F) / max(nq, 1), 3),
                        'quotes_in_pdf_text': round(sum(x['in_pdf'] for x in F) / max(nq, 1), 3),
                        'locations_valid': round(sum(x['valid'] for x in L) / max(sum(x['locations'] for x in L), 1), 3),
                        'mean_steps': round(mean(x['steps'] for x in S), 1), 'figure_located_steps': sum(x['figure_steps'] for x in S)}
    write_json(FT / 'results.json', {'same_version_papers': same, 'agreement_same_version': agreement_same, 'agreement': agreement, 'summary': summary, 'fidelity': fidelity, 'locations': locs, 'shape': shape},
               ['derived/format_test/codings', 'private/analysis/codings/api/fmt-*', 'derived/format_test/inputs'])
    lines = ['# Format test: XML text versus PDF', '', f"Papers: {len(keys)}. Arms: X located XML text (subagent), T pdftotext text (subagent), "
             'P PDF via the batch API, PX PDF plus XML text via the batch API. Two independent codings per arm and paper. '
             'Agreement: tools/check_coding.py agree(), averaged within paper, then over papers.', '',
             '## Agreement', '', '| Pair | Papers | Node set | Mode set | Node sequence | Mode sequence | Entry node | Entry state | Outcome | Decisive mode |',
             '|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|']
    for label, a in agreement.items():
        lines.append(f"| {label} | {a['papers']} | " + ' | '.join(f"{a[f]:.2f}" for f in NUM + BOOL) + ' |')
    lines += ['', f'## Agreement, the {len(same)} papers whose PDF is the same version as the XML', '',
              f"Excluded: {', '.join(k for k in keys if k not in same) or 'none'} (the PDF was the discussion preprint, so arms T and P coded another version).", '',
              '| Pair | Papers | Node set | Mode set | Node sequence | Mode sequence | Entry node | Entry state | Outcome | Decisive mode |',
              '|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|']
    for label, a in agreement_same.items():
        lines.append(f"| {label} | {a['papers']} | " + ' | '.join(f"{a[f]:.2f}" for f in NUM + BOOL) + ' |')
    lines += ['', '## Fidelity, locations and shape', '', '| Arm | Codings | Quotes | In XML text | In PDF text | Valid locations | Mean steps | Figure-located steps |',
              '|:--|:--|:--|:--|:--|:--|:--|:--|']
    for arm, s in summary.items():
        lines.append(f"| {arm} | {s['codings']} | {s['quotes']} | {s['quotes_in_xml_text']:.2f} | {s['quotes_in_pdf_text']:.2f} | {s['locations_valid']:.2f} | {s['mean_steps']} | {s['figure_located_steps']} |")
    (FT / 'report.md').write_text('\n'.join(lines) + '\n')
    log('f01_format_test.py', 'format test: agreement, quote fidelity, locator validity', sum(len(v) for v in cod.values()),
        '; '.join(f"{arm}: in-XML {s['quotes_in_xml_text']:.2f}, valid loc {s['locations_valid']:.2f}" for arm, s in summary.items()))
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
