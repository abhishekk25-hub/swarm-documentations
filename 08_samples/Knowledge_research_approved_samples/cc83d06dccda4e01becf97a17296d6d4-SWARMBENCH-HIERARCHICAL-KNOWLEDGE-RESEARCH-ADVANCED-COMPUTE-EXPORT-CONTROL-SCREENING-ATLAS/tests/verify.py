#!/usr/bin/env python3
"""llm-judge verifier - Advanced Compute Export-Control Screening Atlas.

Heavy deterministic grounding + minority W&B Qwen LLM checks. Fail-closed.
Never send temperature on judge requests (WANDB_Qwen_Vision_Verifier_Template).
"""
from __future__ import annotations

import csv
import gzip
import io
import json
import os
import re
import struct
import traceback
import zlib
from collections import Counter, defaultdict
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None

AGENT_DIR_CANONICAL = Path(os.environ.get("AGENT_OUTPUT_DIR", "/logs/agent"))
AGENT_CANDIDATES = [
    AGENT_DIR_CANONICAL,
    Path("/logs/agent"),
    Path("/workspace/logs/agent"),
    Path("logs/agent"),
    Path("/workspace"),
]
INPUT = Path("/input_artifacts")
if not INPUT.exists():
    INPUT = Path(__file__).resolve().parents[1] / "environment" / "input_artifacts"
VERIFIER = Path(os.environ.get("VERIFIER_OUTPUT_DIR", "/logs/verifier"))

COLUMNS = [
    "claim_id", "jurisdiction_id", "control_theme", "section_locator",
    "obligation_paraphrase", "evidence_quote", "control_class", "duty_actor",
    "licence_posture", "enduse_sensitivity", "control_tightness_score",
    "crosswalk_group_id", "note",
]
LEDGER_COLUMNS = [
    "conflict_id", "claim_id_a", "claim_id_b", "control_theme",
    "class_a", "class_b", "why_it_matters", "evidence_quote_a", "evidence_quote_b",
]
CONTROL_CLASSES = {
    "AUTHORIZATION_REQUIRED", "EXCEPTION_AVAILABLE", "SCREENING_DUTY",
    "DESTINATION_RESTRICTED", "CATCHALL_TRIGGER", "PROCEDURAL_DUTY",
    "PROHIBITION", "NOT_FOUND",
}
DUTY_ACTORS = {
    "EXPORTER", "BROKER", "END_USER", "LICENSING_AUTHORITY",
    "INTERNAL_COMPLIANCE", "UNSPECIFIED",
}
LICENCE_POSTURES = {
    "INDIVIDUAL_LICENCE", "GENERAL_LICENCE", "NO_LICENCE_IF_EXCEPTION",
    "PROHIBITED", "NOT_APPLICABLE", "UNKNOWN_NOT_FOUND",
}
ENDUSE = {"WMD_MILITARY", "GOVERNMENT_SECURE", "CIVILIAN_DUAL", "UNSPECIFIED", "NOT_APPLICABLE"}
DUTY_VERBS = re.compile(
    r"\b(shall|must|require|requires|required|prohibit|prohibits|authori[sz]e|"
    r"authori[sz]ation|licence|license|screen|screening|report|retain|apply|"
    r"notify|control|controls|restricted)\b", re.I)
CODE_PREFIX = re.compile(r"^(Art(icle)?|Sec(tion)?|§|Part|Chapter|Annex)\b", re.I)
_PARA_STOP = {
    "shall", "must", "require", "requires", "about", "under", "which", "their",
    "there", "these", "those", "where", "while", "would", "could", "should",
    "export", "exports", "control", "controls", "goods", "items", "technology",
}
_FETCH_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
_SOURCE_CACHE: dict[str, str] = {}
_LAST_INSTRUMENT_TEXTS: dict[str, str] = {}
_SHELL_MARKERS = (
    "unsupported browser",
    "please enable javascript",
    "javascript-fahigen",
    "javascript-fähigen",
    "nur mit einem javascript",
    "cf-browser-verification",
    "no-script-warning",
    "you are using an unsupported",
    "sign in / sign up",
    "site feedback",
)
_SUBSTANCE_MARKERS = (
    "export", "licence", "license", "authoris", "authoriz", "munition",
    "dual-use", "dual use", "scomet", "itar", "permit", "control",
    "brokering", "end-user", "end user", "strategic",
)

LLM_CHECKS = [
    "Each jurisdiction_arc is specific to that jurisdiction's own rows and not a reused template.",
    "Reconciliation notes for multi-jurisdiction crosswalk groups honestly describe class disagreements where they exist.",
    "The briefing regime_comparison is true of the matrix and does not invent control classes.",
    "recommended_actions are concrete shipment-desk instructions that follow from the matrix rather than generic trade slogans.",
    "Conflict ledger rows name real claim_ids and explain a specific cross-regime overclaim risk.",
    "Notes on substantive rows show regime-specific reading rather than one skeleton with IDs swapped.",
    "The package does not treat an exception path as if it were a prohibition, or a screening duty as if it authorised unrestricted export.",
    "A trade-compliance desk could act on this atlas as delivered: conclusions follow from matrix rows and nothing material is asserted without a row behind it.",
]


def resolve_agent_dir() -> Path:
    for p in AGENT_CANDIDATES:
        if (p / "export_screening_matrix.csv").exists():
            return p
    for p in AGENT_CANDIDATES:
        if p.exists():
            return p
    return AGENT_DIR_CANONICAL


def load_catalog():
    data = json.loads((INPUT / "claim_catalog.json").read_text(encoding="utf-8"))
    claims = {c["claim_id"]: c for c in data["claims"]}
    return data, claims


def _norm(s: str) -> str:
    s = (s or "").lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def word_count(s: str) -> int:
    return len(re.findall(r"[A-Za-z0-9']+", s or ""))


def title_case_ratio(s: str) -> float:
    words = re.findall(r"[A-Za-z][A-Za-z']*", s or "")
    if len(words) < 3:
        return 1.0
    return sum(1 for w in words if w[:1].isupper()) / float(len(words))


def is_substantive_obligation(row: dict) -> bool:
    f = (row.get("obligation_paraphrase") or "").strip()
    q = (row.get("evidence_quote") or "").strip()
    if len(f) < 25 or len(re.findall(r"[A-Za-z]+", f)) < 6:
        return False
    nf, nq = _norm(f), _norm(q)
    if not nf or nf == nq or (nq and nf in nq):
        return False
    if CODE_PREFIX.search(f) or not DUTY_VERBS.search(f):
        return False
    if title_case_ratio(f) >= 0.60:
        return False
    words = q.split()
    if not (12 <= len(words) <= 60) or title_case_ratio(q) >= 0.60:
        return False
    return True


def tightness_recompute(row: dict) -> int:
    cls = (row.get("control_class") or "").strip().upper()
    lic = (row.get("licence_posture") or "").strip().upper()
    end = (row.get("enduse_sensitivity") or "").strip().upper()
    actor = (row.get("duty_actor") or "").strip().upper()
    if cls == "NOT_FOUND":
        return 0
    class_w = {
        "EXCEPTION_AVAILABLE": 0, "PROCEDURAL_DUTY": 1, "SCREENING_DUTY": 2,
        "AUTHORIZATION_REQUIRED": 2, "DESTINATION_RESTRICTED": 2, "CATCHALL_TRIGGER": 2,
        "PROHIBITION": 3,
    }.get(cls, 0)
    lic_w = {
        "NO_LICENCE_IF_EXCEPTION": 0, "GENERAL_LICENCE": 1, "INDIVIDUAL_LICENCE": 2,
        "PROHIBITED": 3, "NOT_APPLICABLE": 0, "UNKNOWN_NOT_FOUND": 0,
    }.get(lic, 0)
    end_w = {
        "CIVILIAN_DUAL": 0, "UNSPECIFIED": 1, "GOVERNMENT_SECURE": 2,
        "WMD_MILITARY": 3, "NOT_APPLICABLE": 0,
    }.get(end, 0)
    actor_w = 0 if actor in ("", "UNSPECIFIED") else 1
    return min(10, class_w + lic_w + end_w + actor_w)


def quote_round_trips(quote: str, source_text: str) -> bool:
    """Full-quote coverage: the normalised quote must appear in full.

    This is an EXACT normalised substring match (``q in s``).  There is no
    fuzzy fallback or word-ratio tolerance.  ``_norm()`` lowercases and
    collapses non-alphanumeric characters, so minor punctuation and case
    differences are absorbed, but every word must be present in order.

    NOTE: ``_quote_window()`` below is a *separate* helper used only to
    locate the region around a quote for downstream window-based checks;
    it is never called by this function and does not affect the pass/fail
    grounding decision.
    """
    s, q = _norm(source_text), _norm(quote)
    if not q or not s or len(q.split()) < 12:
        return False
    return q in s  # exact normalised substring — no fuzzy fallback


def _quote_window(quote: str, source_text: str, radius: int = 500) -> str:
    s, q = _norm(source_text), _norm(quote)
    if not s or not q:
        return ""
    pos = s.find(q)
    if pos < 0:
        words = q.split()
        for n in (min(24, len(words)), 16, 12):
            if len(words) < n:
                continue
            for i in range(0, len(words) - n + 1):
                pos = s.find(" ".join(words[i:i + n]))
                if pos >= 0:
                    break
            if pos >= 0:
                break
    if pos < 0:
        return ""
    return s[max(0, pos - radius): pos + len(q) + radius]


def paraphrase_near_quote(paraphrase: str, quote: str, source_text: str) -> bool:
    """Paraphrase must be structurally distinct from the quote AND grounded.

    A paraphrase that is a lightly reworded near-verbatim copy of the quote
    is rejected: token-Jaccard similarity between paraphrase and quote must
    fall below 0.35 so the analyst's own wording is genuinely different.
    """
    window = _quote_window(quote, source_text)
    if not window:
        return False
    # Reject light rewording: Jaccard cap 0.35 forces genuine rephrasing.
    if _token_jaccard(paraphrase, quote) >= 0.35:
        return False
    terms = [w for w in re.findall(r"[a-z]{5,}", _norm(paraphrase)) if w not in _PARA_STOP]
    if len(terms) < 3:
        return False
    uniq = list(dict.fromkeys(terms))
    hits = sum(1 for t in uniq if t in window)
    return hits / float(len(uniq)) >= 0.55


_LOCATOR_STOP = {
    "look", "for", "the", "and", "about", "section", "passage", "text", "instrument",
    "export", "control", "controls", "locate", "named", "would", "apply", "advanced",
    "compute", "accelerators", "servers", "related", "controlled", "technology",
}


def _token_jaccard(a: str, b: str) -> float:
    ta = set(re.findall(r"[a-z0-9]{4,}", _norm(a)))
    tb = set(re.findall(r"[a-z0-9]{4,}", _norm(b)))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / float(len(ta | tb))


def _comparative_sentence_count(text: str, jurisdiction_ids: set[str]) -> int:
    """Count sentences that compare two named matrix jurisdictions."""
    comparative = re.compile(
        r"\b(?:more|less|tighter|looser|stricter|broader|narrower|higher|lower|"
        r"stronger|weaker|than|versus|vs\.?|compared|relative|unlike|whereas|"
        r"exceeds|below|above|ranks?)\b", re.I)
    count = 0
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        found = {
            jid for jid in jurisdiction_ids
            if re.search(rf"(?<![A-Za-z0-9_]){re.escape(jid)}(?![A-Za-z0-9_])",
                         sentence, re.I)
        }
        if len(found) >= 2 and comparative.search(sentence):
            count += 1
    return count


def quote_is_claim_specific(quote: str, source_text: str, meta: dict) -> bool | None:
    blob = " ".join([
        str(meta.get("locator_hint") or ""),
        str(meta.get("focus_prompt") or ""),
        str(meta.get("control_theme") or "").replace("_", " "),
    ])
    terms = []
    for w in re.findall(r"[A-Za-z][A-Za-z\-]{4,}", blob.lower()):
        w = w.strip("-")
        if w not in _LOCATOR_STOP and w not in terms:
            terms.append(w)
    terms = terms[:12]
    if len(terms) < 2:
        return None
    window = _quote_window(quote, source_text)
    if not window:
        return None
    return any(t in window for t in terms)


def _strip_html(text: str) -> str:
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text)


