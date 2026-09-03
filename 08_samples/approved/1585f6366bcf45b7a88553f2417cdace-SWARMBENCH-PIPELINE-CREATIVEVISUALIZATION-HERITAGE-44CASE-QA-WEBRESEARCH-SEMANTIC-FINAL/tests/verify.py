#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse

SOURCE_TYPES = ["unesco", "external_context"]
CURATOR_QUESTIONS = [
    "What might a visitor or educator incorrectly infer from the basic danger-list label?",
    "Which source would create the most misleading interpretation if used by itself, and what does the other source add?",
    "What important detail appears in one source but not the other, and why does that matter for museum interpretation?",
    "What can a responsible slide visual or media treatment show?",
    "What claim would be unsafe to infer from a visual treatment alone?",
    "How is the place presented, visited, conserved, restricted, or taught to the public now, and how should that change museum slide wording without becoming trip-planning advice?",
    "How should the case be phrased so the slide remains accurate and cautious?",
]
CURATOR_QUESTIONS_KEYS = [
    "likely_misreading",
    "which_source_would_mislead_if_used_alone",
    "source_unique_contributions",
    "what_the_image_can_show",
    "what_the_image_cannot_prove",
    "what_external_context_changes",
    "how_to_phrase_without_overclaiming",
]
PACKAGE_FILES = [
    "retrieval_audit.json",
    "evidence_register.csv",
    "curatorial_quality_review.json",
    "theme_cluster_map.json",
    "selection_rationale.json",
    "final_consistency_audit.json",
    "storyboard_package.json",
    "output.json",
]
BANNED_EXTERNAL_DOMAINS = [
    "whc.unesco.org",
    "unesco.org",
    "wikidata.org",
    "wikipedia.org",
    "wikimedia.org",
]


def clamp01(value) -> float:
    try:
        return min(1.0, max(0.0, float(value)))
    except Exception:
        return 0.0


def read_text(path: Path, limit: int | None = None) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""
    if limit is not None and len(text) > limit:
        return text[:limit] + "\n...[truncated]"
    return text


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace")), None
    except Exception as exc:
        return None, str(exc)


def load_manifest(input_root: Path) -> dict[str, dict]:
    data, err = load_json(input_root / "source_manifest.json")
    if err or not isinstance(data, dict):
        return {}
    cases = {}
    for item in data.get("cases", []):
        if isinstance(item, dict) and item.get("case_id"):
            cases[str(item["case_id"])] = item
    return cases


def load_reference(reference_root: Path) -> tuple[dict[str, dict], dict[str, dict]]:
    ref_index, _ = load_json(reference_root / "source_index.json")
    cases = {}
    if isinstance(ref_index, dict):
        for item in ref_index.get("cases", []):
            if isinstance(item, dict) and item.get("case_id"):
                cases[str(item["case_id"])] = item
    semantic, _ = load_json(reference_root.parent / "semantic_key.json")
    semantic_cases = {}
    if isinstance(semantic, dict):
        semantic_cases = semantic.get("cases", {}) or {}
    return cases, semantic_cases


def expected_unesco_path(cid: str) -> str:
    return f"retrieved_sources/{cid}/unesco_property_page.txt"


def expected_external_path(cid: str) -> str:
    return f"external_context/{cid}/external_context_source.txt"


def agent_rel_path(value) -> str:
    raw = str(value or "").strip().replace("\\", "/")
    for prefix in ("/logs/agent/", "logs/agent/", "./"):
        if raw.startswith(prefix):
            raw = raw[len(prefix):]
    return raw.lstrip("/")


def path_text(agent_root: Path, rel: str, limit: int | None = None) -> str:
    return read_text(agent_root / agent_rel_path(rel), limit=limit)


def normalize_url(url: str) -> str:
    return str(url or "").strip().strip('"\'<>.,);')


def urls_in_text(text: str) -> list[str]:
    return [normalize_url(x) for x in re.findall(r"https?://[^\s\"'<>]+", text or "")]


def host_for(url: str) -> str:
    try:
        return urlparse(normalize_url(url)).netloc.lower().split(":", 1)[0]
    except Exception:
        return ""


def host_matches(host: str, domain: str) -> bool:
    return host == domain or host.endswith("." + domain)


def is_unesco_source(text: str, url: str = "") -> bool:
    blob = f"{url}\n{text}".lower()
    return "whc.unesco.org" in blob or "unesco.org" in blob


def is_independent_external_url(url: str) -> bool:
    host = host_for(url)
    if not host:
        return False
    return not any(host_matches(host, domain) for domain in BANNED_EXTERNAL_DOMAINS)


def first_independent_url(text: str) -> str:
    for url in urls_in_text(text):
        if is_independent_external_url(url):
            return url
    return ""


