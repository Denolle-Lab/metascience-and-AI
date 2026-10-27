# Format test: XML text versus PDF

Papers: 6. Arms: X located XML text (subagent), T pdftotext text (subagent), P PDF via the batch API, PX PDF plus XML text via the batch API. Two independent codings per arm and paper. Agreement: tools/check_coding.py agree(), averaged within paper, then over papers.

## Agreement

| Pair | Papers | Node set | Mode set | Node sequence | Mode sequence | Entry node | Entry state | Outcome | Decisive mode |
|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|
| P within | 6 | 0.85 | 0.84 | 0.71 | 0.63 | 1.00 | 1.00 | 1.00 | 0.83 |
| P-PX | 6 | 0.89 | 0.84 | 0.61 | 0.62 | 0.92 | 1.00 | 1.00 | 0.83 |
| P-T | 6 | 0.87 | 0.75 | 0.67 | 0.56 | 0.83 | 1.00 | 0.92 | 0.92 |
| P-X | 6 | 0.86 | 0.78 | 0.57 | 0.52 | 0.83 | 0.92 | 0.92 | 0.92 |
| PX within | 6 | 0.87 | 0.83 | 0.69 | 0.66 | 0.83 | 1.00 | 1.00 | 0.83 |
| PX-T | 6 | 0.88 | 0.77 | 0.59 | 0.52 | 0.92 | 1.00 | 0.92 | 0.92 |
| PX-X | 6 | 0.87 | 0.82 | 0.60 | 0.57 | 0.92 | 0.92 | 0.92 | 0.92 |
| T within | 6 | 0.85 | 0.74 | 0.70 | 0.55 | 1.00 | 1.00 | 0.83 | 1.00 |
| T-X | 6 | 0.88 | 0.78 | 0.62 | 0.57 | 1.00 | 0.92 | 0.92 | 1.00 |
| X within | 6 | 0.86 | 0.87 | 0.64 | 0.63 | 1.00 | 0.83 | 0.83 | 1.00 |

## Agreement, the 4 papers whose PDF is the same version as the XML

Excluded: [withheld], [withheld] (the PDF was the discussion preprint, so arms T and P coded another version).

| Pair | Papers | Node set | Mode set | Node sequence | Mode sequence | Entry node | Entry state | Outcome | Decisive mode |
|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|
| P within | 4 | 0.84 | 0.88 | 0.71 | 0.68 | 1.00 | 1.00 | 1.00 | 0.75 |
| P-PX | 4 | 0.88 | 0.90 | 0.67 | 0.69 | 1.00 | 1.00 | 1.00 | 0.88 |
| P-T | 4 | 0.90 | 0.77 | 0.70 | 0.58 | 1.00 | 1.00 | 0.88 | 0.88 |
| P-X | 4 | 0.85 | 0.83 | 0.62 | 0.58 | 1.00 | 1.00 | 0.88 | 0.88 |
| PX within | 4 | 0.87 | 0.85 | 0.67 | 0.71 | 1.00 | 1.00 | 1.00 | 1.00 |
| PX-T | 4 | 0.90 | 0.80 | 0.61 | 0.57 | 1.00 | 1.00 | 0.88 | 1.00 |
| PX-X | 4 | 0.86 | 0.83 | 0.60 | 0.63 | 1.00 | 1.00 | 0.88 | 1.00 |
| T within | 4 | 0.89 | 0.80 | 0.75 | 0.56 | 1.00 | 1.00 | 0.75 | 1.00 |
| T-X | 4 | 0.89 | 0.85 | 0.67 | 0.61 | 1.00 | 1.00 | 0.88 | 1.00 |
| X within | 4 | 0.86 | 0.93 | 0.60 | 0.66 | 1.00 | 1.00 | 0.75 | 1.00 |

## Fidelity, locations and shape

| Arm | Codings | Quotes | In XML text | In PDF text | Valid locations | Mean steps | Figure-located steps |
|:--|:--|:--|:--|:--|:--|:--|:--|
| X | 12 | 384 | 1.00 | 0.14 | 1.00 | 24.9 | 123 |
| T | 12 | 366 | 0.78 | 0.83 | 0.98 | 23.8 | 5 |
| P | 12 | 366 | 0.76 | 0.34 | 0.99 | 23.5 | 27 |
| PX | 12 | 461 | 0.97 | 0.16 | 0.98 | 26.4 | 80 |
