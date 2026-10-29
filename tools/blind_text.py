#!/usr/bin/env python3
"""Blinded full text of one paper for the advance coder (agents/advance/RUBRIC.md).

Source, in order: the located publisher XML text (<key>.xml.txt beside the PDF, tools/jats_text.py, the text
code_papers.xml_text_for returns) plus the reference list read from <key>.xml; else pdftotext of the PDF, one block per
page headed [p. N]. pdftotext runs in its default reading-order mode, not -layout: on two-column pages -layout prints
both columns on one line, so a sentence is interleaved with the other column and a quote cannot be checked against the
text (98 of the 260 calc1 and r2calc PDFs without XML text are two-column on page 3; checked October 27, 2026).

Removed: journal name and abbreviations, publisher names and boilerplate (copyright, licence, "cite as", download
stamps, journal homepage lines), running headers and footers (lines repeated at the top or bottom of at least 3 pages
and 30% of pages), line and page numbers, the paper's DOI in any form, URLs on publisher or journal domains, author
names in the front matter (full names, wherever they occur in the body), affiliations (front-matter lines on the first
four pages that name an author or an institution, address blocks that follow them, superscript-numbered affiliation
lines, mailing-address sections, and every raw affiliation string), corresponding-author initials such as '(R.E.V.)',
manuscript date lines on the first pages, e-mail addresses, ORCID identifiers, received / revised / accepted / published
date lines, editor lines, AGU key-point bullets, and the sections acknowledgments, funding, author contributions,
competing interests, review statement, disclaimer, publisher's note, online content, mailing addresses. Kept: title,
abstract, body, figure and table captions, appendices, data availability (URLs scrubbed), references as printed.
Removed tokens are replaced by [author], [journal], [publisher], [publisher URL], [repository URL (host)] or [DOI], so
the coder sees that something was removed. v1.1.1 (October 27, 2026) also replaces publisher host names printed without
a scheme, such as 'wileyonlinelibrary.com/journal/rge' in Wiley page footers.

v1.2.0 (October 28, 2026; diagnosis of advance pilot 1, tags pilot-a-advance and pilot-b-advance):
- XML route parity. The XML text is regenerated from <key>.xml with jats_text.convert(descend_sections=True,
  table_rows=True): Elsevier bodies (ja:body > ce:sections) were dropped by the default converter, which left only the
  abstract and captions in 101 of the 581 v1.1.1 texts and gave every U1 verdict of the pilot; table rows are printed
  as '[Table n] cell | cell' lines, as the pdftotext route prints them. The <key>.xml.txt files and the default
  converter are unchanged, so the inquiry and readiness requests stay byte-identical. An XML text with fewer than
  MIN_BODY_PARAS (15) body paragraphs falls back to pdftotext; meta 'xml_fallback' records why.
- DROP_SEC matches a whole heading ('Contributions of the predictor variables' and references to 'Contributions to
  Mineralogy and Petrology' were dropped as author-contribution sections); run-in headings ('Acknowledgments. We
  thank') are matched by DROP_RUNIN, which leaves out the ambiguous 'contributions', 'affiliations' and 'additional
  information'.
- Leak scrubs, from the coders' blind_leak_noticed reports: 'Government work ... public domain in the USA' notices;
  'our previous / earlier / prior work' becomes 'previous work' (citation kept); the authors' own institutions
  (OpenAlex institution names and the unit segments of the raw affiliation strings) become [institution] in the
  body; journal names are matched longest first ('Earth Surface Processes' no longer pre-empts 'Earth Surface
  Processes and Landforms'); citation-format page headers ('[journal]. 2022;47:1229-1237') are removed; on the
  pdftotext route the paper's own 'how to cite' box (lines that are fragments of the paper's title, and the author,
  journal and DOI lines around them) is removed, also when it falls inside the reference block; the Wiley note
  '[Colour figure can be viewed at ...]' is removed; name-only lines after an editor label (Seismica 'Handling
  Editor:') are removed; DOIs left in the body become [repository DOI (host)] for known data hosts, else [DOI (other)]
  (a prefix such as 10.21979, DR-NTU, names the authors' institution).

v1.2.1 (October 28, 2026; pre-spend check before advance pilot 2): the XML route now keeps the data and code
availability statements that publishers put outside the body (jats_text.convert(availability=True): JATS back
sections, Copernicus notes, Elsevier ce:data-availability), printed as §D1, §D2, ... before the references. At v1.2.0
only 17 of the 318 XML-route texts carried one, against 173 of the 263 pdftotext texts; 227 of the 318 XML sources
hold one. Their URLs and DOIs are scrubbed like the body's. The §D paragraphs do not count toward MIN_BODY_PARAS.
On the pdftotext route the abstract was missing from 15 of the 263 texts (printed without a heading on Wiley
two-column title pages, so it went with the front matter cut at 'I N T RO DU CT I O N') and cut short or interleaved
with affiliation lines in about 15 more. When fewer than half of the record abstract's word 5-grams are in the text,
the record abstract (derived/{gold,r2}/screen_input.json, boilerplate sentences dropped) is put at the top of page 1
with the label 'Abstract (from the bibliographic record; less than half of it was found in the PDF text)' (33 texts;
in about 3 of them the PDF abstract is complete but worded differently from the record's version); meta
'abstract_from_record' says so.

Citations are left as printed (v1.1.0): no surname of a cited author is replaced, in the body or the reference list,
and journal names in the reference list are not replaced. Replacing only the paper's own authors and venue marked which
references were self-citations or same-venue papers (the DOI beside a [journal] reference decoded the venue), so the
selective scrub leaked more than it hid. Journal templates are neutralized in the body: 'Plain Language Summary' becomes
'Summary'; AGU and Nature supplement names ('Figure S3', 'Text S1', 'Extended Data Fig. 2', 'Supporting Information')
become 'Supplementary Figure 3', 'Supplementary Text 1', 'Supplementary Fig. 2', 'Supplementary Material'; running
footers merged into a line ('SEISMICA | volume 1.1 | 2022', 'Nature | Vol 606 | 9') are removed; GitHub, GitLab,
Zenodo and figshare URLs and DOIs become [repository URL (github)] and so on, which keeps the fact of a release.

Names to scrub come from the round metrics (derived/gold/metrics.json, derived/r2/metrics.json: journal, publisher) and
the cached OpenAlex work record (raw/openalex, authorships with raw names, ORCID, institutions and raw affiliation
strings). Journal abbreviations come from the OpenAlex source record (abbreviated_title, alternate_titles), fetched once
per journal from the free OpenAlex API and cached under private/data/roadmap/blind/sources/.

Residual leakage is counted after scrubbing, in the body and in the reference list separately: journal-name and
publisher matches, author full names, the DOI, e-mails, ORCID, repository user or record segments, template markers
(plain-language-summary heading, bullet lines (an upper bound: most are lists in the body), S-numbered supplement
names, Extended Data, '|' footers), a
'[journal]' token followed by a DOI stem or article number, and affiliation words in the first 6,000 characters
(universit*, laborator*, 'institute of', 'department of', 'geological survey'; an independent check that does not use
the scrub patterns, and an upper bound because site names match too). Printed self-citations (the authors' surnames in
citation context) are counted as information, not as leakage: they are kept on purpose, like every other citation.

Writes only the cache private/data/roadmap/blind/<key>.txt and <key>.json (meta: source, sha256 of input and output,
leakage before and after). The cache is reused while BLIND_VERSION and the input sha256 are unchanged.

Usage:
  python tools/blind_text.py KEY [KEY ...]            build (or reuse) and print the meta of each key
  python tools/blind_text.py KEY --print              print the blinded text
  python tools/blind_text.py --manifest FILE.jsonl    build for every key of a manifest that has a PDF; leakage summary
"""
from __future__ import annotations
import argparse
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = Path(os.environ['METASCIENCE_PRIVATE']).resolve() if os.environ.get('METASCIENCE_PRIVATE') else ROOT / 'private'
DATA = PRIVATE / 'data' / 'roadmap'
CACHE = DATA / 'blind'
OPENALEX_RAW = DATA / 'raw' / 'openalex'
API = 'https://api.openalex.org'
BLIND_VERSION = '1.2.1'
MIN_BODY_PARAS = 15     # an XML text with fewer body paragraphs (abstract excluded) is not used; pdftotext instead

