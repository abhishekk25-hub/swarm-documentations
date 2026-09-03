from __future__ import annotations

import argparse
import csv
import datetime
import itertools
import json
import math
import os
import re
import sys
import traceback
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

DOCKET_DATE = "2026-04-06"
PROGRAMME_WEEKS = 8
ENGINEER_WEEK_BUDGET = 20
CRAWL_MARGIN = 1.20
MAX_DETOUR_KM = 25
MIN_DETOUR_KM = 1
DERATE_TABLE = ((7, 1.00), (6, 0.90), (5, 0.75), (0, 0.60))
DESIGN_CEILING = {"4": 55.0, "5": 72.5, "6": 80.0, "9": 90.0, "A": 100.0}
MATERIAL_CLASS = {"1": "CONCRETE", "2": "CONCRETE", "5": "CONCRETE", "6": "CONCRETE",
                  "3": "STEEL", "4": "STEEL", "7": "TIMBER"}
CLASS_BASE_WEEKS = {"CONCRETE": 2, "STEEL": 3, "TIMBER": 2, "OTHER": 3}
WEIGHT_BANDS = [("<=45.0", 45.0), ("45.1-60.0", 60.0), ("60.1-80.0", 80.0),
                ("80.1-110.0", 110.0), (">110.0", 999.9)]
BAND_RANGE = {"<=45.0": (0.0, 45.0), "45.1-60.0": (45.1, 60.0), "60.1-80.0": (60.1, 80.0),
              "80.1-110.0": (80.1, 110.0), ">110.0": (110.1, 1e9)}
DECISIONS = ("ISSUE", "ISSUE_WITH_CONDITIONS", "REROUTE_LOAD", "REROUTE_CLEARANCE",
             "REFUSE", "WITHDRAWN")
LADDER_DECISIONS = tuple(d for d in DECISIONS if d != "WITHDRAWN")
NOT_ISSUED = ("REROUTE_CLEARANCE", "REROUTE_LOAD", "REFUSE")
CONDITION_CODES = ("CENTERLINE_CROSSING", "CRAWL_8KMH", "LANE_CLOSURE", "NIGHT_MOVE",
                   "NO_MEET", "POLICE_ESCORT")
REASON_CODES = ("HEIGHT_CLEARANCE", "CAPACITY_BYPASS_AVAILABLE", "CAPACITY_NO_BYPASS",
                "CAPACITY_BYPASS_TOO_LONG")
ESCORT_CLASSES = ("NONE", "SINGLE", "DOUBLE")
MATERIAL_CLASSES = ("CONCRETE", "STEEL", "TIMBER", "OTHER")
CONDITION_TRENDS = ("DETERIORATED", "IMPROVED", "STABLE")

CHART_VIEWBOX = "0 0 1200 780"
CHART_X0, CHART_PX_PER_KM = 80.0, 20.0
CHART_LANE_Y0, CHART_LANE_H, CHART_BAR_W = 170.0, 110.0, 6.0

REGISTER_COLS = ["structure_number", "corridor_id", "kilometerpoint", "route_label", "county",
                 "facility_carried", "features_intersected", "year_built", "design_load_code",
                 "operating_rating_t", "inventory_rating_t", "governing_condition_rating",
                 "condition_derate_factor", "posting_status", "standing_restriction_t",
                 "governing_memo_id", "effective_capacity_t", "width_limit_m", "height_limit_m",
                 "bypass_detour_km", "material_class", "rerate_eligible", "rerated_capacity_t",
                 "rerate_engineer_weeks", "condition_trend"]
DISPOSITION_KEYS = ["application_id", "applicant", "gross_weight_t", "structures_crossed",
                    "controlling_structure", "controlling_headroom_t", "decision",
                    "condition_codes", "escort_class", "blocking_structures", "detour_km",
                    "refusal_reason_code", "governing_memo_ids"]
SUMMARY_KEYS = ["application_count", "issued_count", "issued_with_conditions_count",
                "reroute_load_count", "reroute_clearance_count", "refused_count",
                "withdrawn_count", "structures_assessed", "structures_with_standing_restriction",
                "distinct_controlling_structures", "total_detour_km",
                "relieved_application_count"]
PROGRAMME_COLS = ["structure_number", "corridor_id", "material_class", "engineer_id",
                  "week_index", "engineer_weeks", "capacity_before_t", "capacity_after_t",
                  "applications_relieved", "relieved_application_ids"]
LEDGER_COLS = ["corridor_id", "weight_band", "band_ceiling_t", "structures_below_ceiling",
               "lowest_effective_capacity_t", "bottleneck_structure", "applications_in_band",
               "applications_blocked_on_corridor", "detour_available"]
REFUSAL_COLS = ["application_id", "decision", "refusal_reason_code", "blocking_structures",
                "shortfall_t", "detour_km", "rerate_would_relieve", "earliest_relief_week",
                "supporting_memo_ids"]

ARTIFACTS = {
    "register": "structure_capacity_register.csv",
    "dispositions": "permit_dispositions.json",
    "programme": "rerating_programme.csv",
    "ledger": "corridor_bottleneck_ledger.tsv",
    "refusals": "refusal_register.csv",
    "chart": "capacity_profile.svg",
    "letter": "permit_decision_letter.md",
}
MAX_ARTIFACT_BYTES = 3 * 1024 * 1024

NUMBER_WORDS = {
    "twenty-two": 22, "twenty-four": 24, "twenty-six": 26, "twenty-eight": 28, "thirty": 30,
    "thirty-two": 32, "thirty-four": 34, "thirty-six": 36, "thirty-eight": 38, "forty": 40,
    "forty-two": 42, "forty-four": 44, "forty-six": 46, "forty-eight": 48, "fifty": 50,
    "fifty-two": 52, "fifty-four": 54, "fifty-six": 56, "fifty-eight": 58, "sixty": 60,
}
MONTH_NAMES = {}
for _i, _m in enumerate(["January", "February", "March", "April", "May", "June", "July",
                         "August", "September", "October", "November", "December"], 1):
    MONTH_NAMES[_m.lower()] = _i
    MONTH_NAMES[_m.lower()[:3]] = _i

TONNAGE_RE = re.compile(
    r"(?:(\d+(?:\.\d+)?)|(" + "|".join(sorted(NUMBER_WORDS, key=len, reverse=True)) +
    r"))\s*(?:tonnes|tonne|t)\b", re.I)
REVISION_RE = re.compile(r"revised to\s*", re.I)
DATE_RE = re.compile(
    r"\b(\d{4}-\d{2}-\d{2}|\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4}|\d{1,2}/\d{1,2}/\d{4})\b")

CUE_ANOTHER = re.compile(
    r"attach\w*\s+to|belong\w*\s+to|cross-?referen\w*|for the record|for information|"
    r"never applied to this structure|not to this structure", re.I)
CUE_RESCIND = re.compile(
    r"rescind\w*|\blift(?:ed|s|ing)?\b|withdraw\w*|withdrawn|\bremov\w*|no longer appl\w*|"
    r"cancel\w*|revok\w*|discharg\w*|stood down|closed out", re.I)
CUE_NOT_IN_FORCE = re.compile(
    r"recommend\w*|propos\w*|not in force|does not bind|withheld|unsigned|not signed|"
    r"await\w*|for (?:consideration|discussion|district)|\bdraft\b|declined to endors\w*|"
    r"no effect|not operative|pending (?:district )?concurrence|pending sign\w*", re.I)
CUE_CONCUR = re.compile(
    r"concur\w*|counter-?sign\w*|sign(?:ed|s|ature|-off)\b|signed off|endors\w*|"
    r"district approval|approved at district|put her signature|put his signature", re.I)
CUE_REVIEW = re.compile(
    r"review|revisit\w*|runs to|until|valid to|in force to|expir\w*|before|diaris\w*", re.I)


FUNCTION_WORDS = frozenset("""a an and the of to in on at by for with from is are was were be been
being it its this that these those as or but not no nor so than then there here which who whom
whose what when where while any all each every both few more most other some such only own same
over under after before during against between into through above below up down out off again
further once he she they we you i him her them us my your their our has have had do does did will
would shall should can could may might must about across""".split())


def content_shingles(text, n=6):
    words = [w for w in re.findall(r"[a-z0-9]+", (text or "").lower())
             if w not in FUNCTION_WORDS]
    return {" ".join(words[i:i + n]) for i in range(max(0, len(words) - n + 1))}


def fnum(value, default=None):
    if value is None:
        return default
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    text = str(value).strip().replace(",", "")
    if not text:
        return default
    try:
        return float(text)
    except ValueError:
        return default


def close(a, b, tol=0.051):
    if a is None or b is None:
        return False
    return abs(float(a) - float(b)) <= tol


def as_bool(value):
    text = str(value).strip().upper()
    if text in ("TRUE", "T", "YES", "Y", "1"):
        return True
    if text in ("FALSE", "F", "NO", "N", "0"):
        return False
    return None


def as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    text = str(value).strip()
    if not text:
        return []
    if text.startswith("["):
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return [str(x).strip() for x in parsed if str(x).strip()]
        except Exception:
            pass
    parts = re.split(r"[;,]", text)
    return [p.strip() for p in parts if p.strip()]


def mean(values):
    return sum(values) / len(values) if values else 0.0


def frac(hit, total):
    return (hit / total) if total else 0.0


def bounded_frac(hit, total):
    """A ratio that cannot exceed 1 because the numerator is capped by the denominator."""
    return frac(min(hit, total), total) if total else 0.0


def set_f1(truth: set, pred: set) -> float:
    if not truth and not pred:
        return 1.0
    if not truth or not pred:
        return 0.0
    tp = len(truth & pred)
    if tp == 0:
        return 0.0
    precision, recall = tp / len(pred), tp / len(truth)
    return 2 * precision * recall / (precision + recall)


def macro_f1(pairs, labels) -> float:
    scores = []
    for label in labels:
        tp = sum(1 for t, p in pairs if t == label and p == label)
        fp = sum(1 for t, p in pairs if t != label and p == label)
        fn = sum(1 for t, p in pairs if t == label and p != label)
        if tp + fn == 0:
            continue
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn)
        scores.append(2 * precision * recall / (precision + recall) if (precision + recall) else 0.0)
    return mean(scores)


def read_csv_file(path: Path, delimiter=","):
    if not path.exists():
        return [], []
    try:
        with path.open(newline="", encoding="utf-8-sig", errors="replace") as handle:
            reader = csv.DictReader(handle, delimiter=delimiter)
            header = [h.strip() for h in (reader.fieldnames or [])]
            rows = []
            for raw in reader:
                rows.append({(k.strip() if k else k): (v if v is not None else "")
                             for k, v in raw.items()})
            return header, rows
    except Exception:
        return [], []


def ngrams(text: str, n: int):
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {" ".join(words[i:i + n]) for i in range(max(0, len(words) - n + 1))}


def governing_condition(record) -> int:
    digits = [int(record[key]) for key in ("deck_condition", "superstructure_condition",
                                           "substructure_condition", "culvert_condition")
              if str(record.get(key, "")).isdigit()]
    return min(digits) if digits else 5


def derate_factor(condition: int) -> float:
    for threshold, factor in DERATE_TABLE:
        if condition >= threshold:
            return factor
    return 0.60


def material_class_of(record) -> str:
    return MATERIAL_CLASS.get(record.get("structure_type_main_material_code", ""), "OTHER")


def engineer_weeks_for(record) -> int:
    weeks = CLASS_BASE_WEEKS[material_class_of(record)]
    if (record.get("number_of_spans_in_main_unit") or 0) >= 4:
        weeks += 1
    if (record.get("structure_length_m") or 0) >= 100.0:
        weeks += 1
    return weeks


DIGIT_WORDS = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
               "seven": 7, "eight": 8, "nine": 9}
UNIT_WORDS = {"three": 3, "four": 4, "five": 5, "six": 6}
WORD_QUANTITY_RE = re.compile(
    r"\b(three|four|five|six)\s+point\s+(zero|one|two|three|four|five|six|seven|eight|nine)"
    r"\s+(zero|one|two|three|four|five|six|seven|eight|nine)\b", re.I)
PLAIN_QUANTITY_RE = re.compile(r"\d+(?:\.\d+)?")
CORRIDOR_TOKEN_RE = re.compile(r"HC-[0-9A-Z]{3}")