def flatten(value) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return "\n".join(f"{k}: {flatten(v)}" for k, v in value.items())
    if isinstance(value, list):
        return "\n".join(flatten(v) for v in value)
    return str(value)


def shrink(value, max_string: int = 1200, max_items: int = 12):
    if isinstance(value, dict):
        return {str(k): shrink(v, max_string, max_items) for k, v in value.items()}
    if isinstance(value, list):
        return [shrink(v, max_string, max_items) for v in value[:max_items]]
    text = str(value or "")
    if len(text) > max_string:
        return text[:max_string] + " ...[truncated]"
    return value


def extract_json_object(text: str) -> dict | None:
    if not text:
        return None

    def try_load(candidate: str) -> dict | None:
        candidate = candidate.strip()
        if candidate.startswith("```"):
            candidate = re.sub(r"^```(?:json)?\s*", "", candidate, flags=re.I)
            candidate = re.sub(r"\s*```$", "", candidate)
        try:
            loaded = json.loads(candidate)
            return loaded if isinstance(loaded, dict) else None
        except Exception:
            return None

    direct = try_load(text)
    if direct is not None:
        return direct

    fenced = re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.I | re.S)
    candidates: list[dict] = []
    for block in fenced:
        loaded = try_load(block)
        if loaded is not None:
            candidates.append(loaded)

    # Balanced-object scan. This recovers JSON even when the model writes a
    # short preface before the object. It also avoids taking the first "{" and
    # last "}" blindly, which can fail if the model mentions examples.
    for start_idx, char in enumerate(text):
        if char != "{":
            continue
        depth = 0
        in_string = False
        escape = False
        for idx in range(start_idx, len(text)):
            ch = text[idx]
            if in_string:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    in_string = False
                continue
            if ch == '"':
                in_string = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    loaded = try_load(text[start_idx : idx + 1])
                    if loaded is not None:
                        candidates.append(loaded)
                    break

    if not candidates:
        return None
    for candidate in reversed(candidates):
        if isinstance(candidate.get("score"), (int, float)):
            return candidate
    for candidate in reversed(candidates):
        if "score" in candidate:
            return candidate
    return candidates[-1]


def fireworks_chat_json(messages: list[dict], cfg: dict, request_id: str, *, max_tokens: int | None = None) -> tuple[dict | None, str | None]:
    api_key = os.environ.get("FIREWORKS_API_KEY", "").strip()
    if not api_key:
        return None, "FIREWORKS_API_KEY not set"
    payload = {
        "model": cfg.get("llm_judge_model", "accounts/fireworks/models/kimi-k2p7-code"),
        "messages": messages,
        "temperature": cfg.get("llm_judge_temperature", 0.0),
        "max_tokens": max_tokens or cfg.get("llm_judge_max_tokens", 900),
    }
    if cfg.get("llm_judge_response_format_json", True):
        payload["response_format"] = {"type": "json_object"}
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        str(cfg.get("llm_judge_endpoint", "https://api.fireworks.ai/inference/v1/chat/completions")),
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Request-Id": request_id,
        },
        method="POST",
    )
    timeout = float(cfg.get("llm_judge_timeout_sec", 40))
    last_error = None
    retries = int(cfg.get("llm_judge_retries", 1))
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read().decode("utf-8", errors="replace")
            parsed = json.loads(body)
            content = parsed["choices"][0]["message"]["content"]
            judged = extract_json_object(content)
            if judged:
                return judged, None
            last_error = f"LLM did not return JSON: {content[:800]}"
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")[:800]
            last_error = f"HTTP {exc.code}: {body}"
        except Exception as exc:
            last_error = str(exc)
        if attempt < retries:
            time.sleep(1.5 * (attempt + 1))
    return None, last_error or "unknown LLM error"


def short_reference_excerpt(reference_root: Path, ref_case: dict, limit: int = 6500) -> str:
    pieces = []
    for rel in ref_case.get("files", []):
        text = read_text(reference_root / rel)
        if not text:
            continue
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        focused = []
        for line in lines:
            low = line.lower()
            if any(term in low for term in ["danger", "threat", "conservation", "integrity", "protection", "description", "criteria", "damage", "risk"]):
                focused.append(line)
            if len("\n".join(focused)) > limit // 2:
                break
        base = "\n".join(lines[:80])
        combined = (base + "\n\n" + "\n".join(focused)).strip()
        pieces.append(combined[:limit])
    return "\n\n---\n\n".join(pieces)[:limit]


def case_related_package_snippets(agent_root: Path, cid: str, limit: int = 5000) -> str:
    pieces = []
    for rel in ["storyboard_package.json", "output.json", "evidence_register.csv", "selection_rationale.json", "curatorial_quality_review.json"]:
        path = agent_root / rel
        if not path.exists():
            continue
        text = read_text(path)
        lower = text.lower()
        pos = lower.find(cid.lower())
        if pos < 0:
            continue
        start = max(0, pos - 1400)
        end = min(len(text), pos + 2600)
        pieces.append(f"FILE {rel}:\n{text[start:end]}")
        if sum(len(p) for p in pieces) >= limit:
            break
    return "\n\n---\n\n".join(pieces)[:limit]