def _looks_like_js_challenge(status: int, content: bytes, ctype: str) -> bool:
    if status in (202, 403) and len(content) < 8000:
        return True
    low = content[:4000].lower()
    return (
        b"cf-browser-verification" in low
        or b"please enable javascript" in low
        or b"unsupported browser" in low
        or b"no-script-warning" in low
        or b"javascript-fahigen" in low
        or "javascript-fähigen".encode("utf-8") in low
    )


def _is_chrome_or_empty_shell(text: str) -> bool:
    """Reject SPA chrome / JS notices that are long enough to clear a naive length floor."""
    if not text or len(text) < 500:
        return True
    low = text.lower()
    shell_hits = sum(1 for m in _SHELL_MARKERS if m in low)
    substance_hits = sum(1 for m in _SUBSTANCE_MARKERS if m in low)
    # Long chrome-only eCFR shells carry Sign In / Site Feedback / unsupported browser
    # and almost none of the regulatory markers.
    if shell_hits >= 2 and substance_hits < 3:
        return True
    if "no-script-warning" in low and substance_hits < 3:
        return True
    if "unsupported browser" in low and "munition" not in low and "itar" not in low:
        return True
    return False


def _fetch_url(url: str) -> str:
    """Network fetch intentionally disabled for deterministic verifier scoring."""
    if url in _SOURCE_CACHE:
        return _SOURCE_CACHE[url]
    text = ""
    _SOURCE_CACHE[url] = text
    return text


