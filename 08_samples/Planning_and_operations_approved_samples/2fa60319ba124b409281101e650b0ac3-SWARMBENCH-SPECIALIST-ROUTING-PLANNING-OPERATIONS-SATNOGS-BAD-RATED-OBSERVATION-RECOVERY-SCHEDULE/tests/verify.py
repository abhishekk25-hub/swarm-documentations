#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
import traceback
from collections import Counter, defaultdict, deque
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

DEFAULT_AGENT_DIR = Path("/logs/agent")
DEFAULT_INPUT_DIR = Path("/input_artifacts")
DEFAULT_OUT_DIR = Path("/logs/verifier")

RECOVERY_HORIZON = timedelta(hours=72)
BASE_MIN_ALTITUDE = 10.0

STATION_COLUMNS = [
    "ground_station", "station_name", "constraint_type", "window_start_utc",
    "window_end_utc", "min_elevation_deg", "embargoed_mode", "max_bookings",
    "evidence_quote",
]
SCHEDULE_COLUMNS = [
    "failure_id", "candidate_id", "norad_cat_id", "transmitter_uuid", "station_id",
    "start_utc", "end_utc", "frequency_hz", "max_altitude_deg", "delay_minutes",
    "tle_evidence_observation_id", "decision_note",
]
BACKLOG_COLUMNS = [
    "failure_id", "disposition", "candidate_id", "reason_code",
    "eligible_candidate_ids", "rationale",
]
IMPACT_COLUMNS = [
    "failure_id", "candidate_id", "station_id", "block_reason", "constraint_detail",
]

CONSTRAINT_TYPES = {
    "none", "booking_freeze", "maintenance_window", "min_elevation",
    "mode_embargo", "booking_cap",
}
BLOCK_REASONS = {"booking_freeze", "maintenance_window", "min_elevation", "mode_embargo"}
REASON_CODES = {"ASSIGNED", "NO_ELIGIBLE_CONTACT", "STATION_CONSTRAINED", "CONTACT_TAKEN"}
DISPOSITIONS = {"RECOVERED", "UNRECOVERED"}

REQUIRED_HEADINGS = [
    "recovery outcome", "station constraints", "control totals", "station load",
    "unrecovered backlog", "shift actions", "provenance and limitations",
]
CONTROL_KEYS = [
    "failures_total", "recovered_total", "unrecovered_total", "scheduled_contacts",
    "distinct_stations", "restricted_stations", "candidates_blocked",
]
DETAIL_COLUMNS = {
    "none": set(),
    "booking_freeze": set(),
    "maintenance_window": {"window_start_utc", "window_end_utc"},
    "min_elevation": {"min_elevation_deg"},
    "mode_embargo": {"embargoed_mode"},
    "booking_cap": {"max_bookings"},
}
ALL_DETAIL_COLUMNS = {"window_start_utc", "window_end_utc", "min_elevation_deg",
                      "embargoed_mode", "max_bookings"}

HANDOVER_MIN_WORDS = 1200
HANDOVER_MAX_WORDS = 2800
HANDOVER_MIN_CASES = 12

PLACEHOLDERS = re.compile(r"\b(?:tbd|todo|lorem ipsum|placeholder|fill this|your answer)\b", re.I)
WHOLE_CELL_PLACEHOLDERS = re.compile(r"^\s*(?:n/?a|none|unknown|not available)\s*[.!]?\s*$", re.I)


def text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def canon_int(value: Any) -> int | None:
    raw = text(value)
    if not re.fullmatch(r"[+-]?\d+(?:\.0+)?", raw):
        return None
    try:
        return int(float(raw))
    except Exception:
        return None


def canon_float(value: Any) -> float | None:
    try:
        number = float(text(value))
        return number if math.isfinite(number) else None
    except Exception:
        return None


def parse_time(value: Any) -> datetime | None:
    raw = text(value)
    if not raw:
        return None
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except Exception:
        return None
    return parsed if parsed.tzinfo is not None else None


