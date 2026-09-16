# Plan: rebuild the meeting 1 reading notes from the cognitive tasks up

September 15, 2026. A plan, not an edit. Nothing below has been applied.

## Verdict

The current notes start in the middle. They open with Platt's loop and assume the reader already knows what deduction, induction, a hypothesis, and a test are. The convenor's diagnosis is right: the notes need a bottom-up build, from the three cognitive tasks, through the unit of hypothesis testing, to the thinkers who defined each step, and only then to a graph on which Platt's "strong" and Cleland's objections can be pointed at.

Recommendation: move the foundations out of the session page into one new public page, "The unit of inquiry," placed right after the glossary, because every mode page uses the verbs it defines (test, confirm, exclude, corroborate). The session page keeps a short "where the two papers sit on the graph" section and the existing Platt diagram as a second figure. Sixteen readings are needed, all verified on Crossref today; none is assigned, all are optional.

## The five layers, in teaching order

### Layer 0. Three cognitive tasks

One table, four columns: task, form, what it guarantees, geoscience example. Peirce's syllogistic framing makes the three symmetric and memorable.

| Task | Form (Peirce, 1878) | Guarantees | Geoscience example |
|:--|:--|:--|:--|
| Deduction | Rule + case, therefore result | Result is certain if the premises are true; adds no new content | If ridge-ridge transforms exist (rule) and this offset is one (case), then first motions on the offset segment are opposite to the ridge-offset sense (result) |
| Induction | Case + result, therefore rule | Rule is probable, never certain; the next case can break it | Twenty catalogs (cases) each give b near 1 (results), therefore b near 1 in general (rule) |
| Abduction | Rule + result, therefore case | Case is the best available explanation, and only that | Peat-mud couplets with sand sheets (result) and what subduction earthquakes do to coasts (rule), therefore a great earthquake (case) |

Two lines after the table: deduction is truth-preserving and content-free; induction and abduction add content and can be wrong. Aristotle named the first two; Peirce named the third (Peirce, 1878; Hanson, 1958, for its role in discovery).

### Layer 1. Inference, hypothesis, prediction, explanation

- Inference: any reasoned move from premises or evidence to a conclusion; the umbrella term (Okasha, 2016, chapter 2, as the one-hour introduction).
- Hypothesis: a candidate claim, not yet established, with consequences that could be checked. Glass (2008), already in the bibliography, for how the word came to mean this. Chamberlin (1890, reprinted 1965) for the working hypothesis against the ruling theory. Gilbert (1886, 1896) for where a geological hypothesis comes from: analogy, then enumeration.
- Prediction versus explanation: a prediction is a consequence derived before the observation; an explanation is a hypothesis fitted to an observation already in hand. Musgrave (1974) and Douglas and Magnus (2013) for why the order matters.

### Layer 2. The unit: one pass through the hypothetico-deductive schema

$$H + A + C \Rightarrow E$$

Define each symbol on its own line: H the hypothesis; A the auxiliary assumptions (instrument theory, background laws, the dating method); C the conditions (what the system was in, set by the investigator or found in nature); E the expected observation. Then the verbs, defined on the schema:

| Verb | On the schema | Who fixed the meaning |
|:--|:--|:--|
| Test | Arrange or find C, derive E, observe | Hempel (1945) |
| Confirm | Observe E; the conjunction survives; strength depends on how unlikely E was without H | Hempel (1945); the Bayesian form P(E given H) over P(E) |
| Corroborate | Survive a test that could have failed, without calling that confirmation | Popper (1959) |
| Falsify | Observe not-E; therefore not-(H + A + C); logic does not say which conjunct to drop | Popper (1959); Duhem (1954); Quine (1951) |
| Exclude | Falsify one member of a stated set of rivals | Platt (1964), after Bacon (1620) |
| Infer to the best explanation | Retain the H that makes E least surprising among the rivals; not an exclusion | Harman (1965); Lipton (2004) |
| Severely test | A test the H would probably have failed if false | Mayo (1996); Mayo and Spanos (2006) |

The Bayesian line closes the layer: P(H given E) is proportional to P(E given H) times P(H). Cleland's last sentence says her differences could be rewritten this way (Cleland, 2002, p. 495); Tarantola (2006), already in the bibliography, is the geophysicist's version.