def case_validation_facts(agent_root: Path, cid: str, memo: dict) -> dict:
    if not isinstance(memo, dict):
        memo = {}
    unesco_rel = expected_unesco_path(cid)
    ext_rel = expected_external_path(cid)
    unesco_text = path_text(agent_root, unesco_rel)
    ext_text = path_text(agent_root, ext_rel)
    ext = memo.get("external_context") if isinstance(memo.get("external_context"), dict) else {}
    cqs = memo.get("curator_questions") if isinstance(memo.get("curator_questions"), dict) else {}
    danger_quote = str(memo.get("danger_quote", "")).strip()
    external_quote = str(ext.get("external_quote", "")).strip()
    declared_url = normalize_url(ext.get("source_url", ""))
    detected_url = first_independent_url(ext_text)
    public_answer = str(cqs.get("what_external_context_changes", ""))
    return {
        "unesco_snapshot_exists": bool(unesco_text.strip()),
        "unesco_snapshot_has_unesco_domain": is_unesco_source(unesco_text),
        "external_snapshot_exists": bool(ext_text.strip()),
        "external_declared_url": declared_url,
        "external_detected_independent_url": detected_url,
        "external_source_is_independent": bool(is_independent_external_url(declared_url) or detected_url),
        "danger_quote_present": bool(danger_quote),
        "danger_quote_exact_in_unesco_snapshot": bool(danger_quote and danger_quote in unesco_text),
        "external_quote_present": bool(external_quote),
        "external_quote_exact_in_external_snapshot": bool(external_quote and external_quote in ext_text),
        "public_context_answer_contains_external_quote": bool(external_quote and external_quote in public_answer),
        "curator_question_keys_present": sorted(k for k in CURATOR_QUESTIONS_KEYS if k in cqs),
        "curator_question_key_count": sum(1 for k in CURATOR_QUESTIONS_KEYS if k in cqs),
    }


def audit_rows_from_loaded(audit) -> list:
    if isinstance(audit, list):
        return audit
    if isinstance(audit, dict):
        for key in ["audit_rows", "rows", "retrieval_audit", "sources", "source_rows"]:
            rows = audit.get(key)
            if isinstance(rows, list):
                return rows
        # Some agents emit a dict keyed by case ID with nested source rows.
        flattened = []
        for value in audit.values():
            if isinstance(value, list):
                flattened.extend(row for row in value if isinstance(row, dict))
            elif isinstance(value, dict):
                for nested_key in ["sources", "rows", "audit_rows"]:
                    nested = value.get(nested_key)
                    if isinstance(nested, list):
                        flattened.extend(row for row in nested if isinstance(row, dict))
        if flattened:
            return flattened
    return []


def collect_case_ids(value) -> list[str]:
    ids = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {"case_id", "primary_case_id"} and isinstance(item, str) and item.startswith("WHR-"):
                ids.append(item)
            elif key in {"case_ids", "lead_scene_ids", "supporting_scene_ids", "holdback_case_ids"} and isinstance(item, list):
                ids.extend(str(x) for x in item if isinstance(x, str) and x.startswith("WHR-"))
            else:
                ids.extend(collect_case_ids(item))
    elif isinstance(value, list):
        for item in value:
            ids.extend(collect_case_ids(item))
    return ids


def compact_slide(slide) -> dict:
    if not isinstance(slide, dict):
        return {"raw": str(slide)[:500]}
    return {
        "slide_no": slide.get("slide_no"),
        "title": slide.get("title") or slide.get("slide_title"),
        "slide_type": slide.get("slide_type"),
        "case_ids": slide.get("case_ids") or slide.get("case_id") or slide.get("primary_case_id"),
        "caption": str(slide.get("caption", ""))[:500],
        "speaker_notes": str(slide.get("speaker_notes", ""))[:700],
        "source_refs": shrink(slide.get("source_refs"), 500, 8),
        "uncertainty_flags": shrink(slide.get("uncertainty_flags"), 500, 8),
    }


def compact_case_row(row) -> dict:
    if not isinstance(row, dict):
        return {"raw": str(row)[:500]}
    keys = [
        "case_id", "decision", "theme", "visual_risk_theme", "safe_claim", "primary_safe_claim",
        "source_quote", "external_context_url", "external_context_quote", "citation_paths",
        "risk_flags", "mitigation_notes",
    ]
    return {k: shrink(row.get(k), 700, 8) for k in keys if k in row}


