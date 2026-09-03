#!/usr/bin/env python3
"""
LLM judge for the Iran-US crisis briefing task.

The judge uses equal boolean checks and computes:
    score = checks_passed / total_checks

Deterministic parsing is used only to gather evidence for the LLM judge. There
are no hard gates: missing files, low URL coverage, or malformed CSVs simply
give the LLM evidence to mark the relevant checks false.
"""

import csv
import json
import os
import re
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None


AGENT_OUTPUT_DIR = Path("/logs/agent")
INPUT_MANIFEST = Path("/input_artifacts/source_manifest.csv")
FIREWORKS_URL = "https://api.fireworks.ai/inference/v1/chat/completions"
JUDGE_MODEL = os.environ.get("JUDGE_MODEL", "accounts/fireworks/models/deepseek-v4-flash")
FIREWORKS_API_KEY = os.environ.get("FIREWORKS_API_KEY", "")

REQUIRED_FILES = [
    "source_audit.csv",
    "source_evidence_ledger.csv",
    "event_timeline.csv",
    "claim_matrix.csv",
    "contradiction_ledger.csv",
    "actor_positions.csv",
    "impact_register.csv",
    "uncertainty_register.csv",
    "appendix_citation_index.csv",
    "executive_briefing.md",
    "full_analytical_report.md",
    "stakeholder_briefing_slides.md",
    "one_page_talking_points.md",
    "monitoring_plan.md",
]

CHECKS = [
    "All 14 required deliverables are present and substantively non-empty.",
    "source_audit.csv contains one row for each seed source ID S001-S100.",
    "source_audit.csv records access status, direct_quote_1/direct_quote_2, evidence_ids_extracted, claim_ids_supported, event_ids_supported, and usability notes for every seed source.",
    "source_evidence_ledger.csv contains 250-350 evidence rows.",
    "source_evidence_ledger.csv includes evidence or retrieval-status notes from at least 70 distinct seed source IDs and direct quoted evidence from at least 45 distinct seed source IDs.",
    "Most quoted evidence rows contain source-specific direct quotes of roughly 8-40 words rather than generic paraphrases.",
    "The evidence ledger covers official/IGO, wire news, regional sources, think tanks, market/shipping/aviation sources, and reference/background sources.",
    "Evidence rows include stable EV### IDs plus source_id, url, retrieval_status, direct_quote, extracted_claim, topic_area, supports_claim_ids, supports_event_ids, supports_deliverables, confidence, and limitations fields.",
    "event_timeline.csv includes at least 35 chronological events covering pre-strike context, U.S. strikes, immediate reactions, Al Udeid retaliation, ceasefire sequence, and post-strike assessment disputes.",
    "Timeline events include evidence_ids, source IDs, and confidence labels rather than unsupported chronology.",
    "The timeline sequence is consistent with the final report and slide deck.",
    "claim_matrix.csv includes at least 50 claims spanning facility damage, uranium stockpile status, advance notice, missile counts, casualties, radiation risk, ceasefire timing, regional reactions, and economic/shipping effects.",
    "Every substantive claim row includes evidence_ids and source IDs that link back to source_evidence_ledger.csv and source_audit.csv.",
    "The claim matrix correctly distinguishes confirmed, disputed, unsupported, and unclear claims.",
    "contradiction_ledger.csv includes at least 25 contradictions or disputed factual conflicts.",
    "contradiction_ledger.csv covers damage assessment, uranium stockpile, missile counts, advance warning timing, ceasefire sequence, radiation/safety, casualty figures, regional reactions, energy/shipping effects, and inspection access.",
    "Every contradiction row links claim_a_evidence_ids and claim_b_evidence_ids to actual evidence rows and explains why the claims conflict.",
    "The final report does not present disputed claims as settled facts.",
    "High-impact claims in the final report are cited to source IDs plus claim_id or event_id, and disputed claims cite contradiction_id.",
    "actor_positions.csv covers at least 20 relevant actors including the United States, Iran, Israel, Qatar, Saudi Arabia, UAE, Oman, Russia, China, UK, France, Germany, the UN, IAEA, EU, and at least four others.",
    "Actor positions include evidence_ids and are attributed neutrally without endorsing one actor's framing as fact.",
    "impact_register.csv includes at least 30 impacts.",
    "The impact register covers diplomatic, legal, nuclear_safety, energy_market, shipping, aviation, humanitarian, domestic_politics, regional_security, and information_environment domains.",
    "Impact severity and confidence labels are supported by cited evidence_ids and source IDs.",
    "uncertainty_register.csv includes at least 15 unresolved questions or evidence gaps.",
    "The uncertainty register covers underground damage, uranium stockpile location/status, missile count discrepancies, ceasefire sequencing, radiation/safety implications, and future inspection access.",
    "Uncertainty rows link to evidence_ids and related_contradiction_ids where applicable.",
    "The executive briefing is decision-ready, concise, approximately 2-4 pages, and includes confirmed facts, disputed facts, implications, and monitoring indicators.",
    "The full analytical report contains all required sections from the instruction and is 6,000-10,000 words or otherwise clearly within the requested long-form range.",
    "The full report explains the source base and limitations, including the limits of public evidence and classified/intelligence uncertainty.",
    "The full report covers U.S. strike timeline and stated rationale without giving tactical advice.",
    "The full report covers Iranian response, Al Udeid retaliation, and the ceasefire sequence with source-grounded nuance.",
    "The full report covers nuclear safety, IAEA/UN context, and legal/diplomatic framing with proper attribution.",
    "The full report covers regional reactions across Gulf, European, Russian, Chinese, Israeli, Iranian, and international actors.",
    "The full report covers energy, shipping, aviation, market, humanitarian, civilian, and information-environment implications.",
    "stakeholder_briefing_slides.md contains 12-18 slide-style sections and covers timeline, actor positions, disputed claims, impacts, uncertainties, and monitoring indicators.",
    "one_page_talking_points.md includes neutral talking points, avoid-saying notes, and Q&A that prevent overclaiming disputed facts.",
    "monitoring_plan.md is a 7-14 day public-source monitoring plan with indicators, source categories, escalation/de-escalation signals, and no operational guidance.",
    "appendix_citation_index.csv maps source_id, evidence_id, claim_id, event_id, deliverables, sections or rows, and supported claims/findings.",
    "Cross-artifact consistency is maintained between the source audit, evidence ledger, timeline, claim matrix, contradiction ledger, actor positions, impact register, uncertainty register, citation index, briefing, report, slides, talking points, and monitoring plan.",
    "The final report uses claim_id/event_id references for major factual claims and contradiction_id references for disputed claims.",
    "The source audit, evidence ledger, claim matrix, timeline, contradiction ledger, and citation index use resolvable IDs rather than orphaned identifiers.",
    "The package does not get credit merely by listing source IDs; it demonstrates source-by-source browsing through quote-backed evidence and retrieval-status notes.",
    "The language is neutral and avoids advocacy, inflammatory framing, propaganda style, or loaded unattributed claims.",
    "The package avoids tactical military advice, targeting guidance, cyber guidance, sanctions evasion guidance, or advice to any belligerent.",
    "The overall package would be professionally useful to a policy, risk, humanitarian, market, or communications team."
]