PUBLISHERS = ['American Geophysical Union', 'AGU', 'Wiley', 'John Wiley', 'Wiley-Blackwell', 'Blackwell', 'Elsevier',
              'Elsevier B.V.', 'Elsevier Ltd', 'Springer', 'Springer Nature', 'Springer-Verlag', 'Nature Publishing Group',
              'Copernicus Publications', 'Copernicus GmbH', 'European Geosciences Union', 'Oxford University Press',
              'Royal Astronomical Society', 'Seismological Society of America', 'Taylor & Francis', 'Taylor and Francis',
              'MDPI', 'Frontiers Media', 'Hindawi', 'IOP Publishing', 'Cambridge University Press', 'SAGE Publications',
              'American Meteorological Society', 'Geological Society of America', 'Geological Society of London',
              'American Association for the Advancement of Science', 'AAAS', 'GeoScienceWorld', 'Royal Meteorological Society',
              'Society of Exploration Geophysicists', 'European Association of Geoscientists', 'EAGE', 'Science China Press',
              'Chinese Academy of Sciences Press', 'PLOS', 'Public Library of Science', 'National Academy of Sciences']
DOMAINS = ['agupubs', 'onlinelibrary.wiley', 'wiley.com', 'sciencedirect', 'elsevier', 'cell.com', 'springer', 'nature.com',
           'academic.oup.com', 'oup.com', 'tandfonline', 'copernicus.org', 'egusphere', 'mdpi.com', 'frontiersin',
           'hindawi', 'iopscience', 'iop.org', 'cambridge.org', 'sagepub', 'ametsoc', 'geoscienceworld', 'seismosoc',
           'science.org', 'sciencemag', 'pnas.org', 'plos.org', 'rmets', 'seg.org', 'earthdoc', 'geolsoc', 'scichina',
           'wileyonlinelibrary']

_DROP_TERMS = (r'acknowledge?ments?|funding(?: information| sources?| statement)?|financial support|'
               r'author contributions?(?: statement)?|author credit(?: statement)?|contributions|credit authorship contribution statement|competing interests?|'
               r'conflicts? of interests?|declaration of competing interests?|declarations?|ethics declarations?|'
               r'review statement|disclaimer|publisher\'?s note|special issue statement|online content|'
               r'author information|additional information|peer review(?: information)?|orcid|about the (?:first |corresponding )?authors?|'
               r'mailing address(?:es)?|authors?\'? addresses|author affiliations?|affiliations?')
# v1.2.0: the whole heading must be a drop term, or several joined by ',', '&', 'and', '/' (AGU 'Acknowledgments,
# Samples, and Data', 'Funding sources & acknowledgements', 'Acknowledgments, funding, and data availability'); a
# heading that only starts with one ('Contributions of the predictor variables') is kept
_JOIN = r'\s*(?:,|&|/|\band\b)\s*(?:and\s+)?'
DROP_SEC = re.compile(rf'^(?:\d+(?:\.\d+)*\.?\s+)?(?:{_DROP_TERMS})(?:{_JOIN}(?:{_DROP_TERMS}|samples|data(?: and code)?(?: availability)?(?: statement)?))*'
                      r'\s*[.:]?\s*$', re.I)
# run-in headings on the pdftotext route ('Acknowledgments. We thank ...', 'Acknowledgments—AEG and WM were supported');
# without the ambiguous single words 'contributions', 'affiliations', 'declarations' and 'additional information'
DROP_RUNIN = re.compile(r'^(?:\d+(?:\.\d+)*\.?\s+)?(acknowledge?ments?|funding(?: information| sources?| statement)?|financial support|'
                        r'author contributions?|credit authorship contribution statement|competing interests?|'
                        r'conflicts? of interests?|declaration of competing interests?|review statement|disclaimer|'
                        r'publisher\'?s note|special issue statement)\s*(?:[.:]\s+|\s*[—–]\s*)\S', re.I)
REF_HEAD = re.compile(r'^\s*(references(?: cited)?|bibliography|literature cited|reference list)\s*$', re.I)
STOP_HEAD = re.compile(r'^\s*(?:\d{1,2}(?:\.\d+)*\.?\s+[A-Z]|abstract|a b s t r a c t|introduction|keywords|key words|plain language summary|appendix|supplement|supporting information|data availability|'
                       r'code availability|data and code availability|code and data availability|open research|'
                       r'availability statement|references|bibliography|literature cited|notes?\b|abbreviations|tables?\s*$|figures?\s*$|'
                       r'figure captions|list of figure captions|table captions)', re.I)
BOILER = re.compile(
    r'(©|\(c\)\s*\d{4}|copyright|all rights reserved|creative commons|open access article|this is an open access|'
    r'licen[cs]ed under|distributed under the terms|published by|journal homepage|contents lists available|'
    r'downloaded from|terms and conditions|terms of use|see the terms|wiley online library|for rules of use|'
    r'citation\s*:|cite (?:this|as)|to cite this|how to cite|please cite|recommended citation|'
    r'^\s*(?:received|revised|accepted|published(?: online)?|available online|article history|first published|'
    r'manuscript received|accepted manuscript|version of record|in final form)\b|'
    r'correspond(?:ence|ing author)|e-?mail\s*:|orcid|edited by|handling editor|associate editor|editor\s*:|'
    r'peer review history|key points\s*:?\s*$|supporting information may be found|reprints and permissions|'
    r'^\s*(?:vol\.?|volume)\s*\d+.*(?:pp\.|pages?)\s*\d+)', re.I)
EMAIL = re.compile(r'[\w.+-]+@[\w-]+(?:\.[\w-]+)+')
ORCID = re.compile(r'(?:https?://)?(?:orcid\.org/)?\b\d{4}-\d{4}-\d{4}-\d{3}[\dX]\b')
URL = re.compile(r'(?:https?://|www\.)[^\s)\]>,;]+', re.I)
# v1.1.1: host names printed without a scheme ('wileyonlinelibrary.com/journal/rge' in Wiley page footers, 57 of the
# 581 cached v1.1.0 texts); replaced when the host is a publisher domain. Not after '@' (e-mail) or '/' (inside a URL).
BARE_URL = re.compile(r'(?<![\w@/.\[])(?:[a-z0-9-]+\.)+(?:com|org|net|cn)(?:/[^\s)\]>,;]*)?', re.I)
AFFIL_WORDS = re.compile(r'\b(universit\w*|institut\w*|department|dept\.|laborator\w*|school of|college|academy|survey|'
                         r'cent(?:er|re)\b|observator\w*|faculty|ministry|key lab|inc\.|ltd|gmbh|cnrs|csic|bureau)\b', re.I)
ACK = re.compile(r'\b(?:we (?:thank|acknowledge|are grateful)|(?:is|are|was|were) grateful to|funded by|supported by (?:the )?(?:grant|national|nsf|nsfc)|grant (?:no|number|agreement)\b)', re.I)
ABS_HEAD = re.compile(r'^\s*(?:abstract\b|a b s t r a c t|summary\s*$|(?:1\.?\s+)?introduction\s*$)', re.I)
ABS_ONLY = re.compile(r'^\s*(?:abstract\b|a b s t r a c t|summary\s*$)', re.I)
# affiliation and address lines (v1.1.0)
COUNTRY = re.compile(r'\b(?:USA|U\.S\.A\.|United States|United Kingdom|UK|U\.K\.|China|P\. ?R\. China|Germany|France|Austria|Italy|'
                     r'Spain|Portugal|Switzerland|Netherlands|The Netherlands|Belgium|Norway|Sweden|Denmark|Finland|Iceland|Poland|'
                     r'Czech Republic|Hungary|Greece|Turkey|Russia|Japan|Korea|Republic of Korea|Taiwan|India|Pakistan|Iran|Israel|'
                     r'Egypt|Morocco|South Africa|Nigeria|Kenya|Ethiopia|Brazil|Argentina|Chile|Peru|Colombia|Mexico|Canada|'
                     r'Australia|New Zealand|Indonesia|Malaysia|Singapore|Thailand|Vietnam|Philippines|Saudi Arabia|Ireland)\.?\s*$')