CUE_NO_CHANGE = re.compile(
    r"unchanged from our filing|nothing changes on this|still correct, nothing has moved|"
    r"no change to anything filed", re.I)
CUE_WITHDRAW = re.compile(
    r"withdraw\w*|cancel\w*|pulled the plug|stand this one down|take this off the docket|"
    r"not going ahead", re.I)
CUE_RELATIVE_UP = re.compile(r"\badd\b|goes up by", re.I)
CUE_RELATIVE_DOWN = re.compile(r"\bknock\b|\btake\b", re.I)


def first_quantity(text):
    word = WORD_QUANTITY_RE.search(text)
    plain = PLAIN_QUANTITY_RE.search(text)
    if word and (not plain or word.start() <= plain.start()):
        return float("%d.%d%d" % (UNIT_WORDS[word.group(1).lower()],
                                  DIGIT_WORDS[word.group(2).lower()],
                                  DIGIT_WORDS[word.group(3).lower()]))
    return float(plain.group()) if plain else None


def read_correspondence(text):
    body = " ".join((text or "").split())
    if CUE_NO_CHANGE.search(body):
        return "NONE", None
    if CUE_WITHDRAW.search(body):
        return "WITHDRAW", None

    corridor = CORRIDOR_TOKEN_RE.search(body)
    leg = re.search(r"\bleg\s+(\d)", body, re.I)
    if corridor and leg:
        stripped = CORRIDOR_TOKEN_RE.sub(" ", body)
        stripped = re.sub(r"\bleg\s+\d", " ", stripped, flags=re.I)
        numbers = [float(x) for x in PLAIN_QUANTITY_RE.findall(stripped)]
        if len(numbers) >= 2:
            return "ROUTE", {"index": int(leg.group(1)) - 1, "corridor_id": corridor.group(),
                             "entry_km": numbers[0], "exit_km": numbers[1]}

    low = body.lower()
    if "width" in low or "across the beam" in low:
        field = "overall_width_m"
    elif "height" in low:
        field = "overall_height_m"
    elif "gross" in low:
        field = "gross_weight_t"
    else:
        return "NONE", None
    value = first_quantity(body)
    if value is None:
        return "NONE", None
    if "filed" in low and (CUE_RELATIVE_UP.search(body) or CUE_RELATIVE_DOWN.search(body)):
        sign = -1.0 if CUE_RELATIVE_DOWN.search(body) else 1.0
        return field.upper()[:6], {"field": field, "delta": sign * value}
    return field.upper()[:6], {"field": field, "absolute": value}


def effective_application(app, messages, docket_date):
    record = {"gross_weight_t": app["gross_weight_t"],
              "overall_width_m": app["overall_width_m"],
              "overall_height_m": app["overall_height_m"],
              "legs": [dict(leg) for leg in app["legs"]], "withdrawn": False}
    filed = dict(record)
    for message in sorted(messages, key=lambda m: (m["received_date"], m["correspondence_id"])):
        if message["received_date"] > docket_date:
            continue
        kind, payload = read_correspondence(message["text"])
        if kind == "WITHDRAW":
            record["withdrawn"] = True
        elif kind == "ROUTE" and payload:
            if 0 <= payload["index"] < len(record["legs"]):
                record["legs"][payload["index"]] = {"corridor_id": payload["corridor_id"],
                                                    "entry_km": payload["entry_km"],
                                                    "exit_km": payload["exit_km"]}
        elif payload and "field" in payload:
            field = payload["field"]
            if "absolute" in payload:
                record[field] = round(payload["absolute"], 2)
            else:
                record[field] = round(filed[field] + payload["delta"], 2)
    record["gross_weight_t"] = max(20.0, round(record["gross_weight_t"], 1))
    return record


def parse_memo_date(text: str):
    text = (text or "").strip().rstrip(".,;").strip()
    found = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", text)
    if found:
        return "%s-%s-%s" % found.groups()
    found = re.match(r"^(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})$", text)
    if found and found.group(2).lower() in MONTH_NAMES:
        return "%04d-%02d-%02d" % (int(found.group(3)), MONTH_NAMES[found.group(2).lower()],
                                   int(found.group(1)))
    found = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", text)
    if found:
        return "%04d-%02d-%02d" % (int(found.group(3)), int(found.group(2)), int(found.group(1)))
    return None


def tonnage_at(match) -> float:
    if match.group(1):
        return round(float(match.group(1)), 1)
    return float(NUMBER_WORDS[match.group(2).lower()])


def review_date_in(text: str):
    dates = [(m.start(), m.group(1)) for m in DATE_RE.finditer(text)]
    if not dates:
        return None
    candidates = []
    for cue in CUE_REVIEW.finditer(text):
        for start, raw in dates:
            if 0 <= start - cue.end() <= 45:
                parsed = parse_memo_date(raw)
                if parsed:
                    candidates.append(parsed)
    return max(candidates) if candidates else None


def read_memo(text: str):
    body = " ".join((text or "").split())
    if CUE_ANOTHER.search(body):
        return "NONE", None, None
    if CUE_RESCIND.search(body):
        return "RESCIND", None, None
    if CUE_NOT_IN_FORCE.search(body):
        return "NONE", None, None
    if not CUE_CONCUR.search(body):
        return "NONE", None, None
    revision = REVISION_RE.search(body)
    match = (TONNAGE_RE.search(body, revision.end()) if revision
             else TONNAGE_RE.search(body))
    if not match:
        return "NONE", None, None
    return "IMPOSE", tonnage_at(match), review_date_in(body)


def standing_restrictions(memos):
    by_structure = defaultdict(list)
    for memo in memos:
        by_structure[memo["structure_number"]].append(memo)
    standing = {}
    for structure, filed in by_structure.items():
        filed.sort(key=lambda m: (m["filed_date"], m["memo_id"]))
        current = None
        for memo in filed:
            action, limit, review = read_memo(memo["text"])
            if action == "RESCIND":
                current = None
            elif action == "IMPOSE":
                current = (limit, review, memo["memo_id"])
        if current and current[1] and current[1] >= DOCKET_DATE:
            standing[structure] = (round(current[0], 1), current[2])
    return standing


def condition_trend_of(current, prior):
    if not prior:
        return "STABLE"
    then_items = [int(prior[key]) for key in ("deck_condition", "superstructure_condition",
                                              "substructure_condition", "culvert_condition")
                  if str(prior.get(key, "")).isdigit()]
    then_condition = min(then_items) if then_items else None
    now_condition = governing_condition(current)
    then_rating, now_rating = prior.get("operating_rating_t"), current["operating_rating_t"]
    fell = ((then_condition is not None and now_condition < then_condition)
            or (then_rating and now_rating and now_rating < then_rating - 1e-9))
    rose = ((then_condition is not None and now_condition > then_condition)
            or (then_rating and now_rating and now_rating > then_rating + 1e-9))
    if fell:
        return "DETERIORATED"
    if rose:
        return "IMPROVED"
    return "STABLE"


def capacity_of(record, standing):
    condition = governing_condition(record)
    factor = derate_factor(condition)
    derated = round(record["operating_rating_t"] * factor, 1)
    if record.get("structure_open_posted_closed") == "P":
        derated = min(derated, record["inventory_rating_t"])
    limit = standing[0] if standing else None
    effective = round(derated if limit is None else min(derated, limit), 1)
    ceiling = DESIGN_CEILING.get(record.get("design_load_code", ""))
    rerated, eligible = None, False
    if (ceiling is not None and condition >= 5
            and record.get("structure_open_posted_closed") == "A"):
        candidate = round(min(ceiling, record["operating_rating_t"]), 1)
        if candidate > effective:
            rerated, eligible = candidate, True
    return {
        "governing_condition": condition,
        "derate_factor": factor,
        "derated_capacity_t": round(derated, 1),
        "standing_restriction_t": limit,
        "governing_memo_id": standing[1] if standing else None,
        "effective_capacity_t": effective,
        "width_limit_m": record["total_horizontal_clearance_m"],
        "height_limit_m": record["min_vertical_clearance_over_bridge_roadway_m"],
        "bypass_detour_km": record["bypass_detour_km"],
        "material_class": material_class_of(record),
        "rerate_eligible": eligible,
        "rerated_capacity_t": rerated,
        "rerate_engineer_weeks": engineer_weeks_for(record),
    }


def escort_class_for(gross, width):
    if width > 5.5 or gross > 110.0:
        return "DOUBLE"
    if width > 4.3 or gross > 60.0:
        return "SINGLE"
    return "NONE"


def path_of(app, by_corridor):
    seen, ordered = set(), []
    for leg in app["legs"]:
        low, high = min(leg["entry_km"], leg["exit_km"]), max(leg["entry_km"], leg["exit_km"])
        for record in by_corridor.get(leg["corridor_id"], []):
            if low - 1e-9 <= record["kilometerpoint"] <= high + 1e-9:
                if record["structure_number"] not in seen:
                    seen.add(record["structure_number"])
                    ordered.append(record)
    ordered.sort(key=lambda r: (r["corridor_id"], r["kilometerpoint"], r["structure_number"]))
    return ordered


def dispose(app, path, caps, by_num):
    if app.get("withdrawn"):
        return {"structures_crossed": [r["structure_number"] for r in path],
                "controlling_structure": "", "controlling_headroom_t": 0.0,
                "decision": "WITHDRAWN", "condition_codes": [], "escort_class": "NONE",
                "blocking_structures": [], "detour_km": 0.0, "refusal_reason_code": "",
                "governing_memo_ids": []}
    gross, width, height = app["gross_weight_t"], app["overall_width_m"], app["overall_height_m"]
    height_block = sorted(r["structure_number"] for r in path
                          if caps[r["structure_number"]]["height_limit_m"] < height)
    over_weight = [r["structure_number"] for r in path
                   if gross > caps[r["structure_number"]]["effective_capacity_t"]]
    over_width = [r["structure_number"] for r in path
                  if width > caps[r["structure_number"]]["width_limit_m"]]
    hard = sorted(s for s in over_weight
                  if gross > round(caps[s]["effective_capacity_t"] * CRAWL_MARGIN, 6))

    codes, detour, blocking, reason = [], 0.0, [], ""
    if height_block:
        decision, blocking, reason = "REROUTE_CLEARANCE", height_block, "HEIGHT_CLEARANCE"
    elif not over_weight and not over_width:
        decision = "ISSUE"
    elif not hard:
        decision = "ISSUE_WITH_CONDITIONS"
    else:
        bypasses = [by_num[s]["bypass_detour_km"] or 0 for s in hard]
        if all(MIN_DETOUR_KM <= b <= MAX_DETOUR_KM for b in bypasses):
            decision, blocking = "REROUTE_LOAD", hard
            detour = float(sum(bypasses))
            reason = "CAPACITY_BYPASS_AVAILABLE"
        else:
            decision, blocking = "REFUSE", hard
            reason = ("CAPACITY_NO_BYPASS" if any(b == 0 for b in bypasses)
                      else "CAPACITY_BYPASS_TOO_LONG")

    if decision == "ISSUE_WITH_CONDITIONS":
        if over_weight:
            codes += ["CENTERLINE_CROSSING", "CRAWL_8KMH", "NO_MEET"]
        if over_width:
            codes.append("LANE_CLOSURE")
        if width > 4.9 or "NO_MEET" in codes:
            codes.append("POLICE_ESCORT")
        if path and max((r["average_daily_traffic"] or 0) for r in path) >= 20000:
            codes.append("NIGHT_MOVE")

    controlling, headroom = "", 0.0
    if path:
        best = min(path, key=lambda r: (round(caps[r["structure_number"]]["effective_capacity_t"]
                                              - gross, 6), r["structure_number"]))
        controlling = best["structure_number"]
        headroom = round(caps[controlling]["effective_capacity_t"] - gross, 1)

    memo_ids = sorted({caps[r["structure_number"]]["governing_memo_id"] for r in path
                       if caps[r["structure_number"]]["governing_memo_id"]})
    return {
        "structures_crossed": [r["structure_number"] for r in path],
        "controlling_structure": controlling,
        "controlling_headroom_t": headroom,
        "decision": decision,
        "condition_codes": sorted(set(codes)),
        "escort_class": escort_class_for(gross, width),
        "blocking_structures": blocking,
        "detour_km": round(detour, 1),
        "refusal_reason_code": reason,
        "governing_memo_ids": memo_ids,
    }


