#!/usr/bin/env python3
import csv
import json
import re
from pathlib import Path


OUTPUT = Path("/logs/agent/output")
INPUT = Path("/environment/input_artifacts")
VERIFIER = Path("/logs/verifier")
RESULTS = []

REQUIRED_INJECT_COLUMNS = [
    "inject_id", "exercise_time", "phase", "target_role", "inject_text",
    "affected_system_or_dependency", "expected_decision", "debrief_objective",
    "source_id", "source_url", "quoted_evidence",
]
REQUIRED_OBSERVER_COLUMNS = [
    "objective_id", "inject_id", "role", "expected_behavior", "observed_behavior_notes",
    "rating_scale", "evidence_of_decision_quality", "improvement_area",
]
REQUIRED_EVIDENCE_COLUMNS = [
    "source_id", "source_url", "title", "publisher", "source_type",
    "quoted_evidence", "used_in_artifact", "used_for",
]
REQUIRED_VISUAL_COLUMNS = [
    "exhibit_id", "source_id", "source_url", "visual_type",
    "visual_observation", "exercise_design_use", "used_in_artifact",
]
REQUIRED_ROLES = [
    "ciso.md", "legal.md", "communications.md", "executive_leadership.md",
    "it_operations.md", "vendor_management.md",
]
ALLOWED_TARGET_ROLES = {
    "CISO", "Legal", "Communications", "Executive Leadership",
    "IT Operations", "Vendor Management",
}
EXTERNAL_ASSET_TAG_RE = re.compile(
    r"<\s*(script|link|img|iframe|audio|video|source|embed)\b[^>]*\b(?:src|href)\s*=\s*['\"]https?://",
    re.IGNORECASE,
)
LINKED_CSS_JS_RE = re.compile(
    r"<\s*script\b[^>]*\bsrc\s*=|<\s*link\b[^>]*\bhref\s*=",
    re.IGNORECASE,
)

EXECUTIVE_REQUIRED_TERMS = [
    "purpose", "audience", "2-hour", "schedule", "assumptions", "artificialities",
    "rules of engagement", "staffing", "success criteria", "pre-read", "remediation",
]
FACILITATOR_REQUIRED_TERMS = [
    "opening script", "phase", "inject", "listen", "expected decision",
    "escalation", "fallback", "debrief",
]
ROLE_REQUIRED_TERMS = [
    "responsibilities", "private context", "decision authority",
    "constraints", "key questions",
]
AFTER_ACTION_REQUIRED_TERMS = [
    "strengths", "gaps", "follow-up", "remediation owners", "due dates", "retest plan",
    "mapping", "objective",
]
VISUAL_LAYOUT_TERMS = [
    "row", "column", "axis", "chart", "table", "figure", "legend", "bar", "panel",
    "layout", "sequence", "proportion", "percentage", "grouping", "taxonomy", "visual",
]
GOVERNMENT_SOURCE_TOKENS = [
    "government", "regulatory", "congressional", "senate", "house",
    "sec", "hhs", "cms", "ocr", "cisa", "fbi", "aspr",
    "office of financial research", "financial_disclosure",
]
HEALTHCARE_SOURCE_TOKENS = [
    "healthcare_sector", "american hospital association", "hospital", "provider impact",
]
TECHNICAL_SOURCE_TOKENS = [
    "technical", "sector_guidance", "ransomware", "ttp", "advisory", "cybersecurity",
]


def check(name, passed, reason=""):
    RESULTS.append({"name": name, "passed": bool(passed), "reason": reason or ("OK" if passed else "failed")})