ADDRESS = re.compile(r'(?:\b(?!(?:19|20)\d\d\b)\d{4,6}\b(?:\s*[A-Z]{1,2}\b)?|\bP\.?\s?O\.? Box\b|\bMail Stop\b|\bMS\s?\d|\b\d+\s+[A-Z][a-z]+\s+'
                     r'(?:Place|Street|St\.|Avenue|Ave\.|Road|Rd\.|Drive|Dr\.|Boulevard|Blvd\.?|Lane|Way|Hall)\b|stra(?:ss|ß)e\b|\bCampus\b)')
_CTRY = COUNTRY.pattern.split(r'\.?\s*$')[0]
COUNTRY_RUNON = re.compile(_CTRY + r'\.\s*\d{1,2}\s?[A-Z]')            # Nature-style run-on affiliations: 'Milan, Italy. 3CNRS, ...'
COUNTRY_INLINE = re.compile(_CTRY + r'[.,;]')
AFFIL_HEAD = re.compile(r'^\s*(?:[\d*†‡§¹²³⁴⁵⁶⁷⁸⁹]{1,3}\s*)?(?:(?:[A-Z][a-z]+\s+){0,3}Department\b|Dept\.|(?:State\s+)?Key Lab|'
                        r'(?:[A-Z][\w-]*\s+){0,6}Laborator(?:y|ies)\s+(?:of|for)\b|School of|(?:[A-Z][\w-]*\s+){0,4}Institute (?:of|for)\b|Faculty of|College of|'
                        r'Division of|Chair of|Graduate School|Universit(?:y|à|é|ät|ad)\b|Dipartimento|Departamento|Istituto)')
AFFIL_UNIT = re.compile(r'\b(?:Group|Sciences|Research|Management|Engineering|Geosciences|Ecology|Division|Unit)\b')
AFFIL_NUM = re.compile(r'^\s*(?:\d{1,2}|[a-h]|[¹²³⁴⁵⁶⁷⁸⁹])\s*[A-Z].{0,200}$')
AFFIL_STRONG = re.compile(r'\b(?:universit\w*|institut\w*|department of|national laborator\w*|school of|college of|academy of|'
                          r'geological survey|observator\w*|research cent(?:er|re))\b', re.I)
INITIALS_LINE = re.compile(r'^\s*\((?:[A-Z]\.\s?){1,4}[A-Z]?\.?\)\s*$')
INITIALS_INLINE = re.compile(r'\((?!(?:U\.S|U\.K|E\.U|N\.B|S\.A|P\.R)\.?\))(?:[A-Z]\.){2,3}[A-Z]?\.?\)')
MONTHS = r'(?:January|February|March|April|May|June|July|August|September|October|November|December)'
DATE_LINE = re.compile(rf'^\s*(?:(?:manuscript|draft|submitted|version)\s*(?:date)?\s*:?\s*)?(?:{MONTHS}\s+\d{{1,2}},?\s+(?:19|20)\d\d|'
                       rf'\d{{1,2}}\s+{MONTHS}\s+(?:19|20)\d\d|{MONTHS}\s+(?:19|20)\d\d)\s*$', re.I)
# journal templates (v1.1.0)
FOOTER = re.compile(r'(?:[A-Z]{4,}|\b[A-Z][a-z]+)\s*\|\s*(?i:vol(?:ume)?)\.?\s*\d+(?:\.\d+)?(?:\s*\|\s*(?:(?i:issue)\s*\d+\s*\|\s*)?\d{1,4})?')
SUPP_SPAN = re.compile(r'\b(Figures?|Figs?\.|Tables?|Texts?|Movies?|Data ?[Ss]ets?|Videos?|Animations?)\s+(S\d+[a-z]?'
                       r'(?:\s*(?:,|and|&|–|-|to)\s*S?\d+[a-z]?)*)')
EXT_DATA = re.compile(r'\bExtended Data (Fig(?:ure)?s?\.?|Tables?)')
SUPP_INFO = re.compile(r'\bSupporting Information\b')
PLS = re.compile(r'\bPlain Language Summary\b', re.I)
REPO = re.compile(r'(?:https?://)?(?:www\.)?(github|gitlab)\.com/[^\s)\]>,;]+|(?:https?://)?(?:dx\.)?(?:doi\.org/)?10\.5281/zenodo\.\d+|'
                  r'(?:https?://)?(?:www\.)?zenodo\.org/(?:records?|deposit|communities)/[^\s)\]>,;]+|'
                  r'(?:https?://)?(?:dx\.)?(?:doi\.org/)?10\.6084/m9\.figshare\.[\w.]+|(?:https?://)?(?:www\.)?figshare\.com/[^\s)\]>,;]+', re.I)
AFFIL_CHECK = re.compile(r'universit|laborator|institute of|department of|geological survey', re.I)  # independent check (critique, Oct 27)
JOURNAL_DOI = re.compile(r'\[journal\][^\n]{0,80}?(?:\b10\.\d{4,5}/|\be\d{4}[A-Z]{2}\d{6}\b|\b(?:19|20)\d\d[A-Z]{2}\d{6}\b)')
TEMPLATE = {'pls_heading': PLS, 'key_point_bullet': re.compile(r'^\s*[•●▪]', re.M), 'supp_s_number': re.compile(r'\b(?:Figure|Fig\.|Table|Text|Movie)s?\s+S\d'),
            'extended_data': re.compile(r'\bExtended Data\b'), 'pipe_footer': FOOTER}


CREDIT = re.compile(r'\b(conceptuali[sz]ation|data curation|formal analysis|funding acquisition|investigation|methodology|'
                    r'project administration|resources|software|supervision|validation|visuali[sz]ation|writing\s*[–—-]\s*'
                    r'(?:original draft|review))\s*:', re.I)
SLUG = re.compile(r'\.indd\b|\.pdf\s+\d|^\s*\d+\s*of\s*\d+\s*$', re.I)
# v1.2.0 leak scrubs
GOV_NOTICE = re.compile(r'[^.\n]{0,160}\b(?:government work|work of the U\.?\s?S\.? government|public\s+domain\s+in\s+the\s+'
                        r'(?:USA|U\.S\.A?\.?|United States))\b[^.]{0,160}\.?', re.I)
OUR_PRIOR = re.compile(r'\b([Oo])ur\s+(own\s+)?(previous|earlier|prior|former|recent)\b')
WILEY_COLOR = re.compile(r'\s*\[\s*Colou?r\s+figure\s+can\s+be\s+viewed\s+(?:at|in)\b[^\]\[]{0,160}\]', re.I)
BODY_DOI = re.compile(r'(?:https?://)?(?:dx\.)?(?:doi\.org/|doi:\s*)?\b(10\.\d{4,9})/[^\s)\]>,;]+', re.I)
DATA_HOSTS = {'10.5281': 'zenodo', '10.6084': 'figshare', '10.1594': 'pangaea', '10.5061': 'dryad', '10.17632': 'mendeley data',
              '10.4211': 'hydroshare', '10.17605': 'osf', '10.7910': 'dataverse', '10.7914': 'fdsn network', '10.24381': 'copernicus cds',
              '10.5067': 'nasa daac', '10.5065': 'ncar', '10.15485': 'ess-dive', '10.26022': 'earthchem', '10.4121': '4tu',
              '10.5285': 'bodc', '10.7289': 'noaa ncei', '10.25921': 'noaa ncei', '10.5066': 'usgs', '10.5069': 'usgs',
              '10.18739': 'arctic data center', '10.15468': 'gbif', '10.5880': 'gfz data services', '10.1029': 'agu',
              '10.5194': 'copernicus', '10.22033': 'esgf', '10.26050': 'wdcc', '10.14470': 'gfz data services'}
