#!/usr/bin/env python3
"""Format test, step 0: inputs for coding the same papers from publisher XML text and from PDF text.

Input : six gold papers with both a PDF and publisher XML, CC BY (chosen 2026-10-25: three core, three broad ring;
        Copernicus and Springer Nature XML); private/data/roadmap/pdfs/gold/<key>.pdf and <key>.xml.txt
Output: derived/format_test/inputs/<key>.xml.txt  (tools/jats_text.py output, with section and paragraph locators)
        derived/format_test/inputs/<key>.pdf.txt  (pdftotext -layout; pages separated by form feeds)
        derived/format_test/design.json          papers, arms, replicate count
Arms  : X = located XML text only; T = pdftotext text only (the subagent coder's current input). Each arm coded twice
        per paper by independent coders, so the within-arm agreement is the noise floor for the between-arm comparison.
Run   : python tools/roadmap/f00_format_test_prep.py
"""
from __future__ import annotations
import shutil
import subprocess
from common import DATA, DERIVED, decision, log, write_json

PAPERS = ['g22_W4285387965', 'g22_W4283688628', 'g22_W4220724311', 'g22_W4306927857', 'g22_W4309046613', 'g22_W4292315839']
SRC = DATA / 'pdfs' / 'gold'
FT = DERIVED / 'format_test'


def main() -> None:
    (FT / 'inputs').mkdir(parents=True, exist_ok=True)
    (FT / 'codings').mkdir(parents=True, exist_ok=True)
    rows = []
    for k in PAPERS:
        shutil.copy(SRC / f'{k}.xml.txt', FT / 'inputs' / f'{k}.xml.txt')
        subprocess.run(['pdftotext', '-layout', str(SRC / f'{k}.pdf'), str(FT / 'inputs' / f'{k}.pdf.txt')], check=True)
        wx = len((FT / 'inputs' / f'{k}.xml.txt').read_text().split())
        wp = len((FT / 'inputs' / f'{k}.pdf.txt').read_text().split())
        rows.append({'key': k, 'words_xml_text': wx, 'words_pdf_text': wp})
        print(k, 'xml', wx, 'pdf', wp)
    write_json(FT / 'design.json', {'papers': rows, 'arms': {'X': 'located XML text only', 'T': 'pdftotext -layout text only'},
                                    'replicates': 2, 'codebook': '1.4.0'}, ['private/data/roadmap/pdfs/gold'])
    log('f00_format_test_prep.py', 'format-test inputs (XML text and PDF text)', len(rows))
    decision('Format test: six CC BY gold papers with both PDF and publisher XML, each coded twice from the located XML text (arm X) '
             'and twice from pdftotext text (arm T) by independent model coders under codebook 1.4.0; within-arm agreement is the '
             'noise floor; quote fidelity is checked against the XML text.')


if __name__ == '__main__':
    main()