def normalize(text):
    text = (text or "").lower()
    text = text.replace("’", "'").replace("“", '"').replace("”", '"')
    text = re.sub(r"[^a-z0-9\s'\"]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def quote_round_trips(quote, source_text):
    q = normalize(quote)
    s = normalize(source_text)
    words = q.split()
    if len(words) < 12:
        return False
    if q and q in s:
        return True
    for i in range(0, max(0, len(words) - 11)):
        if " ".join(words[i:i + 12]) in s:
            return True
    return False


def read_csv(path):
    if not path.exists():
        return [], []
    with path.open(newline="", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames or [], list(reader)


def read_sources():
    path = INPUT / "sources.json"
    try:
        rows = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        rows = []
    return {row.get("source_id"): row for row in rows}


def read_visual_exhibits():
    path = INPUT / "visual_exhibits.json"
    try:
        rows = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        rows = []
    return {row.get("exhibit_id"): row for row in rows}


def valid_source_refs(text, valid_source_ids):
    return set(re.findall(r"\bSRC\d{3}\b", text or "")) & valid_source_ids


def has_all_terms(text, terms):
    haystack = (text or "").lower()
    return all(term.lower() in haystack for term in terms)


def has_any_term(text, terms):
    haystack = (text or "").lower()
    return any(term.lower() in haystack for term in terms)


def source_matches(source, tokens):
    text = f"{source.get('source_type', '')} {source.get('publisher', '')} {source.get('title', '')}".lower()
    return any(token.lower() in text for token in tokens)


def visual_local_file_exists(exhibit):
    local_file = (exhibit.get("local_file") or "").strip()
    if not local_file:
        return False
    path = INPUT / local_file
    if not (path.exists() and path.is_file() and path.suffix.lower() == ".pdf" and path.stat().st_size > 1000):
        return False
    try:
        return path.read_bytes().startswith(b"%PDF")
    except Exception:
        return False


def main():
    VERIFIER.mkdir(parents=True, exist_ok=True)
    sources = read_sources()
    visual_exhibits = read_visual_exhibits()
    check("sources.json has 50 entries", len(sources) == 50, f"{len(sources)} entries")
    check("visual_exhibits.json has at least 5 entries", len(visual_exhibits) >= 5, f"{len(visual_exhibits)} entries")
    missing_visual_files = sorted(
        exhibit_id for exhibit_id, exhibit in visual_exhibits.items()
        if not visual_local_file_exists(exhibit)
    )
    check(
        "visual exhibits have local rendered PDF files",
        not missing_visual_files,
        str(missing_visual_files),
    )

    executive = OUTPUT / "executive_runbook.md"
    facilitator = OUTPUT / "facilitator_guide.md"
    injects = OUTPUT / "injects_timeline.csv"
    roles_dir = OUTPUT / "role_packets"
    observer = OUTPUT / "observer_scorecards.csv"
    evidence = OUTPUT / "evidence_register.csv"
    visual_notes = OUTPUT / "visual_exhibit_notes.csv"
    map_html = OUTPUT / "incident_map.html"
    aar = OUTPUT / "after_action_template.md"

    check("executive_runbook.md exists and >=4000 chars", executive.exists() and executive.stat().st_size >= 4000)
    check("facilitator_guide.md exists and >=8000 chars", facilitator.exists() and facilitator.stat().st_size >= 8000)
    check("injects_timeline.csv exists", injects.exists())
    check("role_packets has all six role files", roles_dir.exists() and all((roles_dir / r).exists() for r in REQUIRED_ROLES))
    check("observer_scorecards.csv exists", observer.exists())
    check("evidence_register.csv exists", evidence.exists())
    check("visual_exhibit_notes.csv exists", visual_notes.exists())
    check("incident_map.html exists and >=5000 chars", map_html.exists() and map_html.stat().st_size >= 5000)
    check("after_action_template.md exists and >=3000 chars", aar.exists() and aar.stat().st_size >= 3000)

    inject_cols, inject_rows = read_csv(injects)
    observer_cols, observer_rows = read_csv(observer)
    evidence_cols, evidence_rows = read_csv(evidence)
    visual_cols, visual_rows = read_csv(visual_notes)

    check("injects_timeline.csv has required columns", all(c in inject_cols for c in REQUIRED_INJECT_COLUMNS), str(inject_cols))
    check("injects_timeline.csv has at least 40 rows", len(inject_rows) >= 40, f"{len(inject_rows)} rows")
    check("every inject row has required non-empty fields", all(all((row.get(c) or "").strip() for c in REQUIRED_INJECT_COLUMNS) for row in inject_rows))
    bad_roles = sorted({row.get("target_role", "").strip() for row in inject_rows if row.get("target_role", "").strip() not in ALLOWED_TARGET_ROLES})
    check("every inject target_role is an allowed role", not bad_roles, str(bad_roles))
    check("observer_scorecards.csv has required columns", all(c in observer_cols for c in REQUIRED_OBSERVER_COLUMNS), str(observer_cols))
    check("observer_scorecards.csv has at least 40 rows", len(observer_rows) >= 40, f"{len(observer_rows)} rows")
    check("evidence_register.csv has required columns", all(c in evidence_cols for c in REQUIRED_EVIDENCE_COLUMNS), str(evidence_cols))
    check("visual_exhibit_notes.csv has required columns", all(c in visual_cols for c in REQUIRED_VISUAL_COLUMNS), str(visual_cols))
    check("visual_exhibit_notes.csv has at least 5 rows", len(visual_rows) >= 5, f"{len(visual_rows)} rows")
    check("every visual exhibit row has required non-empty fields", all(all((row.get(c) or "").strip() for c in REQUIRED_VISUAL_COLUMNS) for row in visual_rows))

    inject_ids = {row.get("inject_id", "").strip() for row in inject_rows if row.get("inject_id")}
    normalized_inject_ids = {iid.upper() for iid in inject_ids}
    source_ids = {row.get("source_id", "").strip() for row in inject_rows + evidence_rows if row.get("source_id")}
    evidence_source_ids = {row.get("source_id", "").strip() for row in evidence_rows if row.get("source_id")}
    valid_source_ids = set(sources)
    valid_exhibit_ids = set(visual_exhibits)

    check("at least 30 distinct source IDs used", len(source_ids) >= 30, f"{len(source_ids)} used")
    check("all used source IDs exist in sources.json", all(sid in sources for sid in source_ids), str(sorted(source_ids - set(sources))))
    check("source_url values match pinned URL", all((not row.get("source_id")) or row.get("source_url", "").strip() == sources.get(row.get("source_id", "").strip(), {}).get("url") for row in inject_rows + evidence_rows))
    visual_ids_used = {row.get("exhibit_id", "").strip() for row in visual_rows if row.get("exhibit_id")}
    visual_source_ids = {row.get("source_id", "").strip() for row in visual_rows if row.get("source_id")}
    check("at least 5 distinct exhibit IDs in visual_exhibit_notes.csv", len(visual_ids_used) >= 5, f"{len(visual_ids_used)} distinct")
    check("all visual exhibit IDs exist in visual_exhibits.json", visual_ids_used <= valid_exhibit_ids, str(sorted(visual_ids_used - valid_exhibit_ids)))
    check("all visual exhibit source IDs exist in sources.json", visual_source_ids <= valid_source_ids, str(sorted(visual_source_ids - valid_source_ids)))
    check(
        "visual exhibit source_id/source_url values match manifest",
        all(
            row.get("exhibit_id", "").strip() in visual_exhibits
            and row.get("source_id", "").strip() == visual_exhibits[row.get("exhibit_id", "").strip()].get("source_id")
            and row.get("source_url", "").strip() == visual_exhibits[row.get("exhibit_id", "").strip()].get("source_url")
            for row in visual_rows
        ),
    )
    check("all inject source IDs appear in evidence_register.csv", {r.get("source_id", "").strip() for r in inject_rows if r.get("source_id")} <= evidence_source_ids)
    check("all observer scorecard inject IDs are valid", all(row.get("inject_id", "").strip() in inject_ids for row in observer_rows))
    objective_ids = {row.get("objective_id", "").strip() for row in observer_rows if row.get("objective_id")}
    normalized_objective_ids = {oid.upper() for oid in objective_ids}

    role_refs_ok = True
    role_ref_counts = {}
    role_source_counts = {}
    role_sources_ok = True
    for role_file in REQUIRED_ROLES:
        text = (roles_dir / role_file).read_text(encoding="utf-8", errors="ignore") if (roles_dir / role_file).exists() else ""
        refs = set(re.findall(r"\bINJ[-_]?\d+\b|\binject[_-]?\d+\b", text, flags=re.IGNORECASE))
        normalized_refs = {r.upper().replace("_", "-").replace("INJECT", "INJ") for r in refs}
        valid = {r for r in normalized_refs if r in normalized_inject_ids}
        role_ref_counts[role_file] = len(valid)
        if len(valid) < 6:
            role_refs_ok = False
        source_refs = valid_source_refs(text, valid_source_ids)
        role_source_counts[role_file] = len(source_refs)
        if len(source_refs) < 3:
            role_sources_ok = False
    check("every role packet references at least six valid inject IDs", role_refs_ok, str(role_ref_counts))
    check("every role packet cites at least three valid source IDs", role_sources_ok, str(role_source_counts))
    role_sections_ok = True
    role_section_failures = []
    for role_file in REQUIRED_ROLES:
        text = (roles_dir / role_file).read_text(encoding="utf-8", errors="ignore") if (roles_dir / role_file).exists() else ""
        if not has_all_terms(text, ROLE_REQUIRED_TERMS):
            role_sections_ok = False
            role_section_failures.append(role_file)
    check("every role packet includes required role content sections", role_sections_ok, str(role_section_failures))

    combined_text = ""
    for path in [executive, facilitator, map_html, aar]:
        if path.exists():
            combined_text += "\n" + path.read_text(encoding="utf-8", errors="ignore")
    if roles_dir.exists():
        for role_file in REQUIRED_ROLES:
            p = roles_dir / role_file
            if p.exists():
                combined_text += "\n" + p.read_text(encoding="utf-8", errors="ignore")
    aar_text = aar.read_text(encoding="utf-8", errors="ignore") if aar.exists() else ""
    aar_refs = {r.upper().replace("_", "-") for r in re.findall(r"\b(?:INJ|OBJ)[-_]?\d+\b", aar_text, flags=re.I)}
    valid_aar_refs = {r for r in aar_refs if r in normalized_inject_ids or r in normalized_objective_ids}
    check("after_action_template references at least 8 valid inject/objective IDs", len(valid_aar_refs) >= 8, str(sorted(valid_aar_refs)))
    check("after_action_template includes all required content sections", has_all_terms(aar_text, AFTER_ACTION_REQUIRED_TERMS))
    map_text = map_html.read_text(encoding="utf-8", errors="ignore") if map_html.exists() else ""
    executive_text = executive.read_text(encoding="utf-8", errors="ignore") if executive.exists() else ""
    facilitator_text = facilitator.read_text(encoding="utf-8", errors="ignore") if facilitator.exists() else ""
    check("executive_runbook includes all required content sections", has_all_terms(executive_text, EXECUTIVE_REQUIRED_TERMS))
    check("facilitator_guide includes all required content sections", has_all_terms(facilitator_text, FACILITATOR_REQUIRED_TERMS))
    debrief_windows = [
        facilitator_text[max(0, m.start() - 700):m.end() + 700]
        for m in re.finditer(r"debrief", facilitator_text, flags=re.I)
    ]
    debrief_text = "\n".join(debrief_windows)
    debrief_inject_refs = {
        r.upper().replace("_", "-").replace("INJECT", "INJ")
        for r in re.findall(r"\bINJ[-_]?\d+\b|\binject[_-]?\d+\b", debrief_text, flags=re.I)
    } & normalized_inject_ids
    debrief_objective_refs = {
        r.upper().replace("_", "-")
        for r in re.findall(r"\bOBJ[-_]?\d+\b", debrief_text, flags=re.I)
    } & normalized_objective_ids
    check(
        "facilitator debrief notes are tied to inject IDs and observer objectives",
        len(debrief_inject_refs) >= 3 and len(debrief_objective_refs) >= 3,
        f"injects={sorted(debrief_inject_refs)}, objectives={sorted(debrief_objective_refs)}",
    )
    artifact_source_ids = (
        valid_source_refs(combined_text, valid_source_ids)
        | {row.get("source_id", "").strip() for row in inject_rows if row.get("source_id")}
        | visual_source_ids
    )
    check(
        "all source IDs cited in output artifacts appear in evidence_register.csv",
        artifact_source_ids <= evidence_source_ids,
        str(sorted(artifact_source_ids - evidence_source_ids)),
    )
    check("executive_runbook cites at least 10 valid source IDs", len(valid_source_refs(executive_text, valid_source_ids)) >= 10)
    check("executive_runbook references at least 3 valid visual exhibit IDs", len(set(re.findall(r"\bVIS\d{3}\b", executive_text)) & valid_exhibit_ids) >= 3)
    check("incident_map.html references at least 20 valid inject IDs", map_html.exists() and sum(1 for iid in inject_ids if iid and iid in map_text) >= 20)
    check("incident_map.html references at least 10 valid source IDs", len(valid_source_refs(map_text, valid_source_ids)) >= 10)
    check("incident_map.html references at least 5 valid visual exhibit IDs", len(set(re.findall(r"\bVIS\d{3}\b", map_text)) & valid_exhibit_ids) >= 5)
    check("incident_map.html has no external asset URLs", map_html.exists() and not EXTERNAL_ASSET_TAG_RE.search(map_text))
    check("incident_map.html keeps CSS and JavaScript inline", map_html.exists() and not LINKED_CSS_JS_RE.search(map_text))

    phases = {row.get("phase", "").strip().lower() for row in inject_rows if row.get("phase")}
    check("at least five distinct exercise phases", len(phases) >= 5, f"{len(phases)} phases")

    gov_used = sum(1 for sid in source_ids if source_matches(sources.get(sid, {}), GOVERNMENT_SOURCE_TOKENS))
    healthcare_used = sum(1 for sid in source_ids if source_matches(sources.get(sid, {}), HEALTHCARE_SOURCE_TOKENS))
    technical_used = sum(1 for sid in source_ids if source_matches(sources.get(sid, {}), TECHNICAL_SOURCE_TOKENS))
    check("at least 10 government/regulatory sources used", gov_used >= 10, str(gov_used))
    check("at least 5 healthcare-sector impact sources used", healthcare_used >= 5, str(healthcare_used))
    check("at least 5 technical advisory or ransomware/TTP sources used", technical_used >= 5, str(technical_used))

    source_text_cache = {}
    def get_source_text(sid):
        if sid not in source_text_cache:
            path = INPUT / sources.get(sid, {}).get("local_text", f"source_text/{sid}.txt")
            try:
                source_text_cache[sid] = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                source_text_cache[sid] = ""
        return source_text_cache[sid]

    visual_layout_rows = 0
    visual_layout_failures = []
    for row in visual_rows:
        exhibit_id = row.get("exhibit_id", "").strip()
        sid = row.get("source_id", "").strip()
        observation = row.get("visual_observation", "").strip()
        row_has_layout_observation = (
            len(observation) >= 50
            and has_any_term(observation, VISUAL_LAYOUT_TERMS)
            and sid in sources
            and not quote_round_trips(observation, get_source_text(sid))
        )
        if row_has_layout_observation:
            visual_layout_rows += 1
        else:
            visual_layout_failures.append(exhibit_id or "<missing exhibit_id>")
    check(
        "at least 5 visual observations describe PDF layout rather than copied source text",
        visual_layout_rows >= 5,
        f"{visual_layout_rows}",
    )
    check(
        "every visual observation is substantive and layout-specific",
        not visual_layout_failures,
        str(visual_layout_failures),
    )

    valid_inject_quotes = 0
    for row in inject_rows:
        sid = row.get("source_id", "").strip()
        if sid in sources and quote_round_trips(row.get("quoted_evidence", ""), get_source_text(sid)):
            valid_inject_quotes += 1
    valid_evidence_quotes = 0
    for row in evidence_rows:
        sid = row.get("source_id", "").strip()
        if sid in sources and quote_round_trips(row.get("quoted_evidence", ""), get_source_text(sid)):
            valid_evidence_quotes += 1
    check("at least 35 inject quotes round-trip to source snapshots", valid_inject_quotes >= 35, f"{valid_inject_quotes}")
    check("at least 25 evidence-register quotes round-trip to source snapshots", valid_evidence_quotes >= 25, f"{valid_evidence_quotes}")

    payload = {"checks": RESULTS, "passed": sum(1 for r in RESULTS if r["passed"]), "total": len(RESULTS)}
    (VERIFIER / "verify_output.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
