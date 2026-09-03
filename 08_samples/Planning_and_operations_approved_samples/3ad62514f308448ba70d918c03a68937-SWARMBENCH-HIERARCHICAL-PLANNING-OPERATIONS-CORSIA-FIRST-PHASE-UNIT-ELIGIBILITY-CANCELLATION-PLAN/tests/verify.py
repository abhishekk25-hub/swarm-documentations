#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import sys
import traceback
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

REQUIREMENT_TONNES = 4_000_000
FIRST_PHASE_LABEL = "CORSIA 2024-2026 (First Phase)"
PILOT_PHASE_LABEL = "CORSIA 2021-2023 (Pilot Phase)"

# The programme names the Council uses, against the registry code the record carries.
PROGRAMME_NAMES = {
    "ACR": "American Carbon Registry",
    "ART": "Architecture for REDD+ Transactions",
    "CAR": "Climate Action Reserve",
    "GOLD": "Gold Standard",
    "ISO": "Isometric",
    "VCS": "Verified Carbon Standard",
}

# The unit name each approved programme's own clauses are written in. A clause that opens
# with "VERs issued to ..." is a Gold Standard clause wherever the extracted text has landed
# it, which is what lets a clause be attributed to the programme that actually carries it
# rather than to whichever heading happens to precede it in the PDF text layer.
UNIT_TOKENS = {"ACR": "ERTs", "ART": "ART credits", "CAR": "CRTs",
               "GOLD": "VERs", "ISO": "Isometric Credits", "VCS": "VCUs"}

# Capacity as the registry states it in its own prose, in the units the registries use.
# "MWh" and "GWh" are energy, not capacity, and must not be read as a capacity figure.
CAPACITY_RX = re.compile(r"(\d{1,4}(?:[.,]\d{1,3})?)\s*(?:MW(?:e|p|th)?|megawatts?)\b")
# Whether the activity the registry describes is electricity generation at all. The same
# Renewable Energy scope covers geothermal district heating, which generates no electricity
# and is therefore not caught by a clause about grid-connected electricity generation.
GENERATION_RX = re.compile(r"electricit|\bGWh\b|\bMWh\b|power plant|power project|"
                           r"power generation|grid", re.I)


def _capacity_mw(dossier: str):
    """Every capacity figure the registry's own description of the activity states, in MW."""
    out = []
    for raw in CAPACITY_RX.findall(dossier or ""):
        if "," in raw and len(raw.split(",")[1]) == 3:      # thousands separator
            raw = raw.replace(",", "")
        v = num(raw.replace(",", "."))
        if v is not None:
            out.append(v)
    return out


def _field_is(field, values):
    """A clause the record's own categorical fields settle on their own."""
    def test(rec, dossier, rules):
        return txt(rec.get(field)) in values
    return test


def _grid_capacity_over_limit(rec, dossier, rules):
    """The clause that turns on installed capacity.

    Nothing in the packaged record carries a capacity, so this is settled from the
    registry's own description of the activity: whether that description is of grid
    electricity generation at all, and what capacity it states. Both are prose.
    """
    if txt(rec.get("scope")) != "Renewable Energy" or not dossier:
        return False
    if not GENERATION_RX.search(dossier):
        return False
    caps = _capacity_mw(dossier)
    limit = rules.get("capacity_limit_mw")
    return bool(caps) and limit is not None and max(caps) > limit


# The exclusion clauses the packaged record can be tested against. Each is keyed by the
# wording the Council uses, so a clause that is not in the document under a given programme
# cannot exclude that programme's units. Where `units` is given the clause is attributed to
# the programme whose unit name opens it; otherwise it is attributed to the programme entry
# the wording sits in.
EXCLUSION_CLAUSES = {
    "california_registry_offset_credits": (
        ("California and Washington Registry Offset Credits", "California Registry Offset Credits"),
        _field_is("arb_wa_project", ("ARB Compliance",)), False),
    "california_early_action": (
        ("California Early Action Offset Credits",),
        _field_is("arb_wa_project", ("ARB Early Action",)), False),
    "engineered_removals": (
        ("Engineered Removals",),
        _field_is("scope", ("Engineered Removal",)), False),
    "grid_connected_capacity": (
        ("grid-connected renewable electricity generation/supply",),
        _grid_capacity_over_limit, True),
}

# The Council admits an authorisation only where the host country authorised the unit for
# use in CORSIA. The registries record that permission in several wordings, and the purpose
# named in the wording is what decides it: an authorisation for a country's own NDC, or one
# the host country has withdrawn, is not an authorisation for CORSIA.
AUTH_FOR_CORSIA = ("authorized for corsia", "intl mitigation purposes",
                   "international mitigation purposes")
AUTH_NOT_CORSIA = ("withdrawn by host country", "ndc use")

# Each programme's Scope of Eligibility excludes activity and unit classes of its own. These
# are the classes the packaged registry record can be tested against; each is quoted in the
# Council document under the programme named.
CEEU_ID = "ICAO-CEEU-2026-04"

# The columns of the register that carry a judgement rather than an identity. These are the
# fields a constant fill would flatten, so it is their spread across the pool that is scored.
ASSESSMENT_COLUMNS = ("programme_approved", "dates_test", "scope_test", "authorisation_test",
                      "availability_test", "verdict")

REGISTER_COLUMNS = ["block_id", "project_id", "registry", "vintage_year", "quantity_available",
                    "programme_approved", "dates_test", "scope_test", "authorisation_test",
                    "availability_test", "verdict", "governing_source_id", "governing_quote"]
SCHEDULE_COLUMNS = ["sequence_no", "block_id", "project_id", "registry", "vintage_year",
                    "quantity_to_cancel", "cumulative_tonnes"]
REFERRAL_KEYS = ["block_id", "question", "programme_position", "programme_quote",
                 "council_position", "council_quote", "recommendation"]
NOTE_HEADINGS = ["Position", "What the Council requires", "Pool disposition", "Referrals",
                 "Cancellation schedule", "Exposure and limitations"]
DISPOSITION_KEYS = ["blocks_assessed", "blocks_cleared", "blocks_referred", "blocks_refused",
                    "tonnes_cleared", "tonnes_scheduled", "requirement_shortfall"]
TEST_VALUES = {"PASS", "FAIL", "UNRESOLVED"}
VERDICTS = {"CLEARED", "REFERRED", "REFUSED"}
# The longest single claim the programme labelling extract carries, in words.
LABEL_QUOTE_MIN_WORDS = 4

PLACEHOLDER = re.compile(r"\b(?:tbd|to be determined|todo|lorem ipsum|placeholder|fill me|"
                         r"insert here|your answer|xxx+)\b", re.I)
BLOCK_RX = re.compile(r"\bCB-\d{3}\b")
WORD_RX = re.compile(r"[A-Za-z0-9'\-]+")
RULE_TOKENS = ("eligible", "issued", "exclusion", "authorized", "authorised", "crediting period",
               "emissions reductions", "cancellation", "scope", "compliance period",
               "double-claiming", "double claiming", "corresponding adjustment")


DECIDING_TOKENS = {
    "dates_test": ("crediting period", "2016", "emissions reductions that occurred",
                   "31 december", "1 january"),
    "scope_exclusion": ("exclusion", "registry offset credits", "early action", "rocs", "eaocs",
                        "engineered removals", "sectoral scope"),
    "scope_identification": ("identified as such", "scope of eligibility", "compliance period",
                             "eligible for cancellation"),
    "authorisation_test": ("authoris", "authoriz", "double-claim", "double claim",
                           "corresponding adjustment", "attestation", "host country"),
    "availability_test": ("cancellation", "cancelled", "unit"),
}


def first_phase_section(ceeu: str) -> str:
    """The part of the Council document that governs the 2024-2026 compliance period."""
    start = ceeu.find("II. CORSIA Eligible Emissions Units for the 2024")
    if start < 0:
        start = ceeu.find("2024 -2026 Compliance Period")
    if start < 0:
        return ""
    end = ceeu.find("III.", start)
    return ceeu[start:end if end > start else len(ceeu)]


def derive_rules(ceeu: str) -> dict:
    """Read the rule set out of the pinned document rather than carrying it as constants.

    The dates, the approved programmes and the exclusion clauses that bear on the packaged
    record are all taken from the first-phase section at grading time, so a change in the
    document changes what the grader expects.
    """
    sec = first_phase_section(ceeu)
    rules: dict[str, Any] = {"section_found": bool(sec)}

    m = re.search(r"started their first crediting period from 1 January (\d{4})", sec)
    rules["crediting_start_from"] = int(m.group(1)[:4]) if m else None

    m = re.search(r"emissions reductions that occurred from 1 January (\d{4}) through "
                  r"31 December (\d{4})", sec)
    rules["reduction_window"] = (int(m.group(1)), int(m.group(2))) if m else None

    m = re.search(r"maximum output capacity greater than (\d+) megawatts? of electricity", sec)
    rules["capacity_limit_mw"] = float(m.group(1)) if m else None

    approved = set()
    for code, name in PROGRAMME_NAMES.items():
        if name in sec:
            approved.add(code)
    rules["approved_registries"] = approved

    # Which exclusion clause appears under which programme, read from that programme's own
    # entry rather than assumed to apply across the document.
    spans = []
    for code, name in PROGRAMME_NAMES.items():
        i = sec.find(name)
        if i >= 0:
            spans.append((i, code))
    spans.sort()
    exclusions: dict[str, list] = {code: [] for code in PROGRAMME_NAMES}
    for n, (i, code) in enumerate(spans):
        j = spans[n + 1][0] if n + 1 < len(spans) else len(sec)
        body = sec[i:j]
        for key, (phrases, test, by_unit) in EXCLUSION_CLAUSES.items():
            if not by_unit and any(ph in body for ph in phrases):
                exclusions[code].append((key, test))
    # A clause that names the unit it excludes carries its own attribution. The document is
    # a two-column PDF and the extracted text puts one programme's heading inside another
    # programme's exclusion list, so a clause opening "VERs issued to ..." is read as the
    # Gold Standard clause it is rather than as the clause of the nearest heading. The same
    # wording under a programme this pool does not draw on attaches to nothing.
    for key, (phrases, test, by_unit) in EXCLUSION_CLAUSES.items():
        if not by_unit:
            continue
        for phrase in phrases:
            for m in re.finditer(re.escape(phrase), sec):
                lead = sec[max(0, m.start() - 90):m.start()]
                owner = max(((lead.rfind(tok), code) for code, tok in UNIT_TOKENS.items()),
                            key=lambda p: p[0])
                if owner[0] >= 0 and (key, test) not in exclusions[owner[1]]:
                    exclusions[owner[1]].append((key, test))
    rules["exclusions"] = exclusions
    return rules