CITE_HEADER = re.compile(r'^\s*(?:\[journal\][^\n]{0,40}?|[A-Z][\w.&\s]{0,60}?)\.?\s*(?:19|20)\d\d\s*;\s*\d+\s*(?:\(\d+\))?\s*:\s*'
                         r'[\w]+(?:\s*[–-]\s*\w+)?\.?\s*$', re.M)
EDITOR_LABEL = re.compile(r'(?:edited by|(?:production|handling|associate|copy (?:&|and) layout|guest|section|chief|managing)?\s*'
                          r'editors?\s*:|reviewed by|reviewers?\s*:)', re.I)
NAME_LINE = re.compile(r"^(?:[A-ZÀ-Þ][\w'’\-À-ÿ]*\.?\s+){1,3}[A-ZÀ-Þ][\w'’\-À-ÿ]+(?:\s*(?:,|and|&)\s*(?:[A-ZÀ-Þ][\w'’\-À-ÿ]*\.?\s+){1,3}"
                       r"[A-ZÀ-Þ][\w'’\-À-ÿ]+)*\s*,?$")


def _head(s: str) -> str:
    """Collapse letter-spaced headings ('R E F E R E N C E S', 'RE FE RE NCE S', 'A C K N O W L E D G M E N T S')."""
    toks = s.split()
    if 2 <= len(toks) <= 4 and len(s) < 40 and re.fullmatch(r'[A-Z\s]+', s.strip()):
        return ''.join(toks) if (DROP_SEC.match(''.join(toks)) or REF_HEAD.match(''.join(toks))) else s
    if len(toks) >= 3 and re.fullmatch(r'[A-Z\s&]+', s.strip()) and sum(len(t) <= 3 for t in toks) >= 0.6 * len(toks):
        return ''.join(toks)
    return s


# ----------------------------------------------------------------------------------------------------------- metadata

def _norm(s: str) -> str:
    return unicodedata.normalize('NFKC', s or '')


def _ascii(s: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))


def _cached_openalex(path: str, params: dict) -> dict | None:
    """Read a response from the OpenAlex cache written by tools/roadmap/common.openalex (same URL hashing); no network."""
    url = f'{API}/{path.lstrip("/")}' + ('?' + urllib.parse.urlencode(params, safe=':,|') if params else '')
    f = OPENALEX_RAW / (hashlib.sha1(url.encode()).hexdigest() + '.json')
    return json.loads(f.read_text())['response'] if f.is_file() else None


_METRICS: dict | None = None


def metrics() -> dict:
    global _METRICS
    if _METRICS is None:
        _METRICS = {}
        for s in ('gold', 'r2'):
            p = DATA / 'derived' / s / 'metrics.json'
            if p.is_file():
                for m in json.loads(p.read_text())['data']:
                    _METRICS.setdefault('g22_' + m['id'], m)
    return _METRICS


_ABSTRACTS = None


def record_abstract(key: str) -> str:
    """The paper's abstract from the bibliographic record (derived/{gold,r2}/screen_input.json, rebuilt from OpenAlex's
    abstract_inverted_index by g06), boilerplate sentences dropped; '' when there is none."""
    global _ABSTRACTS
    if _ABSTRACTS is None:
        _ABSTRACTS = {}
        for s in ('gold', 'r2'):
            p = DATA / 'derived' / s / 'screen_input.json'
            if p.is_file():
                for x in json.loads(p.read_text())['data']:
                    _ABSTRACTS.setdefault(x['key'], x.get('abstract') or '')
    a = re.sub(r'^\s*abstract[\s.:]*', '', _ABSTRACTS.get(key) or '', flags=re.I).strip()
    return ' '.join(x for x in re.split(r'(?<=[.!?])\s+', a) if x and not BOILER.search(x))


def _coverage(part: str, text: str) -> float:
    """Share of the word 5-grams of `part` (words of 4 or more letters, every third start) found in `text`."""
    w = re.findall(r'[a-z]{4,}', part.lower())
    grams = [' '.join(w[i:i + 5]) for i in range(0, max(0, len(w) - 5), 3)]
    t = ' '.join(re.findall(r'[a-z]{4,}', text.lower()))
    return sum(g in t for g in grams) / len(grams) if grams else 1.0


def source_record(source_id: str | None) -> dict:
    """OpenAlex source (journal) record with abbreviations; free API, cached under blind/sources/. {} when offline."""
    if not source_id:
        return {}
    f = CACHE / 'sources' / f'{source_id}.json'
    if f.is_file():
        return json.loads(f.read_text())
    params = {'select': 'id,display_name,abbreviated_title,alternate_titles,host_organization_name'}
    key = os.environ.get('OPENALEX_API_KEY')
    if key:
        params['api_key'] = key
    url = f'{API}/sources/{source_id}?' + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'metascience-roadmap/1.0'}), timeout=60) as r:
            rec = json.load(r)
    except Exception:  # noqa: BLE001  (offline or rate limited: scrub with the metrics name only)
        return {}
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps({'retrieved': time.strftime('%Y-%m-%d'), **rec}, indent=1))
    return rec


def meta_for(key: str) -> dict:
    """Journal, publisher and authors of one paper, from the round metrics and the cached OpenAlex work record."""
    m = metrics().get(key, {})
    wid = key.removeprefix('g22_')
    w = _cached_openalex(f'works/{wid}', {'select': 'id,referenced_works,authorships'}) or {}
    src = source_record(m.get('source_id'))
    authors = []
    for a in w.get('authorships', []):
        names = {_norm((a.get('author') or {}).get('display_name') or ''), _norm(a.get('raw_author_name') or '')} - {''}
        orcid = ((a.get('author') or {}).get('orcid') or '').rsplit('/', 1)[-1]
        insts = [_norm(i.get('display_name') or '') for i in a.get('institutions', []) if i.get('display_name')]
        authors.append({'names': sorted(names), 'orcid': orcid, 'institutions': insts,
                        'raw_affiliations': [_norm(s) for s in a.get('raw_affiliation_strings', []) if s]})
    journals = {m.get('journal'), src.get('display_name'), src.get('abbreviated_title'), *(src.get('alternate_titles') or [])} - {None, ''}
    pubs = set(PUBLISHERS) | ({m.get('publisher'), src.get('host_organization_name')} - {None, ''})
    return {'key': key, 'doi': m.get('doi') or '', 'title': m.get('title') or '', 'journals': sorted(journals),
            'publishers': sorted(pubs), 'authors': authors, 'have_work_record': bool(w), 'have_source_record': bool(src)}


# ----------------------------------------------------------------------------------------------------------- patterns

def _loose(name: str) -> str:
    """Regex for a journal or publisher name that tolerates punctuation, '&'/'and', hyphens and line breaks."""
    words = [w for w in re.split(r'[\s:,\-–—./()]+', _ascii(name)) if w]
    parts = [r'(?:and|&)' if w.lower() in ('and', '&') else re.escape(w) for w in words]
    return r'\b' + r'[\s:,\-–—./()]*'.join(parts) + (r'\b' if words and words[-1][-1].isalnum() else '')


STOP = ('of', 'the', 'and', '&', 'for', 'in', 'on', 'de', 'la', 'et')


def _initialism(name: str) -> str | None:
    caps = [w[0] for w in re.split(r'[\s:,\-–—]+', name) if w and w[0].isupper() and w.lower() not in STOP]
    return ''.join(caps) if 3 <= len(caps) <= 6 else None


