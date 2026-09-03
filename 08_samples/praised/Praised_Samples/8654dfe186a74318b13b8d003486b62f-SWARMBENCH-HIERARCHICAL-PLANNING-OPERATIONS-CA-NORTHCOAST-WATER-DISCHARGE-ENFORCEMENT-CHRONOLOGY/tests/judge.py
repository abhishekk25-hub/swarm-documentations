#!/usr/bin/env python3
"""
Verifier for the North Coast Water Board Enforcement Chronology task.

Grades ONLY the agent's generated deliverables under /logs/agent/:
  - enforcement_chronology.csv  (the grounded findings/chronology ledger; per-order
    findings_<slug>.csv shards and region_<x>_consolidated.csv shards are merged in
    if present)
  - site_dossier.docx           (the written dossier, the centerpiece)
  - crosslink_matrix.csv         (discharger -> parcel -> order -> waterway -> county,
    plus supersedes / superseded_by / related orders)
  - contradiction_log.csv        (supersession / amendment / same-site / conflicting refs)
  - chart_*.png                  (ledger-derived charts)

It NEVER inspects the agent's trajectory, tool/fetch logs, session JSON, or how the
result was produced. The agent may use any method/tool. Only the output files are scored.

Scoring has two parts, both read ONLY from the deliverables:
  - Checks 1-21: an LLM judge marks structural / quality / consistency criteria. The
    judge is run NUM_JUDGE_RUNS times independently and each check is decided by majority
    vote, so no single judge call decides the majority of the reward.
  - Checks 22-30: nine deterministic DEPTH-OF-COVERAGE checks (graduated threshold bands)
    computed in Python directly from the findings ledger. These reward the sustained
    per-order reading the instruction asks for (several findings per order across the
    whole twenty-order set, spread across counties and topics, each backed by a
    substantial verbatim quote) - the work a single context cannot keep up across many
    heavy orders but a swarm of per-order readers can. This is the genuine
    multi-vs-single separation, not a trajectory check.

Anti-padding guard: every depth count is taken over SUBSTANTIVE findings only (see
is_substantive_finding). A row counts as a genuine finding only if regulator_finding is
a real paraphrase SENTENCE asserting what the board found / required / directed - not a
section heading, not an order title or number/label (e.g. "R1-2024-0044"), not a
table-of-contents line with dot leaders / page numbers, and not text copied verbatim out
of the document. This closes two scrapes: (1) flooding the ledger with TOC entries or
quote slices, and (2) the "title in finding, body in quote" split, where the agent lifts
an order's heading into the finding and its body into the quote - two adjacent verbatim
fragments that fool a finding-inside-quote test but are not a paraphrase plus evidence.
Such rows are dropped before counting and are also flagged to the LLM judge (raw vs.
substantive counts plus a [GENUINE]/[PADDING] tag on every sampled row), so they cannot
move either half of the score.

Scoring is simple and additive: one point per check, every check weighted equally.
  reward = (checks passed) / (total checks)
No weighting, no tiers, no caps. The gap comes from the task scale and coordination
requirement, not from how points are awarded.

Fail-closed: this is an llm-judge task, so the deterministic depth checks (22-30) never
produce a non-zero reward on their own. If every LLM judge call fails, the verifier
writes an explicit error state ({"reward": 0.0, "error": ...}) and the depth checks are
not counted - an infrastructure failure is never scored as a genuine zero-reward run.
"""

import csv
import io
import json
import os
import re
import traceback
from collections import Counter
from pathlib import Path

AGENT_DIR = Path("/logs/agent")
REWARD_PATH = Path("/logs/verifier/reward.json")
REWARD_TXT = Path("/logs/verifier/reward.txt")
LLM_CHECKS = 21
DEPTH_CHECKS = 9
NUM_CHECKS = 30
# The LLM judge is run this many times independently and majority-voted, so no
# single judge call decides the majority of the reward.
NUM_JUDGE_RUNS = 3

LEDGER_COLUMNS = [
    "finding_id", "order_id", "discharger", "county", "waterway", "apn",
    "event_date", "topic", "regulator_finding", "quote", "source_url",
]
COUNTIES = ["Del Norte", "Humboldt", "Lake", "Marin", "Mendocino", "Siskiyou", "Sonoma", "Trinity"]
CHART_FILES = [
    "chart_findings_by_topic.png",
    "chart_findings_by_county.png",
    "chart_findings_by_waterway.png",
]

