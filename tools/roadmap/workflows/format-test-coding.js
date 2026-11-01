export const meta = {
  name: 'format-test-coding',
  description: 'Code six papers twice from publisher XML text and twice from PDF text (24 independent codings, codebook 1.4.0)',
  phases: [{ title: 'Code', detail: '24 independent paper-coder runs, one input file each' }],
}
const REPO = '/Users/marinedenolle/GitHub/metascience-and-AI'
const FT = REPO + '/private/data/roadmap/derived/format_test'
const ARMS = { X: { file: 'xml.txt', desc: 'the publisher full text converted from XML, with a locator at the start of every paragraph ([§3.2 ¶4], [§0 ¶1] for the abstract, [Figure 3] for captions). Cite these locators in every page field and set pages_convention to "XML section and paragraph locators (jats_text)". There is no PDF in this arm: for a step read off a figure, cite the figure caption locator.' },
                T: { file: 'pdf.txt', desc: 'the text extracted from the PDF with pdftotext -layout; pages are separated by form-feed characters (\\f). Count pages from 1 and cite PDF page numbers; set pages_convention to "PDF pages counted from 1".' } }
const jobs = []
for (const k of args.papers) for (const arm of ['X', 'T']) for (const rep of [1, 2]) jobs.push({ k, arm, rep })

const SUM = { type: 'object', properties: { file: { type: 'string' }, valid: { type: 'boolean' }, steps: { type: 'integer' }, entry: { type: 'string' }, outcome: { type: 'string' }, codebook_gaps: { type: 'string' } }, required: ['file', 'valid', 'steps', 'entry', 'outcome', 'codebook_gaps'] }

const results = await parallel(jobs.map(j => () => agent(
`Code one paper under the codebook (${REPO}/agents/coder/CODEBOOK.md, version 1.4.0) and its schema (${REPO}/agents/coder/coding.schema.json). Read both in full first.

Your ONLY source for the paper is ${FT}/inputs/${j.k}.${ARMS[j.arm].file}: ${ARMS[j.arm].desc}
Do not open any other version of the paper (no PDF, no other file in ${FT}/inputs/), do not open ${FT}/codings/ or any other coding anywhere, and do not search the web. This is a blind test of how the input format changes a coding; independence matters.

Write the coding to ${FT}/codings/${j.k}.${j.arm}${j.rep}.json with key "${j.k}", codebook_version "1.4.0", coder "claude paper-coder, format test arm ${j.arm} replicate ${j.rep}", and documents ["${j.arm === 'X' ? 'publisher XML text' : 'PDF text (pdftotext)'}"]. Look up the DOI inside the source text. Copy every quote exactly from the source (at most 25 words).
Then run: python3 ${REPO}/tools/check_coding.py validate ${FT}/codings/${j.k}.${j.arm}${j.rep}.json and fix every problem until it reports ok. Edit no other file.`,
  { label: `${j.k.slice(-6)} ${j.arm}${j.rep}`, phase: 'Code', agentType: 'paper-coder', schema: SUM })))
const ok = results.filter(r => r && r.valid).length
log(`${ok} of ${jobs.length} codings valid`)
return { jobs, results }