def _abbrev(name: str, min_sig: int = 3, min_prefix: int = 1) -> str | None:
    """Case-sensitive regex for abbreviations of a name of three or more significant words: every significant word may be
    shortened to any prefix with an optional period, stop words are optional ('J. Geophys. Res. Solid Earth',
    'Q J R Meteorol Soc', 'Earth Planet. Sci. Lett.')."""
    words = [w if w.lower() in STOP else w[0].upper() + w[1:] for w in re.split(r'[\s:,\-–—./()]+', _ascii(name)) if w]
    sig = [w for w in words if w.lower() not in STOP]
    if len(sig) < min_sig or not all(w[0].isalpha() for w in sig):
        return None
    parts = []
    for w in words:
        if w.lower() in STOP:
            parts.append(rf'(?:{re.escape(w)}\s+|{re.escape(w.capitalize())}\s+|&\s*)?' if w.lower() != '&' else r'(?:&\s*|and\s+)?')
        else:
            alts = '|'.join(re.escape(w[:k]) for k in range(len(w), min(min_prefix, len(w)) - 1, -1))
            parts.append(rf'(?:{alts})\.?[\s:,\-–]*')
    return r'\b' + ''.join(parts).rstrip('[\\s:,\\-–]*') + r'(?![A-Za-z])'


def journal_patterns(journals: list[str]) -> list[re.Pattern]:
    """Long names (3+ significant words): full name anywhere, case-insensitive, and abbreviations, case-sensitive.
    Short names (Tectonics, Ocean Science, Geology, Water): only followed by a volume or year number, so the same words in
    running text are kept; the volume may follow a '|' ('SEISMICA | volume 1.1'), and a one-word name in capitals
    ('SEISMICA', 'TECTONICS') is matched anywhere. Initialisms of 3 to 6 capitals (GJI, BSSA, EPSL): whole word,
    case-sensitive."""
    out = []
    for j in journals:
        for v in {j, _ascii(j)}:
            sig = [w for w in re.split(r'[\s:,\-–—./()]+', v) if w and w.lower() not in STOP]
            if len(sig) >= 3:
                out.append(re.compile(_loose(v), re.I))
                if (a := _abbrev(v)):
                    out.append(re.compile(a))
            elif sig:
                vol = r'(?=\s*[,.;:|]?\s*(?:\d|vol\b|volume\b))'
                out.append(re.compile(_loose(v) + vol, re.I))
                if len(sig) == 1 and len(sig[0]) >= 5:
                    out.append(re.compile(r'(?<![A-Z])' + re.escape(sig[0].upper()) + r'(?![A-Z])'))
                if len(sig) == 2 and (a := _abbrev(v, min_sig=2, min_prefix=3)):
                    out.append(re.compile(a + vol))
        if (i := _initialism(j)):
            out.append(re.compile(r'\b' + re.escape(i) + r'\b'))
    return out


def patterns(meta: dict) -> dict:
    journals = sorted((j for j in meta['journals'] if len(j) >= 4), key=len, reverse=True)   # longest first (v1.2.0)
    pre = [_loose(p) for p in meta['publishers'] if len(p) >= 3]
    surn, full, insts, raws, orcids, units = set(), set(), set(), set(), set(), set()
    for a in meta['authors']:
        for n in a['names']:
            n = re.sub(r'\s+', ' ', n).strip()
            if not n:
                continue
            toks = n.replace(',', ' ').split()
            last = toks[-1] if ',' not in n else n.split(',')[0].strip()
            if len(last) >= 2:
                surn.add(last); surn.add(_ascii(last))
            if len(toks) >= 2:
                full.add(n); full.add(_ascii(n))
                first = toks[0] if ',' not in n else n.split(',')[1].strip().split()[0]
                full.add(f'{first[0]}. {last}'); full.add(f'{last}, {first[0]}.'); full.add(f'{first[0]}.{last}')
        insts |= {i for i in a['institutions'] if len(i) >= 6}
        raws |= {r for r in a['raw_affiliations'] if len(r) >= 12}
        # v1.2.0: unit segments of the raw affiliation strings ('Asian School of the Environment', 'Laboratoire Magmas et
        # Volcans'), replaced in the body as [institution]
        for r in a['raw_affiliations']:
            for seg in re.split(r'\s*[,;]\s*', r):
                seg = re.sub(r'^\s*(?:\d+|[a-z])\s+', '', seg).strip(' .')
                if 12 <= len(seg) <= 90 and AFFIL_WORDS.search(seg) and not COUNTRY.search(seg):
                    units.add(seg)
        if a['orcid']:
            orcids.add(a['orcid'])
    doi = meta['doi'].lower().replace('https://doi.org/', '')
    return {'journal': journal_patterns(journals),
            'publisher': re.compile('|'.join(sorted(set(pre), key=len, reverse=True))) if pre else None,
            'surnames': sorted(surn, key=len, reverse=True), 'full': sorted(full - {''}, key=len, reverse=True),
            'institutions': sorted(insts, key=len, reverse=True), 'raw_affiliations': sorted(raws, key=len, reverse=True),
            'institution_names': sorted(insts | units, key=len, reverse=True),
            'orcids': sorted(orcids), 'doi': doi, 'title': meta.get('title') or ''}


def _surname_cite(s: str) -> re.Pattern:
    """A surname in a citation context: followed by 'et al.', ', et al.', 'and X', '& X', ', X', ', and X', initials
    ('Li X N et al.'), a year, or a reference number ('Vantassel 27', 'Adelfio (1)')."""
    e = re.escape(s)
    ctx = (r'(?=,?\s*et\s+al\b|\s+and\s+[A-Z\[]|\s*&\s*[A-Z\[]|,\s*(?:and\s+|&\s*)?[A-Z\[]|[,\s(]*\(?(?:19|20)\d\d[a-z]?\b'
           r'|\s+\d{1,3}(?![\d.])|\s*\(\d{1,3}\)|(?:\s+[A-Z]\b){1,3})')
    return re.compile(rf'(?<![\w-])(?:{e}|{re.escape(s.upper())})(?![\w-]){ctx}')


def _surname_ref(s: str) -> re.Pattern:
    """A surname in an author position of a reference: 'Smith, J.', 'Smith J', 'J. Smith', 'Smith and', 'Smith,'."""
    e = re.escape(s)
    return re.compile(rf'(?:\b{e}\b(?=\s*,|\s+[A-Z]\.|\s+[A-Z]{{1,3}}\b|\s+(?:and|&|et al)\b)|(?<=[A-Z]\.\s){e}\b|(?<=[A-Z]\.){e}\b)')


def templates(text: str) -> str:
    """Journal templates neutralized in the body (v1.1.0): PLS heading, S-numbered supplement names, Extended Data,
    Supporting Information, '|' running footers merged into a line."""
    text = FOOTER.sub('', text)
    text = PLS.sub('Summary', text)
    text = SUPP_SPAN.sub(lambda m: f"Supplementary {m.group(1)} " + re.sub(r'\bS(\d)', r'\1', m.group(2)), text)
    text = EXT_DATA.sub(lambda m: f'Supplementary {m.group(1)}', text)
    return SUPP_INFO.sub('Supplementary Material', text)


def scrub(text: str, P: dict, refs: bool) -> str:
    """refs=False: the body; refs=True: the reference list, where only the paper's own DOI, e-mails, ORCID and repository
    URLs are replaced (citations stay as printed, v1.1.0)."""
    text = REPO.sub(lambda m: f'[repository URL ({(m.group(1) or ("zenodo" if "zenodo" in m.group(0).lower() else "figshare")).lower()})]', text)
    if P['doi']:
        d = re.escape(P['doi'])
        text = re.sub(rf'(?:https?://)?(?:dx\.)?(?:doi\.\s?org/)?(?:doi:\s*)?{d}\S*', '[DOI]', text, flags=re.I)
        suffix = P['doi'].split('/', 1)[-1]
        if len(suffix) >= 6:  # article number or DOI suffix printed without the prefix (AGU e2021JB023701, Copernicus os-18-979-2022)
            text = re.sub(rf'\b[eE]?{re.escape(suffix)}\b', '[DOI]', text, flags=re.I)
    text = WILEY_COLOR.sub('', text)     # also in the reference block: pdftotext puts appendices after the references
    if not refs:
        text = BODY_DOI.sub(_body_doi, text)
        text = URL.sub(lambda m: '[publisher URL]' if any(dm in m.group(0).lower() for dm in DOMAINS) else m.group(0), text)
        text = BARE_URL.sub(lambda m: '[publisher URL]' if any(dm in m.group(0).lower() for dm in DOMAINS) else m.group(0), text)
    text = EMAIL.sub('', text)
    text = ORCID.sub('', text)
    if refs:
        return text
    for r in P['raw_affiliations']:
        text = text.replace(r, '')
    text = INITIALS_INLINE.sub('([author])', text)
    for n in P['full']:
        if len(n) >= 4:
            text = re.sub(rf'(?<![A-Za-z]){re.escape(n)}(?![A-Za-z])', '[author]', text)
    for n in P.get('institution_names', []):
        text = re.sub(r'(?<![\w-])' + r'\s+'.join(map(re.escape, n.split())) + r'(?![\w-])', '[institution]', text)
    text = OUR_PRIOR.sub(lambda m: m.group(3).capitalize() if m.group(1) == 'O' else m.group(3), text)   # 'our previous' -> 'previous'
    text = GOV_NOTICE.sub('', text)
    text = templates(text)
    for rx in P['journal']:
        text = rx.sub('[journal]', text)
    if P['publisher'] is not None:
        text = P['publisher'].sub('[publisher]', text)
    return CITE_HEADER.sub('', text)


