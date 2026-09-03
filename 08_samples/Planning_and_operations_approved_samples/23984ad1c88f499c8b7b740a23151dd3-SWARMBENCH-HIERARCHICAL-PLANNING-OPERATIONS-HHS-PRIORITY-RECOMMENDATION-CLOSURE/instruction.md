`/workspace` is your working directory.

I am the enterprise program-management director for the U.S. Department of Health and Human Services. Prepare a closure-planning portfolio for the Deputy Secretary covering 24 priority recommendations that were open in GAO's May 7, 2025 status letter. The portfolio must show what remains unresolved, what work and evidence would support closure, which actions depend on others, and how leadership should sequence implementation.

Use only the frozen material in `/input_artifacts`. This is an operational closure plan as of May 7, 2025, not a representation of later agency or GAO status. Do not claim that GAO has accepted a recommendation as closed. When a target date or other requested fact is not established by the supplied unit sources, write `unknown` and explain the source gap in the specified field.

## Source corpus

`/input_artifacts/portfolio_roster.json` defines the 24 selected units, their operational areas, and paired source paths. `/input_artifacts/portfolio_arbitration_pairs.csv` defines 72 required two-unit planning decisions under three lenses. `/input_artifacts/source_manifest.csv` records per-unit word counts and hashes. `/input_artifacts/file_manifest.csv` pins every supporting input file. `/input_artifacts/source_provenance.md` explains acquisition and dating. `/input_artifacts/status/gao-25-108032-full.txt` is the complete current-status letter and is supplied for context and excerpt verification.

For every unit, read its originating report and its own bounded status excerpt:

```text
U01 /input_artifacts/units/U01_gao-24-106108_report.txt /input_artifacts/units/U01_gao-24-106108_status.txt
U02 /input_artifacts/units/U02_gao-23-105238_report.txt /input_artifacts/units/U02_gao-23-105238_status.txt
U03 /input_artifacts/units/U03_gao-23-106210_report.txt /input_artifacts/units/U03_gao-23-106210_status.txt
U04 /input_artifacts/units/U04_gao-20-372_report.txt /input_artifacts/units/U04_gao-20-372_status.txt
U05 /input_artifacts/units/U05_gao-25-106775_report.txt /input_artifacts/units/U05_gao-25-106775_status.txt
U06 /input_artifacts/units/U06_gao-20-594_report.txt /input_artifacts/units/U06_gao-20-594_status.txt
U07 /input_artifacts/units/U07_gao-17-143_report.txt /input_artifacts/units/U07_gao-17-143_status.txt
U08 /input_artifacts/units/U08_gao-15-183_report.txt /input_artifacts/units/U08_gao-15-183_status.txt
U09 /input_artifacts/units/U09_gao-23-106025_report.txt /input_artifacts/units/U09_gao-23-106025_status.txt
U10 /input_artifacts/units/U10_gao-19-277_report.txt /input_artifacts/units/U10_gao-19-277_status.txt
U11 /input_artifacts/units/U11_gao-18-564_report.txt /input_artifacts/units/U11_gao-18-564_status.txt
U12 /input_artifacts/units/U12_gao-16-394_report.txt /input_artifacts/units/U12_gao-16-394_status.txt
U13 /input_artifacts/units/U13_gao-19-519_report.txt /input_artifacts/units/U13_gao-19-519_status.txt
U14 /input_artifacts/units/U14_gao-19-433_report.txt /input_artifacts/units/U14_gao-19-433_status.txt
U15 /input_artifacts/units/U15_gao-18-480_report.txt /input_artifacts/units/U15_gao-18-480_status.txt
U16 /input_artifacts/units/U16_gao-24-106202_report.txt /input_artifacts/units/U16_gao-24-106202_status.txt
U17 /input_artifacts/units/U17_gao-21-98_report.txt /input_artifacts/units/U17_gao-21-98_status.txt
U18 /input_artifacts/units/U18_gao-21-49_report.txt /input_artifacts/units/U18_gao-21-49_status.txt
U19 /input_artifacts/units/U19_gao-16-568_report.txt /input_artifacts/units/U19_gao-16-568_status.txt
U20 /input_artifacts/units/U20_gao-14-571_report.txt /input_artifacts/units/U20_gao-14-571_status.txt
U21 /input_artifacts/units/U21_gao-12-51_report.txt /input_artifacts/units/U21_gao-12-51_status.txt
U22 /input_artifacts/units/U22_gao-24-105485_report.txt /input_artifacts/units/U22_gao-24-105485_status.txt
U23 /input_artifacts/units/U23_gao-22-105065_report.txt /input_artifacts/units/U23_gao-22-105065_status.txt
U24 /input_artifacts/units/U24_gao-22-104600_report.txt /input_artifacts/units/U24_gao-22-104600_status.txt
```

