export const meta = {
  name: 'review-gold-coder-app',
  description: 'Review the offline gold-set coding app from five independent lenses, then verify each finding by code reading and by reproduction',
  phases: [
    { title: 'Review', detail: 'five lenses: schema conformance, coder usability, data safety and blinding, JS correctness, agreement parity' },
    { title: 'Verify', detail: 'each finding checked by a code reader and a reproducer' },
  ],
}

const REPO = '/Users/marinedenolle/GitHub/metascience-and-AI'
const SCR = args.scratch
const CONTEXT = `You are reviewing an offline, single-file HTML app that four Earth scientists will use to code research papers for a human "gold set" (inter-coder reliability study).
Files (read them; do NOT edit anything under ${REPO}):
- Template (the source of truth): ${REPO}/tools/roadmap/app/gold_coder.html
- Built app with data embedded: ${REPO}/private/data/roadmap/app/gold-coder.html (open from disk; data in <script id="payload">)
- Build script: ${REPO}/tools/roadmap/g09_human_coding_app.py
- Coding schema: ${REPO}/agents/coder/coding.schema.json ; ratings schema: ${REPO}/agents/coder/ratings.schema.json
- Codebook the coders follow: ${REPO}/agents/coder/CODEBOOK.md
- Python validator and agreement metric of record: ${REPO}/tools/check_coding.py
- End-to-end browser test: ${REPO}/tools/roadmap/app/e2e_test.js (puppeteer-core is installed in ${SCR}/node_modules; run node scripts from ${SCR}; Chrome is at /Applications/Google Chrome.app). Write any test scripts or outputs ONLY under ${SCR}/review/.
Each paper is coded independently by two coders; files are saved as <key>.<initials>.coding.json and <key>.<initials>.ratings.json and committed to a private git repo; the Python pipeline computes agreement later.`

const FINDINGS = {
  type: 'object',
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          title: { type: 'string' },
          severity: { type: 'string', enum: ['blocker', 'major', 'minor'] },
          location: { type: 'string', description: 'file and line or function' },
          evidence: { type: 'string', description: 'what in the code or behaviour shows it' },
          scenario: { type: 'string', description: 'concrete steps or input that trigger the problem and its consequence' },
          fix: { type: 'string' },
        },
        required: ['title', 'severity', 'location', 'evidence', 'scenario', 'fix'],
      },
    },
  },
  required: ['findings'],
}
const VERDICT = {
  type: 'object',
  properties: {
    real: { type: 'boolean' },
    severity: { type: 'string', enum: ['blocker', 'major', 'minor', 'not_a_problem'] },
    reasoning: { type: 'string' },
    reproduction: { type: 'string', description: 'what you ran or read and what it showed' },
  },
  required: ['real', 'severity', 'reasoning', 'reproduction'],
}

const LENSES = [
  { key: 'schema', prompt: 'LENS: schema and codebook conformance. Can a coder produce EVERY valid coding the schema and codebook allow (all enum values, review sequences, tree question 6b, disagreements, alternatives, empty quotes, supplement pages like S3)? Does anything the app writes violate the schemas (types, required keys, additionalProperties, minimum/maximum)? Do the app\'s own checks contradict the codebook (false errors or missing errors), e.g. the repeat rule, the granularity warning, quotes at most 25 words, every claim has a page?' },
  { key: 'usability', prompt: 'LENS: usability for a real coding session of 45 to 60 minutes per paper by an Earth scientist new to the codebook. Walk through the full task: pick identity, find the paper and PDF, code 15 to 30 steps, reorder steps, add a review sequence, answer the tree, rate, save. Where will they get stuck, lose time, make systematic errors, or misunderstand an instruction? Check keyboard use, focus loss after re-render, scrolling position after adding a step, readability, the phone/narrow layout. Prefer findings that would change coding quality or agreement.' },
  { key: 'safety', prompt: 'LENS: data safety and blinding. Find every way work can be lost or corrupted (localStorage blocked or full, two tabs open on the same paper, reload mid-typing with the 250 ms debounce, importing the wrong file, restoring a backup over newer drafts, switching coder, saving to folder vs download, overwriting a saved file) and every way a coder could see the other coder\'s work or the metrics they must rate blind (embedded payload content, coordinator view, shared computer). Also check that nothing is sent over the network.' },
  { key: 'js', prompt: 'LENS: JavaScript correctness. Read the code for bugs: state that goes stale after renderForm, event handlers bound to removed elements, wrong indices after delete/move, D being null, renumbering, the custom JSON-schema validator (does it handle every construct used in the two schemas?), HTML escaping and injection from paper titles or user text, the coordinator CSV quoting, theme toggle. Run the e2e test (node ${REPO}/tools/roadmap/app/e2e_test.js with OUT=${SCR}/review/e2e) and write extra puppeteer tests under ${SCR}/review/ for edge cases you suspect.' },
  { key: 'agreement', prompt: 'LENS: agreement-metric parity. The coordinator view reimplements tools/check_coding.py agree() in JavaScript. Compare them line by line (runs merging, Jaccard, edit distance, sequence similarity, which sequence is used, boolean fields). Test parity numerically: use real codings in ' + REPO + '/private/analysis/codings/agent/ and ' + REPO + '/private/analysis/codings/reference/ (pairs with the same key in both folders), compute agree() with python3 tools/check_coding.py agree A B (check its CLI) and the JS version (extract the functions into a node script under ' + SCR + '/review/). Report any difference. Also check that the coordinator pairs files correctly when a coder saved twice or when three codings of one paper are loaded.' },
]

const results = await pipeline(
  LENSES,
  L => agent(`${CONTEXT}\n\n${L.prompt}\n\nReport only real, specific problems with evidence; do not pad. Severity: blocker = produces invalid or lost data or breaks blinding; major = likely to change coding quality or waste substantial time; minor = polish.`, { label: `review:${L.key}`, phase: 'Review', schema: FINDINGS }),
  (rev, L) => parallel(((rev && rev.findings) || []).map((f, i) => () => parallel([
    () => agent(`${CONTEXT}\n\nA reviewer reported this problem with the app. Try to REFUTE it by reading the code carefully; default to real=false if the code does not actually behave as claimed.\n${JSON.stringify(f)}`, { label: `verify-read:${L.key}:${i}`, phase: 'Verify', schema: VERDICT }),
    () => agent(`${CONTEXT}\n\nA reviewer reported this problem with the app. Try to REPRODUCE it by running the built app in headless Chrome with a puppeteer script you write under ${SCR}/review/ (or by running the Python/JS code involved). Report real=true only if you observed it.\n${JSON.stringify(f)}`, { label: `verify-run:${L.key}:${i}`, phase: 'Verify', schema: VERDICT }),
  ]).then(vs => ({ lens: L.key, finding: f, verdicts: vs.filter(Boolean) })))),
)

const all = results.filter(Boolean).flat().filter(Boolean)
const confirmed = all.filter(x => x.verdicts.some(v => v.real) && x.verdicts.filter(v => v.real).length >= 1 && !(x.verdicts.length === 2 && x.verdicts.every(v => !v.real)))
log(`${all.length} findings; ${confirmed.length} confirmed by at least one verifier`)
return { all }