def _body_doi(m: re.Match) -> str:
    """A DOI left in the body (data availability, captions): [repository DOI (host)] for known data hosts, else
    [DOI (other)]; a trailing sentence period is kept."""
    s, tail = m.group(0), ''
    while s and s[-1] in '.':
        s, tail = s[:-1], tail + '.'
    host = DATA_HOSTS.get(m.group(1))
    return (f'[repository DOI ({host})]' if host else '[DOI (other)]') + tail


def drop_own_citation(text: str, P: dict) -> tuple[str, int]:
    """pdftotext route: remove the paper's own 'how to cite' box. Lines that are fragments of the paper's title
    (at least 20 letters and digits, found in the title) are removed, and within 6 lines of one, lines that name one
    of the paper's authors, a journal name, [journal], [DOI] or a 'volume(issue), pages' string. (number of lines removed)"""
    nt = re.sub(r'[^0-9a-z]', '', _ascii(P.get('title') or '').lower())
    if len(nt) < 30:
        return text, 0
    lines = text.split('\n')
    frag = [i for i, ln in enumerate(lines) if not ln.startswith('TITLE:') and
            len(x := re.sub(r'[^0-9a-z]', '', _ascii(ln).lower())) >= 20 and x in nt]
    if not frag:
        return text, 0
    name_rx = [re.compile(rf'(?<![A-Za-z]){re.escape(n)}(?![A-Za-z])') for n in P['full'] if len(n) >= 4]
    cite = re.compile(r'\[journal\]|\[DOI\]|\b\d+\s*\(\d+\)\s*,\s*\d+\s*[–-]\s*\d+|how to cite', re.I)
    drop = set(frag)
    for i in frag:
        for j in range(max(0, i - 6), min(len(lines), i + 7)):
            ln = lines[j]
            if j not in drop and not MARKLINE.match(ln) and (cite.search(ln) or any(r.search(ln) for r in name_rx)
                                                             or any(r.search(ln) for r in P['journal'])):
                drop.add(j)
    return '\n'.join(ln for j, ln in enumerate(lines) if j not in drop), len(drop)


MARKLINE = re.compile(r'^\[p\. \d+\]$')


def leakage(body: str, refs: str, P: dict) -> dict:
    def cnt(rx, s):
        return len(rx.findall(s)) if rx is not None else 0

    def part(s, is_refs):
        jn = len({m.span() for rx in P['journal'] for m in rx.finditer(s)})
        out = {('journal_name_unmarked' if is_refs else 'journal'): jn, 'publisher': cnt(P['publisher'], s) if not is_refs else 0,
               'author_full_name': sum(len(re.findall(rf'(?<![A-Za-z]){re.escape(n)}(?![A-Za-z])', s)) for n in P['full'] if len(n) >= 4) if not is_refs else 0,
               'self_citation_printed': sum(len((_surname_ref(x) if is_refs else _surname_cite(x)).findall(s)) for x in P['surnames']),
               'author_token': s.count('[author]'), 'journal_token_with_doi': len(JOURNAL_DOI.findall(s)),
               'repository_segment': len(REPO.findall(s)),
               'doi': (len(re.findall(re.escape(P['doi']), s, re.I)) + (len(re.findall(rf"\\b{re.escape(P['doi'].split('/', 1)[-1])}\\b", s, re.I))
                                                                         if len(P['doi'].split('/', 1)[-1]) >= 6 else 0)) if P['doi'] else 0,
               'email': len(EMAIL.findall(s)), 'orcid': len(ORCID.findall(s)),
               'publisher_url': sum(any(d in u.lower() for d in DOMAINS) for u in URL.findall(s) + BARE_URL.findall(s)) if not is_refs else 0,
               'ack_phrase': len(ACK.findall(s)) if not is_refs else 0}
        if not is_refs:
            out.update({f'template_{k}': len(rx.findall(s)) for k, rx in TEMPLATE.items()})
            # v1.2.0 leak cues
            out['own_institution'] = sum(len(re.findall(r'(?<![\w-])' + r'\s+'.join(map(re.escape, n.split())) + r'(?![\w-])', s))
                                         for n in P.get('institution_names', []))
            out['first_person_prior_work'] = len(OUR_PRIOR.findall(s))
            out['government_notice'] = len(GOV_NOTICE.findall(s))
            out['citation_header_line'] = len(CITE_HEADER.findall(s))
            out['wiley_color_note'] = len(WILEY_COLOR.findall(s))
            out['body_doi'] = len(BODY_DOI.findall(s))
            out['affiliation_words_first_6000'] = len(AFFIL_CHECK.findall(s[:6000]))
        return out
    return {'body': part(body, False), 'references': part(refs, True)}


# Fields of leakage() that are information, not leakage: kept on purpose (citations as printed), or an upper bound.
INFO_FIELDS = {'references.journal_name_unmarked', 'body.self_citation_printed', 'references.self_citation_printed'}


# ----------------------------------------------------------------------------------------------------------- XML route

def _local(tag) -> str:
    return tag.rsplit('}', 1)[-1] if isinstance(tag, str) else ''


def _join(e) -> str:
    s = ' '.join(t.strip() for t in e.itertext() if t and t.strip())
    return re.sub(r'\s+([,.;:)])', r'\1', re.sub(r'\(\s+', '(', re.sub(r'\s+', ' ', s))).strip()


def xml_references(xml_path: Path) -> list[str]:
    """Reference list of a JATS or Elsevier full-text XML, one plain-text entry per reference."""
    if not xml_path.is_file():
        return []
    sys.path.insert(0, str(ROOT / 'tools'))
    from jats_text import parse  # noqa: E402
    try:
        root = parse(xml_path)
    except ET.ParseError:
        return []
    out = []
    for r in (e for e in root.iter() if _local(e.tag) in ('ref', 'bib-reference')):
        struct = next((e for e in r.iter() if _local(e.tag) in ('element-citation', 'reference', 'citation')), None)
        mixed = next((e for e in r.iter() if _local(e.tag) in ('mixed-citation', 'other-ref', 'textref')), None)
        if mixed is not None and struct is None:
            out.append(_join(mixed)); continue
        if struct is None:
            t = _join(r)
            if t:
                out.append(t)
            continue
        names, rest = [], []
        for a in (e for e in struct.iter() if _local(e.tag) in ('name', 'author', 'string-name')):
            sur = next((x.text for x in a.iter() if _local(x.tag) == 'surname' and x.text), '')
            giv = next((x.text for x in a.iter() if _local(x.tag) in ('given-names', 'given-name') and x.text), '')
            if sur:
                names.append(f'{sur.strip()}, {giv.strip()}'.rstrip(', '))
        skip = {'name', 'author', 'string-name', 'surname', 'given-names', 'given-name', 'person-group', 'authors'}
        for e in struct.iter():
            if _local(e.tag) in skip or len(e):
                continue
            # leaf element not inside an author name
            if e.text and e.text.strip():
                rest.append(e.text.strip())
        names_set = {n for a in names for n in a.replace(',', ' ').split()}
        rest = [x for x in rest if x not in names_set]
        out.append('; '.join(names) + ('. ' if names else '') + ', '.join(rest))
    return [re.sub(r'\s+', ' ', x).strip() for x in out if x.strip()]


