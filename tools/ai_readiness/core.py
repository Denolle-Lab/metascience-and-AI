"""Offline evidence and probability-design analysis; adapted from the proposal pilot.

No retrieval engine, model client, credential loader, or network I/O is imported.
"""
from __future__ import annotations
import hashlib, json, math, random, re, statistics
from pathlib import Path
from datetime import datetime, timezone


VERSION = "0.3.0-offline"

FAMILIES = {
    "seismic_elastic": r"\b(seismi\w*|earthquake waveform\w*|acoustic sensing|DAS)\b",
    "geodetic_position_displacement": r"\b(GNSS|GPS|geodetic|geodesy|displacement time series)\b",
    "radar_backscatter_interferometry": r"\b(InSAR|SAR|synthetic aperture radar|radar backscatter)\b",
    "optical_reflectance": r"\b(optical reflectance|multispectral|hyperspectral|Landsat|Sentinel[- ]?2)\b",
    "passive_microwave": r"\b(passive microwave|microwave brightness temperature)\b",
    "thermal_radiance": r"\b(thermal infrared|thermal radiance|land surface temperature)\b",
    "atmospheric_in_situ": r"\b(radiosonde\w*|weather station\w*|in[- ]situ atmospheric)\b",
    "hydrologic_in_situ": r"\b(streamflow|discharge gauge\w*|stream gauge\w*|well water level\w*)\b",
    "oceanographic_in_situ": r"\b(Argo|ocean buoy\w*|oceanographic mooring\w*|CTD)\b",
    "gravity_potential": r"\b(gravimetr\w*|gravity anomal\w*|GRACE)\b",
    "electromagnetic_electrical": r"\b(magnetotelluric\w*|electrical resistivity|electromagnetic sounding)\b",
    "geochemical_biological": r"\b(geochem\w*|isotop\w*|environmental DNA|eDNA|biodiversity)\b",
    "human_system_records": r"\b(crop yield\w*|trade flow\w*|census|infrastructure network\w*)\b",
    "cs_text_language": r"\b(text|language|token|corpus|corpora|document)\w*\b",
    "cs_image_video": r"\b(image|video|visual|photograph)\w*\b",
    "cs_audio_speech": r"\b(audio|speech|acoustic signal)\w*\b",
    "cs_structured_tabular": r"\b(tabular|structured table)\w*\b",
    "cs_graph_relational": r"\b(graph|relational network)\w*\b",
    "cs_robotics_proprioception": r"\b(propriocept|joint angle|tactile)\w*\b",
    "other": r"(?!)",
}

AI_PATTERN = r"\b(machine learning|deep learning|neural network\w*|foundation model\w*|artificial intelligence|random forest\w*|support vector machine\w*|transformer\w*)\b"

FUSION = ["co_used_only", "joint_non_ml_inversion", "late_output_fusion", "joint_ml_inputs", "cross_modal_representation_learning", "cross_modal_transfer_test"]

def utc_now():
    return datetime.now(timezone.utc).isoformat()

def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)

def read_jsonl(path):
    with Path(path).open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]

