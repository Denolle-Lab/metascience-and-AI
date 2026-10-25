#!/usr/bin/env python3
"""Gold set, step 2: the candidate pool of 2022 Earth-science research articles.

Input : derived/gold/author_profile.json (g01)
Output: derived/gold/pool.json  one record per candidate with cheap OpenAlex fields and its ring
Rules (each recorded in DECISIONS.md when run):
  - publication_year 2022, type article, has an abstract, at least 15 references (drops comments, replies, notes)
  - venue has a full-text route: publisher reachable with a key in keys.env (Elsevier, Wiley, AGU, Springer Nature
    open access) or open without a key (Copernicus/EGU, Science Advances, Seismica), or one of the core seismology
    journals the convenor pulls by hand (GJI, BSSA, SRL)
  - ring 'core': primary topic is one of the convenor's own research topics (weight >= 2 in the profile, Earth-science
    or seismology topics only)
  - ring 'broad': primary topic in a neighbouring Earth-science subfield, not already core
  - papers authored by the convenor are excluded; papers with a convenor co-author are kept in the pool and flagged
Run   : python tools/roadmap/g02_pool.py
"""
from __future__ import annotations
from collections import Counter
from common import DERIVED, decision, log, paged, read_json, sid, write_json

HOSTS = {  # OpenAlex host organizations with a full-text route
    'P4310320990': ('Elsevier', 'key'), 'P4310320595': ('Wiley', 'key'), 'P4310315809': ('AGU', 'key'),
    'P4310319965': ('Springer Nature', 'key_oa_only'), 'P4310319908': ('Nature Portfolio', 'key_oa_only'),
    'P4310319900': ('Springer', 'key_oa_only'), 'P4310313756': ('Copernicus', 'open'),
}
SOURCES = {  # individual venues added by source id
    'S2737427234': ('Science Advances', 'open'), 'S4387284412': ('Seismica', 'open'),
    'S108821158': ('Geophysical Journal International', 'manual'),
    'S59098468': ('Bulletin of the Seismological Society of America', 'manual'),
    'S183957208': ('Seismological Research Letters', 'manual'),
}
BROAD_SUBFIELDS = {'1908': 'Geophysics', '1906': 'Geochemistry and Petrology', '1904': 'Earth-Surface Processes',
                   '1907': 'Geology', '1902': 'Atmospheric Science', '1910': 'Oceanography',
                   '1912': 'Space and Planetary Science', '2312': 'Water Science and Technology'}
SEL = ('id,doi,title,publication_year,type,primary_topic,topics,authorships,primary_location,cited_by_count,'
       'citation_normalized_percentile,fwci,referenced_works_count,counts_by_year,open_access')
BASE = 'publication_year:2022,type:article,has_abstract:true,referenced_works_count:>14'


def core_topics(profile: dict) -> list[dict]:
    out = []
    for t in profile['topics']:
        name = t['topic'].lower()
        earthy = t['field'] in ('Earth and Planetary Sciences', 'Environmental Science') or 'seism' in name or 'geophys' in name
        if t['weight'] >= 2 and earthy and t['subfield'] != 'Civil and Structural Engineering':
            out.append(t)
    return out


def venue(w: dict):
    src = (w.get('primary_location') or {}).get('source') or {}
    s = sid(src.get('id'))
    if s in SOURCES:
        return SOURCES[s]
    for h in src.get('host_organization_lineage') or []:
        if sid(h) in HOSTS:
            return HOSTS[sid(h)]
    return None


def slim(w: dict, ring: str, mine: set, coauth: set) -> dict:
    src = (w.get('primary_location') or {}).get('source') or {}
    pt = w.get('primary_topic') or {}
    aus = {sid((a.get('author') or {}).get('id')) for a in w.get('authorships', [])}
    pub, route = venue(w)
    cnp = w.get('citation_normalized_percentile') or {}
    return {'id': sid(w['id']), 'doi': (w.get('doi') or '').replace('https://doi.org/', ''), 'title': w.get('title'),
            'journal': src.get('display_name'), 'source_id': sid(src.get('id')), 'publisher': pub, 'route': route,
            'is_oa': (w.get('open_access') or {}).get('is_oa'), 'ring': ring,
            'topic_id': sid(pt.get('id')), 'topic': pt.get('display_name'),
            'subfield': (pt.get('subfield') or {}).get('display_name'), 'subfield_id': sid((pt.get('subfield') or {}).get('id')),
            'topic_ids': [sid(t['id']) for t in (w.get('topics') or [])[:3]],
            'n_authors': len(aus), 'convenor_coauthor': bool(aus & coauth), 'convenor_author': bool(aus & mine),
            'cited_by_count': w.get('cited_by_count'), 'cnp': cnp.get('value'), 'fwci': w.get('fwci'),
            'n_refs': w.get('referenced_works_count'),
            'counts_by_year': {c['year']: c['cited_by_count'] for c in w.get('counts_by_year', [])}}


def main() -> None:
    prof = read_json(DERIVED / 'gold' / 'author_profile.json')
    mine, coauth = set(prof['author_ids']), set(prof['coauthor_ids'])
    core = core_topics(prof)
    core_ids = [t['topic_id'] for t in core]
    pool, seen = [], set()
    for chunk in [core_ids[i:i + 20] for i in range(0, len(core_ids), 20)]:
        for w in paged('works', {'filter': f"{BASE},primary_topic.id:{'|'.join(chunk)}", 'select': SEL}, cap=60000):
            if venue(w) and w['id'] not in seen:
                seen.add(w['id']); pool.append(slim(w, 'core', mine, coauth))
    for sf in BROAD_SUBFIELDS:
        for w in paged('works', {'filter': f'{BASE},primary_topic.subfield.id:{sf}', 'select': SEL}, cap=60000):
            if venue(w) and w['id'] not in seen:
                seen.add(w['id']); pool.append(slim(w, 'broad', mine, coauth))
    n_mine = sum(p['convenor_author'] for p in pool)
    pool = [p for p in pool if not p['convenor_author']]
    params = {'base_filter': BASE, 'core_topics': [(t['topic_id'], t['topic'], t['weight']) for t in core],
              'broad_subfields': BROAD_SUBFIELDS, 'hosts': HOSTS, 'sources': SOURCES}
    write_json(DERIVED / 'gold' / 'pool.json', pool, ['derived/gold/author_profile.json', 'OpenAlex works API'], params)
    by = Counter((p['ring'], p['route']) for p in pool)
    log('g02_pool.py', '2022 Earth-science articles with a full-text route', len(pool),
        f"core {sum(v for (r, _), v in by.items() if r == 'core')}, broad {sum(v for (r, _), v in by.items() if r == 'broad')}; "
        f'{n_mine} convenor-authored dropped')
    decision(f"Pool = 2022 research articles (abstract, >= 15 references) in venues with a full-text route: keys (Elsevier, Wiley, AGU, "
             f"Springer Nature open access), open (Copernicus/EGU, Science Advances, Seismica), manual (GJI, BSSA, SRL). Restricting to "
             f"fetchable venues is a known availability bias; MDPI, Frontiers, Taylor & Francis and others are out of scope. "
             f"Core ring = {len(core)} convenor topics ({', '.join(t['topic'] for t in core)}); broad ring = subfields "
             f"{', '.join(BROAD_SUBFIELDS.values())}. {n_mine} papers authored by the convenor excluded; co-authored papers flagged.")
    print(f'pool {len(pool)}:', dict(by))
    print('core topics:', [t['topic'] for t in core])


if __name__ == '__main__':
    main()
