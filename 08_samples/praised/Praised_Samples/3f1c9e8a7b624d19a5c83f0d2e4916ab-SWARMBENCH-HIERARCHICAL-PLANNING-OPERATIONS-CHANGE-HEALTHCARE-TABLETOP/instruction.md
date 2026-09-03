I am the CISO of a regional healthcare network. Our executive team wants a ready-to-run cyber crisis tabletop exercise based on the 2024 Change Healthcare incident, with enough operational realism to test executive decision-making, legal/regulatory judgment, communications coordination, IT operations response, and third-party dependency management.

Use the pinned source list at `/environment/input_artifacts/sources.json`. The local text snapshots in `/environment/input_artifacts/source_text/` are the authoritative quote source for verifying quotes and avoiding citation drift; you may consult the original public URLs for extra context if available. Also use `/environment/input_artifacts/visual_exhibits.json`, which identifies real source-derived visual exhibits such as PDF charts, tables, figures, and control-taxonomy layouts. Every incident fact used in the exercise must be backed by a `source_id` and a verbatim quote from the corresponding source snapshot.

Your working directory is `/`. Write all final deliverables to `/logs/agent/output/`.

Required Deliverables

Create this exact output structure:

/logs/agent/output/
  executive_runbook.md
  facilitator_guide.md
  injects_timeline.csv
  role_packets/
    ciso.md
    legal.md
    communications.md
    executive_leadership.md
    it_operations.md
    vendor_management.md
  observer_scorecards.csv
  evidence_register.csv
  visual_exhibit_notes.csv
  incident_map.html
  after_action_template.md

Source and Evidence Rules

Use the 50 pinned sources in `/environment/input_artifacts/sources.json`.
Use at least 30 distinct `source_id` values across the final package.
Use at least 10 government or regulatory sources, at least 5 healthcare-sector impact sources, and at least 5 technical advisory or ransomware/TTP sources. Determine these categories from the `source_type` and `publisher` fields in `/environment/input_artifacts/sources.json`.
Every incident-specific claim must cite a `source_id`, the original `source_url`, and a verbatim `quoted_evidence` string.
A quote should be at least 12 words long and must appear in that source's local text snapshot under `/environment/input_artifacts/source_text/`.
At least 35 rows in `injects_timeline.csv` must have `quoted_evidence` that round-trips to the matching local source snapshot.
At least 25 rows in `evidence_register.csv` must have `quoted_evidence` that round-trips to the matching local source snapshot.
Do not invent facts, citations, dates, breach details, financial impacts, technical controls, or regulatory obligations.

Visual Exhibit Rules

Use `/environment/input_artifacts/visual_exhibits.json` to identify source-derived visual exhibits from the pinned corpus.
Each visual exhibit includes a `local_file` pointing to a rendered PDF in `/environment/input_artifacts/source_pdfs/`; inspect those local PDFs for the visual/table layout, not only the text snapshots.
Interpret at least 5 distinct visual exhibits. These may include PDF charts, financial tables, survey infographics, technical advisory tables, or cybersecurity-goal taxonomy layouts.
Visual interpretation means explaining what the exhibit's visual/table structure shows and how it affects exercise design. Do not merely repeat a quote from `source_text/`.
Each `visual_observation` must be at least 50 characters and describe layout/table/chart features such as rows, columns, axes, percentages, proportions, groupings, legends, panels, sequence, or taxonomy structure.
Every interpreted visual exhibit must cite `exhibit_id`, `source_id`, `source_url`, `visual_type`, and a short `visual_observation`.
At least 5 valid `exhibit_id` values must appear in `incident_map.html`.
At least 3 valid `exhibit_id` values must appear in `executive_runbook.md`.

Deliverable Requirements

`executive_runbook.md`

Write the sponsor-facing runbook for the CISO and executive sponsor. It must include:

