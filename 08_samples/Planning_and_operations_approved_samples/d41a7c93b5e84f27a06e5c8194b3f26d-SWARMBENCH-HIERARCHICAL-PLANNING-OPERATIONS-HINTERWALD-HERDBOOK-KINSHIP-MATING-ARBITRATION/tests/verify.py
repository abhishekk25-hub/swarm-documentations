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
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ROUND_YEAR = 2010
KINSHIP_CEILING = 0.03125
TOP_QUARTILE = 25
NETWORK_PLACES = 14
MAX_COWS_PER_BULL = 2

KINSHIP_COLUMNS = ["animal_id", "sex", "age_class", "holding", "inbreeding_coefficient",
                   "mean_kinship", "mk_rank", "founder_share", "breeding_status",
                   "active_restrictions", "evidence_note"]
ALLOCATION_COLUMNS = ["allocation_id", "cow_id", "bull_id", "pair_kinship", "expected_progeny_f",
                      "host_holding", "cow_mk_rank", "bull_mk_rank",
                      "displaced_alternative_id", "selection_rationale"]
MOVEMENT_COLUMNS = ["movement_id", "animal_id", "from_holding", "to_holding", "movement_reason",
                    "allocation_id", "receiving_health_status", "certificate_class",
                    "transport_category", "isolation_days", "arrival_capacity_after",
                    "evidence_note"]
CONFLICT_COLUMNS = ["conflict_id", "animal_id", "mk_rank", "genetics_position",
                    "veterinary_position", "movement_position", "binding_constraint",
                    "arbitrated_outcome", "resolution_note"]

PLAN_HEADINGS = ["Round outcome", "Conservation standing", "Control totals", "Board conflicts",
                 "Movements and isolation", "Allocation decisions", "Provenance and limitations"]
CONTROL_KEYS = ["living_animals", "breeding_eligible", "allocations_made", "places_committed",
                "movements_planned", "cross_border_movements", "animals_under_restriction",
                "conflicts_recorded"]
CONSTRAINT_CODES = ["AGE", "HEALTH_BLOCK", "RESTED", "NO_ELIGIBLE_PARTNER",
                    "MOVEMENT_BLOCK", "NO_PLACE"]
STATUS_CODES = ["INELIGIBLE_AGE", "HELD_HEALTH", "RESTED", "ELIGIBLE"]
AGE_CODES = ["YOUNGSTOCK", "BREEDING_AGE", "AGED"]
MOVEMENT_REASONS = ["SIRE_PLACEMENT", "ISOLATION_RELIEF"]

PLACEHOLDER = re.compile(r"\b(?:tbd|to be determined|todo|lorem ipsum|placeholder|fill me|"
                         r"insert here|your answer|xxx+)\b", re.I)
ID_RX = re.compile(r"\b\d{15}\b")
WORD_RX = re.compile(r"[A-Za-z0-9'\-]+")


def txt(v: Any) -> str:
    return "" if v is None else str(v).strip()


def frac(n: float, d: float) -> float:
    return 0.0 if d <= 0 else max(0.0, min(1.0, n / d))


def mean(vals) -> float:
    vals = list(vals)
    return 0.0 if not vals else sum(vals) / len(vals)


def num(v: Any):
    try:
        f = float(str(v).strip())
    except (TypeError, ValueError):
        return None
    return None if math.isnan(f) or math.isinf(f) else f


def close(a, b, tol) -> bool:
    return a is not None and abs(a - b) <= tol


