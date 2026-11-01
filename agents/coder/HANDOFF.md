# Rerunning the paper-coding protocol with another model

For colleagues who want to code papers with the same protocol, for example with an open-weight OLMo model, and
compare with the lab's Claude codings. Written October 27, 2026, for paper codebook 1.5.0.

## What the protocol is

- **Codebook** `agents/coder/CODEBOOK.md` and **definitions** `definitions.json`: how to turn a paper into a walk on
  the graph of inquiry (entry, steps with node, mode, action, location, quote, move; tree answers; outcome; decisive
  move; checks).
- **Schema** `coding.schema.json`: the JSON a coding must match.
- **Validator** `tools/check_coding.py validate <file>`: schema plus rules (quotes at most 25 words, locators, node
  and mode vocabularies). **Agreement** `tools/check_coding.py agree <a> <b>`: entry, outcome, decisive mode, node
  and mode sets and sequences.
- **Prompt**: the system prompt is the codebook plus the schema, with a short instruction; the user message is the
  paper's located text plus one instruction line. `tools/code_papers_open.py export` writes both exactly.

## Steps

1. **Set up.** `conda env create -f environment.yml`, `conda activate metascience`. Keys, if any, go in
   `~/.config/metascience/keys.env` (see the README).
2. **Choose papers.** A manifest is a JSON-lines file with at least `key` and `doi` per line. Round 1 and round 2
   manifests are produced by `tools/roadmap/g12_calc1_manifest.py` (see `tools/roadmap/README.md`).
3. **Get full text.** `python tools/fetch_pdfs.py add-manifest <manifest>` then `run` (open-access routes, plus
   publisher text-and-data-mining routes where your institution has access). `python tools/roadmap/g10_fetch_xml.py
   --manifest <manifest>` adds publisher XML and its located text (`<key>.xml.txt`, every paragraph with a
   section-and-paragraph locator).
4. **Export the exact inputs.**
   `python tools/code_papers_open.py export --manifest <manifest> --pdf-text --out <folder>`
   writes `system.txt`, `papers/<key>.user.txt`, `requests.jsonl` (one OpenAI-style chat request per paper) and
   `inputs.json` (sha256 of every text, its source, XML or pdftotext). Papers longer than 200,000 characters are
   skipped and listed. Only share the folder for papers whose licence allows it.
5. **Run a model.** Serve it behind an OpenAI-compatible endpoint (for example `vllm serve <model>`), then
   `OPEN_LLM_BASE_URL=http://localhost:8000/v1 OPEN_LLM_MODEL=<model> python tools/code_papers_open.py run --manifest <manifest> --pdf-text --tag <tag>`.
   Codings go to `private/analysis/codings/open/<tag>/`, with `run.json` recording model, endpoint, prompt hash,
   per-paper status, tokens and time. Rerunning the command retries only papers not yet valid.
6. **Compare.** For each paper coded by both: `python tools/check_coding.py agree <claude file> <open file>`.
   The lab's Claude baseline (two independent Claude runs, 50 papers): node-set overlap 0.86, entry state 92%,
   outcome 100%.

## Sizes to plan for

- Text input per paper: median about 67,000 characters (round 1, XML or PDF text), 90th percentile 123,000, cap
  200,000. System prompt: 29,600 characters. Roughly, median input about 25,000 tokens.
- Output: Claude used a median of 16,400 tokens per coding including reasoning. The JSON itself is smaller.
- The hard parts for a model: valid nested JSON, and quotes copied exactly (at most 25 words) with correct locators.
  Constrained decoding against the schema helps the first; the validator checks the second.

## What is not shared

