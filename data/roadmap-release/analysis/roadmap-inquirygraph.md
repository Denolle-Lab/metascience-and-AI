# Roadmap: `inquirygraph`, a standalone package for encoding scientific inquiry

Drafted October 25, 2026, for Marine Denolle. Prose. Status: proposed.

## What it is

A versioned specification and a Python package for coding how a piece of research proceeds: where it enters the graph of inquiry, which steps the authors took (graph node and mode of inquiry, each with a quote and a page), how it ended, and which step decided it. The same vocabulary codes AI agent loops, so human workflows and agent loops can be compared on one scale.

- **Name:** `inquirygraph` (repository `Denolle-Lab/inquirygraph`, PyPI `inquirygraph`, both free on October 25, 2026). Alternative if the group prefers a shorter name: `scimodes` (also free).
- **Two layers, versioned separately:**
  - **Specification:** the vocabulary (graph v0.4.2 nodes and edges, the 13 modes, the decision tree), the two codebooks (papers; agent loops), and the JSON schemas. Plain files, licensed CC BY 4.0, usable without the code.
  - **Implementation:** a Python package and command-line tool that validates codings, scores agreement, runs model coders, migrates old codings, and aggregates a corpus. Licensed Apache-2.0.

## Trigger: start after the first corpus calculation

Spin-out starts when all of these exist (the "first calculation"):

1. The 525 eligible papers from the screened 600 (2022 preselection) coded once with codebook v1.3 or its successor. Papers held for licence reasons are coded when cleared or listed as held.
2. The 100 gold-set papers coded twice by independent model coders, with test–retest agreement per field from `check_coding.py agree`.
3. A short results note in `private/analysis/` on what the first calculation shows and what broke in the codebook. Codebook problems found at corpus scale go into the first specification release, so the spec does not change twice in the first month.

Human coding of the gold set is not required to start; it is required for the first public release.

## Stage A: private repository (trigger + 2 weeks)

1. **Ask UW CoMotion first.** Before any public licence, file the software disclosure, or ask CoMotion whether an open-source release of UW-developed software needs one. Mention the possible AI2 collaboration. The repository can be created privately while this is pending.
2. **Extract with history.** Use `git filter-repo` on a clone of `metascience-and-AI`, keeping only the paths below, so the record of how the codebook evolved (and why) comes with it:

| From `metascience-and-AI` | To `inquirygraph` |
|:--|:--|
| `agents/coder/` (CODEBOOK.md, coding.schema.json, RUNBOOK.md) | `spec/codebooks/paper/`, `spec/schemas/coding.schema.json` |
| `agents/loop-coder/` | `spec/codebooks/loop/`, `spec/schemas/loop.schema.json` |
| `agents/controller/decision-tree.json` | `spec/vocabulary/decision-tree.json` |
| graph v0.4.2 nodes and edges (now only in `unit.qmd` and the walk builders) | `spec/vocabulary/graph.json` (new; generated once, then the source) |
| the 13 modes (`agents/mode-instructions.json`) | `spec/vocabulary/modes.json` |
| `tools/check_coding.py` | `src/inquirygraph/validate.py`, `agree.py` |
| `tools/aggregate_codings.py` | `src/inquirygraph/aggregate.py` |
| `tools/code_papers.py` | `src/inquirygraph/coders/batch.py` |
| `.claude/agents/paper-coder.md`, `agent-loop-coder.md` | `integrations/claude-code/agents/` |
| letter map v0.4.1 to v0.4.2 (`private/analysis/success-set/LETTERS.md`) | `src/inquirygraph/migrate.py` (codings carry their spec version; old ones migrate forward) |

3. **Package layout and command-line tool:**

```text
inquirygraph/
  spec/            vocabulary/, codebooks/, schemas/, SPEC_VERSION, CHANGELOG.md
  src/inquirygraph/
    validate.py  agree.py  aggregate.py  migrate.py
    coders/      prompt.py (codebook to prompt), providers/ (anthropic, openai-compatible for open-weight models), batch.py, agent.py
    cli.py       inquirygraph validate | agree | code | aggregate | migrate | export
  examples/        codings of CC BY papers only, with their DOIs
  benchmarks/      reliability reports, one per release
  integrations/    claude-code/ (agent definitions), workflows/
  tests/  docs/
  LICENSE (Apache-2.0)  LICENSE-spec (CC BY 4.0)  CITATION.cff  CONTRIBUTING.md  GOVERNANCE.md  CODE_OF_CONDUCT.md
```