def read_text(path: Path) -> str:
    if not path.exists():
        return "[MISSING]"
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as exc:
        return f"[READ_ERROR: {exc}]"
    return text


def read_csv_rows(path: Path, limit: int = 600) -> list[dict]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8", errors="ignore", newline="") as handle:
            return list(csv.DictReader(handle))[:limit]
    except Exception:
        return []


def ids_in_text(text: str) -> set[str]:
    return set(re.findall(r"\bS\d{3}\b", text or ""))


def split_ids(value: str, prefix: str) -> set[str]:
    if not value:
        return set()
    return set(re.findall(rf"\b{prefix}\d{{3}}\b", value))


def quote_word_count(value: str) -> int:
    return len(re.findall(r"\b\w+\b", value or ""))


def rows_missing_any(rows: list[dict], columns: list[str]) -> int:
    return sum(1 for row in rows if any(not str(row.get(col, "")).strip() for col in columns))


def collect_evidence() -> dict:
    files = {}
    all_text = ""
    for name in REQUIRED_FILES:
        path = AGENT_OUTPUT_DIR / name
        text = read_text(path)
        files[name] = {
            "exists": path.exists(),
            "size_bytes": path.stat().st_size if path.exists() else 0,
            "excerpt": text,
        }
        all_text += "\n" + text

    csv_summaries = {}
    csv_rows_by_name = {}
    for name in REQUIRED_FILES:
        if name.endswith(".csv"):
            rows = read_csv_rows(AGENT_OUTPUT_DIR / name)
            csv_rows_by_name[name] = rows
            csv_summaries[name] = {
                "row_count": len(rows),
                "columns": list(rows[0].keys()) if rows else [],
                "sample_rows": rows[:8],
                "source_ids_seen": sorted({row.get("source_id", "") for row in rows if row.get("source_id", "")})[:120],
            }

    manifest_rows = read_csv_rows(INPUT_MANIFEST, limit=150)
    manifest_ids = {row.get("source_id", "") for row in manifest_rows if row.get("source_id")}
    cited_ids = sorted(ids_in_text(all_text))

    markdown_word_counts = {
        name: len(re.findall(r"\b\w+\b", files[name]["excerpt"]))
        for name in REQUIRED_FILES
        if name.endswith(".md")
    }

    evidence_rows = csv_rows_by_name.get("source_evidence_ledger.csv", [])
    quoted_evidence_rows = [
        row for row in evidence_rows
        if quote_word_count(row.get("direct_quote", "")) >= 8
    ]
    evidence_ids = {row.get("evidence_id", "") for row in evidence_rows if row.get("evidence_id")}
    claim_rows = csv_rows_by_name.get("claim_matrix.csv", [])
    timeline_rows = csv_rows_by_name.get("event_timeline.csv", [])
    contradiction_rows = csv_rows_by_name.get("contradiction_ledger.csv", [])
    actor_rows = csv_rows_by_name.get("actor_positions.csv", [])
    impact_rows = csv_rows_by_name.get("impact_register.csv", [])
    uncertainty_rows = csv_rows_by_name.get("uncertainty_register.csv", [])
    citation_rows = csv_rows_by_name.get("appendix_citation_index.csv", [])

    linked_evidence_ids = set()
    for rows, cols in [
        (claim_rows, ["evidence_ids"]),
        (timeline_rows, ["evidence_ids"]),
        (contradiction_rows, ["claim_a_evidence_ids", "claim_b_evidence_ids"]),
        (actor_rows, ["evidence_ids"]),
        (impact_rows, ["evidence_ids"]),
        (uncertainty_rows, ["evidence_ids"]),
        (citation_rows, ["evidence_id"]),
    ]:
        for row in rows:
            for col in cols:
                linked_evidence_ids |= split_ids(str(row.get(col, "")), "EV")

    computed_metrics = {
        "source_evidence_ledger": {
            "row_count": len(evidence_rows),
            "quoted_row_count_with_8plus_words": len(quoted_evidence_rows),
            "distinct_sources_with_any_evidence": len({row.get("source_id", "") for row in evidence_rows if row.get("source_id", "")}),
            "distinct_sources_with_quotes": len({row.get("source_id", "") for row in quoted_evidence_rows if row.get("source_id", "")}),
            "rows_missing_required_fields": rows_missing_any(evidence_rows, [
                "evidence_id", "source_id", "url", "retrieval_status", "direct_quote",
                "extracted_claim", "topic_area", "supports_claim_ids", "supports_event_ids",
                "supports_deliverables", "confidence", "limitations"
            ]),
            "quoted_rows_missing_direct_quote": sum(
                1 for row in evidence_rows
                if quote_word_count(row.get("direct_quote", "")) < 8
            ),
        },
        "linkage": {
            "evidence_id_count": len(evidence_ids),
            "linked_evidence_id_count": len(linked_evidence_ids),
            "orphan_linked_evidence_ids": sorted(linked_evidence_ids - evidence_ids)[:50],
            "claim_rows_missing_evidence_ids": rows_missing_any(claim_rows, ["evidence_ids"]),
            "timeline_rows_missing_evidence_ids": rows_missing_any(timeline_rows, ["evidence_ids"]),
            "contradiction_rows_missing_evidence_ids": rows_missing_any(
                contradiction_rows, ["claim_a_evidence_ids", "claim_b_evidence_ids"]
            ),
            "actor_rows_missing_evidence_ids": rows_missing_any(actor_rows, ["evidence_ids"]),
            "impact_rows_missing_evidence_ids": rows_missing_any(impact_rows, ["evidence_ids"]),
            "uncertainty_rows_missing_evidence_or_contradiction": rows_missing_any(
                uncertainty_rows, ["evidence_ids", "related_contradiction_ids"]
            ),
        },
        "row_counts": {
            "source_audit": len(csv_rows_by_name.get("source_audit.csv", [])),
            "event_timeline": len(timeline_rows),
            "claim_matrix": len(claim_rows),
            "contradiction_ledger": len(contradiction_rows),
            "actor_positions": len(actor_rows),
            "impact_register": len(impact_rows),
            "uncertainty_register": len(uncertainty_rows),
            "appendix_citation_index": len(citation_rows),
        },
        "final_report_id_mentions": {
            "claim_ids": len(set(re.findall(r"\bCL\d{3}\b", files["full_analytical_report.md"]["excerpt"]))),
            "event_ids": len(set(re.findall(r"\bEVT\d{3}\b", files["full_analytical_report.md"]["excerpt"]))),
            "contradiction_ids": len(set(re.findall(r"\bCON\d{3}\b", files["full_analytical_report.md"]["excerpt"]))),
        },
    }

    return {
        "required_file_presence": {
            name: {"exists": files[name]["exists"], "size_bytes": files[name]["size_bytes"]}
            for name in REQUIRED_FILES
        },
        "manifest_source_count": len(manifest_rows),
        "manifest_ids_sample": sorted(manifest_ids)[:110],
        "distinct_seed_ids_cited_or_mapped_count": len([sid for sid in cited_ids if sid in manifest_ids]),
        "distinct_seed_ids_cited_or_mapped": [sid for sid in cited_ids if sid in manifest_ids],
        "csv_summaries": csv_summaries,
        "markdown_excerpts": {
            name: files[name]["excerpt"]
            for name in REQUIRED_FILES
            if name.endswith(".md")
        },
        "markdown_word_counts": markdown_word_counts,
        "computed_metrics": computed_metrics,
    }


