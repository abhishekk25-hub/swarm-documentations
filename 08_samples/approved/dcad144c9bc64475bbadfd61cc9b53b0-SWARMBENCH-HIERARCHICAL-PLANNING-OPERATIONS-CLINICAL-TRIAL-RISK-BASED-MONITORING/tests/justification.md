# Justification

Overview

This is a planning-and-operations task. A contract research organization's (CRO) clinical-operations
lead must build the upcoming quarter's risk-based monitoring (RBM) plan across the CRO's
cardiometabolic (type 2 diabetes) trial portfolio. The portfolio is ~50 real ClinicalTrials.gov study
records; CRA monitor-hours are fixed and cannot cover every site this quarter, so the lead must
monitor the right trials, in the right order, on a defensible cadence. The agent receives the CRO's
working files -- one human-readable study record per trial (`/input_artifacts/trials/NCT*.txt`), the
adopted RBM rulebook (`monitoring_rulebook.md`), quality/regulatory's 12-authority confirmation list
(`sources_to_confirm.md`), and a provenance note -- and must produce the full monitoring packet: an
Excel workbook at `/logs/agent/output.xlsx` and a long evidence-backed plan at
`/logs/agent/monitoring_plan.md`.

The trial records are real public-domain registry records retrieved verbatim from ClinicalTrials.gov
(NLM Data API v2; 17 U.S.C. 105). The CRO's monitoring-hour capacity, the risk-point weights and the
visit-window cadence are the scenario's stated operating parameters, grounded in ICH E6(R2) and the
FDA risk-based-monitoring guidance and disclosed as such in the provenance note.

Where the difficulty lives (and why it is multi-agent, not single)

The load-bearing facts do not arrive as a clean table. Every trial's monitoring-risk fields -- its
overall recruitment status versus its divergent per-site statuses, its phase and study type, its
enrollment count and whether that count is estimated or actual, its facility count, its intervention
types and its last-update date -- must be READ out of ~50 long, format-varying prose records before
any score or schedule exists. There is no structured input to parse, so a code-capable agent cannot
script its way past the reading; and once the fields are extracted, the scoring, tiering and the
reference schedule are modest. The score is dominated by breadth that does NOT compress into one
script and that a single context cannot sustain to completion:
- Reading every one of the ~50 records accurately. In one context the later records get skimmed, so
  the regulated-intervention flag is dropped, enrollment is misread, and overall-vs-site status
  divergences are missed -- which silently corrupts the risk tiers and the schedule.
- Load-bearing browsing across 12 distinct live authorities (ICH E6(R2)/E6(R3), the FDA RBM guidance
  and its Q&A, ICH E8(R1), 21 CFR Parts 312/812/11, FDAAA 801 / 42 CFR 11, 45 CFR 46, TransCelerate
  RBM, and NLM ClinicalTrials.gov), each requiring an actual retrieval, a confirmed fact, the
  retrieved URL, and a frozen date.
- A long evidence-backed plan with a specific quantified monitoring proof for every in-scope trial
  and a full window/capacity infeasibility analysis.
- Carrying every trial in the portfolio through to an audited decision.

A single agent reliably finishes the numeric core but truncates the accurate reading of the later
records, the citations, the per-trial proofs, and the audit coverage, so coverage degrades. A
hierarchical specialist swarm partitions the reading and the breadth and keeps coverage complete.

Three real-world judgment problems are built into the real data (documented in the rulebook, not
hidden traps): a record's overall recruitment status governs scope, but ~11 trials have one or more
site-level statuses that diverge from it (the overall status governs and the divergence is logged);
many in-scope trials individually look monitorable yet collectively exceed the CRA-hours cap and the
visit-window cadence once scheduled together, so some are deferred for capacity and some are
window-infeasible (an interaction invisible trial-by-trial); and 17 trials are completed, terminated,
withdrawn, suspended or not-yet-recruiting and are set aside with a reason.

Reference findings over the shipped data: 35 in-scope trials and 17 excluded; 14 high / 16 medium / 5
low risk tier; 30 regulated trials; 11 overall-vs-site status conflicts; 27 monitoring visits
scheduled, 6 window-infeasible and 2 deferred for capacity; 10 of 14 high-tier trials monitored this
quarter.

Verification