4. **Model providers behind an adapter.** Anthropic first, then any OpenAI-compatible endpoint, so open-weight models (for example AI2's OLMo served with vLLM) can run the same codebook. A coding records the provider, model identifier, codebook version and prompt hash.
5. **Tests and CI:** schema validation of every example; agreement-metric unit tests; a round-trip test that migrates old codings forward; prompt snapshots so a codebook edit shows up as a prompt diff.

## Stage B: the seminar becomes a user of the package (trigger + 3 weeks)

- `metascience-and-AI` adds `inquirygraph` as a pinned dependency (a git tag until the first PyPI release) and keeps thin wrappers where scripts are referenced.
- `tools/validate.py` checks that the book's graph figure and decision-tree page match the pinned specification version.
- The roadmap scripts (`tools/roadmap/`) write the package and spec version into every `_provenance` block, so each past result names the codebook it used.
- `agents/coder/` and `agents/loop-coder/` in the seminar repository become pointers to the package; edits to the codebook happen only in `inquirygraph`.

## Stage C: validation as part of each release (trigger + 2 to 3 months)

- **Human agreement:** Phase 0 of the research roadmap. Two people code the 40-paper human gold set; report Krippendorff's alpha per field (entry state, outcome, node set, mode set, decisive move) and model-to-human agreement.
- **Test–retest and cross-model agreement:** the same papers coded twice by the same model, and once by a second model family (an open-weight model), so users see how much a coding depends on the model.
- **Benchmark report per release** (`benchmarks/v0.x.md`): corpus, models, agreement per field, known failure modes. A release without a report is not a release.
- **Public examples:** any coded paper, open-licence or subscription. Codings quote papers in passages of at most 25 words and never reproduce one (PI rule of October 27, 2026); the full texts stay in the private repository.

## Stage D: first public release, v0.x (when Stage C and the CoMotion answer are in)

- Make the repository public under Apache-2.0 (code) and CC BY 4.0 (specification).
- Contributions under the DCO (`Signed-off-by` on each commit); add a CLA only if a partner requires one.
- Publish to PyPI; archive the release on Zenodo for a DOI; `CITATION.cff` points to it.
- Documentation site (GitHub Pages): what the vocabulary is, how to code a paper, how to run a coder, how to propose a change.
- Announce to the seminar, to AI2 contacts, and at a venue where both communities meet (for example an AGU session on AI for science).

## How the specification changes

- **Proposals in writing.** Any change to the vocabulary, a codebook or a schema is an issue using a proposal template: the change, the paper or coding disagreement that forced it, the expected effect on existing codings, and a migration if needed. This continues the seminar's rule that each change cites its source.
- **Who decides:** maintainers listed in `GOVERNANCE.md` (Marine Denolle as lead; others added as they contribute). Decisions are recorded in `spec/CHANGELOG.md` with the proposal number.
- **Version numbers for the specification:**

| Bump | When | Example |
|:--|:--|:--|
| Major | Old codings no longer validate or change meaning | renaming node letters, removing a mode |
| Minor | New optional field, new mode or node that old codings simply do not use | adding question-driven inquiry |
| Patch | Wording and clarification with no change to valid codings | a granularity rule made more precise |

- The package version follows the code; each package release states which specification versions it reads and writes.

## Stage E: v1.0 and beyond

- **v1.0 when:** the vocabulary has gone through one full corpus run without a major change; human agreement meets the thresholds set in Phase 0 (alpha of at least 0.67 on categorical fields, 0.8 on outcome fields); at least one contributor outside the lab has merged a change.
- **Papers:** a software paper (JOSS) at the first public release; a methods paper on the codebook and its reliability once Stage C is complete; later, the research results from the roadmap phases, which cite the package version used.

## Working with AI2

- Keep the repository in Denolle-Lab under lab governance; AI2 contributes through the same proposals and pull requests as anyone else. If a formal collaboration starts, move it to a jointly governed GitHub organization at that point.
- Natural connections: Semantic Scholar API and S2ORC as corpus sources; open-weight models as coders; AI2's agent systems as subjects for the loop codebook.
- Before sharing anything beyond the public release, check what UW CoMotion and any collaboration agreement say about joint development.

## What stays out of the package

- All downloaded data and full texts, the roadmap analysis, gold-set decisions, and codings of subscription papers: these remain in `metascience-private`.
- Seminar pages and meeting material: these remain in `metascience-and-AI`.

## Risks

| Risk | Mitigation |
|:--|:--|
| The codebook keeps changing and old codings break | Codings carry their spec version; migrations ship with the package; major bumps are rare and announced |
| Users treat model codings as ground truth | Benchmark report with error rates in every release; the docs say which fields are reliable |
| Licence or IP problems delay the public release | Ask CoMotion at Stage A, while the repository is still private |
| Dependence on one model provider | Provider adapter; cross-model agreement reported |
| Copyrighted text leaks into public examples | Examples restricted to CC BY papers; a CI check rejects examples whose DOI lacks a CC licence in OpenAlex |
| Seminar and package drift apart | Seminar pins the package; the validator checks the book against the pinned spec |

## Timeline, counted from the trigger (T)

| When | Milestone |
|:--|:--|
| T | First calculation done: 525 papers coded once, 100 gold papers coded twice, results note written |
| T + 2 weeks | CoMotion contacted; private `Denolle-Lab/inquirygraph` with history; CLI and tests passing |
| T + 3 weeks | Seminar depends on the package; roadmap scripts record the package version |
| T + 2 to 3 months | Human gold set coded; first benchmark report |
| After CoMotion answer | Public v0.x: PyPI, Zenodo DOI, docs, JOSS submission |
| After a full corpus run with no major change | v1.0 |

## Decisions for Marine

1. Confirm the name `inquirygraph` (or `scimodes`).
2. Who besides you is a maintainer at the start.
3. Whether the first public release waits for the human gold set (recommended) or goes out earlier as a preview with model-only reliability.