def from_xml(xml_text: str, xml_path: Path) -> tuple[str, str, list]:
    """(body, references, dropped section headings) from the located XML text."""
    lines, drop, dropped = [], None, []
    for ln in xml_text.splitlines():
        if ln.startswith('DOI:'):
            continue
        m = re.match(r'^§(\S+) ?(.*)$', ln)
        if m:
            num, title = m.groups()
            if drop and (num == drop or num.startswith(drop + '.')):
                continue
            drop = None
            if DROP_SEC.match(title.strip()):
                drop = num; dropped.append(title.strip()); continue
        else:
            p = re.match(r'^\[§(\S+) ¶\d+\]', ln)
            if p and drop and (p.group(1) == drop or p.group(1).startswith(drop + '.')):
                continue
            if not p and drop and not ln.startswith('['):
                continue
        lines.append(ln)
    refs = xml_references(xml_path)
    ref_text = '\n'.join(f'[Ref {i}] {r}' for i, r in enumerate(refs, 1))
    return '\n'.join(lines), ref_text, dropped


# ----------------------------------------------------------------------------------------------------------- PDF route

def _key_line(s: str) -> str:
    return re.sub(r'\d+', '#', re.sub(r'\s+', ' ', s.strip().lower()))


def from_pdf(pdf: Path, P: dict) -> tuple[str, str, list]:
    raw = subprocess.run(['pdftotext', '-enc', 'UTF-8', str(pdf), '-'], capture_output=True, text=True, timeout=180).stdout
    pages = [pg.splitlines() for pg in raw.split('\f')]
    while pages and not any(x.strip() for x in pages[-1]):
        pages.pop()
    # running headers and footers: normalized lines among the first/last 4 non-empty lines of a page, repeated on many pages
    from collections import Counter
    zone = Counter()
    for pg in pages:
        ne = [x for x in pg if x.strip()]
        for x in set(_key_line(y) for y in ne[:4] + ne[-4:]):
            zone[x] += 1
    thr = max(3, int(0.3 * len(pages)))
    repeated = {k for k, v in zone.items() if v >= thr and len(k) < 160}
    inst_rx = [re.compile(re.escape(i), re.I) for i in P['institutions']]
    name_rx = [re.compile(rf'(?<![A-Za-z]){re.escape(n)}(?![A-Za-z])') for n in P['full'] if len(n) >= 4]
    sur_rx = [re.compile(rf'\b(?:{re.escape(s)}|{re.escape(s.upper())})\b') for s in P['surnames']]
    # front matter: when an abstract or introduction heading is found on page 1 or 2 (or an abstract heading on page 3 or
    # 4, as in accepted manuscripts with a title page), every line before it is dropped (title block, authors,
    # affiliations, correspondence, dates, citation box, funding, and since v1.1.0 the AGU key-point bullets, a journal
    # template); otherwise the line filters below remove what names an author or institution
    front_end = (next(((i, j) for i, pg in enumerate(pages[:2], 1) for j, x in enumerate(pg) if ABS_HEAD.match(_head(x.strip()))), None)
                 or next(((i, j) for i, pg in enumerate(pages[2:4], 3) for j, x in enumerate(pg) if ABS_ONLY.match(_head(x.strip()))), None))
    front_drop = set()
    if front_end:
        for i, pg in enumerate(pages[:front_end[0]], 1):
            for j, x in enumerate(pg):
                if (i, j) >= front_end:
                    break
                front_drop.add((i, j))
    out_pages, dropped, in_refs, ref_lines, drop_left, skip_para = [], [], False, [], 0, False
    front = front_end is None
    affil = False   # inside an affiliation or address block (v1.1.0)
    editor_left = 0  # name-only lines still to drop after an editor label (v1.2.0)
    last_front_page = max(2, front_end[0] if front_end else 2)
    for i, pg in enumerate(pages, 1):
        body_part, ref_part = [], []
        for j, x in enumerate(pg):
            if (i, j) in front_drop:
                skip_para = False
                continue
            s = x.strip()
            if not s:
                skip_para = False
                (ref_part if in_refs else body_part).append(''); continue
            if re.fullmatch(r'[\d\s]+', s) or _key_line(s) in repeated:
                continue
            s = FOOTER.sub('', s).strip()
            if not s:
                continue
            named = any(r.search(s) for r in name_rx) or any(r.search(s) for r in inst_rx)
            if affil:
                if len(s) < 100 and (AFFIL_WORDS.search(s) or ADDRESS.search(s) or COUNTRY.search(s) or COUNTRY_INLINE.search(s)
                                     or INITIALS_LINE.match(s) or named):
                    continue
                affil = False
            if COUNTRY_RUNON.search(s) and len(s) < 200:
                affil = True
                continue
            if INITIALS_LINE.match(s) or (i <= 4 and DATE_LINE.match(s)):
                continue
            if i <= last_front_page + 1 and len(s) < 220 and (
                    (AFFIL_NUM.match(s) and AFFIL_STRONG.search(s)) or (AFFIL_HEAD.match(s) and len(s) < 120)
                    or (len(s) < 70 and s.endswith(',') and (AFFIL_WORDS.search(s) or AFFIL_UNIT.search(s))) or (named and len(s) < 120)):
                affil = True
                continue
            if front and i <= 2 and ABS_HEAD.match(_head(s)):
                front = False
            if front and i <= 2 and (any(r.search(s) for r in name_rx) or any(r.search(s) for r in inst_rx)
                                     or (AFFIL_WORDS.search(s) and len(s) < 220) or EMAIL.search(s)
                                     or (any(r.search(s) for r in sur_rx) and len(s) < 200 and ',' in s)):
                continue
            if skip_para:
                continue
            if SLUG.search(s):
                continue
            if CREDIT.search(s) and len(CREDIT.findall(s)) >= 2 or re.match(CREDIT.pattern, s, re.I):
                skip_para = True; dropped.append('author contributions (CRediT roles)'); continue
            if re.match(r'^\s*(?:photo|image) (?:credit|courtesy)', s, re.I):
                continue
            if editor_left:
                if NAME_LINE.match(s) and len(s) < 80:
                    editor_left -= 1; continue
                editor_left = 0
            if EDITOR_LABEL.search(s) and len(s) < 120:
                editor_left = 4
                rest = EDITOR_LABEL.split(s)[-1].strip()
                if not rest or NAME_LINE.match(rest) or len(s) < 80:
                    continue
            if BOILER.search(s) and len(s) < 300:
                # a citation or copyright notice runs on over several lines: drop to the end of its paragraph
                skip_para = bool(re.search(r'citation|cite|©|copyright|licen[cs]|open access|published by|received|accepted', s, re.I))
                continue
            h = _head(s)
            if not in_refs and REF_HEAD.match(h):
                in_refs, drop_left = True, 0
                continue
            if drop_left:
                if STOP_HEAD.match(h) and not DROP_SEC.match(h):
                    drop_left = 0
                else:
                    drop_left -= 1; continue
            if (DROP_SEC.match(h) and len(h) < 60) or DROP_RUNIN.match(h):
                dropped.append(s[:60]); drop_left = 80; continue
            (ref_part if in_refs else body_part).append(s)
        txt = re.sub(r'\n{3,}', '\n\n', '\n'.join(body_part)).strip()
        if txt:
            out_pages.append(f'[p. {i}]\n{txt}')
        rtxt = re.sub(r'\n{3,}', '\n\n', '\n'.join(ref_part)).strip()
        if rtxt:
            ref_lines.append(f'[p. {i}]\n{rtxt}')
    refs = ('References\n' + '\n\n'.join(ref_lines)) if ref_lines else ''
    body, nb = drop_own_citation('\n\n'.join(out_pages), P)
    refs, nr = drop_own_citation(refs, P)
    if nb + nr:
        dropped.append(f"own citation box ({nb + nr} lines)")
    return body, refs, dropped


