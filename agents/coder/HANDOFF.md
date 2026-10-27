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

Papers, review records and codings that quote them stay in the lab's private repository unless the paper's licence
allows sharing. Results are reported on the seminar site. The registry of every experiment, with inputs, commands,
commits and costs, is `private/data/roadmap/EXPERIMENTS.md` in the lab repository.