def summarize_package_for_judge(package, manifest: dict[str, dict]) -> dict:
    if not isinstance(package, dict):
        return {"package_is_valid_object": False, "raw_excerpt": str(package)[:12000]}
    expected_ids = sorted(manifest)
    slides = package.get("slides") if isinstance(package.get("slides"), list) else []
    evidence = package.get("evidence_table") if isinstance(package.get("evidence_table"), list) else []
    media = package.get("media_manifest") if isinstance(package.get("media_manifest"), list) else []
    citations = package.get("citation_appendix") if isinstance(package.get("citation_appendix"), list) else []
    risks = package.get("interpretation_risk_register") if isinstance(package.get("interpretation_risk_register"), list) else []
    decision_ids = []
    for key in ["lead_scene_ids", "supporting_scene_ids", "holdback_case_ids"]:
        vals = package.get(key)
        if isinstance(vals, list):
            decision_ids.extend(str(x) for x in vals)
    slide_ids = sorted(set(collect_case_ids(slides)))
    evidence_ids = sorted(set(collect_case_ids(evidence)))
    decision_set = set(decision_ids)
    return {
        "package_is_valid_object": True,
        "deck_title": package.get("deck_title"),
        "expected_case_count": len(expected_ids),
        "expected_slide_count": 30,
        "actual_slide_count": len(slides),
        "lead_scene_ids": package.get("lead_scene_ids"),
        "supporting_scene_ids": package.get("supporting_scene_ids"),
        "holdback_case_ids": package.get("holdback_case_ids"),
        "decision_partition_count": len(decision_ids),
        "decision_partition_unique_count": len(decision_set),
        "decision_missing_case_ids": [cid for cid in expected_ids if cid not in decision_set],
        "decision_extra_case_ids": sorted(cid for cid in decision_set if cid not in set(expected_ids)),
        "slide_case_coverage_count": len(slide_ids),
        "slide_case_ids": slide_ids,
        "evidence_table_count": len(evidence),
        "evidence_case_coverage_count": len(evidence_ids),
        "evidence_missing_case_ids": [cid for cid in expected_ids if cid not in set(evidence_ids)],
        "media_manifest_count": len(media),
        "citation_appendix_count": len(citations),
        "interpretation_risk_register_count": len(risks),
        "slides": [compact_slide(slide) for slide in slides],
        "evidence_rows": [compact_case_row(row) for row in evidence],
        "risk_theme_index": shrink(package.get("risk_theme_index"), 1200, 12),
        "regional_balance": shrink(package.get("regional_balance"), 1200, 12),
        "retrieval_audit_summary": shrink(package.get("retrieval_audit_summary"), 1200, 12),
        "curator_handoff": shrink(package.get("curator_handoff"), 1600, 12),
        "revision_log": shrink(package.get("revision_log"), 1200, 12),
    }

def read_case_payload(agent_root: Path, cid: str) -> dict:
    memo, memo_err = load_json(agent_root / "case_memos" / f"{cid}.json")
    if not isinstance(memo, dict):
        memo = {"_parse_error": memo_err or "missing memo"}
    unesco_rel = expected_unesco_path(cid)
    ext_rel = expected_external_path(cid)
    return {
        "memo": memo,
        "validation_facts": case_validation_facts(agent_root, cid, memo),
        "unesco_snapshot_excerpt": path_text(agent_root, unesco_rel, 5000),
        "external_snapshot_excerpt": path_text(agent_root, ext_rel, 5000),
        "package_case_snippets": case_related_package_snippets(agent_root, cid, 5000),
    }


