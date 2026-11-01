#!/usr/bin/env python3
"""Gold set, step 1: the convenor's research profile from her publications in OpenAlex.

Input : ORCID (default Marine Denolle, 0000-0002-1610-2250).
Output: private/data/roadmap/derived/gold/author_profile.json
        - her works (id, doi, year, type, primary topic, subfield), her co-author ids (for exclusion/flagging)
        - topic and subfield counts over her articles, weighted 1 per article (primary topic) plus 0.5 per
          secondary topic
Run   : python tools/roadmap/g01_author_profile.py [--orcid ...]
"""
from __future__ import annotations
import argparse
from collections import Counter
from common import DERIVED, decision, log, openalex, paged, sid, write_json

SEL = 'id,doi,title,publication_year,type,primary_topic,topics,authorships,primary_location'


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--orcid', default='0000-0002-1610-2250')
    a = ap.parse_args()
    authors = openalex('authors', {'filter': f'orcid:{a.orcid}', 'select': 'id,display_name,orcid,works_count'}).get('results', [])
    aid = [sid(x['id']) for x in authors]
    works = paged('works', {'filter': f'author.orcid:{a.orcid}', 'select': SEL})
    arts = [w for w in works if w.get('type') == 'article']
    topics, subf, coauth = Counter(), Counter(), Counter()
    names = {}
    for w in arts:
        pt = w.get('primary_topic') or {}
        if pt:
            topics[sid(pt['id'])] += 1
            names[sid(pt['id'])] = (pt['display_name'], pt.get('subfield', {}).get('display_name'), pt.get('field', {}).get('display_name'))
            subf[pt.get('subfield', {}).get('display_name')] += 1
        for t in (w.get('topics') or [])[1:3]:
            topics[sid(t['id'])] += 0.5
            names.setdefault(sid(t['id']), (t['display_name'], t.get('subfield', {}).get('display_name'), t.get('field', {}).get('display_name')))
        for au in w.get('authorships', []):
            i = sid((au.get('author') or {}).get('id'))
            if i and i not in aid:
                coauth[i] += 1
    data = {
        'orcid': a.orcid, 'author_ids': aid,
        'n_works': len(works), 'n_articles': len(arts),
        'topics': [{'topic_id': t, 'weight': w, 'topic': names[t][0], 'subfield': names[t][1], 'field': names[t][2]} for t, w in topics.most_common()],
        'subfields': subf.most_common(),
        'coauthor_ids': sorted(coauth),
        'works': [{'id': sid(w['id']), 'doi': w.get('doi'), 'year': w.get('publication_year'), 'type': w.get('type'),
                   'title': w.get('title'), 'primary_topic': sid((w.get('primary_topic') or {}).get('id'))} for w in works],
    }
    write_json(DERIVED / 'gold' / 'author_profile.json', data, [f'OpenAlex works, author.orcid:{a.orcid}'])
    log('g01_author_profile.py', f'works by ORCID {a.orcid}', len(works), f'{len(arts)} articles, {len(topics)} topics, {len(coauth)} co-authors')
    decision(f'Research profile = OpenAlex topics of the {len(arts)} articles under ORCID {a.orcid} (primary topic weight 1, '
             'two secondary topics weight 0.5). Co-authors are recorded so the gold set can exclude or flag their papers.')
    print(f'{len(works)} works, {len(arts)} articles; top topics:')
    for t in data['topics'][:25]:
        print(f"  {t['weight']:5.1f}  {t['topic']}  [{t['subfield']} / {t['field']}]")
    print('subfields:', data['subfields'][:10])


if __name__ == '__main__':
    main()