# Anchor orders known to exist on the North Coast adopted-orders portal. Used only to
# measure how much of the real document set the ledger draws on; the depth checks group
# by whatever order_ids appear, so the agent is free to read others as well.
KNOWN_ORDERS = {
    "R1-2024-0044", "R1-2024-0026", "R1-2024-0047", "R1-2025-0033", "R1-2024-0015",
    "R1-2022-0019", "R1-2024-0054", "R1-2025-0016", "R1-2025-0032", "R1-2025-0043",
    "R1-2024-0037", "R1-2024-0050", "R1-2025-0036", "R1-2024-0042",
    "R1-2021-0023", "R1-2018-0012",
}
# A North Coast order number looks like R1-2024-0044 (region-year-sequence).
_ORDER_ID_RE = re.compile(r"R\d{1,2}\s*[-\u2013]\s*\d{4}\s*[-\u2013]\s*\d{3,4}", re.IGNORECASE)


def _norm_topic(t):
    return re.sub(r"[^a-z0-9]", "", (t or "").lower())


def _norm_text(s):
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def _norm_order_id(s):
    m = _ORDER_ID_RE.search(s or "")
    if m:
        return re.sub(r"\s", "", m.group(0).upper().replace("\u2013", "-"))
    return _norm_text(s)


# A genuine paraphrase of a board finding states what the board found / required / directed
# or what the discharger did, so it almost always carries one of these action verbs. A
# scraped section TITLE ("Purpose of the Order", "Legal Requirements") is a noun phrase
# with none.
_FINDING_VERB_RE = re.compile(
    r"\b("
    r"require\w*|must|shall|should|direct\w*|order\w*|find|finds|found|determine\w*|"
    r"note|notes|noted|identif\w+|approv\w+|acknowledg\w+|accept\w*|criticiz\w+|"
    r"conclud\w+|expect\w*|need\w*|provide\w*|submit\w*|report\w*|demonstrate\w*|"
    r"ensure\w*|address\w*|evaluate\w*|recommend\w*|flag\w*|fail\w*|lack\w*|"
    r"caus\w*|permit\w*|allow\w*|discharg\w*|abate\w*|remediat\w*|stabiliz\w*|"
    r"violat\w*|exceed\w*|threaten\w*|impact\w*|erod\w*|clean\w*|restore\w*|"
    r"improve\w*|reduce\w*|increase\w*|continue\w*|deny|denied|reject\w*|"
    r"is required|are required|was required|were required|did not|does not|has not|have not"
    r")\b",
    re.IGNORECASE,
)

# Start-anchored order label/ID the scrape prepends, e.g. "R1-2024-0044:" or
# "Order No. R1-2024-0044 ...". Anchored to the start so a number mentioned mid-sentence
# in a real paraphrase does not trip it.
_CODE_PREFIX_RE = re.compile(
    r"^\s*(order\s*(no\.?)?\s*)?R\d{1,2}\s*[-\u2013]\s*\d{4}\s*[-\u2013]\s*\d{3,4}\b",
    re.IGNORECASE,
)


def _title_case_ratio(s):
    """Fraction of words that begin with a capital letter. Section titles are mostly
    Title-Cased ('Purpose Of The Order'); real sentences are not."""
    words = re.findall(r"[A-Za-z][A-Za-z'\u2019&.\-]*", s)
    if len(words) < 3:
        return 1.0
    cap = sum(1 for w in words if w[:1].isupper())
    return cap / len(words)


def is_substantive_finding(r):
    """A row counts as a GENUINE finding only if its regulator_finding is a real
    paraphrase SENTENCE in the analyst's own words - not scraped boilerplate - AND it is
    backed by a real verbatim quote. The instruction is explicit that the finding must be
    the board's point in the agent's own words and DIFFERENT text from the quote, so these
    are content requirements, not formatting nit-picks.

    A row is substantive only when ALL hold:
      - regulator_finding is present, >= 25 chars and >= 6 words;
      - it has no dot-leader run (".... 12");
      - it is not identical to, nor a verbatim slice of, the quote;
      - it does not begin with an order label/number (e.g. "R1-2024-0044", "Order No. ...");
      - it contains a regulatory action verb (it asserts what the board / discharger did);
      - it is not a mostly Title-Cased heading (capitalized-word ratio < 0.6);
      - the quote is present, >= 40 chars of actual text, has no dot-leader run, and is
        not a mostly Title-Cased heading line.
    """
    f = (r.get("regulator_finding") or "").strip()
    q = (r.get("quote") or "").strip()
    if len(f) < 25:
        return False
    if len(re.findall(r"[A-Za-z]+", f)) < 6:
        return False
    if re.search(r"\.\s*\.\s*\.\s*\.", f):  # dot-leader / TOC artifact
        return False
    nf, nq = _norm_text(f), _norm_text(q)
    if not nf or nf == nq or nf in nq:
        return False
    if _CODE_PREFIX_RE.search(f):           # starts with an order label/ID
        return False
    if not _FINDING_VERB_RE.search(f):      # no action verb -> a noun-phrase title
        return False
    if _title_case_ratio(f) >= 0.6:         # mostly Title-Cased heading
        return False
    if len(q) < 40:
        return False
    if re.search(r"\.\s*\.\s*\.\s*\.", q):  # dot-leader / TOC line in the quote
        return False
    if _title_case_ratio(q) >= 0.6:         # quote is a Title-Cased heading, not prose
        return False
    return True