### Layer 3. The thinkers, and which node each owns

A timeline table, one line each, with the node of the Layer 4 graph the thinker's contribution attaches to.

| Year | Thinker | Contribution | Node |
|:--|:--|:--|:--|
| 1620 | Bacon | Eliminative induction; the instance of the fingerpost that decides between roads | Design, Exclude |
| 1840 | Whewell | Hypotheses come first; consilience when independent classes of facts agree | Generate, Retain |
| 1843 | Mill | Methods of agreement and difference: what controlling C means | Conditions |
| 1878 | Peirce | Abduction as the third task | Generate |
| 1886 | Gilbert | Hypotheses by analogy, in geology | Generate |
| 1890 | Chamberlin | Hold a family of hypotheses at once | Generate |
| 1906 | Duhem | No crucial experiment in physics; refutation hits the conjunction | Exclude, Protect |
| 1934 | Popper | Falsification; the asymmetry between refuting and confirming | Exclude |
| 1945 | Hempel | The logic of confirmation and its paradoxes | Retain |
| 1951 | Quine | Duhem's holism generalized to all belief | Protect |
| 1958 | Hanson | Discovery has a logic; observation is theory-laden | Generate, Observe |
| 1964 | Platt | Strong inference | The loop |
| 1965 | Harman | Inference to the best explanation named | Retain |
| 1970 | Lakatos | Protective belt; research programmes | Protect |
| 1996 | Mayo | Severity as the measure of a test | Design |
| 2001 | Cleland | Historical versus experimental: the asymmetry of overdetermination | Conditions, Retain |

### Layer 4. The graph: one unit as a workflow

Nine nodes. Every thinker above sits on one; both papers are overlays on it.

```
flowchart TD
    Q["Question or anomaly"] --> G["Generate H1..Hn<br/>(abduction; Peirce, Gilbert, Chamberlin)"]
    G --> D["Derive E_i from H_i + A + C<br/>(deduction; Hempel)"]
    D --> DS["Design: pick the C and the observable<br/>where the E_i differ<br/>(Bacon's fingerpost; Mill; Mayo)"]
    DS --> C["Set or find the conditions C<br/>(set: experiment; found: trace)"]
    C --> O["Observe<br/>(theory-laden; Hanson)"]
    O --> M{"Match E_i?"}
    M -- "not E_i" --> X["Exclude H_i<br/>(Popper; Platt)"]
    M -- "E_i" --> K["Retain H_i: confirm, corroborate,<br/>or best explanation<br/>(Hempel; Popper; Harman)"]
    X --> P["Or protect H_i: revise A or C instead<br/>(Duhem; Quine; Lakatos)"]
    P --> D
    X --> R["Refine the survivors<br/>into subhypotheses"]
    K --> R
    R --> G
```

Two overlays, drawn as coloured node sets on the same graph on the page:

- **Platt's strong inference** is the path Q, G with n greater than 1, D, DS with a crucial experiment, C set, O, M, X, R, and back. What makes it strong is one property of the DS node: every outcome at M excludes at least one H. The tree branches and prunes at each pass. It is Bacon's eliminative induction with Chamberlin's family at G and Popper's asymmetry at X. Platt supplies nothing at G beyond "invent" and hands the reader to Pólya (Platt, 1964, p. 347).
- **Cleland's objections** land on four nodes. At C: in historical science C is found, not set, so Mill's methods of difference are unavailable. At X: refutation hits the conjunction, and in practice A or C goes first; Neptune (Cleland, 2001, p. 988). At K: the smoking gun is a retention move, inference to the best explanation, not an exclusion; it need not touch the rivals (Cleland, 2002, pp. 482-483). Before G: an exploratory phase in which the phenomenon is not yet stable and no H is worth deriving from; Cech, Viking (Cleland, 2002, pp. 479-480, 486). Her positive claim, the asymmetry of overdetermination, is why the found-C path works at all: a past event leaves many traces, so O can be repeated on new traces without control.

### Layer 5. What "strong" means, and what its critics say

