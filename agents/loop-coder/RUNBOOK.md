# Human workflows against agent loops: runbook for a new set of papers and systems

Reproduces the comparison behind the AI@UW figures `loops_matrix` and `loops_nodes` (slides 05 and 06) on any set of papers and agent systems. How the October 24, 2026 version was actually made, with every prompt and tool call, is in `private/analysis/provenance/README.md`.

Every model step below is a Claude Code subagent (model `claude-opus-5-5` in the 2026 runs) with its prompt written out here. Nothing is coded by a human unless step 5 is done. Run from the repository root. Write everything under `private/`.

## 1. Choose the papers

```bash
python3 tools/select_dois.py ...        # or tools/corpus.py; see agents/coder/RUNBOOK.md, section 1
python3 tools/fetch_pdfs.py add-manifest private/corpus/<name>.jsonl && python3 tools/fetch_pdfs.py run
```

Decide before coding which papers form the human set. Write the list, the selection rule and the date into `private/analysis/<study>/MANIFEST.md`. For process documents (peer-review files, open discussions, preprint versions), record which papers have them.

## 2. Code the papers (human workflow side)

Either the API batch coder (`agents/coder/RUNBOOK.md`; check the licence first), or one subagent per batch of up to five papers with this prompt:

```text
You are the seminar's automated paper coder. Read .claude/agents/paper-coder.md, then agents/coder/CODEBOOK.md
(version <V>) and agents/coder/coding.schema.json, and follow them exactly.
Code these papers, one JSON file each, codebook_version "<V>", coder "claude subagent, codebook <V>, run <DATE>".
| key | DOI | PDF |
| ... | ... | ... |
If a PDF is not the paper named by the DOI, stop for that paper and report it.
Scratch folder for extracted text: <SCRATCH>/coder_<study>/.
Write each coding to private/analysis/<study>/codings/<key>.json and run
`python3 tools/check_coding.py validate <file>` until it reports ok.
Blind: do not open any other coding, and edit no other file.
Final message: a table with key, entry state and node, outcome, number of final_paper steps, the node sequence,
and the codebook gaps you hit.
```

Where a process document exists, add it to the row and say "code a `review` sequence too". All human papers must be coded under one codebook version. `compare_loops.py` warns if they are not.

## 3. Code the agent systems (agent loop side)

One subagent per batch of up to six systems:

```text
You are the seminar's agent-loop coder. Read .claude/agents/agent-loop-coder.md, then agents/loop-coder/CODEBOOK.md
(version <V>), agents/loop-coder/loop.schema.json, and section 3 of agents/coder/CODEBOOK.md, and follow them exactly.
Code these systems, one JSON file each, codebook_version "<V>", coder "claude subagent, loop codebook <V>, run <DATE>".
| key | system | primary sources (DOI, arXiv ID, or URL) |
| ... | ... | ... |
Put downloads only under <SCRATCH>/loops_<study>/ and never execute anything downloaded.
Write each coding to private/analysis/<study>/agent-codings/<key>.json and run
`python3 tools/compare_loops.py validate <file>` until it reports ok.
Blind: do not open private/talks/aiuw-2026/data/agent_loops.csv or any other agent coding. Edit no other file.
Final message: a table with key, full nodes, partial nodes with their surrogates, the loop sequence, the stop rule,
no_conclusion_exit, and the codebook gaps you hit.
```

## 4. Check reliability before comparing

- **Agents:** code every system twice, in two subagents that cannot see each other's output, into `agent-codings-a/` and `agent-codings-b/`. Then run `python3 tools/compare_loops.py agree <a> <b>`. Report observed agreement, Cohen's kappa over all marks, and agreement by node. Resolve disagreements in a third folder and record each resolution.
- **Papers:** code at least a quarter of the papers twice, then run `python3 tools/check_coding.py agree-dir <a> <b>`.
- Agreement between two model coders is not agreement with a person.

## 5. Human coding (needed before any claim leaves the lab)

A person codes the same subset of papers and systems blind, under the same codebooks. Report agreement of model against person with the same commands. The Phase 0 gate in `private/analysis/roadmap-plurality-loops.md` (Krippendorff's alpha of at least 0.67 on categorical fields) applies here too.

## 6. Compare

```bash
python3 tools/compare_loops.py compare \
  --human 'private/analysis/<study>/codings/*.json' \
  --agents private/analysis/<study>/agent-codings-resolved \
  [--review-returns private/analysis/<study>/review_returns.json] \
  --out private/analysis/<study>/compare --figures
```

`compare.json` holds:
- the share of papers using each node, and the share of agents running each node in full and in part;
- the upper medians of distinct nodes per paper and per agent;
- how many agents' node sets and transition sets are subsets of the human record;
- the transitions only agents use, and the count only humans use;
- the codebook versions of the human codings;
- how many agent codings carry evidence for every mark.

## 7. Report

Report every number with its folder and the codebook versions behind it. Also state:
- the reliability figures from step 4 (and step 5, once it is done);
- which systems were read from full text and which only from web extracts.

## Reproducing the October 24, 2026 numbers

The legacy CSV has no evidence fields, so its imported codings do not validate. The numbers still reproduce exactly. Checked on October 25, 2026: every field of `private/talks/aiuw-2026/data/loops_compare.json` matches, and `compare.json` adds four fields plus a `human_only` count.

```bash
python3 tools/compare_loops.py import-csv private/talks/aiuw-2026/data/agent_loops.csv <SCRATCH>/agents
echo '{"V": 29, "R": 24, "H": 17, "D": 11, "C": 10, "S": 8, "O": 8, "I": 7, "X": 4, "N": 4, "P": 2, "E": 1, "F": 1}' > <SCRATCH>/review_returns.json
python3 tools/compare_loops.py compare --human 'private/analysis/codings/reference/*.json' \
  --human 'private/analysis/codings/agent/*_c*.json' --human-review private/analysis/codings/agent/graff2025.json \
  --agents <SCRATCH>/agents --review-returns <SCRATCH>/review_returns.json --out <SCRATCH>/out --figures
```
