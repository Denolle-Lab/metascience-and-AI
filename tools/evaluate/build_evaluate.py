"""Build the public evaluation page, evaluate/index.html, from the repository's own vocabulary.

The page lets anyone open a paper (DOI lookup, or a local PDF that never leaves the browser)
and record its modes of inquiry, its walk, and its answers to the decision tree, then download
the answers as JSON. Everything it asks is generated here from:

  modes/*.qmd                        the 13 modes (title, epistemic purpose)
  unit.qmd                           graph v0.4.2 node table (letter, verb)
  agents/controller/decision-tree.json   the controller questions and branches
  agents/coder/coding.schema.json    entry states, outcomes, claim statuses (same categories as the model coder)

Run:   python tools/evaluate/build_evaluate.py           (writes evaluate/index.html)
       python tools/evaluate/build_evaluate.py --check   (exit 1 if the page is out of date)
"""
import json, re, sys, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = Path(__file__).with_name("template.html")
OUT = ROOT / "evaluate" / "index.html"
SCHEMA_VERSION = "0.1.0"   # version of the evaluation file format the page writes

SHORT = {"observation": "Observation", "exploration": "Exploration", "question": "Question", "hypothesis": "Hypothesis",
         "theory": "Theory", "simulation": "Simulation", "instruments": "Instruments", "methods": "Methods",
         "synthesis": "Synthesis", "reconstruction": "Reconstruction", "robustness": "Robustness",
         "estimation": "Estimation", "regularities": "Regularities"}
ORDER = ["question", "exploration", "observation", "instruments", "methods", "estimation", "regularities",
         "theory", "simulation", "hypothesis", "reconstruction", "synthesis", "robustness"]
ENTRY = {"anomaly": "an anomaly: something unexpected in data", "problem": "an unsolved problem",
         "hypothesis": "a hypothesis to test", "data_without_theory": "data without a theory",
         "capability": "a new capability: instrument, method, or data set", "external_goal": "a goal set from outside (a mission, a benchmark, a hazard)",
         "challenged_result": "a published result to challenge or replicate"}
OUTCOME = {"kept": "kept: the claim is retained", "excluded": "excluded: a rival is ruled out",
           "contradicted": "contradicted: an earlier claim is refuted", "no_conclusion": "no conclusion reached"}
STATUS = {"confirmed": "confirmed by a test it could have failed", "best_explanation": "best explanation among stated rivals",
          "regularity_in_range": "a regularity, within a stated range", "estimate_with_resolution": "an estimate with stated resolution or uncertainty",
          "capability_characterized": "a capability, characterized", "forecast_skill": "forecast skill, verified", "none": "no claim status"}


def modes():
    out = []
    for f in sorted((ROOT / "modes").glob("*.qmd")):
        t = f.read_text()
        mid = re.search(r"^mode_id:\s*(\S+)", t, re.M).group(1)
        ver = re.search(r'^mode_version:\s*"?([^"\n]+)"?', t, re.M).group(1)
        title = re.search(r"^# (.+?)\s*\{", t, re.M).group(1)
        purpose = re.search(r"## Epistemic purpose\s*\n+- (.+)", t).group(1)
        purpose = re.sub(r"\[@[^\]]+\]", "", purpose)
        purpose = re.split(r"(?<=\.)\s", purpose)[0].strip()
        out.append({"id": mid, "title": title, "short": SHORT[mid], "purpose": purpose, "version": ver})
    out.sort(key=lambda m: ORDER.index(m["id"]))
    return out


def nodes():
    t = (ROOT / "unit.qmd").read_text()
    rows = re.findall(r"^\| \*\*([A-Z])\*\* \| (.+?) \|", t, re.M)
    seen, out = set(), []
    for k, verb in rows:
        if k in seen:
            continue
        seen.add(k)
        out.append({"k": k, "verb": re.sub(r"\*\*", "", verb).strip()})
    return out


def spec():
    tree = json.loads((ROOT / "agents/controller/decision-tree.json").read_text())
    sch = json.loads((ROOT / "agents/coder/coding.schema.json").read_text())
    P = sch["properties"]
    ms = modes()
    ns = nodes()
    order = [n for n in P["entry"]["properties"]["node"]["enum"]]
    assert sorted(n["k"] for n in ns) == sorted(order), "graph nodes in unit.qmd differ from the coding schema"
    assert sorted(m["id"] for m in ms) == sorted(P["sequences"]["items"]["properties"]["steps"]["items"]["properties"]["mode"]["enum"]), \
        "modes/*.qmd differ from the coding schema"
    return {
        "schema_version": SCHEMA_VERSION,
        "graph_version": "0.4.2",
        "codebook_version": P["codebook_version"]["enum"][-1],
        "modes_version": {m["id"]: m["version"] for m in ms},
        "built": datetime.date.today().isoformat(),
        "modes": ms,
        "nodes": sorted(ns, key=lambda n: order.index(n["k"])),
        "entry_states": [[k, ENTRY[k]] for k in P["entry"]["properties"]["state"]["enum"]],
        "outcomes": [[k, OUTCOME[k]] for k in P["end"]["properties"]["outcome"]["enum"]],
        "statuses": [[k, STATUS[k]] for k in P["end"]["properties"]["claim_status"]["enum"]],
        "tree": {"version": tree["version"], "start": tree["start"],
                 "questions": [{"n": q["n"], "q": q["q"], "sub": q["sub"], "down": q["down"],
                                "branches": [{"label": b["label"], "name": b.get("name", ""), "ret": b.get("ret", "")} for b in q["branches"]]}
                               for q in tree["questions"]]},
    }


def render(sp):
    html = TEMPLATE.read_text()
    marker = "/*__SPEC__*/null"
    assert html.count(marker) == 1
    return html.replace(marker, json.dumps(sp, ensure_ascii=False))


def main():
    sp = spec()
    if "--check" in sys.argv:
        if not OUT.exists():
            sys.exit("evaluate/index.html is missing; run python tools/evaluate/build_evaluate.py")
        cur = OUT.read_text()
        m = re.search(r'"built": "[0-9-]+"', cur)
        sp["built"] = json.loads("{" + m.group(0) + "}")["built"] if m else sp["built"]
        if render(sp) != cur:
            sys.exit("evaluate/index.html is out of date; run python tools/evaluate/build_evaluate.py")
        print("evaluate/index.html is up to date")
        return
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(render(sp))
    print(f"wrote {OUT.relative_to(ROOT)}: {len(sp['modes'])} modes, {len(sp['nodes'])} nodes, "
          f"{len(sp['tree']['questions'])} tree questions, form v{SCHEMA_VERSION}")


if __name__ == "__main__":
    main()