- Strong means: exclusion, not confirmation, is the unit of progress; the method's speed comes from pruning.
- Davis (2006) asks whether strong inference was ever a description of practice or a rallying cry; Fudge (2014), fifty years on, finds the paper still cited as an ideal and rarely as a method followed. Both belong beside Platt, not against him.
- The seminar's question then becomes precise: which of the nine nodes does each of the ten modes actually exercise, and which does an agent own. That is the hand-off to the glossary and to meeting 2.

## Where the text goes

| Piece | Location | Length | Status rule |
|:--|:--|:--|:--|
| Layers 0 to 5 | New page `unit.qmd`, "The unit of inquiry", second chapter after `glossary.qmd` | Under 900 words plus three tables, one formula block, one graph | Bullet level with tables, as the public book requires; prose in `private/text/unit.md` |
| Overlays and the Platt diagram | `sessions/01-scientific-method.qmd`, section "Where the two papers sit on the unit graph", replacing the restored reading notes | Under 350 words; the current mermaid figure kept as Figure 2 with a one-line caption change: "Platt's loop as one path through the unit graph" | Drafted |
| Inference table | Moves from the session page to `unit.qmd` Layer 0, gaining an abduction row | | |
| Verbs | Linked from `modes/hypothesis.qmd`, whose "characteristic failure" bullet (an auxiliary absorbs every failure) cites Duhem and Quine | One line | |
| Glossary | One bullet under "How to use a mode": "The verbs test, confirm, exclude, and corroborate are defined on the unit page" | One line | |

## The meeting, if the notes change

The case exercise gains one step before the current one: each participant places one recent paper of their own on the nine-node graph and marks which nodes the paper performed, which it skipped, and where C was set or found. Ten minutes. The rest of the hour stands. Discussion question 3 ("how ideas are generated or how claims are warranted") becomes answerable by pointing: G versus K.

## Readings to add

Sixteen records, none assigned. Every DOI below was verified on Crossref on September 15, 2026; Hanson has no DOI. Open-access status from OpenAlex was not checked for these; most are books or paywalled journals and will need reading copies.