def compute_depth_metrics(rows):
    """Objective depth-of-coverage metrics, computed from the output ledger only and
    counting ONLY substantive (genuine) findings - see is_substantive_finding.

    The separating signal is PER-ORDER depth: the instruction asks for several distinct
    findings per order across the whole twenty-order set ("do not let it thin out after
    the first few"). A complete-but-shallow pass can name every site and cite every order
    once, but it cannot put real depth behind each one. A run cannot fake depth by flooding
    the ledger with scraped headings or quote slices either: those rows fail
    is_substantive_finding and are dropped before any depth count."""
    raw_total = len(rows)
    sub = [r for r in rows if is_substantive_finding(r)]
    total = len(sub)

    order_keys = [_norm_order_id(r.get("order_id")) for r in sub]
    order_keys = [k for k in order_keys if k]
    distinct_orders = set(order_keys)
    distinct_known_orders = set(
        k for k in order_keys if k in KNOWN_ORDERS or _ORDER_ID_RE.search(k or "")
    )

    county_counts = Counter((r.get("county") or "").strip().lower() for r in sub if (r.get("county") or "").strip())
    topic_counts = Counter(_norm_topic(r.get("topic")) for r in sub if _norm_topic(r.get("topic")))
    order_counts = Counter(order_keys)

    long_quotes = sum(1 for r in sub if len((r.get("quote") or "").strip()) >= 80)

    return {
        "raw_rows": raw_total,
        "substantive_findings": total,
        "total_findings": total,
        "distinct_orders": len(distinct_orders),
        "distinct_known_orders": len(distinct_known_orders),
        "orders_with_ge3_findings": sum(1 for c in order_counts.values() if c >= 3),
        "orders_with_ge5_findings": sum(1 for c in order_counts.values() if c >= 5),
        "counties_with_ge8_findings": sum(1 for c in county_counts.values() if c >= 8),
        "topics_with_ge8_findings": sum(1 for c in topic_counts.values() if c >= 8),
        "findings_with_quote_ge80_chars": long_quotes,
    }


def depth_checks(rows):
    """Checks 22-30: deterministic depth-of-coverage, graduated threshold bands, counting
    ONLY substantive findings (see is_substantive_finding). Each is one independent point
    (no weighting). They reward the sustained per-order reading that the instruction asks
    for across the whole set - the work that does not fit a single context but spreads
    naturally across a swarm of per-order readers. A shallow run still keeps full credit on
    the quality checks (1-21); these only measure depth."""
    m = compute_depth_metrics(rows)
    specs = [
        (22, m["orders_with_ge3_findings"] >= 10,
         f"{m['orders_with_ge3_findings']} orders have >= 3 substantive findings each "
         f"(need >= 10; several genuine findings per order, not one or two)."),
        (23, m["orders_with_ge3_findings"] >= 14,
         f"{m['orders_with_ge3_findings']} orders have >= 3 substantive findings each "
         f"(need >= 14 for near-full-set depth)."),
        (24, m["orders_with_ge5_findings"] >= 6,
         f"{m['orders_with_ge5_findings']} orders have >= 5 substantive findings each "
         f"(need >= 6; real depth on individual orders)."),
        (25, m["orders_with_ge5_findings"] >= 10,
         f"{m['orders_with_ge5_findings']} orders have >= 5 substantive findings each "
         f"(need >= 10 for sustained depth across the set)."),
        (26, m["total_findings"] >= 90,
         f"Ledger has {m['total_findings']} substantive findings "
         f"(need >= 90; raw rows = {m['raw_rows']})."),
        (27, m["total_findings"] >= 150,
         f"Ledger has {m['total_findings']} substantive findings "
         f"(need >= 150 for full-set depth; raw rows = {m['raw_rows']})."),
        (28, m["counties_with_ge8_findings"] >= 4,
         f"{m['counties_with_ge8_findings']} counties have >= 8 substantive findings each "
         f"(need >= 4; depth must spread across the region, not one county)."),
        (29, m["topics_with_ge8_findings"] >= 5,
         f"{m['topics_with_ge8_findings']} topics have >= 8 substantive findings each "
         f"(need >= 5 of the 9 topics for taxonomy-wide depth)."),
        (30, m["findings_with_quote_ge80_chars"] >= 100,
         f"{m['findings_with_quote_ge80_chars']} substantive findings carry a substantial "
         f"verbatim quote (>= 80 chars) (need >= 100)."),
    ]
    return [{"id": cid, "pass": ok, "reason": reason} for cid, ok, reason in specs], m