Each unit is exactly the first priority recommendation listed under `Recommendation:` or `Recommendations:` in that unit's status excerpt. When the excerpt contains multiple bullets, select the first bullet. The status excerpt is authoritative for the selected recommendation, actions taken, remaining work, and date information as of May 7, 2025. The originating report is authoritative for the underlying finding and operational context.

**Deliverables**

Write only the nine deliverables below to `/logs/agent/`. Working files may remain under `/workspace`.

### 1. Recommendation register

Write `/logs/agent/recommendation_register.csv` with exactly this header:

```csv
unit_id,report_id,operational_area,recommendation_owner,status_class,target_date,target_date_basis,closure_owner,wave,dependency_count,current_gap_summary
```

Include exactly one row for each U01 through U24. `report_id` and `operational_area` must match the roster. `recommendation_owner` identifies the official or component addressed by the selected recommendation and must be 2-18 words. `closure_owner` is the accountable owner label you assign. `current_gap_summary` must be 25-60 words and must agree with the corresponding dossier.

`status_class` must use exactly one of these values:

- `not_started`: the status says no responsive action was taken or no implementation work began.
- `in_progress_no_evidence`: the status describes planned or ongoing work but no completed responsive artifact or action.
- `partially_addressed`: the status describes at least one completed responsive action and also identifies substantive work still needed.
- `implementation_evidence_pending`: the status describes a completed responsive procedure, artifact, or activity but says application, operation, or confirmation is still needed before full implementation.
- `unknown`: the supplied status does not establish any of those conditions.

`target_date` is the explicit date tied to completing the selected recommendation's remaining work. Use `YYYY-MM-DD` when a day is stated, `YYYY-MM` when only month and year are stated, `YYYY` when only a year is stated, and `unknown` when the status excerpt supplies no completion date. `target_date_basis` must be an exact contiguous 6-35-word span from the status excerpt when a date is present. When the date is `unknown`, write a 12-40-word explanation of the absence; do not borrow a date from the originating report or another unit.

`wave` is an integer from 1 through 4 and must match the wave plan. `dependency_count` is the number of distinct cross-unit predecessor units in that unit's dependency row; an internal same-unit predecessor counts as zero.

### 2. Recommendation dossiers

Write `/logs/agent/recommendation_dossiers.jsonl` as exactly 24 JSON objects, one object per line, with exactly these fields:

```text
unit_id, report_id, selected_recommendation, report_finding_quote, recommendation_quote,
current_status_quote, status_class, target_date, target_date_basis, current_gap,
closure_criterion, closure_owner, decision_notes
```

`selected_recommendation` must reproduce the complete text in the unit status excerpt's `Recommendation:` passage, excluding only a trailing printed page header when one appears. Do not abbreviate it or add obligations. `report_finding_quote` must be one exact contiguous 18-110-word span from the unit's originating report that establishes the control failure or operational condition behind the recommendation. `recommendation_quote` must be one exact contiguous 18-110-word span beginning at the start of that same `Recommendation:` passage. `current_status_quote` must be one exact contiguous 18-110-word span from the unit's `Actions needed:` passage. Preserve literal case and whitespace within all quotes; do not join passages, insert ellipses, or normalize the wording.