| Key | Reference | Use |
|:--|:--|:--|
| `bacon2004` (was `bacon1620` in this plan) | Bacon, F. (2004). *Novum organum* (G. Rees & M. Wakely, Eds.). In *The Oxford Francis Bacon, Vol. 11*. Oxford University Press. https://doi.org/10.1093/oseo/instance.00007242 (Original work published 1620) | Layer 3; Platt's own source |
| `whewell2014` | Whewell, W. (2014). *The philosophy of the inductive sciences, founded upon their history*. Cambridge University Press. https://doi.org/10.1017/CBO9781139644662 (Original work published 1840) | Layer 3 |
| `mill2011` | Mill, J. S. (2011). *A system of logic, ratiocinative and inductive*. Cambridge University Press. https://doi.org/10.1017/CBO9781139149839 (Original work published 1843) | Layer 3; the C node |
| `peirce1992` | Peirce, C. S. (1992). Deduction, induction, and hypothesis. In N. Houser & C. Kloesel (Eds.), *The essential Peirce, Vol. 1* (pp. 186–199). Indiana University Press. https://doi.org/10.2307/j.ctvpwhg1z.17 (Original work published 1878) | Layer 0 |
| `gilbert1886` | Gilbert, G. K. (1886). The inculcation of scientific method by example, with an illustration drawn from the Quaternary geology of Utah. *American Journal of Science*, *s3-31*(184), 284–299. https://doi.org/10.2475/ajs.s3-31.184.284 | Layer 1; pairs with `gilbert1896` already in the bibliography |
| `duhem1954` | Duhem, P. (1954). *The aim and structure of physical theory* (P. P. Wiener, Trans.). Princeton University Press. https://doi.org/10.1515/9780691233857 (Original work published 1906) | Layer 2; the X and P nodes |
| `popper2005` | Popper, K. R. (2005). *The logic of scientific discovery*. Routledge. https://doi.org/10.4324/9780203994627 (Original work published 1934; English 1959) | Layer 2 |
| `hempel1945` | Hempel, C. G. (1945). Studies in the logic of confirmation (I.). *Mind*, *54*(213), 1–26. https://doi.org/10.1093/mind/LIV.213.1 | Layer 2; the K node |
| `quine1951` | Quine, W. V. (1951). Two dogmas of empiricism. *The Philosophical Review*, *60*(1), 20–43. https://doi.org/10.2307/2181906 | Layer 2; the P node |
| `hanson1958` | Hanson, N. R. (1958). *Patterns of discovery: An inquiry into the conceptual foundations of science*. Cambridge University Press. No DOI. | Layer 0 and 3 |
| `harman1965` | Harman, G. H. (1965). The inference to the best explanation. *The Philosophical Review*, *74*(1), 88–95. https://doi.org/10.2307/2183532 | Layer 2; Cleland's smoking gun |
| `musgrave1974` | Musgrave, A. (1974). Logical versus historical theories of confirmation. *The British Journal for the Philosophy of Science*, *25*(1), 1–23. https://doi.org/10.1093/bjps/25.1.1 | Layer 1; prediction versus accommodation |
| `mayo1996` | Mayo, D. G. (1996). *Error and the growth of experimental knowledge*. University of Chicago Press. https://doi.org/10.7208/chicago/9780226511993.001.0001 | Layer 2; severity |
| `mayo2006` | Mayo, D. G., & Spanos, A. (2006). Severe testing as a basic concept in a Neyman–Pearson philosophy of induction. *The British Journal for the Philosophy of Science*, *57*(2), 323–357. https://doi.org/10.1093/bjps/axl003 | Layer 2; the article-length version |
| `lipton2004` | Lipton, P. (2004). *Inference to the best explanation* (2nd ed.). Routledge. https://doi.org/10.4324/9780203470855 | Layer 2 |
| `davis2006` | Davis, R. H. (2006). Strong inference: Rationale or inspiration? *Perspectives in Biology and Medicine*, *49*(2), 238–250. https://doi.org/10.1353/pbm.2006.0022 | Layer 5 |
| `fudge2014` | Fudge, D. S. (2014). Fifty years of J. R. Platt's strong inference. *Journal of Experimental Biology*, *217*(8), 1202–1204. https://doi.org/10.1242/jeb.104976 | Layer 5 |
| `douglas2013` | Douglas, H., & Magnus, P. D. (2013). State of the field: Why novel prediction matters. *Studies in History and Philosophy of Science Part A*, *44*(4), 580–589. https://doi.org/10.1016/j.shpsa.2013.04.001 | Layer 1 |
| `okasha2016` | Okasha, S. (2016). Scientific inference. In *Philosophy of science: A very short introduction* (2nd ed., chap. 2). Oxford University Press. https://doi.org/10.1093/actrade/9780198745587.003.0002 | The one-hour introduction for anyone new to all of this |

Already in the bibliography and reused: `platt1964`, `cleland2001`, `cleland2002`, `chamberlin1965`, `gilbert1896`, `glass2008`, `tarantola2006`, `simon1973`, `klahr1988`, `holmes1987`. Lakatos (1970) and Hacking (1983) are in the private bibliography and can be promoted.

## Order of work

| Step | Files | Check |
|:--|:--|:--|
| 1 | Add the 19 records to `references.bib` and `curriculum.json` as optional readings of meeting 1; regenerate `bibliography.qmd` | `tools/validate.py`; `tools/check_links.py` on the new DOIs |
| 2 | Write `unit.qmd`; add it to `_quarto.yml` after `glossary.qmd`; write `private/text/unit.md` | `quarto render unit.qmd`; the graph renders in both themes |
| 3 | Replace the session page's reading notes with the overlay section; keep the Platt figure as Figure 2 | Render; the two mermaid figures render; cross-links resolve |
| 4 | One-line links from `glossary.qmd` and `modes/hypothesis.qmd` | Validate |
| 5 | Add the placing step to the case exercise if adopted | |
| 6 | `private/bibliography.md` entries for the 19 records; `VALIDATION.md` | |

One commit for step 1, one for steps 2 to 5, one for step 6.

## Decisions for the convenor

1. A separate `unit.qmd` page, or everything inside the session page.
2. The placing step added to the case exercise.
3. Okasha as a recommended pre-read for the group, or left optional.