Exercise purpose and intended audience.
2-hour schedule.
Assumptions and artificialities.
Rules of engagement.
Staffing needs.
Success criteria.
Participant pre-read instructions.
Post-exercise remediation workflow.
At least 10 cited source-backed incident facts.
The file must be at least 4,000 characters long.

`facilitator_guide.md`

Write the minute-by-minute guide a facilitator can use during the session. It must include:

Opening script.
Phase-by-phase facilitation plan.
When to deliver each inject.
What answers to listen for.
Expected decisions.
Escalation prompts.
Fallback prompts if participants stall.
Debrief notes tied to at least 3 inject IDs and at least 3 observer objective IDs.
The file must be at least 8,000 characters long.

`injects_timeline.csv`

Create at least 40 inject rows with these exact columns:

inject_id,exercise_time,phase,target_role,inject_text,affected_system_or_dependency,expected_decision,debrief_objective,source_id,source_url,quoted_evidence

Every row must have non-empty values in every column. `target_role` must be one of:

CISO, Legal, Communications, Executive Leadership, IT Operations, Vendor Management

Use at least five distinct exercise phase names in the `phase` column.

`role_packets/`

Create one private packet for each required role:

`ciso.md`
`legal.md`
`communications.md`
`executive_leadership.md`
`it_operations.md`
`vendor_management.md`

Each role packet must include:

Role responsibilities.
Private context.
Decision authority.
Constraints.
Key questions to ask during the exercise.
At least 6 relevant `inject_id` references from `injects_timeline.csv`.
At least 3 cited source-backed facts using valid `source_id` references from `/environment/input_artifacts/sources.json`.

`observer_scorecards.csv`

Create at least 40 observation rows with these exact columns:

objective_id,inject_id,role,expected_behavior,observed_behavior_notes,rating_scale,evidence_of_decision_quality,improvement_area

Every `inject_id` must exist in `injects_timeline.csv`.

`evidence_register.csv`

List every source actually used in the exercise with these exact columns:

source_id,source_url,title,publisher,source_type,quoted_evidence,used_in_artifact,used_for

Every `source_id` and `source_url` must match `/environment/input_artifacts/sources.json`.
Every `source_id` used in `injects_timeline.csv` must also appear in `evidence_register.csv`.

`visual_exhibit_notes.csv`

Create at least 5 visual exhibit interpretation rows with these exact columns:

exhibit_id,source_id,source_url,visual_type,visual_observation,exercise_design_use,used_in_artifact

Every `exhibit_id` must exist in `/environment/input_artifacts/visual_exhibits.json`. Every `source_id` and `source_url` must match the exhibit's source metadata. Use this file to record how source-derived charts, tables, diagrams, or visual layouts shaped the tabletop design.

`incident_map.html`

Create a self-contained HTML visual artifact. It must not depend on external assets. It should show:

Incident phases.
Affected systems or dependencies.
External stakeholders.
Decision points.
Role ownership.
At least 20 valid inject IDs.
At least 10 source IDs.
At least 5 valid visual exhibit IDs from `visual_exhibits.json`.

The file must be at least 5,000 characters long. Do not use external URLs in `<script>`, `<link>`, `<img>`, `<iframe>`, `<audio>`, `<video>`, `<source>`, or `<embed>` tags; keep CSS and JavaScript inline.

`after_action_template.md`

Create a practical after-action report template with sections for:

Strengths.
Gaps.
Decisions requiring follow-up.
Remediation owners.
Due dates.
Retest plan.
Mapping back to observer objectives or inject IDs.
At least 8 valid `inject_id` or `objective_id` references.
The file must be at least 3,000 characters long.

Quality Bar

This package must be useful to a real CISO or cyber crisis program lead. Avoid generic ransomware filler. The materials should test decisions that a healthcare organization would actually face during a third-party claims clearinghouse outage and data breach: cash-flow continuity, claims workarounds, patient-care impact, breach notification, legal/regulatory coordination, executive communications, vendor pressure, technical restoration assumptions, and long-term remediation.