def _read_text(path):
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


# The ledger schema is described in prose in instruction.md, so an agent may pick
# reasonable-but-different header names. We grade the CONTENT the agent produced, not the
# exact header spelling, so equivalent columns are mapped onto the canonical schema below.
_CANON_ALIASES = {
    "finding_id":        {"id", "fid", "rowid", "rowno", "no", "findingno", "index", "idx"},
    "order_id":          {"orderid", "orderno", "ordernumber", "caono", "cao", "docid",
                          "documentid", "decisionid", "caseid", "caseno", "fileid"},
    "discharger":        {"responsibleparty", "party", "parties", "operator", "dischargername",
                          "name", "company", "entity", "owner"},
    "county":            {"countyname"},
    "waterway":          {"water", "creek", "river", "receivingwater", "receivingwaters",
                          "waterbody", "stream", "watercourse", "watersofthestate"},
    "apn":               {"parcel", "parcelno", "parcelnumber", "assessorparcelnumber", "apns",
                          "assessorparcelnumbers"},
    "event_date":        {"date", "orderdate", "findingdate", "eventdate", "adopteddate"},
    "topic":             {"category", "theme", "topictag", "topicarea", "violationtype"},
    "regulator_finding": {"regulatoryfinding", "finding", "boardfinding", "regulatorpoint",
                          "point", "paraphrase", "summary", "findingtext", "findingsummary"},
    "quote":             {"verbatim", "verbatimquote", "evidence", "evidencequote", "excerpt",
                          "passage", "sourcequote"},
    "source_url":        {"url", "link", "sourcelink", "source", "orderurl", "documenturl"},
}


def _canon_key(name):
    return re.sub(r"[^a-z0-9]", "", (name or "").lower())


_ALIAS_TO_CANON = {}
for _canon, _aliases in _CANON_ALIASES.items():
    _ALIAS_TO_CANON[_canon_key(_canon)] = _canon
    for _a in _aliases:
        _ALIAS_TO_CANON[_canon_key(_a)] = _canon


def _normalize_row(r):
    """Map a row's columns onto the canonical ledger schema regardless of header spelling.
    An explicit canonical column always wins; an alias only fills a canonical field that
    is otherwise empty."""
    out = dict(r)
    for raw_key, val in r.items():
        canon = _ALIAS_TO_CANON.get(_canon_key(raw_key))
        if not canon:
            continue
        if (out.get(canon) or "").strip():
            continue
        if (val or "").strip():
            out[canon] = val
    return out


def _parse_csv_rows(text):
    if not text.strip():
        return []
    try:
        reader = csv.DictReader(io.StringIO(text))
        return [_normalize_row(dict(r)) for r in reader]
    except Exception:
        return []


def load_ledger():
    """Load the chronology ledger from enforcement_chronology.csv, merging any per-order
    findings_<slug>.csv shards and region_<x>_consolidated.csv shards. De-duplicates on
    (order_id, quote). Only output files are read - no trajectory inspection."""
    rows = []
    rows.extend(_parse_csv_rows(_read_text(AGENT_DIR / "enforcement_chronology.csv")))
    try:
        shards = sorted(
            fn for fn in os.listdir(AGENT_DIR)
            if (fn.lower().startswith("findings_") and fn.lower().endswith(".csv"))
            or (fn.lower().startswith("region_") and fn.lower().endswith("_consolidated.csv"))
        )
    except OSError:
        shards = []
    for fn in shards:
        rows.extend(_parse_csv_rows(_read_text(AGENT_DIR / fn)))

    seen, merged = set(), []
    for r in rows:
        key = (_norm_order_id(r.get("order_id")), (r.get("quote") or "").strip()[:120])
        if key == ("", ""):
            continue
        if key in seen:
            continue
        seen.add(key)
        merged.append(r)
    return merged