def call_judge(prompt: str) -> str:
    if requests is None:
        print("JUDGE_DEBUG: requests library not available", file=sys.stderr)
        return ""
    if not FIREWORKS_API_KEY:
        print("JUDGE_DEBUG: FIREWORKS_API_KEY is empty or not set", file=sys.stderr)
        return ""
    try:
        response = requests.post(
            FIREWORKS_URL,
            headers={
                "Authorization": f"Bearer {FIREWORKS_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": JUDGE_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.0,
                "max_tokens": 7000,
            },
            timeout=120,
        )
        if response.status_code != 200:
            print(f"JUDGE_DEBUG: API status {response.status_code}: {response.text[:500]}", file=sys.stderr)
            return ""
        return response.json()["choices"][0]["message"]["content"]
    except Exception as exc:
        print(f"JUDGE_DEBUG: API exception: {exc}", file=sys.stderr)
        return ""


def extract_json(text: str) -> dict:
    if not text:
        return {}
    try:
        return json.loads(text)
    except Exception:
        pass
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        return {}
    try:
        return json.loads(match.group(0))
    except Exception:
        return {}


def build_prompt(evidence: dict) -> str:
    checks_json = json.dumps(
        [{"id": i + 1, "name": name} for i, name in enumerate(CHECKS)],
        indent=2,
    )
    evidence_json = json.dumps(evidence, indent=2)
    return f"""You are an independent LLM judge evaluating a SwarmBench crisis-intelligence task.

Grade ONLY the submitted deliverables using the equal boolean checks below.
Do not reward coordination style. Do not compare single-agent vs multi-agent behavior.
Each check is worth exactly one point. Mark a check true only if the evidence in the submitted files supports it.
Missing or incomplete files should only cause the relevant checks to fail; continue grading all other checks.

Return STRICT JSON with this shape:
{{
  "checks": [
    {{"id": 1, "passed": true, "reason": "short evidence-based reason"}},
    ...
  ]
}}

Checks:
{checks_json}

Evidence extracted from /logs/agent:
{evidence_json}
"""