Paper texts, abstracts and open-review texts are not redistributed: the codings quote papers (25 words at most), they
do not republish them. Codings with quotes, derived tables and figure provenance are public in the data release,
[`data/roadmap-release/`](https://github.com/Denolle-Lab/metascience-and-AI/tree/framework-v0.5/data/roadmap-release), built by `tools/roadmap/g22_release.py`. Per-paper records of the papers in human
coding are held back until that coding is done. The registry of every experiment, with inputs, commands, commits and
costs, is `data/roadmap/EXPERIMENTS.md` in the release (`private/data/roadmap/EXPERIMENTS.md` in the lab repository).

## Frozen hand-off packages (October 28, 2026)

`tools/roadmap/g33_handoff.py` freezes, per task, the fixed paper set and what the model reads, so an open-weight
model reruns exactly the task Claude ran. Each package is `private/data/roadmap/handoff/<task>/` (private: it holds
paper text): `system.txt`, `user/<key>.user.txt` (written with `coder = "<model>"`), `papers.jsonl` (keys, DOIs,
sha256 of every input text, Claude's content blocks), `claude_outputs.jsonl` (each Claude coding: file sha256, batch,
cost, drift checks), `handoff.json` (versions, instrument file hashes and commits, request settings, exclusions) and
`SHA256SUMS`. The public record of versions and hashes is `preregistration/handoff-manifest.json`. A frozen package
is never overwritten; `freeze --refreeze` moves it to `handoff/_superseded/` first.

| Task | Status | Papers | Rerun | Compare |
|:--|:--|--:|:--|:--|
| inquiry | frozen October 28 | 581 | `code_papers_open.py run --manifest private/data/roadmap/handoff/inquiry/papers.jsonl --pdf-text --tag <tag>`, then `g33_handoff.py verify --task inquiry --open-tag <tag>` | `check_coding.py agree-dir private/analysis/codings/api/calc1 private/analysis/codings/open/<tag>` (and `r2`); Claude retest baseline `gold-r2` |
| review | not frozen: freeze it after the cop22 full texts and review records are on disk and before the review-v2 batches (rounds 1, 2 and cop22, review addendum 1.0.0, max_tokens 48,000) | 97 at the October 28 dry run (cop22 full texts not yet on disk) | after freezing: `code_papers_open.py run --manifest private/data/roadmap/handoff/review/papers.jsonl --review-dir private/data/roadmap/review --tag <tag>`, or `g33_handoff.py requests --task review` | `check_coding.py agree-dir` on the review sequences; disclosures with `g30_disclosure_agreement.py --codings private/analysis/codings/open/<tag>`; the reconstruction features with `g34_reconstruction.py features --set NAME=<inquiry>,<tag>,plan,open` |
| inquiry-cop22 | not frozen: freeze it once the cop22 full texts are on disk, before the cop22 inquiry batch | 0 at the dry run (no cop22 full text yet) | as inquiry, with `handoff/inquiry-cop22/papers.jsonl` | `check_coding.py agree-dir private/analysis/codings/api/cop22 private/analysis/codings/open/<tag>` |
| advance | not frozen (waits for pilot 2 and the g24 plan) | 572 at the dry run | `g33_handoff.py requests --task advance --model <m> --out <file>`, sent with any OpenAI batch runner (vLLM `run_batch`) | `g24_advance.py pilot --tags <claude tag>,<open tag>` (test-retest block) |

- `verify` recomputes every input from its source and compares hashes. Use it before a rerun: the pdftotext route
  depends on the poppler version, so a different machine can change the text of the 260 PDF-route papers.
- The open model reads text only. Claude also read the PDF page images, and for 16 inquiry papers Claude read the
  PDF alone, because their Elsevier XML was fetched after the batch (`xml_for_open_model_not_for_claude` in
  `handoff.json`). Compare those 16 apart.
- `code_papers_open.py` skips papers over 200,000 characters (4 inquiry papers). By the estimate of 2.7 characters
  per token, 20 inquiry inputs exceed 65,536 tokens before output, so check the model's context window first.
- Advance pilot papers (20, `derived/advance/pilot_keys.json`) carry `confirmatory_exclude` in `papers.jsonl`.
  Leave them out of any confirmatory comparison.