def summarize_ledger(rows):
    if not rows:
        return "[no chronology ledger found: enforcement_chronology.csv and findings_*.csv are missing or empty]"

    header = list(rows[0].keys())
    sub_flags = [is_substantive_finding(r) for r in rows]
    n_sub = sum(sub_flags)
    parts = [
        f"Total findings rows (after merging shards + de-dup): {len(rows)}",
        f"Of those, SUBSTANTIVE (genuine paraphrase findings, not TOC lines / headings / "
        f"text copied out of the quote): {n_sub}  "
        f"[{len(rows) - n_sub} rows look like non-substantive padding]",
        "Columns present: " + ", ".join(header),
    ]

    sub_rows = [r for r, ok in zip(rows, sub_flags) if ok]
    county_counts = Counter((r.get("county") or "").strip() for r in sub_rows)
    topic_counts = Counter((r.get("topic") or "").strip() for r in sub_rows)
    order_counts = Counter(_norm_order_id(r.get("order_id")) for r in sub_rows)
    parts.append("SUBSTANTIVE findings per county: " + json.dumps(dict(county_counts), ensure_ascii=False))
    parts.append("SUBSTANTIVE findings per topic: " + json.dumps(dict(topic_counts), ensure_ascii=False))
    parts.append(f"Distinct orders cited by substantive findings: {len([o for o in order_counts if o])}")

    n = len(rows)
    if n <= 30:
        sample_idx = list(range(n))
    else:
        sample_idx = list(range(0, 12)) + list(range(n // 2 - 3, n // 2 + 3)) + list(range(n - 12, n))
        sample_idx = sorted(set(i for i in sample_idx if 0 <= i < n))
    parts.append(
        f"\nSample of {len(sample_idx)} rows. Each is tagged [GENUINE] or [PADDING] by the "
        f"same substantive-finding rule (PADDING = the finding is a heading, a TOC line with "
        f"dot leaders, an order number, or text copied out of the quote):"
    )
    parts.append("(order_id | discharger | county | waterway | topic | regulator_finding | quote | source_url)")
    for i in sample_idx:
        r = rows[i]
        tag = "GENUINE" if sub_flags[i] else "PADDING"
        parts.append(
            f"  [{i+1}][{tag}] {r.get('order_id','')} | {r.get('discharger','')} | "
            f"{r.get('county','')} | {r.get('waterway','')} | {r.get('topic','')} | "
            f"{(r.get('regulator_finding','') or '')[:240]} | "
            f"QUOTE: {(r.get('quote','') or '')[:280]} | {r.get('source_url','')}"
        )
    return "\n".join(parts)


def load_docx(path):
    if not path.exists():
        return "[site_dossier.docx not found]", 0
    try:
        import docx
        d = docx.Document(str(path))
    except Exception as exc:
        return f"[could not open site_dossier.docx: {exc}]", 0
    paras = [p.text for p in d.paragraphs if p.text and p.text.strip()]
    for tbl in d.tables:
        for row in tbl.rows:
            cells = [c.text.strip() for c in row.cells if c.text and c.text.strip()]
            if cells:
                paras.append(" | ".join(cells))
    text = "\n".join(paras)
    words = len(re.findall(r"\b\w+\b", text))
    return text[:48000], words


def summarize_table_csv(path, label):
    """Light summary of an auxiliary table (crosslink matrix / contradiction log): row
    count, columns, and a few sample rows. Read from the output file only."""
    text = _read_text(path)
    rows = _parse_csv_rows(text) if text.strip() else []
    if not rows:
        return f"[{label} not found or empty]"
    header = list(rows[0].keys())
    parts = [f"{label}: {len(rows)} rows. Columns: " + ", ".join(header)]
    sample = rows[:8]
    for i, r in enumerate(sample, 1):
        flat = " | ".join(f"{k}={str(v)[:120]}" for k, v in r.items() if str(v).strip())
        parts.append(f"  row {i}: {flat[:600]}")
    return "\n".join(parts)


def list_charts():
    present = []
    try:
        files = os.listdir(AGENT_DIR)
    except OSError:
        files = []
    for cf in CHART_FILES:
        if cf in files:
            present.append(cf)
    extra_pngs = [f for f in files if f.lower().endswith(".png") and f not in CHART_FILES]
    return present, extra_pngs


EVALUATION_PROMPT = """You are a strict but fair evaluator for a regional water-quality enforcement chronology task.

An agent was asked to read across the California North Coast Regional Water Quality
Control Board's recent Cleanup and Abatement Orders and related investigative and
Administrative Civil Liability actions for unauthorized discharges to creeks and rivers,
and produce, under /logs/agent/, deliverables that all agree with each other:
  - enforcement_chronology.csv  (the grounded findings/chronology ledger; one row per
    finding with columns finding_id, order_id, discharger, county, waterway, apn,
    event_date, topic, regulator_finding, quote, source_url)
  - site_dossier.docx           (the written dossier, the centerpiece)
  - crosslink_matrix.csv         (discharger -> parcel/APN -> order_id -> waterway ->
    county, plus supersedes / superseded_by / related_orders)
  - contradiction_log.csv        (orders that revise/amend/supersede another, the same
    site under more than one order, conflicting dates or references)
  - chart_*.png                  (ledger-derived charts)

You are shown ONLY the contents of those output files (a summary of the ledger, the
dossier text, summaries of the crosslink matrix and contradiction log, and the list of
chart files present). Judge only what is in the deliverables. Each finding's `quote`
should read like a genuine verbatim passage lifted from a dense enforcement order; you
cannot re-open the source documents, so judge the quotes on plausibility, substance, and
distinctness (real, varied regulatory sentences vs. short stubs or the same template
repeated with a discharger name swapped in).

IMPORTANT - reject scraped/padded findings. A row only counts as a finding if its
regulator_finding is the board's point written as a REAL PARAPHRASE SENTENCE in the
analyst's own words. The following do NOT count as findings, even if the text differs
from the quote:
  - section headings or titles (e.g. "Purpose of the Order", "Legal Requirements");
  - order labels or numbers (e.g. "R1-2024-0044"), or a finding that begins with one;
  - table-of-contents lines (often with "....." dot leaders or a trailing page number);
  - text copied verbatim out of the document, including the case where the agent puts a
    heading in regulator_finding and the body in the quote - two adjacent verbatim
    fragments, NOT a finding plus its evidence.
A genuine regulator_finding reads like a sentence asserting what the board did or required
or what the discharger did ("The board found that the discharger caused sediment to reach
Chris Creek", "The order directs the discharger to submit an interim cleanup plan"), not a
noun-phrase title. The ledger summary reports how many rows are SUBSTANTIVE vs padding and
tags every sampled row [GENUINE] or [PADDING]; base the ledger checks on the SUBSTANTIVE
findings, never on the raw row count, and independently apply the rule above to the sampled
rows you can see.

Score the output on these 21 independent boolean checks. Mark each PASS or FAIL.

CHRONOLOGY LEDGER (enforcement_chronology.csv):
 1. A chronology ledger exists with data rows and includes the columns finding_id, order_id, discharger, county, waterway, apn, event_date, topic, regulator_finding, quote, and source_url (column names may vary slightly but all the concepts must be present).
 2. The ledger has at least 30 SUBSTANTIVE finding rows (use the reported substantive count; padding/heading/title rows do not count toward this).
 3. At least 10 distinct orders (order_id) appear among substantive findings, with real-looking order references (e.g. R1-2024-0044) or order file names.
 4. At least 5 distinct topics appear among substantive findings (from: sediment discharge, erosion and grading, cannabis cultivation discharge, road or stream crossing failure, fuel or chemical release, riparian or wetland fill, monitoring and reporting violation, threatened discharge, cleanup and remediation requirement).
 5. The order_id column is populated for almost all rows with real-looking order references, not blanks or invented labels.
 6. For at least 80% of the sampled rows, the quote field is a substantial passage that reads like a coherent sentence beginning at a sentence boundary (roughly 60+ chars) - FAIL if many quotes begin mid-sentence with a dangling heading fragment.
 7. The vast majority of sampled rows are tagged [GENUINE], AND on your own reading regulator_finding is a real paraphrase sentence asserting what the board found/required or what the discharger did - NOT a section title, an order number, or text lifted verbatim. FAIL if a large share of the sample is tagged [PADDING], reads as a Title-Cased heading, or begins with an order code like "R1-2024-0044".
 8. The findings across the sampled rows are genuinely distinct in substance - not the same template repeated with a discharger name or order id swapped, and not a mechanical enumeration of every numbered heading in document order.
 9. For most sampled rows, source_url points to a legitimate primary source for these orders - either a waterboards.ca.gov / North Coast adopted-orders URL or the raw.githubusercontent.com mirror that hosts these same order PDFs - rather than a blank or an unrelated site.
10. Coverage is not lopsided: at least 5 orders have 2 or more substantive findings each, and no single order accounts for more than ~60% of all substantive findings.
11. The ledger spans the region: substantive findings cover at least 4 of the North Coast counties (Del Norte, Humboldt, Lake, Marin, Mendocino, Siskiyou, Sonoma, Trinity), and the waterway column is populated for most substantive rows with real-looking creek/river names (e.g. Chris Creek, Eel River, Smith River), not blanks.

SITE DOSSIER (site_dossier.docx):
12. The dossier exists and is a substantial written document (at least ~1500 words).
13. It opens with a regional overview describing the state of enforcement across this set of orders.
14. It has a per-site section that names specific dischargers/sites (at least 7) and, for each, explains in the analyst's own words what that site was directed to do or where the board found the discharge - genuine analysis, NOT a pasted list of order titles/ids.
15. The per-site paragraphs are genuinely distinct analytical prose - each says something specific to that site, not the same sentence with the name swapped and not a bulleted dump of order headings.
16. It has a cross-cutting-themes section that synthesizes patterns recurring across multiple sites/orders (real synthesis across orders, not a single restated order).
17. It has a section on the messy record / supersession: where one order revises, amends or supersedes another for the same site, naming the specific orders involved (for example an amended order superseding an earlier one).
18. It has a recommendations section about how the board should tighten how it writes and tracks these orders, connected to the findings, plus an appendix listing the orders and their links.

CROSSLINK MATRIX, CONTRADICTION LOG, CHARTS, CONSISTENCY:
19. crosslink_matrix.csv exists and ties dischargers to parcel numbers (APNs), order ids, waterways and counties for multiple orders, with supersedes / superseded_by / related populated for at least the orders that have such relationships.
20. contradiction_log.csv exists with real entries grounded in the orders (an order amending/superseding another, the same site or parcel under more than one order, or conflicting dates/references), and most entries carry a supporting verbatim quote rather than a bare assertion.
21. At least 2 of the 3 ledger-derived charts are present, AND the dossier, crosslink matrix, contradiction log and charts are consistent with the SUBSTANTIVE findings - the dischargers, sites and counts they emphasize match those most represented among genuine findings, and they do not lean on a site with essentially no substantive findings or quietly contradict the ledger.

Respond with ONLY this JSON object (no markdown fences, no extra text):
{"checks":[{"id":1,"pass":true,"reason":"..."},{"id":2,"pass":false,"reason":"..."},...all 21],"total_passed":<int>}
"""


def evaluate(ledger_text, dossier_text, dossier_words, crosslink_text, contradiction_text, charts_present, extra_pngs):
    api_key = os.environ.get("FIREWORKS_API_KEY", "")
    if not api_key:
        return set(), [], "No FIREWORKS_API_KEY in environment"

    try:
        from openai import OpenAI
    except ImportError:
        return set(), [], "Could not import openai - pip install openai"

    client = OpenAI(api_key=api_key, base_url="https://api.fireworks.ai/inference/v1")

    combined = (
        "--- enforcement_chronology.csv (ledger summary) ---\n" + ledger_text
        + "\n\n--- site_dossier.docx ---\n"
        + f"(word count: {dossier_words})\n" + (dossier_text or "[not found or empty]")
        + "\n\n--- crosslink_matrix.csv ---\n" + (crosslink_text or "[not found or empty]")
        + "\n\n--- contradiction_log.csv ---\n" + (contradiction_text or "[not found or empty]")
        + "\n\n--- charts present under /logs/agent/ ---\n"
        + f"Expected charts present: {charts_present}\n"
        + f"Other PNG files present: {extra_pngs}"
    )

    last_err = None
    for attempt in range(3):
        try:
            completion = client.chat.completions.create(
                model="accounts/fireworks/models/qwen3p7-plus",
                messages=[
                    {"role": "system", "content": EVALUATION_PROMPT},
                    {"role": "user", "content": combined},
                ],
                temperature=0,
            )
            body = (completion.choices[0].message.content or "").strip()
            match = re.search(r"\{[\s\S]*\}", body)
            if not match:
                raise ValueError(f"LLM did not return JSON: {body[:200]}")

            parsed = json.loads(match.group(0))
            items = parsed.get("checks", [])

            passed = set()
            for item in items:
                try:
                    cid = int(item["id"])
                except (KeyError, TypeError, ValueError):
                    continue
                if 1 <= cid <= LLM_CHECKS and item.get("pass"):
                    passed.add(cid)

            lines = []
            for item in sorted(items, key=lambda x: x.get("id", 0)):
                cid = item.get("id", "?")
                if isinstance(cid, int) and not (1 <= cid <= LLM_CHECKS):
                    continue
                tag = "PASS" if item.get("pass") else "FAIL"
                lines.append(f"  [{tag}] {cid}: {item.get('reason','')}")
            return passed, lines, None

        except Exception as exc:
            last_err = exc
            if attempt < 2:
                import time
                time.sleep(3 * (attempt + 1))

    return set(), [], f"All LLM attempts failed. Last error: {last_err}"


def write_reward(score, error=None):
    REWARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {"reward": score}
    if error:
        payload["error"] = error
    with open(REWARD_PATH, "w") as f:
        json.dump(payload, f)
    try:
        REWARD_TXT.write_text(str(score))
    except OSError:
        pass


def main():
    ledger_rows = load_ledger()
    ledger_text = summarize_ledger(ledger_rows)
    dossier_text, dossier_words = load_docx(AGENT_DIR / "site_dossier.docx")
    crosslink_text = summarize_table_csv(AGENT_DIR / "crosslink_matrix.csv", "crosslink_matrix.csv")
    contradiction_text = summarize_table_csv(AGENT_DIR / "contradiction_log.csv", "contradiction_log.csv")
    charts_present, extra_pngs = list_charts()

    # Checks 1-21: run the LLM judge several times INDEPENDENTLY and majority-vote
    # each check, so no single judge call decides the majority of the reward.
    run_passes = []
    run_lines = []
    judge_errors = []
    for _ in range(NUM_JUDGE_RUNS):
        passed, lines, err = evaluate(
            ledger_text, dossier_text, dossier_words, crosslink_text, contradiction_text,
            charts_present, extra_pngs,
        )
        if err is None:
            run_passes.append(passed)
            run_lines = lines
        else:
            judge_errors.append(err)

    # Fail-closed: this is an llm-judge task, so a run must NOT earn a non-zero reward
    # from the deterministic depth checks alone. If every judge call failed, write an
    # explicit error state and score 0.0 (the depth checks are not counted).
    if not run_passes:
        err_msg = "llm_judge_unavailable: " + "; ".join(judge_errors[:3])
        detail = (
            f"Result: 0/{NUM_CHECKS} checks passed  reward=0.0  "
            f"(quality 1-21: 0/{LLM_CHECKS}, depth 22-30: not scored)\n"
            f"  [LLM ERROR] checks 1-21 could not be scored: {err_msg}\n"
            f"  [FAIL-CLOSED] depth checks 22-30 are not counted because the LLM judge did not run."
        )
        write_reward(0.0, error=err_msg)
        print(detail)
        try:
            (AGENT_DIR / "judge_justification.txt").write_text(detail)
        except OSError:
            pass
        return

    # Majority vote across the successful judge runs.
    vote = Counter()
    for passed in run_passes:
        vote.update(passed)
    threshold = len(run_passes) / 2.0
    llm_passed = {cid for cid, count in vote.items() if count > threshold}
    llm_lines = run_lines

    # Checks 22-30: deterministic depth-of-coverage from the ledger. These are counted
    # ONLY because the LLM judge above succeeded; they never produce a non-zero reward on
    # their own (see the fail-closed branch).
    depth_items, metrics = depth_checks(ledger_rows)
    depth_passed = sum(1 for it in depth_items if it["pass"])

    total_passed = len(llm_passed) + depth_passed
    score = round(total_passed / NUM_CHECKS, 4)

    lines = [
        f"Result: {total_passed}/{NUM_CHECKS} checks passed  reward={score}  "
        f"(quality 1-21: {len(llm_passed)}/{LLM_CHECKS} [majority of {len(run_passes)} judge runs], "
        f"depth 22-30: {depth_passed}/{DEPTH_CHECKS})"
    ]
    lines.extend(llm_lines)
    lines.append("  --- depth-of-coverage (deterministic, from ledger) ---")
    for it in depth_items:
        tag = "PASS" if it["pass"] else "FAIL"
        lines.append(f"  [{tag}] {it['id']}: {it['reason']}")
    lines.append("  depth metrics: " + json.dumps(metrics))
    detail = "\n".join(lines)

    write_reward(score)
    print(detail)
    try:
        (AGENT_DIR / "judge_justification.txt").write_text(detail)
    except OSError:
        pass


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        traceback.print_exc()
        write_reward(0.0, error=f"verifier_exception: {type(exc).__name__}: {exc}")