def deterministic_checks(agent_root: Path, manifest: dict[str, dict], ref_cases: dict[str, dict]) -> tuple[float, dict, list[str]]:
    notes: list[str] = []
    score = 0.0
    total = 0.0

    def add(condition: bool, weight: float, note: str):
        nonlocal score, total
        total += weight
        if condition:
            score += weight
        elif len(notes) < 240:
            notes.append(note)

    ids = sorted(manifest)
    expected_ids = set(ids)
    details = {
        "case_count": len(ids),
        "valid_memos": 0,
        "unesco_sources": 0,
        "external_sources": 0,
        "quote_checks_passed": 0,
        "quote_checks_total": 0,
        "retrieval_audit_rows": 0,
        "evidence_register_rows": 0,
        "package_slide_count": 0,
    }

    add((agent_root / "case_memos").is_dir(), 8, "missing case_memos directory")
    for name in PACKAGE_FILES:
        add((agent_root / name).exists(), 2, f"missing {name}")

    memos = {}
    for cid in ids:
        memo, err = load_json(agent_root / "case_memos" / f"{cid}.json")
        ok = isinstance(memo, dict)
        add(ok, 1.5, f"missing or invalid memo for {cid}: {err}")
        if not ok:
            continue
        memos[cid] = memo
        details["valid_memos"] += 1
        add(str(memo.get("case_id", "")) == cid, 0.4, f"{cid} memo has wrong case_id")
        add(str(memo.get("property_name", "")).strip() == manifest[cid].get("property_name", "").strip(), 0.4, f"{cid} memo property_name mismatch")
        add(isinstance(memo.get("curator_questions"), dict), 0.8, f"{cid} missing curator_questions object")
        add(isinstance(memo.get("external_context"), dict), 0.8, f"{cid} missing external_context object")

    for cid in ids:
        unesco_path = agent_root / expected_unesco_path(cid)
        ext_path = agent_root / expected_external_path(cid)
        unesco_text = read_text(unesco_path)
        ext_text = read_text(ext_path)
        unesco_ok = bool(unesco_text.strip()) and is_unesco_source(unesco_text)
        ext_url = first_independent_url(ext_text)
        ext_ok = bool(ext_text.strip()) and bool(ext_url)
        add(unesco_path.exists(), 1.0, f"{cid} missing UNESCO source snapshot")
        add(unesco_ok, 1.4, f"{cid} UNESCO source snapshot missing UNESCO URL/domain")
        add(ext_path.exists(), 1.0, f"{cid} missing external context source snapshot")
        add(ext_ok, 1.6, f"{cid} external source missing independent non-UNESCO/Wikimedia URL")
        details["unesco_sources"] += int(unesco_ok)
        details["external_sources"] += int(ext_ok)

    # Exact quote grounding for quotes explicitly requested or recorded by the output.
    def check_quote(cid: str, quote: str, source_rel: str, label: str, weight: float = 1.0):
        quote = str(quote or "").strip()
        if not quote:
            add(False, weight, f"{cid} missing quote for {label}")
            details["quote_checks_total"] += 1
            return
        source_text = path_text(agent_root, source_rel)
        ok = bool(source_text) and quote in source_text
        add(ok, weight, f"{cid} quote for {label} not exact substring of {source_rel}")
        details["quote_checks_total"] += 1
        details["quote_checks_passed"] += int(ok)

    for cid, memo in memos.items():
        check_quote(cid, memo.get("danger_quote", ""), expected_unesco_path(cid), "danger_quote", 1.3)
        ext = memo.get("external_context") if isinstance(memo.get("external_context"), dict) else {}
        check_quote(cid, ext.get("external_quote", ""), expected_external_path(cid), "external_context.external_quote", 1.3)
        cqs = memo.get("curator_questions") if isinstance(memo.get("curator_questions"), dict) else {}
        if ext.get("external_quote"):
            answer = str(cqs.get("what_external_context_changes", ""))
            add(str(ext.get("external_quote")) in answer, 0.8, f"{cid} public-context curator answer does not include saved external quote")
        for idx, item in enumerate(memo.get("claim_boundaries") or []):
            if isinstance(item, dict) and item.get("quoted_support"):
                src = agent_rel_path(item.get("source_path") or item.get("source_ref") or expected_unesco_path(cid))
                check_quote(cid, item.get("quoted_support"), src, f"claim_boundaries[{idx}].quoted_support", 0.4)

    audit, audit_err = load_json(agent_root / "retrieval_audit.json")
    audit_rows = audit_rows_from_loaded(audit)
    details["retrieval_audit_rows"] = len(audit_rows)
    add(bool(audit_rows), 3, f"retrieval_audit.json has no readable rows: {audit_err}")
    if audit_rows:
        pairs = set()
        for row in audit_rows:
            if isinstance(row, dict):
                cid = str(row.get("case_id", ""))
                st = str(row.get("source_type", "")).lower()
                pairs.add((cid, st))
                quote = str(row.get("retrieved_quote", "")).strip()
                rel = agent_rel_path(row.get("retrieved_source_path", ""))
                if quote and rel:
                    check_quote(cid, quote, rel, f"retrieval_audit.{st}", 0.15)
        expected_pairs = {(cid, st) for cid in ids for st in SOURCE_TYPES}
        add(expected_pairs.issubset(pairs), 5, "retrieval_audit does not cover every case/source pair")
        add(all(cid in expected_ids and st in SOURCE_TYPES for cid, st in pairs), 2, "retrieval_audit contains invalid case IDs or source types")

    register_rows = []
    register_path = agent_root / "evidence_register.csv"
    if register_path.exists():
        try:
            with register_path.open("r", encoding="utf-8", newline="") as handle:
                register_rows = list(csv.DictReader(handle))
        except Exception as exc:
            notes.append(f"evidence_register.csv invalid: {exc}")
    details["evidence_register_rows"] = len(register_rows)
    register_case_ids = [str(row.get("case_id", "")) for row in register_rows]
    register_ids = set(register_case_ids)
    add(len(register_rows) == len(ids), 4, "evidence_register.csv should contain exactly one row per listed case")
    add(register_ids == expected_ids and len(register_case_ids) == len(register_ids), 4, "evidence_register.csv does not cover each expected case exactly once")
    for row in register_rows:
        cid = str(row.get("case_id", ""))
        if cid not in expected_ids:
            add(False, 0.2, f"evidence_register has invalid case_id {cid}")
            continue
        if row.get("source_quote") and row.get("source_quote_path"):
            check_quote(cid, row.get("source_quote"), agent_rel_path(row.get("source_quote_path")), "evidence_register.source_quote", 0.12)
        if row.get("external_context_quote"):
            check_quote(cid, row.get("external_context_quote"), expected_external_path(cid), "evidence_register.external_context_quote", 0.12)

    package, package_err = load_json(agent_root / "storyboard_package.json")
    output, output_err = load_json(agent_root / "output.json")
    add(isinstance(package, dict), 5, f"storyboard_package.json invalid: {package_err}")
    add(isinstance(output, dict), 3, f"output.json invalid: {output_err}")
    if isinstance(package, dict) and isinstance(output, dict):
        add(package == output, 2, "output.json does not mirror storyboard_package.json")
    if isinstance(package, dict):
        slides = package.get("slides")
        if isinstance(slides, list):
            details["package_slide_count"] = len(slides)
        add(isinstance(slides, list) and len(slides) == 30, 5, "storyboard_package does not contain exactly 30 slides")
        decision_ids = []
        for key in ["lead_scene_ids", "supporting_scene_ids", "holdback_case_ids"]:
            vals = package.get(key)
            add(isinstance(vals, list), 1.5, f"storyboard_package missing list {key}")
            if isinstance(vals, list):
                decision_ids.extend(str(v) for v in vals)
        used_ids = set(decision_ids)
        add(used_ids.issubset(expected_ids), 3, "storyboard_package references invalid case IDs")
        add(used_ids == expected_ids and len(decision_ids) == len(used_ids), 3, "storyboard_package decision lists do not partition every listed case exactly once")
        add(all(key in package for key in ["evidence_table", "media_manifest", "risk_theme_index", "citation_appendix", "interpretation_risk_register"]), 4, "storyboard_package missing requested review/appendix sections")

    deterministic_score = score / total if total else 0.0
    details["deterministic_points"] = round(score, 3)
    details["deterministic_total"] = round(total, 3)
    return deterministic_score, details, notes