# ----------------------------------------------------------------------------------------------------------- build

def sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def build(key: str, pdf: Path, xml_text: str | None = None, refresh: bool = False) -> tuple[str, dict]:
    """(blinded text, meta) for one paper. xml_text is what code_papers.xml_text_for(pdf) returned (None: use the PDF)."""
    pdf = Path(pdf)
    xml_path, xml_from, fallback, n_body = pdf.with_suffix('.xml'), None, None, None
    if xml_text:
        # v1.2.0: regenerate from the XML with the Elsevier-body and table-row options; the .xml.txt is the fallback
        xml_from = 'xml.txt'
        if xml_path.is_file():
            sys.path.insert(0, str(ROOT / 'tools'))
            from jats_text import parse, convert  # noqa: E402
            try:
                xml_text, xml_from = convert(parse(xml_path), descend_sections=True, table_rows=True, availability=True), 'xml'
            except ET.ParseError:
                pass
        n_body = len(re.findall(r'^\[§(?!0 |D\d)[^\]]* ¶\d+\]', xml_text, re.M))   # abstract and availability excluded
        if n_body < MIN_BODY_PARAS:
            fallback = f'{n_body} body paragraphs in the XML text (fewer than {MIN_BODY_PARAS}): pdftotext used'
            xml_text = None
    src = 'xml' if xml_text else 'pdftotext'
    in_sha = sha(xml_text) if xml_text else hashlib.sha256(pdf.read_bytes()).hexdigest()
    ct, cm = CACHE / f'{key}.txt', CACHE / f'{key}.json'
    if not refresh and ct.is_file() and cm.is_file():
        m = json.loads(cm.read_text())
        if m.get('blind_version') == BLIND_VERSION and m.get('input_sha256') == in_sha:
            return ct.read_text(), m
    meta = meta_for(key)
    P = patterns(meta)
    if xml_text:
        body, refs, dropped = from_xml(xml_text, pdf.with_suffix('.xml'))
    else:
        body, refs, dropped = from_pdf(pdf, P)
    abstract_from_record = False
    if not xml_text:
        # v1.2.1: an abstract printed without a heading (Wiley two-column title pages) goes with the front matter cut at
        # the Introduction heading; the record abstract is put back at the top of page 1, labelled as such
        rec = record_abstract(key)
        if rec and _coverage(rec, body) < 0.5:
            lab = 'Abstract (from the bibliographic record; less than half of it was found in the PDF text) '
            body = re.sub(r'^(\[p\. \d+\]\n)?', lambda m: (m.group(0) or '') + lab + rec + '\n\n', body, count=1)
            abstract_from_record = True
    before = leakage(body, refs, P)
    body_s, refs_s = scrub(body, P, refs=False), scrub(refs, P, refs=True)
    after = leakage(body_s, refs_s, P)
    head = ('Locators: [§n ¶k] section n paragraph k; [Fig. n] / [Table n] captions and table rows; [Ref n] reference n.'
            if src == 'xml' else 'Locators: [p. N] marks the start of PDF page N.')
    title = '' if src == 'xml' else f"TITLE: {meta['title']}\n\n" if meta['title'] else ''
    text = (head + '\n\n' + title + body_s.strip() + '\n\n' + ('§R References\n' if src == 'xml' else '') + refs_s.strip() + '\n')
    m = {'key': key, 'blind_version': BLIND_VERSION, 'built': time.strftime('%Y-%m-%d %H:%M'), 'source': src,
         'input': str((xml_path if xml_from == 'xml' else pdf.with_suffix('.xml.txt')) if xml_text else pdf).replace(str(PRIVATE), 'private'),
         'xml_converter': 'jats_text.convert(descend_sections=True, table_rows=True, availability=True)' if xml_text and xml_from == 'xml' else None,
         'xml_body_paragraphs': n_body, 'xml_fallback': fallback, 'abstract_from_record': abstract_from_record,
         'input_sha256': in_sha, 'output_sha256': sha(text), 'chars': len(text), 'words': len(text.split()),
         'reference_entries': len(re.findall(r'^\[Ref \d+\]', refs_s, re.M)) if src == 'xml' else None,
         'have_work_record': meta['have_work_record'], 'have_source_record': meta['have_source_record'],
         'n_authors': len(meta['authors']), 'journal_names_scrubbed': meta['journals'], 'sections_dropped': dropped,
         'leakage_before': before, 'leakage_after': after}
    CACHE.mkdir(parents=True, exist_ok=True)
    ct.write_text(text)
    cm.write_text(json.dumps(m, indent=1, ensure_ascii=False))
    return text, m


def cached(key: str) -> str | None:
    f = CACHE / f'{key}.txt'
    return f.read_text() if f.is_file() else None


ARCHIVE = CACHE / 'archive'   # earlier versions, one folder per BLIND_VERSION (archive/1.1.1: the texts advance pilot 1 read)


def cached_as_read(key: str, sha256: str | None = None) -> tuple[str | None, dict]:
    """(text, meta) of the blinded text whose sha256 is the one a coder read (a coding's run.blind_sha256): the current
    cache when it matches or when no sha256 is given, else the archived version that matches; (None, {}) when none does."""
    cur, cm = cached(key), CACHE / f'{key}.json'
    if cur is not None and (sha256 is None or sha(cur) == sha256):
        return cur, (json.loads(cm.read_text()) if cm.is_file() else {})
    for d in sorted(ARCHIVE.glob('*'), reverse=True) if ARCHIVE.is_dir() else []:
        f = d / f'{key}.txt'
        if f.is_file() and sha(t := f.read_text()) == sha256:
            m = d / f'{key}.json'
            return t, (json.loads(m.read_text()) if m.is_file() else {'blind_version': d.name})
    return None, {}


def _queue_pdf(key: str) -> Path | None:
    q = json.loads((PRIVATE / 'download-queue.json').read_text())
    v = q.get(key) or {}
    if v.get('status') != 'have' or not v.get('file'):
        return None
    f = Path(v['file'])
    p = PRIVATE.joinpath(*f.parts[1:]) if f.parts and f.parts[0] == 'private' else ROOT / f
    return p if p.is_file() else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('keys', nargs='*'); ap.add_argument('--manifest'); ap.add_argument('--print', action='store_true')
    ap.add_argument('--refresh', action='store_true'); ap.add_argument('--no-xml', action='store_true')
    a = ap.parse_args()
    keys = list(a.keys)
    if a.manifest:
        keys += [json.loads(l)['key'] for l in Path(a.manifest).read_text().splitlines() if l.strip()]
    tot, n = {}, 0
    for k in keys:
        pdf = _queue_pdf(k)
        if not pdf:
            print(f'{k}: no PDF in the queue'); continue
        xt = pdf.with_suffix('.xml.txt')
        text, m = build(k, pdf, None if a.no_xml or not xt.is_file() else xt.read_text(), refresh=a.refresh)
        n += 1
        for part in ('body', 'references'):
            for f, v in m['leakage_after'][part].items():
                tot.setdefault(f'{part}.{f}', [0, 0]); tot[f'{part}.{f}'][0] += v; tot[f'{part}.{f}'][1] += v > 0
        if a.print:
            sys.stdout.write(text)
        elif not a.manifest:
            print(json.dumps({x: m[x] for x in ('key', 'source', 'chars', 'words', 'sections_dropped', 'leakage_before', 'leakage_after')}, indent=1))
    if a.manifest:
        print(f'{n} papers blinded; residual leakage after scrubbing: total occurrences, papers with any')
        for f, (v, p) in sorted(tot.items()):
            print(f'  {f:40s} {v:6d} {p:5d}' + ('   (information: kept on purpose)' if f in INFO_FIELDS else
                                                '   (upper bound: site names match too)' if f.endswith('first_6000') else
                                                '   (upper bound: body lists match too)' if f.endswith('key_point_bullet') else ''))
    return 0


if __name__ == '__main__':
    sys.exit(main())