# Where a scope exclusion decides a block, the clause that excludes it is what its quotation
# has to carry. Merging the exclusion vocabulary into one category would let a sentence about
# registry offset credits stand behind a block excluded as an engineered removal.
CLAUSE_TOKENS = {
    "california_registry_offset_credits": ("registry offset credits", "rocs", "california"),
    "california_early_action": ("early action", "eaocs"),
    "engineered_removals": ("engineered removals", "sectoral scope 16", "sectoral scope"),
    "grid_connected_capacity": ("grid-connected renewable electricity", "maximum output capacity",
                                "megawatt"),
}


# A clause the Council writes about one programme names that programme's own unit. A quote
# carrying "VCUs" is a sentence about Verified Carbon Standard units and cannot be the
# sentence that decides a Climate Action Reserve block, however well its vocabulary matches
# the test. Sentences that name no unit at all are the document's programme-neutral wording
# and are not attributed to anyone.
UNIT_RX = {code: re.compile(r"\b" + re.escape(tok) + r"\b") for code, tok in UNIT_TOKENS.items()}


def quote_programmes(quote: str) -> set:
    """The programmes a quotation names by their own unit, empty where it names none."""
    return {code for code, rx in UNIT_RX.items() if rx.search(quote or "")}


def quote_fits_programme(quote: str, registry: str) -> bool:
    """A quotation may stand behind a block only if it is not about a different programme."""
    named = quote_programmes(quote)
    return not named or registry in named


def rules_of_quote(ctx) -> dict:
    """Every deciding rule each governing sentence is made to stand behind, across the register.

    One sentence covering rows that are decided by different rules is a sentence being reused
    as a category label rather than quoted as the rule that decided a row. The rule is what
    this is tested against rather than the verdict, because the same sentence legitimately
    decides rows that ended differently: the condition the Council attaches to a programme is
    the rule that clears a block whose record shows it met and the rule that refers a block
    whose record is silent on it, and a register that quotes it for both has quoted correctly.
    A sentence carried across two different rules is still refused.
    """
    out: dict = {}
    for r in ctx["register_rows"]:
        t = ctx["truth"].get(txt(r.get("block_id")))
        if t is None:
            continue
        out.setdefault(trimmed(txt(r.get("governing_quote"))).lower(), set()).add(deciding_key(t))
    return out


def deciding_key(t: dict) -> tuple:
    """The rule that settles a block: its test, and where a scope exclusion decides it, the
    specific clause. Two blocks excluded under different clauses are not the same case."""
    test = deciding_test(t)
    return (test, t.get("excluded_by", "") if test == "scope_exclusion" else "")


def deciding_tokens(t: dict) -> tuple:
    """The wording a quotation must carry to count as deciding this block."""
    test, clause = deciding_key(t)
    if clause and clause in CLAUSE_TOKENS:
        return CLAUSE_TOKENS[clause]
    return DECIDING_TOKENS[test]


def deciding_test(t: dict) -> str:
    """The test that actually settles a block, which is the one its quotation must carry."""
    if t["dates_test"] == "FAIL":
        return "dates_test"
    if t["scope_test"] == "FAIL":
        return "scope_exclusion" if t.get("excluded_by") else "scope_identification"
    if t["availability_test"] == "FAIL":
        return "availability_test"
    return "authorisation_test"


def spearman(pairs) -> float:
    pairs = [(a, b) for a, b in pairs if a is not None and b is not None]
    n = len(pairs)
    if n < 8:
        return 0.0

    def ranked(vals):
        order = sorted(range(n), key=lambda i: vals[i])
        out = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and vals[order[j + 1]] == vals[order[i]]:
                j += 1
            avg = (i + j) / 2.0
            for k in range(i, j + 1):
                out[order[k]] = avg
            i = j + 1
        return out

    xs, ys = ranked([q[0] for q in pairs]), ranked([q[1] for q in pairs])
    mx, my = sum(xs) / n, sum(ys) / n
    top = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    den = (sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys)) ** 0.5
    return 0.0 if den == 0 else abs(top / den)


def txt(v: Any) -> str:
    return "" if v is None else str(v).strip()


def frac(n: float, d: float) -> float:
    return 0.0 if d <= 0 else max(0.0, min(1.0, n / d))


def mean(vals) -> float:
    vals = list(vals)
    return sum(vals) / len(vals) if vals else 0.0


def num(v: Any):
    try:
        f = float(str(v).replace(",", "").strip())
        return None if math.isnan(f) or math.isinf(f) else f
    except (TypeError, ValueError):
        return None


def year(v: Any):
    f = num(v)
    return int(f) if f is not None else None


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").replace("’", "'").replace("‘", "'")
                  .replace("“", '"').replace("”", '"').replace("–", "-")
                  .replace("—", "-")).strip()


def words(s: str):
    return WORD_RX.findall(s or "")


# The text layer of a two-column PDF glues each footnote marker onto the word before it, so
# the sentence a reader sees as "from 1 January 2016 and in respect of" is "from 1 January
# 20167 and in respect of" in the extract, and "estimated to have" is "estimated14 to have".
FOOTNOTE_MARK = re.compile(r"(?<=[A-Za-z])\d{1,3}(?:\s*,\s*\d{1,3})*")
FOOTNOTE_YEAR = re.compile(r"\b((?:1[89]|20)\d{2})\d{1,2}\b")


def canon(s: str) -> str:
    """A quotation reduced to the sequence of words it is made of.

    The brief offers the same Council document as a PDF and as text extracted from it, so a
    sentence copied correctly out of either has to round-trip. Dropping the extract's
    footnote markers and its punctuation before comparing does that; it does not admit a
    sentence the document does not contain, because the whole word sequence still has to be
    there in order.
    """
    t = FOOTNOTE_YEAR.sub(r"\1", norm(s).lower())
    return " ".join(re.findall(r"[a-z0-9]+", FOOTNOTE_MARK.sub("", t)))


def source_id(v: Any) -> str:
    """The source identifier a row attributes its quotation to.

    sources.json names the capture and puts the same name on both files it was taken from,
    so a row citing the identifier, the file it read or the path to it is citing the same
    document and is read as such.
    """
    s = txt(v).replace("\\", "/").rsplit("/", 1)[-1]
    return re.sub(r"\.(?:txt|pdf|md|json)$", "", s, flags=re.I).strip()


def in_ceeu(ctx, quote: str) -> bool:
    """Whether a quotation is verbatim in the part of the Council document that governs the
    compliance period this task is about.

    The brief asks for the sentence that decides a first-phase block, and the document says
    different things about the same programme in its pilot-phase, first-phase and
    second-phase sections, with a general preamble above all three. A sentence lifted from
    the preamble, or from the section governing another compliance period, is present in the
    file but is not the rule the row applied, so the round trip is scoped to the first-phase
    section rather than run over the whole document. That section carries every programme's
    entry, its eligibility timeframe, its eligible unit dates and its scope of eligibility
    with the exclusions under it, so every sentence a correct row needs is inside it. If the
    section cannot be located in the pinned snapshot the scope falls back to the whole
    document, so a change in the document's headings degrades to the previous behaviour
    rather than failing every row.
    """
    q = trimmed(quote)
    if not q:
        return False
    return q in ctx["ceeu_first"] or canon(q) in ctx["ceeu_first_canon"]


def trimmed(s: str) -> str:
    """A quoted run with the writer's own quotation marks and sentence punctuation taken off,
    so that a sentence copied correctly is not failed for the comma the note put after it."""
    out = norm(s)
    while True:
        stripped = out.strip(" .,;:!?()[]").strip("\"“”‘’'")
        if stripped == out:
            return out
        out = stripped


def read_csv(path: Path):
    if not path.is_file():
        return []
    try:
        with path.open(newline="", encoding="utf-8", errors="replace") as fh:
            return list(csv.DictReader(fh))
    except OSError:
        return []


def header_of(path: Path):
    if not path.is_file():
        return []
    try:
        with path.open(newline="", encoding="utf-8", errors="replace") as fh:
            return next(csv.reader(fh), [])
    except OSError:
        return []


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def discriminating(hits: dict, subset: list) -> float:
    overall = frac(sum(1 for v in hits.values() if v), len(hits)) if hits else 0.0
    if not subset:
        return overall
    hard = frac(sum(1 for a in subset if hits.get(a)), len(subset))
    return math.sqrt(overall * hard)


def _length(v: Any):
    """A CSS/SVG length read as a number, ignoring the unit it is written in."""
    m = re.match(r"\s*(-?\d+(?:\.\d+)?)", str(v or ""))
    return float(m.group(1)) if m else None


# A drawing with neither a viewBox nor a stated size still has a user coordinate system, and
# anything drawn far outside it is clipped rather than seen. Bounding an unstated canvas
# generously keeps a legitimate page from being punished for not declaring one, while still
# refusing a channel whose values run to registry tonnages.
DEFAULT_CANVAS = (1000.0, 1000.0)


def _canvas_of(attrs: dict):
    """The user coordinate space the outermost svg draws in, from its viewBox or its size."""
    vb = re.findall(r"-?\d+(?:\.\d+)?", attrs.get("viewbox", ""))
    if len(vb) == 4 and float(vb[2]) > 0 and float(vb[3]) > 0:
        return (float(vb[2]), float(vb[3]))
    w, h = _length(attrs.get("width")), _length(attrs.get("height"))
    if w and h and w > 0 and h > 0 and "%" not in attrs.get("width", "") \
            and "%" not in attrs.get("height", ""):
        return (w, h)
    return None


def canvas_of(ctx) -> tuple:
    doc = ctx.get("doc")
    return (doc.canvas if doc and doc.canvas else DEFAULT_CANVAS)


def within(values, limit: float, low_ok: float = -0.1, high_ok: float = 1.1) -> bool:
    """Whether a geometric channel stays inside the canvas it is drawn on.

    A mark placed at ten times the width of the drawing is off the page: the channel carries
    the number but shows the committee nothing, so it is not an encoding of the pool.
    """
    vals = [v for v in values if v is not None]
    return bool(vals) and all(low_ok * limit <= v <= high_ok * limit for v in vals)


