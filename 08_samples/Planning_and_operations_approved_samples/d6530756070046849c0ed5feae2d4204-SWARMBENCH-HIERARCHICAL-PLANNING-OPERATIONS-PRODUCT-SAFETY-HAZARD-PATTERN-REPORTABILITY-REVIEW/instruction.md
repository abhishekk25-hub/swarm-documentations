From: VP, Product Safety and Regulatory Affairs
To: Hazard surveillance desk
Re: The Q3 hazard-pattern and reportability packet for the review board

We have never actually swept the public incident record for the brands we carry, and I am not
going into the board meeting with a hand-wave. I need the surveillance packet for this cycle:
what hazard patterns are sitting in the public record against our brand families, which of
them have crossed our own reporting trigger, how long they have been sitting there, and which
ones the board can physically hear in the next two weeks. The cycle reference date is
2026-07-06.

Everything is in /input_artifacts. The corpus is /input_artifacts/incident_reports.csv, one
row per real CPSC incident report, carrying the coded intake fields (report number and date,
product category and type, the brand as it was reported, model, manufacturer, retailer, the
coded victim severity, age and location), the consumer's own account in
`incident_description`, and, where the firm filed one, its response in `company_comment`.
/input_artifacts/surveillance_policy.md is our adopted method and it is binding: it defines
the failure-mode families and how to read them, the harm levels, how the coded severity field
maps onto them, the company-posture taxonomy, the evidence grades, what makes a hazard
pattern, the three reportability triggers, the filing deadline, the board's sitting capacity
and the disposition ladder. /input_artifacts/brand_register.csv maps the brand string as
reported onto the brand family we track. /input_artifacts/data_provenance_note.md says where
the records came from and how the slate was drawn.

Some things that will bite you if you are not careful. The failure mode is a reading, not a
lookup — the coded product type tells you what the thing is, never how it failed, and the
narrative is where the actual failure lives. The coded severity field is wrong constantly, in
both directions; I have seen an emergency-room visit filed as "Incident, No Injury" and I want
those disagreements found and flagged, not smoothed over. The company responses are the other
half of the evidence and most of them are house boilerplate that says nothing about the
incident at hand, so read them for what the firm actually committed to rather than for tone —
that reading is what decides whether an incident counts toward a trigger at all, and getting
it wrong quietly moves a trigger date. Brand strings in the source are a mess and the same
brand family shows up under several spellings and under parent and sub-brand names; resolve
through the register. And patterns do not respect product category — the same brand family and
the same failure mode turn up across different categories of goods and that is one pattern,
not two, so whoever assembles the final register has to reconcile them into one before the
trigger arithmetic means anything. A pattern split in half triggers later than it should, or
not at all, and that is the error that actually hurts us.

The packet is three files, all written to /logs/agent.

First, the register at **/logs/agent/hazard_register.json**. It is parsed downstream, so use
this exact shape: a top-level object with `incidents`, `patterns` and `summary`.

Each entry in `incidents` is one report, with `report_no` (exactly as in the corpus),
`brand_family`, `failure_mode`, `harm_level`, `severity_conflict` (true or false),
`company_posture`, `evidence_grade`, `pattern_id`, and `rationale` — a short, specific note
naming the report number, saying in your own words what that account actually describes,
and stating why the failure mode, harm level, posture and grade follow from it. I have to be
able to audit any single determination off its note alone, so a note that would read the same
on another report is not good enough. Every report in the corpus appears exactly once.

Each entry in `patterns` is one hazard pattern, with `pattern_id`, `brand_family`,
`failure_mode`, `incident_count`, `countable_count`, `trigger_rule` (`A`, `B`, `C`, or null),
`trigger_date` (ISO date or null), `filing_deadline` (ISO date or null), `exposure_days`,
`disposition`, `member_report_nos` (the report numbers in the pattern), and `basis` — a short
note saying which incidents drove the trigger and why the disposition follows. Pattern ids are
yours to assign; use them consistently across all three files.

`summary` carries at least `total_incidents`, `total_patterns`, `severity_conflict_count`,
`grade_counts` (by evidence grade), `disposition_counts` (by disposition),
`triggered_pattern_count`, `board_slots_used`, `board_backlog_count` and `max_exposure_days`,
all consistent with the arrays above.

Second, the board docket at **/logs/agent/board_docket.csv**, a header row and one row per
seated pattern, carrying the columns `board_slot`, `board_date`, `pattern_id`,
`brand_family`, `failure_mode`, `trigger_rule`, `trigger_date`, `filing_deadline`,
`exposure_days`, `countable_count`. Seat it the way the method says and no other way. This
is the sheet the board chair works from, so it has to be exactly right.

Third, the written review at **/logs/agent/hazard_review_memo.md**, which is what I walk the
board through, so it has to stand on its own and be backed by the analysis rather than generic
safety prose. Cover, in order: an Executive Summary; a Corpus Overview; the Method; the
Failure-Mode Classification, saying how the families were read and calling out the accounts
that were not obvious; Harm Substantiation and Coded-Severity Conflicts, with the conflicts
found and what they change; Company Posture and Evidence Grading; Hazard Pattern
Consolidation, including the patterns whose incidents span more than one product category and
what consolidating them did to the trigger; Reportability Triggers and Exposure, showing which
rule fired for each triggered pattern and how long the exposure has run; the Board Docket and
Capacity, naming what is seated, what is not, and what the shortfall means; Pattern
Determinations, with a short specific note per pattern carrying its brand family, failure
mode, countable count, trigger rule, trigger date and disposition; and Recommendations and
Escalation. Real figures throughout — if a number belongs there, put the real one, and no
placeholders.

This is more than one pass can hold and still read every account accurately, judge every
company response, grade the evidence, consolidate the patterns across categories, run the
trigger arithmetic and write the review, so organise the work however works best. Whoever
produces the final packet owns reconciling the pieces against the method before it goes out:
the register, the docket and the memo must agree with each other and with the policy.

The one thing that cannot slip: the packet must actually be written to /logs/agent before you
finish — the register at /logs/agent/hazard_register.json, the docket at
/logs/agent/board_docket.csv and the memo at /logs/agent/hazard_review_memo.md. Notes in
/workspace are not the deliverable; this job is a failure if those three files are not there
and complete when you stop. Do not end after only planning: carry it through, write all three
into /logs/agent, then read them back to confirm they are there and complete. You will be
working out of /workspace, so keep scratch and intermediate files in there. Thanks.