def judge_case(case_id: str, agent_root: Path, input_manifest: dict[str, dict], ref_cases: dict[str, dict], semantic_cases: dict[str, dict], reference_root: Path, cfg: dict) -> tuple[str, dict]:
    manifest_case = input_manifest.get(case_id, {})
    ref_case = ref_cases.get(case_id, {})
    payload = {
        "case_id": case_id,
        "property_name": manifest_case.get("property_name") or ref_case.get("property_name"),
        "official_unesco_start_url": manifest_case.get("official_unesco_start_url"),
        "task_curator_questions": CURATOR_QUESTIONS,
        "hidden_reference_context": {
            "state_party": ref_case.get("state_party_heading"),
            "danger_year": ref_case.get("danger_year"),
            "unesco_site_id": ref_case.get("unesco_site_id"),
            "unesco_reference_excerpt": short_reference_excerpt(reference_root, ref_case, int(cfg.get("llm_reference_excerpt_chars", 6500))),
            "source_derived_anchors": semantic_cases.get(case_id, {}),
        },
        "agent_output": shrink(read_case_payload(agent_root, case_id), int(cfg.get("llm_field_max_chars", 1400)), 12),
    }
    system = (
        "You are a strict but fair museum interpretation evaluator. Judge whether the agent's output satisfies the user task for one heritage case. "
        "Use the hidden UNESCO reference excerpt, source-derived anchors, saved-source excerpts, and validation_facts as evaluation context. Do not require exact wording or a gold answer. "
        "Reward real source-grounded meaning, complete curator-question answers, specific comparison between UNESCO and external context, exact evidence use, and cautious visual interpretation. "
        "Penalize generic template filling, invented or unsupported external context, quotes that validation_facts say are not exact saved-source substrings, missing direct public-source support, unsafe current access/travel claims, and answers that do not actually compare what the sources add or omit. "
        "A structurally complete memo with weak or fake semantics should score low. Do not punish harmless JSON formatting differences. "
        "Do not write analysis, prefaces, markdown, or explanations outside JSON. The first character of your response must be { and the last must be }. "
        "Return exactly this JSON shape: {\"score\": number, \"subscores\": object, \"reason\": string, \"major_issues\": array}."
    )
    rubric = {
        "score": "number from 0 to 1 for this case; reserve >=0.85 for case-specific, source-grounded, cautious work with strong curator-question coverage",
        "subscores": {
            "curator_question_coverage": "answers all seven required curator questions with substance, not placeholders",
            "source_grounding_and_quotes": "uses saved UNESCO and external-source evidence; exact quote validity should follow validation_facts",
            "source_comparison_and_tension": "explains what each source contributes, omits, or could distort if used alone",
            "external_public_context": "uses a credible independent public source for conservation/public interpretation/access/restriction/teaching context without trip-planning advice",
            "visual_caution_and_claim_boundaries": "distinguishes what visuals can show from what they cannot prove and states do-not-claim boundaries",
            "case_specificity": "uses concrete entities, risks, and details aligned with the real property rather than generic danger-list prose",
        },
        "reason": "short evidence-based explanation that mentions the decisive strengths or failures",
        "major_issues": ["list important failures, if any"],
    }
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": json.dumps({"rubric": rubric, "case_payload": payload}, ensure_ascii=False)},
    ]
    judged, err = fireworks_chat_json(messages, cfg, f"heritage-case-{case_id}", max_tokens=int(cfg.get("llm_case_max_tokens", 900)))
    if err or not isinstance(judged, dict):
        return case_id, {"score": 0.0, "reason": err or "invalid LLM judge response", "major_issues": ["llm_judge_failed"]}
    score = clamp01(judged.get("score"))
    judged["score"] = score
    return case_id, judged