class Doc(HTMLParser):
    SHAPE_TAGS = {"circle", "rect", "ellipse", "path", "polygon", "line", "polyline", "g", "use"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.attrs_list, self.json_blocks, self.text_parts, self.tags = [], {}, [], Counter()
        self.canvas = None
        self._svg = 0
        self._mode = None
        self._id = None

    def handle_starttag(self, tag, attrs):
        t = tag.lower()
        d = {k.lower(): (v or "") for k, v in attrs}
        self.tags[t] += 1
        if t == "svg":
            if self._svg == 0 and self.canvas is None:
                self.canvas = _canvas_of(d)
            self._svg += 1
        if t == "script" and "json" in d.get("type", "").lower():
            self._mode, self._id = "json", d.get("id", "")
        elif t in self.SHAPE_TAGS:
            d["__tag__"] = t
            d["__in_svg__"] = self._svg > 0
            self.attrs_list.append(d)

    def handle_endtag(self, tag):
        if tag.lower() == "svg" and self._svg:
            self._svg -= 1
        self._mode = self._id = None

    def handle_data(self, data):
        if self._mode == "json" and self._id:
            self.json_blocks[self._id] = self.json_blocks.get(self._id, "") + data
        elif self._mode is None:
            self.text_parts.append(data)


def embedded_table(doc, block_id):
    raw = doc.json_blocks.get(block_id) if doc else None
    if not raw:
        return None
    try:
        blob = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return blob if isinstance(blob, list) and any(isinstance(d, dict) and d for d in blob) else None


def hidden(attrs: dict, canvas: tuple = DEFAULT_CANVAS) -> bool:
    """Whether a mark is one the committee cannot actually see.

    A mark of no size is invisible; so, for the purpose of reading a pool off a picture, is a
    mark drawn larger than the whole canvas, which covers the drawing rather than sitting in
    it. Both are refused, so neither end of the range can carry an encoding for free.
    """
    style = attrs.get("style", "").lower().replace(" ", "")
    if "display:none" in style or "visibility:hidden" in style or "opacity:0" in style:
        return True
    ceiling = max(canvas)
    for key in ("width", "height", "r"):
        v = _length(attrs.get(key, ""))
        if v is not None and (v <= 0 or v > ceiling):
            return True
    return False


def external_references(html: str) -> list:
    """Every resource the page would have to fetch from elsewhere in order to render.

    The brief asks for one self-contained page, because the committee reads it off a screen
    with no access to whatever machine wrote it. A fragment target and a data URI are part of
    the file itself; anything else named in a src, an href, a CSS url() or an @import is not,
    and a page that depends on one of those is not the page the brief asked for.
    """
    out = []
    for rx in (r"""(?:src|href|xlink:href)\s*=\s*["']([^"']*)["']""",
               r"""url\(\s*["']?([^"')]+)["']?\s*\)"""):
        for m in re.finditer(rx, html or "", re.I):
            ref = m.group(1).strip()
            if ref and not ref.startswith("#") and not ref.lower().startswith("data:"):
                out.append(ref)
    out += re.findall(r"@import\b", html or "", re.I)
    return out


def build_context(input_dir: Path, agent_dir: Path) -> dict:
    pool = read_csv(input_dir / "candidate_pool.csv")
    labels = {r["project_id"]: r.get("programme_labels", "")
              for r in read_csv(input_dir / "programme_labelling_extract.csv")}
    ceeu = norm(read_text(input_dir / "sources" / f"{CEEU_ID}.txt"))
    # The scope every quotation attributed to the Council document is round-tripped against:
    # the section governing the 2024-2026 compliance period, falling back to the whole
    # document only where that section cannot be located in the snapshot.
    ceeu_first = first_phase_section(ceeu) or ceeu
    dossier_raw = read_text(input_dir / "activity_dossiers.md")
    dossiers: dict[str, str] = {}
    for chunk in re.split(r"\n(?=## )", dossier_raw):
        m = re.match(r"##\s*([A-Za-z0-9\-]+)", chunk.strip())
        if m:
            dossiers[m.group(1)] = norm(chunk)
    sources = {
        CEEU_ID: ceeu,
        "ICAO-TAB-SUMMARY-2026-04": norm(read_text(input_dir / "sources" / "ICAO-TAB-SUMMARY-2026-04.txt")),
        "ICAO-EUC-DOC09": norm(read_text(input_dir / "sources" / "ICAO-EUC-DOC09.txt")),
    }

    rules = derive_rules(ceeu)
    crediting_from = rules["crediting_start_from"] or 2016
    window = rules["reduction_window"] or (2021, 2026)
    approved_registries = rules["approved_registries"] or set(PROGRAMME_NAMES)
    exclusions = rules["exclusions"]

    truth: dict[str, dict] = {}
    for r in pool:
        bid = txt(r.get("block_id"))
        label = labels.get(txt(r.get("project_id")), "")
        fv, vy = year(r.get("first_project_vintage")), year(r.get("vintage_year"))
        qty = num(r.get("quantity_available")) or 0.0
        registry = txt(r.get("registry"))
        approved = "PASS" if registry in approved_registries else "FAIL"
        dates = "PASS" if (fv is not None and fv >= crediting_from and vy is not None
                           and window[0] <= vy <= window[1]) else "FAIL"

        # Scope is two questions the Council asks of the same activity. Has the programme
        # identified the unit for this compliance period, and does the activity fall outside
        # the exclusions that programme's own Scope of Eligibility carries?
        excluded_by = ""
        entry = dossiers.get(txt(r.get("project_id")), "")
        for key, test in exclusions.get(registry, ()):
            if test(r, entry, rules):
                excluded_by = key
                break
        identified = FIRST_PHASE_LABEL in label
        scope = "PASS" if identified and not excluded_by else "FAIL"

        low = label.lower()
        if any(k in low for k in AUTH_NOT_CORSIA) and not any(k in low for k in AUTH_FOR_CORSIA):
            auth = "FAIL"
        elif any(k in low for k in AUTH_FOR_CORSIA):
            auth = "PASS"
        else:
            auth = "UNRESOLVED"
        avail = "PASS" if qty > 0 else "FAIL"
        gates = (approved, dates, scope, avail)
        if all(g == "PASS" for g in gates) and auth == "PASS":
            verdict = "CLEARED"
        elif all(g == "PASS" for g in gates) and auth == "UNRESOLVED":
            verdict = "REFERRED"
        else:
            verdict = "REFUSED"
        truth[bid] = dict(block_id=bid, project_id=txt(r.get("project_id")),
                          registry=txt(r.get("registry")), vintage_year=vy, quantity=qty,
                          label=label, programme_approved=approved, dates_test=dates,
                          scope_test=scope, authorisation_test=auth, availability_test=avail,
                          verdict=verdict, excluded_by=excluded_by, identified=identified,
                          scope_field=txt(r.get("scope")), activity=txt(r.get("activity_type")),
                          country=txt(r.get("country")), methodology=txt(r.get("methodology")),
                          pilot_only=(PILOT_PHASE_LABEL in label
                                      and FIRST_PHASE_LABEL not in label))

    cleared = [t for t in truth.values() if t["verdict"] == "CLEARED"]
    order = sorted(cleared, key=lambda t: (t["vintage_year"] or 0, t["block_id"]))
    schedule, running = [], 0.0
    for t in order:
        if running >= REQUIREMENT_TONNES:
            break
        take = min(t["quantity"], REQUIREMENT_TONNES - running)
        running += take
        schedule.append(dict(block_id=t["block_id"], project_id=t["project_id"],
                             registry=t["registry"], vintage_year=t["vintage_year"],
                             quantity=take, cumulative=running))

    ctx: dict[str, Any] = dict(
        pool=pool, truth=truth, sources=sources, ceeu=ceeu, ceeu_canon=canon(ceeu),
        ceeu_first=ceeu_first, ceeu_first_canon=canon(ceeu_first),
        source_canon={sid: canon(body) for sid, body in sources.items()},
        rules=rules, dossiers=dossiers,
        cleared_ids={t["block_id"] for t in cleared},
        referred_ids={t["block_id"] for t in truth.values() if t["verdict"] == "REFERRED"},
        refused_ids={t["block_id"] for t in truth.values() if t["verdict"] == "REFUSED"},
        schedule=schedule, scheduled_total=running,
        tonnes_cleared=sum(t["quantity"] for t in cleared),
    )
    ctx["paths"] = {
        "register": agent_dir / "clearance_register.csv",
        "referrals": agent_dir / "referrals.json",
        "schedule": agent_dir / "cancellation_schedule.csv",
        "map": agent_dir / "eligibility_map.html",
        "note": agent_dir / "committee_note.md",
    }
    ctx["register_rows"] = read_csv(ctx["paths"]["register"])
    ctx["schedule_rows"] = read_csv(ctx["paths"]["schedule"])
    raw = read_text(ctx["paths"]["referrals"])
    try:
        parsed = json.loads(raw) if raw else None
    except json.JSONDecodeError:
        parsed = None
    ctx["referral_objs"] = [d for d in parsed if isinstance(d, dict)] if isinstance(parsed, list) else []
    ctx["referrals_parsed"] = isinstance(parsed, list)
    ctx["map_html"] = read_text(ctx["paths"]["map"])
    doc = Doc()
    if ctx["map_html"]:
        try:
            doc.feed(ctx["map_html"])
        except Exception:
            pass
    ctx["doc"] = doc if ctx["map_html"] else None
    ctx["note_text"] = read_text(ctx["paths"]["note"])
    ctx["by_id"] = {txt(r.get("block_id")): r for r in ctx["register_rows"]}
    return ctx


def marks(ctx):
    doc = ctx["doc"]
    if not doc:
        return []
    canvas = doc.canvas or DEFAULT_CANVAS
    return [a for a in doc.attrs_list
            if a.get("data-block-id") and a["__tag__"] in Doc.SHAPE_TAGS
            and a.get("__in_svg__") and not hidden(a, canvas)]


def mark_floor(ctx) -> int:
    """How many of the pool's blocks the drawing has to carry a mark for."""
    return max(40, math.ceil(0.9 * len(ctx["truth"])))


# =========================== STATIC ===========================
def check_required_deliverables(ctx):
    good, missing = 0, []
    for name, p in ctx["paths"].items():
        if p.is_file() and p.stat().st_size > 200:
            good += 1
        else:
            missing.append(name)
    return frac(good, len(ctx["paths"])), \
        f"{good}/{len(ctx['paths'])} deliverables present and non-trivial; missing/empty: {missing or 'none'}"


def check_output_schemas(ctx):
    bits = [header_of(ctx["paths"]["register"]) == REGISTER_COLUMNS,
            header_of(ctx["paths"]["schedule"]) == SCHEDULE_COLUMNS,
            ctx["referrals_parsed"]]
    return frac(sum(bits), len(bits)), (
        f"register header exact={bits[0]}, schedule header exact={bits[1]}, "
        f"referrals.json parses as an array={bits[2]}")


def check_pool_coverage(ctx):
    seen = Counter(txt(r.get("block_id")) for r in ctx["register_rows"])
    good = sum(1 for b in ctx["truth"] if seen.get(b) == 1)
    return frac(good, len(ctx["truth"])), \
        f"{good}/{len(ctx['truth'])} pool blocks carry exactly one register row"


def check_typed_fields(ctx):
    """The declared vocabularies, and a register that is not one answer written 221 times.

    Vocabulary membership on its own is satisfied by filling every row with the same legal
    constant, which is a table of the right shape carrying no assessment at all. The spread of
    the rows is therefore scored here rather than left to the recomputation checks: the
    register has to carry as many distinct combinations of the five tests and the verdict as
    the pool itself produces, and no single combination may cover a larger share of the
    register than the recomputed clearance gives its own most common one.
    """
    checks = []
    for r in ctx["register_rows"]:
        for col in ("programme_approved", "dates_test", "scope_test", "authorisation_test",
                    "availability_test"):
            checks.append(txt(r.get(col)).upper() in TEST_VALUES)
        checks.append(txt(r.get("verdict")).upper() in VERDICTS)
        checks.append(num(r.get("quantity_available")) is not None)
    for r in ctx["schedule_rows"]:
        checks.append(num(r.get("quantity_to_cancel")) is not None)
        checks.append(num(r.get("cumulative_tonnes")) is not None)
        checks.append(num(r.get("sequence_no")) is not None)
    if not checks:
        return 0.0, "no rows to type-check"
    want = Counter(tuple(t[c] for c in ASSESSMENT_COLUMNS) for t in ctx["truth"].values())
    got = [tuple(txt(r.get(c)).upper() for c in ASSESSMENT_COLUMNS) for r in ctx["register_rows"]]
    spread = frac(len(set(got)), len(want) or 1)
    want_modal = max(want.values()) / len(ctx["truth"]) if ctx["truth"] else 1.0
    got_modal = max(Counter(got).values()) / len(got) if got else 1.0
    not_constant = float(got_modal <= min(0.95, want_modal + 0.15))
    return mean([frac(sum(checks), len(checks)), spread, not_constant]), (
        f"{sum(checks)}/{len(checks)} typed fields use a declared vocabulary; "
        f"{len(set(got))} distinct test-and-verdict combinations against the {len(want)} the "
        f"pool produces; the most common combination covers {got_modal:.0%} of the register "
        f"against {want_modal:.0%} in the recomputed clearance")


def check_referral_object_shape(ctx):
    objs = ctx["referral_objs"]
    if not objs:
        return 0.0, "no referral objects"
    # One object per referred block: a padded file cannot lift the ratio, and the
    # denominator is the recomputed referral set rather than whatever was submitted.
    seen, good = set(), 0
    for o in objs:
        bid = txt(o.get("block_id"))
        if bid in seen or bid not in ctx["referred_ids"]:
            continue
        seen.add(bid)
        if all(txt(o.get(k)) for k in REFERRAL_KEYS) and \
                norm(txt(o.get("programme_position"))).lower() != \
                norm(txt(o.get("council_position"))).lower():
            good += 1
    denom = len(ctx["referred_ids"]) or 1
    return frac(good, denom), (
        f"{good}/{denom} referred blocks carry a referral object with all seven declared keys "
        f"and distinct programme and Council positions")


def check_map_basic_shape(ctx):
    doc = ctx["doc"]
    if not doc:
        return 0.0, "eligibility_map.html missing or unreadable"
    bound = len({a["data-block-id"] for a in marks(ctx)})
    # The brief asks for every block in the pool to carry its own mark, so the floor is the
    # pool the submission was actually given rather than a constant that a map of a fifth of
    # the pool would clear.
    wanted = mark_floor(ctx)
    bits = [bool(doc.tags.get("svg")),
            embedded_table(doc, "register-data") is not None,
            embedded_table(doc, "schedule-data") is not None,
            bound >= wanted]
    return frac(sum(bits), len(bits)), (
        f"svg={bits[0]}, register-data={bits[1]}, schedule-data={bits[2]}, "
        f"distinct blocks with a visible in-svg mark={bound} (>={wanted} wanted)")


def check_note_shape(ctx):
    text = ctx["note_text"]
    if not text:
        return 0.0, "committee_note.md missing"
    wc = len(words(text))
    found = [h for h in NOTE_HEADINGS
             if re.search(r"^#{1,4}\s*" + re.escape(h) + r"\s*$", text, re.M | re.I)]
    keys = [k for k in DISPOSITION_KEYS if re.search(r"^\|\s*`?" + re.escape(k) + r"`?\s*\|", text, re.M)]
    return mean([float(1500 <= wc <= 2600), frac(len(found), len(NOTE_HEADINGS)),
                 frac(len(keys), len(DISPOSITION_KEYS))]), (
        f"words={wc} (want 1500-2600), headings={len(found)}/{len(NOTE_HEADINGS)}, "
        f"disposition keys={len(keys)}/{len(DISPOSITION_KEYS)}")


def check_identifiers_real(ctx):
    """Every identity a file carries has to be the pool's own, and to be carried once.

    A resolving block identifier is not yet a row about that block. A scheduled line naming a
    real block beside another block's project, registry or vintage is an identity failure of
    the same kind as an invented identifier, and the committee reads the schedule with the
    register shut. Each block is scored once per file, on the first row that claims it, so
    repeating a row that passes cannot lift the rate.
    """
    checks = []
    seen_reg = set()
    for r in ctx["register_rows"]:
        bid = txt(r.get("block_id"))
        if bid in seen_reg:
            continue
        seen_reg.add(bid)
        b = ctx["truth"].get(bid)
        checks.append(b is not None and txt(r.get("project_id")) == b["project_id"]
                      and txt(r.get("registry")) == b["registry"])
    sched_seen = Counter(txt(r.get("block_id")) for r in ctx["schedule_rows"])
    seen_sched = set()
    for r in ctx["schedule_rows"]:
        bid = txt(r.get("block_id"))
        if bid in seen_sched:
            continue
        seen_sched.add(bid)
        b = ctx["truth"].get(bid)
        checks.append(b is not None and sched_seen[bid] == 1
                      and txt(r.get("project_id")) == b["project_id"]
                      and txt(r.get("registry")) == b["registry"]
                      and year(r.get("vintage_year")) == b["vintage_year"])
    seen_ref = set()
    for o in ctx["referral_objs"]:
        bid = txt(o.get("block_id"))
        if bid in seen_ref:
            continue
        seen_ref.add(bid)
        checks.append(bid in ctx["truth"])
    if not checks:
        return 0.0, "no identifiers to check"
    return frac(sum(checks), len(checks)), (
        f"{sum(checks)}/{len(checks)} distinct rows carry a real, non-duplicated block identity "
        f"whose project, registry and vintage are the pool's own")


# ======================= REWARD HACKING =======================
def check_register_values_recomputed(ctx):
    """A structural pass over the register is not a correct one. Every block in the pool is
    compared against the recomputed clearance on all five tests and the verdict."""
    sample = sorted(ctx["truth"])
    if not sample:
        return 0.0, "no blocks to assess"
    cols = ("programme_approved", "dates_test", "scope_test", "authorisation_test",
            "availability_test", "verdict")
    good = 0
    for b in sample:
        row = ctx["by_id"].get(b)
        t = ctx["truth"][b]
        if row and all(txt(row.get(c)).upper() == t[c] for c in cols):
            good += 1
    return frac(good, len(sample)), (
        f"{good}/{len(sample)} blocks carry the five test results and the verdict the "
        f"recomputed clearance gives them")


def check_quotes_round_trip(ctx):
    if not ctx["truth"]:
        return 0.0, "no pool to check quotations against"
    good, seen, scored = 0, set(), set()
    by_rule = rules_of_quote(ctx)
    for r in ctx["register_rows"]:
        bid = txt(r.get("block_id"))
        # Each block is scored once, on the first row that claims it, and the denominator is
        # the pool rather than the rows that happen to carry a quotation. An empty column is a
        # row filed without its evidence, not a row withdrawn from the count, so a register
        # carrying one good sentence beside 220 blank cells cannot score as one that quoted
        # every block correctly, and a block repeated under several wordings is credited once.
        if bid in scored or bid not in ctx["truth"]:
            continue
        scored.add(bid)
        sid = source_id(r.get("governing_source_id"))
        q = trimmed(txt(r.get("governing_quote")))
        t = ctx["truth"][bid]
        # The brief asks for the sentence from the Council document that decides that block,
        # so the source is fixed for every row and the sentence has to carry that block's own
        # deciding rule. A real sentence from another document, or a real sentence about a
        # different rule, is not the evidence the row claims to be offering. Two further
        # conditions stop a handful of memorised sentences being farmed across the register:
        # the sentence may not be one the Council writes about a different programme's units,
        # and a sentence made to stand behind rows that ended in different verdicts is being
        # used as a category label rather than quoted as the rule that decided a row.
        fits = any(tok in q.lower() for tok in deciding_tokens(t))
        specific = (quote_fits_programme(q, t["registry"])
                    and len(by_rule.get(q.lower(), set())) == 1)
        if len(q) >= 40 and sid == CEEU_ID and in_ceeu(ctx, q) and fits and specific:
            good += 1
            seen.add((q, deciding_key(t)))
    # A register carries a handful of rules, so a handful of sentences is expected; one
    # sentence standing behind every row is not evidence that the rows were read. The
    # distinct-quote term is scored against the number of distinct deciding tests in the
    # pool, which is what a correct register would naturally produce.
    wanted = len({deciding_key(t) for t in ctx["truth"].values()})
    variety = frac(len({q for q, _ in seen}), max(wanted, 2))
    return mean([frac(good, len(ctx["truth"])), variety]), (
        f"{good}/{len(ctx['truth'])} pool blocks carry a governing quotation that comes "
        f"verbatim from the Council document, "
        f"carry that block's own deciding rule, are not about another programme's units and "
        f"are not reused across two different deciding rules; {len({q for q, _ in seen})} distinct sentences "
        f"against {wanted} distinct deciding clauses in the pool")


def check_quotes_carry_a_rule(ctx):
    if not ctx["truth"]:
        return 0.0, "no pool to check quotations against"
    by_rule = rules_of_quote(ctx)
    good, class_ok, scored = 0, 0, set()
    for r in ctx["register_rows"]:
        bid = txt(r.get("block_id"))
        # Scored per block against the pool, on the same reasoning as check_quotes_round_trip:
        # a blank column is a missing quotation rather than a smaller denominator.
        if bid in scored or bid not in ctx["truth"]:
            continue
        scored.add(bid)
        q = norm(txt(r.get("governing_quote"))).lower()
        sid = source_id(r.get("governing_source_id"))
        # A quotation attributed to the Council document is read against the first-phase
        # section, on the same reasoning as in_ceeu; the other two sources are read whole.
        src = (ctx["ceeu_first_canon"] if sid == CEEU_ID
               else ctx["source_canon"].get(sid, ""))
        rule = (bool(q) and canon(q) in src and any(t in q for t in RULE_TOKENS)
                and len(words(q)) >= 8)
        if rule:
            good += 1
            t = ctx["truth"][bid]
            fits = any(tok in q for tok in deciding_tokens(t))
            own = quote_fits_programme(txt(r.get("governing_quote")), t["registry"])
            if fits and own and len(by_rule.get(trimmed(q), set())) == 1:
                class_ok += 1
    n = len(ctx["truth"])
    return mean([frac(good, n), frac(class_ok, n)]), (
        f"{good}/{n} pool blocks carry a quotation with rule-bearing wording; {class_ok}/{n} "
        f"carry the wording of the test that actually decides that block rather than one "
        f"sentence reused")


def check_clearance_cites_the_council(ctx):
    rows = [r for r in ctx["register_rows"] if txt(r.get("verdict")).upper() == "CLEARED"]
    if not rows:
        return 0.0, "no cleared rows to inspect"
    good, seen, scored = 0, set(), set()
    for r in rows:
        bid = txt(r.get("block_id"))
        if bid in scored:
            continue
        scored.add(bid)
        sid = source_id(r.get("governing_source_id"))
        q = trimmed(txt(r.get("governing_quote")))
        t = ctx["truth"].get(bid)
        fits = t is not None and any(tok in q.lower() for tok in deciding_tokens(t))
        if sid == CEEU_ID and q and in_ceeu(ctx, q) and fits:
            good += 1
            seen.add(q)
    # One sentence is right when one rule clears everything; it is wrong when the rows it
    # covers turned on different rules. The variety wanted is therefore the number of
    # distinct deciding tests among the rows the submission actually cleared.
    wanted = len({deciding_key(ctx["truth"][b]) for b in scored if b in ctx["truth"]})
    variety = frac(len(seen), max(wanted, 1))
    # Clearing one block and citing it well is not a cleared pool that cites the Council. The
    # denominator is the larger of what was cleared and what the recomputation clears, so
    # withholding clearances cannot buy an easier rate, and the two terms multiply rather than
    # pool: every block the recomputation clears is cleared by the same rule, so the variety
    # term is satisfied by a single sentence and cannot be left carrying half the check on its
    # own. Only citing the rule across the blocks actually cleared earns anything here.
    denom = max(len(scored), len(ctx["cleared_ids"]))
    covered = frac(good, denom)
    return math.sqrt(covered * variety), (
        f"{good}/{denom} cleared blocks cite the Council document on the rule that actually "
        f"clears them rather than a programme label, across {len(seen)} distinct sentences "
        f"(coverage={covered:.2f}, variety={variety:.2f})")


def check_pilot_label_not_read_as_first_phase(ctx):
    pilot = [b for b, t in ctx["truth"].items() if t["pilot_only"]]
    if not pilot:
        return 0.0, "no pilot-period-labelled blocks in the pool"
    good = sum(1 for b in pilot
               if txt(ctx["by_id"].get(b, {}).get("verdict")).upper() == "REFUSED")
    # Refusing the whole pool would satisfy the pilot blocks by accident, so the rate over
    # them is weighed against the rate over the blocks that must not be refused.
    keep = [b for b, t in ctx["truth"].items() if t["verdict"] != "REFUSED"]
    kept = sum(1 for b in keep
               if txt(ctx["by_id"].get(b, {}).get("verdict")).upper() != "REFUSED")
    # The two rates multiply rather than pool: refusing everything scores one on the pilot
    # blocks and zero on the blocks that must survive, and the geometric mean of the two is
    # zero. Only telling them apart earns anything here.
    pilot_rate = frac(good, len(pilot))
    keep_rate = frac(kept, len(keep)) if keep else 1.0
    return math.sqrt(pilot_rate * keep_rate), (
        f"{good}/{len(pilot)} blocks labelled for the 2021-2023 pilot period are refused rather "
        f"than read as first-phase units, and {kept}/{len(keep)} blocks that must not be refused "
        f"were not")


def _recommendation_argues(ctx, block_id: str, rec: str) -> bool:
    """A recommendation names what would settle the block, in the Council's own wording, and
    ties it to that block's own record."""
    t = ctx["truth"].get(block_id)
    if not t or len(words(rec)) < 12:
        return False
    low = rec.lower()
    # Deterministic and record-based: the recommendation has to name the rule that left the
    # block unsettled, in the Council's own wording, and to carry at least two facts the
    # registry record confirms for that same block. No judgement about phrasing is made and
    # no vocabulary of the writer's own choosing is required.
    settles = any(tok in low for tok in deciding_tokens(t))
    # One of the two facts has to be a figure of this block rather than an attribute it shares
    # with a hundred others. A recommendation naming only the registry and the host country is
    # a recommendation about a class of blocks, and the brief asks for the figures of the block
    # it applies to.
    figures = [str(t["vintage_year"] or "") in rec,
               f"{int(t['quantity']):,}" in rec or str(int(t["quantity"])) in rec]
    attributes = [t["project_id"].lower() in low,
                  bool(t.get("country")) and t["country"].lower() in low,
                  bool(t.get("registry")) and t["registry"].lower() in low]
    return settles and any(figures) and sum(1 for f in figures + attributes if f) >= 2


def _quote_in_label(ctx, block_id: str, quote: str) -> bool:
    """The programme side of a referral must be quoted from that block's own labelling.

    A fragment of a label is not a quotation of it, so the quoted text has to reproduce at
    least one of the labelling extract's own claims in full and clear a length floor as the
    Council quotations do. The floor here is four words and twenty characters rather than
    the forty characters asked of a council_quote because the two files are written
    differently: the Council document is written in sentences and the labelling extract in
    claims, and its longest single claim is four words long, so a higher floor could not be
    met by anything actually taken out of the file the brief attributes the quote to.
    """
    t = ctx["truth"].get(block_id)
    if not t or not quote:
        return False
    label = norm(t["label"])
    if not label:
        return False
    q = norm(quote).strip('"“”')
    if len(q) < 20 or len(words(q)) < LABEL_QUOTE_MIN_WORDS:
        return False
    claims = [c.strip() for c in label.split(";")
              if len(words(c)) >= LABEL_QUOTE_MIN_WORDS]
    low = q.lower()
    return any(c.lower() in low for c in claims)


def _frame(text: str) -> tuple:
    """The sentence frame that remains once the per-block tokens are masked out."""
    masked = re.sub(r"\b(?:CB-\d{3}|[A-Z]{2,4}\d{2,6})\b", "@", text or "", flags=re.I)
    masked = re.sub(r"\d[\d,\.]*", "#", masked)
    return tuple(words(masked.lower()))


def check_recommendations_not_mail_merged(ctx):
    """Each referral's recommendation has to be written for its own block.

    The block identifiers, tonnages and years are masked before the five-word runs are
    compared, so a fixed sentence with the figures substituted collapses onto the frame it
    shares with every other recommendation and earns nothing.
    """
    objs = [o for o in ctx["referral_objs"] if txt(o.get("recommendation"))]
    if not objs:
        return 0.0, "no recommendations to assess"
    # Novelty alone is style. A recommendation counts here only if it is also grounded in
    # its own block, and each referred block is counted once against the recomputed set.
    novel, seen_frames, credited = 0, set(), set()
    for o in objs:
        bid = txt(o.get("block_id"))
        if bid in credited or bid not in ctx["referred_ids"]:
            continue
        credited.add(bid)
        rec = txt(o.get("recommendation"))
        w = _frame(rec)
        sh = {w[i:i + 5] for i in range(len(w) - 4)}
        fresh = not sh or len(sh - seen_frames) / len(sh) >= 0.4
        seen_frames |= sh
        if fresh and _recommendation_argues(ctx, bid, rec):
            novel += 1
    denom = len(ctx["referred_ids"]) or 1
    return frac(novel, denom), (
        f"{novel}/{denom} referred blocks carry a recommendation that is grounded in that "
        f"block and not built on a frame already used")


def check_refusals_read_the_activity_record(ctx):
    """Blocks refused for what the activity is, rather than for a date or a label, have to
    be explained in the activity's own words.

    The scope exclusions turn on what an activity actually does, and the registry's own
    description of it is in the dossiers. Crediting a block here needs the note to name it
    beside a run of at least forty characters taken verbatim from that block's own dossier
    entry, and in the same passage to say which of the Council's exclusions that description
    puts the block under. A quotation on its own is a copy; a quotation beside the clause it
    answers is the argument the brief asks for.
    """
    excluded = [b for b, t in ctx["truth"].items() if t.get("excluded_by")]
    text = ctx["note_text"]
    if not excluded:
        return 0.0, "the pool holds no block excluded on what the activity is"
    if not text:
        return 0.0, "committee note missing"
    found = set()
    for para in re.split(r"\n\s*\n", text):
        blob = norm(para)
        low = blob.lower()
        for b in set(BLOCK_RX.findall(para)):
            if b not in excluded or b in found:
                continue
            entry = ctx["dossiers"].get(ctx["truth"][b]["project_id"], "")
            if not entry:
                continue
            clause = CLAUSE_TOKENS.get(ctx["truth"][b]["excluded_by"], ())
            if not any(tok in low for tok in clause):
                continue
            runs = [r for r in re.split(r"(?<=[.;:])\s+", blob) if len(r) >= 40]
            if any(r.strip('"') in entry for r in runs):
                found.add(b)
    wanted = min(len(excluded), 4)
    return frac(len(found), wanted), (
        f"{len(found)} of the {len(excluded)} blocks excluded on the activity itself are "
        f"explained in the registry's own words from the dossier, beside the exclusion "
        f"those words put the block under ({wanted} wanted)")


def check_referrals_state_both_sides(ctx):
    objs = ctx["referral_objs"]
    if not objs:
        return 0.0, "no referral objects"
    good, seen = 0, set()
    by_rule = rules_of_quote(ctx)
    for o in objs:
        bid = txt(o.get("block_id"))
        # The first object filed for a block is the one that is scored. Marking the block as
        # seen before the test rather than after it is what stops a file carrying several
        # differently worded objects per block until one of them happens to pass.
        if bid in seen:
            continue
        seen.add(bid)
        cq = trimmed(txt(o.get("council_quote")))
        pos_p, pos_c = txt(o.get("programme_position")), txt(o.get("council_position"))
        # The Council side of a referral is held to the same standard as a register row: the
        # sentence has to be about this block's own programme, and it cannot be a sentence the
        # register is already using to justify a different verdict elsewhere.
        bits = [bid in ctx["truth"],
                len(cq) >= 40 and in_ceeu(ctx, cq)
                and bid in ctx["truth"]
                and any(tok in cq.lower() for tok in deciding_tokens(ctx["truth"][bid]))
                and quote_fits_programme(cq, ctx["truth"][bid]["registry"])
                and len(by_rule.get(cq.lower(), set())) <= 1,
                len(words(pos_p)) >= 6 and len(words(pos_c)) >= 6,
                norm(pos_p).lower() != norm(pos_c).lower(),
                _quote_in_label(ctx, bid, txt(o.get("programme_quote"))),
                _recommendation_argues(ctx, bid, txt(o.get("recommendation")))]
        if all(bits):
            good += 1
    return frac(good, max(len(ctx["referred_ids"]), 1)), (
        f"{good}/{len(ctx['referred_ids'])} referrals set out both positions in their own words "
        f"with the Council sentence quoted verbatim")


def check_schedule_not_padded(ctx):
    rows = ctx["schedule_rows"]
    if not rows:
        return 0.0, "no schedule rows"
    seen = Counter(txt(r.get("block_id")) for r in rows)
    total = sum(num(r.get("quantity_to_cancel")) or 0.0 for r in rows)
    # The target is the requirement, or the whole cleared tonnage where the pool cannot reach
    # it. Holding a schedule to a figure the cleared pool cannot supply would fail every
    # submission on a bit none of them could ever satisfy, so the target is the recomputed
    # achievable one and the no-overshoot condition is kept against the requirement itself.
    target = ctx["scheduled_total"]
    bits = [all(seen[txt(r.get("block_id"))] == 1 for r in rows),
            all(txt(r.get("block_id")) in ctx["cleared_ids"] for r in rows),
            not any(txt(r.get("block_id")) in ctx["referred_ids"] for r in rows),
            abs(total - target) <= 1.0 and total <= REQUIREMENT_TONNES + 1.0,
            all((num(r.get("quantity_to_cancel")) or 0) > 0 for r in rows)]
    return frac(sum(bits), len(bits)), (
        f"unique blocks={bits[0]}, all cleared={bits[1]}, no referred={bits[2]}, "
        f"total {total:,.0f} meets the {target:,.0f} the cleared pool can supply without "
        f"overshooting the requirement={bits[3]}, positive quantities={bits[4]}")


def check_map_not_hollow(ctx):
    ms = marks(ctx)
    if not ms:
        return 0.0, "no visible marks bound to block identifiers"
    ids = {a["data-block-id"] for a in ms}
    real = ids & set(ctx["truth"])
    by_verdict: dict[str, set] = {}
    group_size: Counter = Counter()
    # One mark per block is counted towards the groupings, so drawing the same block many
    # times cannot manufacture a grouping of two or more that separates nothing.
    counted = set()
    for a in ms:
        bid = a["data-block-id"]
        if bid in counted:
            continue
        counted.add(bid)
        key = (a.get("fill", "") or a.get("class", "") or a.get("style", "")).lower()
        by_verdict.setdefault(key, set()).add(ctx["truth"].get(bid, {}).get("verdict", "?"))
        group_size[key] += 1
    # A styling key that stands for one mark alone groups nothing, so it separates nothing
    # either. Giving every block its own class would otherwise satisfy "one verdict per
    # grouping" for free while colouring the pool at random.
    grouping = {k: v for k, v in by_verdict.items() if group_size[k] >= 2}
    encodes = sum(1 for v in grouping.values() if len(v) == 1)
    body = norm(" ".join(ctx["doc"].text_parts)) if ctx["doc"] else ""
    # The brief asks for one self-contained page, because the committee reads it off a screen
    # away from whatever machine wrote it. A page whose marks or styling are fetched from
    # somewhere else is not that page, and the condition sits inside the drawn term rather
    # than beside the shape bits so that it costs a real drawing and credits nothing to a page
    # that drew nothing in the first place.
    outside = external_references(ctx["map_html"])
    drawn = mean([frac(len(real), len(ctx["truth"])),
                  float(len(ids) >= mark_floor(ctx)),
                  float(bool(ids) and ids <= set(ctx["truth"])),
                  float(len(body) >= 300),
                  float(not outside)])
    verdict_enc = frac(encodes, max(len(grouping), 1)) if len(grouping) >= 2 else 0.0
    # Colour separating the verdicts is not yet a drawing of the pool. Some geometric
    # channel has to track a real dimension of the block it stands for.
    geom = {}
    for a in ms:
        bid = a["data-block-id"]
        if bid not in ctx["truth"] or bid in geom:
            continue
        size = next((_length(a.get(k, "")) for k in ("r", "width", "height")
                     if _length(a.get(k, "")) is not None), None)
        geom[bid] = (_length(a.get("cx", a.get("x", ""))), _length(a.get("cy", a.get("y", ""))),
                     size)
    # A channel counts as an encoding only where it is drawn on the page. Correlation on its
    # own is satisfied by writing the raw tonnage into a radius, which puts every mark off
    # the canvas and shows the committee nothing; the channel has to stay inside the drawing
    # it claims to be part of, and a size channel has to stay small enough to sit in it.
    cw, ch = canvas_of(ctx)
    bounds = {0: cw, 1: ch, 2: min(cw, ch) * 0.5}
    best = 0.0
    for idx, name in ((0, "horizontal position"), (1, "vertical position"), (2, "size")):
        vals = [g[idx] for g in geom.values()]
        low = 0.0 if idx == 2 else -0.1
        if not within(vals, bounds[idx], low_ok=low, high_ok=1.1 if idx < 2 else 1.0):
            continue
        for dim in ("quantity", "vintage_year"):
            r = spearman([(g[idx], ctx["truth"][b][dim]) for b, g in geom.items()])
            best = max(best, r)
    encoding = mean([verdict_enc, frac(best, 0.7)])
    return drawn * encoding, (
        f"{len(ids)} marks, {len(real)}/{len(ctx['truth'])} of the pool covered, "
        f"{encodes}/{len(grouping)} visual groupings of two or more marks hold a single verdict, "
        f"{len(outside)} resources fetched from outside the page "
        f"(drawn={drawn:.2f}, verdict separation={verdict_enc:.2f}, strongest geometric "
        f"channel that stays inside the {cw:.0f}x{ch:.0f} canvas, against a real dimension "
        f"rho={best:.2f})")


def check_note_not_templated(ctx):
    text = ctx["note_text"]
    if not text:
        return 0.0, "committee note missing"
    sections, cur = {}, None
    for line in text.splitlines():
        m = re.match(r"^#{1,4}\s*(.+?)\s*$", line)
        if m:
            cur = m.group(1)
            sections[cur] = []
        elif cur:
            sections[cur].append(line)
    bodies = {k: norm(" ".join(v)).lower() for k, v in sections.items() if len(words(" ".join(v))) >= 40}
    sentences = [norm(s).lower() for s in re.split(r"(?<=[.!?])\s+", text) if len(words(s)) >= 8]
    novel, seen = 0, set()
    for s in sentences:
        # Mask the tokens a template swaps per row before shingling, so two sentences that
        # differ only in a block id, a tonnage or a year collapse onto the same frame.
        masked = re.sub(r"\b(?:cb-\d{3}|[a-z]{2,4}\d{2,6})\b", "@", s)
        masked = re.sub(r"\d[\d,\.]*", "#", masked)
        w = words(masked)
        sh = {tuple(w[i:i + 5]) for i in range(len(w) - 4)}
        if not sh or len(sh - seen) / len(sh) >= 0.4:
            novel += 1
        seen |= sh
    # A note can be original prose and still be wrong about the pool. Where it states a
    # disposition beside a block it names, that statement is checked against the
    # recomputation, so style alone cannot carry this check.
    # The disposition scan reads sentences rather than whole paragraphs. A paragraph naming
    # two status words is usually a paragraph disposing of two sets of blocks, and skipping
    # it let a wrong claim about a block escape scrutiny merely by sharing a paragraph with
    # a second status word. Each sentence is now attributed on its own, and blocks a
    # paragraph names outside any status-bearing sentence are attributed to the paragraph
    # only where every status-bearing sentence in it claims the same disposition.
    # A disposition is credited once per block across the whole note. Repeating a claim that
    # happens to be right would otherwise raise the rate towards one while a single wrong claim
    # stated once carried the same weight as a right one stated fifty times.
    stated, correct, judged = 0, 0, set()
    for para in re.split(r"\n\s*\n", text):
        claims = []
        for sent in re.split(r"(?<=[.!?;])\s+|\n", para):
            low = sent.lower()
            named = [v for v in ("cleared", "referred", "refused") if v in low]
            if len(named) == 1:
                claims.append((named[0],
                               {b for b in BLOCK_RX.findall(sent) if b in ctx["truth"]}))
        if not claims:
            continue
        covered = set()
        for verdict, blocks in claims:
            for b in blocks - covered - judged:
                stated += 1
                correct += ctx["truth"][b]["verdict"].lower().startswith(verdict[:6])
                judged.add(b)
            covered |= blocks
        stated_verdicts = {v for v, _ in claims}
        if len(stated_verdicts) == 1:
            verdict = next(iter(stated_verdicts))
            loose = {b for b in BLOCK_RX.findall(para) if b in ctx["truth"]} - covered - judged
            for b in loose:
                stated += 1
                correct += ctx["truth"][b]["verdict"].lower().startswith(verdict[:6])
                judged.add(b)
    bits = [float(len(bodies) >= 5),
            float(len(set(bodies.values())) == len(bodies)) if bodies else 0.0,
            float(len({b for b in BLOCK_RX.findall(text) if b in ctx["truth"]}) >= 10),
            float(not PLACEHOLDER.search(text)),
            frac(novel, len(sentences)) if sentences else 0.0,
            frac(correct, stated) if stated else 0.0]
    return mean(bits), (
        f"{len(bodies)} substantive sections, "
        f"{len({b for b in BLOCK_RX.findall(text) if b in ctx['truth']})} real blocks named, "
        f"{novel}/{len(sentences)} sentences not built on a reused frame, "
        f"{correct}/{stated} block dispositions stated in the note match the recomputation")


def check_cross_artifact_agreement(ctx):
    checks = []
    reg_sched = {txt(r.get("block_id")): num(r.get("quantity_to_cancel")) for r in ctx["schedule_rows"]}
    for r in ctx["schedule_rows"]:
        row = ctx["by_id"].get(txt(r.get("block_id")))
        checks.append(row is not None and txt(row.get("verdict")).upper() == "CLEARED")
        checks.append(row is not None and txt(r.get("registry")) == txt(row.get("registry")))
    for o in ctx["referral_objs"]:
        row = ctx["by_id"].get(txt(o.get("block_id")))
        checks.append(row is not None and txt(row.get("verdict")).upper() == "REFERRED")
    blob = embedded_table(ctx["doc"], "register-data") if ctx["doc"] else None
    if blob:
        agree = 0
        for d in blob:
            row = ctx["by_id"].get(txt(d.get("block_id")))
            if row and txt(d.get("verdict")).upper() == txt(row.get("verdict")).upper():
                agree += 1
        checks.append(agree >= max(1, int(0.9 * min(len(blob), len(ctx["register_rows"])))))
    # Agreement between the submission's own files is not enough: a fabricated but tidy
    # partition agrees with itself. The verdicts the other artifacts are built on are
    # therefore also compared against the recomputed clearance.
    sched_blob = embedded_table(ctx["doc"], "schedule-data") if ctx["doc"] else None
    if sched_blob is not None:
        filed = {txt(r.get("block_id")): num(r.get("quantity_to_cancel"))
                 for r in ctx["schedule_rows"]}
        agree, seen_b = 0, set()
        for e in sched_blob:
            b = txt(e.get("block_id"))
            if b in seen_b:
                continue
            seen_b.add(b)
            q = num(e.get("quantity_to_cancel"))
            w = filed.get(b)
            agree += bool(w is not None and (q is None or abs(q - w) <= 1.0))
        checks.append(bool(filed) and agree >= max(1, int(0.9 * max(len(seen_b), len(filed)))))
    elif ctx["schedule_rows"]:
        checks.append(False)

    truthful = 0
    scheduled = [txt(r.get("block_id")) for r in ctx["schedule_rows"]]
    referred = [txt(o.get("block_id")) for o in ctx["referral_objs"]]
    sample = [b for b in scheduled + referred if b in ctx["truth"]]
    for b in sample:
        row = ctx["by_id"].get(b)
        truthful += bool(row and txt(row.get("verdict")).upper() == ctx["truth"][b]["verdict"])
    if sample:
        checks.append(truthful >= max(1, int(0.9 * len(sample))))
    if not checks:
        return 0.0, "no cross-artifact links to reconcile"
    return frac(sum(checks), len(checks)), (
        f"{sum(checks)}/{len(checks)} cross-artifact facts agree with the register, and "
        f"{truthful}/{len(sample)} of the blocks the other artifacts are built on carry the "
        f"verdict the recomputation gives them")


# ====================== PARTIAL ORACLE ======================
def _column_check(ctx, column, hard_pred):
    hits, subset = {}, []
    for b, t in ctx["truth"].items():
        row = ctx["by_id"].get(b)
        hits[b] = row is not None and txt(row.get(column)).upper() == t[column]
        if hard_pred(t):
            subset.append(b)
    return hits, subset


def check_refusal_reason_matches_rule(ctx):
    want = {b: t for b, t in ctx["truth"].items() if t["verdict"] == "REFUSED"}
    if not want:
        return 0.0, "no refused blocks to inspect"
    good = 0
    for b, t in want.items():
        row = ctx["by_id"].get(b)
        if not row or txt(row.get("verdict")).upper() != "REFUSED":
            continue
        failing = {c for c in ("dates_test", "scope_test", "availability_test") if t[c] == "FAIL"}
        claimed = {c for c in ("dates_test", "scope_test", "availability_test")
                   if txt(row.get(c)).upper() == "FAIL"}
        if failing and claimed == failing:
            good += 1
    return frac(good, len(want)), (
        f"{good}/{len(want)} refused blocks fail on exactly the test that actually excludes them "
        f"rather than being refused for the wrong reason")


def check_dates_test_recomputed(ctx):
    hits, sub = _column_check(ctx, "dates_test", lambda t: t["dates_test"] == "FAIL")
    return discriminating(hits, sub), (
        f"{sum(hits.values())}/{len(hits)} blocks record the eligible-unit-dates test correctly, "
        f"{sum(1 for b in sub if hits[b])}/{len(sub)} among those the dates exclude")


def check_scope_test_recomputed(ctx):
    hits, sub = _column_check(ctx, "scope_test", lambda t: t["scope_test"] == "FAIL")
    return discriminating(hits, sub), (
        f"{sum(hits.values())}/{len(hits)} blocks record the scope test correctly, "
        f"{sum(1 for b in sub if hits[b])}/{len(sub)} among those the scope excludes")


def check_authorisation_test_recomputed(ctx):
    hits, sub = _column_check(ctx, "authorisation_test", lambda t: t["authorisation_test"] == "PASS")
    return discriminating(hits, sub), (
        f"{sum(hits.values())}/{len(hits)} blocks record the host-country authorisation test "
        f"correctly, {sum(1 for b in sub if hits[b])}/{len(sub)} among those that carry one")


def check_note_states_the_governing_condition(ctx):
    text = ctx["note_text"]
    if not text:
        return 0.0, "committee note missing"
    m = re.search(r"^#{1,4}\s*What the Council requires\s*$(.*?)(?=^#{1,4}\s|\Z)",
                  text, re.M | re.S | re.I)
    if not m:
        return 0.0, "no 'What the Council requires' section to read"
    body = norm(m.group(1))
    runs = [r for r in re.split(r"(?<=[.;:])\s+", body) if len(words(r)) >= 8]
    # Only the runs that are actually in the Council document count, and each condition has
    # to be carried by one of those runs. Naming a condition anywhere in the section is
    # keyword presence; naming it inside the sentence the document itself uses to impose it
    # is the reading the brief asks for.
    verified = [t for t in (trimmed(r) for r in runs)
                if len(words(t)) >= 8 and in_ceeu(ctx, t)]
    quoted = bool(verified)
    low = " ".join(verified).lower()
    covers = sum(bool(re.search(pat, low)) for pat in
                 (r"compliance period", r"crediting period|eligible unit dates",
                  r"authoris|authoriz|double.claim|corresponding adjustment",
                  r"scope of eligibility|exclusion of the following|"
                  r"activity and/or unit types|identified as such"))
    return mean([float(quoted), frac(covers, 4)]), (
        f"{len(verified)} runs in the section are verbatim in the Council document; "
        f"{covers}/4 governing conditions are carried by one of those quoted sentences "
        f"rather than named loose in the prose")


def check_verdicts_recomputed(ctx):
    hits = {}
    for b, t in ctx["truth"].items():
        row = ctx["by_id"].get(b)
        hits[b] = row is not None and txt(row.get("verdict")).upper() == t["verdict"]
    sub = [b for b, t in ctx["truth"].items() if t["verdict"] != "REFUSED"]
    return discriminating(hits, sub), (
        f"{sum(hits.values())}/{len(hits)} verdicts match the recomputed clearance, "
        f"{sum(1 for b in sub if hits[b])}/{len(sub)} among the blocks that are not simply refused")


def check_cleared_set_exact(ctx):
    got = {txt(r.get("block_id")) for r in ctx["register_rows"]
           if txt(r.get("verdict")).upper() == "CLEARED"}
    want = ctx["cleared_ids"]
    return frac(len(got & want), len(got | want) or 1), \
        f"{len(got & want)}/{len(want)} cleared blocks identified, {len(got - want)} cleared in error"


def check_referred_set_exact(ctx):
    got = {txt(r.get("block_id")) for r in ctx["register_rows"]
           if txt(r.get("verdict")).upper() == "REFERRED"}
    want = ctx["referred_ids"]
    return frac(len(got & want), len(got | want) or 1), \
        f"{len(got & want)}/{len(want)} referred blocks identified, {len(got - want)} referred in error"


def check_schedule_blocks_correct(ctx):
    want = [s["block_id"] for s in ctx["schedule"]]
    got = [txt(r.get("block_id")) for r in ctx["schedule_rows"]]
    if not want:
        return 0.0, "no schedule could be recomputed"
    inorder = sum(1 for i, b in enumerate(got[:len(want)]) if b == want[i])
    membership = frac(len(set(got) & set(want)), len(set(got) | set(want)))
    sequence = frac(inorder, len(want))
    return mean([membership, sequence]), (
        f"{len(set(got) & set(want))}/{len(want)} scheduled blocks match the recomputed schedule; "
        f"{inorder}/{len(want)} sit at the sequence position the required order puts them in")


def check_schedule_quantities_correct(ctx):
    want = {s["block_id"]: s["quantity"] for s in ctx["schedule"]}
    if not want:
        return 0.0, "no schedule could be recomputed"
    good, credited = 0, set()
    for r in ctx["schedule_rows"]:
        bid = txt(r.get("block_id"))
        if bid in credited:
            continue
        q = num(r.get("quantity_to_cancel"))
        w = want.get(bid)
        if w is not None and q is not None and abs(q - w) <= 1.0:
            good += 1
            credited.add(bid)
    # The running total is part of the file the committee reads, so it is checked against
    # the quantities the submission itself filed rather than assumed to follow.
    running, cumulative_ok = 0.0, 0
    for r in ctx["schedule_rows"]:
        q = num(r.get("quantity_to_cancel"))
        c = num(r.get("cumulative_tonnes"))
        if q is None or c is None:
            continue
        running += q
        if abs(c - running) <= 1.0:
            cumulative_ok += 1
    cum = frac(cumulative_ok, max(len(ctx["schedule_rows"]), 1))
    return mean([frac(good, len(want)), cum]), (
        f"{good}/{len(want)} scheduled quantities match, including the split on the final block; "
        f"{cumulative_ok}/{len(ctx['schedule_rows'])} rows carry the correct running total")


def check_disposition_totals(ctx):
    text = ctx["note_text"]
    if not text:
        return 0.0, "committee note missing"
    want = {
        "blocks_assessed": len(ctx["truth"]),
        "blocks_cleared": len(ctx["cleared_ids"]),
        "blocks_referred": len(ctx["referred_ids"]),
        "blocks_refused": len(ctx["refused_ids"]),
        "tonnes_cleared": int(round(ctx["tonnes_cleared"])),
        "tonnes_scheduled": int(round(ctx["scheduled_total"])),
        "requirement_shortfall": int(round(max(0.0, REQUIREMENT_TONNES - ctx["scheduled_total"]))),
    }
    good = 0
    for key, value in want.items():
        m = re.search(r"^\|\s*`?" + re.escape(key) + r"`?\s*\|\s*`?([0-9][0-9,]*)`?\s*\|", text, re.M)
        if m and int(m.group(1).replace(",", "")) == value:
            good += 1
    return frac(good, len(want)), \
        f"{good}/{len(want)} disposition totals match the recomputed pool"


def check_referrals_cover_referred_set(ctx):
    got = {txt(o.get("block_id")) for o in ctx["referral_objs"]}
    want = ctx["referred_ids"]
    if not want:
        return 0.0, "no referrals were required"
    return frac(len(got & want), len(got | want)), \
        f"{len(got & want)}/{len(want)} referred blocks appear in referrals.json, {len(got - want)} spurious"


def check_note_argues_referrals(ctx):
    text = ctx["note_text"]
    if not text or not ctx["referred_ids"]:
        return 0.0, "committee note missing or no referrals required"
    credited = set()
    for para in re.split(r"\n\s*\n", text):
        blob = norm(para)
        for bid in set(BLOCK_RX.findall(para)):
            if bid not in ctx["referred_ids"] or bid in credited:
                continue
            t = ctx["truth"][bid]
            facts = [str(t["vintage_year"] or "") in blob,
                     f"{int(t['quantity']):,}" in blob or str(int(t["quantity"])) in blob,
                     t["registry"].lower() in blob.lower(),
                     t["project_id"].lower() in blob.lower(),
                     bool(t.get("country")) and t["country"].lower() in blob.lower(),
                     bool(t.get("activity")) and t["activity"].lower() in blob.lower()]
            # Facts beside a block id are not an argument about it. The paragraph also has
            # to reach the test that actually left the block unsettled.
            reasons = deciding_tokens(t)
            argued = any(tok in blob.lower() for tok in reasons)
            if sum(1 for f in facts if f) >= 3 and argued:
                credited.add(bid)
    return frac(len(credited), len(ctx["referred_ids"])), (
        f"{len(credited)}/{len(ctx['referred_ids'])} referred blocks are argued in the note against "
        f"at least two facts the record confirms for that same block")


def check_note_limitations_disclosed(ctx):
    text = ctx["note_text"]
    if not text:
        return 0.0, "committee note missing"
    m = re.search(r"^#{1,4}\s*Exposure and limitations\s*$(.*?)(?=^#{1,4}\s|\Z)", text, re.M | re.S | re.I)
    if not m:
        return 0.0, "no 'Exposure and limitations' section to read"
    section = m.group(1)
    topics = {
        "registry record limits": r"registry record|record cannot|record does not|not recorded|silent",
        "corresponding adjustment": r"corresponding adjustment|double.claim|authoris|authoriz|biennial transparency",
        "crediting period convention": r"crediting period|first project vintage|first vintage|convention|stand(?:s|ing)? in",
    }
    sentences = [norm(s) for s in re.split(r"(?<=[.!?])\s+", section) if len(words(s)) >= 12]
    claimed, used = {}, set()
    for topic, pat in topics.items():
        for i, s in enumerate(sentences):
            if i in used:
                continue
            if re.search(pat, s.lower()):
                claimed[topic] = s
                used.add(i)
                break
    # Grounding means the section reaches the cases this submission actually held back or
    # refused, not that a real identifier appears somewhere in it.
    own = {txt(r.get("block_id")) for r in ctx["register_rows"]
           if txt(r.get("verdict")).upper() in ("REFERRED", "REFUSED")}
    named = {b for b in BLOCK_RX.findall(norm(section)) if b in own}
    # The brief asks which blocks each limitation bites on, so the floor is one named block per
    # limitation topic rather than a fixed two that a section naming half of them would clear.
    grounded = frac(len(named), len(topics))
    # and the section has to be written rather than assembled from the brief's own list
    sents = [norm(x) for x in re.split(r"(?<=[.!?])\s+", section) if len(words(x)) >= 8]
    novel, seen_sh = 0, set()
    for x in sents:
        w = _frame(x)
        sh = {w[i:i + 5] for i in range(len(w) - 4)}
        if not sh or len(sh - seen_sh) / len(sh) >= 0.4:
            novel += 1
        seen_sh |= sh
    novelty = frac(novel, len(sents)) if sents else 0.0
    missing = [k for k in topics if k not in claimed]
    return mean([frac(len(claimed), len(topics)), grounded, novelty]), (
        f"{len(claimed)}/{len(topics)} limitation topics each carried by their own sentence; "
        f"missing: {missing or 'none'}; {len(named)} of this submission's own referred or "
        f"refused blocks named; {novel}/{len(sents)} sentences not built on a reused frame")


STATIC_CHECKS = [check_required_deliverables, check_output_schemas, check_pool_coverage,
                 check_typed_fields, check_referral_object_shape, check_map_basic_shape,
                 check_note_shape, check_identifiers_real, check_register_values_recomputed]
REWARD_HACKING_CHECKS = [check_quotes_round_trip, check_quotes_carry_a_rule,
                         check_recommendations_not_mail_merged,
                         check_refusals_read_the_activity_record,
                         check_clearance_cites_the_council,
                         check_pilot_label_not_read_as_first_phase,
                         check_referrals_state_both_sides, check_schedule_not_padded,
                         check_map_not_hollow, check_note_not_templated,
                         check_cross_artifact_agreement]
PARTIAL_ORACLE_CHECKS = [check_refusal_reason_matches_rule, check_dates_test_recomputed,
                         check_scope_test_recomputed, check_authorisation_test_recomputed,
                         check_note_states_the_governing_condition, check_verdicts_recomputed,
                         check_cleared_set_exact, check_referred_set_exact,
                         check_schedule_blocks_correct, check_schedule_quantities_correct,
                         check_disposition_totals, check_referrals_cover_referred_set,
                         check_note_argues_referrals, check_note_limitations_disclosed]
CHECKS = {"static_checks": STATIC_CHECKS,
          "reward_hacking_checks": REWARD_HACKING_CHECKS,
          "partial_oracle_checks": PARTIAL_ORACLE_CHECKS}


def write_error(out: Path, exc: BaseException) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "verifier_status.json").write_text(json.dumps(
        {"status": "verifier_error", "reward_is_graded": False,
         "error_type": type(exc).__name__, "error": str(exc)}, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent-dir", default=os.environ.get("AGENT_DIR", "/logs/agent"))
    ap.add_argument("--input-dir", default=os.environ.get("INPUT_DIR", "/input_artifacts"))
    ap.add_argument("--out-dir", default=os.environ.get("VERIFIER_DIR", "/logs/verifier"))
    args = ap.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    try:
        (out / "reward.json").unlink()
    except (FileNotFoundError, OSError):
        pass

    try:
        ctx = build_context(Path(args.input_dir), Path(args.agent_dir))
        details, buckets, errors = [], {}, []
        for bucket, funcs in CHECKS.items():
            values = []
            for fn in funcs:
                try:
                    score, reason = fn(ctx)
                    score = max(0.0, min(1.0, float(score)))
                except Exception as exc:                               # noqa: BLE001
                    score, reason = 0.0, f"check error {type(exc).__name__}: {exc}"
                    errors.append(f"{fn.__name__}: {type(exc).__name__}: {exc}")
                values.append(score)
                row = {"bucket": bucket, "check_function": fn.__name__, "weight": 1,
                       "score": round(score, 6), "reason": reason}
                details.append(row)
                print(json.dumps(row, sort_keys=True))
            buckets[bucket] = mean(values)

        reward = mean(buckets.values())
        payload = {"reward": round(reward, 6),
                   "total_static_check_score": round(buckets["static_checks"], 6),
                   "total_reward_hacking_check_score": round(buckets["reward_hacking_checks"], 6),
                   "total_partial_oracle_check_score": round(buckets["partial_oracle_checks"], 6)}
        (out / "reward.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        (out / "verify_output.json").write_text(
            json.dumps({"scores": payload, "checks": details}, indent=2) + "\n", encoding="utf-8")
        (out / "verifier_status.json").write_text(json.dumps(
            {"status": "ok" if not errors else "ok_with_check_errors", "reward_is_graded": True,
             "check_count": len(details), "check_errors": errors,
             "bucket_check_counts": {k: len(v) for k, v in CHECKS.items()}}, indent=2) + "\n",
            encoding="utf-8")
        print(json.dumps(payload, sort_keys=True))
        return 0
    except Exception as exc:                                           # noqa: BLE001
        traceback.print_exc()
        write_error(out, exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