`current_gap` must be an authored 45-110-word reconciliation of what the report found, what the recommendation requires, what HHS has done, and what remains unresolved. It must engage specific language from both source files, add substantive analysis beyond the quoted passages, and must not be a reusable template or a concatenation of quotes. `closure_criterion` must be 35-90 words describing an observable state that would substantively resolve the selected recommendation; completing an activity alone is not sufficient unless the source defines that activity as the required outcome. `decision_notes` must be 25-70 authored words explaining the key implementation choice or uncertainty for leadership and must be recommendation-specific. Status, date, and owner fields must match the register exactly.

### 3. Closure action ledger

Write `/logs/agent/closure_actions.csv` with exactly this header:

```csv
action_id,unit_id,sequence,action_type,action,rationale,source_anchor,predecessor_action_id,owner_role,completion_evidence_id
```

Include exactly five rows per unit, with IDs `AC-U01-01` through `AC-U24-05`. `sequence` is 1 through 5. Each unit must use each `action_type` exactly once: `governance`, `process`, `data`, `workforce`, and `validation`. `action` must be 10-35 words and `rationale` 18-55 words. The rationale must explain why that action addresses this unit's current gap, not define the action type. `source_anchor` must be an exact contiguous 6-30-word span from that unit's report or status excerpt that supports the need for the action.

The source anchor supports the rationale but must not be pasted into it. The rationale must add substantial recommendation-specific analysis beyond the anchor. Rationales must remain distinct after source-anchor words are removed, so reordered, lightly edited, or name-swapped boilerplate is not acceptable.

`predecessor_action_id` is `NONE` for sequence 1 and otherwise names an earlier action for the same unit. `owner_role` is an accountable owner label. `completion_evidence_id` must reference one of that unit's three evidence items.

### 4. Closure evidence plan

Write `/logs/agent/closure_evidence_plan.csv` with exactly this header:

```csv
evidence_id,unit_id,evidence_type,evidence_request,acceptance_test,rationale,source_anchor,accountable_owner,action_ids
```

Include exactly three rows per unit with IDs `EV-U01-01` through `EV-U24-03`. Each unit must use each `evidence_type` exactly once: `design`, `operating`, and `outcome`. `evidence_request` must be 12-40 words. `acceptance_test` must be 18-60 words and state an observable pass condition, not merely request a document. It must identify the record, sample, measure, result, control, or exception population being tested; state the verified state or comparison; and use a quantitative or exhaustive boundary such as a number, percentage, `all`, `each`, `every`, `none`, `zero`, or an explicit minimum/maximum. `rationale` must be 18-55 words explaining how this evidence proves part of the unit's closure criterion. `source_anchor` must be an exact contiguous 6-30-word span from that unit's sources. The anchor must not be pasted into the rationale; the rationale must add substantial recommendation-specific analysis beyond it and remain distinct after anchor and criterion terms are removed. `accountable_owner` is an accountable owner label. `action_ids` is a pipe-separated list containing every action supported by that evidence item; it must be nonempty, contain no duplicates, contain only that unit's actions, and across the three rows cover all five unit actions at least once.

### 5. Dependency register

Write `/logs/agent/dependency_register.csv` with exactly this header:

```csv
dependency_id,unit_id,affected_action_id,predecessor_unit_id,predecessor_action_id,dependency_type,rationale,affected_source_anchor,predecessor_source_anchor,risk_if_unmet
```

Include exactly one row per unit with ID `DP-U01` through `DP-U24`. `affected_action_id` belongs to that unit. `dependency_type` must be one of `internal`, `shared_governance`, `shared_data`, `shared_workforce`, or `external_decision`.

For an internal dependency, `predecessor_unit_id` must equal `unit_id` and `predecessor_action_id` must name an earlier action from the same unit. For a cross-unit dependency, both predecessor fields must identify a different expected unit and one of its actions. Include at least eight cross-unit dependencies across the portfolio. `rationale` must be 25-65 words and explain why the predecessor must be complete before the affected action. `affected_source_anchor` must be an exact 6-30-word span from the affected unit's sources. `predecessor_source_anchor` must be an exact 6-30-word span from the predecessor unit's sources. Neither anchor may be pasted into the rationale; the authored contribution beyond each anchor must be substantial and recommendation-specific. `risk_if_unmet` must be 15-45 words.