def _oracle_texts() -> dict[str, str]:
    out = {}
    here = Path(__file__).resolve().parent
    for name in ("partial_oracle.json.gz", "partial_oracle.json"):
        path = here / name
        if not path.exists():
            continue
        try:
            if name.endswith(".gz"):
                with gzip.open(path, "rt", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = json.loads(path.read_text(encoding="utf-8"))
            for iid, rec in (data.get("instruments") or {}).items():
                txt = rec.get("normalised_text") or ""
                if txt:
                    out[iid] = txt
        except Exception:
            pass
        break
    return out


def fetch_jurisdiction_text(jid: str, url: str, fallbacks: list[str] | None = None) -> str:
    """Return pinned verifier source text for deterministic scoring.

    Agents still fetch the public source_url values live while solving. The
    verifier's deterministic quote/window checks must be reproducible across
    grading runs, so correctness is decided against the task-build snapshot in
    partial_oracle.json.gz rather than against mutable live web pages.
    """
    return _oracle_texts().get(jid, "")


# --- PNG helpers (stdlib only) ---

def _png_scanlines(path):
    try:
        raw = path.read_bytes()
    except Exception:
        return None
    if not raw.startswith(b"\x89PNG\r\n\x1a\n"):
        return None
    pos, idat, palette = 8, bytearray(), b""
    width = height = bitd = colort = interlace = None
    while pos + 8 <= len(raw):
        ln = struct.unpack(">I", raw[pos:pos + 4])[0]
        typ = raw[pos + 4:pos + 8]
        data = raw[pos + 8:pos + 8 + ln]
        pos += 12 + ln
        if typ == b"IHDR" and len(data) >= 13:
            width, height, bitd, colort, _, _, interlace = struct.unpack(">IIBBBBB", data[:13])
        elif typ == b"PLTE":
            palette = data
        elif typ == b"IDAT":
            idat += data
        elif typ == b"IEND":
            break
    if not width or not height or bitd != 8 or interlace:
        return None
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(colort)
    if channels is None:
        return None
    try:
        buf = zlib.decompress(bytes(idat))
    except Exception:
        return None
    stride = width * channels
    if len(buf) < (stride + 1) * height:
        return None
    rows, prev, off = [], bytearray(stride), 0
    for _ in range(height):
        f = buf[off]
        off += 1
        line = bytearray(buf[off:off + stride])
        off += stride
        if f == 1:
            for i in range(channels, stride):
                line[i] = (line[i] + line[i - channels]) & 0xFF
        elif f == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif f == 3:
            for i in range(stride):
                a = line[i - channels] if i >= channels else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 0xFF
        elif f == 4:
            for i in range(stride):
                a = line[i - channels] if i >= channels else 0
                b = prev[i]
                c = prev[i - channels] if i >= channels else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 0xFF
        rows.append(bytes(line))
        prev = line
    return width, height, channels, colort, palette, rows


def _png_ink_and_signature(path):
    dec = _png_scanlines(path)
    if dec is None:
        return None
    width, height, channels, colort, palette, rows = dec
    ystep = max(1, height // 200)
    xstep = max(1, width // 200)
    cell_sum = [0] * 64
    cell_n = [0] * 64
    cell_ink = [0] * 64
    ink = total = 0
    for y in range(0, height, ystep):
        line = rows[y]
        gy = min(7, y * 8 // height)
        for x in range(0, width, xstep):
            if colort == 3:
                o = line[x] * 3
                if o + 3 > len(palette):
                    continue
                r, g, b = palette[o], palette[o + 1], palette[o + 2]
            else:
                o = x * channels
                if channels >= 3:
                    r, g, b = line[o], line[o + 1], line[o + 2]
                else:
                    r = g = b = line[o]
            lum = (r * 299 + g * 587 + b * 114) // 1000
            cell = gy * 8 + min(7, x * 8 // width)
            cell_sum[cell] += lum
            cell_n[cell] += 1
            total += 1
            if lum < 235:
                ink += 1
                cell_ink[cell] += 1
    if not total:
        return None
    sig = tuple((cell_sum[i] // cell_n[i] // 8) if cell_n[i] else 0 for i in range(64))
    return {"ink_share": ink / float(total), "cells_with_ink": sum(1 for i in range(64) if cell_ink[i] > 0),
            "signature": sig}


def _png_series_profile(path: Path, bins: int) -> list[float]:
    dec = _png_scanlines(path)
    if dec is None or bins <= 0:
        return []
    width, height, channels, colort, palette, rows = dec
    x0, x1 = int(width * 0.08), int(width * 0.98)
    y0, y1 = int(height * 0.12), int(height * 0.86)
    if x1 <= x0 or y1 <= y0:
        return []
    profiles = []
    for b in range(bins):
        xa = x0 + (x1 - x0) * b // bins
        xb = x0 + (x1 - x0) * (b + 1) // bins
        ink_rows = []
        for y in range(y0, y1, max(1, (y1 - y0) // 80)):
            line = rows[y]
            hit = False
            for x in range(xa, max(xa + 1, xb), max(1, (xb - xa) // 20)):
                if colort == 3:
                    o = line[x] * 3
                    if o + 3 > len(palette):
                        continue
                    r, g, b_ = palette[o], palette[o + 1], palette[o + 2]
                else:
                    o = x * channels
                    if channels >= 3:
                        r, g, b_ = line[o], line[o + 1], line[o + 2]
                    else:
                        r = g = b_ = line[o]
                if (r * 299 + g * 587 + b_ * 114) // 1000 < 220:
                    hit = True
                    break
            if hit:
                ink_rows.append(y)
        if not ink_rows:
            profiles.append(0.0)
        else:
            profiles.append(1.0 - ((min(ink_rows) - y0) / float(max(1, y1 - y0))))
    return profiles


def _series_values(data: dict) -> list[float]:
    if not isinstance(data, dict) or not data:
        return []
    try:
        items = sorted(((str(k), float(v)) for k, v in data.items() if float(v) > 0),
                       key=lambda kv: kv[0])
    except Exception:
        return []
    return [v for _, v in items]


def _profile_correlates(profile: list[float], values: list[float]) -> bool:
    if len(profile) < 2 or len(values) < 2:
        return False
    # resample values to profile length
    n = len(profile)
    resampled = []
    for i in range(n):
        j = min(len(values) - 1, int(i * len(values) / float(n)))
        resampled.append(values[j])
    if max(resampled) <= 0 or max(profile) <= 0:
        return False
    pv = [p / max(profile) for p in profile]
    rv = [v / max(resampled) for v in resampled]
    mean_p = sum(pv) / n
    mean_r = sum(rv) / n
    num = sum((pv[i] - mean_p) * (rv[i] - mean_r) for i in range(n))
    den_p = sum((pv[i] - mean_p) ** 2 for i in range(n)) ** 0.5
    den_r = sum((rv[i] - mean_r) ** 2 for i in range(n)) ** 0.5
    if den_p < 1e-9 or den_r < 1e-9:
        return False
    return (num / (den_p * den_r)) >= 0.35


def png_content_report(paths, chart_data: dict) -> dict:
    problems, sigs = [], {}
    series_map = {
        "control_class_distribution.png": chart_data.get("control_class_counts") or {},
        "tightness_score_histogram.png": chart_data.get("tightness_score_histogram") or {},
        "theme_coverage_by_jurisdiction.png": chart_data.get("theme_coverage_by_jurisdiction") or {},
        "conflict_density.png": chart_data.get("conflict_density") or {},
    }
    for p in paths:
        if not p.exists():
            problems.append(f"{p.name}: missing")
            continue
        m = _png_ink_and_signature(p)
        if m is None:
            problems.append(f"{p.name}: not a readable 8-bit PNG")
            continue
        if m["ink_share"] < 0.01 or m["cells_with_ink"] < 8:
            problems.append(f"{p.name}: blank or near-blank")
            continue
        vals = _series_values(series_map.get(p.name, {}))
        if vals:
            prof = _png_series_profile(p, max(2, len(vals)))
            if not _profile_correlates(prof, vals):
                problems.append(f"{p.name}: pixel profile does not correlate with chart_data series")
                continue
        sigs[p.name] = m["signature"]
    names = sorted(sigs)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            if sigs[names[i]] == sigs[names[j]]:
                problems.append(f"{names[i]} and {names[j]} are the same image")
    return {
        "ok": not problems and len(sigs) == len(list(paths)),
        "reason": "; ".join(problems) if problems else f"{len(sigs)} distinct plots correlated to chart_data",
    }


def _mean_score(rows):
    vals = []
    for r in rows:
        try:
            vals.append(int(float(str(r.get("control_tightness_score", "")).strip())))
        except Exception:
            continue
    return round(sum(vals) / float(len(vals)), 4) if vals else None


def run_deterministic(agent: Path, catalog: dict, claims: dict) -> list[dict]:
    global _LAST_INSTRUMENT_TEXTS
    results = []

    def check(name, passed, reason="", kind="content"):
        results.append({"name": name, "passed": bool(passed), "reason": reason, "kind": kind})

    matrix_path = agent / "export_screening_matrix.csv"
    rows = []
    cols = []
    if matrix_path.exists():
        try:
            with matrix_path.open(encoding="utf-8", errors="ignore", newline="") as f:
                rdr = csv.DictReader(f)
                cols = list(rdr.fieldnames or [])
                rows = list(rdr)
        except Exception:
            rows, cols = [], []

    check("export_screening_matrix.csv exists with the required columns",
          cols == COLUMNS, f"got {cols}", kind="structural")

    by_id = {}
    for r in rows:
        cid = (r.get("claim_id") or "").strip()
        if cid and cid not in by_id:
            by_id[cid] = r
    check("matrix carries one row per catalog claim with no duplicates",
          len(by_id) == len(claims) and len(rows) == len(by_id),
          f"unique={len(by_id)} rows={len(rows)} catalog={len(claims)}", kind="structural")

    # Catalog identity cross-check
    id_ok = theme_ok = 0
    for cid, meta in claims.items():
        r = by_id.get(cid)
        if not r:
            continue
        if (r.get("jurisdiction_id") or "").strip() == meta.get("jurisdiction_id"):
            id_ok += 1
        if (r.get("control_theme") or "").strip() == meta.get("control_theme"):
            theme_ok += 1
    check("row jurisdiction_id matches the catalog assignment for each claim_id",
          id_ok == len(claims), f"{id_ok}/{len(claims)}", kind="structural")
    check("row control_theme matches the catalog assignment for each claim_id",
          theme_ok == len(claims), f"{theme_ok}/{len(claims)}", kind="structural")

    vocab_ok = 0
    for r in by_id.values():
        if ((r.get("control_class") or "").strip().upper() in CONTROL_CLASSES
                and (r.get("duty_actor") or "").strip().upper() in DUTY_ACTORS
                and (r.get("licence_posture") or "").strip().upper() in LICENCE_POSTURES
                and (r.get("enduse_sensitivity") or "").strip().upper() in ENDUSE):
            vocab_ok += 1
    check("all four controlled columns use only their closed vocabularies",
          by_id and vocab_ok == len(by_id), f"{vocab_ok}/{len(by_id)}", kind="structural")

    # Fetch texts
    inst_meta = catalog.get("jurisdictions") or {}
    inst_text = {}
    for jid, meta in inst_meta.items():
        inst_text[jid] = fetch_jurisdiction_text(
            jid, meta.get("url") or "", meta.get("fallbacks") or [])
    _LAST_INSTRUMENT_TEXTS = dict(inst_text)
    resolved = {i for i, t in inst_text.items() if len(t) >= 500}
    check("all ten jurisdictions resolved for grounding",
          len(resolved) == 10, f"resolved {sorted(resolved)}", kind="structural")

    # Catalog-faithful rows only enter grounded pool
    faithful = []
    for cid, r in by_id.items():
        meta = claims.get(cid, {})
        if ((r.get("jurisdiction_id") or "").strip() == meta.get("jurisdiction_id")
                and (r.get("control_theme") or "").strip() == meta.get("control_theme")):
            faithful.append(r)

    substantive = [r for r in faithful if is_substantive_obligation(r)]
    grounded, quote_checked, quote_hits = [], 0, 0
    on_topic = on_topic_checked = 0
    para_ok = 0
    seen_quotes: dict[tuple[str, str], list[str]] = defaultdict(list)
    quote_reuse_bad = []
    for r in substantive:
        jid = (r.get("jurisdiction_id") or "").strip()
        src = inst_text.get(jid, "")
        if len(src) < 500:
            continue
        quote = r.get("evidence_quote") or ""
        quote_checked += 1
        if quote_round_trips(quote, src):
            quote_hits += 1
            grounded.append(r)
            meta = claims.get((r.get("claim_id") or "").strip(), {})
            theme = (r.get("control_theme") or meta.get("control_theme") or "").strip()
            key = (jid, theme)
            for old in seen_quotes[key]:
                if _token_jaccard(quote, old) >= 0.80:
                    quote_reuse_bad.append((key, (r.get("claim_id") or "").strip()))
                    break
            seen_quotes[key].append(quote)
            v = quote_is_claim_specific(quote, src, meta)
            if v is not None:
                on_topic_checked += 1
                if v:
                    on_topic += 1
            if paraphrase_near_quote(r.get("obligation_paraphrase") or "", quote, src):
                para_ok += 1

    obligation_reuse_bad = []
    seen_paraphrases = []
    for r in grounded:
        paraphrase = (r.get("obligation_paraphrase") or "").strip()
        if not paraphrase:
            continue
        cid = (r.get("claim_id") or "").strip()
        for old_cid, old_paraphrase in seen_paraphrases:
            if _token_jaccard(paraphrase, old_paraphrase) >= 0.80:
                obligation_reuse_bad.append((old_cid, cid))
                break
        seen_paraphrases.append((cid, paraphrase))

    grounded_share = len(grounded) / float(len(claims) or 1)
    quote_rate = (quote_hits / quote_checked) if quote_checked else 0.0
    on_topic_rate = (on_topic / on_topic_checked) if on_topic_checked else 0.0
    para_rate = (para_ok / len(grounded)) if grounded else 0.0

    check("at least 80 grounded obligation rows (substantive AND full-quote round-trips)",
          len(grounded) >= 80, f"{len(grounded)}", kind="content")
    check("at least 120 grounded obligation rows",
          len(grounded) >= 120, f"{len(grounded)}", kind="content")
    check("grounded_share (grounded/catalog) >= 0.50",
          grounded_share >= 0.50, f"{grounded_share:.3f}", kind="content")
    check("quotes full-cover round-trip on >=50% of substantive rows",
          quote_checked > 0 and quote_rate >= 0.50, f"{quote_rate:.2f}", kind="content")
    check("quotes full-cover round-trip on >=70% of substantive rows",
          quote_checked > 0 and quote_rate >= 0.70, f"{quote_rate:.2f}", kind="content")
    check("quotes full-cover round-trip on >=85% of substantive rows",
          quote_checked > 0 and quote_rate >= 0.85, f"{quote_rate:.2f}", kind="content")
    check("quotes sit in the passage the claim names, not just somewhere in the instrument",
          on_topic_checked > 0 and on_topic_rate >= 0.70 and not quote_reuse_bad,
          f"{on_topic}/{on_topic_checked}; near-duplicate quotes={quote_reuse_bad[:5]}",
          kind="content")
    check("paraphrases are grounded near their evidence_quote window on >=70% of grounded rows",
          grounded and para_rate >= 0.70, f"{para_rate:.2f}", kind="content")
    check("grounded obligation paraphrases are not near-duplicates across rows",
          not obligation_reuse_bad,
          f"near_duplicate_pairs={obligation_reuse_bad[:5]}", kind="content")

    score_hits = 0
    for r in grounded:
        try:
            got = int(float(str(r.get("control_tightness_score", "")).strip()))
        except Exception:
            got = -1
        if got == tightness_recompute(r):
            score_hits += 1
    score_rate = (score_hits / len(grounded)) if grounded else 0.0
    check("control_tightness_score recomputes on >=80% of grounded rows",
          bool(grounded) and score_rate >= 0.80, f"{score_hits}/{len(grounded)}", kind="content")
    check("control_tightness_score recomputes on >=95% of grounded rows",
          bool(grounded) and score_rate >= 0.95, f"{score_rate:.2f}", kind="content")

    # Classifications must leave a footprint in the quote window, not only vocab+arith.
    class_checked = class_hits = 0
    for r in grounded:
        jid = (r.get("jurisdiction_id") or "").strip()
        v = class_compatible_with_window(r, inst_text.get(jid, ""))
        if v is None:
            continue
        class_checked += 1
        if v:
            class_hits += 1
    class_rate = (class_hits / class_checked) if class_checked else 0.0
    check("declared control_class is compatible with the quote window on >=90% of grounded rows",
          class_checked > 0 and class_rate >= 0.90,
          f"{class_hits}/{class_checked}", kind="content")

    # --- QD-10.5 grounding: licence_posture AND enduse_sensitivity AND duty_actor ---
    # These three classification sub-fields are each checked against the fetched
    # instrument text via field_compatible_with_window(), which uses the
    # FIELD_FOOTPRINTS lookup table.  This is NOT vocabulary-membership-only;
    # each declared value must leave a value-specific keyword footprint within
    # ±250 chars of the evidence_quote position in the real source.
    licence_checked = licence_hits = 0
    enduse_checked = enduse_hits = 0
    duty_actor_checked = duty_actor_hits = 0
    for r in grounded:
        jid = (r.get("jurisdiction_id") or "").strip()
        src = inst_text.get(jid, "")
        v = field_compatible_with_window(r, src, "licence_posture")
        if v is not None:
            licence_checked += 1
            if v:
                licence_hits += 1
        v = field_compatible_with_window(r, src, "enduse_sensitivity")
        if v is not None:
            enduse_checked += 1
            if v:
                enduse_hits += 1
        v = field_compatible_with_window(r, src, "duty_actor")
        if v is not None:
            duty_actor_checked += 1
            if v:
                duty_actor_hits += 1
    licence_rate = (licence_hits / licence_checked) if licence_checked else 0.0
    enduse_rate = (enduse_hits / enduse_checked) if enduse_checked else 0.0
    duty_actor_rate = (duty_actor_hits / duty_actor_checked) if duty_actor_checked else 0.0
    check("declared licence_posture is compatible with the quote window on >=90% of grounded rows",
          licence_checked > 0 and licence_rate >= 0.90,
          f"{licence_hits}/{licence_checked}", kind="content")
    check("declared enduse_sensitivity is compatible with the quote window on >=90% of grounded rows",
          enduse_checked > 0 and enduse_rate >= 0.90,
          f"{enduse_hits}/{enduse_checked}", kind="content")
    check("declared duty_actor is compatible with the quote window on >=90% of grounded rows",
          duty_actor_checked > 0 and duty_actor_rate >= 0.90,
          f"{duty_actor_hits}/{duty_actor_checked}", kind="content")

    # Finished-row quality checks: a row should not count as useful solely because
    # a quote round-trips. It also needs internally consistent scoring, a row-specific
    # note, and classification fields that leave footprints near the quote.
    recomputed_rows = []
    note_quality_rows = []
    recomputed_note_rows = []
    recomputed_note_paraphrase_rows = []
    compat2_rows = []
    compat3_rows = []
    quality_grounded_rows = []
    strongest_rows = []
    for r in grounded:
        jid = (r.get("jurisdiction_id") or "").strip()
        src = inst_text.get(jid, "")
        quote = r.get("evidence_quote") or ""
        try:
            got = int(float(str(r.get("control_tightness_score", "")).strip()))
        except Exception:
            got = -1
        recomputed = got == tightness_recompute(r)
        note = (r.get("note") or "").strip()
        note_quality = word_count(note) >= 8 and title_case_ratio(note) < 0.60
        paraphrase_quality = paraphrase_near_quote(
            r.get("obligation_paraphrase") or "", quote, src)
        field_values = [
            class_compatible_with_window(r, src),
            field_compatible_with_window(r, src, "licence_posture"),
            field_compatible_with_window(r, src, "enduse_sensitivity"),
            field_compatible_with_window(r, src, "duty_actor"),
        ]
        observed_fields = [v for v in field_values if v is not None]
        field_hits = sum(1 for v in observed_fields if v)
        compat2 = len(observed_fields) >= 2 and field_hits >= 2
        compat3 = len(observed_fields) >= 3 and field_hits >= 3
        if recomputed:
            recomputed_rows.append(r)
        if note_quality:
            note_quality_rows.append(r)
        if recomputed and note_quality:
            recomputed_note_rows.append(r)
        if recomputed and note_quality and paraphrase_quality:
            recomputed_note_paraphrase_rows.append(r)
        if compat2:
            compat2_rows.append(r)
        if compat3:
            compat3_rows.append(r)
        if recomputed and note_quality and compat2:
            quality_grounded_rows.append(r)
        if recomputed and note_quality and paraphrase_quality and compat3:
            strongest_rows.append(r)

    recomputed_j = {(r.get("jurisdiction_id") or "").strip() for r in recomputed_rows}
    note_themes = {(r.get("control_theme") or "").strip() for r in note_quality_rows}
    recomputed_note_paraphrase_j = {
        (r.get("jurisdiction_id") or "").strip() for r in recomputed_note_paraphrase_rows}
    recomputed_note_paraphrase_themes = {
        (r.get("control_theme") or "").strip() for r in recomputed_note_paraphrase_rows}
    quality_j = {(r.get("jurisdiction_id") or "").strip() for r in quality_grounded_rows}
    quality_themes = {(r.get("control_theme") or "").strip() for r in quality_grounded_rows}
    strongest_j = {(r.get("jurisdiction_id") or "").strip() for r in strongest_rows}
    strongest_themes = {(r.get("control_theme") or "").strip() for r in strongest_rows}
    check("at least 10 grounded rows have recomputable tightness scores",
          len(recomputed_rows) >= 10, f"{len(recomputed_rows)}", kind="content")
    check("at least 25 grounded rows have recomputable tightness scores",
          len(recomputed_rows) >= 25, f"{len(recomputed_rows)}", kind="content")
    check("at least 35 grounded rows have recomputable tightness scores",
          len(recomputed_rows) >= 35, f"{len(recomputed_rows)}", kind="content")
    check("recomputable grounded rows span at least 4 jurisdictions",
          len([j for j in recomputed_j if j]) >= 4,
          f"{sorted(j for j in recomputed_j if j)}", kind="content")
    check("at least 10 grounded rows carry substantive row-specific notes",
          len(note_quality_rows) >= 10, f"{len(note_quality_rows)}", kind="content")
    check("at least 20 grounded rows carry substantive row-specific notes",
          len(note_quality_rows) >= 20, f"{len(note_quality_rows)}", kind="content")
    check("substantive grounded notes span at least 10 control themes",
          len([t for t in note_themes if t]) >= 10,
          f"{len([t for t in note_themes if t])}", kind="content")
    check("substantive grounded notes span at least 14 control themes",
          len([t for t in note_themes if t]) >= 14,
          f"{len([t for t in note_themes if t])}", kind="content")
    check("at least 10 grounded rows combine recomputable scores with substantive notes",
          len(recomputed_note_rows) >= 10, f"{len(recomputed_note_rows)}", kind="content")
    check("at least 20 grounded rows combine recomputable scores with substantive notes",
          len(recomputed_note_rows) >= 20, f"{len(recomputed_note_rows)}", kind="content")
    check("at least 15 grounded rows have two source-compatible classification footprints",
          len(compat2_rows) >= 15, f"{len(compat2_rows)}", kind="content")
    check("at least 20 grounded rows have two source-compatible classification footprints",
          len(compat2_rows) >= 20, f"{len(compat2_rows)}", kind="content")
    check("at least 10 grounded rows have three source-compatible classification footprints",
          len(compat3_rows) >= 10, f"{len(compat3_rows)}", kind="content")
    check("at least 13 grounded rows have three source-compatible classification footprints",
          len(compat3_rows) >= 13, f"{len(compat3_rows)}", kind="content")
    check("at least 5 quality-grounded rows combine quote, recomputed score, note, and field footprints",
          len(quality_grounded_rows) >= 5, f"{len(quality_grounded_rows)}", kind="content")
    check("at least 10 quality-grounded rows combine quote, recomputed score, note, and field footprints",
          len(quality_grounded_rows) >= 10, f"{len(quality_grounded_rows)}", kind="content")
    check("at least 14 quality-grounded rows combine quote, recomputed score, note, and field footprints",
          len(quality_grounded_rows) >= 14, f"{len(quality_grounded_rows)}", kind="content")
    check("quality-grounded rows span at least 4 jurisdictions",
          len([j for j in quality_j if j]) >= 4,
          f"{sorted(j for j in quality_j if j)}", kind="content")
    check("quality-grounded rows span at least 8 control themes",
          len([t for t in quality_themes if t]) >= 8,
          f"{len([t for t in quality_themes if t])}", kind="content")
    check("at least 3 strongest rows add grounded paraphrases to quality-grounded evidence",
          len(strongest_rows) >= 3, f"{len(strongest_rows)}", kind="content")
    check("at least 6 grounded rows combine recomputable scores, substantive notes, and grounded paraphrases",
          len(recomputed_note_paraphrase_rows) >= 6,
          f"{len(recomputed_note_paraphrase_rows)}", kind="content")
    check("rows combining recomputable scores, substantive notes, and grounded paraphrases span at least 4 jurisdictions",
          len([j for j in recomputed_note_paraphrase_j if j]) >= 4,
          f"{sorted(j for j in recomputed_note_paraphrase_j if j)}", kind="content")
    check("rows combining recomputable scores, substantive notes, and grounded paraphrases span at least 6 control themes",
          len([t for t in recomputed_note_paraphrase_themes if t]) >= 6,
          f"{len([t for t in recomputed_note_paraphrase_themes if t])}", kind="content")
    check("strongest quality rows span at least 2 jurisdictions",
          len([j for j in strongest_j if j]) >= 2,
          f"{sorted(j for j in strongest_j if j)}", kind="content")
    check("strongest quality rows span at least 3 control themes",
          len([t for t in strongest_themes if t]) >= 3,
          f"{len([t for t in strongest_themes if t])}", kind="content")
    check("quality-grounded rows span at least 5 jurisdictions",
          len([j for j in quality_j if j]) >= 5,
          f"{sorted(j for j in quality_j if j)}", kind="content")

    # QD-10.6: note column must show real per-row reading, not blank/templated stubs.
    note_ok = 0
    notes = []
    for r in grounded:
        note = (r.get("note") or "").strip()
        notes.append(note)
        if word_count(note) >= 8 and title_case_ratio(note) < 0.60:
            note_ok += 1
    note_rate = (note_ok / len(grounded)) if grounded else 0.0
    note_dup = 0
    for i, a in enumerate(notes):
        if word_count(a) < 8:
            continue
        for b in notes[i + 1:i + 8]:
            if word_count(b) >= 8 and _token_jaccard(a, b) >= 0.90:
                note_dup += 1
                break
    check("substantive notes appear on >=60% of grounded rows with limited near-duplicates",
          grounded and note_rate >= 0.60 and note_dup <= max(3, len(grounded) // 10),
          f"rate={note_rate:.2f} near_dup_rows={note_dup}", kind="content")

    j_sub = Counter((r.get("jurisdiction_id") or "").strip() for r in grounded)
    check("at least 8 jurisdictions have >=8 grounded rows each",
          sum(1 for c in j_sub.values() if c >= 8) >= 8, str(dict(j_sub)), kind="content")
    check("all 10 jurisdictions have grounded rows in the matrix",
          set(j_sub) >= set(inst_meta), str(sorted(j_sub)), kind="content")

    xw_groups, xw_themes = defaultdict(set), defaultdict(set)
    xw_quotes = defaultdict(list)
    for r in grounded:
        xw = (r.get("crosswalk_group_id") or "").strip()
        if xw and xw.upper() != "XW-NONE":
            xw_groups[xw].add((r.get("jurisdiction_id") or "").strip())
            xw_themes[xw].add((r.get("control_theme") or "").strip())
            xw_quotes[xw].append(r.get("evidence_quote") or "")
    multi = sum(1 for insts in xw_groups.values() if len(insts) >= 2)
    coherent = sum(1 for xw, insts in xw_groups.items()
                   if len(insts) >= 2 and len(xw_themes[xw]) == 1)
    check("at least 12 multi-jurisdiction crosswalk groups over grounded rows",
          multi >= 12, f"{multi}", kind="content")
    check("multi-jurisdiction crosswalk groups hold a single control_theme each",
          multi > 0 and (coherent / multi) >= 0.80, f"{coherent}/{multi}", kind="content")

    # QD-10.4: reject pure theme-bucketing (XW-<theme> or one quote stamped across regimes).
    mechanical = 0
    diverse = 0
    for xw, insts in xw_groups.items():
        if len(insts) < 2:
            continue
        themes = xw_themes[xw]
        theme = next(iter(themes)) if len(themes) == 1 else ""
        theme_slug = theme.replace("_", "").lower()
        xw_slug = re.sub(r"[^a-z0-9]", "", xw.lower())
        if theme and (theme.lower() in xw.lower() or theme_slug == xw_slug.replace("xw", "")):
            mechanical += 1
            continue
        qs = [q for q in xw_quotes[xw] if word_count(q) >= 12]
        distinct = 0
        for i, a in enumerate(qs):
            if all(_token_jaccard(a, b) < 0.80 for b in qs[:i]):
                distinct += 1
        if distinct >= 2:
            diverse += 1
        else:
            mechanical += 1
    multi_n = max(1, multi)
    check("multi-jurisdiction crosswalk groups carry distinct regime quotes, not theme-label buckets",
          multi > 0 and (diverse / multi_n) >= 0.50,
          f"diverse={diverse} mechanical={mechanical} multi={multi}", kind="content")

    # Deliverables
    atlas_path = agent / "jurisdiction_control_atlas.json"
    ledger_path = agent / "exception_conflict_ledger.csv"
    chart_data_path = agent / "chart_data.json"
    out_path = agent / "counsel_briefing.json"
    charts = [
        "control_class_distribution.png", "tightness_score_histogram.png",
        "theme_coverage_by_jurisdiction.png", "conflict_density.png",
    ]

    atlas = {}
    if atlas_path.exists():
        try:
            atlas = json.loads(atlas_path.read_text(encoding="utf-8"))
        except Exception:
            atlas = {"_error": True}

    rows_by_j = defaultdict(list)
    for r in by_id.values():
        rows_by_j[(r.get("jurisdiction_id") or "").strip()].append(r)

    dk_j = atlas.get("jurisdictions") if isinstance(atlas.get("jurisdictions"), list) else []
    inst_agree = 0
    for entry in dk_j:
        jid = (entry.get("jurisdiction_id") or "").strip()
        rs = rows_by_j.get(jid) or []
        if not rs:
            continue
        try:
            count_ok = int(entry.get("claims_reviewed") or 0) == len(rs)
        except Exception:
            count_ok = False
        want_fc = Counter((r.get("control_class") or "").strip().upper() for r in rs
                          if (r.get("control_class") or "").strip())
        got_fc = entry.get("control_class_counts") or {}
        try:
            fc_ok = {k.upper(): int(v) for k, v in got_fc.items() if int(v)} == dict(want_fc)
        except Exception:
            fc_ok = False
        want_mean = _mean_score(rs)
        try:
            mean_ok = want_mean is not None and abs(float(entry.get("mean_tightness_score")) - want_mean) <= 0.05
        except Exception:
            mean_ok = False
        arc_wc = word_count(str(entry.get("jurisdiction_arc") or ""))
        arc_ok = 80 <= arc_wc <= 180
        if count_ok and fc_ok and mean_ok and arc_ok:
            inst_agree += 1

    matrix_group_claims = defaultdict(set)
    matrix_group_j = defaultdict(set)
    for r in by_id.values():
        xw = (r.get("crosswalk_group_id") or "").strip()
        if xw and xw.upper() != "XW-NONE":
            matrix_group_claims[xw].add((r.get("claim_id") or "").strip())
            matrix_group_j[xw].add((r.get("jurisdiction_id") or "").strip())
    dk_groups = atlas.get("crosswalk_groups") if isinstance(atlas.get("crosswalk_groups"), list) else []
    grp_agree = 0
    for entry in dk_groups:
        xw = (entry.get("crosswalk_group_id") or "").strip()
        if not xw or xw not in matrix_group_claims:
            continue
        claims_ok = set(entry.get("claim_ids") or []) == matrix_group_claims[xw]
        j_ok = set(entry.get("jurisdictions_covered") or []) == matrix_group_j[xw]
        if claims_ok and j_ok:
            grp_agree += 1
    atlas_ok = (len(dk_j) >= 8 and inst_agree >= 8
                and len(dk_groups) >= 8 and grp_agree == len(dk_groups))
    check("atlas reconciles with the matrix (per-jurisdiction figures and crosswalk groups)",
          atlas_ok, f"jurisdictions={inst_agree}/{len(dk_j)} groups={grp_agree}/{len(dk_groups)}",
          kind="content")

    led_cols, led_rows = [], []
    if ledger_path.exists():
        try:
            with ledger_path.open(encoding="utf-8", errors="ignore", newline="") as lf:
                lr = csv.DictReader(lf)
                led_cols = list(lr.fieldnames or [])
                led_rows = list(lr)
        except Exception:
            led_cols, led_rows = [], []
    check("exception_conflict_ledger.csv carries the rulebook columns in order",
          led_cols == LEDGER_COLUMNS, f"got {led_cols}", kind="structural")

    traced_pairs = set()
    for lr_row in led_rows:
        a = (lr_row.get("claim_id_a") or "").strip()
        b = (lr_row.get("claim_id_b") or "").strip()
        if not a or not b or a == b or a not in by_id or b not in by_id:
            continue
        fa = (lr_row.get("class_a") or "").strip().upper()
        fb = (lr_row.get("class_b") or "").strip().upper()
        if fa == fb:
            continue
        if fa != (by_id[a].get("control_class") or "").strip().upper():
            continue
        if fb != (by_id[b].get("control_class") or "").strip().upper():
            continue
        if len((lr_row.get("why_it_matters") or "").strip()) < 40:
            continue
        traced_pairs.add(tuple(sorted((a, b))))
    check("conflict ledger has >=3 distinct disagreeing claim pairs that trace to the matrix",
          len(traced_pairs) >= 3, f"{len(traced_pairs)} distinct pairs", kind="content")

    chart_data = {}
    if chart_data_path.exists():
        try:
            chart_data = json.loads(chart_data_path.read_text(encoding="utf-8"))
        except Exception:
            chart_data = {}

    want_force = Counter((r.get("control_class") or "").strip().upper() for r in by_id.values()
                         if (r.get("control_class") or "").strip())
    got_force = chart_data.get("control_class_counts") or {}
    try:
        force_match = {k.upper(): int(v) for k, v in got_force.items()} == dict(want_force)
    except Exception:
        force_match = False
    want_hist = Counter()
    for r in by_id.values():
        try:
            want_hist[int(float(str(r.get("control_tightness_score", "")).strip()))] += 1
        except Exception:
            continue
    got_hist = chart_data.get("tightness_score_histogram") or {}
    try:
        hist_match = ({int(k): int(v) for k, v in got_hist.items() if int(v)}
                      == {k: v for k, v in want_hist.items() if v})
    except Exception:
        hist_match = False
    want_topic = {jid: len({(r.get("control_theme") or "").strip()
                            for r in rs if (r.get("control_theme") or "").strip()})
                  for jid, rs in rows_by_j.items() if jid}
    got_topic = chart_data.get("theme_coverage_by_jurisdiction") or {}
    try:
        topic_match = {str(k): int(v) for k, v in got_topic.items()} == \
                      {str(k): int(v) for k, v in want_topic.items()}
    except Exception:
        topic_match = False
    want_density = Counter()
    for xw, js in matrix_group_j.items():
        if len(js) >= 2:
            themes = {(r.get("control_theme") or "").strip()
                      for r in by_id.values()
                      if (r.get("crosswalk_group_id") or "").strip() == xw}
            for t in themes:
                if t:
                    want_density[t] += 1
    got_density = chart_data.get("conflict_density") or {}
    try:
        density_match = ({str(k): int(v) for k, v in got_density.items() if int(v)}
                         == {str(k): int(v) for k, v in want_density.items() if v})
    except Exception:
        density_match = False
    check("chart_data series equal the matrix (class counts and tightness histogram)",
          force_match and hist_match, f"force={force_match} hist={hist_match}", kind="content")
    check("chart_data theme-coverage and conflict-density series equal the matrix",
          topic_match and density_match, f"topic={topic_match} density={density_match}", kind="content")

    missing_png = [n for n in charts if not (agent / n).exists() or (agent / n).stat().st_size < 2000]
    png_report = png_content_report([agent / n for n in charts], chart_data)
    check("the four PNGs are distinct plots whose content correlates with chart_data",
          png_report["ok"], png_report["reason"], kind="content")

    briefing = {}
    if out_path.exists():
        try:
            briefing = json.loads(out_path.read_text(encoding="utf-8"))
        except Exception:
            briefing = {}

    absent = []
    if not atlas_path.exists() or "_error" in atlas:
        absent.append("jurisdiction_control_atlas.json")
    if not ledger_path.exists():
        absent.append("exception_conflict_ledger.csv")
    if not out_path.exists() or not briefing:
        absent.append("counsel_briefing.json")
    absent.extend(missing_png)
    check("all deliverable files are present, parse, and are non-trivial",
          not absent, f"missing/unparseable: {absent}", kind="structural")

    try:
        brief_count_ok = int(briefing.get("claims_reviewed") or 0) in (len(claims), len(by_id))
    except Exception:
        brief_count_ok = False
    want_brief_fc = Counter((r.get("control_class") or "").strip().upper() for r in by_id.values()
                            if (r.get("control_class") or "").strip())
    got_brief_fc = briefing.get("control_class_counts")
    try:
        brief_fc_ok = (isinstance(got_brief_fc, dict)
                       and {k.upper(): int(v) for k, v in got_brief_fc.items() if int(v)}
                       == dict(want_brief_fc))
    except Exception:
        brief_fc_ok = False
    want_brief_mean = _mean_score(list(by_id.values()))
    try:
        brief_mean_ok = (want_brief_mean is not None
                         and abs(float(briefing.get("mean_tightness_score")) - want_brief_mean) <= 0.05)
    except Exception:
        brief_mean_ok = False
    check("briefing headline figures reconcile with the matrix (count, class counts, mean score)",
          brief_count_ok and brief_fc_ok and brief_mean_ok,
          f"count={brief_count_ok} force={brief_fc_ok} mean={brief_mean_ok}", kind="content")

    j_in_matrix = {(r.get("jurisdiction_id") or "").strip() for r in by_id.values() if (r.get("jurisdiction_id") or "").strip()}
    got_js = briefing.get("jurisdictions_covered")
    js_ok = isinstance(got_js, list) and {str(i).strip() for i in got_js} == j_in_matrix and len(j_in_matrix) >= 2

    by_theme = defaultdict(list)
    for r in by_id.values():
        t = (r.get("control_theme") or "").strip()
        if t:
            by_theme[t].append(r)
    theme_means = {t: m for t, rs in by_theme.items() if (m := _mean_score(rs)) is not None}
    ranked = [t for t, _ in sorted(theme_means.items(), key=lambda kv: -kv[1])]
    top_band = set(ranked[:max(5, len(ranked) // 3)])
    got_top = briefing.get("highest_tightness_themes")
    top_names = [_norm(str(t)) for t in got_top] if isinstance(got_top, list) else []
    top_real = [t for t in top_names if any(_norm(k) == t for k in theme_means)]
    top_in_band = [t for t in top_real if any(_norm(k) == t for k in top_band)]
    top_ok = (2 <= len(top_names) <= 8 and len(top_real) == len(top_names)
              and len(top_in_band) >= max(2, (len(top_names) + 1) // 2))
    check("briefing highest_tightness_themes are real themes that really do score highest",
          top_ok and js_ok, f"{len(top_in_band)}/{len(top_names)} jurisdictions_covered={js_ok}",
          kind="content")

    # QD-10.3: Conflicted jurisdiction pairs MUST have actual class disagreement.
    # The inner loop below explicitly compares control_class values between
    # jurisdiction pairs within each crosswalk group.  A pair (ja, jb) only
    # enters the 'meets' set when at least one row-pair shares the same
    # control_theme but has DIFFERENT control_class values (class_a != class_b
    # on line below).  This is NOT co-membership-only.
    meets = set()
    for xw, js in matrix_group_j.items():
        if not xw or len(js) < 2:
            continue
        group_rows = [r for r in by_id.values()
                      if (r.get("crosswalk_group_id") or "").strip() == xw]
        ordered = sorted(i for i in js if i)
        for a in range(len(ordered)):
            for b in range(a + 1, len(ordered)):
                ja, jb = ordered[a], ordered[b]
                collision = False
                for ra in group_rows:
                    if (ra.get("jurisdiction_id") or "").strip() != ja:
                        continue
                    theme_a = (ra.get("control_theme") or "").strip()
                    class_a = (ra.get("control_class") or "").strip().upper()
                    if not theme_a or not class_a:
                        continue
                    for rb in group_rows:
                        if (rb.get("jurisdiction_id") or "").strip() != jb:
                            continue
                        theme_b = (rb.get("control_theme") or "").strip()
                        class_b = (rb.get("control_class") or "").strip().upper()
                        if theme_a == theme_b and class_a and class_b and class_a != class_b:
                            collision = True
                            break
                    if collision:
                        break
                if collision:
                    meets.add((ja, jb))
    got_pairs = briefing.get("most_conflicted_jurisdiction_pairs")
    pair_items = got_pairs if isinstance(got_pairs, list) else []
    pairs_real = 0
    for item in pair_items:
        if isinstance(item, dict):
            blob = " ".join(str(v) for v in item.values())
        elif isinstance(item, (list, tuple)):
            blob = " ".join(str(v) for v in item)
        else:
            blob = str(item)
        found = sorted({i for i in j_in_matrix if i and i.lower() in blob.lower()})
        if len(found) >= 2 and any((found[a], found[b]) in meets
                                   for a in range(len(found))
                                   for b in range(a + 1, len(found))):
            pairs_real += 1
    check("briefing conflicted jurisdiction pairs are real shared-theme class collisions",
          2 <= len(pair_items) <= 8 and pairs_real == len(pair_items),
          f"{pairs_real}/{len(pair_items)}", kind="content")

    fam_text = str(briefing.get("regime_comparison") or "")
    fam_wc = word_count(fam_text)
    present = {f for f in want_brief_fc if f and f != "NOT_FOUND"}
    named = sum(1 for f in present if f.replace("_", " ").lower() in fam_text.lower()
                or f.lower() in fam_text.lower())
    need_named = min(len(present), max(2, len(present) - 1))
    check("briefing regime_comparison is 150-300 words and names classes the matrix contains",
          150 <= fam_wc <= 300 and len(present) >= 2 and named >= need_named
          and _comparative_sentence_count(fam_text, j_in_matrix) >= 2,
          f"words={fam_wc} named={named}/{len(present)} "
          f"comparative_sentences={_comparative_sentence_count(fam_text, j_in_matrix)}",
          kind="content")

    actions = briefing.get("recommended_actions") if isinstance(
        briefing.get("recommended_actions"), list) else []
    act_texts = [str(a).strip() for a in actions if str(a).strip()]
    long_enough = [a for a in act_texts if len(a) >= 40]
    action_reuse_bad = []
    for i, current in enumerate(long_enough):
        for previous in long_enough[:i]:
            if _token_jaccard(current, previous) >= 0.60:
                action_reuse_bad.append((previous, current))
                break
    check("briefing has 3-5 substantive, non-duplicated recommended_actions",
          3 <= len(act_texts) <= 5 and len(long_enough) == len(act_texts)
          and not action_reuse_bad,
          f"{len(act_texts)} actions near_duplicate_pairs={action_reuse_bad[:3]}",
          kind="content")

    summary = str(briefing.get("summary") or "")
    check("briefing summary exists and is at most 200 words",
          20 <= word_count(summary) <= 200, f"words={word_count(summary)}", kind="content")

    # Path check: when /logs/agent exists as a directory in this environment, the submission
    # must live there. Local offline harnesses that never mount /logs/agent are not failed
    # for using a recovery candidate; Cloud Run always has the canonical mount.
    canonical_present = AGENT_DIR_CANONICAL.exists()
    check("outputs were written under the canonical /logs/agent directory",
          (not canonical_present) or str(agent.resolve()) == str(AGENT_DIR_CANONICAL.resolve()),
          f"used {agent}; canonical_present={canonical_present}", kind="structural")

    results.append({
        "name": "_metrics",
        "passed": True,
        "reason": json.dumps({
            "substantive": len(substantive),
            "grounded_share": round(grounded_share, 4),
            "multi_crosswalk": multi,
            "jurisdiction_sub": dict(j_sub),
            "recomputable_grounded_rows": len(recomputed_rows),
            "substantive_note_rows": len(note_quality_rows),
            "recomputed_note_rows": len(recomputed_note_rows),
            "recomputed_note_paraphrase_rows": len(recomputed_note_paraphrase_rows),
            "classification_compat2_rows": len(compat2_rows),
            "classification_compat3_rows": len(compat3_rows),
            "quality_grounded_rows": len(quality_grounded_rows),
            "strongest_quality_rows": len(strongest_rows),
            "quality_grounded_jurisdictions": sorted(j for j in quality_j if j),
            "quality_grounded_theme_count": len([t for t in quality_themes if t]),
            "strongest_quality_jurisdictions": sorted(j for j in strongest_j if j),
            "strongest_quality_theme_count": len([t for t in strongest_themes if t]),
            "agent_dir_used": str(agent),
            "agent_dir_is_canonical": str(agent) == str(AGENT_DIR_CANONICAL),
        }),
        "kind": "meta",
    })
    return results


# --- W&B judge (no temperature) ---

PROVIDERS = [
    ("WANDB_API_KEY", "https://api.inference.wandb.ai/v1"),
    ("FIREWORKS_API_KEY", "https://api.fireworks.ai/inference/v1"),
    ("OPENAI_API_KEY", "https://api.openai.com/v1"),
    ("MOONSHOT_API_KEY", "https://api.moonshot.ai/v1"),
]
# Qwen leads (W&B template + independence from agent Kimi family). Bare kimi-k2.6 is
# Moonshot-direct only and sits last so a rollback still grades.
AGENT_FAMILY_HINTS = ("kimi", "moonshot")
JUDGE_MODELS = [m.strip() for m in os.environ.get("JUDGE_MODEL", "").split(",") if m.strip()] or [
    "Qwen/Qwen3.6-35B-A3B",
    "deepseek-ai/DeepSeek-V4-Flash",
    "zai-org/GLM-5.2",
    "openai/gpt-oss-120b",
    "moonshotai/Kimi-K2.6",
    "kimi-k2.6",
]
JUDGE_CALL_TIMEOUT = 180
_CLIENT_WHY = "not yet attempted"
_MODEL_WHY = "not yet attempted"
_MODEL_CAPS: dict[str, dict] = {}
_THINKING_OFF_MODELS = {"kimi-k2.6", "kimi-k2.5"}
_CAP_HINTS = (
    ("thinking_off", ("thinking",)),
    ("json_mode", ("response_format", "json_object", "json mode")),
)


def _provider():
    key = os.environ.get("GRADER_API_KEY")
    if key:
        return key, os.environ.get("GRADER_BASE_URL", PROVIDERS[0][1]), "GRADER_API_KEY"
    for env_name, url in PROVIDERS:
        k = os.environ.get(env_name)
        if k:
            return k, os.environ.get("GRADER_BASE_URL", url), env_name
    return None, None, None


def _caps(model: str) -> dict:
    if model not in _MODEL_CAPS:
        _MODEL_CAPS[model] = {
            "thinking_off": model in _THINKING_OFF_MODELS or model.startswith("kimi-"),
            "json_mode": True,
        }
    return dict(_MODEL_CAPS[model])


def _demote(model: str, err: Exception) -> bool:
    msg = str(err).lower()
    caps = _MODEL_CAPS.get(model)
    if not caps:
        return False
    for cap, words in _CAP_HINTS:
        if caps.get(cap) and any(w in msg for w in words):
            caps[cap] = False
            return True
    return False


def _req(model: str, messages: list, budget: int, json_mode: bool = True) -> dict:
    c = _caps(model)
    kw = {"model": model, "messages": messages, "max_tokens": budget, "timeout": JUDGE_CALL_TIMEOUT}
    # Never send temperature (W&B template).
    if c["json_mode"] and json_mode:
        kw["response_format"] = {"type": "json_object"}
    if c["thinking_off"]:
        kw["extra_body"] = {"thinking": {"type": "disabled"}}
    return kw


def _create(cli, model, messages, budget, json_mode=True):
    last = None
    for _ in range(len(_CAP_HINTS) + 1):
        try:
            return cli.chat.completions.create(**_req(model, messages, budget, json_mode))
        except Exception as e:
            last = e
            if not _demote(model, e):
                raise
    raise last


def _client():
    global _CLIENT_WHY
    key, base_url, name = _provider()
    if not key:
        _CLIENT_WHY = "no grader API key exported"
        return None
    try:
        from openai import OpenAI
        cli = OpenAI(base_url=base_url, api_key=key, timeout=JUDGE_CALL_TIMEOUT, max_retries=2)
    except Exception as e:
        _CLIENT_WHY = f"client build failed: {e!r}"
        return None
    _CLIENT_WHY = f"available ({name} -> {base_url})"
    return cli


def _resolve_model(cli):
    global _MODEL_WHY
    tried = []
    for m in JUDGE_MODELS:
        try:
            _create(cli, m, [{"role": "user", "content": "ok"}], 1, json_mode=False)
            _MODEL_WHY = f"resolved to {m}"
            return m
        except Exception as e:
            tried.append(f"{m}:{type(e).__name__}")
    _MODEL_WHY = "no model answered; " + "; ".join(tried)
    return None


def _message_text(resp) -> str:
    try:
        msg = resp.choices[0].message
    except Exception:
        return ""
    for attr in ("content", "reasoning_content", "reasoning"):
        val = getattr(msg, attr, None)
        if isinstance(val, str) and val.strip():
            return val
    return ""


def _extract_json_object(raw: str) -> dict:
    """Parse provider JSON even when it is wrapped in fences or short prose."""
    text = (raw or "").strip()
    if not text:
        raise ValueError("empty judge response")
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I).strip()
        text = re.sub(r"\s*```$", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start:end + 1])
        raise


def _safe_model_name(model: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", model or "unknown")[:80]


FIELD_FOOTPRINTS = {
    "control_class": {
        "AUTHORIZATION_REQUIRED": (
            "licence", "license", "authoris", "authoriz", "permit", "approval required",
            "shall not export", "must obtain",
        ),
        "EXCEPTION_AVAILABLE": (
            "exception", "exemption", "general licence", "general license", "ogel",
            "simplified", "open general",
        ),
        "SCREENING_DUTY": (
            "end-user", "end user", "denied", "screen", "screening", "due diligence",
            "know your customer",
        ),
        "DESTINATION_RESTRICTED": (
            "destination", "embargo", "country", "territory", "prohibited destination",
            "restricted destination",
        ),
        "CATCHALL_TRIGGER": (
            "catch-all", "catchall", "catch all", "unlisted", "not listed", "may be used",
        ),
        "PROCEDURAL_DUTY": (
            "record", "report", "retain", "application", "apply for", "notify", "register",
            "compliance programme", "compliance program",
        ),
        "PROHIBITION": (
            "prohibit", "prohibition", "offence", "offense", "unlawful", "shall not", "ban",
        ),
    },
    "licence_posture": {
        "INDIVIDUAL_LICENCE": (
            "licence", "license", "authoris", "authoriz", "permit", "approval",
            "application", "must obtain", "shall not export",
        ),
        "GENERAL_LICENCE": (
            "general licence", "general license", "open general", "global licence",
            "global license", "license exception", "licence exception",
        ),
        "NO_LICENCE_IF_EXCEPTION": (
            "exception", "exemption", "no licence", "no license", "not required",
            "does not require", "licence is not required", "license is not required",
        ),
        "PROHIBITED": (
            "prohibit", "prohibition", "shall not", "unlawful", "offence", "offense", "ban",
        ),
    },
    "enduse_sensitivity": {
        "WMD_MILITARY": (
            "military", "weapon", "weapons", "wmd", "nuclear", "missile", "chemical",
            "biological", "defence", "defense", "armed forces",
        ),
        "GOVERNMENT_SECURE": (
            "government", "public security", "intelligence", "security", "surveillance",
            "law enforcement", "police", "cybersecurity", "cyber security",
        ),
        "CIVILIAN_DUAL": (
            "dual use", "dual-use", "civil", "civilian", "commercial", "industrial",
            "listed", "specified", "computer", "integrated circuit",
        ),
    },
    # QD-10.5: duty_actor footprints ground the actor field against source text,
    # not just vocabulary membership.
    "duty_actor": {
        "EXPORTER": (
            "exporter", "exporting", "applicant", "shipper", "consignor", "seller",
            "person who exports", "party exporting",
        ),
        "BROKER": (
            "broker", "brokering", "intermediary", "arranger", "agent", "facilitator",
            "third party",
        ),
        "END_USER": (
            "end-user", "end user", "ultimate consignee", "recipient", "buyer",
            "consignee", "final user",
        ),
        "LICENSING_AUTHORITY": (
            "authority", "minister", "secretary", "government", "department",
            "competent authority", "designated authority",
        ),
        "INTERNAL_COMPLIANCE": (
            "compliance", "icp", "internal", "officer", "compliance officer",
            "compliance programme", "compliance program",
        ),
    },
}


def field_compatible_with_window(row: dict, source_text: str, field: str) -> bool | None:
    """Declared classification fields must leave a value-specific footprint near the quote.

    The window radius is 250 characters either side of the quote position,
    tight enough to require the footprint term to sit close to the evidence
    rather than anywhere in the instrument.
    """
    value = (row.get(field) or "").strip().upper()
    if value in ("", "NOT_FOUND", "NOT_APPLICABLE", "UNKNOWN_NOT_FOUND", "UNSPECIFIED"):
        return None
    hints = FIELD_FOOTPRINTS.get(field, {}).get(value, ())
    if not hints:
        return None
    window = _quote_window(row.get("evidence_quote") or "", source_text, radius=250)
    if not window:
        return False
    return any(h in window for h in hints)


def class_compatible_with_window(row: dict, source_text: str) -> bool | None:
    return field_compatible_with_window(row, source_text, "control_class")


def matrix_spread(path: Path, want_rows: int | None = None) -> str:
    """Feed the judge an honest view of the matrix.

    Prefer the full matrix with truncated cells. If the CSV is huge, take a
    content-hash-seeded random sample covering every jurisdiction rather than a
    fixed stride that an agent could game.
    """
    import hashlib
    import random

    try:
        with path.open(encoding="utf-8", errors="ignore", newline="") as fh:
            rdr = csv.reader(fh)
            header = next(rdr, None)
            rows = list(rdr)
    except Exception:
        return ""
    if header is None:
        return ""
    raw = path.read_bytes() if path.exists() else b""
    # Cap payload: keep all rows when small; otherwise random sample seeded by content.
    max_rows = want_rows if want_rows is not None else 180
    if len(rows) > max_rows:
        seed = int(hashlib.sha256(raw).hexdigest()[:16], 16)
        rng = random.Random(seed)
        # Stratify by jurisdiction column if present.
        try:
            j_idx = header.index("jurisdiction_id")
        except ValueError:
            j_idx = None
        if j_idx is not None:
            by_j = defaultdict(list)
            for r in rows:
                if len(r) > j_idx:
                    by_j[r[j_idx]].append(r)
            picked = []
            per = max(1, max_rows // max(1, len(by_j)))
            for bucket in by_j.values():
                rng.shuffle(bucket)
                picked.extend(bucket[:per])
            rng.shuffle(picked)
            rows = picked[:max_rows]
        else:
            rng.shuffle(rows)
            rows = rows[:max_rows]
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    for r in rows:
        w.writerow([str(c)[:220] for c in r])
    return buf.getvalue()


def fetched_instrument_evidence(agent: Path, limit_per_j: int = 1800) -> dict:
    """Compact source-text evidence for the LLM judge, keyed by jurisdiction."""
    rows = []
    path = agent / "export_screening_matrix.csv"
    if path.exists():
        try:
            with path.open(encoding="utf-8", errors="ignore", newline="") as fh:
                rows = list(csv.DictReader(fh))
        except Exception:
            rows = []
    quotes_by_j = defaultdict(list)
    for r in rows:
        jid = (r.get("jurisdiction_id") or "").strip()
        quote = (r.get("evidence_quote") or "").strip()
        if jid and quote and len(quotes_by_j[jid]) < 8:
            quotes_by_j[jid].append(quote)

    out = {}
    for jid, text in sorted(_LAST_INSTRUMENT_TEXTS.items()):
        if len(text) < 500:
            continue
        chunks = []
        for quote in quotes_by_j.get(jid, []):
            window = _quote_window(quote, text, radius=300)
            if not window:
                continue
            if any(_token_jaccard(window, old) >= 0.85 for old in chunks):
                continue
            chunks.append(window[:700])
            if sum(len(c) for c in chunks) >= limit_per_j:
                break
        if not chunks:
            chunks = [text[:limit_per_j]]
        out[jid] = {
            "source_chars": len(text),
            "raw_independent_instrument_excerpt": text[:1200],
            "source_excerpt_or_quote_windows": chunks,
        }
    return out


def call_llm_judge(agent: Path, det_results: list[dict]):
    status = {
        "grader_key": _provider()[2],
        "grader_base_url": _provider()[1],
        "judged_checks_total": len(LLM_CHECKS),
        "judged_checks_scored": 0,
        "endpoint_template": "https://api.inference.wandb.ai/v1/chat/completions",
        "default_model_template": "Qwen/Qwen3.6-35B-A3B",
    }
    cli = _client()
    status["client_note"] = _CLIENT_WHY
    if cli is None:
        return None, status
    model = _resolve_model(cli)
    status["model_note"] = _MODEL_WHY
    status["judge_model"] = model
    status["judge_independent_of_agent"] = not any(
        h in (model or "").lower() for h in AGENT_FAMILY_HINTS)
    if model is None:
        return None, status
    caps = _caps(model)
    status["request_shape"] = {
        "temperature": "omitted",
        "thinking": "disabled" if caps["thinking_off"] else "provider default",
        "json_mode": bool(caps["json_mode"]),
    }

    def clip(path: Path, n: int = 8000) -> str:
        try:
            return path.read_text(encoding="utf-8", errors="ignore")[:n]
        except Exception:
            return ""

    evidence = {
        "deterministic_summary": [
            {"name": r["name"], "passed": r["passed"], "reason": r["reason"]}
            for r in det_results if r.get("kind") != "meta"
        ][:80],
        "fetched_instrument_excerpts": fetched_instrument_evidence(agent),
        "atlas_excerpt": clip(agent / "jurisdiction_control_atlas.json", 12000),
        "briefing": clip(agent / "counsel_briefing.json", 6000),
        "ledger_excerpt": clip(agent / "exception_conflict_ledger.csv", 4000),
        # Full required cohort: the task requires 180 matrix rows, so the judge
        # sees all required rows with truncated cells instead of a 120-row sample.
        "matrix_full_required_rows": matrix_spread(
            agent / "export_screening_matrix.csv", want_rows=180)
            or clip(agent / "export_screening_matrix.csv", 16000),
    }
    prompt = (
        "You grade an advanced-compute export-control screening atlas on output quality only. "
        "Use fetched_instrument_excerpts as independent source text whenever grounding matters. "
        "Return a JSON object of the form "
        '{"checks": [{"id": 1, "passed": true, "reason": "..."}]} '
        f"with exactly {len(LLM_CHECKS)} entries, ids 1..{len(LLM_CHECKS)}.\n\n"
        "Criteria:\n" + "\n".join(f"{i+1}. {c}" for i, c in enumerate(LLM_CHECKS))
        + "\n\nEvidence:\n" + json.dumps(evidence)[:60000]
    )
    messages = [
        {"role": "system", "content": "You are a strict benchmark verifier. Return JSON only."},
        {"role": "user", "content": prompt},
    ]
    errors = []
    attempts = []
    status["judge_attempts"] = attempts
    candidate_models = [model] + [m for m in JUDGE_MODELS if m != model]
    for candidate in candidate_models:
        for json_mode in (True, False):
            attempt = {
                "model": candidate,
                "json_mode": bool(json_mode),
                "judge_independent_of_agent": not any(
                    h in (candidate or "").lower() for h in AGENT_FAMILY_HINTS),
            }
            try:
                resp = _create(cli, candidate, messages, 1800, json_mode=json_mode)
                raw = _message_text(resp)
                attempt["response_chars"] = len(raw or "")
                status["raw_response_preview"] = raw[:240]
                raw_name = "llm_judge_response_%s_%s.txt" % (
                    _safe_model_name(candidate), "json" if json_mode else "plain")
                try:
                    VERIFIER.mkdir(parents=True, exist_ok=True)
                    (VERIFIER / raw_name).write_text((raw or "")[:40000], encoding="utf-8")
                    attempt["raw_response_file"] = raw_name
                except Exception as write_exc:
                    attempt["raw_response_error"] = (
                        f"{type(write_exc).__name__}: {write_exc}")[:180]
                data = _extract_json_object(raw)
                checks = data.get("checks") or []
                seen_ids = set()
                for c in checks:
                    try:
                        seen_ids.add(int(c.get("id", -1)))
                    except Exception:
                        continue
                if not set(range(1, len(LLM_CHECKS) + 1)).issubset(seen_ids):
                    raise ValueError(
                        f"judge returned {len(seen_ids)} of {len(LLM_CHECKS)} required verdict ids")
                out = []
                for i in range(len(LLM_CHECKS)):
                    item = next((c for c in checks if int(c.get("id", -1)) == i + 1), None)
                    out.append({
                        "passed": bool(item and item.get("passed")),
                        "reason": str((item or {}).get("reason") or "").strip()[:500],
                    })
                status["judge_model"] = candidate
                status["request_shape"]["json_mode"] = bool(json_mode)
                status["judged_checks_scored"] = len(out)
                status["graded"] = True
                if errors:
                    status["retry_notes"] = errors[-4:]
                attempt["verdicts"] = len(out)
                attempts.append(attempt)
                return out, status
            except Exception as e:
                attempt["error"] = f"{type(e).__name__}: {e}"[:260]
                attempts.append(attempt)
                errors.append(f"{candidate}/json_mode={json_mode}:{type(e).__name__}: {e}")
    status["error"] = "; ".join(errors[-6:]) if errors else "judge produced no parseable response"
    return None, status


def write_reward(payload: dict):
    VERIFIER.mkdir(parents=True, exist_ok=True)
    (VERIFIER / "reward.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    reward = payload.get("reward")
    if reward is None:
        if not payload.get("invalid_evaluation"):
            (VERIFIER / "reward.txt").write_text("0.0", encoding="utf-8")
    else:
        (VERIFIER / "reward.txt").write_text(str(reward), encoding="utf-8")
    print(json.dumps(payload, indent=2))


def _category_scores(all_checks: list[dict], manifest_checks: dict | None = None) -> dict:
    """Map equal-weight results onto S-08 category means for Batch-12/14 reporting."""
    # Prefer labels from verify emission kinds; S-08 static ~= structural,
    # reward_hacking ~= content deterministic, partial_oracle ~= LLM.
    structural = [c for c in all_checks if c.get("kind") == "structural"]
    content = [c for c in all_checks if c.get("kind") == "content"]
    llm = [c for c in all_checks if c.get("source") == "llm"]
    rh = [c for c in content if c.get("source") != "llm"]

    def mean(xs):
        return round((sum(1 for c in xs if c.get("passed")) / len(xs)), 4) if xs else 0.0

    return {
        "structural_check_score": mean(structural),
        "reward_hacking_check_score": mean(rh),
        "partial_oracle_check_score": mean(llm),
    }


def _runtime_weighted_reward(all_checks: list[dict]) -> float:
    """Canonical bucket-level reward.

    The verifier first computes the three normalized bucket totals reported as
    total_static_check_score, total_reward_hacking_check_score, and
    total_partial_oracle_check_score. Runtime reward is the equal mean of those
    three bucket totals, not a flat per-check weighted mean where bucket sizes
    could silently change the scoring formula.
    """
    cats = _category_scores(all_checks)
    bucket_weights = {
        "structural_check_score": 1.0,
        "reward_hacking_check_score": 1.0,
        "partial_oracle_check_score": 1.0,
    }
    available = sum(bucket_weights.values())
    earned = sum(cats[name] * weight for name, weight in bucket_weights.items())
    return round(earned / available, 4) if available else 0.0


STATIC_CHECK_NAMES = {
    1: "export_screening_matrix.csv exists with the required columns",
    2: "matrix carries one row per catalog claim with no duplicates",
    3: "row jurisdiction_id matches the catalog assignment for each claim_id",
    4: "row control_theme matches the catalog assignment for each claim_id",
    5: "all four controlled columns use only their closed vocabularies",
    6: "all ten jurisdictions resolved for grounding",
    7: "exception_conflict_ledger.csv carries the rulebook columns in order",
    8: "all deliverable files are present, parse, and are non-trivial",
    9: "outputs were written under the canonical /logs/agent directory",
}

REWARD_HACKING_CHECK_NAMES = {
    1: "at least 80 grounded obligation rows (substantive AND full-quote round-trips)",
    2: "at least 120 grounded obligation rows",
    3: "grounded_share (grounded/catalog) >= 0.50",
    4: "quotes full-cover round-trip on >=50% of substantive rows",
    5: "quotes full-cover round-trip on >=70% of substantive rows",
    6: "quotes full-cover round-trip on >=85% of substantive rows",
    7: "quotes sit in the passage the claim names, not just somewhere in the instrument",
    8: "paraphrases are grounded near their evidence_quote window on >=70% of grounded rows",
    9: "control_tightness_score recomputes on >=80% of grounded rows",
    10: "control_tightness_score recomputes on >=95% of grounded rows",
    11: "declared control_class is compatible with the quote window on >=90% of grounded rows",
    12: "substantive notes appear on >=60% of grounded rows with limited near-duplicates",
    13: "at least 8 jurisdictions have >=8 grounded rows each",
    14: "all 10 jurisdictions have grounded rows in the matrix",
    15: "at least 12 multi-jurisdiction crosswalk groups over grounded rows",
    16: "multi-jurisdiction crosswalk groups hold a single control_theme each",
    17: "multi-jurisdiction crosswalk groups carry distinct regime quotes, not theme-label buckets",
    18: "atlas reconciles with the matrix (per-jurisdiction figures and crosswalk groups)",
    19: "conflict ledger has >=3 distinct disagreeing claim pairs that trace to the matrix",
    20: "chart_data series equal the matrix (class counts and tightness histogram)",
    21: "chart_data theme-coverage and conflict-density series equal the matrix",
    22: "the four PNGs are distinct plots whose content correlates with chart_data",
    23: "briefing headline figures reconcile with the matrix (count, class counts, mean score)",
    24: "briefing highest_tightness_themes are real themes that really do score highest",
    25: "briefing conflicted jurisdiction pairs are real shared-theme class collisions",
    26: "briefing regime_comparison is 150-300 words and names classes the matrix contains",
    27: "briefing has 3-5 substantive, non-duplicated recommended_actions",
    28: "briefing summary exists and is at most 200 words",
    29: "grounded obligation paraphrases are not near-duplicates across rows",
    30: "declared licence_posture is compatible with the quote window on >=90% of grounded rows",
    31: "declared enduse_sensitivity is compatible with the quote window on >=90% of grounded rows",
    32: "declared duty_actor is compatible with the quote window on >=90% of grounded rows",
    33: "at least 10 grounded rows have recomputable tightness scores",
    34: "at least 25 grounded rows have recomputable tightness scores",
    35: "at least 35 grounded rows have recomputable tightness scores",
    36: "recomputable grounded rows span at least 4 jurisdictions",
    37: "at least 10 grounded rows carry substantive row-specific notes",
    38: "at least 20 grounded rows carry substantive row-specific notes",
    39: "substantive grounded notes span at least 10 control themes",
    40: "substantive grounded notes span at least 14 control themes",
    41: "at least 10 grounded rows combine recomputable scores with substantive notes",
    42: "at least 20 grounded rows combine recomputable scores with substantive notes",
    43: "at least 15 grounded rows have two source-compatible classification footprints",
    44: "at least 20 grounded rows have two source-compatible classification footprints",
    45: "at least 10 grounded rows have three source-compatible classification footprints",
    46: "at least 13 grounded rows have three source-compatible classification footprints",
    47: "at least 5 quality-grounded rows combine quote, recomputed score, note, and field footprints",
    48: "at least 10 quality-grounded rows combine quote, recomputed score, note, and field footprints",
    49: "at least 14 quality-grounded rows combine quote, recomputed score, note, and field footprints",
    50: "quality-grounded rows span at least 4 jurisdictions",
    51: "quality-grounded rows span at least 8 control themes",
    52: "at least 3 strongest rows add grounded paraphrases to quality-grounded evidence",
    53: "at least 6 grounded rows combine recomputable scores, substantive notes, and grounded paraphrases",
    54: "rows combining recomputable scores, substantive notes, and grounded paraphrases span at least 4 jurisdictions",
    55: "rows combining recomputable scores, substantive notes, and grounded paraphrases span at least 6 control themes",
    56: "strongest quality rows span at least 2 jurisdictions",
    57: "strongest quality rows span at least 3 control themes",
    58: "quality-grounded rows span at least 5 jurisdictions",
}


# Caching wrappers to make individual score_* function calls fast and idempotent during evaluation.
_DET_CACHE: dict = {}
_LLM_CACHE: dict = {}


def get_cached_deterministic(agent_path: Path, catalog: dict, claims: dict) -> list[dict]:
    key = str(agent_path.resolve())
    if key not in _DET_CACHE:
        _DET_CACHE[key] = run_deterministic(agent_path, catalog, claims)
    return _DET_CACHE[key]


def get_cached_llm_judge(agent_path: Path, det_results: list[dict]) -> tuple[list[dict] | None, dict]:
    key = str(agent_path.resolve())
    if key not in _LLM_CACHE:
        _LLM_CACHE[key] = call_llm_judge(agent_path, det_results)
    return _LLM_CACHE[key]


def _manifest_agent(agent: Path | str | None) -> Path:
    return Path(agent) if agent is not None else resolve_agent_dir()


def _manifest_catalog_claims(catalog: dict | None, claims: dict | None) -> tuple[dict, dict]:
    if catalog is None or claims is None:
        return load_catalog()
    return catalog, claims


def _manifest_deterministic_result(
        check_name: str,
        agent: Path | str | None = None,
        catalog: dict | None = None,
        claims: dict | None = None) -> dict:
    agent_path = _manifest_agent(agent)
    catalog, claims = _manifest_catalog_claims(catalog, claims)
    for result in get_cached_deterministic(agent_path, catalog, claims):
        if result.get("name") == check_name:
            return result
    return {"name": check_name, "passed": False, "reason": "check name not emitted", "kind": "meta"}


def _manifest_llm_result(
        index: int,
        agent: Path | str | None = None,
        det_results: list[dict] | None = None,
        catalog: dict | None = None,
        claims: dict | None = None) -> dict:
    agent_path = _manifest_agent(agent)
    if det_results is None:
        catalog, claims = _manifest_catalog_claims(catalog, claims)
        det_results = [
            r for r in get_cached_deterministic(agent_path, catalog, claims)
            if r.get("kind") in ("content", "structural")
        ]
    llm, status = get_cached_llm_judge(agent_path, det_results)
    name = LLM_CHECKS[index - 1]
    if llm is None:
        return {
            "name": name,
            "passed": False,
            "reason": "llm_judge_unavailable_fail_closed",
            "kind": "content",
            "source": "llm",
            "llm_status": status,
        }
    item = llm[index - 1]
    return {
        "name": name,
        "passed": bool(item.get("passed")),
        "reason": item.get("reason") or "",
        "kind": "content",
        "source": "llm",
        "judge_score": 1.0 if item.get("passed") else 0.0,
        "judge_justification": item.get("reason") or ("Independent LLM judge boolean verdict; no justification was returned."),
    }


def score_static_checks_1(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(STATIC_CHECK_NAMES[1], agent, catalog, claims)
def score_static_checks_2(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(STATIC_CHECK_NAMES[2], agent, catalog, claims)
def score_static_checks_3(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(STATIC_CHECK_NAMES[3], agent, catalog, claims)
def score_static_checks_4(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(STATIC_CHECK_NAMES[4], agent, catalog, claims)
def score_static_checks_5(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(STATIC_CHECK_NAMES[5], agent, catalog, claims)
def score_static_checks_6(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(STATIC_CHECK_NAMES[6], agent, catalog, claims)
def score_static_checks_7(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(STATIC_CHECK_NAMES[7], agent, catalog, claims)
def score_static_checks_8(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(STATIC_CHECK_NAMES[8], agent, catalog, claims)
def score_static_checks_9(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(STATIC_CHECK_NAMES[9], agent, catalog, claims)
def score_reward_hacking_checks_1(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[1], agent, catalog, claims)
def score_reward_hacking_checks_2(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[2], agent, catalog, claims)
def score_reward_hacking_checks_3(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[3], agent, catalog, claims)
def score_reward_hacking_checks_4(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[4], agent, catalog, claims)
def score_reward_hacking_checks_5(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[5], agent, catalog, claims)
def score_reward_hacking_checks_6(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[6], agent, catalog, claims)
def score_reward_hacking_checks_7(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[7], agent, catalog, claims)
def score_reward_hacking_checks_8(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[8], agent, catalog, claims)
def score_reward_hacking_checks_9(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[9], agent, catalog, claims)
def score_reward_hacking_checks_10(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[10], agent, catalog, claims)
def score_reward_hacking_checks_11(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[11], agent, catalog, claims)
def score_reward_hacking_checks_12(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[12], agent, catalog, claims)
def score_reward_hacking_checks_13(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[13], agent, catalog, claims)
def score_reward_hacking_checks_14(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[14], agent, catalog, claims)
def score_reward_hacking_checks_15(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[15], agent, catalog, claims)
def score_reward_hacking_checks_16(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[16], agent, catalog, claims)
def score_reward_hacking_checks_17(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[17], agent, catalog, claims)
def score_reward_hacking_checks_18(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[18], agent, catalog, claims)
def score_reward_hacking_checks_19(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[19], agent, catalog, claims)
def score_reward_hacking_checks_20(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[20], agent, catalog, claims)
def score_reward_hacking_checks_21(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[21], agent, catalog, claims)
def score_reward_hacking_checks_22(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[22], agent, catalog, claims)
def score_reward_hacking_checks_23(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[23], agent, catalog, claims)
def score_reward_hacking_checks_24(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[24], agent, catalog, claims)
def score_reward_hacking_checks_25(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[25], agent, catalog, claims)
def score_reward_hacking_checks_26(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[26], agent, catalog, claims)
def score_reward_hacking_checks_27(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[27], agent, catalog, claims)
def score_reward_hacking_checks_28(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[28], agent, catalog, claims)
def score_reward_hacking_checks_29(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[29], agent, catalog, claims)
def score_reward_hacking_checks_30(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[30], agent, catalog, claims)
def score_reward_hacking_checks_31(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[31], agent, catalog, claims)
def score_reward_hacking_checks_32(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[32], agent, catalog, claims)
def score_reward_hacking_checks_33(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[33], agent, catalog, claims)
def score_reward_hacking_checks_34(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[34], agent, catalog, claims)
def score_reward_hacking_checks_35(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[35], agent, catalog, claims)
def score_reward_hacking_checks_36(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[36], agent, catalog, claims)
def score_reward_hacking_checks_37(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[37], agent, catalog, claims)
def score_reward_hacking_checks_38(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[38], agent, catalog, claims)
def score_reward_hacking_checks_39(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[39], agent, catalog, claims)
def score_reward_hacking_checks_40(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[40], agent, catalog, claims)
def score_reward_hacking_checks_41(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[41], agent, catalog, claims)
def score_reward_hacking_checks_42(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[42], agent, catalog, claims)
def score_reward_hacking_checks_43(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[43], agent, catalog, claims)
def score_reward_hacking_checks_44(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[44], agent, catalog, claims)
def score_reward_hacking_checks_45(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[45], agent, catalog, claims)
def score_reward_hacking_checks_46(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[46], agent, catalog, claims)
def score_reward_hacking_checks_47(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[47], agent, catalog, claims)
def score_reward_hacking_checks_48(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[48], agent, catalog, claims)
def score_reward_hacking_checks_49(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[49], agent, catalog, claims)
def score_reward_hacking_checks_50(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[50], agent, catalog, claims)
def score_reward_hacking_checks_51(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[51], agent, catalog, claims)
def score_reward_hacking_checks_52(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[52], agent, catalog, claims)
def score_reward_hacking_checks_53(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[53], agent, catalog, claims)
def score_reward_hacking_checks_54(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[54], agent, catalog, claims)
def score_reward_hacking_checks_55(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[55], agent, catalog, claims)
def score_reward_hacking_checks_56(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[56], agent, catalog, claims)
def score_reward_hacking_checks_57(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[57], agent, catalog, claims)
def score_reward_hacking_checks_58(agent=None, catalog=None, claims=None): return _manifest_deterministic_result(REWARD_HACKING_CHECK_NAMES[58], agent, catalog, claims)
def score_partial_oracle_checks_1(agent=None, det_results=None, catalog=None, claims=None): return _manifest_llm_result(1, agent, det_results, catalog, claims)
def score_partial_oracle_checks_2(agent=None, det_results=None, catalog=None, claims=None): return _manifest_llm_result(2, agent, det_results, catalog, claims)
def score_partial_oracle_checks_3(agent=None, det_results=None, catalog=None, claims=None): return _manifest_llm_result(3, agent, det_results, catalog, claims)
def score_partial_oracle_checks_4(agent=None, det_results=None, catalog=None, claims=None): return _manifest_llm_result(4, agent, det_results, catalog, claims)
def score_partial_oracle_checks_5(agent=None, det_results=None, catalog=None, claims=None): return _manifest_llm_result(5, agent, det_results, catalog, claims)
def score_partial_oracle_checks_6(agent=None, det_results=None, catalog=None, claims=None): return _manifest_llm_result(6, agent, det_results, catalog, claims)
def score_partial_oracle_checks_7(agent=None, det_results=None, catalog=None, claims=None): return _manifest_llm_result(7, agent, det_results, catalog, claims)
def score_partial_oracle_checks_8(agent=None, det_results=None, catalog=None, claims=None): return _manifest_llm_result(8, agent, det_results, catalog, claims)


def main():
    agent = resolve_agent_dir()
    catalog, claims = load_catalog()

    # 1. Warm deterministic cache and inspect metrics
    det = get_cached_deterministic(agent, catalog, claims)
    metrics = next((r for r in det if r["name"] == "_metrics"), None)
    det_scored = [r for r in det if r.get("kind") in ("content", "structural")]

    # 2. Warm LLM cache
    llm, llm_status = get_cached_llm_judge(agent, det_scored)
    llm_status["graded"] = llm is not None
    VERIFIER.mkdir(parents=True, exist_ok=True)
    (VERIFIER / "llm_status.json").write_text(json.dumps(llm_status, indent=2), encoding="utf-8")

    if llm is None:
        write_reward({
            "reward": None,
            "invalid_evaluation": True,
            "total_static_check_score": None,
            "total_reward_hacking_check_score": None,
            "total_partial_oracle_check_score": None,
            "content_score": None,
            "structural_score": None,
            "structural_check_score": None,
            "reward_hacking_check_score": None,
            "partial_oracle_check_score": None,
            "error": "llm_judge_unavailable_fail_closed",
            "llm_status": llm_status,
            "deterministic_passed": sum(1 for r in det_scored if r["passed"]),
            "deterministic_total": len(det_scored),
            "details": det_scored,
            "metrics": json.loads(metrics["reason"]) if metrics else {},
        })
        (VERIFIER / "reward.txt").write_text("0.0", encoding="utf-8")
        (VERIFIER / "verifier_error.txt").write_text(
            "invalid_evaluation: LLM judge unavailable or unparseable\n", encoding="utf-8")
        return

    # 3. QD-03: Execute every manifest score_* check function directly so the manifest is 100% truthful
    all_checks = []
    # Static checks (1..9)
    for i in range(1, 10):
        fn = globals()[f"score_static_checks_{i}"]
        all_checks.append(fn(agent=agent, catalog=catalog, claims=claims))

    # Reward hacking checks (1..58)
    for i in range(1, 59):
        fn = globals()[f"score_reward_hacking_checks_{i}"]
        all_checks.append(fn(agent=agent, catalog=catalog, claims=claims))

    # Partial oracle LLM checks (1..8)
    for i in range(1, 9):
        fn = globals()[f"score_partial_oracle_checks_{i}"]
        all_checks.append(fn(agent=agent, det_results=det_scored, catalog=catalog, claims=claims))

    # Print judge justifications for transparency
    llm_items = [c for c in all_checks if c.get("source") == "llm"]
    for i, item in enumerate(llm_items, start=1):
        print(json.dumps({
            "judge_item": i,
            "judge_score": item.get("judge_score", 1.0 if item.get("passed") else 0.0),
            "judge_justification": item.get("judge_justification") or item.get("reason") or "",
        }, ensure_ascii=False))

    content = [c for c in all_checks if c.get("kind") == "content"]
    structural = [c for c in all_checks if c.get("kind") == "structural"]
    passed = sum(1 for c in all_checks if c.get("passed"))
    total = len(all_checks) or 1
    cats = _category_scores(all_checks)
    weighted_reward = _runtime_weighted_reward(all_checks)
    write_reward({
        "reward": weighted_reward,
        "reward_formula": "canonical_equal_bucket_mean",
        "bucket_weights": {
            "total_static_check_score": 1,
            "total_reward_hacking_check_score": 1,
            "total_partial_oracle_check_score": 1,
        },
        "total_static_check_score": cats["structural_check_score"],
        "total_reward_hacking_check_score": cats["reward_hacking_check_score"],
        "total_partial_oracle_check_score": cats["partial_oracle_check_score"],
        "content_score": round((sum(1 for c in content if c.get("passed")) / len(content)) if content else 0.0, 4),
        "structural_score": round((sum(1 for c in structural if c.get("passed")) / len(structural)) if structural else 0.0, 4),
        **cats,
        "checks_passed": passed,
        "total_checks": total,
        "content_checks": len(content),
        "structural_checks": len(structural),
        "llm_status": llm_status,
        "details": all_checks,
        "metrics": json.loads(metrics["reason"]) if metrics else {},
    })


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        traceback.print_exc()
        write_reward({
            "reward": None,
            "invalid_evaluation": True,
            "total_static_check_score": None,
            "total_reward_hacking_check_score": None,
            "total_partial_oracle_check_score": None,
            "content_score": None,
            "structural_score": None,
            "structural_check_score": None,
            "reward_hacking_check_score": None,
            "partial_oracle_check_score": None,
            "error": f"verifier_exception: {type(exc).__name__}: {exc}",
        })
        try:
            VERIFIER.mkdir(parents=True, exist_ok=True)
            (VERIFIER / "reward.txt").write_text("0.0", encoding="utf-8")
            (VERIFIER / "verifier_error.txt").write_text(
                f"invalid_evaluation: verifier raised {type(exc).__name__}\n", encoding="utf-8")
        except Exception:
            pass
