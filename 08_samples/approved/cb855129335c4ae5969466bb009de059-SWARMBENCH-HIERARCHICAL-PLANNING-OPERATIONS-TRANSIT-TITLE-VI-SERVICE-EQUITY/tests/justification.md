# Justification

Overview

This is a planning-and-operations task. County Connect Transit Authority is taking an FY2026
service-change package to its Board, and federal law requires a Title VI service-equity analysis
before a major service change can be adopted. The agent receives the agency's working files - the
adopted service-change package, a raw GTFS schedule export, quarter-mile walkshed populations
overlaid on ACS demographics, the service calendar, the adopted Title VI equity policy, a
25-comment public-comment log, counsel's list of authorities to confirm (`sources_to_confirm.md`),
and a provenance note - and must produce the full Board packet: an Excel workbook at
`/logs/agent/output.xlsx`, a long evidence-backed written report at `/logs/agent/board_report.md`,
and three PNG charts in `/logs/agent`.

Where the difficulty lives (and why it is multi-agent, not single)

The numeric core - per-route people-trips (walkshed population x annual trips, broken out for
minority and low-income riders, before and after each change) and the aggregate disparate-impact /
disproportionate-burden rollup - is fully computable. A single, code-capable agent can and does
script it correctly at any scale, so the rubric gives it only modest weight. The score is
dominated by breadth that does NOT compress into one script and that a single context cannot
sustain to completion:
- Load-bearing browsing across 13 distinct live authorities and ACS tables (FTA Circular 4702.1B,
  42 USC 2000d, 49 CFR Part 21, DOT Order 5610.2C, EO 12898, ACS B03002/C17002/B08201/C16001/B01001,
  the NTD, the GTFS reference, and ACS MOE guidance), each requiring an actual retrieval, a
  confirmed fact, the retrieved URL, and a frozen date.
- A long evidence-backed report with a specific justification for every changed route and a
  transit-dependent population context (zero-vehicle, limited-English-proficiency, older adults).
- Dispositioning all 25 public comments, including triaging out-of-scope asks (fares, amenities).

A single agent reliably finishes the script but truncates the citations, the route-by-route
narrative, and the comment synthesis, so coverage degrades. A hierarchical specialist swarm
partitions the breadth and keeps coverage complete.

Three real-world judgment problems are built into the data (documented in the policy and files,
not hidden traps): the adopted proposal and the GTFS export disagree on some routes' post-change
trips (the proposal governs and the discrepancy is logged); sub-threshold feeder changes are
individually below the 25% screen but belong in the aggregate rollup under the policy; and two
routes have ACS block-group overlap below 50% and are excluded for data quality and disclosed.

Reference solution over the shipped data: a disparate impact on minority populations
(di_ratio ~ 1.25, threshold 1.20) and no disproportionate burden on low-income populations
(db_ratio ~ 1.14); 2 conflicts resolved to the proposal value; 2 routes excluded for data quality.

Verification

A deterministic executable verifier (`tests/verify.py`, run by `tests/test.sh`, writing the reward
to `/logs/verifier/reward.txt`). No LLM judge, no pre-authored answer file, no network at grade
time. The verifier recomputes the numeric reference from the raw input tables in
`tests/reference_inputs/` and scores a transparent WEIGHTED RUBRIC (fixed, mode-agnostic weights;
no per-mode branch, cap, floor, or multiplier), each category scored as its own earned/possible
ratio with smooth partial credit:
- numeric_backbone (0.30): per-route major screen, rollup inclusion, governing trips, and overall/
  minority/low-income people-trip deltas (1% tol); system rollup metrics and ratios; both headline
  findings; conflict and exclusion handling. Both single and multi typically max this.
- source_register (0.22): for each of the 13 authorities, a row carrying a load-bearing fact token
  (provably from opening the source), an official-domain URL, and a frozen date. Checked against
  `reference_inputs/sources_reference.json`; the verifier never fetches.
- route_justifications (0.18): a quantified narrative justification in the report for every changed
  route.
- comment_synthesis (0.15): every public comment dispositioned (in the `comment_disposition` sheet
  or the report synthesis), comment ids read from `reference_inputs/public_comment_log.txt`.
- report_structure (0.10): the 12 required report sections present, key equity disclosures, report
  numbers consistent with the recomputed finding, no placeholder text, and a length floor.
- charts (0.05): the three required PNG charts exist on disk and are listed in `chart_manifest`.

Fixture validation (pre-pilot sanity check, `.build_helpers/titlevi/fixtures.py`): a complete gold
packet scores 0.99; a fixture that scripts the numbers correctly (numeric_backbone 1.0) but runs
short on breadth (about half the citations, route justifications, and comment dispositions, and a
partial report) scores 0.65; a stub scores 0.05. The gap of ~0.35 lives entirely in the
un-scriptable browsing/writing/coverage dimensions, which is the intended multi-agent advantage.

Coordination

Pattern - Hierarchical specialist DAG: 13 specialist roles arranged in a six-stage dependency
chain (below). The orchestrator spawns the specialist team directly, so the observed execution
trajectory has a spawn-depth of 3 (orchestrator -> specialist -> occasional helper) and up to 14
sub-agent sessions in a run, which is what task.toml's dag_depth / dag_width record:
- Ingest (1): a Data Reconciliation Steward builds the canonical route table (conflicts, exclusions,
  major-change screen, annualization) everything else depends on.
- Research (3, parallel): three specialists partition the 13 sources - legal authorities, ACS data
  tables, and reference standards - so the load-bearing browsing is parallelized and verified.
- Equity compute (3, parallel): two People-Trips Analysts partition the routes; an Evidence &
  Provenance Specialist ties routes to source files.
- Rollup (1): an Aggregate Equity Lead makes the disparate-impact / disproportionate-burden call.
- Writing (4, parallel): a Route-Narrative Writer (per-route justifications), a Public-Comment
  Synthesis Writer (all 25 dispositions), a Report-Lead Writer (the framing sections and
  transit-dependent context), and a Visualization Specialist (the three charts).
- Reduce (1): a Reducer reconciles every part against the policy and assembles both deliverables -
  the 9-sheet workbook and the written `board_report.md`.

AHT Estimate

- Reconcile proposal vs GTFS, canonical table, conflicts, exclusions = 240 min
- People-trips computation + aggregate disparate-impact / disproportionate-burden rollup = 360 min
- Confirm and freeze citations for 13 authorities/ACS tables against official sources = 300 min
- Triage and disposition all 25 public comments = 150 min
- Long evidence-backed report (12 sections, per-route justifications, transit-dependent context) = 480 min
- Three charts = 90 min
- Workbook + report assembly and internal-consistency reconciliation = 180 min
- Total ~ 1800 min ~ 30h