def read_csv(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    try:
        with path.open(encoding="utf-8-sig", newline="") as fh:
            return [{(k or "").strip(): txt(v) for k, v in row.items()} for row in csv.DictReader(fh)]
    except (OSError, UnicodeDecodeError, csv.Error):
        return []


def header_of(path: Path) -> list[str]:
    if not path.is_file():
        return []
    try:
        with path.open(encoding="utf-8-sig", newline="") as fh:
            return [h.strip() for h in next(csv.reader(fh), [])]
    except (OSError, UnicodeDecodeError, StopIteration, csv.Error):
        return []


def norm_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def words(s: str) -> list[str]:
    return WORD_RX.findall(s or "")


NOT_A_QUOTE = re.compile(r"^(?:n/?a|nil|none|null|no note|not applicable|no evidence|-{1,3}|–|—)$", re.I)


def quoted_sentence(s: str) -> str:
    q = norm_ws(s).strip("“”‘’\"'")
    if NOT_A_QUOTE.match(q):
        return ""
    q = re.sub(r"^\s*\b\d{15}\b\s*[:,;–-]?\s*", "", q)
    return q.strip()


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def discriminating(hits: dict[str, bool], subset: list[str]) -> float:
    overall = frac(sum(1 for v in hits.values() if v), len(hits)) if hits else 0.0
    if not subset:
        return overall
    hard = frac(sum(1 for a in subset if hits.get(a)), len(subset))
    return math.sqrt(overall * hard)


def build_kinship(pedigree: list[dict]):
    ids = {r["animal_id"] for r in pedigree}
    parents: dict[str, tuple[str | None, str | None]] = {}
    order: list[str] = []
    for r in pedigree:
        sid = r["animal_id"]
        s = r.get("sire_id") if r.get("sire_id") in ids else None
        d = r.get("dam_id") if r.get("dam_id") in ids else None
        if s is None and d is None:
            parents[sid] = (None, None)
            order.append(sid)
            continue
        ps: list[str] = []
        for label, v in (("SIRE", s), ("DAM", d)):
            if v is None:
                fid = f"{sid}:{label}"
                parents[fid] = (None, None)
                order.append(fid)
                ps.append(fid)
            else:
                ps.append(v)
        parents[sid] = (ps[0], ps[1])
        order.append(sid)

    f: dict[tuple[str, str], float] = {}
    get = f.get
    for i, a in enumerate(order):
        p0, p1 = parents[a]
        for j in range(i + 1):
            b = order[j]
            if a == b:
                if p0 and p1:
                    key = (p0, p1) if p0 <= p1 else (p1, p0)
                    val = 0.5 * (1.0 + get(key, 0.0))
                else:
                    val = 0.5
            else:
                v = 0.0
                if p0:
                    v += get((p0, b) if p0 <= b else (b, p0), 0.0)
                if p1:
                    v += get((p1, b) if p1 <= b else (b, p1), 0.0)
                val = 0.5 * v
            if val:
                f[(b, a) if b <= a else (a, b)] = val

    share: dict[str, dict[str, float]] = {}
    for sid in order:
        s, d = parents[sid]
        if s is None and d is None:
            share[sid] = {sid: 1.0}
            continue
        acc: dict[str, float] = {}
        for p in (s, d):
            for fid, v in share.get(p, {}).items():
                acc[fid] = acc.get(fid, 0.0) + 0.5 * v
        share[sid] = acc
    return f, parents, order, share


class Doc(HTMLParser):
    SHAPE_TAGS = {"circle", "ellipse", "rect", "line", "polyline", "polygon", "path", "g", "text"}
    GEOMETRY_TAGS = {"circle", "ellipse", "rect", "line", "polyline", "polygon", "path"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.attrs: list[dict] = []
        self.styles: list[str] = []
        self.json_blocks: dict[str, str] = {}
        self.text_parts: list[str] = []
        self.tags: Counter = Counter()
        self.svg_shape_children = 0
        self._mode: str | None = None
        self._id: str | None = None
        self._svg_depth = 0
        self._open_groups: list[dict] = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        d = {k.lower(): (v or "") for k, v in attrs}
        d["__tag__"] = tag
        d["__in_svg__"] = self._svg_depth > 0
        d["__draws__"] = tag in self.GEOMETRY_TAGS
        self.attrs.append(d)
        self.tags[tag] += 1
        if tag == "svg":
            self._svg_depth += 1
        elif self._svg_depth > 0 and tag in self.GEOMETRY_TAGS:
            self.svg_shape_children += 1
            for grp in self._open_groups:
                grp["__draws__"] = True
        if tag == "g":
            self._open_groups.append(d)
        if tag == "style":
            self._mode = "style"
        elif tag == "script":
            self._mode = "json" if d.get("type", "").lower() == "application/json" else "script"
            self._id = d.get("id", "")

    def handle_endtag(self, tag):
        if tag.lower() == "g" and self._open_groups:
            self._open_groups.pop()
        if tag.lower() == "svg" and self._svg_depth > 0:
            self._svg_depth -= 1
        self._mode = None
        self._id = None

    def handle_data(self, data):
        if self._mode == "style":
            self.styles.append(data)
        elif self._mode == "json" and self._id:
            self.json_blocks[self._id] = self.json_blocks.get(self._id, "") + data
        elif self._mode is None:
            self.text_parts.append(data)


def parse_html(text: str) -> Doc:
    doc = Doc()
    try:
        doc.feed(text)
    except Exception:
        pass
    return doc


def hidden(attrs: dict, css: str) -> bool:
    style = attrs.get("style", "").lower().replace(" ", "")
    if "display:none" in style or "visibility:hidden" in style or "opacity:0" in style:
        return True
    for key in ("width", "height", "r"):
        v = attrs.get(key, "")
        n = num(v.replace("px", "")) if v else None
        if n is not None and n <= 0:
            return True
    for key in ("x", "y", "cx", "cy"):
        n = num(attrs.get(key, ""))
        if n is not None and n < -1000:
            return True
    for cls in attrs.get("class", "").split():
        block = re.search(r"\." + re.escape(cls) + r"\s*\{([^}]*)\}", css or "", re.I)
        if block and re.search(r"display\s*:\s*none|visibility\s*:\s*hidden|opacity\s*:\s*0(?!\.)",
                               block.group(1), re.I):
            return True
    return False


def embedded_json(doc: Doc, block_id: str):
    raw = doc.json_blocks.get(block_id)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def embedded_table(doc: Doc, block_id: str):
    blob = embedded_json(doc, block_id)
    if isinstance(blob, list) and any(isinstance(d, dict) and d for d in blob):
        return blob
    return None


def build_context(input_dir: Path, agent_dir: Path, tests_dir: Path) -> dict:
    ped = read_csv(input_dir / "herdbook_pedigree.csv")
    holdings = read_csv(input_dir / "member_holdings.csv")
    weights = read_csv(input_dir / "weight_records.csv")
    prior = read_csv(input_dir / "previous_matings.csv")
    rules = read_csv(input_dir / "movement_rules.csv")

    standing_path = tests_dir / "health_standing.json"
    standing = json.loads(standing_path.read_text(encoding="utf-8"))
    truth = standing["animals"]

    rec = {r["animal_id"]: r for r in ped}
    living = sorted(r["animal_id"] for r in ped if r.get("status") == "LIVING")
    living_set = set(living)

    f, parents, order, share = build_kinship(ped)

    def kin(a: str, b: str) -> float:
        return f.get((a, b) if a <= b else (b, a), 0.0)

    mk = {a: sum(kin(a, b) for b in living) / len(living) for a in living} if living else {}
    inbreeding = {}
    for a in living:
        pa = parents.get(a, (None, None))
        inbreeding[a] = kin(pa[0], pa[1]) if pa[0] and pa[1] else 0.0
    ranked = sorted(living, key=lambda a: (round(mk[a], 9), a))
    rank = {a: i + 1 for i, a in enumerate(ranked)}

    age_class = {}
    for a in living:
        yrs = ROUND_YEAR - int(num(rec[a].get("birth_year")) or 0)
        age_class[a] = "YOUNGSTOCK" if yrs < 2 else ("BREEDING_AGE" if yrs <= 12 else "AGED")

    binding = {a: dict(truth.get(a, {}).get("binding", {})) for a in living}
    governing = {a: dict(truth.get(a, {}).get("governing", {})) for a in living}

    calvings09: Counter = Counter()
    failed_pairs: Counter = Counter()
    for r in prior:
        if txt(r.get("season")) == "2009":
            calvings09[r.get("cow_id", "")] += int(num(r.get("calvings")) or 0)
        if txt(r.get("outcome")) == "FAILED":
            failed_pairs[(r.get("cow_id", ""), r.get("bull_id", ""))] += 1

    status = {}
    for a in living:
        keys = set(binding[a])
        if age_class[a] != "BREEDING_AGE":
            status[a] = "INELIGIBLE_AGE"
        elif "BREEDING_BLOCK" in keys or "ISOLATION_ONLY" in keys:
            status[a] = "HELD_HEALTH"
        elif rec[a].get("sex") == "female" and calvings09[a] >= 2:
            status[a] = "RESTED"
        else:
            status[a] = "ELIGIBLE"

    hold = {h["holding_code"]: h for h in holdings}
    free_places = {c: int(num(h.get("breeding_places")) or 0) - int(num(h.get("breeding_places_occupied")) or 0)
                   for c, h in hold.items()}
    free_boxes = {c: int(num(h.get("isolation_boxes")) or 0) - int(num(h.get("isolation_boxes_occupied")) or 0)
                  for c, h in hold.items()}
    home = {a: rec[a].get("holding", "") for a in living}

    latest_weight: dict[str, float] = {}
    seen: dict[str, str] = {}
    for r in weights:
        sid, when = r.get("animal_id", ""), r.get("weighed_on", "")
        if sid in living_set and (sid not in seen or when > seen[sid]):
            seen[sid] = when
            latest_weight[sid] = num(r.get("liveweight_kg")) or 0.0

    rulemap = {(r.get("rule_type"), r.get("rule_key")): r.get("rule_value") for r in rules}

    def transport_category(a: str) -> str:
        w = latest_weight.get(a)
        if w is None:
            return ""
        if w < 350.0:
            return rulemap.get(("transport_category", "LIVEWEIGHT_UNDER_350"), "CAT_1")
        if w <= 550.0:
            return rulemap.get(("transport_category", "LIVEWEIGHT_350_TO_550"), "CAT_2")
        return rulemap.get(("transport_category", "LIVEWEIGHT_ABOVE_550"), "CAT_3")

    def crosses_border(a: str, b: str) -> bool:
        return hold.get(a, {}).get("country") != hold.get(b, {}).get("country")

    def certificate_class(src: str, dst: str) -> str:
        key = "CROSS_BORDER" if crosses_border(src, dst) else "DOMESTIC"
        return rulemap.get(("certificate_class", key), key)

    def isolation_days(a: str, src: str, dst: str) -> int:
        hs = hold.get(dst, {}).get("health_status", "")
        key = ("CROSS_BORDER" if crosses_border(src, dst) else "DOMESTIC") + "|" + hs
        base = int(num(rulemap.get(("isolation_base_days", key))) or 0)
        ext = binding.get(a, {}).get("EXTENDED_ISOLATION")
        return base + (int(ext.get("days") or 0) if isinstance(ext, dict) else 0)

    over_committed = [c for c, h in hold.items()
                      if int(num(h.get("isolation_boxes_occupied")) or 0) > int(num(h.get("isolation_boxes")) or 0)]
    relief_required = sorted(a for a in living
                             if home[a] in over_committed
                             and "ISOLATION_ONLY" in binding[a]
                             and "MOVEMENT_BLOCK" not in binding[a])

    ctx: dict[str, Any] = {
        "pedigree": ped, "rec": rec, "living": living, "living_set": living_set,
        "kin": kin, "parents": parents, "share": share, "mk": mk, "rank": rank, "ranked": ranked,
        "inbreeding": inbreeding, "age_class": age_class, "binding": binding, "governing": governing,
        "status": status, "calvings09": calvings09, "failed_pairs": failed_pairs, "prior": prior,
        "hold": hold, "free_places": free_places, "free_boxes": free_boxes, "home": home,
        "latest_weight": latest_weight, "rulemap": rulemap,
        "transport_category": transport_category, "certificate_class": certificate_class,
        "isolation_days": isolation_days, "crosses_border": crosses_border,
        "over_committed": over_committed, "relief_required": relief_required,
    }

    ctx["paths"] = {
        "kinship": agent_dir / "kinship_register.csv",
        "allocation": agent_dir / "mating_allocations.csv",
        "movement": agent_dir / "movement_plan.csv",
        "conflict": agent_dir / "board_conflicts.csv",
        "dashboard": agent_dir / "herd_dashboard.html",
        "plan": agent_dir / "conservation_plan.md",
    }
    ctx["kinship_rows"] = read_csv(ctx["paths"]["kinship"])
    ctx["allocation_rows"] = read_csv(ctx["paths"]["allocation"])
    ctx["movement_rows"] = read_csv(ctx["paths"]["movement"])
    ctx["conflict_rows"] = read_csv(ctx["paths"]["conflict"])
    ctx["html_text"] = read_text(ctx["paths"]["dashboard"])
    ctx["doc"] = parse_html(ctx["html_text"]) if ctx["html_text"] else None
    ctx["plan_text"] = read_text(ctx["paths"]["plan"])
    ctx["valid_allocations"] = _valid_allocations(ctx)
    return ctx


def founder_items(raw: str) -> list[str]:
    return [p for p in re.split(r"[|;]", raw or "") if p.strip()]


def parse_founder_share(ctx, raw: str) -> dict[str, float]:
    base = {a for a, p in ctx["parents"].items() if p == (None, None) and a in ctx["rec"]}
    out: dict[str, float] = {}
    for item in founder_items(raw):
        if ":" not in item:
            continue
        label, _, val = item.rpartition(":")
        v = num(val)
        if v is None:
            continue
        label = label.strip()
        head, sep, tail = label.rpartition(":")
        if sep and tail in ("SIRE", "DAM") and head in base:
            label = head
        out[label] = out.get(label, 0.0) + v
    return out


def allocation_blocked(ctx, cow: str, bull: str, host: str) -> str:
    rec, status, binding = ctx["rec"], ctx["status"], ctx["binding"]
    if cow not in ctx["living_set"] or bull not in ctx["living_set"]:
        return "unknown animal"
    if rec[cow].get("sex") != "female" or rec[bull].get("sex") != "male":
        return "sex mismatch"
    if status[cow] != "ELIGIBLE" or status[bull] != "ELIGIBLE":
        return "not both eligible"
    if ctx["kin"](cow, bull) >= KINSHIP_CEILING:
        return "kinship ceiling"
    if f"MATING_EXCLUSION:{bull}" in binding[cow] or f"MATING_EXCLUSION:{cow}" in binding[bull]:
        return "mating exclusion"
    if ctx["failed_pairs"][(cow, bull)] >= 2:
        return "twice failed"
    if host != ctx["home"][cow]:
        return "host is not the cow's holding"
    if ctx["home"][bull] != host and "MOVEMENT_BLOCK" in binding[bull]:
        return "bull under movement block"
    return ""


def _valid_allocations(ctx) -> list[dict]:
    seen_cows: set[str] = set()
    seen_ids: set[str] = set()
    bull_use: Counter = Counter()
    bull_host: dict[str, str] = {}
    hosted: Counter = Counter()
    out = []
    for r in ctx["allocation_rows"]:
        aid = txt(r.get("allocation_id"))
        cow, bull, host = txt(r.get("cow_id")), txt(r.get("bull_id")), txt(r.get("host_holding"))
        if not aid or aid in seen_ids or cow in seen_cows:
            continue
        if allocation_blocked(ctx, cow, bull, host):
            continue
        if bull_use[bull] >= MAX_COWS_PER_BULL:
            continue
        if bull in bull_host and bull_host[bull] != host:
            continue
        if ctx["free_places"].get(host, 0) - hosted[host] <= 0:
            continue
        seen_ids.add(aid)
        seen_cows.add(cow)
        bull_use[bull] += 1
        bull_host[bull] = host
        hosted[host] += 1
        out.append({"allocation_id": aid, "cow_id": cow, "bull_id": bull, "host": host, "row": r})
    return out


def expected_sire_movements(ctx) -> dict[str, dict]:
    out = {}
    for a in ctx["valid_allocations"]:
        bull, host = a["bull_id"], a["host"]
        if ctx["home"][bull] != host:
            out[bull] = {"from": ctx["home"][bull], "to": host, "allocation_id": a["allocation_id"]}
    return out


def partner_options(ctx, animal: str) -> tuple[list[str], list[str]]:
    is_cow = ctx["rec"][animal].get("sex") == "female"
    others = [o for o in ctx["living"]
              if ctx["status"][o] == "ELIGIBLE"
              and (ctx["rec"][o].get("sex") == "male" if is_cow else ctx["rec"][o].get("sex") == "female")]
    workable, relaxed = [], []
    for o in others:
        cow, bull = (animal, o) if is_cow else (o, animal)
        if ctx["kin"](cow, bull) >= KINSHIP_CEILING:
            continue
        if f"MATING_EXCLUSION:{bull}" in ctx["binding"][cow] or \
           f"MATING_EXCLUSION:{cow}" in ctx["binding"][bull]:
            continue
        if ctx["failed_pairs"][(cow, bull)] >= 2:
            continue
        relaxed.append(o)
        if not allocation_blocked(ctx, cow, bull, ctx["home"][cow]):
            workable.append(o)
    return workable, relaxed


def expected_conflicts(ctx) -> dict[str, str]:
    placed = {b for a in ctx["valid_allocations"] for b in (a["cow_id"], a["bull_id"])}
    out: dict[str, str] = {}
    for animal in ctx["ranked"][:TOP_QUARTILE]:
        if animal in placed:
            continue
        st = ctx["status"][animal]
        if st == "INELIGIBLE_AGE":
            out[animal] = "AGE"
            continue
        if st == "HELD_HEALTH":
            out[animal] = "HEALTH_BLOCK"
            continue
        if st == "RESTED":
            out[animal] = "RESTED"
            continue
        workable, relaxed = partner_options(ctx, animal)
        if workable:
            out[animal] = "NO_PLACE"
        elif relaxed:
            out[animal] = "MOVEMENT_BLOCK"
        else:
            out[animal] = "NO_ELIGIBLE_PARTNER"
    return out


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
    specs = [("kinship", KINSHIP_COLUMNS), ("allocation", ALLOCATION_COLUMNS),
             ("movement", MOVEMENT_COLUMNS), ("conflict", CONFLICT_COLUMNS)]
    good, notes = 0, []
    for key, cols in specs:
        got = header_of(ctx["paths"][key])
        if got == cols:
            good += 1
        else:
            notes.append(f"{key}: {'missing' if not got else 'header mismatch'}")
    return frac(good, len(specs)), f"{good}/{len(specs)} CSV headers exact; {notes or 'all exact'}"


def check_typed_fields(ctx):
    checks: list[bool] = []
    for r in ctx["kinship_rows"]:
        checks.append(num(r.get("inbreeding_coefficient")) is not None)
        checks.append(num(r.get("mean_kinship")) is not None)
        n = num(r.get("mk_rank"))
        checks.append(n is not None and float(n).is_integer() and 1 <= n <= max(1, len(ctx["living"])))
        checks.append(txt(r.get("breeding_status")) in STATUS_CODES)
        checks.append(txt(r.get("age_class")) in AGE_CODES)
    for r in ctx["allocation_rows"]:
        checks.append(num(r.get("pair_kinship")) is not None)
        checks.append(num(r.get("expected_progeny_f")) is not None)
        checks.append(txt(r.get("host_holding")) in ctx["hold"])
    for r in ctx["movement_rows"]:
        checks.append(txt(r.get("movement_reason")) in MOVEMENT_REASONS)
        d = num(r.get("isolation_days"))
        checks.append(d is not None and d >= 0 and float(d).is_integer())
        c = num(r.get("arrival_capacity_after"))
        checks.append(c is not None and c >= 0)
        checks.append(txt(r.get("to_holding")) in ctx["hold"])
    for r in ctx["conflict_rows"]:
        checks.append(txt(r.get("binding_constraint")) in CONSTRAINT_CODES)
        checks.append(num(r.get("mk_rank")) is not None)
    if not checks:
        return 0.0, "no rows to type-check"
    varied = []
    for rows, col in ((ctx["kinship_rows"], "mean_kinship"), (ctx["kinship_rows"], "mk_rank"),
                      (ctx["kinship_rows"], "inbreeding_coefficient"),
                      (ctx["allocation_rows"], "pair_kinship")):
        vals = [txt(r.get(col)) for r in rows if txt(r.get(col))]
        if len(vals) >= 4:
            varied.append(float(len(set(vals)) >= max(2, len(vals) // 4)))
    typed = frac(sum(checks), len(checks))
    score = mean([typed, mean(varied)]) if varied else typed
    return score, (
        f"{sum(checks)}/{len(checks)} typed fields parse and use a declared vocabulary; "
        f"{sum(varied):.0f}/{len(varied)} of the columns that must differ between animals "
        f"actually differ")


def check_living_herd_coverage(ctx):
    counts = Counter(txt(r.get("animal_id")) for r in ctx["kinship_rows"])
    good = sum(1 for a in ctx["living"] if counts.get(a) == 1)
    return frac(good, len(ctx["living"])), \
        f"{good}/{len(ctx['living'])} living animals carry exactly one standing row"


def bound_visible_marks(ctx) -> list[dict]:
    doc = ctx["doc"]
    if not doc:
        return []
    css = "\n".join(doc.styles)
    return [a for a in doc.attrs
            if a.get("data-animal-id") and a["__tag__"] in Doc.SHAPE_TAGS
            and a.get("__in_svg__") and a.get("__draws__") and not hidden(a, css)]


def check_dashboard_basic_shape(ctx):
    doc = ctx["doc"]
    if not doc:
        return 0.0, "herd_dashboard.html missing or unparseable"
    bound = len({a["data-animal-id"] for a in bound_visible_marks(ctx)})
    bits = [
        bool(doc.tags.get("svg")),
        embedded_table(doc, "kinship-data") is not None,
        embedded_table(doc, "allocation-data") is not None,
        embedded_table(doc, "conflict-data") is not None,
        bound >= 40,
    ]
    return frac(sum(bits), len(bits)), (
        f"svg={bits[0]}, kinship-data={bits[1]}, allocation-data={bits[2]}, "
        f"conflict-data={bits[3]}, distinct animals with a visible in-svg mark={bound} "
        f"(>=40 wanted; raw geometry drawn={doc.svg_shape_children})")


def check_conservation_plan_shape(ctx):
    text = ctx["plan_text"]
    if not text:
        return 0.0, "conservation_plan.md missing"
    wc = len(words(text))
    found = [h for h in PLAN_HEADINGS if re.search(r"^#{1,4}\s*" + re.escape(h) + r"\s*$", text, re.M | re.I)]
    keys = [k for k in CONTROL_KEYS if re.search(r"^\|\s*`?" + re.escape(k) + r"`?\s*\|", text, re.M)]
    return mean([float(1800 <= wc <= 3200), frac(len(found), len(PLAN_HEADINGS)),
                 frac(len(keys), len(CONTROL_KEYS))]), (
        f"words={wc} (want 1800-3200), headings={len(found)}/{len(PLAN_HEADINGS)}, "
        f"control-total keys={len(keys)}/{len(CONTROL_KEYS)}")


def check_no_invented_or_duplicated_ids(ctx):
    living = ctx["living_set"]
    checks = []
    seen = Counter(txt(r.get("animal_id")) for r in ctx["kinship_rows"])
    for r in ctx["kinship_rows"]:
        sid = txt(r.get("animal_id"))
        checks.append(sid in living and seen[sid] == 1)
    alloc_ids = Counter(txt(r.get("allocation_id")) for r in ctx["allocation_rows"])
    cow_use = Counter(txt(r.get("cow_id")) for r in ctx["allocation_rows"])
    bull_use = Counter(txt(r.get("bull_id")) for r in ctx["allocation_rows"])
    for r in ctx["allocation_rows"]:
        cow, bull = txt(r.get("cow_id")), txt(r.get("bull_id"))
        checks.append(cow in living and bull in living and cow != bull
                      and ctx["rec"].get(cow, {}).get("sex") == "female"
                      and ctx["rec"].get(bull, {}).get("sex") == "male"
                      and ctx["status"].get(cow) == "ELIGIBLE"
                      and ctx["status"].get(bull) == "ELIGIBLE"
                      and alloc_ids[txt(r.get("allocation_id"))] == 1
                      and cow_use[cow] == 1 and bull_use[bull] <= MAX_COWS_PER_BULL)
    move_ids = Counter(txt(r.get("movement_id")) for r in ctx["movement_rows"])
    moved = Counter(txt(r.get("animal_id")) for r in ctx["movement_rows"])
    for r in ctx["movement_rows"]:
        sid = txt(r.get("animal_id"))
        checks.append(sid in living and move_ids[txt(r.get("movement_id"))] == 1 and moved[sid] == 1
                      and txt(r.get("from_holding")) != txt(r.get("to_holding")))
    cids = Counter(txt(r.get("animal_id")) for r in ctx["conflict_rows"])
    for r in ctx["conflict_rows"]:
        sid = txt(r.get("animal_id"))
        checks.append(sid in living and cids[sid] == 1)
    if not checks:
        return 0.0, "no rows submitted"
    return frac(sum(checks), len(checks)), \
        f"{sum(checks)}/{len(checks)} rows carry a real, non-duplicated identity"


def check_founder_share_not_padded(ctx):
    rows = ctx["kinship_rows"]
    if not rows:
        return 0.0, "no standing rows"
    good = 0
    strings = []
    for r in rows:
        raw = txt(r.get("founder_share"))
        strings.append(raw)
        items = founder_items(raw)
        ok = bool(items)
        seen_labels: list[str] = []
        for it in items:
            if ":" not in it:
                ok = False
                break
            label, _, val = it.rpartition(":")
            v = num(val)
            if v is None or v <= 0:
                ok = False
                break
            seen_labels.append(label.strip())
        parsed = parse_founder_share(ctx, raw)
        labels = list(parsed)
        total = sum(parsed.values())
        sid = txt(r.get("animal_id"))
        true_founders = {k for k, v in ctx["share"].get(sid, {}).items() if v >= 5e-5}
        real_named = len(set(labels) & true_founders)
        depth_ok = len(labels) >= 2 or ctx["parents"].get(sid, ("x",))[0] is None
        grounded_ok = bool(true_founders) and real_named == len(true_founders) \
            and not (set(labels) - true_founders)
        if ok and depth_ok and grounded_ok and len(seen_labels) == len(set(seen_labels)) \
                and abs(total - 1.0) <= 0.002:
            good += 1
    distinct = len({s for s in strings if s})
    return mean([frac(good, len(rows)), frac(distinct, max(1, len(rows) * 0.5))]), (
        f"{good}/{len(rows)} founder-share strings well formed and summing to 1; "
        f"{distinct} distinct strings across {len(rows)} rows")


def check_evidence_quotes_are_governing(ctx):
    rows = [r for r in ctx["kinship_rows"] if quoted_sentence(txt(r.get("evidence_note")))]
    if not rows:
        return 0.0, "no evidence quotations supplied"
    good = 0
    for r in rows:
        sid = txt(r.get("animal_id"))
        quote = quoted_sentence(txt(r.get("evidence_note")))
        pool = " || ".join(norm_ws(g.get("evidence", ""))
                           for g in ctx["governing"].get(sid, {}).values())
        if len(quote) >= 40 and quote in pool:
            good += 1
    return frac(good, len(rows)), (
        f"{good}/{len(rows)} quotations come verbatim from a statement that actually governs "
        f"one of that animal's own restrictions")


def check_evidence_settles_breeding_standing(ctx):
    expected: dict[str, str] = {}
    for a in ctx["living"]:
        gov = ctx["governing"][a]
        for key in ("BREEDING_BLOCK", "ISOLATION_ONLY"):
            if key in ctx["binding"][a]:
                expected[a] = norm_ws(ctx["binding"][a][key].get("evidence", ""))
                break
        else:
            for key in ("BREEDING_BLOCK", "ISOLATION_ONLY"):
                if key in gov:
                    expected[a] = norm_ws(gov[key].get("evidence", ""))
                    break
    if not expected:
        return 0.0, "no animal has a breeding-relevant statement"
    submitted = {txt(r.get("animal_id")): quoted_sentence(txt(r.get("evidence_note")))
                 for r in ctx["kinship_rows"]}
    def quoted_exactly(got: str, want: str) -> bool:
        g, w = got.rstrip(" ."), want.rstrip(" .")
        return bool(g) and g == w
    good = sum(1 for a, want in expected.items()
               if submitted.get(a) and quoted_exactly(submitted[a], want))
    unwarranted = [a for a in ctx["living"]
                   if a not in expected and submitted.get(a)]
    return frac(good, len(expected) + len(unwarranted)), (
        f"{good}/{len(expected)} animals quote the statement that settles their breeding "
        f"standing; {len(unwarranted)} animals carry a quotation where nothing bears on it")


def check_allocation_rows_not_fabricated(ctx):
    rows = ctx["allocation_rows"]
    if not rows:
        return 0.0, "no allocations submitted"
    good = 0
    for r in rows:
        cow, bull = txt(r.get("cow_id")), txt(r.get("bull_id"))
        alt = txt(r.get("displaced_alternative_id"))
        rationale = txt(r.get("selection_rationale"))
        alt_real = alt in ctx["living_set"] and alt not in (cow, bull)
        alt_workable = False
        if alt_real and cow in ctx["living_set"]:
            if ctx["rec"][alt].get("sex") == "male":
                alt_workable = not allocation_blocked(ctx, cow, alt, ctx["home"].get(cow, ""))
            elif ctx["rec"][alt].get("sex") == "female" and bull in ctx["living_set"]:
                alt_workable = not allocation_blocked(ctx, alt, bull, ctx["home"].get(alt, ""))
        bits = [
            cow in ctx["living_set"] and bull in ctx["living_set"],
            alt_real and alt_workable,
            len(words(rationale)) >= 18,
            bool(ID_RX.search(rationale)) and bool({cow, bull} & set(ID_RX.findall(rationale))),
            alt in rationale or txt(r.get("host_holding")) in rationale,
            any(v and v in rationale for v in (txt(r.get("pair_kinship")),
                                               txt(r.get("cow_mk_rank")), txt(r.get("bull_mk_rank")))),
            alt_real and (f"{ctx['kin'](cow, alt):.5f}" in rationale
                          if ctx["rec"].get(alt, {}).get("sex") == "male"
                          else f"{ctx['kin'](alt, bull):.5f}" in rationale
                          or str(ctx["rank"].get(alt, "")) and
                          re.search(r"\b" + str(ctx["rank"].get(alt, 0)) + r"\b", rationale) is not None),
        ]
        if all(bits):
            good += 1
    return frac(good, len(rows)), (
        f"{good}/{len(rows)} allocations name a displaced alternative that was itself a "
        f"workable option and argue from their own figures")


def check_movement_rows_not_padded(ctx):
    rows = ctx["movement_rows"]
    if not rows:
        return 0.0, "no movements submitted"
    good = 0
    for r in rows:
        sid = txt(r.get("animal_id"))
        bits = [
            sid in ctx["living_set"],
            txt(r.get("from_holding")) == ctx["home"].get(sid, "\0"),
            txt(r.get("to_holding")) in ctx["hold"],
            "MOVEMENT_BLOCK" not in ctx["binding"].get(sid, {}),
        ]
        reason = txt(r.get("movement_reason"))
        if reason == "SIRE_PLACEMENT":
            bits.append(txt(r.get("allocation_id")) in {a["allocation_id"] for a in ctx["valid_allocations"]})
        elif reason == "ISOLATION_RELIEF":
            bits.append(not txt(r.get("allocation_id")))
        else:
            bits.append(False)
        if all(bits):
            good += 1
    return frac(good, len(rows)), (
        f"{good}/{len(rows)} movements leave the animal's real holding for a reason the round creates")


def check_cross_artifact_reconciliation(ctx):
    checks = []
    for a in ctx["valid_allocations"]:
        for animal, col in ((a["cow_id"], "cow_mk_rank"), (a["bull_id"], "bull_mk_rank")):
            checks.append(close(num(a["row"].get(col)), float(ctx["rank"][animal]), 0.01))
            checks.append(ctx["status"][animal] == "ELIGIBLE")
        checks.append(a["host"] == ctx["home"][a["cow_id"]])
    placed = {b for a in ctx["valid_allocations"] for b in (a["cow_id"], a["bull_id"])}
    for r in ctx["conflict_rows"]:
        sid = txt(r.get("animal_id"))
        checks.append(sid in ctx["living_set"] and sid not in placed)
        checks.append(sid in ctx["rank"] and close(num(r.get("mk_rank")), float(ctx["rank"][sid]), 0.01))
    for r in ctx["movement_rows"]:
        sid = txt(r.get("animal_id"))
        checks.append(sid in ctx["home"] and txt(r.get("from_holding")) == ctx["home"][sid])
    for r in ctx["kinship_rows"]:
        sid = txt(r.get("animal_id"))
        if sid in ctx["home"]:
            checks.append(txt(r.get("holding")) == ctx["home"][sid])
    if not checks:
        return 0.0, "no cross-artifact links to reconcile"
    return frac(sum(checks), len(checks)), (
        f"{sum(checks)}/{len(checks)} cross-artifact facts agree with the recomputed herdbook")


def check_artifacts_bounded_and_not_templated(ctx):
    bits = []
    for _, p in ctx["paths"].items():
        size = p.stat().st_size if p.is_file() else 0
        bits.append(0 < size <= 4_000_000)
    bits.append(not any(PLACEHOLDER.search(b or "") for b in (ctx["plan_text"], ctx["html_text"])))
    for rows, col in ((ctx["allocation_rows"], "selection_rationale"),
                      (ctx["conflict_rows"], "resolution_note")):
        vals = [norm_ws(txt(r.get(col))).lower() for r in rows if txt(r.get(col))]
        bits.append(bool(vals) and len(set(vals)) == len(vals))
    paras = [norm_ws(p).lower() for p in re.split(r"\n\s*\n", ctx["plan_text"]) if len(words(p)) >= 25]
    bits.append(bool(paras) and len(set(paras)) == len(paras))
    payloads = ["|".join(txt(r.get(c)) for c in KINSHIP_COLUMNS if c != "animal_id")
                for r in ctx["kinship_rows"]]
    bits.append(bool(payloads) and len(set(payloads)) >= max(2, len(payloads) * 0.5))
    return frac(sum(1 for b in bits if b), len(bits)), \
        f"{sum(1 for b in bits if b)}/{len(bits)} bounded-and-original checks pass"


TRANSLATE_RX = re.compile(r"translate\(\s*(-?[\d.]+)[ ,]+(-?[\d.]+)")


def _mark_geometry(attrs: dict):
    x = y = None
    m = TRANSLATE_RX.search(attrs.get("transform", ""))
    if m:
        x, y = float(m.group(1)), float(m.group(2))
    for key, target in (("x", "x"), ("cx", "x"), ("y", "y"), ("cy", "y")):
        v = num(attrs.get(key, ""))
        if v is not None:
            if target == "x" and x is None:
                x = v
            elif target == "y" and y is None:
                y = v
    size = None
    for key in ("r", "width", "height"):
        v = num(str(attrs.get(key, "")).replace("px", ""))
        if v is not None:
            size = v
            break
    fill = attrs.get("fill", "")
    if not fill:
        m = re.search(r"fill\s*:\s*([^;]+)", attrs.get("style", ""), re.I)
        if m:
            fill = m.group(1).strip()
    return x, y, size, fill


def _spearman(pairs) -> float:
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

    xs, ys = ranked([p[0] for p in pairs]), ranked([p[1] for p in pairs])
    mx, my = sum(xs) / n, sum(ys) / n
    num_ = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    den = (sum((xs[i] - mx) ** 2 for i in range(n)) * sum((ys[i] - my) ** 2 for i in range(n))) ** 0.5
    return 0.0 if den == 0 else abs(num_ / den)


def check_dashboard_not_hidden_or_hollow(ctx):
    doc = ctx["doc"]
    if not doc:
        return 0.0, "dashboard missing"
    marks = bound_visible_marks(ctx)
    ids = {a["data-animal-id"] for a in marks}
    body = norm_ws(" ".join(doc.text_parts))

    best, channel = 0.0, "none"
    by_id: dict[str, dict] = {}
    for a in marks:
        by_id.setdefault(a["data-animal-id"], a)
    known = [(i, g) for i, a in by_id.items() if i in ctx["rank"]
             for g in [_mark_geometry(a)]]
    if len(known) >= 8:
        order_sig = []
        for i, (x, y, _s, _f) in known:
            if x is not None and y is not None:
                order_sig.append((round(y, 3) * 100000 + round(x, 3), ctx["rank"][i]))
        x_sig = [(x, ctx["rank"][i]) for i, (x, _y, _s, _f) in known if x is not None]
        y_sig = [(y, ctx["rank"][i]) for i, (_x, y, _s, _f) in known if y is not None]
        size_sig = [(s, ctx["rank"][i]) for i, (_x, _y, s, _f) in known if s is not None]
        fills = {f for _i, (_x, _y, _s, f) in known if f}
        colour_sig = []
        if 2 <= len(fills) <= 12:
            idx = {f: n for n, f in enumerate(sorted(fills))}
            colour_sig = [(idx.get(f), ctx["rank"][i]) for i, (_x, _y, _s, f) in known if f]
        for name, sig in (("reading order", order_sig), ("horizontal position", x_sig),
                          ("vertical position", y_sig), ("size", size_sig), ("colour", colour_sig)):
            r = _spearman(sig)
            if r > best:
                best, channel = r, name

    drawn = mean([
        frac(len(ids & ctx["living_set"]), len(ctx["living_set"])),
        float(len(ids) >= 40),
        float(bool(marks) and all(a.get("data-animal-id") in ctx["living_set"] for a in marks)),
        float(len(body) >= 400),
    ])
    priority = frac(best, 0.75)
    return drawn * priority, (
        f"{len(ids)} visible in-svg marks bound to animal ids; "
        f"{len(ids & ctx['living_set'])}/{len(ctx['living_set'])} of the living herd covered; "
        f"marks drawn={drawn:.2f}; strongest rank-encoding channel {channel} rho={best:.2f} "
        f"(priority term={priority:.2f}, applied as a multiplier)")


def check_conservation_plan_not_templated(ctx):
    text = ctx["plan_text"]
    if not text:
        return 0.0, "conservation plan missing"
    sections, cur = {}, None
    for line in text.splitlines():
        m = re.match(r"^#{1,4}\s*(.+?)\s*$", line)
        if m:
            cur = m.group(1)
            sections[cur] = []
        elif cur:
            sections[cur].append(line)
    bodies = {k: norm_ws(" ".join(v)).lower() for k, v in sections.items() if len(words(" ".join(v))) >= 40}
    sentences = [norm_ws(s).lower() for s in re.split(r"(?<=[.!?])\s+", text) if len(words(s)) >= 8]
    novel, seen_shingles = 0, set()
    for s in sentences:
        w = words(s)
        sh = {tuple(w[i:i + 5]) for i in range(len(w) - 4)}
        if not sh or len(sh - seen_shingles) / len(sh) >= 0.4:
            novel += 1
        seen_shingles |= sh
    bits = [
        float(len(bodies) >= 5),
        float(len(set(bodies.values())) == len(bodies)) if bodies else 0.0,
        float(len({i for i in ID_RX.findall(text) if i in ctx["living_set"]}) >= 12),
        float(not PLACEHOLDER.search(text)),
        float(len(set(words(text.lower()))) >= 420),
        frac(novel, len(sentences)) if sentences else 0.0,
    ]
    return mean(bits), (
        f"{len(bodies)} substantive sections, "
        f"{len({i for i in ID_RX.findall(text) if i in ctx['living_set']})} real animals named, "
        f"{len(set(words(text.lower())))} distinct words")


def check_conflict_positions_are_specific(ctx):
    rows = ctx["conflict_rows"]
    if not rows:
        return 0.0, "no conflicts recorded"
    good = 0
    for r in rows:
        sid = txt(r.get("animal_id"))
        gen = txt(r.get("genetics_position"))
        vet = txt(r.get("veterinary_position"))
        mov = txt(r.get("movement_position"))
        note = txt(r.get("resolution_note"))
        rank = ctx["rank"].get(sid)
        keys = set(ctx["binding"].get(sid, {}))
        bits = [
            all(len(words(x)) >= 6 for x in (gen, vet, mov, note)),
            rank is not None and re.search(r"\b" + str(rank) + r"\b", gen) is not None,
            (not keys and re.search(r"\bno\b|\bnone\b|clear|unrestricted|no restriction", vet, re.I) is not None)
            or any(k.split(":")[0].lower().replace("_", " ") in vet.lower().replace("_", " ") for k in keys),
            ctx["home"].get(sid, "\0") in mov or ctx["home"].get(sid, "\0") in note,
            sid in note or sid in gen,
            sid in ctx["mk"] and f"{ctx['mk'][sid]:.5f}" in (gen + " " + note),
            any(f"{ctx['mk'][i]:.5f}" in (gen + " " + note)
                for i in ID_RX.findall(gen + " " + note)
                if i in ctx["living_set"] and i != sid and i in ctx["mk"]),
        ]
        if all(bits):
            good += 1
    return frac(good, len(rows)), (
        f"{good}/{len(rows)} conflict rows state each board's position in that animal's own "
        f"terms, carry its own recomputed figure, and measure it against a named animal "
        f"whose own figure is quoted correctly")


def _by_id(rows):
    return {txt(r.get("animal_id")): r for r in rows}


def check_inbreeding_coefficients(ctx):
    got = _by_id(ctx["kinship_rows"])
    hits = {a: (a in got and close(num(got[a].get("inbreeding_coefficient")), ctx["inbreeding"][a], 1.1e-4))
            for a in ctx["living"]}
    inbred = [a for a in ctx["living"] if ctx["inbreeding"][a] > 0]
    return discriminating(hits, inbred), (
        f"{sum(hits.values())}/{len(hits)} inbreeding coefficients match the recomputed pedigree, "
        f"{sum(1 for a in inbred if hits[a])}/{len(inbred)} among the actually inbred animals")


def check_mean_kinship_values(ctx):
    got = _by_id(ctx["kinship_rows"])
    good = sum(1 for a in ctx["living"]
               if a in got and close(num(got[a].get("mean_kinship")), ctx["mk"][a], 1.1e-5))
    return frac(good, len(ctx["living"])), \
        f"{good}/{len(ctx['living'])} mean-kinship values match the recomputed matrix"


def check_mean_kinship_ranks(ctx):
    got = _by_id(ctx["kinship_rows"])
    good = sum(1 for a in ctx["living"]
               if a in got and close(num(got[a].get("mk_rank")), float(ctx["rank"][a]), 0.01))
    return frac(good, len(ctx["living"])), \
        f"{good}/{len(ctx['living'])} conservation-priority ranks match, ties broken by animal id"


def check_founder_shares_exact(ctx):
    got = _by_id(ctx["kinship_rows"])
    good = 0
    for a in ctx["living"]:
        row = got.get(a)
        if not row:
            continue
        want = {k: v for k, v in ctx["share"].get(a, {}).items() if v >= 5e-5}
        parsed = parse_founder_share(ctx, txt(row.get("founder_share")))
        if set(parsed) == set(want) and all(abs(parsed[k] - want[k]) <= 1.1e-4 for k in want):
            good += 1
    return frac(good, len(ctx["living"])), \
        f"{good}/{len(ctx['living'])} founder-share vectors match the recomputed descent"


def check_age_class_and_residence(ctx):
    got = _by_id(ctx["kinship_rows"])
    hits = {}
    for a in ctx["living"]:
        row = got.get(a)
        hits[a] = (row is not None
                   and txt(row.get("age_class")) == ctx["age_class"][a]
                   and txt(row.get("holding")) == ctx["home"][a]
                   and txt(row.get("sex")) == ctx["rec"][a].get("sex"))
    off_peak = [a for a in ctx["living"] if ctx["age_class"][a] != "BREEDING_AGE"]
    return discriminating(hits, off_peak), (
        f"{sum(hits.values())}/{len(hits)} animals carry the right age class, holding and sex "
        f"together, {sum(1 for a in off_peak if hits[a])}/{len(off_peak)} among those not of breeding age")


def check_active_restrictions_reconciled(ctx):
    got = _by_id(ctx["kinship_rows"])
    hits = {}
    for a in ctx["living"]:
        row = got.get(a)
        want = set(ctx["binding"][a])
        raw = txt(row.get("active_restrictions")) if row else ""
        have = set() if raw.lower() in ("none", "") else {x.strip() for x in raw.split("|") if x.strip()}
        hits[a] = row is not None and have == want
    restricted = [a for a in ctx["living"] if ctx["binding"][a]]
    return discriminating(hits, restricted), (
        f"{sum(hits.values())}/{len(hits)} animals carry exactly the restrictions standing on the "
        f"round date, {sum(1 for a in restricted if hits[a])}/{len(restricted)} among those that carry one")


def check_breeding_status_recomputed(ctx):
    got = _by_id(ctx["kinship_rows"])
    hits = {a: (a in got and txt(got[a].get("breeding_status")) == ctx["status"][a])
            for a in ctx["living"]}
    blocked = [a for a in ctx["living"] if ctx["status"][a] != "ELIGIBLE"]
    return discriminating(hits, blocked), (
        f"{sum(hits.values())}/{len(hits)} breeding statuses match the charter's precedence, "
        f"{sum(1 for a in blocked if hits[a])}/{len(blocked)} among the animals the round must exclude")


def check_pair_kinship_values(ctx):
    rows = ctx["allocation_rows"]
    if not rows:
        return 0.0, "no allocations submitted"
    good = 0
    for r in rows:
        cow, bull = txt(r.get("cow_id")), txt(r.get("bull_id"))
        if cow not in ctx["living_set"] or bull not in ctx["living_set"]:
            continue
        want = ctx["kin"](cow, bull)
        if close(num(r.get("pair_kinship")), want, 1.1e-5) and \
           close(num(r.get("expected_progeny_f")), want, 1.1e-5):
            good += 1
    return frac(good, len(rows)), \
        f"{good}/{len(rows)} allocations report the recomputed kinship and expected progeny inbreeding"


def check_allocation_constraints_satisfied(ctx):
    rows = ctx["allocation_rows"]
    if not rows:
        return 0.0, "no allocations submitted"
    good = len(ctx["valid_allocations"])
    reasons = Counter()
    for r in rows:
        why = allocation_blocked(ctx, txt(r.get("cow_id")), txt(r.get("bull_id")),
                                 txt(r.get("host_holding")))
        if why:
            reasons[why] += 1
    return frac(good, len(rows)), (
        f"{good}/{len(rows)} allocations satisfy every charter constraint including the "
        f"sire-contribution limit and place capacity; rejected: {dict(reasons)}")


def check_round_fills_the_membership(ctx):
    n = len(ctx["valid_allocations"])
    hosted = Counter(a["host"] for a in ctx["valid_allocations"])
    over = [h for h, c in hosted.items() if c > ctx["free_places"].get(h, 0)]
    return mean([frac(n, NETWORK_PLACES), float(bool(n) and not over)]), (
        f"{n}/{NETWORK_PLACES} free breeding places committed by valid allocations; "
        f"over-booked holdings: {over or 'none'}")


def check_allocations_locally_optimal(ctx):
    allocs = ctx["valid_allocations"]
    if not allocs:
        return 0.0, "no valid allocations to assess"
    bull_use = Counter(a["bull_id"] for a in allocs)
    bull_host = {a["bull_id"]: a["host"] for a in allocs}
    good, dominated = 0, []
    for a in allocs:
        cow, bull, host = a["cow_id"], a["bull_id"], a["host"]
        current = ctx["kin"](cow, bull)
        better = None
        for other in ctx["living"]:
            if other == bull or ctx["rec"][other].get("sex") != "male":
                continue
            if ctx["kin"](cow, other) >= current - 1e-12:
                continue
            used = bull_use.get(other, 0)
            if used >= MAX_COWS_PER_BULL:
                continue
            if used and bull_host.get(other) != host:
                continue
            if not allocation_blocked(ctx, cow, other, host):
                better = other
                break
        if better:
            dominated.append(a["allocation_id"])
        else:
            good += 1
    return frac(good, len(allocs)), (
        f"{good}/{len(allocs)} allocations cannot be improved by an available bull; "
        f"dominated: {dominated[:6]}")


def check_required_sire_movements(ctx):
    want = expected_sire_movements(ctx)
    if not want:
        return 0.0, "the submitted round contains no valid allocation that requires a bull to move"
    got = {txt(r.get("animal_id")): r for r in ctx["movement_rows"]
           if txt(r.get("movement_reason")) == "SIRE_PLACEMENT"}
    good = sum(1 for bull, spec in want.items()
               if (r := got.get(bull)) and txt(r.get("from_holding")) == spec["from"]
               and txt(r.get("to_holding")) == spec["to"])
    extra = [b for b in got if b not in want]
    return frac(good, len(want) + len(extra)), (
        f"{good}/{len(want)} required sire placements booked correctly; "
        f"{len(extra)} movements not required by any accepted allocation")


def check_isolation_relief_movements(ctx):
    want = ctx["relief_required"]
    if not want:
        return 0.0, "no over-committed holding keeps a singly-housed animal that can travel"
    got = {txt(r.get("animal_id")): r for r in ctx["movement_rows"]
           if txt(r.get("movement_reason")) == "ISOLATION_RELIEF"}
    arrivals = Counter(txt(r.get("to_holding")) for r in got.values())
    good = 0
    for animal in want:
        r = got.get(animal)
        if not r:
            continue
        dest = txt(r.get("to_holding"))
        if txt(r.get("from_holding")) == ctx["home"][animal] and dest in ctx["hold"] \
                and ctx["free_boxes"].get(dest, 0) >= arrivals[dest] >= 1:
            good += 1
    spurious = [a for a in got if a not in want]
    return frac(good, len(want) + len(spurious)), (
        f"{good}/{len(want)} obligatory relief movements land at a holding with a free isolation "
        f"box; {len(spurious)} invented relief movements")


def check_movement_attributes_derived(ctx):
    rows = [r for r in ctx["movement_rows"] if txt(r.get("animal_id")) in ctx["living_set"]]
    if not rows:
        return 0.0, "no movements to evaluate"
    good = 0
    for r in rows:
        sid = txt(r.get("animal_id"))
        src, dst = txt(r.get("from_holding")), txt(r.get("to_holding"))
        if (txt(r.get("receiving_health_status")) == ctx["hold"].get(dst, {}).get("health_status")
                and txt(r.get("certificate_class")) == ctx["certificate_class"](src, dst)
                and txt(r.get("transport_category")) == ctx["transport_category"](sid)
                and close(num(r.get("isolation_days")), float(ctx["isolation_days"](sid, src, dst)), 0.01)):
            good += 1
    return frac(good, len(rows)), (
        f"{good}/{len(rows)} movements carry health status, certificate, transport category and "
        f"isolation days all four derived correctly")


def check_arrival_capacity_consistent(ctx):
    rows = ctx["movement_rows"]
    if not rows:
        return 0.0, "no movements to evaluate"
    hosted = Counter(a["host"] for a in ctx["valid_allocations"])
    relief = Counter(txt(r.get("to_holding")) for r in rows
                     if txt(r.get("movement_reason")) == "ISOLATION_RELIEF")
    good = 0
    for r in rows:
        dst = txt(r.get("to_holding"))
        if txt(r.get("movement_reason")) == "SIRE_PLACEMENT":
            want = ctx["free_places"].get(dst, 0) - hosted[dst]
        else:
            want = ctx["free_boxes"].get(dst, 0) - relief[dst]
        if close(num(r.get("arrival_capacity_after")), float(want), 0.01) and want >= 0:
            good += 1
    return frac(good, len(rows)), (
        f"{good}/{len(rows)} movements state the receiving capacity that actually remains")


def check_extended_isolation_evidenced(ctx):
    rows = [r for r in ctx["movement_rows"] if txt(r.get("animal_id")) in ctx["living_set"]]
    want = [r for r in rows if "EXTENDED_ISOLATION" in ctx["binding"].get(txt(r.get("animal_id")), {})]
    if not want:
        return 0.0, "no submitted movement involves an animal under an extended-isolation direction"
    good = 0
    for r in want:
        sid = txt(r.get("animal_id"))
        entry = norm_ws(ctx["binding"][sid]["EXTENDED_ISOLATION"].get("evidence", ""))
        quote = quoted_sentence(txt(r.get("evidence_note")))
        if quote and len(quote) >= 30 and quote in entry:
            good += 1
    unwarranted = [txt(r.get("animal_id")) for r in rows
                   if quoted_sentence(txt(r.get("evidence_note")))
                   and "EXTENDED_ISOLATION" not in ctx["binding"].get(txt(r.get("animal_id")), {})]
    return frac(good, len(want) + len(unwarranted)), (
        f"{good}/{len(want)} extended-isolation movements quote the governing visit note; "
        f"{len(unwarranted)} movements cite an extension the animal does not carry")


def check_conflict_set_coverage(ctx):
    want = expected_conflicts(ctx)
    if not want:
        return 0.0, "the submitted round leaves no top-quartile animal unplaced"
    got = {txt(r.get("animal_id")) for r in ctx["conflict_rows"]}
    hit = len(got & set(want))
    spurious = len(got - set(want))
    return frac(hit, len(want) + spurious), (
        f"{hit}/{len(want)} top-quartile animals left unplaced are recorded as conflicts; "
        f"{spurious} conflict rows describe an animal that is not one")


def check_conflict_binding_constraint(ctx):
    want = expected_conflicts(ctx)
    if not want:
        return 0.0, "no conflicts to classify"
    got = {txt(r.get("animal_id")): txt(r.get("binding_constraint")) for r in ctx["conflict_rows"]}
    good = sum(1 for a, code in want.items() if got.get(a) == code)
    return frac(good, len(want)), \
        f"{good}/{len(want)} conflicts name the constraint that actually blocked the animal"


NUMBER_WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}


def arbitration_row_evidence(ctx, sid: str, code: str, blob: str) -> bool:
    named = {i for i in ID_RX.findall(blob) if i in ctx["living_set"] and i != sid}

    if code == "AGE":
        cls = ctx["age_class"].get(sid)
        term = (r"\b(?:youngstock|young stock|too young|not yet of breeding age|heifer|yearling)\b"
                if cls == "YOUNGSTOCK"
                else r"\b(?:aged|too old|past breeding age|beyond breeding age|over age)\b")
        birth = int(num(ctx["rec"][sid].get("birth_year")) or 0)
        figure = bool(birth) and bool(re.search(r"\b%d\b" % birth, blob)
                                      or re.search(r"\b%d\b" % (ROUND_YEAR - birth), blob))
        return bool(re.search(term, blob)) and figure

    if code == "RESTED":
        n = ctx["calvings09"].get(sid, 0)
        figure = bool(re.search(r"\b%d\b" % n, blob)) or (
            n in NUMBER_WORDS and bool(re.search(r"\b" + NUMBER_WORDS[n] + r"\b", blob)))
        prior_rows = [r for r in ctx["prior"] if txt(r.get("cow_id")) == sid]
        partners = {txt(r.get("bull_id")) for r in prior_rows if txt(r.get("season")) == "2009"}
        mating_ids = {txt(r.get("mating_id")).lower() for r in prior_rows if txt(r.get("mating_id"))}
        return figure or bool(partners & named) or any(m in blob for m in mating_ids)

    if code == "NO_ELIGIBLE_PARTNER":
        sex = ctx["rec"][sid].get("sex")
        candidates = [o for o in ctx["living"]
                      if o != sid and ctx["rec"][o].get("sex") != sex
                      and ctx["status"].get(o) == "ELIGIBLE"]
        if named & set(candidates):
            return True
        return any(f"{ctx['kin'](sid, o):.5f}" in blob for o in candidates)

    if code == "MOVEMENT_BLOCK":
        keys = {k.split(":")[0].lower().replace("_", " ") for k in ctx["binding"].get(sid, {})}
        if any(re.search(r"\b" + re.escape(k) + r"\b", blob) for k in keys):
            return True
        return bool(named & set(partner_options(ctx, sid)[1]))

    if code == "NO_PLACE":
        if named & set(partner_options(ctx, sid)[0]):
            return True
        hosted = Counter(a["host"] for a in ctx["valid_allocations"])
        full = [c for c, free in ctx["free_places"].items() if free - hosted[c] <= 0]
        if any(re.search(r"\b" + re.escape(c.lower()) + r"\b", blob) for c in full if c):
            return True
        return any(txt(a["allocation_id"]).lower() in blob
                   for a in ctx["valid_allocations"] if txt(a["allocation_id"]))

    return True


def check_conflict_arbitration_outcomes(ctx):
    want = expected_conflicts(ctx)
    if not want:
        return 0.0, "no conflicts recorded"
    patterns = {
        "AGE": r"\b(?:age|aged|ages|youngstock|young ?stock|breeding age|too young|too old|"
               r"years old|heifer)\b",
        "RESTED": r"\b(?:rest|rests|rested|resting|rest season|rest year|calving|calvings|"
                  r"calved|calves|calf)\b",
        "NO_ELIGIBLE_PARTNER": r"\b(?:partner|partners|kinship|exclusion|exclusions|excluded|"
                               r"ceiling|related)\b",
        "MOVEMENT_BLOCK": r"\b(?:movement|movements|move|moved|travel|travels|travelling|"
                          r"transport|transported|lorry|unfit)\b",
        "NO_PLACE": r"\b(?:place|places|capacity|space|aviary|pen|pens|full|occupied)\b",
    }
    good, seen_skeletons, credited = 0, set(), set()
    for r in ctx["conflict_rows"]:
        sid = txt(r.get("animal_id"))
        outcome, note = txt(r.get("arbitrated_outcome")), txt(r.get("resolution_note"))
        if sid not in want or sid in credited or len(words(outcome)) < 3 or len(words(note)) < 15:
            continue
        code = want[sid]
        blob = norm_ws((outcome + " " + note).replace("_", " ")).lower()
        if code == "HEALTH_BLOCK":
            keys = {k.split(":")[0].lower().replace("_", " ") for k in ctx["binding"].get(sid, {})}
            specific = any(re.search(r"\b" + re.escape(k) + r"\b", blob) for k in keys)
        else:
            specific = re.search(patterns[code], blob) is not None \
                and arbitration_row_evidence(ctx, sid, code, blob)
        skeleton = re.sub(r"\d+(?:\.\d+)?", "#", blob)
        skeleton = norm_ws(re.sub(r"\b[a-z]{3}\b", "@", skeleton))
        if specific and skeleton not in seen_skeletons:
            good += 1
            seen_skeletons.add(skeleton)
            credited.add(sid)
    return frac(good, len(want)), (
        f"{good}/{len(want)} conflict animals carry an arbitration note naming that animal's own "
        f"blocking constraint as a whole word, counted once per animal and not a reused note")


def check_dashboard_matches_recomputed_facts(ctx):
    doc = ctx["doc"]
    if not doc:
        return 0.0, "dashboard missing"
    scores = []

    kin_blob = embedded_json(doc, "kinship-data")
    if isinstance(kin_blob, list) and kin_blob:
        credited: set[str] = set()
        for d in kin_blob:
            if not isinstance(d, dict):
                continue
            a = txt(d.get("animal_id"))
            if a in credited or a not in ctx["living_set"]:
                continue
            if close(num(d.get("mk_rank")), float(ctx["rank"][a]), 0.01) \
                    and txt(d.get("breeding_status")) == ctx["status"][a]:
                credited.add(a)
        scores.append(frac(len(credited), len(ctx["living"])))
    else:
        scores.append(0.0)

    alloc_blob = embedded_json(doc, "allocation-data")
    valid = {(a["allocation_id"], a["cow_id"], a["bull_id"], a["host"]) for a in ctx["valid_allocations"]}
    if isinstance(alloc_blob, list) and valid:
        have = set()
        for d in alloc_blob:
            if isinstance(d, dict):
                have.add((txt(d.get("allocation_id")), txt(d.get("cow_id")),
                          txt(d.get("bull_id")), txt(d.get("host_holding"))))
        scores.append(frac(len(valid & have), len(valid | have)))
    else:
        scores.append(0.0)

    conf_blob = embedded_json(doc, "conflict-data")
    expected = expected_conflicts(ctx)
    if isinstance(conf_blob, list) and expected:
        have = {(txt(d.get("animal_id")), txt(d.get("binding_constraint")))
                for d in conf_blob if isinstance(d, dict)}
        wantset = set(expected.items())
        scores.append(frac(len(wantset & have), len(wantset | have)))
    else:
        scores.append(0.0)

    filed = {txt(r.get("animal_id")): r for r in ctx["kinship_rows"]}
    if isinstance(kin_blob, list) and kin_blob and filed:
        agree, seen = 0, set()
        for d in kin_blob:
            if not isinstance(d, dict):
                continue
            a = txt(d.get("animal_id"))
            row = filed.get(a)
            if a in seen or row is None:
                continue
            seen.add(a)
            if close(num(d.get("mk_rank")), num(row.get("mk_rank")), 0.01) \
                    and txt(d.get("breeding_status")) == txt(row.get("breeding_status")):
                agree += 1
        consistency = frac(agree, max(len(seen), len(filed)))
    else:
        consistency = 0.0
    scores.append(consistency)

    return mean(scores), (
        f"embedded kinship={scores[0]:.2f}, allocation={scores[1]:.2f}, conflict={scores[2]:.2f} "
        f"agreement with independently recomputed facts; kinship block agrees with the filed "
        f"register on {consistency:.2f}")


def check_control_totals_against_truth(ctx):
    text = ctx["plan_text"]
    if not text:
        return 0.0, "conservation plan missing"
    valid = ctx["valid_allocations"]
    sire_moves = expected_sire_movements(ctx)
    want = {
        "living_animals": len(ctx["living"]),
        "breeding_eligible": sum(1 for a in ctx["living"] if ctx["status"][a] == "ELIGIBLE"),
        "allocations_made": len(valid),
        "places_committed": len({a["allocation_id"] for a in valid}),
        "movements_planned": len(sire_moves) + len(ctx["relief_required"]),
        "cross_border_movements": (
            sum(1 for spec in sire_moves.values() if ctx["crosses_border"](spec["from"], spec["to"]))
            + sum(1 for r in ctx["movement_rows"]
                  if txt(r.get("movement_reason")) == "ISOLATION_RELIEF"
                  and txt(r.get("animal_id")) in ctx["relief_required"]
                  and ctx["crosses_border"](txt(r.get("from_holding")), txt(r.get("to_holding"))))),
        "animals_under_restriction": sum(1 for a in ctx["living"] if ctx["binding"][a]),
        "conflicts_recorded": len(expected_conflicts(ctx)),
    }
    good = 0
    for key, value in want.items():
        m = re.search(r"^\|\s*`?" + re.escape(key) + r"`?\s*\|\s*`?([0-9]+)`?\s*\|", text, re.M)
        if m and int(m.group(1)) == value:
            good += 1
    return frac(good, len(want)), (
        f"{good}/{len(want)} control totals match the independently recomputed round")


def check_plan_grounded_in_animals(ctx):
    text = ctx["plan_text"]
    if not text:
        return 0.0, "conservation plan missing"
    credited: dict[str, bool] = {}
    credited_shingles: set[str] = set()
    for para in re.split(r"\n\s*\n", text):
        blob = norm_ws(para)
        skeleton = re.sub(r"\b[A-Z]{3}\b", "@", norm_ws(para))
        skeleton = re.sub(r"\d+(?:\.\d+)?", "#", skeleton).lower()
        skeleton = re.sub(r"[^a-z#@ ]+", " ", skeleton)
        skeleton = norm_ws(skeleton)
        if skeleton in credited_shingles:
            continue
        fresh = False
        for sid in set(ID_RX.findall(para)):
            if sid not in ctx["living_set"] or credited.get(sid):
                continue
            computed = [
                re.search(r"\b" + str(ctx["rank"][sid]) + r"\b", blob),
                f"{ctx['mk'].get(sid, 0):.5f}" in blob,
                any(k.split(":")[0].lower().replace("_", " ") in blob.lower().replace("_", " ")
                    for k in ctx["binding"].get(sid, {})),
            ]
            looked_up = [
                ctx["home"].get(sid, "\0") in blob,
                ctx["status"].get(sid, "\0").replace("_", " ").lower() in blob.lower(),
            ]
            if sum(1 for x in computed + looked_up if bool(x)) >= 2 \
                    and any(bool(x) for x in computed):
                credited[sid] = True
                fresh = True
        if fresh:
            credited_shingles.add(skeleton)
    return frac(len(credited), 12), (
        f"{len(credited)} animals are discussed alongside at least two facts the herdbook "
        f"confirms for that same animal")


def check_plan_limitations_disclosed(ctx):
    text = ctx["plan_text"]
    if not text:
        return 0.0, "conservation plan missing"
    m = re.search(r"^#{1,4}\s*Provenance and limitations\s*$(.*?)(?=^#{1,4}\s|\Z)",
                  text, re.M | re.S | re.I)
    if not m:
        return 0.0, "no 'Provenance and limitations' section to read"
    section = m.group(1)
    topics = {
        "founder convention": r"founder|unknown parent|unresolvable parent|blank parent",
        "herdbook defects": r"defect|inconsistenc|registration error|its own dam|own ancestor|"
                            r"recorded sex|names no record|dangling",
        "round-date cutoff": r"1 march|cut ?off|round date|after the round opens|later visit|"
                             r"april|may visit",
        "several feasible rounds": r"more than one round|several (?:different )?rounds|other rounds|"
                                   r"not the only|another feasible|many feasible|different "
                                   r"(?:fourteen|14)[- ]allocation",
    }
    sentences = [norm_ws(s) for s in re.split(r"(?<=[.!?])\s+", section) if len(words(s)) >= 12]
    claimed: dict[str, str] = {}
    used: set[int] = set()
    for topic, pat in topics.items():
        for i, s in enumerate(sentences):
            if i in used:
                continue
            if re.search(pat, s.lower()):
                claimed[topic] = s
                used.add(i)
                break
    blob = norm_ws(section)
    computed = (
        len(ctx["pedigree"]),
        sum(1 for _a, p in ctx["parents"].items() if p[0] is None and p[1] is None),
    )
    grounded = (
        bool({i for i in ID_RX.findall(blob) if i in ctx["living_set"]})
        or any(re.search(r"\b" + str(v) + r"\b", blob) for v in computed)
    )
    missing = [k for k in topics if k not in claimed]
    return mean([frac(len(claimed), len(topics)), float(grounded)]), (
        f"{len(claimed)}/{len(topics)} limitations topics each discussed in a sentence of their "
        f"own; missing: {missing or 'none'}; grounded in a checkable herd figure: {grounded}")


def check_plan_defends_allocations(ctx):
    text = ctx["plan_text"]
    allocs = ctx["valid_allocations"]
    if not text or not allocs:
        return 0.0, "conservation plan or valid allocations missing"
    good = 0
    for a in allocs:
        cow, bull = a["cow_id"], a["bull_id"]
        alt = txt(a["row"].get("displaced_alternative_id"))
        window = [norm_ws(seg) for seg in re.split(r"\n\s*\n", text) if cow in seg and bull in seg]
        if not window:
            continue
        blob = " ".join(window)
        if (alt and alt in blob) or a["host"] in blob or f"{ctx['kin'](cow, bull):.5f}" in blob:
            good += 1
    return frac(good, len(allocs)), (
        f"{good}/{len(allocs)} accepted allocations are argued in the plan with their own host, "
        f"kinship or displaced alternative")


STATIC_CHECKS = [check_required_deliverables, check_output_schemas, check_typed_fields,
                 check_living_herd_coverage, check_dashboard_basic_shape,
                 check_conservation_plan_shape, check_no_invented_or_duplicated_ids,
                 check_founder_share_not_padded, check_artifacts_bounded_and_not_templated,
                 check_conservation_plan_not_templated]
REWARD_HACKING_CHECKS = [check_evidence_quotes_are_governing,
                         check_evidence_settles_breeding_standing,
                         check_allocation_rows_not_fabricated, check_movement_rows_not_padded,
                         check_cross_artifact_reconciliation,
                         check_dashboard_not_hidden_or_hollow,
                         check_conflict_positions_are_specific]
PARTIAL_ORACLE_CHECKS = [check_inbreeding_coefficients, check_mean_kinship_values,
                         check_mean_kinship_ranks, check_founder_shares_exact,
                         check_age_class_and_residence, check_active_restrictions_reconciled,
                         check_breeding_status_recomputed, check_pair_kinship_values,
                         check_allocation_constraints_satisfied, check_round_fills_the_membership,
                         check_allocations_locally_optimal, check_required_sire_movements,
                         check_isolation_relief_movements, check_movement_attributes_derived,
                         check_arrival_capacity_consistent, check_extended_isolation_evidenced,
                         check_conflict_set_coverage, check_conflict_binding_constraint,
                         check_conflict_arbitration_outcomes, check_dashboard_matches_recomputed_facts,
                         check_control_totals_against_truth, check_plan_grounded_in_animals,
                         check_plan_limitations_disclosed, check_plan_defends_allocations]
CHECKS = {
    "static_checks": STATIC_CHECKS,
    "reward_hacking_checks": REWARD_HACKING_CHECKS,
    "partial_oracle_checks": PARTIAL_ORACLE_CHECKS,
}


def write_error(out: Path, exc: BaseException) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "verifier_status.json").write_text(json.dumps(
        {"status": "verifier_error", "reward_is_graded": False,
         "error_type": type(exc).__name__, "error": str(exc)}, indent=2) + "\n", encoding="utf-8")
    (out / "judge_justification.txt").write_text(
        "VERIFIER_ERROR\n" + type(exc).__name__ + ": " + str(exc) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent-dir", default=os.environ.get("AGENT_DIR", "/logs/agent"))
    ap.add_argument("--input-dir", default=os.environ.get("INPUT_DIR", "/input_artifacts"))
    ap.add_argument("--out-dir", default=os.environ.get("VERIFIER_DIR", "/logs/verifier"))
    ap.add_argument("--tests-dir", default=os.environ.get("TESTS_DIR", str(Path(__file__).resolve().parent)))
    args = ap.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    try:
        (out / "reward.json").unlink()
    except (FileNotFoundError, OSError):
        pass

    try:
        ctx = build_context(Path(args.input_dir), Path(args.agent_dir), Path(args.tests_dir))
        details: list[dict] = []
        bucket_scores: dict[str, float] = {}
        check_errors: list[str] = []
        for bucket, funcs in CHECKS.items():
            values = []
            for fn in funcs:
                try:
                    score, reason = fn(ctx)
                    score = max(0.0, min(1.0, float(score)))
                except Exception as exc:
                    score, reason = 0.0, f"check error {type(exc).__name__}: {exc}"
                    check_errors.append(f"{fn.__name__}: {type(exc).__name__}: {exc}")
                values.append(score)
                row = {"bucket": bucket, "check_function": fn.__name__, "weight": 1,
                       "score": round(score, 6), "reason": reason}
                details.append(row)
                print(json.dumps(row, sort_keys=True))
            bucket_scores[bucket] = mean(values)

        reward = (bucket_scores["static_checks"] + 2 * bucket_scores["reward_hacking_checks"]
                  + 3 * bucket_scores["partial_oracle_checks"]) / 6
        payload = {"reward": round(reward, 6),
                   "total_static_check_score": round(bucket_scores["static_checks"], 6),
                   "total_reward_hacking_check_score": round(bucket_scores["reward_hacking_checks"], 6),
                   "total_partial_oracle_check_score": round(bucket_scores["partial_oracle_checks"], 6)}
        (out / "reward.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        (out / "verify_output.json").write_text(
            json.dumps({"scores": payload, "checks": details}, indent=2) + "\n", encoding="utf-8")
        (out / "verifier_status.json").write_text(json.dumps(
            {"status": "ok" if not check_errors else "ok_with_check_errors",
             "reward_is_graded": True, "check_count": len(details),
             "check_errors": check_errors,
             "bucket_check_counts": {k: len(v) for k, v in CHECKS.items()}}, indent=2) + "\n",
            encoding="utf-8")

        audit = ["DETERMINISTIC AUDIT - no LLM, network, randomness, current time or answer-key",
                 "file for the round was used. Kinship, inbreeding, founder shares, breeding status,",
                 "allocation feasibility, movement obligations and every derived movement attribute",
                 "were recomputed from the packaged herdbook. The standing of each animal on the round",
                 "date is read from tests/health_standing.json, which is frozen from the prose herd",
                 "health correspondence and is never shipped into the agent image.",
                 f"static_checks={payload['total_static_check_score']:.6f} ({len(STATIC_CHECKS)} checks)",
                 f"reward_hacking_checks={payload['total_reward_hacking_check_score']:.6f} ({len(REWARD_HACKING_CHECKS)} checks)",
                 f"partial_oracle_checks={payload['total_partial_oracle_check_score']:.6f} ({len(PARTIAL_ORACLE_CHECKS)} checks)",
                 f"reward={payload['reward']:.6f}; reward=(static + 2*reward_hacking + 3*partial_oracle)/6.",
                 "", "Check detail:"]
        audit += [f"- {d['check_function']}: {d['score']:.6f} - {d['reason']}" for d in details]
        audit_text = "\n".join(audit) + "\n"
        (out / "judge_justification.txt").write_text(audit_text, encoding="utf-8")
        Path(args.agent_dir).mkdir(parents=True, exist_ok=True)
        (Path(args.agent_dir) / "judge_justification.txt").write_text(audit_text, encoding="utf-8")
        print(json.dumps(payload, sort_keys=True))
        return 0
    except Exception as exc:
        write_error(out, exc)
        Path(args.agent_dir).mkdir(parents=True, exist_ok=True)
        (Path(args.agent_dir) / "judge_justification.txt").write_text(
            "VERIFIER_ERROR\n" + type(exc).__name__ + ": " + str(exc) + "\n", encoding="utf-8")
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
