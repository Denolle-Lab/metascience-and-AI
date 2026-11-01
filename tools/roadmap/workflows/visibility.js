export const meta = {
  name: 'review-visibility',
  description: 'Label how each review-process change shows in the published paper: two independent labelers per paper, adjudication of disagreements',
  phases: [{ title: 'Label', detail: 'two independent labelers per paper' }, { title: 'Adjudicate', detail: 'one adjudicator for steps where the labelers differ' }],
}

const BASE = args.base
const keys = args.keys

const LABEL = {
  type: 'object',
  properties: {
    key: { type: 'string' },
    steps: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          i: { type: 'integer' },
          label: { type: 'string', enum: ['as_revision', 'as_planned', 'absent', 'no_change'] },
          quote: { type: 'string', description: 'Up to 25 words copied exactly from the published text; empty for absent or no_change' },
          locator: { type: 'string', description: 'Section/paragraph locator from the published text, e.g. [§3.2 ¶4]; empty if none' },
          reason: { type: 'string', description: 'One sentence' },
        },
        required: ['i', 'label', 'quote', 'locator', 'reason'],
      },
    },
  },
  required: ['key', 'steps'],
}

const RULES = `Labels, one per review step:
- as_revision: the published paper shows the change AND marks it as a revision or as prompted by review (e.g. "as suggested by a reviewer", "we added in revision", a specific acknowledgement tying this change to a referee). A generic thank-you to reviewers does not count.
- as_planned: the published paper shows the change (the added analysis, test, figure, caveat, rewording, dataset, etc. is there) but presents it as part of the original work, with no sign it came from review.
- absent: the review step describes a change to the work, but the published paper does not contain it.
- no_change: the review step records no change to the work: a declined request, a reply that only argues or clarifies to the referee, or a promise that was not a change to the manuscript.
Steps with move "declined" are usually no_change, but check: authors sometimes decline in the reply and still change the text.
For as_revision and as_planned, give a quote of at most 25 words copied character for character from the published text file (it will be checked by script), and the [§ ¶] locator printed before that paragraph. For absent, say in the reason what you searched for. Do not quote the review record as evidence of the published paper.`

function labelPrompt(key, who) {
  return `You are labeler ${who}, working independently. Paper ${key}.
Files (read them; use grep for searching the published text):
- Packet: ${BASE}/visibility_input/${key}.json : the numbered review steps (what changed during open peer review, coded from the review record), each with node, mode, action, page in the review record, quote and move.
- Published paper text: the "final_text" path in the packet (publisher XML text with [§ ¶] locators).
- Review record: the "review_record" path in the packet (referee comments, author replies, tracked changes), for context only.
For EVERY review step in the packet, decide how it appears in the published paper.
${RULES}
Return one entry per review step, same i numbers, key "${key}".`
}

phase('Label')
const results = await pipeline(
  keys,
  (key) => parallel(['A', 'B'].map(who => () => agent(labelPrompt(key, who), { label: `label ${who}: ${key}`, phase: 'Label', schema: LABEL }))),
  async (pair, key) => {
    const [a, b] = pair
    if (!a || !b) { log(`${key}: a labeler failed; paper skipped`); return null }
    const bi = Object.fromEntries(b.steps.map(s => [s.i, s]))
    const diff = a.steps.filter(s => bi[s.i] && bi[s.i].label !== s.label)
    let adj = {}
    if (diff.length) {
      const items = diff.map(s => `step ${s.i}: labeler A says ${s.label} (${s.reason}${s.quote ? '; quote: ' + s.quote : ''}); labeler B says ${bi[s.i].label} (${bi[s.i].reason}${bi[s.i].quote ? '; quote: ' + bi[s.i].quote : ''})`).join('\n')
      const r = await agent(`You adjudicate disagreements between two labelers for paper ${key}. Packet: ${BASE}/visibility_input/${key}.json (published text and review record paths inside).
${RULES}
Disagreements:
${items}
Re-read the review step and search the published text yourself. Decide each one; return only these steps (i numbers ${diff.map(s => s.i).join(', ')}), key "${key}".`, { label: `adjudicate: ${key}`, phase: 'Adjudicate', schema: LABEL })
      if (r) adj = Object.fromEntries(r.steps.map(s => [s.i, s]))
    }
    const steps = a.steps.filter(s => bi[s.i]).map(s => {
      const t = bi[s.i]
      if (t.label === s.label) {
        const pick = s.quote ? s : t
        return { i: s.i, label: s.label, agreed: true, quote: pick.quote, locator: pick.locator, reason: s.reason, label_a: s.label, label_b: t.label }
      }
      const d = adj[s.i]
      return d ? { i: s.i, label: d.label, agreed: false, quote: d.quote, locator: d.locator, reason: d.reason, label_a: s.label, label_b: t.label } : null
    }).filter(Boolean)
    return { key, steps, labeled_a: a.steps.length, labeled_b: b.steps.length, disagreements: diff.length }
  },
)
const out = results.filter(Boolean)
log(`${out.length} of ${keys.length} papers labeled`)
return { data: out }