### 6. Implementation wave plan

Write `/logs/agent/implementation_wave_plan.csv` with exactly this header:

```csv
unit_id,wave,readiness,closure_owner,predecessor_unit_ids,dependency_count,decision_rationale,next_gate
```

Include exactly one row per unit. `readiness` must be `blocked`, `foundation`, `ready_for_execution`, or `ready_for_validation`. `predecessor_unit_ids` is a pipe-separated sorted list of distinct cross-unit predecessors or `NONE`. `dependency_count` is its count, with `NONE` counting as zero. A unit with a cross-unit predecessor must be assigned to a strictly later wave than every predecessor. A unit with no cross-unit predecessor may use any wave justified by its source-grounded readiness. `decision_rationale` must be 30-75 words naming the unit's specific unresolved gap and all admitted cross-unit predecessors. `next_gate` must be a 12-35-word observable decision gate.

### 7. Portfolio priority arbitration

Write `/logs/agent/priority_arbitration.csv` with exactly this header:

```csv
pair_id,comparison_lens,unit_a,unit_b,advance_unit_id,defer_unit_id,unit_a_status_anchor,unit_b_status_anchor,advance_rationale,deferral_consequence,dependency_effect,decision_confidence
```

Include exactly one row for every pair in `/input_artifacts/portfolio_arbitration_pairs.csv`; preserve its `pair_id`, `comparison_lens`, `unit_a`, and `unit_b`. `advance_unit_id` and `defer_unit_id` must be the two supplied units in opposite order. `decision_confidence` must be `high`, `medium`, or `low`.

`unit_a_status_anchor` and `unit_b_status_anchor` must each be an exact contiguous 6-30-word span from that unit's own status excerpt. `advance_rationale` must be 45-90 authored words that compare both units under the named lens and explain why the selected unit should receive earlier portfolio attention. `deferral_consequence` must be 30-70 authored words explaining the recommendation-specific operational consequence of delaying `defer_unit_id`; it must engage that unit's report and status evidence rather than repeat the advance rationale. `dependency_effect` must be 25-60 authored words explaining how the two units' submitted dependency and wave records reinforce, weaken, or fail to decide the ordering.

Interpret the three lenses as follows:

- `closure_readiness`: compare how close each unit is to producing sufficient implementation evidence, while distinguishing completed responsive work from plans or unsupported assertions.
- `dependency_leverage`: compare which unit's earlier completion would remove or reduce more operational prerequisites in the submitted dependency and wave plan.
- `evidence_burden`: compare the remaining difficulty of obtaining credible design, operating, and outcome evidence, including the consequence of deferring the unit with the more material unresolved control failure.

A sentence that could be moved unchanged to another pair is not a substantive arbitration. The two rationale fields must remain distinct across the 72 pairs after pair IDs, unit IDs, report IDs, and quoted anchor language are removed. A majority win count is not itself a justification: the row must make the two-unit tradeoff from the frozen sources and submitted plan.

### 8. Traceability graph

Write `/logs/agent/traceability_graph.json` with exactly these top-level keys:

```text
units, actions, evidence, dependencies, arbitrations, patterns, claims
```

`units` must contain one object per expected unit with `unit_id`, `report_id`, `action_ids`, `evidence_ids`, `dependency_id`, `arbitration_ids`, `wave`, and `claim_ids`. `arbitration_ids` contains every pair in which the unit appears, in source-pair order. `actions`, `evidence`, `dependencies`, and `arbitrations` must contain every corresponding submitted record once, preserving identifiers, unit ownership, and field values.

Create exactly six pattern objects with IDs `PT-01` through `PT-06`. Each has exactly `pattern_id`, `title`, `unit_ids`, `report_anchors`, `explanation`, and `material_differences`. Each pattern must cite at least three distinct expected units. The six unit rosters must be distinct and together cover at least ten units. `report_anchors` is an object keyed by every cited unit, with one exact contiguous 6-30-word span from that unit's report supporting the same control-failure relationship. `explanation` must be 45-100 authored words and remain distinct after source-anchor wording is removed. `material_differences` must be 30-80 authored words and explain meaningful variation among the cited units rather than restating the explanation.