def run_case_judges(agent_root: Path, manifest: dict[str, dict], ref_cases: dict[str, dict], semantic_cases: dict[str, dict], reference_root: Path, cfg: dict) -> dict:
    result = {
        "enabled": bool(cfg.get("llm_judge_enabled", True)),
        "available": bool(os.environ.get("FIREWORKS_API_KEY", "").strip()),
        "workers": int(cfg.get("llm_judge_workers", 8)),
        "case_scores": {},
        "average_score": 0.0,
        "notes": [],
    }
    if not result["enabled"]:
        result["notes"].append("LLM judge disabled")
        return result
    ids = sorted(manifest)
    max_cases = min(len(ids), int(cfg.get("llm_judge_max_cases", len(ids))))
    ids = ids[:max_cases]

    scores = []
    judge_ids = []
    for cid in ids:
        memo_path = agent_root / "case_memos" / f"{cid}.json"
        memo, memo_err = load_json(memo_path)
        if not isinstance(memo, dict):
            issue = memo_err or "missing memo"
            result["case_scores"][cid] = {
                "score": 0.0,
                "reason": f"Missing or invalid case memo: {issue}",
                "major_issues": ["missing_or_invalid_case_memo"],
                "llm_judge_skipped": True,
            }
            scores.append(0.0)
        else:
            judge_ids.append(cid)

    if not result["available"]:
        result["notes"].append("FIREWORKS_API_KEY not set; valid memos could not be semantically judged")
        for cid in judge_ids:
            result["case_scores"][cid] = {
                "score": 0.0,
                "reason": "FIREWORKS_API_KEY not set",
                "major_issues": ["llm_judge_unavailable"],
            }
            scores.append(0.0)
        result["average_score"] = sum(scores) / len(ids) if ids else 0.0
        return result

    workers = max(1, min(int(cfg.get("llm_judge_workers", 8)), len(judge_ids) or 1))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(judge_case, cid, agent_root, manifest, ref_cases, semantic_cases, reference_root, cfg): cid for cid in judge_ids}
        for fut in as_completed(futures):
            cid = futures[fut]
            try:
                case_id, judged = fut.result()
            except Exception as exc:
                case_id, judged = cid, {"score": 0.0, "reason": str(exc), "major_issues": ["judge_exception"]}
            result["case_scores"][case_id] = judged
            scores.append(clamp01(judged.get("score")))
    result["average_score"] = sum(scores) / len(ids) if ids else 0.0
    return result