def build_truth(input_dir: Path) -> dict:
    extract = json.loads((input_dir / "nbi_structure_extract.json").read_text(encoding="utf-8"))
    structures = extract["structures"]
    by_num = {r["structure_number"]: r for r in structures}
    by_corridor = defaultdict(list)
    for record in structures:
        by_corridor[record["corridor_id"]].append(record)
    for rows in by_corridor.values():
        rows.sort(key=lambda r: (r["kilometerpoint"], r["structure_number"]))

    prior_raw = json.loads((input_dir / "nbi_prior_deliveries.json").read_text(encoding="utf-8"))
    prior = {r["structure_number"]: (r.get("delivery_2022") or {})
             for r in prior_raw["structures"]}
    trends = {r["structure_number"]: condition_trend_of(r, prior.get(r["structure_number"]))
              for r in structures}

    memos = [json.loads(line) for line in
             (input_dir / "field_restriction_memos.jsonl").read_text(encoding="utf-8").splitlines()
             if line.strip()]
    memos_by_structure = defaultdict(list)
    for memo in memos:
        memos_by_structure[memo["structure_number"]].append(memo["memo_id"])

    standing = standing_restrictions(memos)
    caps = {r["structure_number"]: capacity_of(r, standing.get(r["structure_number"]))
            for r in structures}

    apps = []
    with (input_dir / "permit_applications.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            legs = []
            for index in (1, 2, 3):
                corridor = row["leg%d_corridor_id" % index].strip()
                if corridor:
                    legs.append({"corridor_id": corridor,
                                 "entry_km": float(row["leg%d_entry_km" % index]),
                                 "exit_km": float(row["leg%d_exit_km" % index])})
            apps.append({"application_id": row["application_id"], "applicant": row["applicant"],
                         "commodity": row["commodity"],
                         "gross_weight_t": float(row["gross_weight_t"]),
                         "overall_width_m": float(row["overall_width_m"]),
                         "overall_height_m": float(row["overall_height_m"]),
                         "legs": legs})

    correspondence = [json.loads(line) for line in
                      (input_dir / "applicant_correspondence.jsonl").read_text(
                          encoding="utf-8").splitlines() if line.strip()]
    by_application = defaultdict(list)
    for message in correspondence:
        by_application[message["application_id"]].append(message)
    effective = {}
    for app in apps:
        amended = effective_application(app, by_application.get(app["application_id"], []),
                                        DOCKET_DATE)
        merged = dict(app)
        merged["filed_gross_weight_t"] = app["gross_weight_t"]
        merged["filed_overall_width_m"] = app["overall_width_m"]
        merged.update(amended)
        effective[app["application_id"]] = merged
    apps = [effective[a["application_id"]] for a in apps]

    paths, dispositions = {}, {}
    for app in apps:
        path = path_of(app, by_corridor)
        paths[app["application_id"]] = path
        dispositions[app["application_id"]] = dispose(app, path, caps, by_num)

    engineers = {}
    with (input_dir / "rating_engineers.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            engineers[row["engineer_id"]] = {"specialty_class": row["specialty_class"],
                                             "available_weeks": int(row["available_weeks"]),
                                             "home_district": row["home_district"]}

    relief_needs = {}
    for app in apps:
        aid = app["application_id"]
        decided = dispositions[aid]
        if decided["decision"] not in ("REROUTE_LOAD", "REFUSE"):
            continue
        blocking = decided["blocking_structures"]
        if not blocking or not all(caps[s]["rerate_eligible"] for s in blocking):
            continue
        boosted = {k: dict(v) for k, v in caps.items()}
        for structure in blocking:
            boosted[structure]["effective_capacity_t"] = boosted[structure]["rerated_capacity_t"]
        after = dispose(app, paths[aid], boosted, by_num)
        if after["decision"] in ("ISSUE", "ISSUE_WITH_CONDITIONS"):
            relief_needs[aid] = tuple(sorted(blocking))

    candidates = sorted({s for need in relief_needs.values() for s in need})
    weights = {s: caps[s]["rerate_engineer_weeks"] for s in candidates}
    optimum = 0
    for size in range(len(candidates) + 1):
        for combo in itertools.combinations(candidates, size):
            if sum(weights[s] for s in combo) > ENGINEER_WEEK_BUDGET:
                continue
            got = sum(1 for need in relief_needs.values() if set(need) <= set(combo))
            optimum = max(optimum, got)

    ledger = {}
    for corridor, rows in by_corridor.items():
        effs = [caps[r["structure_number"]]["effective_capacity_t"] for r in rows]
        lowest = min(effs)
        bottleneck = min(rows, key=lambda r: (caps[r["structure_number"]]["effective_capacity_t"],
                                              r["structure_number"]))["structure_number"]
        detour = by_num[bottleneck]["bypass_detour_km"] or 0
        for band, ceiling in WEIGHT_BANDS:
            low, high = BAND_RANGE[band]
            in_band, blocked = 0, 0
            for app in apps:
                aid = app["application_id"]
                if not (low - 1e-9 <= app["gross_weight_t"] <= high + 1e-9):
                    continue
                touched = {r["structure_number"] for r in paths[aid]
                           if r["corridor_id"] == corridor}
                if not touched:
                    continue
                in_band += 1
                if touched & set(dispositions[aid]["blocking_structures"]):
                    blocked += 1
            ledger[(corridor, band)] = {
                "band_ceiling_t": ceiling,
                "structures_below_ceiling": sum(1 for e in effs if e < ceiling),
                "lowest_effective_capacity_t": round(lowest, 1),
                "bottleneck_structure": bottleneck,
                "applications_in_band": in_band,
                "applications_blocked_on_corridor": blocked,
                "detour_available": MIN_DETOUR_KM <= detour <= MAX_DETOUR_KM,
            }

    rules_text = (input_dir / "permit_rules.md").read_text(encoding="utf-8")
    memo_text = " ".join(memo["text"] for memo in memos)

    return {"structures": structures, "by_num": by_num, "by_corridor": dict(by_corridor),
            "trends": trends, "correspondence": correspondence,
            "correspondence_by_app": dict(by_application),
            "caps": caps, "standing": standing, "memos": memos,
            "memos_by_structure": dict(memos_by_structure), "apps": apps,
            "app_by_id": {a["application_id"]: a for a in apps},
            "paths": paths, "disp": dispositions, "engineers": engineers,
            "relief_needs": relief_needs, "relief_optimum": optimum, "ledger": ledger,
            "corpus_shingles": content_shingles(rules_text) | content_shingles(memo_text)}


def load_submission(agent_dir: Path) -> dict:
    sub: dict[str, Any] = {"errors": []}
    paths = {key: agent_dir / name for key, name in ARTIFACTS.items()}
    sub["paths"] = paths

    header, rows = read_csv_file(paths["register"])
    sub["register_header"], sub["register_rows"] = header, rows
    sub["register_by_structure"] = {}
    for row in rows:
        key = (row.get("structure_number") or "").strip()
        if key and key not in sub["register_by_structure"]:
            sub["register_by_structure"][key] = row

    sub["dispositions_doc"], sub["dispositions"], sub["summary"] = None, [], {}
    if paths["dispositions"].exists():
        try:
            doc = json.loads(paths["dispositions"].read_text(encoding="utf-8-sig"))
            sub["dispositions_doc"] = doc
            if isinstance(doc, dict):
                entries = doc.get("dispositions")
                if isinstance(entries, list):
                    sub["dispositions"] = [e for e in entries if isinstance(e, dict)]
                if isinstance(doc.get("summary"), dict):
                    sub["summary"] = doc["summary"]
        except Exception as exc:
            sub["errors"].append("permit_dispositions.json unreadable: %s" % exc)
    sub["disp_by_id"] = {}
    for entry in sub["dispositions"]:
        key = str(entry.get("application_id", "")).strip()
        if key and key not in sub["disp_by_id"]:
            sub["disp_by_id"][key] = entry

    sub["programme_header"], sub["programme_rows"] = read_csv_file(paths["programme"])
    sub["ledger_header"], sub["ledger_rows"] = read_csv_file(paths["ledger"], delimiter="\t")
    sub["refusal_header"], sub["refusal_rows"] = read_csv_file(paths["refusals"])
    sub["refusal_by_id"] = {}
    for row in sub["refusal_rows"]:
        key = (row.get("application_id") or "").strip()
        if key and key not in sub["refusal_by_id"]:
            sub["refusal_by_id"][key] = row

    sub["chart_text"] = ""
    sub["chart_rects"] = []
    sub["chart_labels"] = []
    sub["chart_root"] = None
    if paths["chart"].exists():
        raw = paths["chart"].read_text(encoding="utf-8", errors="replace")
        sub["chart_text"] = raw
        try:
            root = ET.fromstring(raw)
            sub["chart_root"] = root
            for element in root.iter():
                tag = element.tag.split("}")[-1]
                if tag == "rect" and element.get("data-structure"):
                    sub["chart_rects"].append(element)
                elif tag == "text":
                    sub["chart_labels"].append("".join(element.itertext()))
        except Exception as exc:
            sub["errors"].append("capacity_profile.svg unparseable: %s" % exc)

    sub["letter_text"] = ""
    sub["letter_sections"] = {}
    sub["letter_order"] = []
    if paths["letter"].exists():
        text = paths["letter"].read_text(encoding="utf-8", errors="replace")
        sub["letter_text"] = text
        chunks = re.split(r"^##\s+", text, flags=re.MULTILINE)
        for chunk in chunks[1:]:
            head = chunk.splitlines()[0] if chunk.splitlines() else ""
            found = re.match(r"(APP-\d{3})", head.strip())
            if found:
                aid = found.group(1)
                sub["letter_order"].append(aid)
                sub["letter_sections"].setdefault(aid, chunk)
            elif head.strip().lower().startswith("docket summary"):
                sub["letter_summary"] = chunk
    sub.setdefault("letter_summary", "")
    return sub


def reg_val(sub, structure, column):
    row = sub["register_by_structure"].get(structure)
    return (row.get(column, "") if row else "")


def artifact_has_substance(key, path, truth) -> bool:
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    applications = {a["application_id"] for a in truth["apps"]}
    structures = set(truth["by_num"])
    if key == "dispositions":
        try:
            doc = json.loads(raw)
        except Exception:
            return False
        entries = doc.get("dispositions") if isinstance(doc, dict) else None
        if not isinstance(entries, list):
            return False
        named = {str(e.get("application_id", "")).strip() for e in entries
                 if isinstance(e, dict)}
        return len(named & applications) >= 2
    if key == "chart":
        if "<svg" not in raw.lower():
            return False
        drawn = set(re.findall(r'data-structure="([^"]*)"', raw))
        return len(drawn & structures) >= 2
    if key == "letter":
        return len(set(re.findall(r"APP-\d{3}", raw)) & applications) >= 2
    delimiter = "\t" if key == "ledger" else ","
    lines = [line for line in raw.splitlines() if line.strip()]
    if len(lines) < 2 or delimiter not in lines[0]:
        return False
    body = "\n".join(lines[1:])
    if key == "register":
        return len({s for s in structures if s in body}) >= 2
    if key in ("programme",):
        return len({s for s in structures if s in body}) >= 1
    if key == "refusals":
        return len(set(re.findall(r"APP-\d{3}", body)) & applications) >= 1
    return True


def static_required_artifacts_present(ctx):
    sub = ctx["S"]
    good, notes = 0, []
    for key, name in ARTIFACTS.items():
        path = sub["paths"][key]
        if not path.exists():
            notes.append("%s missing" % name)
            continue
        size = path.stat().st_size
        if size == 0:
            notes.append("%s empty" % name)
        elif size > MAX_ARTIFACT_BYTES:
            notes.append("%s over 3 MB" % name)
        elif not artifact_has_substance(key, path, ctx["T"]):
            notes.append("%s carries none of the docket's own records" % name)
        else:
            good += 1
    return frac(good, len(ARTIFACTS)), (
        "%d/%d artifacts present, under 3 MB and carrying records from this docket%s"
        % (good, len(ARTIFACTS), ("; " + "; ".join(notes)) if notes else ""))


def static_register_shape_and_coverage(ctx):
    T, sub = ctx["T"], ctx["S"]
    truth_ids = {r["structure_number"] for r in T["structures"]}
    header_ok = 1.0 if sub["register_header"] == REGISTER_COLS else 0.0
    rows = sub["register_rows"]
    count_ok = 1.0 if len(rows) == len(truth_ids) else 0.0
    written = [(r.get("structure_number") or "").strip() for r in rows]
    coverage = frac(len({s for s in written if s in truth_ids}), len(truth_ids))
    order_key = []
    for row in rows:
        order_key.append(((row.get("corridor_id") or "").strip(),
                          fnum(row.get("kilometerpoint"), 0.0),
                          (row.get("structure_number") or "").strip()))
    sorted_ok = 1.0 if order_key and order_key == sorted(order_key) else 0.0
    score = mean([header_ok, count_ok, coverage, sorted_ok])
    return score, ("header %s, %d rows (expected %d), %.0f%% of structures covered, sort %s"
                   % ("exact" if header_ok else "wrong", len(rows), len(truth_ids),
                      100 * coverage, "ok" if sorted_ok else "wrong"))


def static_dispositions_json_shape(ctx):
    T, sub = ctx["T"], ctx["S"]
    doc = sub["dispositions_doc"]
    parts = []
    parts.append(1.0 if isinstance(doc, dict) and set(doc.keys()) ==
                 {"docket_date", "dispositions", "summary"} else 0.0)
    entries = sub["dispositions"]
    parts.append(1.0 if len(entries) == len(T["apps"]) else 0.0)
    key_ok = sum(1 for e in entries if set(e.keys()) == set(DISPOSITION_KEYS))
    parts.append(frac(key_ok, len(T["apps"])))
    parts.append(1.0 if set(sub["summary"].keys()) == set(SUMMARY_KEYS) else 0.0)
    truth_ids = {a["application_id"] for a in T["apps"]}
    parts.append(frac(len(set(sub["disp_by_id"]) & truth_ids), len(truth_ids)))
    return mean(parts), ("%d entries, %d with the exact key set, summary keys %s, %d/%d "
                         "application ids present" % (len(entries), key_ok,
                                                      "exact" if parts[3] else "wrong",
                                                      len(set(sub["disp_by_id"]) & truth_ids),
                                                      len(truth_ids)))


def static_programme_and_refusal_shape(ctx):
    T, sub = ctx["T"], ctx["S"]
    parts = []
    parts.append(1.0 if sub["programme_header"] == PROGRAMME_COLS else 0.0)
    eligible = sum(1 for cap in T["caps"].values() if cap["rerate_eligible"])
    expected_floor = max(1, min(4, eligible // 12))
    parts.append(bounded_frac(len(sub["programme_rows"]), expected_floor))
    parts.append(1.0 if sub["refusal_header"] == REFUSAL_COLS else 0.0)
    truth_ids = {a["application_id"] for a in T["apps"]}
    written = [(r.get("application_id") or "").strip() for r in sub["refusal_rows"]]
    parts.append(frac(sum(1 for a in written if a in truth_ids), len(written)) if written else 0.0)
    parts.append(1.0 if written and written == sorted(written) else 0.0)
    return mean(parts), ("programme header %s with %d rows; refusal header %s with %d rows, "
                         "sorted %s" % ("exact" if parts[0] else "wrong",
                                        len(sub["programme_rows"]),
                                        "exact" if parts[2] else "wrong", len(written),
                                        "yes" if parts[4] else "no"))


def static_ledger_shape(ctx):
    T, sub = ctx["T"], ctx["S"]
    parts = [1.0 if sub["ledger_header"] == LEDGER_COLS else 0.0]
    rows = sub["ledger_rows"]
    parts.append(1.0 if len(rows) == len(T["ledger"]) else 0.0)
    written = {((r.get("corridor_id") or "").strip(), (r.get("weight_band") or "").strip())
               for r in rows}
    parts.append(frac(len(written & set(T["ledger"])), len(T["ledger"])))
    band_rank = {band: index for index, (band, _) in enumerate(WEIGHT_BANDS)}
    keys = [((r.get("corridor_id") or "").strip(),
             band_rank.get((r.get("weight_band") or "").strip(), 99)) for r in rows]
    parts.append(1.0 if keys and keys == sorted(keys) else 0.0)
    return mean(parts), "%d rows, %d/%d corridor-band cells present, sort %s" % (
        len(rows), len(written & set(T["ledger"])), len(T["ledger"]),
        "ok" if parts[3] else "wrong")


def static_chart_is_standalone_svg(ctx):
    sub = ctx["S"]
    text = sub["chart_text"]
    parts = []
    root = sub["chart_root"]
    parts.append(1.0 if root is not None and root.tag.split("}")[-1] == "svg" else 0.0)
    parts.append(1.0 if root is not None and (root.get("viewBox") or "").strip() == CHART_VIEWBOX
                 else 0.0)
    external = re.search(r"(?:href|src|xlink:href)\s*=\s*[\"']\s*(?:https?:)?//", text, re.I)
    parts.append(0.0 if external else 1.0)
    parts.append(1.0 if len(sub["chart_rects"]) > 0 else 0.0)
    return mean(parts), "root %s, viewBox %s, external refs %s, %d tagged rects" % (
        "svg" if parts[0] else "not svg", "exact" if parts[1] else "wrong",
        "found" if external else "none", len(sub["chart_rects"]))


def static_letter_section_inventory(ctx):
    T, sub = ctx["T"], ctx["S"]
    truth_ids = [a["application_id"] for a in T["apps"]]
    summary_words = len((sub.get("letter_summary") or "").split())
    parts = [1.0 if summary_words >= 12 else 0.0]
    parts.append(frac(len(set(sub["letter_sections"]) & set(truth_ids)), len(truth_ids)))
    parts.append(1.0 if sub["letter_order"] == sorted(sub["letter_order"]) and sub["letter_order"]
                 else 0.0)
    duplicates = len(sub["letter_order"]) - len(set(sub["letter_order"]))
    parts.append(1.0 if duplicates == 0 and sub["letter_order"] else 0.0)
    return mean(parts), "docket summary %s, %d/%d application sections, ascending %s, %d duplicates" % (
        "present (%d words)" % summary_words if parts[0] else "missing or too short",
        len(set(sub["letter_sections"]) & set(truth_ids)),
        len(truth_ids), "yes" if parts[2] else "no", duplicates)


def static_identifier_domain_integrity(ctx):
    T, sub = ctx["T"], ctx["S"]
    structures = set(T["by_num"])
    applications = {a["application_id"] for a in T["apps"]}
    memo_ids = {m["memo_id"] for m in T["memos"]}
    engineers = set(T["engineers"])
    good = total = 0

    def account(values, domain):
        nonlocal good, total
        for value in values:
            value = str(value).strip()
            if not value:
                continue
            total += 1
            if value in domain:
                good += 1

    account([r.get("structure_number") for r in sub["register_rows"]], structures)
    account([r.get("governing_memo_id") for r in sub["register_rows"]], memo_ids)
    for entry in sub["dispositions"]:
        account([entry.get("application_id")], applications)
        account(as_list(entry.get("structures_crossed")), structures)
        account([entry.get("controlling_structure")], structures)
        account(as_list(entry.get("blocking_structures")), structures)
        account(as_list(entry.get("governing_memo_ids")), memo_ids)
    for row in sub["programme_rows"]:
        account([row.get("structure_number")], structures)
        account([row.get("engineer_id")], engineers)
        account(as_list(row.get("relieved_application_ids")), applications)
    for row in sub["refusal_rows"]:
        account([row.get("application_id")], applications)
        account(as_list(row.get("blocking_structures")), structures)
        account(as_list(row.get("supporting_memo_ids")), memo_ids)
    for row in sub["ledger_rows"]:
        account([row.get("bottleneck_structure")], structures)
    return frac(good, total), "%d/%d identifier references resolve to a packaged record" % (
        good, total)


def static_declared_ordering_and_derived_counts(ctx):
    T, sub = ctx["T"], ctx["S"]
    good = total = 0

    def score(condition):
        nonlocal good, total
        total += 1
        if condition:
            good += 1

    ids = [str(e.get("application_id", "")).strip() for e in sub["dispositions"]]
    score(bool(ids) and ids == sorted(ids))

    position = {r["structure_number"]: (r["corridor_id"], r["kilometerpoint"],
                                        r["structure_number"]) for r in T["structures"]}
    for entry in sub["dispositions"]:
        crossed = as_list(entry.get("structures_crossed"))
        keys = [position[x] for x in crossed if x in position]
        score(len(keys) == len(crossed) and keys == sorted(keys))
        memos = as_list(entry.get("governing_memo_ids"))
        score(memos == sorted(set(memos)))
        blocking = as_list(entry.get("blocking_structures"))
        score(blocking == sorted(set(blocking)))
        codes = as_list(entry.get("condition_codes"))
        score(codes == sorted(set(codes)))

    for entry in sub["dispositions"]:
        decision = str(entry.get("decision", "")).strip().upper()
        reason = str(entry.get("refusal_reason_code", "")).strip()
        score(bool(reason) == (decision in NOT_ISSUED))
        detour = fnum(entry.get("detour_km"), 0.0)
        score(close(detour, 0.0, 1e-9) or decision == "REROUTE_LOAD")

    programme_order = [(fnum(r.get("week_index"), 0.0), (r.get("structure_number") or "").strip())
                       for r in sub["programme_rows"]]
    score(bool(programme_order) and programme_order == sorted(programme_order))

    for row in sub["programme_rows"]:
        relieved = as_list(row.get("relieved_application_ids"))
        score(relieved == sorted(set(relieved)))
        stated = fnum(row.get("applications_relieved"))
        score(stated is not None and int(stated) == len(relieved))

    for row in sub["refusal_rows"]:
        blocking = as_list(row.get("blocking_structures"))
        score(blocking == sorted(set(blocking)))
        memos = as_list(row.get("supporting_memo_ids"))
        score(memos == sorted(set(memos)))

    places = {"kilometerpoint": 3, "condition_derate_factor": 2, "height_limit_m": 2,
              "operating_rating_t": 1, "inventory_rating_t": 1, "effective_capacity_t": 1,
              "width_limit_m": 1}
    optional_places = {"standing_restriction_t": 1, "rerated_capacity_t": 1}
    for row in sub["register_rows"]:
        for column, decimals in places.items():
            written = str(row.get(column, "")).strip()
            score(bool(re.fullmatch(r"-?\d+\.\d{%d}" % decimals, written)))
        for column, decimals in optional_places.items():
            written = str(row.get(column, "")).strip()
            score(not written or bool(re.fullmatch(r"-?\d+\.\d{%d}" % decimals, written)))

    return frac(good, total), (
        "%d/%d declared ordering, emptiness and derived-count rules hold - ascending application "
        "order, path order in structures_crossed, ascending de-duplicated identifier lists, a "
        "reason code only where the application is not issued, a zero detour except on a load "
        "reroute, the programme sorted by week then structure, applications_relieved equal to "
        "the length of its own list, and every register column written to the number of decimal "
        "places the instruction fixes" % (good, total))


def reward_hacking_no_duplicate_or_phantom_rows(ctx):
    T, sub = ctx["T"], ctx["S"]
    parts, notes = [], []

    written = [(r.get("structure_number") or "").strip() for r in sub["register_rows"]]
    duplicates = len(written) - len(set(written))
    real = {s2 for s2 in written if s2 in T["by_num"]}
    substantive = set()
    for structure in real:
        cap = T["caps"][structure]
        if (close(fnum(reg_val(sub, structure, "effective_capacity_t")),
                  cap["effective_capacity_t"])
                or close(fnum(reg_val(sub, structure, "condition_derate_factor")),
                         cap["derate_factor"], 0.006)):
            substantive.add(structure)
    parts.append(frac(max(0, len(substantive) - duplicates), len(T["by_num"])))
    notes.append("register %d real structures of which %d carry a derived value that holds up, "
                 "%d duplicate rows" % (len(real), len(substantive), duplicates))

    ids = [str(e.get("application_id", "")).strip() for e in sub["dispositions"]]
    dup_apps = len(ids) - len(set(ids))
    known = {a for a in ids if a in T["app_by_id"]}
    parts.append(frac(max(0, len(known) - dup_apps), len(T["apps"])))
    notes.append("dispositions %d known applications, %d duplicate" % (len(known), dup_apps))

    prog = [(r.get("structure_number") or "").strip() for r in sub["programme_rows"]]
    dup_prog = len(prog) - len(set(prog))
    eligible = sum(1 for s2 in set(prog)
                   if s2 in T["caps"] and T["caps"][s2]["rerate_eligible"])
    claimed = [a for r in sub["programme_rows"] for a in as_list(r.get("relieved_application_ids"))]
    dup_claim = len(claimed) - len(set(claimed))
    parts.append(frac(max(0, eligible - dup_prog - dup_claim), max(1, len(prog))))
    notes.append("programme %d/%d rows eligible, %d duplicate, %d double-claimed applications"
                 % (eligible, len(prog), dup_prog, dup_claim))

    truth_refused = {a["application_id"] for a in T["apps"]
                     if T["disp"][a["application_id"]]["decision"] in NOT_ISSUED}
    refusal_ids = [(r.get("application_id") or "").strip() for r in sub["refusal_rows"]]
    dup_ref = len(refusal_ids) - len(set(refusal_ids))
    padded = sum(1 for aid in set(refusal_ids) if aid not in truth_refused)
    parts.append(frac(max(0, len(set(refusal_ids) & truth_refused) - dup_ref - padded),
                      len(truth_refused)))
    notes.append("refusal register covers %d of the %d applications that are not issued, "
                 "%d duplicate, %d padded"
                 % (len(set(refusal_ids) & truth_refused), len(truth_refused), dup_ref, padded))
    return mean(parts), "; ".join(notes)


def reward_hacking_summary_reconciles_with_rows(ctx):
    T, sub = ctx["T"], ctx["S"]
    entries = sub["dispositions"]
    decisions = [str(e.get("decision", "")).strip().upper() for e in entries]
    own = {
        "application_count": len(entries),
        "issued_count": decisions.count("ISSUE"),
        "issued_with_conditions_count": decisions.count("ISSUE_WITH_CONDITIONS"),
        "reroute_load_count": decisions.count("REROUTE_LOAD"),
        "reroute_clearance_count": decisions.count("REROUTE_CLEARANCE"),
        "refused_count": decisions.count("REFUSE"),
        "withdrawn_count": decisions.count("WITHDRAWN"),
        "structures_assessed": len(sub["register_rows"]),
        "structures_with_standing_restriction": sum(
            1 for r in sub["register_rows"] if str(r.get("standing_restriction_t", "")).strip()),
        "distinct_controlling_structures": len({str(e.get("controlling_structure", "")).strip()
                                                for e in entries
                                                if str(e.get("controlling_structure", "")).strip()}),
        "total_detour_km": round(sum(fnum(e.get("detour_km"), 0.0) for e in entries), 1),
        "relieved_application_count": len({a for r in sub["programme_rows"]
                                           for a in as_list(r.get("relieved_application_ids"))}),
    }
    hits, misses = 0, []
    for key, expected in own.items():
        stated = sub["summary"].get(key)
        ok = (close(fnum(stated), expected, 0.051) if isinstance(expected, float)
              else (fnum(stated) is not None and abs(fnum(stated) - expected) < 1e-9))
        if ok:
            hits += 1
        else:
            misses.append("%s stated %r vs rows %r" % (key, stated, expected))
    self_consistency = frac(hits, len(own))

    truth_counts = {
        "structures_with_standing_restriction": len(T["standing"]),
        "distinct_controlling_structures": len({T["disp"][a["application_id"]]
                                                ["controlling_structure"] for a in T["apps"]
                                                if T["disp"][a["application_id"]]
                                                ["controlling_structure"]}),
        "total_detour_km": round(sum(T["disp"][a["application_id"]]["detour_km"]
                                     for a in T["apps"]), 1),
    }
    grounded_hits = 0
    for key, expected in truth_counts.items():
        stated = fnum(sub["summary"].get(key))
        if stated is not None and abs(stated - expected) <= 0.051:
            grounded_hits += 1
    refused_declared = sum(fnum(sub["summary"].get(k), 0.0) or 0.0 for k in
                           ("reroute_load_count", "reroute_clearance_count", "refused_count"))
    tie = 1.0 if abs(refused_declared - len(sub["refusal_rows"])) < 1e-9 and sub["refusal_rows"] \
        else 0.0
    grounded = mean([frac(grounded_hits, len(truth_counts)), tie])

    return self_consistency * grounded, (
        "%d/%d summary fields reconcile with the rows written; %d/%d analysis-derived counts "
        "stated correctly; refusal register %s the declared unissued count%s"
        % (hits, len(own), grounded_hits, len(truth_counts),
           "matches" if tie else "does not match",
           ("; " + "; ".join(misses[:3])) if misses else ""))


def reward_hacking_register_is_derived_not_copied(ctx):
    T, sub = ctx["T"], ctx["S"]
    agree = 0
    for structure, cap in T["caps"].items():
        record = T["by_num"][structure]
        must_move = abs(cap["effective_capacity_t"] - record["operating_rating_t"]) > 0.051
        effective = fnum(reg_val(sub, structure, "effective_capacity_t"))
        operating = fnum(reg_val(sub, structure, "operating_rating_t"))
        if effective is None or operating is None:
            continue
        if (abs(effective - operating) > 0.051) == must_move:
            agree += 1
    relationship = frac(agree, len(T["caps"]))

    magnitude = 0
    for structure, cap in T["caps"].items():
        record = T["by_num"][structure]
        effective = fnum(reg_val(sub, structure, "effective_capacity_t"))
        if effective is None or not record["operating_rating_t"]:
            continue
        truth_ratio = cap["effective_capacity_t"] / record["operating_rating_t"]
        written_ratio = effective / record["operating_rating_t"]
        if abs(written_ratio - truth_ratio) <= 0.01:
            magnitude += 1
    magnitude = frac(magnitude, len(T["caps"]))

    written = [fnum(r.get("effective_capacity_t")) for r in sub["register_rows"]]
    written = [round(v, 1) for v in written if v is not None]
    truth_values = [cap["effective_capacity_t"] for cap in T["caps"].values()]
    spread = bounded_frac(len(set(written)), len(set(truth_values))) if written else 0.0
    dominance = (Counter(written).most_common(1)[0][1] / len(written)) if written else 1.0
    truth_dominance = Counter(truth_values).most_common(1)[0][1] / len(truth_values)
    concentration = (1.0 if dominance <= truth_dominance + 0.05
                     else 1.0 - bounded_frac(dominance - truth_dominance,
                                             max(1e-9, 1.0 - truth_dominance)))
    return mean([relationship, magnitude, min(spread, concentration)]), (
        "%d/%d structures move (or hold) exactly as the derate, posting cap and standing limit "
        "require and %.0f%% carry the right size of move against the pinned operating rating; "
        "%d distinct capacities written against %d in the evidence; the most common value covers "
        "%.0f%% of rows against %.0f%% in the evidence"
        % (agree, len(T["caps"]), 100 * magnitude, len(set(written)), len(set(truth_values)),
           100 * dominance, 100 * truth_dominance))


def truth_marks_for(ctx, aid):
    T = ctx["T"]
    app, truth = T["app_by_id"][aid], T["disp"][aid]
    marks = {aid, app["applicant"], app["commodity"]}
    marks |= set(truth["structures_crossed"])
    marks |= set(truth["governing_memo_ids"])
    marks |= {"%.1f" % app["gross_weight_t"], "%.2f" % app["overall_width_m"],
              "%.2f" % app["overall_height_m"]}
    if truth["controlling_structure"]:
        marks.add("%.1f" % T["caps"][truth["controlling_structure"]]["effective_capacity_t"])
    return {m for m in marks if m and len(str(m)) >= 3}


def reward_hacking_letter_sections_are_case_specific(ctx):
    T, sub = ctx["T"], ctx["S"]
    ids = [a["application_id"] for a in T["apps"]]
    sections = {aid: sub["letter_sections"].get(aid, "") for aid in ids}
    present = [aid for aid in ids if sections[aid].strip()]
    if not present:
        return 0.0, "no application sections to inspect"

    grams = {aid: ngrams(sections[aid], 8) for aid in present}
    distinct = 0
    for aid in present:
        worst = 0.0
        for other in present:
            if other == aid:
                continue
            a, b = grams[aid], grams[other]
            if a and b:
                worst = max(worst, len(a & b) / len(a | b))
        if worst < 0.45:
            distinct += 1
    part_distinct = frac(distinct, len(ids))

    shared = Counter()
    for aid in present:
        shared.update(grams[aid])
    top_runs = [count for _, count in shared.most_common(5)]
    top_share = (mean(top_runs) / len(present)) if top_runs else 1.0
    part_template = 1.0 - bounded_frac(max(0.0, top_share - 0.30), 0.70)

    all_marks = set()
    for aid in present:
        all_marks |= truth_marks_for(ctx, aid)
    spread = {mark: sum(1 for aid in present if mark in sections[aid]) for mark in all_marks}
    rare_cap = max(1, int(0.25 * len(present)))
    own_marks = 0
    for aid in present:
        carried = {mark for mark in truth_marks_for(ctx, aid)
                   if mark in sections[aid] and spread.get(mark, 0) <= rare_cap}
        if len(carried) >= 3:
            own_marks += 1
    part_own = frac(own_marks, len(ids))

    return mean([part_distinct, part_template, part_own]), (
        "%d/%d sections distinct from every other section; the five most reused eight-word runs "
        "reach %.0f%% of sections on average (up to 30%% is free); %d/%d carry at least three "
        "identifiers or figures that genuinely belong to that application and to few others"
        % (distinct, len(ids), 100 * top_share, own_marks, len(ids)))


def reward_hacking_letter_figures_match_dispositions(ctx):
    T, sub = ctx["T"], ctx["S"]
    ids = [a["application_id"] for a in T["apps"]]
    hits = total = 0
    flooded_sections = 0
    for aid in ids:
        section = sub["letter_sections"].get(aid, "")
        entry = sub["disp_by_id"].get(aid)
        app = T["app_by_id"][aid]
        total += 7
        if not section.strip():
            continue
        named_any = sum(1 for s2 in T["by_num"] if s2 in section)
        if named_any > len(T["disp"][aid]["structures_crossed"]) + 2:
            flooded_sections += 1
            continue
        numbers = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", section)]
        truth = T["disp"][aid]
        gross = fnum(entry.get("gross_weight_t")) if entry else None
        if (gross is not None and abs(gross - app["gross_weight_t"]) <= 0.051
                and any(abs(n - app["gross_weight_t"]) <= 0.051 for n in numbers)):
            hits += 1
        controlling = str(entry.get("controlling_structure", "")).strip() if entry else ""
        if (truth["controlling_structure"] and controlling == truth["controlling_structure"]
                and controlling in section):
            hits += 1
        decision = str(entry.get("decision", "")).strip().upper() if entry else ""
        spoken = section.upper().replace("-", "_").replace(" ", "_")
        if decision == truth["decision"] and decision in spoken:
            hits += 1
        if any(record["structure_number"] in section for record in T["paths"][aid]):
            hits += 1
        if any(abs(n - app["overall_width_m"]) <= 0.011
               or abs(n - app["overall_height_m"]) <= 0.011 for n in numbers):
            hits += 1
        if app["applicant"].split()[0].lower() in section.lower():
            hits += 1
        if app["commodity"].split()[0].lower() in section.lower():
            hits += 1
    return frac(hits, total), (
        "%d/%d section claims agree with that application's own disposition row and with the "
        "packaged application record; %d sections forfeited for naming far more structures than "
        "the movement touches" % (hits, total, flooded_sections))


def reward_hacking_letter_not_copied_source_prose(ctx):
    T, sub = ctx["T"], ctx["S"]
    windows = content_shingles(sub["letter_text"])
    if not windows:
        return 0.0, "letter carries no readable prose"
    overlap = len(windows & T["corpus_shingles"])
    density = overlap / len(windows)
    score = 1.0 - bounded_frac(density, 0.08)
    return score, ("%.1f%% of the letter's six-content-word runs also appear in the packaged memo "
                   "and rules prose (0%% earns full credit, 8%% or more earns none)"
                   % (100 * density))


def reward_hacking_chart_geometry_follows_register(ctx):
    T, sub = ctx["T"], ctx["S"]
    lanes = {corridor: rank for rank, corridor in enumerate(sorted(T["by_corridor"]))}
    rects = sub["chart_rects"]
    if not rects:
        return 0.0, "no rects carrying data-structure"

    programmed = {(r.get("structure_number") or "").strip() for r in sub["programme_rows"]}
    truth_bottleneck = {key[0]: value["bottleneck_structure"]
                        for key, value in T["ledger"].items()}

    def expected_from(km, capacity, corridor):
        height = round(capacity)
        return (CHART_X0 + CHART_PX_PER_KM * km,
                CHART_LANE_Y0 + CHART_LANE_H * lanes[corridor] - height, height)

    grounded = role_good = 0
    for rect in rects:
        structure = (rect.get("data-structure") or "").strip()
        corridor = (rect.get("data-corridor") or "").strip()
        record = T["by_num"].get(structure)
        if record is None or corridor not in lanes:
            continue
        x, y, h = fnum(rect.get("x")), fnum(rect.get("y")), fnum(rect.get("height"))
        width_ok = close(fnum(rect.get("width")), CHART_BAR_W, 0.51)

        tx, ty, th = expected_from(record["kilometerpoint"],
                                   T["caps"][structure]["effective_capacity_t"],
                                   record["corridor_id"])
        if (corridor == record["corridor_id"] and width_ok and close(x, tx, 1.01)
                and close(y, ty, 1.01) and close(h, th, 1.01)):
            grounded += 1

        expected_role = ("RERATED" if structure in programmed
                         else "BOTTLENECK" if truth_bottleneck.get(record["corridor_id"]) == structure
                         else "NORMAL")
        if (rect.get("data-role") or "").strip().upper() == expected_role:
            role_good += 1

    total = len(T["by_num"])
    labels = " | ".join(sub["chart_labels"])
    label_hits = 0
    for corridor in sorted(T["by_corridor"]):
        lowest = T["ledger"][(corridor, WEIGHT_BANDS[0][0])]["lowest_effective_capacity_t"]
        if corridor in labels and ("%.1f" % lowest) in labels:
            label_hits += 1
    spent = sum(fnum(r.get("engineer_weeks"), 0.0) or 0.0 for r in sub["programme_rows"])
    numbers = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", labels)]
    total_stated = 1.0 if any(abs(n - spent) < 1e-9 for n in numbers) and spent > 0 else 0.0
    label_score = mean([frac(label_hits, len(T["by_corridor"])), total_stated])

    drawn = [(r.get("data-structure") or "").strip() for r in rects]
    phantom = sum(1 for d in drawn if d not in T["by_num"])
    duplicated = len(drawn) - len(set(drawn))
    honest = 1.0 - bounded_frac(phantom + duplicated, max(1, len(drawn)))
    return mean([frac(grounded, total), frac(role_good, total), honest, label_score]), (
        "%d of %d structures drawn where the evidence puts them, %d carrying the right role, "
        "%d phantom and %d duplicated bars; %d/%d lane labels carry the corridor and its lowest "
        "capacity and the programme total is %s"
        % (grounded, total, role_good, phantom, duplicated, label_hits, len(T["by_corridor"]),
           "stated" if total_stated else "absent"))


def reward_hacking_no_invented_codes_or_criteria(ctx):
    T, sub = ctx["T"], ctx["S"]
    good = total = 0

    def account(values, allowed):
        nonlocal good, total
        for value in values:
            value = str(value).strip()
            if not value:
                continue
            total += 1
            if value.upper() in allowed:
                good += 1

    account([e.get("decision") for e in sub["dispositions"]], set(DECISIONS))
    for entry in sub["dispositions"]:
        account(as_list(entry.get("condition_codes")), set(CONDITION_CODES))
        account([entry.get("escort_class")], set(ESCORT_CLASSES))
        account([entry.get("refusal_reason_code")], set(REASON_CODES))
    account([r.get("refusal_reason_code") for r in sub["refusal_rows"]], set(REASON_CODES))
    account([r.get("decision") for r in sub["refusal_rows"]], set(NOT_ISSUED))
    account([r.get("material_class") for r in sub["register_rows"]], set(MATERIAL_CLASSES))
    account([r.get("material_class") for r in sub["programme_rows"]], set(MATERIAL_CLASSES))
    account([r.get("condition_trend") for r in sub["register_rows"]], set(CONDITION_TRENDS))
    for row in sub["programme_rows"]:
        week = fnum(row.get("week_index"))
        total += 1
        if week is not None and 1 <= week <= PROGRAMME_WEEKS and float(week).is_integer():
            good += 1
    legality = frac(good, total)

    def paired_information(field, truth_of):
        pairs = []
        for app in T["apps"]:
            entry = sub["disp_by_id"].get(app["application_id"])
            stated = str((entry or {}).get(field, "")).strip().upper()
            pairs.append((truth_of(app), stated or "<missing>"))
        n = len(pairs)
        if n == 0:
            return 0.0
        joint, left, right = Counter(pairs), Counter(a for a, _ in pairs), Counter(
            b for _, b in pairs)

        def entropy(counter):
            return -sum((c / n) * math.log(c / n) for c in counter.values() if c)

        h_left, h_right = entropy(left), entropy(right)
        if h_left <= 1e-12 or h_right <= 1e-12:
            return 0.0
        info = sum((c / n) * math.log((c / n) / ((left[a] / n) * (right[b] / n)))
                   for (a, b), c in joint.items() if c)
        # normalised mutual information is analytically within [0, 1]; the bounded ratio
        # keeps floating-point noise from carrying it outside without masking a real value
        return bounded_frac(2 * max(info, 0.0), h_left + h_right)

    agreement = mean([
        paired_information("decision", lambda a: T["disp"][a["application_id"]]["decision"]),
        paired_information("escort_class",
                           lambda a: T["disp"][a["application_id"]]["escort_class"]),
    ])
    return mean([legality, agreement]), (
        "%d/%d coded values come from the closed lists the rules state; verdicts carry %.3f of "
        "the information the evidence carries, paired application by application (a repeated or "
        "round-robin verdict earns none)" % (good, total, agreement))


def reward_hacking_memo_citations_actually_govern(ctx):
    T, sub = ctx["T"], ctx["S"]
    truth = {(structure, cap["governing_memo_id"]) for structure, cap in T["caps"].items()
             if cap["governing_memo_id"]}
    predicted = set()
    for row in sub["register_rows"]:
        structure = (row.get("structure_number") or "").strip()
        memo = (row.get("governing_memo_id") or "").strip()
        if structure and memo:
            predicted.add((structure, memo))
    register_score = set_f1(truth, predicted)

    valid = {memo for _, memo in truth}
    cited = total = 0
    for entry in sub["dispositions"]:
        for memo in as_list(entry.get("governing_memo_ids")):
            total += 1
            cited += 1 if memo in valid else 0
    for row in sub["refusal_rows"]:
        for memo in as_list(row.get("supporting_memo_ids")):
            total += 1
            cited += 1 if memo in valid else 0
    downstream = frac(cited, total) if total else 0.0
    return mean([register_score, downstream]), (
        "register citation F1 %.3f against the %d memos that actually govern (%d asserted); "
        "%d/%d memos cited in the dispositions and refusal register are governing memos"
        % (register_score, len(truth), len(predicted), cited, total))


def partial_oracle_coded_facts_and_derate(ctx):
    T, sub = ctx["T"], ctx["S"]
    hits = total = 0
    for structure, cap in T["caps"].items():
        total += 6
        record = T["by_num"][structure]
        transcribed = [
            reg_val(sub, structure, "route_label").strip() == record["route_label"],
            reg_val(sub, structure, "county").strip().upper() == record["county_name"],
            close(fnum(reg_val(sub, structure, "year_built")), record["year_built"], 0.01),
            reg_val(sub, structure, "design_load_code").strip() == record["design_load_code"],
            close(fnum(reg_val(sub, structure, "operating_rating_t")),
                  record["operating_rating_t"]),
            close(fnum(reg_val(sub, structure, "inventory_rating_t")),
                  record["inventory_rating_t"]),
            reg_val(sub, structure, "posting_status").strip()
            == record["structure_open_posted_closed"],
            reg_val(sub, structure, "material_class").strip().upper() == cap["material_class"],
        ]
        if all(transcribed):
            hits += 1
        condition = fnum(reg_val(sub, structure, "governing_condition_rating"))
        if condition is not None and int(condition) == cap["governing_condition"]:
            hits += 1
        if close(fnum(reg_val(sub, structure, "condition_derate_factor")),
                 cap["derate_factor"], 0.006):
            hits += 1
        if close(fnum(reg_val(sub, structure, "width_limit_m")), cap["width_limit_m"], 0.051):
            hits += 1
        if close(fnum(reg_val(sub, structure, "height_limit_m")), cap["height_limit_m"], 0.006):
            hits += 1
        if close(fnum(reg_val(sub, structure, "bypass_detour_km")), cap["bypass_detour_km"],
                 0.051):
            hits += 1
    return frac(hits, total), (
        "%d/%d coded readings correct across the 88 structures - the transcribed identity block "
        "(route, county, year, design load, both ratings, posting status and material class) "
        "taken as one, plus governing condition, derate factor, width limit, height limit and "
        "bypass detour" % (hits, total))


def partial_oracle_standing_restrictions(ctx):
    T, sub = ctx["T"], ctx["S"]
    truth = {(s, "%.1f" % cap["standing_restriction_t"]) for s, cap in T["caps"].items()
             if cap["standing_restriction_t"] is not None}
    predicted = set()
    for row in sub["register_rows"]:
        structure = (row.get("structure_number") or "").strip()
        value = fnum(row.get("standing_restriction_t"))
        if structure and value is not None:
            predicted.add((structure, "%.1f" % round(value, 1)))
    score = set_f1(truth, predicted)
    return score, ("F1 %.3f over the %d interim limits actually standing on the docket date; "
                   "%d asserted, %d of them correct in both structure and figure"
                   % (score, len(truth), len(predicted), len(truth & predicted)))


def partial_oracle_effective_capacity(ctx):
    T, sub = ctx["T"], ctx["S"]
    hits = sum(1 for structure, cap in T["caps"].items()
               if close(fnum(reg_val(sub, structure, "effective_capacity_t")),
                        cap["effective_capacity_t"]))
    return frac(hits, len(T["caps"])), (
        "%d/%d structures carry the effective capacity the derate, posting cap and standing limit "
        "produce" % (hits, len(T["caps"])))


def partial_oracle_letter_states_case_facts(ctx):
    T, sub = ctx["T"], ctx["S"]
    hits = total = 0
    for app in T["apps"]:
        aid = app["application_id"]
        truth = T["disp"][aid]
        section = sub["letter_sections"].get(aid, "")
        total += 7 if truth["decision"] in NOT_ISSUED else 6
        if not section.strip():
            continue
        spoken = section.upper().replace("-", "_").replace(" ", "_")
        if truth["decision"] in spoken:
            others = [d for d in DECISIONS if d != truth["decision"] and d in spoken
                      and not (d == "ISSUE" and "ISSUE_WITH_CONDITIONS" in spoken)]
            if not others:
                hits += 1
        named_any = sum(1 for s2 in T["by_num"] if s2 in section)
        flooded = named_any > len(truth["structures_crossed"]) + 2
        if flooded:
            continue
        if truth["controlling_structure"] and truth["controlling_structure"] in section:
            hits += 1
        capacity = (T["caps"][truth["controlling_structure"]]["effective_capacity_t"]
                    if truth["controlling_structure"] else None)
        numbers = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", section)]
        if capacity is not None and any(abs(n - capacity) <= 0.051 for n in numbers):
            hits += 1
        corridors = sorted({T["by_num"][s2]["corridor_id"] for s2 in truth["structures_crossed"]})
        if corridors and all(c in section for c in corridors):
            hits += 1
        if any(abs(n - len(truth["structures_crossed"])) < 1e-9 for n in numbers):
            hits += 1
        if truth["governing_memo_ids"]:
            if all(memo in section for memo in truth["governing_memo_ids"]):
                hits += 1
        elif not re.search(r"FRM-\d{4}", section):
            hits += 1
        if truth["decision"] in NOT_ISSUED:
            named = [s2 for s2 in truth["blocking_structures"] if s2 in section]
            if truth["blocking_structures"] and len(named) == len(truth["blocking_structures"]):
                hits += 1
    return frac(hits, total), (
        "%d/%d letter claims match the evidence for that application - decision, controlling "
        "structure and its capacity, the corridors the path runs on, how many structures it "
        "crosses, the governing memos, and the blocking structures where it is not issued"
        % (hits, total))


def partial_oracle_rerate_eligibility_and_yield(ctx):
    T, sub = ctx["T"], ctx["S"]
    flag_hits = value_hits = weeks_hits = 0
    for structure, cap in T["caps"].items():
        stated = as_bool(reg_val(sub, structure, "rerate_eligible"))
        if stated is not None and stated == cap["rerate_eligible"]:
            flag_hits += 1
        present = structure in sub["register_by_structure"]
        written = fnum(reg_val(sub, structure, "rerated_capacity_t"))
        if cap["rerate_eligible"]:
            if close(written, cap["rerated_capacity_t"]):
                value_hits += 1
        elif present and written is None:
            value_hits += 1
        if close(fnum(reg_val(sub, structure, "rerate_engineer_weeks")),
                 cap["rerate_engineer_weeks"], 0.01):
            weeks_hits += 1
    total = len(T["caps"])
    return mean([frac(flag_hits, total), frac(value_hits, total), frac(weeks_hits, total)]), (
        "%d/%d eligibility flags, %d/%d re-rated capacities, %d/%d effort figures correct"
        % (flag_hits, total, value_hits, total, weeks_hits, total))


def partial_oracle_path_construction(ctx):
    T, sub = ctx["T"], ctx["S"]
    membership, ordered = [], 0
    exact = 0
    for app in T["apps"]:
        aid = app["application_id"]
        truth_order = [r["structure_number"] for r in T["paths"][aid]]
        entry = sub["disp_by_id"].get(aid)
        predicted = as_list(entry.get("structures_crossed")) if entry else []
        membership.append(set_f1(set(truth_order), set(predicted)))
        if predicted == truth_order:
            ordered += 1
            exact += 1
    return mean([mean(membership), frac(ordered, len(T["apps"]))]), (
        "mean path F1 %.3f across %d applications; %d resolved exactly and in path order"
        % (mean(membership), len(T["apps"]), exact))


def partial_oracle_controlling_structure(ctx):
    T, sub = ctx["T"], ctx["S"]
    hits = total = 0
    for app in T["apps"]:
        aid = app["application_id"]
        truth = T["disp"][aid]
        entry = sub["disp_by_id"].get(aid) or {}
        total += 2
        if str(entry.get("controlling_structure", "")).strip() == truth["controlling_structure"]:
            hits += 1
        if close(fnum(entry.get("controlling_headroom_t")), truth["controlling_headroom_t"]):
            hits += 1
    return frac(hits, total), ("%d/%d controlling-structure identities and headroom figures "
                               "correct" % (hits, total))


def partial_oracle_decision_classification(ctx):
    T, sub = ctx["T"], ctx["S"]
    pairs = []
    for app in T["apps"]:
        aid = app["application_id"]
        entry = sub["disp_by_id"].get(aid) or {}
        pairs.append((T["disp"][aid]["decision"],
                      str(entry.get("decision", "")).strip().upper()))
    score = macro_f1(pairs, LADDER_DECISIONS)
    exact = sum(1 for t, p in pairs if t == p)
    return score, "macro F1 %.3f over the five decisions; %d/%d applications decided correctly" % (
        score, exact, len(pairs))


def partial_oracle_condition_codes(ctx):
    T, sub = ctx["T"], ctx["S"]
    truth = {(a["application_id"], code) for a in T["apps"]
             for code in T["disp"][a["application_id"]]["condition_codes"]}
    predicted = set()
    for entry in sub["dispositions"]:
        aid = str(entry.get("application_id", "")).strip()
        for code in as_list(entry.get("condition_codes")):
            predicted.add((aid, code.upper()))
    score = set_f1(truth, predicted)
    return score, ("F1 %.3f over the %d application-condition pairs the rules require; "
                   "%d asserted, %d correct" % (score, len(truth), len(predicted),
                                                len(truth & predicted)))


def partial_oracle_escort_class(ctx):
    T, sub = ctx["T"], ctx["S"]
    pairs = []
    for app in T["apps"]:
        aid = app["application_id"]
        entry = sub["disp_by_id"].get(aid) or {}
        pairs.append((T["disp"][aid]["escort_class"],
                      str(entry.get("escort_class", "")).strip().upper()))
    score = macro_f1(pairs, ESCORT_CLASSES)
    exact = sum(1 for t, p in pairs if t == p)
    return score, "macro F1 %.3f over the three escort classes; %d/%d correct" % (
        score, exact, len(pairs))


def partial_oracle_blocking_structures_and_detour(ctx):
    T, sub = ctx["T"], ctx["S"]
    truth = {(a["application_id"], s) for a in T["apps"]
             for s in T["disp"][a["application_id"]]["blocking_structures"]}
    predicted = set()
    for entry in sub["dispositions"]:
        aid = str(entry.get("application_id", "")).strip()
        for structure in as_list(entry.get("blocking_structures")):
            predicted.add((aid, structure))
    blocking_score = set_f1(truth, predicted)

    detour_apps = [a["application_id"] for a in T["apps"]
                   if T["disp"][a["application_id"]]["detour_km"] > 0]
    hits = 0
    for aid in detour_apps:
        entry = sub["disp_by_id"].get(aid)
        if entry and close(fnum(entry.get("detour_km")), T["disp"][aid]["detour_km"]):
            hits += 1
    detour_score = frac(hits, len(detour_apps))
    return mean([blocking_score, detour_score]), (
        "blocking-structure F1 %.3f over %d application-structure pairs; %d/%d rerouted "
        "applications carry the right detour distance"
        % (blocking_score, len(truth), hits, len(detour_apps)))


def partial_oracle_refusal_register_reasons(ctx):
    T, sub = ctx["T"], ctx["S"]
    refused = [a["application_id"] for a in T["apps"]
               if T["disp"][a["application_id"]]["decision"] in NOT_ISSUED]
    hits = total = 0
    completion = {}
    for row in sub["programme_rows"]:
        structure = (row.get("structure_number") or "").strip()
        week = fnum(row.get("week_index"))
        weeks = fnum(row.get("engineer_weeks"))
        if structure and week is not None and weeks is not None:
            completion[structure] = int(week + weeks - 1)

    for aid in refused:
        truth = T["disp"][aid]
        row = sub["refusal_by_id"].get(aid)
        total += 5
        if row is None:
            continue
        hits += 1
        if str(row.get("refusal_reason_code", "")).strip().upper() == truth["refusal_reason_code"]:
            hits += 1
        expected_shortfall = 0.0
        if truth["decision"] != "REROUTE_CLEARANCE" and truth["blocking_structures"]:
            lowest = min(T["caps"][s]["effective_capacity_t"] for s in truth["blocking_structures"])
            expected_shortfall = round(T["app_by_id"][aid]["gross_weight_t"] - lowest, 1)
        if close(fnum(row.get("shortfall_t")), expected_shortfall):
            hits += 1
        stated = as_bool(row.get("rerate_would_relieve"))
        if stated is not None and stated == (aid in T["relief_needs"]):
            hits += 1
        blocking = truth["blocking_structures"]
        if blocking and all(b in completion for b in blocking) and aid in T["relief_needs"]:
            expected_week = max(completion[b] for b in blocking)
            if close(fnum(row.get("earliest_relief_week")), expected_week, 0.01):
                hits += 1
        elif not str(row.get("earliest_relief_week", "")).strip():
            hits += 1
    return frac(hits, total), ("%d/%d refusal-register facts correct across the %d applications "
                               "that were not issued" % (hits, total, len(refused)))


def partial_oracle_rerating_programme_feasibility_and_saturation(ctx):
    T, sub = ctx["T"], ctx["S"]
    rows = sub["programme_rows"]
    if not rows:
        return 0.0, "no re-rating programme submitted"

    feas_hits = feas_total = 0
    spent = 0.0
    occupancy = defaultdict(set)
    engineer_total = Counter()
    chosen = []
    for row in rows:
        structure = (row.get("structure_number") or "").strip()
        engineer = (row.get("engineer_id") or "").strip()
        week = fnum(row.get("week_index"))
        weeks = fnum(row.get("engineer_weeks"))
        cap = T["caps"].get(structure)
        feas_total += 5

        if cap and cap["rerate_eligible"]:
            feas_hits += 1
            chosen.append(structure)
        if cap and close(weeks, cap["rerate_engineer_weeks"], 0.01):
            feas_hits += 1
        if cap and close(fnum(row.get("capacity_before_t")), cap["effective_capacity_t"]) \
                and close(fnum(row.get("capacity_after_t")), cap["rerated_capacity_t"]):
            feas_hits += 1
        engineer_row = T["engineers"].get(engineer)
        material = cap["material_class"] if cap else None
        if engineer_row and material and engineer_row["specialty_class"] in ("ANY", material):
            feas_hits += 1
        if (week is not None and weeks is not None and week >= 1
                and week + weeks - 1 <= PROGRAMME_WEEKS):
            occupied = set(range(int(week), int(week + weeks)))
            if engineer_row and not (occupancy[engineer] & occupied):
                feas_hits += 1
            occupancy[engineer] |= occupied
        if weeks is not None:
            spent += weeks
            engineer_total[engineer] += weeks

    budget_ok = 1.0 if spent <= ENGINEER_WEEK_BUDGET + 1e-9 else 0.0
    availability_ok = 1.0
    for engineer, used in engineer_total.items():
        limit = T["engineers"].get(engineer, {}).get("available_weeks", 0)
        if used > limit + 1e-9:
            availability_ok = 0.0
    feasibility = mean([frac(feas_hits, feas_total), budget_ok, availability_ok])

    chosen_set = set(chosen)
    truly_relieved = {aid for aid, need in T["relief_needs"].items() if set(need) <= chosen_set}
    claimed = {a for row in rows for a in as_list(row.get("relieved_application_ids"))}
    honesty = frac(len(claimed & truly_relieved), len(claimed)) if claimed else 0.0

    finish, attributed_to = {}, {}
    for row in rows:
        structure = (row.get("structure_number") or "").strip()
        week, weeks = fnum(row.get("week_index")), fnum(row.get("engineer_weeks"))
        if structure and week is not None and weeks is not None:
            finish[structure] = int(week + weeks - 1)
        for a in as_list(row.get("relieved_application_ids")):
            attributed_to[a] = structure
    attribution_ok = attribution_total = 0
    for aid in sorted(truly_relieved):
        blocking = [b for b in T["relief_needs"][aid] if b in finish]
        if not blocking:
            continue
        attribution_total += 1
        expected = sorted(blocking, key=lambda b: (-finish[b], b))[0]
        if attributed_to.get(aid) == expected:
            attribution_ok += 1
    attribution = frac(attribution_ok, attribution_total) if attribution_total else 0.0
    honesty = mean([honesty, attribution])
    saturation = (bounded_frac(len(truly_relieved), T["relief_optimum"])
                  if T["relief_optimum"] else 1.0)

    return mean([feasibility, honesty, saturation]), (
        "feasibility %.3f (%.1f of %d engineer-weeks spent); %d of %d claimed relieved "
        "applications actually relieve when the ladder is re-run and %d of %d are credited to "
        "the structure the tie-break rule names; saturation %d/%d against the optimum this "
        "verifier computed"
        % (feasibility, spent, ENGINEER_WEEK_BUDGET, len(claimed & truly_relieved), len(claimed),
           attribution_ok, attribution_total, len(truly_relieved), T["relief_optimum"]))


def partial_oracle_corridor_ledger_values(ctx):
    T, sub = ctx["T"], ctx["S"]
    written = {}
    for row in sub["ledger_rows"]:
        key = ((row.get("corridor_id") or "").strip(), (row.get("weight_band") or "").strip())
        written.setdefault(key, row)
    hits = total = 0
    for key, truth in T["ledger"].items():
        row = written.get(key)
        total += 6
        if row is None:
            continue
        if close(fnum(row.get("structures_below_ceiling")), truth["structures_below_ceiling"], 0.01):
            hits += 1
        if close(fnum(row.get("lowest_effective_capacity_t")),
                 truth["lowest_effective_capacity_t"]):
            hits += 1
        if (row.get("bottleneck_structure") or "").strip() == truth["bottleneck_structure"]:
            hits += 1
        if close(fnum(row.get("applications_in_band")), truth["applications_in_band"], 0.01):
            hits += 1
        if close(fnum(row.get("applications_blocked_on_corridor")),
                 truth["applications_blocked_on_corridor"], 0.01):
            hits += 1
        stated = as_bool(row.get("detour_available"))
        if stated is not None and stated == truth["detour_available"]:
            hits += 1
    return frac(hits, total), "%d/%d derived corridor-band values correct across the 30 cells" % (
        hits, total)


SUMMARY_FIGURES = [
    ("applications on the docket", r"applicat", r"issue|condition|reroute|refus|reliev|restrict"),
    ("issued outright", r"issue", r"condition"),
    ("issued with conditions", r"condition", None),
    ("rerouted on capacity", r"reroute|re-route|capacit|load reroute", r"clearance|height"),
    ("rerouted on clearance", r"clearance|height|overhead", None),
    ("refused", r"refus", None),
    ("withdrawn", r"withdraw|cancel", None),
    ("structures carrying a standing limit", r"standing|interim|restrict", r"applicat"),
]


def partial_oracle_amended_application_record(ctx):
    T, sub = ctx["T"], ctx["S"]
    weight_hits = 0
    for app in T["apps"]:
        entry = sub["disp_by_id"].get(app["application_id"])
        if entry and close(fnum(entry.get("gross_weight_t")), app["gross_weight_t"]):
            weight_hits += 1
    truth_withdrawn = {a["application_id"] for a in T["apps"] if a.get("withdrawn")}
    stated_withdrawn = {str(e.get("application_id", "")).strip() for e in sub["dispositions"]
                        if str(e.get("decision", "")).strip().upper() == "WITHDRAWN"}
    amended = [a["application_id"] for a in T["apps"]
               if abs(a["gross_weight_t"] - a["filed_gross_weight_t"]) > 0.051]
    amended_hits = sum(1 for aid in amended
                       if close(fnum((sub["disp_by_id"].get(aid) or {}).get("gross_weight_t")),
                                T["app_by_id"][aid]["gross_weight_t"]))
    return mean([frac(weight_hits, len(T["apps"])), set_f1(truth_withdrawn, stated_withdrawn),
                 frac(amended_hits, len(amended)) if amended else 1.0]), (
        "%d/%d dispositions carry the gross weight that stands after the correspondence; "
        "withdrawal F1 %.3f over the %d applications actually withdrawn; %d/%d of the amended "
        "weights were picked up rather than the filed figure"
        % (weight_hits, len(T["apps"]), set_f1(truth_withdrawn, stated_withdrawn),
           len(truth_withdrawn), amended_hits, len(amended)))


def partial_oracle_condition_trend(ctx):
    T, sub = ctx["T"], ctx["S"]
    pairs = []
    for structure in T["by_num"]:
        stated = reg_val(sub, structure, "condition_trend").strip().upper()
        pairs.append((T["trends"][structure], stated))
    score = macro_f1(pairs, CONDITION_TRENDS)
    exact = sum(1 for a, b in pairs if a == b)
    spread = Counter(T["trends"].values())
    return score, ("macro F1 %.3f over the three trends; %d/%d structures correct against the "
                   "2022 delivery (the evidence carries %d stable, %d improved, %d deteriorated)"
                   % (score, exact, len(pairs), spread["STABLE"], spread["IMPROVED"],
                      spread["DETERIORATED"]))


def partial_oracle_docket_summary_figures(ctx):
    T, sub = ctx["T"], ctx["S"]
    section = sub.get("letter_summary", "")
    if not section.strip():
        return 0.0, "no docket summary section to read"
    numbers = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", section)]
    if len(set(numbers)) > 20:
        return 0.0, ("the docket summary states %d distinct numbers; a summary that lists every "
                     "figure it can think of is not stating the docket's figures"
                     % len(set(numbers)))

    decisions = Counter(T["disp"][a["application_id"]]["decision"] for a in T["apps"])
    values = [len(T["apps"]), decisions["ISSUE"], decisions["ISSUE_WITH_CONDITIONS"],
              decisions["REROUTE_LOAD"], decisions["REROUTE_CLEARANCE"], decisions["REFUSE"],
              decisions["WITHDRAWN"], len(T["standing"])]

    clauses = [c.lower() for c in re.split(r"[.;,\n]|\band\b", section) if c.strip()]

    def stated_near(value, require, forbid):
        for clause in clauses:
            if not any(abs(float(x) - value) <= 1e-9
                       for x in re.findall(r"\d+(?:\.\d+)?", clause)):
                continue
            if re.search(require, clause) and not (forbid and re.search(forbid, clause)):
                return True
        return False

    hits = sum(1 for (_, require, forbid), value in zip(SUMMARY_FIGURES, values)
               if stated_near(value, require, forbid))

    spent = sum(fnum(r.get("engineer_weeks"), 0.0) or 0.0 for r in sub["programme_rows"])
    relieved = len({a for r in sub["programme_rows"]
                    for a in as_list(r.get("relieved_application_ids"))})
    own = 0
    if spent > 0 and stated_near(spent, r"week", None):
        own += 1
    if stated_near(relieved, r"reliev|freed|unlock", None):
        own += 1
    return mean([frac(hits, len(values)), frac(own, 2)]), (
        "%d/%d corpus figures and %d/2 programme figures are stated in the docket summary next "
        "to words naming which figure they are" % (hits, len(values), own))


STATIC_CHECKS = [static_required_artifacts_present,
                 static_register_shape_and_coverage,
                 static_dispositions_json_shape,
                 static_programme_and_refusal_shape,
                 static_ledger_shape,
                 static_chart_is_standalone_svg,
                 static_letter_section_inventory,
                 static_identifier_domain_integrity,
                 static_declared_ordering_and_derived_counts]
REWARD_HACKING_CHECKS = [reward_hacking_no_duplicate_or_phantom_rows,
                         reward_hacking_summary_reconciles_with_rows,
                         reward_hacking_register_is_derived_not_copied,
                         reward_hacking_letter_sections_are_case_specific,
                         reward_hacking_letter_figures_match_dispositions,
                         reward_hacking_letter_not_copied_source_prose,
                         reward_hacking_chart_geometry_follows_register,
                         reward_hacking_no_invented_codes_or_criteria,
                         reward_hacking_memo_citations_actually_govern]
PARTIAL_ORACLE_CHECKS = [partial_oracle_coded_facts_and_derate,
                         partial_oracle_standing_restrictions,
                         partial_oracle_effective_capacity,
                         partial_oracle_letter_states_case_facts,
                         partial_oracle_rerate_eligibility_and_yield,
                         partial_oracle_path_construction,
                         partial_oracle_controlling_structure,
                         partial_oracle_decision_classification,
                         partial_oracle_condition_codes,
                         partial_oracle_escort_class,
                         partial_oracle_blocking_structures_and_detour,
                         partial_oracle_refusal_register_reasons,
                         partial_oracle_rerating_programme_feasibility_and_saturation,
                         partial_oracle_corridor_ledger_values,
                         partial_oracle_docket_summary_figures,
                         partial_oracle_condition_trend,
                         partial_oracle_amended_application_record]
CHECKS = {"static_checks": STATIC_CHECKS,
          "reward_hacking_checks": REWARD_HACKING_CHECKS,
          "partial_oracle_checks": PARTIAL_ORACLE_CHECKS}


def write_error(out: Path, exc: BaseException) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "verifier_status.json").write_text(json.dumps(
        {"status": "verifier_error", "reward_is_graded": False,
         "error_type": type(exc).__name__, "error": str(exc)}, indent=2) + "\n", encoding="utf-8")
    (out / "judge_justification.txt").write_text(
        "VERIFIER_ERROR\n%s: %s\n" % (type(exc).__name__, exc), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-dir", default=os.environ.get("AGENT_DIR", "/logs/agent"))
    parser.add_argument("--input-dir", default=os.environ.get("INPUT_DIR", "/input_artifacts"))
    parser.add_argument("--out-dir", default=os.environ.get("VERIFIER_DIR", "/logs/verifier"))
    args = parser.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    try:
        (out / "reward.json").unlink()
    except FileNotFoundError:
        pass
    try:
        truth = build_truth(Path(args.input_dir))
        submission = load_submission(Path(args.agent_dir))
        ctx = {"T": truth, "S": submission, "agent": Path(args.agent_dir)}

        details, buckets = [], {}
        for bucket, functions in CHECKS.items():
            values = []
            for function in functions:
                try:
                    score, reason = function(ctx)
                    score = float(score)
                    if not 0.0 <= score <= 1.0:
                        raise ValueError(
                            "%s returned %r; every check must return a score inside [0, 1]"
                            % (function.__name__, score))
                except Exception as exc:
                    score, reason = 0.0, "check error %s: %s" % (type(exc).__name__, exc)
                values.append(score)
                row = {"bucket": bucket, "check_function": function.__name__,
                       "weight": 1, "score": round(score, 6), "reason": reason}
                details.append(row)
                print(json.dumps(row, sort_keys=True))
            buckets[bucket] = mean(values)

        reward = (buckets["static_checks"] + 2 * buckets["reward_hacking_checks"]
                  + 3 * buckets["partial_oracle_checks"]) / 6
        payload = {"reward": round(reward, 6),
                   "total_static_check_score": round(buckets["static_checks"], 6),
                   "total_reward_hacking_check_score": round(buckets["reward_hacking_checks"], 6),
                   "total_partial_oracle_check_score": round(buckets["partial_oracle_checks"], 6)}
        (out / "reward.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        (out / "verify_output.json").write_text(json.dumps(
            {"scores": payload, "checks": details}, indent=2) + "\n", encoding="utf-8")
        (out / "verifier_status.json").write_text(json.dumps(
            {"status": "ok", "reward_is_graded": True, "check_count": len(details),
             "bucket_check_counts": {k: len(v) for k, v in CHECKS.items()},
             "relief_optimum": truth["relief_optimum"],
             "submission_read_errors": submission["errors"]}, indent=2) + "\n", encoding="utf-8")

        audit = ["DETERMINISTIC AUDIT - no LLM, no network, no randomness, no clock read and no "
                 "answer-key file was used.",
                 "Every expectation was recomputed from the pinned NBI extract, the memo corpus, "
                 "the application table, the engineer roster and the rules file.",
                 "static_checks=%.6f (%d checks)" % (payload["total_static_check_score"],
                                                     len(STATIC_CHECKS)),
                 "reward_hacking_checks=%.6f (%d checks)" % (
                     payload["total_reward_hacking_check_score"], len(REWARD_HACKING_CHECKS)),
                 "partial_oracle_checks=%.6f (%d checks)" % (
                     payload["total_partial_oracle_check_score"], len(PARTIAL_ORACLE_CHECKS)),
                 "reward=%.6f; reward=(static + 2*reward_hacking + 3*partial_oracle)/6."
                 % payload["reward"], "", "Check detail:"]
        audit += ["- %s: %.6f - %s" % (d["check_function"], d["score"], d["reason"])
                  for d in details]
        text = "\n".join(audit) + "\n"
        (out / "judge_justification.txt").write_text(text, encoding="utf-8")
        Path(args.agent_dir).mkdir(parents=True, exist_ok=True)
        (Path(args.agent_dir) / "judge_justification.txt").write_text(text, encoding="utf-8")
        print(json.dumps(payload, sort_keys=True))
        return 0
    except Exception as exc:
        write_error(out, exc)
        try:
            Path(args.agent_dir).mkdir(parents=True, exist_ok=True)
            (Path(args.agent_dir) / "judge_justification.txt").write_text(
                "VERIFIER_ERROR\n%s: %s\n" % (type(exc).__name__, exc), encoding="utf-8")
        except Exception:
            pass
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