A deterministic executable verifier (`tests/verify.py`, run by `tests/test.sh`, writing the reward to
`/logs/verifier/reward.txt`). No LLM judge, no pre-authored answer file, no network at grade time. The
verifier recomputes the entire numeric reference -- every risk score, tier, monitoring-hour figure,
the in-scope/exclusion determination, the overall-vs-site status reconciliation and the reference
monitoring schedule -- from the gold per-trial fields in `tests/reference_inputs/trials_reference.json`
(extracted verbatim from the real records) using the rulebook constants, and scores a transparent
WEIGHTED RUBRIC (fixed, mode-agnostic weights; no per-mode branch, cap, floor, or multiplier), each
category scored as its own earned/possible ratio with smooth partial credit. Weights track each
deliverable's prominence in the work brief:
- numeric_backbone (0.26): per-trial risk score, tier, monitoring hours and monitoring decision;
  in-scope/out-of-scope determination and exclusion reasons; summary rollup metrics; CRA capacity
  allocation within cap.
- status_reconciliation (0.12): the overall-vs-site status conflicts identified, resolved to the
  governing value, and the divergent site statuses cited.
- source_register (0.22): for each of the 12 authorities, the row labelled with that source_id
  carrying a load-bearing fact token (provably from opening the source), an official-domain URL, and
  a frozen date. Checked against `reference_inputs/sources_reference.json`; the verifier never fetches.
- trial_proofs (0.18): a quantified monitoring-proof note in the plan for every in-scope trial.
- audit_coverage (0.10): every trial carried to a decision in the `audit_log` sheet or the plan.
- report_structure (0.12): the 12 required plan sections present, key RBM concepts, plan numbers
  consistent with the recomputed schedule, no placeholder text, and a length floor.

The analytical workbook (numeric_backbone + status_reconciliation = 0.38) is the largest deliverable;
confirming and citing the twelve authorities (0.22) and the long evidence-backed plan (trial_proofs +
report_structure = 0.30) are the other primary deliverables the brief calls for.

Fixture validation (pre-pilot sanity check, `.build_helpers/ctmonitor/fixtures.py`): a complete gold
packet scores 1.00; a fixture that extracts the early records correctly but degrades on the later ones
(dropped regulated flags, misread enrollment, wrong tiers/hours) and runs short on breadth (about a
third of the citations, trial proofs and audit entries, and a partial plan) scores 0.69; a stub scores
0.02. The ~0.31 gap lives entirely in the un-scriptable reading/browsing/writing/coverage dimensions,
which is the intended multi-agent advantage.

Coordination

Pattern - Hierarchical specialist DAG: 22 specialist roles across three dependency levels
(leaf workers -> subset coordinators -> final assemblers). The orchestrator spawns the eighteen
level-1 leaf specialists, then the two level-2 coordinators (each consolidating only its own group),
then the two level-3 assemblers that depend on the coordinators, so the observed trajectory has a
spawn-depth of 3 and up to ~18 concurrent sub-agent sessions, which is what task.toml's
dag_depth (3) / dag_width (22) record:
- Extract (13, parallel, leaf): thirteen extraction specialists each read and extract a small
  batch of ~4 of the ~50 records (the fields, the scope rule, the status reconciliation) carefully
  and in parallel, so no specialist ever skims under context pressure.
- Research (5, parallel, leaf): five specialists partition the 12 authorities - GCP foundations,
  current-revision GCP and operational Q&A, study-design/framework, FDA/CFR regulation, and
  registry/human-subjects - so the load-bearing browsing is parallelized and verified.
- Coordinate (2, intermediate): an Extraction-Coordinator that reads the thirteen batch outputs,
  merges them into one portfolio table and confirms every one of the ~50 trials is covered exactly
  once, and a Research-Coordinator that reads the five research outputs, merges them into one source
  register and confirms all twelve authorities are confirmed. These intermediate coordinators are
  what make the DAG a genuine hierarchy rather than a flat fan-out: they absorb eighteen raw leaf
  outputs into two coverage-checked masters before any final synthesis runs.
- Assemble (2, parallel, terminal): a Workbook-Builder (derives the tiers, schedule and capacity
  allocation from the consolidated extraction master, reconciles every part against the rulebook,
  and writes the 8-sheet `output.xlsx`) and a Plan-Writer (writes the full twelve-section
  `monitoring_plan.md` - per-trial proofs, infeasibility analysis, framing and citations). Each
  reads the two coordinator masters and writes its
  own deliverable directly to /logs/agent.

AHT Estimate

- Read ~50 records, extract fields, apply scope rule, reconcile status conflicts = 360 min
- Risk-score / tier / hours every in-scope trial and build the schedule + capacity allocation = 240 min
- Confirm and freeze citations for 12 authorities against official sources = 300 min
- Long evidence-backed plan (12 sections, per-trial monitoring proofs, infeasibility analysis) = 480 min
- Workbook + plan assembly and internal-consistency reconciliation = 240 min
- Total ~ 1620 min ~ 27h