def write_jsonl(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    temporary.replace(path)

def normalized_doi(value):
    if not value:
        return None
    return re.sub(r"^(https?://(dx\.)?doi\.org/|doi:\s*)", "", value.strip(), flags=re.I).lower().rstrip(".")

def paper_ids_digest(ids):
    return hashlib.sha256(json.dumps(sorted(ids), separators=(",", ":")).encode()).hexdigest()

def deduplicate(works):
    """Connect matching DOI OR OpenAlex IDs, including transitive duplicates."""
    groups, key_group, next_group = {}, {}, 0
    for work in works:
        keys = []
        if work.get("id"):
            keys.append("id:" + work["id"].rstrip("/"))
        if normalized_doi(work.get("doi")):
            keys.append("doi:" + normalized_doi(work["doi"]))
        if not keys:
            raise ValueError("A work lacks both a DOI and OpenAlex ID; cannot safely deduplicate.")
        matches = {key_group[key] for key in keys if key in key_group}
        group = min(matches) if matches else next_group
        if not matches:
            next_group += 1
        merged = [work]
        for existing in matches:
            merged.extend(groups.pop(existing))
        groups[group] = merged
        for item in merged:
            for key in ("id:" + item["id"].rstrip("/") if item.get("id") else None,
                        "doi:" + normalized_doi(item["doi"]) if item.get("doi") else None):
                if key:
                    key_group[key] = group
    result = []
    for items in groups.values():
        # Prefer the richest abstract, then stable identifier, without inventing text.
        chosen = max(items, key=lambda x: (len(x.get("abstract_inverted_index") or {}), x.get("id", ""))).copy()
        chosen["retrieval_query_ids"] = sorted({q for item in items for q in item.get("retrieval_query_ids", [])})
        chosen["dedup_openalex_ids"] = sorted({item["id"] for item in items if item.get("id")})
        result.append(chosen)
    return sorted(result, key=lambda row: row.get("id", row.get("doi", "")))

def reconstruct_abstract(index):
    if not index:
        return None
    words = {}
    for word, offsets in index.items():
        for offset in offsets:
            if offset in words and words[offset] != word:
                raise ValueError("Ambiguous abstract index positions.")
            words[offset] = word
    return " ".join(words.get(position, "[MISSING]") for position in range(max(words) + 1))

def evidence_matches(text, pattern, field):
    return [{"field": field, "start": match.start(), "end": match.end(), "matched_text": match.group(0)}
            for match in re.finditer(pattern, text, flags=re.I)]

def screen_work(work):
    title = work.get("display_name") or work.get("title") or ""
    abstract = reconstruct_abstract(work.get("abstract_inverted_index"))
    fields = {"title": title, "abstract": abstract or ""}
    candidates = {family: [e for field, text in fields.items() for e in evidence_matches(text, pattern, field)]
                  for family, pattern in FAMILIES.items()}
    candidates = {family: evidence for family, evidence in candidates.items() if evidence}
    ai = [e for field, text in fields.items() for e in evidence_matches(text, AI_PATTERN, field)]
    method_candidates = {
        "deep_learning": [e for field, text in fields.items() for e in evidence_matches(text, r"\b(deep learning|convolutional neural network\w*|CNNs?|transformer\w*|LSTMs?|recurrent neural network\w*)\b", field)],
        "foundation_model": [e for field, text in fields.items() for e in evidence_matches(text, r"\b(foundation model\w*|large language model\w*|LLMs?)\b", field)]
    }
    return {"paper_id": work.get("id"), "doi": normalized_doi(work.get("doi")),
            "cohort_id": work.get("cohort_id"), "modality_ontology": work.get("modality_ontology"),
            "year": work.get("publication_year"), "title": title, "abstract": abstract,
            "abstract_status": "available" if abstract else "missing",
            "screen_only": True, "screen_version": VERSION,
            "screen_interpretation": "Lexical candidate matches; neither actual modality use nor actual AI use.",
            "modality_candidates": candidates, "ai_candidate": bool(ai), "ai_evidence": ai,
            "method_candidates": method_candidates,
            "actual_modality_use": None, "actual_ai_use": None,
            "source_id": ((work.get("primary_location") or {}).get("source") or {}).get("id")}

def screen(args):
    source_digest = hashlib.sha256(Path(args.input).read_bytes()).hexdigest()
    rows = [dict(screen_work(work), source_works_jsonl_sha256=source_digest) for work in read_jsonl(args.input)]
    write_jsonl(args.out, rows)

def validate_sample_frame(rows, manifest):
    """A complete harvest manifest cannot bless a filtered/replaced screen file."""
    ids = [row.get("paper_id") for row in rows]
    if any(not isinstance(paper_id, str) or not paper_id for paper_id in ids):
        raise ValueError("Every screen record needs a paper ID matching the frozen frame.")
    if len(rows) != manifest.get("unique_works") or len(ids) != len(set(ids)):
        raise ValueError("Screen count/unique IDs do not match the complete manifest; do not sample a filtered subset.")
    if paper_ids_digest(ids) != manifest.get("paper_ids_sha256"):
        raise ValueError("Screen paper IDs differ from the frozen manifest.")
    expected_digest = manifest.get("works_jsonl_sha256")
    if not expected_digest or any(row.get("source_works_jsonl_sha256") != expected_digest for row in rows):
        raise ValueError("Screen provenance does not match the manifest's original works.jsonl hash.")

def sample_rows(rows, n_per_stratum, seed):
    if n_per_stratum < 2:
        raise ValueError("Use at least two per stratum to allow design-based variance estimation.")
    strata = {}
    for row in rows:
        stratum = f"{row['year']}|{row.get('source_id') or 'unknown_source'}|AI_screen_{int(row['ai_candidate'])}"
        strata.setdefault(stratum, []).append(row)
    selected, design = [], []
    for stratum, population in sorted(strata.items()):
        population = sorted(population, key=lambda row: row["paper_id"])
        n, N = min(n_per_stratum, len(population)), len(population)
        stable_seed = hashlib.sha256(f"{seed}|{stratum}".encode()).hexdigest()
        for row in random.Random(stable_seed).sample(population, n):
            item = row.copy()
            item.update(sampling_stratum=stratum, inclusion_probability=n / N)
            selected.append(item)
        design.append({"sampling_stratum": stratum, "year": population[0]["year"], "N": N, "n": n})
    return sorted(selected, key=lambda row: row["paper_id"]), design

def sample(args):
    manifest = read_json(args.manifest)
    if not manifest.get("frame_complete"):
        raise ValueError("Frame is incomplete. Finish harvesting before creating a probability sample.")
    rows = read_jsonl(args.input)
    validate_sample_frame(rows, manifest)
    if any(not row.get("screen_only") for row in rows):
        raise ValueError("Sampling expects the metadata screen output, including AI-screen negatives.")
    selected, strata = sample_rows(rows, args.n_per_stratum, args.seed)
    write_jsonl(args.out, selected)
    atomic_json(args.design, {"design": "stratified_simple_random_without_replacement", "seed": args.seed,
                "prototype_layout": "year_x_source_x_AI_screen; differs from the protocol's subject_x_year_band_x_AI_screen pilot",
                "frame_complete": True, "frame_manifest_sha256": hashlib.sha256(Path(args.manifest).read_bytes()).hexdigest(),
                "scope": "Frozen source frame and eligibility rules only; not all Earth-science or CS literature.",
                "sample_assignments": [{"paper_id": r["paper_id"], "year": r["year"],
                    "sampling_stratum": r["sampling_stratum"], "inclusion_probability": r["inclusion_probability"]}
                    for r in selected],
                "sample_ids_sha256": paper_ids_digest([r["paper_id"] for r in selected]),
                "strata": strata})

def annotation_template(row):
    return {"paper_id": row["paper_id"], "doi": row.get("doi"), "title": row["title"], "year": row["year"],
            "cohort_id": row.get("cohort_id"), "modality_ontology": row.get("modality_ontology"),
            "source_id": row.get("source_id"), "sampling_stratum": row.get("sampling_stratum"),
            "inclusion_probability": row.get("inclusion_probability"), "review_status": "not_reviewed",
            "reviewer_id": None, "review_date": None, "evidence_level": None,
            "full_text_status": "not_attempted", "eligibility": "uncertain", "eligibility_reason": None,
            "evidence": [], "data_sources": [], "actual_modality_families": None,
            "ai_actual_use": "uncertain", "ai_method_families": [], "ai_role": None,
            "deep_learning_actual_use": "uncertain", "foundation_model_actual_use": "uncertain",
            "foundation_model_pretraining": "uncertain", "foundation_model_roles": None,
            "training_regimes": None, "model_scale": [], "small_model_comparisons": [],
            "adoption_explanations": [],
            "fusion_labels": None, "dataset_dois_used": [], "readiness_barriers": [], "need_claims": [],
            "readiness_assessment": {"access": None, "machine_readability": None,
                "cross_experiment_interoperability": None, "training_scalability": None,
                "independent_evaluation": None, "community_reuse_evidence": None},
            "notes": "Do not copy screen labels into actual-use labels without reading and citing the methods/results."}

def template(args):
    write_jsonl(args.out, [annotation_template(row) for row in read_jsonl(args.input)])

def validate_review(row):
    if row.get("review_status") != "reviewed":
        return False
    if not row.get("reviewer_id") or row.get("evidence_level") != "full_text":
        raise ValueError("A reviewed row requires reviewer_id and full_text evidence_level.")
    if row.get("full_text_status") not in ("available_open", "available_licensed"):
        raise ValueError("A full-text reviewed row requires available_open or available_licensed full_text_status; unavailable/partial/parse-failed text is not a completed full-text review.")
    if row.get("eligibility") not in ("yes", "no", "uncertain"):
        raise ValueError("Invalid eligibility label.")
    if row.get("eligibility") == "yes":
        families = row.get("actual_modality_families")
        if families is not None and (not isinstance(families, list) or not set(families) <= set(FAMILIES)):
            raise ValueError("Unknown actual modality family.")
        if row.get("ai_actual_use") not in ("yes", "no", "uncertain"):
            raise ValueError("Invalid actual AI-use label.")
        fusion = row.get("fusion_labels")
        if fusion is not None and (not isinstance(fusion, list) or not set(fusion) <= set(FUSION)):
            raise ValueError("Unknown fusion label.")
        # Additional actual-use labels remain unknown for legacy annotations.
        for key in ["deep_learning_actual_use", "foundation_model_actual_use", "foundation_model_pretraining"]:
            if row.get(key, "uncertain") not in ("yes", "no", "uncertain"):
                raise ValueError("Invalid " + key + " label.")
            if row.get(key) == "yes" and row.get("ai_actual_use") != "yes":
                raise ValueError(key + " requires verified actual AI use.")
        if row.get("foundation_model_actual_use") == "yes" and row.get("deep_learning_actual_use") != "yes":
            raise ValueError("This codebook's neural foundation models require verified deep-learning use.")
        if row.get("foundation_model_pretraining") == "yes" and row.get("foundation_model_actual_use") != "yes":
            raise ValueError("Foundation-model pretraining requires verified foundation-model use.")
        # Each positive actual-use/fusion label must have its own locatable evidence record.
        required = set(families or []) | set(fusion or [])
        if row.get("ai_actual_use") == "yes":
            required.add("ai_actual_use")
        for key in ["deep_learning_actual_use", "foundation_model_actual_use", "foundation_model_pretraining"]:
            if row.get(key) == "yes":
                required.add(key)
        supported = set()
        for record in row.get("evidence", []):
            if not record.get("url") or not record.get("section_or_page") or not record.get("excerpt"):
                raise ValueError("Evidence requires URL, section/page, and a short excerpt.")
            if len(record["excerpt"].split()) > 25:
                raise ValueError("Evidence excerpts must not exceed 25 words each; respect total source quotation limits too.")
            supported.update(record.get("supports", []))
        if not required <= supported:
            raise ValueError("Positive actual-use/fusion labels lack evidence: " + ", ".join(sorted(required - supported)))
    return True

def metric(row, name):
    if row.get("eligibility") == "no":
        return (0, 0)
    if row.get("eligibility") != "yes":
        return None
    if name == "multimodal_actual_use":
        families = row.get("actual_modality_families")
        return None if families is None else (int(len(set(families)) >= 2), 1)
    if name == "ai_actual_use":
        ai = row.get("ai_actual_use")
        return None if ai not in ("yes", "no") else (int(ai == "yes"), 1)
    extended = {
        "deep_learning_actual_use": ("deep_learning_actual_use", None),
        "foundation_model_actual_use": ("foundation_model_actual_use", None),
        "foundation_model_pretraining": ("foundation_model_pretraining", None),
        "deep_learning_given_ai": ("deep_learning_actual_use", "ai_actual_use"),
        "foundation_model_given_ai": ("foundation_model_actual_use", "ai_actual_use"),
        "foundation_model_given_deep_learning": ("foundation_model_actual_use", "deep_learning_actual_use"),
    }
    if name in extended:
        target, condition = extended[name]
        if condition:
            value = row.get(condition, "uncertain")
            if value == "no":
                return (0, 0)
            if value != "yes":
                return None
        value = row.get(target, "uncertain")
        return None if value not in ("yes", "no") else (int(value == "yes"), 1)
    if name == "multimodal_given_ai":
        ai, families = row.get("ai_actual_use"), row.get("actual_modality_families")
        if ai == "no":
            return (0, 0)
        if ai != "yes" or families is None:
            return None
        return (int(len(set(families)) >= 2), 1)
    if name == "ai_given_multimodal":
        families, ai = row.get("actual_modality_families"), row.get("ai_actual_use")
        if families is None:
            return None
        if len(set(families)) < 2:
            return (0, 0)
        return None if ai not in ("yes", "no") else (int(ai == "yes"), 1)
    if name == "joint_ml_inputs_or_representation":
        families, labels = row.get("actual_modality_families"), row.get("fusion_labels")
        if families is None or labels is None or row.get("ai_actual_use") == "uncertain":
            return None
        positive = len(set(families)) >= 2 and row.get("ai_actual_use") == "yes" and bool(set(labels) & {"joint_ml_inputs", "cross_modal_representation_learning"})
        return (int(positive), 1)
    raise ValueError("Unknown metric")

def estimate_stratified(rows, strata, name, domain_year=None):
    by_stratum = {}
    for row in rows:
        by_stratum.setdefault(row.get("sampling_stratum"), []).append(row)
    eligible_total, positive_total, terms = 0.0, 0.0, []
    for stratum in strata:
        sample = by_stratum.get(stratum["sampling_stratum"], [])
        N, n = stratum["N"], stratum["n"]
        if isinstance(N, bool) or isinstance(n, bool) or not isinstance(N, int) or not isinstance(n, int) or not 1 <= n <= N:
            raise ValueError("Every stratum needs integer 1 <= n <= N.")
        if len(sample) != n or any(not math.isclose(row.get("inclusion_probability") or 0, n / N, rel_tol=1e-9) for row in sample):
            return {"available": False, "reason": "Missing sampled rows or inconsistent inclusion probabilities."}
        values = [metric(row, name) if domain_year is None or row.get("year") == domain_year else (0, 0) for row in sample]
        if any(value is None for value in values):
            return {"available": False, "reason": "Uncertain eligibility/actual-use labels; do not recode missing as negative."}
        mean_y = sum(value[0] for value in values) / n
        mean_x = sum(value[1] for value in values) / n
        positive_total += N * mean_y
        eligible_total += N * mean_x
        terms.append((N, n, values))
    if not eligible_total:
        return {"available": False, "reason": "No eligible denominator."}
    proportion = positive_total / eligible_total
    variance = 0.0
    for N, n, values in terms:
        if n == N:
            continue
        if n < 2:
            return {"available": False, "reason": "A non-census stratum needs at least two reviewed papers for variance."}
        residuals = [y - proportion * x for y, x in values]
        variance += N * N * (1 - n / N) * statistics.variance(residuals) / n
    se = math.sqrt(variance) / eligible_total
    boundary_non_census = proportion in (0, 1) and any(n < N for N, n, _ in terms)
    return {"available": True, "proportion": proportion, "eligible_population_total_estimate": eligible_total,
            "positive_population_total_estimate": positive_total, "standard_error": se,
            "ci95_normal_approximation": None if boundary_non_census else [max(0, proportion - 1.96 * se), min(1, proportion + 1.96 * se)],
            "ci_limitation": "A boundary estimate in a non-census sample does not justify a zero-width interval; use exact finite-population or sensitivity bounds." if boundary_non_census else None,
            "ci_method": "Stratified SRS ratio estimator, Taylor residual variance with finite-population correction; normal approximation. Sparse/boundary estimates need sensitivity analysis."}

def validate_annotation_design(rows, design):
    """Bind reviewed IDs to the saved draw, not just plausible stratum counts.

    Missing annotation rows remain missing; substituted IDs/assignments fail.
    Old designs without a saved draw support descriptive output only.
    """
    assignments = design.get("sample_assignments")
    if assignments is None:
        return False
    ids = [r.get("paper_id") for r in assignments]
    if any(not isinstance(i, str) or not i for i in ids) or len(ids) != len(set(ids)):
        raise ValueError("Saved sample assignments contain missing or duplicate paper IDs.")
    if design.get("sample_ids_sha256") != paper_ids_digest(ids):
        raise ValueError("Saved sample-ID digest mismatch.")
    expected = {r["paper_id"]: r for r in assignments}
    strata = {r["sampling_stratum"]: r for r in design["strata"]}
    if len(strata) != len(design["strata"]):
        raise ValueError("Duplicate sampling strata in design.")
    counts = {k: 0 for k in strata}
    for r in assignments:
        group = r.get("sampling_stratum")
        if group not in strata:
            raise ValueError("Saved assignment has a stratum absent from design.")
        h = strata[group]
        if any(isinstance(h.get(k),bool) or not isinstance(h.get(k),int) for k in ['N','n']) or not 1 <= h['n'] <= h['N']:
            raise ValueError("Every stratum needs integer 1 <= n <= N.")
        if (h.get("year") is not None and r.get("year") != h["year"]) or not math.isclose(r.get("inclusion_probability") or 0, h["n"] / h["N"], rel_tol=1e-9):
            raise ValueError("Saved assignment year/probability contradicts design.")
        counts[group] += 1
    if any(counts[k] != h["n"] for k, h in strata.items()):
        raise ValueError("Saved sample assignments do not match stratum sample sizes.")
    for r in rows:
        if r["paper_id"] not in expected:
            raise ValueError("Annotation paper ID was not in the saved probability sample.")
        original = expected[r["paper_id"]]
        if r.get("year") != original["year"] or r.get("sampling_stratum") != original["sampling_stratum"]:
            raise ValueError("Annotation year/stratum differs from the saved draw.")
        if not math.isclose(r.get("inclusion_probability") or 0, original["inclusion_probability"], rel_tol=1e-9):
            raise ValueError("Annotation inclusion probability differs from the saved draw.")
    return True

METRICS = ["multimodal_actual_use", "ai_actual_use", "deep_learning_actual_use",
           "foundation_model_actual_use", "foundation_model_pretraining", "multimodal_given_ai",
           "ai_given_multimodal", "joint_ml_inputs_or_representation", "deep_learning_given_ai",
           "foundation_model_given_ai", "foundation_model_given_deep_learning"]


def make_report(raw, design=None):
    ids = [r["paper_id"] for r in raw]
    cohort_ids={r.get('cohort_id') for r in raw if r.get('cohort_id')}
    ontologies={r.get('modality_ontology') for r in raw if r.get('modality_ontology')}
    if len(cohort_ids)>1 or len(ontologies)>1:
        raise ValueError('Keep different cohorts/ontologies in separate reports.')
    cohort_id=(design or {}).get('cohort_id') or next(iter(cohort_ids),None)
    ontology=(design or {}).get('modality_ontology') or next(iter(ontologies),None)
    if cohort_ids and cohort_id not in cohort_ids or ontologies and ontology not in ontologies:
        raise ValueError('Annotation cohort/ontology differs from the saved design.')
    for row in raw:
        labels=row.get('actual_modality_families') or []
        if ontology=='earth_measurement_families' and any(t.startswith('cs_') for t in labels):
            raise ValueError('CS information channels cannot be coded as Earth measurement families.')
        if ontology=='cs_information_channels' and any(not t.startswith('cs_') and t!='other' for t in labels):
            raise ValueError('Earth measurement families cannot be silently pooled with CS information channels.')
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate annotation paper IDs; adjudicate before reporting.")
    reviewed = [r for r in raw if validate_review(r)]
    if design and (design.get("design") != "stratified_simple_random_without_replacement" or not design.get("frame_complete")):
        raise ValueError("Population estimates require a complete, documented stratified SRS frame.")
    bound = validate_annotation_design(raw, design) if design else False
    assignments = (design or {}).get("sample_assignments", [])
    years = sorted({r["year"] for r in raw} | {r["year"] for r in assignments} | {h["year"] for h in (design or {}).get("strata",[]) if h.get("year") is not None})
    def domain(year):
        rows = [r for r in reviewed if year is None or r["year"] == year]
        expected = (sum(year is None or r["year"] == year for r in assignments) if assignments else sum(h["n"] for h in design["strata"] if year is None or h.get("year")==year)) if design else None
        observed = sum(year is None or r["year"] == year for r in raw)
        result = {"year": year, "annotation_rows": observed, "expected_sampled_rows": expected,
                  "missing_annotation_rows": max(0, expected-observed) if expected is not None else None,
                  "reviewed_rows": len(rows), "metrics": {}}
        for name in METRICS:
            known = [metric(r, name) for r in rows]
            numerator = sum(v[0] for v in known if v is not None)
            denominator = sum(v[1] for v in known if v is not None)
            population = {"available": False, "reason": "No bound probability-sampling design supplied."}
            if bound:
                # Preserve every original stratum/sample row for annual domain ratios.
                # Filtering rows or splitting the original N by observed years is invalid.
                population = estimate_stratified(reviewed, design["strata"], name, domain_year=year)
            result["metrics"][name] = {"reviewed_eligible_known_denominator": denominator,
                "reviewed_positive_count": numerator,
                "reviewed_subset_proportion": numerator/denominator if denominator else None,
                "unknown_or_inaccessible_labels": sum(v is None for v in known), "population_estimate": population}
        return result
    return {"created_at": utc_now(), "schema_version": 1,
        "cohort_id": cohort_id, "modality_ontology": ontology,
        "annotation_rows": len(raw), "human_reviewed_full_text_rows": len(reviewed),
        "not_reviewed_rows": len(raw)-len(reviewed), "sample_binding_verified": bound,
        "scope": (design or {}).get("scope", "Reviewed accessible subset only; no population inference."),
        "screen_labels_used_as_actual_use": False,
        "full_text_status_counts": {s: sum((r.get("full_text_status") or "unspecified")==s for r in raw)
            for s in sorted({r.get("full_text_status") or "unspecified" for r in raw})},
        "pooled": domain(None), "years": [domain(y) for y in years],
        "limitations": ["Frame/indexing and full-text coverage are distinct from sampling uncertainty.",
            "Annual estimates are survey domains using all original strata; no annual trend test is performed.",
            "Missing or unreviewed sampled rows suppress estimates; unknown labels are never zero.",
            "Author-reported adoption barriers are distinct from assessor hypotheses and causal explanations."]}


def report(args):
    result = make_report(read_jsonl(args.input), read_json(args.design) if args.design else None)
    atomic_json(args.out, result)


_validate_review_base = validate_review


def validate_review(row):
    valid = _validate_review_base(row)
    if not valid or row.get('eligibility') != 'yes':
        return valid
    evidence = row.get('evidence', [])
    supports = {s for e in evidence for s in e.get('supports', [])}
    evidence_ids = {e.get('evidence_id') for e in evidence if e.get('evidence_id')}
    regimes = row.get('training_regimes')
    allowed = {'supervised','self_supervised','semi_supervised','self_training_pseudo_labels','reinforcement_learning','other'}
    if regimes is not None:
        if not isinstance(regimes,list) or len(regimes)!=len(set(regimes)) or not set(regimes)<=allowed:
            raise ValueError('Invalid/duplicate training regimes.')
        if regimes and row.get('ai_actual_use')!='yes':
            raise ValueError('Training regimes require actual AI-use evidence.')
        if any('training_regime:'+r not in supports for r in regimes):
            raise ValueError('Training regimes need their own locatable supporting evidence.')
    roles=row.get('foundation_model_roles')
    if roles:
        allowed_roles={'pretrain_from_scratch','continued_pretraining','finetune','frozen_features','inference','evaluate_existing'}
        if not isinstance(roles,list) or not set(roles)<=allowed_roles or row.get('foundation_model_actual_use')!='yes':
            raise ValueError('Foundation-model roles require verified use and allowed role names.')
        if set(roles)&{'pretrain_from_scratch','continued_pretraining'} and row.get('foundation_model_pretraining')!='yes':
            raise ValueError('Pretraining role contradicts foundation_model_pretraining label.')
    for comparison in row.get('small_model_comparisons',[]):
        if not all(comparison.get(k) for k in ['task','baseline','comparison_model','metric_and_outcome','matched_conditions','evidence_ids']):
            raise ValueError('Small-model adequacy needs task, models, result, matched conditions and evidence IDs.')
        if not set(comparison['evidence_ids'])<=evidence_ids:
            raise ValueError('Small-model comparison references missing evidence IDs.')
    for explanation in row.get('adoption_explanations',[]):
        if explanation.get('origin') not in ('explicit_author_statement','assessor_hypothesis'):
            raise ValueError('Adoption explanations must distinguish author statements from assessor hypotheses.')
        if explanation['origin']=='explicit_author_statement' and (not explanation.get('evidence_ids') or not set(explanation['evidence_ids'])<=evidence_ids):
            raise ValueError('Explicit author adoption explanations need locatable evidence IDs.')
    return valid


_make_report_base = make_report


def make_report(raw, design=None):
    result=_make_report_base(raw, design)
    reviewed=[r for r in raw if r.get('review_status')=='reviewed' and r.get('eligibility')=='yes']
    from collections import Counter
    result['evidence_summaries']={
        'interpretation':'Descriptive counts in reviewed eligible papers only; statements are not causal explanations.',
        'training_regimes':dict(Counter(t for r in reviewed for t in (r.get('training_regimes') or []))),
        'foundation_model_roles':dict(Counter(t for r in reviewed for t in (r.get('foundation_model_roles') or []))),
        'small_model_comparison_papers':sum(bool(r.get('small_model_comparisons')) for r in reviewed),
        'explicit_author_adoption_explanations':dict(Counter(e.get('reason','other') for r in reviewed for e in r.get('adoption_explanations',[]) if e.get('origin')=='explicit_author_statement')),
        'assessor_hypotheses':dict(Counter(e.get('reason','other') for r in reviewed for e in r.get('adoption_explanations',[]) if e.get('origin')=='assessor_hypothesis'))}
    return result


def endpoint_changes(result, protocol=None):
    """Explicit endpoint contrasts, never an inferred population trend or test."""
    unavailable={'available':False,'reason':'A documented endpoint comparison protocol is required; annual plots alone do not establish growth.'}
    if not protocol:return unavailable
    required=['complete_publication_years','identical_source_frame','matched_eligibility','matched_codebook','comparable_full_text_coverage']
    gates=protocol.get('comparability',{})
    if not all(isinstance(gates.get(k),dict) and gates[k].get('confirmed') is True and gates[k].get('evidence') for k in required):
        return {'available':False,'reason':'Endpoint completeness/frame/eligibility/codebook/full-text gates are unresolved.'}
    years=protocol.get('years')
    if not isinstance(years,list) or len(years)!=2 or any(isinstance(y,bool) or not isinstance(y,int) for y in years) or years[0]>=years[1]:
        raise ValueError('Endpoint protocol needs two increasing integer publication years.')
    annual={a['year']:a for a in result['years']}
    if any(y not in annual for y in range(years[0],years[1]+1)):
        return {'available':False,'reason':'Missing intervening or endpoint years; no endpoint contrast computed.'}
    # No partial review year can masquerade as a completed endpoint series.
    for y in range(years[0],years[1]+1):
        a=annual[y]
        if a['missing_annotation_rows'] or a['annotation_rows']!=a['reviewed_rows'] or not a['reviewed_rows']:
            return {'available':False,'reason':'At least one year has missing or incomplete full-text reviews.'}
    first,last=annual[years[0]],annual[years[1]]
    metrics={}
    for name in METRICS:
        a,b=first['metrics'][name],last['metrics'][name]
        pa,pb=a['population_estimate'],b['population_estimate']
        if result.get('sample_binding_verified') and pa.get('available') and pb.get('available'):
            x,z=pa['proportion'],pb['proportion'];basis='bound_design_population_point_estimates'
        elif all(not v['unknown_or_inaccessible_labels'] and v['reviewed_subset_proportion'] is not None for v in [a,b]):
            x,z=a['reviewed_subset_proportion'],b['reviewed_subset_proportion'];basis='reviewed_accessible_subset_descriptive_only'
        else:
            metrics[name]={'available':False,'reason':'Endpoint labels or denominators are unknown/incomplete.'};continue
        metrics[name]={'available':True,'basis':basis,'first_year':years[0],'last_year':years[1],
            'first_proportion':x,'last_proportion':z,'percentage_point_change':100*(z-x),
            'last_to_first_ratio':z/x if x>0 else None,
            'ratio_limitation':None if x>0 else 'A zero baseline has no finite proportional ratio.',
            'uncertainty':'Point contrast only; no contrast CI, trend test, significance or causal interpretation.'}
    return {'available':True,'protocol':protocol,'metrics':metrics,
        'interpretation':'Endpoint point contrasts within the documented frame; descriptive subset contrasts are not field-level adoption trends.'}


_report_without_endpoints=report


def report(args):
    result=make_report(read_jsonl(args.input),read_json(args.design) if args.design else None)
    protocol=read_json(args.endpoint_protocol) if getattr(args,'endpoint_protocol',None) else None
    result['endpoint_changes']=endpoint_changes(result,protocol)
    atomic_json(args.out,result)