Create exactly 12 claim objects with IDs `CL-01` through `CL-12`. CL-01 through CL-04 are `unit_specific`, CL-05 through CL-08 are `comparative`, and CL-09 through CL-12 are `portfolio_wide`. Each claim has exactly `claim_id`, `scope`, `statement`, `unit_ids`, `evidence_ids`, `pattern_ids`, and `source_anchors`. `statement` must be 18-80 authored words. Unit-specific claims cite exactly one unit, comparative claims at least two, and portfolio-wide claims at least three. Every cited evidence ID must belong to a cited unit. `source_anchors` is keyed by every cited unit and contains one exact 6-30-word unit-local report or status span supporting that claim. The graph must be acyclic and all many-to-many references must resolve in both directions.

### 9. Executive decision memo

Write `/logs/agent/executive_decision_memo.md` in 1,700-2,300 words. Its title must be exactly:

```text
# HHS Priority Recommendation Closure Decision Memo
```

Use these `##` sections exactly once and in this order:

```text
## Decision requested
## Portfolio posture
## Portfolio arbitration
## Implementation waves
## Cross-portfolio patterns
## Closure evidence and governance
## Limitations
## Claim register
```

In `Portfolio posture`, name all 24 units and state each unit's exact `status_class`, `wave`, `closure_owner`, and `dependency_count` from the structured files. Keep the labels `wave N` and `dependency_count N` beside the applicable unit.

In `Portfolio arbitration`, explain the principal tradeoffs surfaced by all three lenses and identify contradictions or cycles that leadership must resolve rather than hiding them. Include exactly these two labelled lines, computed from all 72 arbitration rows. Rank units by count descending and break ties by ascending unit ID:

```text
Advance leaders: UXX(N)|UXX(N)|UXX(N)|UXX(N)|UXX(N)|UXX(N)
Deferral exposure: UXX(N)|UXX(N)|UXX(N)|UXX(N)|UXX(N)|UXX(N)
```

The first line contains the six units most often selected in `advance_unit_id`; the second contains the six units most often selected in `defer_unit_id`. Each `(N)` is the exact count. Discuss at least six pair IDs spanning all three lenses, including what is lost by deferral and how the dependency plan affects the choice.

In `Implementation waves`, give the sorted exact roster on four lines using `Wave N: UXX|UXX...`; use `NONE` for an empty roster. Explain every cross-unit predecessor relationship on its own line beginning `Dependency UXX <- UYY:`, where UXX is the affected unit and UYY its predecessor. In `Cross-portfolio patterns`, discuss all six patterns and include one roster line per pattern using `PT-XX | units UXX|UXX...`, preserving the trace graph's unit order.

The `Claim register` must contain exactly 12 authored 35-140-word claim paragraphs matching CL-01 through CL-12. Each paragraph must reproduce its trace claim's `statement` literally and end with exactly one terminal declaration in this grammar:

```text
Claim: CL-XX | Scope: unit_specific|comparative|portfolio_wide | Units: UXX[|UXX...] | Evidence: EV-UXX-XX[|EV-UXX-XX...] | Patterns: PT-XX[|PT-XX...]|NONE
```

The declaration must agree exactly with that claim object. Keep one declaration per paragraph; a newline alone may separate claim paragraphs. The declared scope and roster are authoritative: unit-specific claims cite exactly one unit and only its evidence, comparative claims cite at least two units, and portfolio-wide claims cite at least three units. A claim may use a source-grounded figure only when its own trace node supplies the figure's unit-local support.

## Final consistency review

Before finishing, reopen all nine deliverables. Confirm that every expected identifier has one authoritative record, every arbitration pair uses its two assigned units once, all identifiers resolve in both directions, every cross-unit dependency precedes the affected unit's wave, every structured value restated in the memo is exact, every required authored field is nonempty and recommendation-specific, and every genuine missing date remains `unknown`. Do not modify files under `/input_artifacts`.