def normalize_results(judge_data: dict) -> list[dict]:
    by_id = {}
    for item in judge_data.get("checks", []):
        try:
            cid = int(item.get("id"))
        except Exception:
            continue
        by_id[cid] = item

    results = []
    for idx, name in enumerate(CHECKS, start=1):
        item = by_id.get(idx, {})
        results.append({
            "id": idx,
            "name": name,
            "passed": bool(item.get("passed", False)),
            "reason": str(item.get("reason", "No judge rationale returned"))[:500],
        })
    return results


def main() -> float:
    evidence = collect_evidence()
    prompt = build_prompt(evidence)
    raw_response = call_judge(prompt)
    judge_data = extract_json(raw_response)
    results = normalize_results(judge_data)

    passed = sum(1 for item in results if item["passed"])
    total = len(results)
    score = passed / total if total else 0.0

    output = {
        "judge_score": round(score, 4),
        "checks_passed": passed,
        "total_checks": total,
        "details": results,
        "raw_judge_response": raw_response[:4000],
        "evidence_summary": {
            "manifest_source_count": evidence["manifest_source_count"],
            "distinct_seed_ids_cited_or_mapped_count": evidence["distinct_seed_ids_cited_or_mapped_count"],
            "required_file_presence": evidence["required_file_presence"],
            "computed_metrics": evidence["computed_metrics"],
        },
    }

    print(json.dumps(output, indent=2))
    return score


if __name__ == "__main__":
    main()