def run_package_judge(agent_root: Path, manifest: dict[str, dict], cfg: dict) -> dict:
    result = {"enabled": bool(cfg.get("llm_judge_enabled", True)), "available": bool(os.environ.get("FIREWORKS_API_KEY", "").strip()), "score": 0.0, "reason": ""}
    if not result["enabled"]:
        result["reason"] = "LLM judge disabled"
        return result
    if not result["available"]:
        result["reason"] = "FIREWORKS_API_KEY not set"
        return result
    package, perr = load_json(agent_root / "storyboard_package.json")
    output, _ = load_json(agent_root / "output.json")
    evidence = read_text(agent_root / "evidence_register.csv", limit=int(cfg.get("llm_package_evidence_chars", 9000)))
    selection = read_text(agent_root / "selection_rationale.json", limit=int(cfg.get("llm_package_appendix_chars", 9000)))
    theme = read_text(agent_root / "theme_cluster_map.json", limit=int(cfg.get("llm_package_appendix_chars", 9000)))
    consistency = read_text(agent_root / "final_consistency_audit.json", limit=int(cfg.get("llm_package_appendix_chars", 9000)))
    payload = {
        "task_goal": "Judge the final 30-slide museum-style visual learning arc and board handoff package.",
        "expected_case_ids": sorted(manifest),
        "package_parse_error": perr,
        "storyboard_package_summary": summarize_package_for_judge(package, manifest),
        "storyboard_package_excerpt": read_text(agent_root / "storyboard_package.json", 12000),
        "output_matches_package": package == output if isinstance(package, dict) and isinstance(output, dict) else False,
        "evidence_register_excerpt": evidence,
        "selection_rationale_excerpt": selection,
        "theme_cluster_map_excerpt": theme,
        "final_consistency_audit_excerpt": consistency,
    }
    system = (
        "You are a strict museum-board package evaluator. Judge the overall final handoff, not individual case minutiae. "
        "Use storyboard_package_summary for complete structural facts; it includes all slide summaries and coverage counts, so do not infer missing slides from a truncated excerpt. "
        "Reward coherent synthesis, source-grounded caution, useful visual-learning arc, sensible clustering/selection rationale, citation/evidence consistency, and transparent limitations. "
        "Penalize missing case coverage, unsupported current access/travel/safety claims, inconsistent decision partitions, weak evidence appendices, and final-package claims that contradict retrieval limits. "
        "Do not require a gold answer and do not punish harmless JSON formatting differences. "
        "Do not write analysis, prefaces, markdown, or explanations outside JSON. The first character of your response must be { and the last must be }. "
        "Return exactly this JSON shape: {\"score\": number, \"reason\": string, \"major_issues\": array}."
    )
    rubric = {
        "score": "number from 0 to 1 for the final package",
        "criteria": [
            "30-slide learning arc is coherent and useful to a museum board; use actual_slide_count from the summary",
            "lead/support/holdback selections partition the expected cases and are justified by case evidence",
            "theme clustering and regional/risk balance are meaningful and case-specific",
            "citations, evidence rows, and risk registers cover the expected cases and support claims",
            "current public-context and access/safety claims are cautious and not trip-planning advice",
            "remaining limits, terminal retrieval failures, and revision risks are clearly summarized without hiding gaps",
        ],
        "reason": "short explanation",
        "major_issues": ["list important failures, if any"],
    }
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": json.dumps({"rubric": rubric, "package_payload": payload}, ensure_ascii=False)},
    ]
    judged, err = fireworks_chat_json(messages, cfg, "heritage-package-judge", max_tokens=int(cfg.get("llm_package_max_tokens", 1000)))
    if err or not isinstance(judged, dict):
        result["reason"] = err or "invalid LLM judge response"
        return result
    result.update(judged)
    result["score"] = clamp01(judged.get("score"))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-root", required=True)
    parser.add_argument("--input-root", required=True)
    parser.add_argument("--reference-root", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--reward-out", required=True)
    args = parser.parse_args()

    agent_root = Path(args.agent_root)
    input_root = Path(args.input_root)
    reference_root = Path(args.reference_root)
    cfg, cfg_err = load_json(Path(args.config))
    if cfg_err or not isinstance(cfg, dict):
        cfg = {}

    manifest = load_manifest(input_root)
    ref_cases, semantic_cases = load_reference(reference_root)
    if not manifest:
        reward = 0.0
        details = {"error": "source_manifest.json missing or invalid"}
    else:
        det_score, det_details, notes = deterministic_checks(agent_root, manifest, ref_cases)
        case_judge = run_case_judges(agent_root, manifest, ref_cases, semantic_cases, reference_root, cfg)
        package_judge = run_package_judge(agent_root, manifest, cfg)
        deterministic_weight = float(cfg.get("deterministic_weight", 0.30))
        case_weight = float(cfg.get("case_llm_weight", 0.55))
        package_weight = float(cfg.get("package_llm_weight", 0.15))
        total_weight = max(0.0001, deterministic_weight + case_weight + package_weight)
        reward = (
            deterministic_weight * det_score
            + case_weight * clamp01(case_judge.get("average_score"))
            + package_weight * clamp01(package_judge.get("score"))
        ) / total_weight
        details = {
            "reward": round(clamp01(reward), 6),
            "deterministic_score": round(det_score, 6),
            "case_llm_score": round(clamp01(case_judge.get("average_score")), 6),
            "package_llm_score": round(clamp01(package_judge.get("score")), 6),
            "weights": {
                "deterministic": deterministic_weight,
                "case_llm": case_weight,
                "package_llm": package_weight,
            },
            "deterministic_details": det_details,
            "deterministic_notes": notes[:80],
            "case_judge": case_judge,
            "package_judge": package_judge,
        }

    reward = clamp01(reward)
    out = Path(args.reward_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(f"{reward:.6f}\n", encoding="utf-8")
    details_path = out.parent / "verifier_details.json"
    details_path.write_text(json.dumps(details, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"reward": reward, "details_path": str(details_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