def frac(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return min(1.0, max(0.0, numerator / denominator))


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    if not path.is_file():
        return [], []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def first_by_key(rows: list[dict], key) -> dict:
    out: dict = {}
    for row in rows:
        k = key(row)
        if k is not None and k not in out:
            out[k] = row
    return out


def split_ids(value: Any) -> list[int]:
    out = []
    for chunk in re.split(r"[|,;\s]+", text(value)):
        n = canon_int(chunk)
        if n is not None:
            out.append(n)
    return out


def norm_space(value: str) -> str:
    return " ".join(str(value).split())


AVAIL_RE = re.compile(
    r"##\s*Availability for the recovery window\s*\n+(.*?)(?=\n##\s|\Z)", re.S | re.I
)

DECLARATION_KEY = "station_declarations.json"


def availability_section(note: str) -> str:
    match = AVAIL_RE.search(note)
    return match.group(1).strip() if match else ""


def load_declaration_key(tests_dir: Path) -> dict[int, dict[str, Any]]:
    raw = json.loads((tests_dir / DECLARATION_KEY).read_text(encoding="utf-8"))
    return {int(gs): entry for gs, entry in raw.items()}


def _declaration_blocks(candidate: dict, rule: dict[str, str]) -> bool:
    kind = rule["constraint_type"]
    if kind == "booking_freeze":
        return True
    if kind == "maintenance_window":
        start, end = parse_time(rule["window_start_utc"]), parse_time(rule["window_end_utc"])
        cstart, cend = parse_time(candidate["start"]), parse_time(candidate["end"])
        if None in (start, end, cstart, cend):
            return False
        return cstart < end and cend > start
    if kind == "min_elevation":
        limit = canon_float(rule["min_elevation_deg"])
        altitude = canon_float(candidate["max_altitude"])
        if limit is None or altitude is None:
            return False
        return altitude < limit
    if kind == "mode_embargo":
        return text(candidate.get("transmitter_mode")) == rule["embargoed_mode"]
    return False


BLOCK_PRECEDENCE = ["booking_freeze", "maintenance_window", "min_elevation", "mode_embargo"]


def candidate_blocked_by(candidate: dict, rules: list[dict[str, str]]) -> str | None:
    hits = {r["constraint_type"] for r in rules if _declaration_blocks(candidate, r)}
    for kind in BLOCK_PRECEDENCE:
        if kind in hits:
            return kind
    return None


def baseline_eligible(failure: dict, candidate: dict) -> bool:
    if text(candidate.get("status")) != "good":
        return False
    if candidate.get("norad_cat_id") != failure.get("norad_cat_id"):
        return False
    if text(candidate.get("transmitter_uuid")) != text(failure.get("transmitter_uuid")):
        return False
    if candidate.get("observation_frequency") != failure.get("observation_frequency"):
        return False
    if text(candidate.get("transmitter_status")) != "active":
        return False
    altitude = canon_float(candidate.get("max_altitude"))
    if altitude is None or altitude < BASE_MIN_ALTITUDE:
        return False
    fend = parse_time(failure.get("end"))
    cstart = parse_time(candidate.get("start"))
    if fend is None or cstart is None:
        return False
    return fend < cstart <= fend + RECOVERY_HORIZON


class MinCostFlow:

    def __init__(self) -> None:
        self.graph: dict[str, list[list]] = defaultdict(list)

    def add_edge(self, u: str, v: str, capacity: int, cost: int) -> None:
        self.graph[u].append([v, capacity, cost, len(self.graph[v])])
        self.graph[v].append([u, 0, -cost, len(self.graph[u]) - 1])

    def solve(self, source: str, sink: str) -> tuple[int, int]:
        flow = cost = 0
        while True:
            dist: dict[str, float] = {source: 0}
            in_queue = {source}
            prev: dict[str, tuple[str, int]] = {}
            queue = deque([source])
            while queue:
                u = queue.popleft()
                in_queue.discard(u)
                for idx, edge in enumerate(self.graph[u]):
                    v, cap, w, _ = edge
                    if cap <= 0:
                        continue
                    nd = dist[u] + w
                    if nd < dist.get(v, float("inf")) - 1e-9:
                        dist[v] = nd
                        prev[v] = (u, idx)
                        if v not in in_queue:
                            in_queue.add(v)
                            queue.append(v)
            if sink not in dist:
                break
            push = float("inf")
            node = sink
            while node != source:
                u, idx = prev[node]
                push = min(push, self.graph[u][idx][1])
                node = u
            node = sink
            while node != source:
                u, idx = prev[node]
                edge = self.graph[u][idx]
                edge[1] -= push
                self.graph[edge[0]][edge[3]][1] += push
                cost += push * edge[2]
                node = u
            flow += push
        return flow, cost


def _flow_network(ctx: dict[str, Any], eligibility: dict[int, list[int]],
                  caps: dict[int, int], limit: int | None = None) -> tuple[MinCostFlow, str, str]:
    net = MinCostFlow()
    src, gate, sink = "__src__", "__gate__", "__sink__"
    total = sum(len(v) for v in eligibility.values()) + len(ctx["failures"]) + 1
    net.add_edge(src, gate, limit if limit is not None else total, 0)
    used: set[int] = set()
    for failure_id, candidate_ids in eligibility.items():
        if not candidate_ids:
            continue
        fnode = f"f:{failure_id}"
        net.add_edge(gate, fnode, 1, 0)
        for candidate_id in candidate_ids:
            net.add_edge(fnode, f"c:{candidate_id}", 1,
                         ctx["delay_seconds"][(failure_id, candidate_id)])
            used.add(candidate_id)
    stations = set()
    for candidate_id in used:
        station = ctx["candidate_by_id"][candidate_id]["ground_station"]
        net.add_edge(f"c:{candidate_id}", f"s:{station}", 1, 0)
        stations.add(station)
    for station in stations:
        net.add_edge(f"s:{station}", sink, caps.get(station, total), 0)
    return net, src, sink


def optimum(ctx: dict[str, Any], eligibility: dict[int, list[int]],
            caps: dict[int, int]) -> tuple[int, int]:
    net, src, sink = _flow_network(ctx, eligibility, caps)
    return net.solve(src, sink)


def min_delay_at(ctx: dict[str, Any], size: int, eligibility: dict[int, list[int]],
                 caps: dict[int, int]) -> int | None:
    if size <= 0:
        return 0
    net, src, sink = _flow_network(ctx, eligibility, caps, limit=size)
    flow, cost = net.solve(src, sink)
    return cost if flow == size else None


def read_context(agent_dir: Path, input_dir: Path,
                 tests_dir: Path | None = None) -> dict[str, Any]:
    ctx: dict[str, Any] = {"agent_dir": agent_dir, "input_dir": input_dir,
                           "tests_dir": tests_dir or Path(__file__).resolve().parent}

    failures = load_json(input_dir / "bad_rated_observations.json")["records"]
    candidates = load_json(input_dir / "candidate_observations.json")["records"]
    stations = load_json(input_dir / "stations.json")["records"]
    tle = load_json(input_dir / "tle_snapshot.json")["records"]

    ctx["failures"] = failures
    ctx["candidates"] = candidates
    ctx["stations"] = stations
    ctx["failure_by_id"] = {r["id"]: r for r in failures}
    ctx["candidate_by_id"] = {r["id"]: r for r in candidates}
    ctx["station_by_id"] = {r["ground_station"]: r for r in stations}
    ctx["tle_by_id"] = {r["evidence_observation_id"]: r for r in tle}

    notes_dir = input_dir / "station_operations"
    key = load_declaration_key(ctx["tests_dir"])
    true_constraints: dict[int, list[dict[str, str]]] = {}
    availability: dict[int, str] = {}
    evidence_sentences: dict[int, dict[str, str]] = {}
    clear_sentences: dict[int, list[str]] = {}
    for station in stations:
        gs = station["ground_station"]
        path = notes_dir / f"station_{gs}.md"
        raw = path.read_text(encoding="utf-8") if path.is_file() else ""
        entry = key.get(gs, {"declarations": [], "clear_sentences": []})
        true_constraints[gs] = entry["declarations"]
        evidence_sentences[gs] = {d["constraint_type"]: norm_space(d["evidence_sentence"])
                                  for d in entry["declarations"]}
        clear_sentences[gs] = [norm_space(c) for c in entry.get("clear_sentences", [])]
        availability[gs] = norm_space(availability_section(raw))
    ctx["evidence_sentences"] = evidence_sentences
    ctx["clear_sentences"] = clear_sentences
    ctx["true_constraints"] = true_constraints
    ctx["availability"] = availability
    ctx["station_caps"] = {
        gs: int(r["max_bookings"])
        for gs, rules in true_constraints.items()
        for r in rules
        if r["constraint_type"] == "booking_cap" and r["max_bookings"]
    }

    baseline: dict[int, list[int]] = {}
    blocked: dict[int, dict[int, str]] = {}
    eligibility: dict[int, list[int]] = {}
    delay_seconds: dict[tuple[int, int], int] = {}
    for failure in failures:
        fid = failure["id"]
        base, live, gone = [], [], {}
        fend = parse_time(failure["end"])
        for candidate in candidates:
            if not baseline_eligible(failure, candidate):
                continue
            cid = candidate["id"]
            base.append(cid)
            delay_seconds[(fid, cid)] = int(
                (parse_time(candidate["start"]) - fend).total_seconds()
            )
            reason = candidate_blocked_by(
                candidate, true_constraints[candidate["ground_station"]]
            )
            if reason:
                gone[cid] = reason
            else:
                live.append(cid)
        baseline[fid] = sorted(base)
        blocked[fid] = gone
        eligibility[fid] = sorted(live)
    ctx["baseline"] = baseline
    ctx["blocked"] = blocked
    ctx["eligibility"] = eligibility
    ctx["delay_seconds"] = delay_seconds

    best_size, best_cost = optimum(ctx, eligibility, ctx["station_caps"])
    ctx["optimal_size"] = best_size
    ctx["optimal_cost"] = best_cost

    ctx["true_disposition"] = {}
    for failure in failures:
        fid = failure["id"]
        if not baseline[fid]:
            ctx["true_disposition"][fid] = "NO_ELIGIBLE_CONTACT"
        elif not eligibility[fid]:
            ctx["true_disposition"][fid] = "STATION_CONSTRAINED"
        else:
            ctx["true_disposition"][fid] = "RECOVERABLE"

    ctx["station_path"] = agent_dir / "station_constraints.csv"
    ctx["schedule_path"] = agent_dir / "recovery_schedule.csv"
    ctx["backlog_path"] = agent_dir / "backlog_disposition.csv"
    ctx["impact_path"] = agent_dir / "constraint_impact.csv"
    ctx["handover_path"] = agent_dir / "operations_handover.md"

    ctx["station_rows"], ctx["station_cols"] = load_csv(ctx["station_path"])
    ctx["schedule_rows"], ctx["schedule_cols"] = load_csv(ctx["schedule_path"])
    ctx["backlog_rows"], ctx["backlog_cols"] = load_csv(ctx["backlog_path"])
    ctx["impact_rows"], ctx["impact_cols"] = load_csv(ctx["impact_path"])
    resolve_columns(ctx["station_rows"], STATION_ALIASES)
    resolve_columns(ctx["schedule_rows"], SCHEDULE_ALIASES)
    resolve_columns(ctx["backlog_rows"], BACKLOG_ALIASES)
    resolve_columns(ctx["impact_rows"], IMPACT_ALIASES)
    ctx["handover"] = (
        ctx["handover_path"].read_text(encoding="utf-8", errors="replace")
        if ctx["handover_path"].is_file() else ""
    )

    declared: dict[int, list[dict[str, str]]] = defaultdict(list)
    for row in ctx["station_rows"]:
        gs = canon_int(row.get("ground_station"))
        kind = text(row.get("constraint_type"))
        if gs is None or kind not in CONSTRAINT_TYPES or kind == "none":
            continue
        declared[gs].append({
            "constraint_type": kind,
            "window_start_utc": text(row.get("window_start_utc")),
            "window_end_utc": text(row.get("window_end_utc")),
            "min_elevation_deg": text(row.get("min_elevation_deg")),
            "embargoed_mode": text(row.get("embargoed_mode")),
            "max_bookings": text(row.get("max_bookings")),
        })
    ctx["declared_constraints"] = declared
    ctx["declared_caps"] = {
        gs: canon_int(r["max_bookings"])
        for gs, rules in declared.items()
        for r in rules
        if r["constraint_type"] == "booking_cap" and canon_int(r["max_bookings"]) is not None
    }
    declared_blocked: dict[int, dict[int, str]] = {}
    declared_eligibility: dict[int, list[int]] = {}
    for failure in failures:
        fid = failure["id"]
        live, gone = [], {}
        for candidate in candidates:
            if not baseline_eligible(failure, candidate):
                continue
            reason = candidate_blocked_by(candidate, declared.get(candidate["ground_station"], []))
            if reason:
                gone[candidate["id"]] = reason
            else:
                live.append(candidate["id"])
        declared_blocked[fid] = gone
        declared_eligibility[fid] = sorted(live)
    ctx["declared_blocked"] = declared_blocked
    ctx["declared_eligibility"] = declared_eligibility
    d_size, d_cost = optimum(ctx, declared_eligibility, ctx["declared_caps"])
    ctx["declared_optimal_size"] = d_size
    ctx["declared_optimal_cost"] = d_cost
    ctx["declared_disposition"] = {}
    for failure in failures:
        fid = failure["id"]
        if not baseline[fid]:
            ctx["declared_disposition"][fid] = "NO_ELIGIBLE_CONTACT"
        elif not declared_eligibility[fid]:
            ctx["declared_disposition"][fid] = "STATION_CONSTRAINED"
        else:
            ctx["declared_disposition"][fid] = "RECOVERABLE"

    released: dict[int, int] = {}
    for row in ctx["schedule_rows"]:
        fid, cid = canon_int(row.get("failure_id")), canon_int(row.get("candidate_id"))
        if fid is not None and cid is not None and fid not in released:
            released[fid] = cid
    ctx["released"] = released
    return ctx


STATION_ALIASES = {
    "ground_station": ("station_id", "station", "gs", "ground_station_id"),
}
SCHEDULE_ALIASES = {
    "failure_id": ("backlog_case_id", "bad_observation_id", "case_id", "bad_case_id"),
    "candidate_id": ("candidate_contact_id", "assigned_candidate_id", "matched_contact_id",
                     "candidate_observation_id"),
    "station_id": ("ground_station", "station"),
    "start_utc": ("start",),
    "end_utc": ("end",),
    "frequency_hz": ("observation_frequency", "frequency"),
    "max_altitude_deg": ("max_altitude",),
    "tle_evidence_observation_id": ("tle_observation_id", "tle_evidence_id"),
}
BACKLOG_ALIASES = {
    "failure_id": ("backlog_case_id", "bad_observation_id", "case_id", "bad_case_id"),
    "candidate_id": ("matched_contact_id", "assigned_candidate_id", "candidate_contact_id"),
    "reason_code": ("disposition_reason", "reason"),
    "eligible_candidate_ids": ("eligible_candidates", "cleared_candidate_ids"),
    "rationale": ("justification",),
}
IMPACT_ALIASES = {
    "failure_id": ("backlog_case_id", "bad_observation_id", "case_id"),
    "candidate_id": ("candidate_contact_id", "blocked_candidate_id",
                     "candidate_observation_id"),
    "station_id": ("ground_station", "station"),
    "block_reason": ("reason_code", "reason"),
    "constraint_detail": ("impact_description", "detail"),
}


def resolve_columns(rows: list[dict[str, str]],
                    aliases: dict[str, tuple[str, ...]]) -> list[dict[str, str]]:
    if not rows:
        return rows
    present = set(rows[0].keys())
    mapping = {}
    for canonical, options in aliases.items():
        if canonical in present:
            continue
        for option in options:
            if option in present:
                mapping[canonical] = option
                break
    if not mapping:
        return rows
    for row in rows:
        for canonical, source in mapping.items():
            row[canonical] = row.get(source, "")
    return rows


def submitted_station_map(ctx: dict[str, Any]) -> dict[int, list[dict[str, str]]]:
    out: dict[int, list[dict[str, str]]] = defaultdict(list)
    for row in ctx["station_rows"]:
        gs = canon_int(row.get("ground_station"))
        if gs is not None:
            out[gs].append(row)
    return dict(out)


def submitted_declaration_pairs(ctx: dict[str, Any]) -> set[tuple[int, str]]:
    pairs = set()
    for row in ctx["station_rows"]:
        gs = canon_int(row.get("ground_station"))
        kind = text(row.get("constraint_type"))
        if gs is not None and kind and kind != "none":
            pairs.add((gs, kind))
    return pairs


def true_declaration_pairs(ctx: dict[str, Any]) -> set[tuple[int, str]]:
    return {(gs, r["constraint_type"])
            for gs, rules in ctx["true_constraints"].items() for r in rules}


def check_deliverables_present(ctx):
    paths = [ctx["station_path"], ctx["schedule_path"], ctx["backlog_path"],
             ctx["impact_path"], ctx["handover_path"]]
    ok = [p.is_file() and p.stat().st_size > 200 for p in paths]
    return mean([float(x) for x in ok]), f"{sum(ok)}/{len(ok)} declared deliverables exist and are non-trivial"


def check_csv_schema_and_vocabularies(ctx):
    schema = [
        float(ctx["station_cols"] == STATION_COLUMNS),
        float(ctx["schedule_cols"] == SCHEDULE_COLUMNS),
        float(ctx["backlog_cols"] == BACKLOG_COLUMNS),
        float(ctx["impact_cols"] == IMPACT_COLUMNS),
    ]
    vocab = [
        mean([float(text(r.get("constraint_type")) in CONSTRAINT_TYPES) for r in ctx["station_rows"]]) if ctx["station_rows"] else 0.0,
        mean([float(text(r.get("reason_code")) in REASON_CODES) for r in ctx["backlog_rows"]]) if ctx["backlog_rows"] else 0.0,
        mean([float(text(r.get("disposition")) in DISPOSITIONS) for r in ctx["backlog_rows"]]) if ctx["backlog_rows"] else 0.0,
        mean([float(text(r.get("block_reason")) in BLOCK_REASONS) for r in ctx["impact_rows"]]) if ctx["impact_rows"] else 0.0,
    ]
    return mean(schema + vocab), f"headers={[int(x) for x in schema]}, vocabularies={[round(v,3) for v in vocab]}"


def check_typed_fields_parse(ctx):
    units: list[float] = []
    for row in ctx["schedule_rows"]:
        units += [
            float(canon_int(row.get("failure_id")) is not None),
            float(canon_int(row.get("candidate_id")) is not None),
            float(parse_time(row.get("start_utc")) is not None),
            float(parse_time(row.get("end_utc")) is not None),
            float(canon_float(row.get("max_altitude_deg")) is not None),
            float(canon_float(row.get("delay_minutes")) is not None),
        ]
    for row in ctx["station_rows"]:
        kind = text(row.get("constraint_type"))
        if kind == "maintenance_window":
            units += [float(parse_time(row.get("window_start_utc")) is not None),
                      float(parse_time(row.get("window_end_utc")) is not None)]
        elif kind == "min_elevation":
            units.append(float(canon_float(row.get("min_elevation_deg")) is not None))
        elif kind == "booking_cap":
            units.append(float(canon_int(row.get("max_bookings")) is not None))
    return mean(units), f"{sum(units):.0f}/{len(units)} typed fields parse" if units else "no typed fields"


def check_station_roster_coverage(ctx):
    expected = {s["ground_station"] for s in ctx["stations"]}
    seen = Counter(canon_int(r.get("ground_station")) for r in ctx["station_rows"])
    covered = sum(1 for gs in expected if seen.get(gs, 0) >= 1)
    dupes = Counter()
    for row in ctx["station_rows"]:
        dupes[(canon_int(row.get("ground_station")), text(row.get("constraint_type")))] += 1
    repeated = sum(1 for k, n in dupes.items() if n > 1)
    return mean([frac(covered, len(expected)), 1.0 if not repeated else 0.0]),         f"{covered}/{len(expected)} stations present; {repeated} repeated (station, declaration) rows"


def check_declaration_detail_columns(ctx):
    units: list[float] = []
    for row in ctx["station_rows"]:
        kind = text(row.get("constraint_type"))
        if kind not in DETAIL_COLUMNS:
            units.append(0.0)
            continue
        needed = DETAIL_COLUMNS[kind]
        filled_ok = all(text(row.get(col)) for col in needed)
        blank_ok = all(not text(row.get(col)) for col in ALL_DETAIL_COLUMNS - needed)
        units.append(float(filled_ok and blank_ok))
    return mean(units), f"{sum(units):.0f}/{len(units)} rows fill only their applicable detail columns" if units else "no station rows"


def check_backlog_roster_coverage(ctx):
    expected = {f["id"] for f in ctx["failures"]}
    seen = Counter(canon_int(r.get("failure_id")) for r in ctx["backlog_rows"])
    exactly_once = sum(1 for fid in expected if seen.get(fid, 0) == 1)
    return frac(exactly_once, len(expected)), f"{exactly_once}/{len(expected)} failures have exactly one backlog row"


def check_handover_shape(ctx):
    body = ctx["handover"]
    lower = body.lower()
    found = [re.search(r"^#{1,6}\s*" + re.escape(h), lower, re.M) for h in REQUIRED_HEADINGS]
    headings = mean([float(m is not None) for m in found])
    positions = [m.start() for m in found if m is not None]
    ordered = 1.0 if len(positions) < 2 else float(
        all(a < b for a, b in zip(positions, positions[1:])))
    words = len(body.split())
    in_range = float(HANDOVER_MIN_WORDS <= words <= HANDOVER_MAX_WORDS)
    control = mean([float(re.search(r"\|\s*" + re.escape(k) + r"\s*\|", lower) is not None)
                    for k in CONTROL_KEYS])
    load_table = float(re.search(r"\|\s*station_id\s*\|\s*scheduled_contacts\s*\|", lower) is not None)
    return mean([headings, ordered, in_range, control, load_table]), \
        (f"headings={headings:.3f}, in_declared_order={int(ordered)}, words={words}, "
         f"control_keys={control:.3f}, load_table={int(load_table)}")


def check_no_duplicate_or_invented_rows(ctx):
    units: list[float] = []
    known_f = {f["id"] for f in ctx["failures"]}
    known_c = {c["id"] for c in ctx["candidates"]}
    known_s = {s["ground_station"] for s in ctx["stations"]}

    seen: set[tuple[int, int]] = set()
    for row in ctx["schedule_rows"]:
        fid, cid = canon_int(row.get("failure_id")), canon_int(row.get("candidate_id"))
        key = (fid, cid)
        units.append(float(fid in known_f and cid in known_c and key not in seen))
        seen.add(key)
    true_name = {s["ground_station"]: norm_space(str(s.get("station_name", ""))).lower()
                 for s in ctx["stations"]}
    seen_s: set[tuple[int, str]] = set()
    for row in ctx["station_rows"]:
        gs = canon_int(row.get("ground_station"))
        key = (gs, text(row.get("constraint_type")))
        name_ok = gs in true_name and norm_space(text(row.get("station_name"))).lower() == true_name[gs]
        units.append(float(gs in known_s and key not in seen_s and name_ok))
        seen_s.add(key)
    seen_i: set[tuple[int, int]] = set()
    for row in ctx["impact_rows"]:
        fid, cid = canon_int(row.get("failure_id")), canon_int(row.get("candidate_id"))
        key = (fid, cid)
        units.append(float(fid in known_f and cid in known_c and key not in seen_i))
        seen_i.add(key)
    return mean(units), f"{sum(units):.0f}/{len(units)} submitted keys are unique and known"


def check_no_candidate_reuse(ctx):
    counts = Counter(canon_int(r.get("candidate_id")) for r in ctx["schedule_rows"])
    counts.pop(None, None)
    if not counts:
        return 0.0, "no schedule rows"
    once = sum(1 for cid, n in counts.items() if n == 1 and cid in ctx["candidate_by_id"])
    return frac(once, len(counts)), f"{once}/{len(counts)} scheduled candidates are known and used exactly once"


def check_station_booking_caps_respected(ctx):
    load = Counter()
    for row in ctx["schedule_rows"]:
        gs = canon_int(row.get("station_id"))
        if gs is not None:
            load[gs] += 1
    capped = ctx["declared_caps"]
    if not capped:
        return 1.0, "no station declared a booking cap"
    ok = sum(1 for gs, cap in capped.items() if load.get(gs, 0) <= cap)
    over = {gs: (load[gs], cap) for gs, cap in capped.items() if load.get(gs, 0) > cap}
    return frac(ok, len(capped)), f"{ok}/{len(capped)} capped stations within allowance; over={over}"


def check_evidence_quotes_are_verbatim(ctx):
    units: list[float] = []
    for row in ctx["station_rows"]:
        gs = canon_int(row.get("ground_station"))
        quote = norm_space(text(row.get("evidence_quote")))
        section = ctx["availability"].get(gs, "")
        units.append(float(len(quote) >= 40 and bool(section) and quote in section))
    return mean(units), f"{sum(units):.0f}/{len(units)} evidence quotes are verbatim from that station's availability statement" if units else "no station rows"


def check_evidence_quotes_carry_the_detail(ctx):
    submitted = submitted_station_map(ctx)
    units: list[float] = []
    for gs, rules in ctx["declared_constraints"].items():
        rows = submitted.get(gs, [])
        if not rules:
            row = next((r for r in rows if text(r.get("constraint_type")) == "none"), None)
            if row is None:
                continue
            quote = norm_space(text(row.get("evidence_quote")))
            clear = ctx["clear_sentences"].get(gs, [])
            units.append(float(bool(quote) and any(quote in c for c in clear)))
            continue
        for rule in rules:
            kind = rule["constraint_type"]
            row = next((r for r in rows if text(r.get("constraint_type")) == kind), None)
            if row is None:
                continue
            quote = norm_space(text(row.get("evidence_quote")))
            sentence = ctx["evidence_sentences"].get(gs, {}).get(kind, "")
            units.append(float(bool(quote) and bool(sentence) and quote in sentence))
    return mean(units), f"{sum(units):.0f}/{len(units)} evidence quotes come from the sentence stating that row's declaration" if units else "no declarations reported"


def check_impact_rows_are_real(ctx):
    units: list[float] = []
    rows = first_by_key(ctx["impact_rows"],
                        lambda r: (canon_int(r.get("failure_id")), canon_int(r.get("candidate_id"))))
    declared = ctx["declared_constraints"]
    for (fid, cid), row in sorted(rows.items(), key=lambda kv: (kv[0][0] or 0, kv[0][1] or 0)):
        reason = text(row.get("block_reason"))
        truth = ctx["declared_blocked"].get(fid, {})
        attributed = cid in truth and truth[cid] == reason
        candidate = ctx["candidate_by_id"].get(cid)
        station_ok = candidate is not None and canon_int(row.get("station_id")) == candidate["ground_station"]
        detail = text(row.get("constraint_detail"))
        detail_ok = bool(detail) and not WHOLE_CELL_PLACEHOLDERS.fullmatch(detail)
        if detail_ok and candidate is not None:
            operative = [v for r in declared.get(candidate["ground_station"], [])
                         if r["constraint_type"] == reason
                         for v in (r.get("window_start_utc"), r.get("window_end_utc"),
                                   r.get("min_elevation_deg"), r.get("embargoed_mode"))
                         if text(v)]
            if operative:
                detail_ok = any(norm_space(str(v)).lower() in norm_space(detail).lower()
                                for v in operative)
        units.append(mean([float(attributed), float(station_ok), float(detail_ok)]))
    return mean(units), (f"{sum(units):.1f}/{len(units)} impact rows name a real, correctly-attributed "
                         f"removal with the right station and an operative detail" if units else "no impact rows")


def check_no_hollow_schedule(ctx):
    units: list[float] = []
    rows = first_by_key(ctx["schedule_rows"],
                        lambda r: (canon_int(r.get("failure_id")), canon_int(r.get("candidate_id"))))
    for (fid, cid), row in sorted(rows.items(), key=lambda kv: (kv[0][0] or 0, kv[0][1] or 0)):
        filled = [text(row.get(col)) for col in SCHEDULE_COLUMNS]
        populated = all(v for v in filled) and not any(
            WHOLE_CELL_PLACEHOLDERS.fullmatch(v) for v in filled)
        candidate = ctx["candidate_by_id"].get(cid)
        failure = ctx["failure_by_id"].get(fid)
        grounded = candidate is not None and canon_int(row.get("norad_cat_id")) == candidate["norad_cat_id"]
        if grounded and failure is not None:
            gap = (parse_time(candidate["start"]) - parse_time(failure["end"])).total_seconds()
            claimed = canon_float(row.get("delay_minutes"))
            grounded = claimed is not None and abs(claimed - gap / 60.0) <= 0.02
        units.append(float(populated and grounded))
    return mean(units), (f"{sum(units):.0f}/{len(units)} distinct schedule rows are populated and "
                         f"match the snapshot" if units else "no schedule rows")


def _skeleton(note: str) -> str:
    tokens = ["#" if any(ch.isdigit() for ch in tok) else tok
              for tok in note.lower().split()]
    masked = re.sub(r"[^a-z# ]+", " ", " ".join(tokens))
    return re.sub(r"(?:# )+#?", "# ", " ".join(masked.split())).strip()


def _diversity(notes: list[str]) -> list[float]:
    if not notes:
        return []
    counts = Counter(_skeleton(n) for n in notes)
    ceiling = max(2, (len(notes) + 1) // 2)
    return [float(counts[_skeleton(n)] <= ceiling) for n in notes]


def _row_specific(note: str, tokens: list[str]) -> bool:
    if len(note.strip()) < 25 or PLACEHOLDERS.search(note) or WHOLE_CELL_PLACEHOLDERS.fullmatch(note.strip()):
        return False
    lower = note.lower()
    hits = sum(1 for t in tokens if t and re.search(
        r"(?<![a-z0-9])" + re.escape(str(t).lower()) + r"(?![a-z0-9])", lower))
    return hits >= 2


def check_decision_notes_are_row_specific(ctx):
    units: list[float] = []
    rows = first_by_key(ctx["schedule_rows"],
                        lambda r: (canon_int(r.get("failure_id")), canon_int(r.get("candidate_id"))))
    for (_fid, cid), row in sorted(rows.items(), key=lambda kv: (kv[0][0] or 0, kv[0][1] or 0)):
        candidate = ctx["candidate_by_id"].get(cid)
        if candidate is None:
            units.append(0.0)
            continue
        tokens = [cid, canon_int(row.get("failure_id")), candidate["norad_cat_id"],
                  candidate["ground_station"], candidate["max_altitude"]]
        units.append(float(_row_specific(text(row.get("decision_note")), [str(t) for t in tokens])))
    diversity = _diversity([text(r.get("decision_note")) for r in ctx["schedule_rows"]])
    combined = [a * b for a, b in zip(units, diversity)] if diversity else units
    return mean(combined), f"{sum(combined):.0f}/{len(combined)} decision notes cite two row-true values in non-templated wording" if combined else "no schedule rows"


def check_backlog_rationales_are_case_specific(ctx):
    units: list[float] = []
    for row in ctx["backlog_rows"]:
        fid = canon_int(row.get("failure_id"))
        failure = ctx["failure_by_id"].get(fid)
        if failure is None:
            units.append(0.0)
            continue
        tokens = [fid, failure["norad_cat_id"], failure["ground_station"],
                  failure["station_name"], failure["transmitter_uuid"],
                  len(ctx["declared_eligibility"].get(fid, []))]
        units.append(float(_row_specific(text(row.get("rationale")), [str(t) for t in tokens])))
    diversity = _diversity([text(r.get("rationale")) for r in ctx["backlog_rows"]])
    combined = [a * b for a, b in zip(units, diversity)] if diversity else units
    return mean(combined), f"{sum(combined):.0f}/{len(combined)} backlog rationales cite two case-true values in non-templated wording" if combined else "no backlog rows"


def check_notes_are_not_source_pasted(ctx):
    sections = [s for s in ctx["availability"].values() if s]
    units: list[float] = []
    for row in ctx["schedule_rows"]:
        note = norm_space(text(row.get("decision_note")))
        units.append(float(bool(note) and not any(note and note in s for s in sections)))
    for row in ctx["backlog_rows"]:
        note = norm_space(text(row.get("rationale")))
        units.append(float(bool(note) and not any(note and note in s for s in sections)))
    return mean(units), f"{sum(units):.0f}/{len(units)} authored notes are not pasted from the station notes" if units else "no authored notes"


def check_handover_uses_specific_cases(ctx):
    body = ctx["handover"]
    def prose_of(block: str) -> str:
        kept = [ln for ln in block.splitlines()
                if not re.match(r"\s*(?:[-*+]\s|\d+[.)]\s|\||#)", ln)]
        return " ".join(kept)

    blocks = [t for t in (prose_of(b) for b in re.split(r"\n\s*\n", body))
              if len(t.split()) >= 40]
    discussed = 0
    for failure in ctx["failures"]:
        fid = str(failure["id"])
        facts = [str(failure["norad_cat_id"]), str(failure["ground_station"]),
                 str(failure["station_name"]), str(failure["transmitter_uuid"])]
        for block in blocks:
            if not re.search(r"(?<!\d)" + fid + r"(?!\d)", block):
                continue
            if any(f and f in block for f in facts):
                discussed += 1
                break
    return frac(discussed, HANDOVER_MIN_CASES), f"{discussed} distinct failures discussed in a prose paragraph beside a true case fact; {HANDOVER_MIN_CASES} required"


def check_cross_artifact_reconciliation(ctx):
    units: list[float] = []
    backlog = {canon_int(r.get("failure_id")): r for r in ctx["backlog_rows"]}
    impact_pairs = defaultdict(set)
    for row in ctx["impact_rows"]:
        impact_pairs[canon_int(row.get("failure_id"))].add(canon_int(row.get("candidate_id")))
    for failure in ctx["failures"]:
        fid = failure["id"]
        row = backlog.get(fid)
        if row is None:
            units.append(0.0)
            continue
        code = text(row.get("reason_code"))
        disposition = text(row.get("disposition"))
        claimed = canon_int(row.get("candidate_id"))
        released = ctx["released"].get(fid)
        cleared = ctx["declared_eligibility"].get(fid, [])
        parts = [
            float((code == "ASSIGNED") == (released is not None)),
            float((disposition == "RECOVERED") == (code == "ASSIGNED")),
            float(claimed == released if released is not None else claimed is None),
            float(code != "STATION_CONSTRAINED" or bool(impact_pairs.get(fid))),
            float(code != "NO_ELIGIBLE_CONTACT" or not ctx["baseline"].get(fid)),
            float(bool(cleared) == bool(split_ids(row.get("eligible_candidate_ids")))),
        ]
        units.append(mean(parts))
    return mean(units), f"{sum(units):.1f}/{len(units)} cases reconcile across schedule, backlog and impact ledger"


def check_declaration_recall(ctx):
    expected = true_declaration_pairs(ctx)
    got = submitted_declaration_pairs(ctx)
    if not expected:
        return 1.0, "no station declares a binding constraint"
    found = len(expected & got)
    return frac(found, len(expected)), \
        f"{found}/{len(expected)} true station declarations recovered"


def check_declaration_precision(ctx):
    expected = true_declaration_pairs(ctx)
    got = submitted_declaration_pairs(ctx)
    if not got:
        return 0.0, "register claims no declarations at all"
    kept = len(expected & got)
    return frac(kept, len(got)), \
        f"{kept}/{len(got)} claimed declarations are genuine ({len(got - expected)} invented)"


def check_station_constraint_detail_accuracy(ctx):
    submitted = submitted_station_map(ctx)
    units: list[float] = []
    for gs, rules in ctx["true_constraints"].items():
        for rule in rules:
            kind = rule["constraint_type"]
            row = next((r for r in submitted.get(gs, [])
                        if text(r.get("constraint_type")) == kind), None)
            if row is None:
                units.append(0.0)
                continue
            if kind == "maintenance_window":
                units.append(float(
                    parse_time(row.get("window_start_utc")) == parse_time(rule["window_start_utc"])
                    and parse_time(row.get("window_end_utc")) == parse_time(rule["window_end_utc"])))
            elif kind == "min_elevation":
                units.append(float(canon_float(row.get("min_elevation_deg"))
                                   == canon_float(rule["min_elevation_deg"])))
            elif kind == "mode_embargo":
                units.append(float(text(row.get("embargoed_mode")) == rule["embargoed_mode"]))
            elif kind == "booking_cap":
                units.append(float(canon_int(row.get("max_bookings"))
                                   == canon_int(rule["max_bookings"])))
            else:
                units.append(1.0)
    return mean(units), f"{sum(units):.0f}/{len(units)} declarations carry the correct operative values" if units else "no declarations"


def check_schedule_rows_faithful(ctx):
    units: list[float] = []
    rows = first_by_key(ctx["schedule_rows"],
                        lambda r: (canon_int(r.get("failure_id")), canon_int(r.get("candidate_id"))))
    for (fid, cid), row in sorted(rows.items(), key=lambda kv: (kv[0][0] or 0, kv[0][1] or 0)):
        failure = ctx["failure_by_id"].get(fid)
        candidate = ctx["candidate_by_id"].get(cid)
        if candidate is None or failure is None:
            units.append(0.0)
            continue
        identity = [
            float(canon_int(row.get("norad_cat_id")) == candidate["norad_cat_id"]),
            float(text(row.get("transmitter_uuid")) == text(candidate["transmitter_uuid"])),
            float(canon_int(row.get("station_id")) == candidate["ground_station"]),
            float(parse_time(row.get("start_utc")) == parse_time(candidate["start"])),
            float(parse_time(row.get("end_utc")) == parse_time(candidate["end"])),
            float(canon_float(row.get("frequency_hz"))
                  == canon_float(candidate["observation_frequency"])),
        ]
        gap = (parse_time(candidate["start"]) - parse_time(failure["end"])).total_seconds()
        claimed = canon_float(row.get("delay_minutes"))
        record = ctx["tle_by_id"].get(canon_int(row.get("tle_evidence_observation_id")))
        units.append(mean(identity + [
            float(baseline_eligible(failure, candidate)),
            float(claimed is not None and abs(claimed - gap / 60.0) <= 0.02),
            float(record is not None and record["norad_cat_id"] == candidate["norad_cat_id"]),
        ]))
    return mean(units), f"{sum(units):.1f}/{len(units)} released rows faithfully describe a real, baseline-eligible candidate" if units else "no schedule rows"


def check_station_constraint_compliance(ctx):
    units: list[float] = []
    for row in ctx["schedule_rows"]:
        cid = canon_int(row.get("candidate_id"))
        candidate = ctx["candidate_by_id"].get(cid)
        if candidate is None:
            units.append(0.0)
            continue
        rules = ctx["declared_constraints"].get(candidate["ground_station"], [])
        units.append(float(candidate_blocked_by(candidate, rules) is None))
    return mean(units), f"{sum(units):.0f}/{len(units)} released rows are legal under the owning station's declaration" if units else "no schedule rows"


def check_eligible_candidate_lists(ctx):
    units: list[float] = []
    rows = first_by_key(ctx["backlog_rows"], lambda r: canon_int(r.get("failure_id")))
    for fid in sorted(ctx["declared_eligibility"]):
        row = rows.get(fid)
        units.append(0.0 if row is None else
                     float(sorted(set(split_ids(row.get("eligible_candidate_ids"))))
                           == ctx["declared_eligibility"][fid]))
    return mean(units), (f"{sum(units):.0f}/{len(units)} roster cases carry the exact "
                         f"station-cleared eligible set" if units else "no cases")


def check_constraint_impact_completeness(ctx):
    expected = {(fid, cid) for fid, m in ctx["declared_blocked"].items() for cid in m}
    got = {(canon_int(r.get("failure_id")), canon_int(r.get("candidate_id")))
           for r in ctx["impact_rows"]}
    if not expected:
        return 1.0, "no candidates are removed by station constraints"
    found = len(expected & got)
    spurious = len(got - expected)
    recall = frac(found, len(expected))
    precision = frac(found, len(got)) if got else 0.0
    return mean([recall, precision]), \
        f"{found}/{len(expected)} true removals reported, {spurious} spurious rows, precision={precision:.3f}"


def check_maximum_recovery_cardinality(ctx):
    valid = 0
    used: set[int] = set()
    load = Counter()
    for fid, cid in ctx["released"].items():
        if cid in ctx["declared_eligibility"].get(fid, []) and cid not in used:
            station = ctx["candidate_by_id"][cid]["ground_station"]
            if load[station] + 1 <= ctx["declared_caps"].get(station, len(ctx["candidates"])):
                load[station] += 1
                used.add(cid)
                valid += 1
    return frac(valid, ctx["declared_optimal_size"]), f"valid released assignments={valid}, optimum={ctx['optimal_size']}"


def check_minimum_delay_quality(ctx):
    pairs = []
    used: set[int] = set()
    load = Counter()
    for fid, cid in ctx["released"].items():
        if cid in ctx["declared_eligibility"].get(fid, []) and cid not in used:
            station = ctx["candidate_by_id"][cid]["ground_station"]
            if load[station] + 1 <= ctx["declared_caps"].get(station, len(ctx["candidates"])):
                load[station] += 1
                used.add(cid)
                pairs.append((fid, cid))
    if not pairs:
        return 0.0, "no valid released assignments"
    actual = sum(ctx["delay_seconds"][(f, c)] for f, c in pairs)
    best = min_delay_at(ctx, len(pairs), ctx["declared_eligibility"], ctx["declared_caps"])
    if best is None:
        return 0.0, f"no feasible assignment of size {len(pairs)}"
    if actual <= 0:
        return 1.0, "zero total delay"
    return frac(best, actual), f"actual delay={actual}s, best at cardinality {len(pairs)}={best}s"


def _contention_supported(ctx: dict[str, Any], failure_id: int) -> bool:
    cleared = ctx["declared_eligibility"].get(failure_id, [])
    if not cleared:
        return False
    taken = {cid for fid, cid in ctx["released"].items() if fid != failure_id}
    load = Counter()
    for row in ctx["schedule_rows"]:
        station = canon_int(row.get("station_id"))
        if station is not None:
            load[station] += 1
    for candidate_id in cleared:
        if candidate_id in taken:
            continue
        station = ctx["candidate_by_id"][candidate_id]["ground_station"]
        cap = ctx["declared_caps"].get(station)
        if cap is not None and load.get(station, 0) >= cap:
            continue
        return False
    return True


def check_disposition_reason_accuracy(ctx):
    units: list[float] = []
    rows = first_by_key(ctx["backlog_rows"], lambda r: canon_int(r.get("failure_id")))
    for fid in sorted(ctx["declared_disposition"]):
        row = rows.get(fid)
        if row is None:
            units.append(0.0)
            continue
        code = text(row.get("reason_code"))
        truth = ctx["declared_disposition"][fid]
        if truth == "RECOVERABLE":
            if code == "ASSIGNED":
                units.append(1.0)
            elif code == "CONTACT_TAKEN":
                units.append(float(_contention_supported(ctx, fid)))
            else:
                units.append(0.0)
        else:
            units.append(float(code == truth))
    return mean(units), f"{sum(units):.0f}/{len(units)} of the roster's cases carry a reason code matching the derived disposition" if units else "no cases"


def check_handover_control_totals(ctx):
    body = ctx["handover"]
    load = Counter()
    for row in ctx["schedule_rows"]:
        gs = canon_int(row.get("station_id"))
        if gs is not None:
            load[gs] += 1
    recovered = len(ctx["released"])
    expected = {
        "failures_total": len(ctx["failures"]),
        "recovered_total": recovered,
        "unrecovered_total": len(ctx["failures"]) - recovered,
        "scheduled_contacts": len(ctx["schedule_rows"]),
        "distinct_stations": len(load),
        "restricted_stations": sum(1 for rules in ctx["declared_constraints"].values() if rules),
        "candidates_blocked": sum(len(m) for m in ctx["declared_blocked"].values()),
    }
    units = []
    for key, value in expected.items():
        m = re.search(r"\|\s*" + re.escape(key) + r"\s*\|\s*([^|]+?)\s*\|", body, re.I)
        units.append(float(m is not None and canon_int(m.group(1)) == value))
    rows_ok = []
    for gs, count in load.items():
        m = re.search(r"\|\s*" + str(gs) + r"\s*\|\s*(\d+)\s*\|", body)
        rows_ok.append(float(m is not None and int(m.group(1)) == count))
    station_load = mean(rows_ok) if rows_ok else 0.0
    return mean(units + [station_load]), \
        f"control totals {sum(units):.0f}/{len(units)}; station-load rows {station_load:.3f}"


CITATION_STOPWORDS = {
    "satnogs", "network", "document", "documentation", "guide", "section", "page",
    "record", "records", "recovery", "window", "report", "reports", "provenance",
    "limitation", "limitations", "operator", "operators", "declaration", "declarations",
    "observation", "observations", "station", "stations", "schedule", "scheduled",
    "candidate", "candidates", "failure", "failures", "against", "between", "because",
    "therefore", "however", "including", "further", "should", "cannot", "exercise",
}


def _pdf_pages(ctx: dict[str, Any]) -> list[str]:
    if "pdf_pages" in ctx:
        return ctx["pdf_pages"]
    pages: list[str] = []
    path = ctx["input_dir"] / "satnogs_network_docs.pdf"
    try:
        from pypdf import PdfReader
        pages = [(p.extract_text() or "").lower() for p in PdfReader(str(path)).pages]
    except Exception:
        try:
            raw = path.read_bytes()
            pages = [""] * raw.count(b"/Type /Page") or []
        except Exception:
            pages = []
    ctx["pdf_pages"] = pages
    return pages


def check_provenance_citations(ctx):
    body = ctx["handover"]
    lower = body.lower()
    guide = float("observation ratings" in lower and "satnogs_operation_guide.html" in lower)
    cited = []
    for sentence in re.split(r"(?<=[.!?])\s+", lower):
        for m in re.finditer(r"page\s+(\d+)[^.]{0,80}satnogs_network_docs\.pdf"
                             r"|satnogs_network_docs\.pdf[^.]{0,80}page\s+(\d+)", sentence):
            cited.append((int(m.group(1) or m.group(2)), sentence))
    pages = _pdf_pages(ctx)
    if not cited or not pages:
        pdf = 0.0
    else:
        good = []
        for page, claim in cited:
            if not 1 <= page <= len(pages):
                good.append(0.0)
                continue
            content = pages[page - 1]
            tokens = {t for t in re.findall(r"[a-z]{6,}|\d{2,}", claim)
                      if t not in CITATION_STOPWORDS and t != str(page)}
            hits = sum(1 for t in tokens if t in content)
            good.append(float(hits >= 2))
        pdf = mean(good)
    declared = float(bool(re.search(
        r"operator declaration|not part of the public satnogs record|collected for this exercise",
        lower)))
    exercise = float(bool(re.search(r"exercise policy|72\s*hour|maximum-cardinality", lower)))
    return mean([guide, pdf, declared, exercise]), \
        (f"guide_citation={int(guide)}, pdf_pages_cited={[c for c, _ in cited]} of {len(pages)} "
         f"real pages -> {pdf:.2f}, declaration_caveat={int(declared)}, policy_caveat={int(exercise)}")


CHECKS: dict[str, list] = {
    "static_checks": [
        check_deliverables_present,
        check_csv_schema_and_vocabularies,
        check_typed_fields_parse,
        check_station_roster_coverage,
        check_declaration_detail_columns,
        check_backlog_roster_coverage,
        check_handover_shape,
    ],
    "reward_hacking_checks": [
        check_no_duplicate_or_invented_rows,
        check_no_candidate_reuse,
        check_station_booking_caps_respected,
        check_evidence_quotes_are_verbatim,
        check_evidence_quotes_carry_the_detail,
        check_impact_rows_are_real,
        check_no_hollow_schedule,
        check_decision_notes_are_row_specific,
        check_backlog_rationales_are_case_specific,
        check_notes_are_not_source_pasted,
        check_handover_uses_specific_cases,
        check_cross_artifact_reconciliation,
    ],
    "partial_oracle_checks": [
        check_declaration_recall,
        check_declaration_precision,
        check_station_constraint_detail_accuracy,
        check_schedule_rows_faithful,
        check_station_constraint_compliance,
        check_eligible_candidate_lists,
        check_constraint_impact_completeness,
        check_maximum_recovery_cardinality,
        check_minimum_delay_quality,
        check_disposition_reason_accuracy,
        check_handover_control_totals,
        check_provenance_citations,
    ],
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-dir", default=str(DEFAULT_AGENT_DIR))
    parser.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    agent_dir, input_dir = Path(args.agent_dir), Path(args.input_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stale = out_dir / "reward.json"
    if stale.exists():
        stale.unlink()

    try:
        ctx = read_context(agent_dir, input_dir, Path(__file__).resolve().parent)
    except Exception as exc:
        (out_dir / "verifier_status.json").write_text(json.dumps(
            {"status": "verifier_error", "reward_is_graded": False,
             "error_type": type(exc).__name__, "error": str(exc)}, indent=2) + "\n",
            encoding="utf-8")
        traceback.print_exc()
        return 1

    details = []
    bucket_scores: dict[str, float] = {}
    for bucket, funcs in CHECKS.items():
        values = []
        for fn in funcs:
            try:
                score, reason = fn(ctx)
                score = float(min(1.0, max(0.0, score)))
            except Exception as exc:
                score, reason = 0.0, f"check raised {type(exc).__name__}: {exc}"
            values.append(score)
            details.append({"bucket": bucket, "check_function": fn.__name__,
                            "weight": 1, "score": round(score, 6), "reason": reason})
        bucket_scores[bucket] = mean(values)

    reward = (bucket_scores["static_checks"]
              + 2 * bucket_scores["reward_hacking_checks"]
              + 3 * bucket_scores["partial_oracle_checks"]) / 6
    payload = {
        "reward": round(reward, 6),
        "total_static_check_score": round(bucket_scores["static_checks"], 6),
        "total_reward_hacking_check_score": round(bucket_scores["reward_hacking_checks"], 6),
        "total_partial_oracle_check_score": round(bucket_scores["partial_oracle_checks"], 6),
    }
    (out_dir / "reward.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (out_dir / "verifier_status.json").write_text(json.dumps(
        {"status": "ok", "reward_is_graded": True, "check_count": len(details),
         "bucket_check_counts": {k: len(v) for k, v in CHECKS.items()},
         "results": details}, indent=2) + "\n", encoding="utf-8")

    lines = [
        f"static_checks={payload['total_static_check_score']:.6f} ({len(CHECKS['static_checks'])} checks)",
        f"reward_hacking_checks={payload['total_reward_hacking_check_score']:.6f} ({len(CHECKS['reward_hacking_checks'])} checks)",
        f"partial_oracle_checks={payload['total_partial_oracle_check_score']:.6f} ({len(CHECKS['partial_oracle_checks'])} checks)",
        f"reward={payload['reward']:.6f}; reward=(static + 2*reward_hacking + 3*partial_oracle)/6.",
        "", "Check detail:",
    ]
    for row in details:
        lines.append(f"  [{row['bucket']}] {row['check_function']}: {row['score']:.6f} -- {row['reason']}")
    report = "\n".join(lines)
    print(report)
    (out_dir / "test-stdout.txt").write_text(report + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
