I need this cycle's hazard-pattern and reportability packet for the Product Safety Review
Board. Cycle reference date is 2026-07-06.

Source material is in /input_artifacts: 204 real CPSC incident reports in
incident_reports.csv, each with the coded intake fields, the consumer's written account and,
where one exists, the firm's filed response; our binding method in surveillance_policy.md;
the brand-string to brand-family mapping in brand_register.csv; and a provenance note.

Every report gets worked and lands in exactly one hazard pattern. Patterns are keyed on brand
family and failure mode and cut across product categories. Trigger arithmetic, filing
deadlines, exposure and disposition all follow the method. The board hears two dossiers per
business day over ten business days and that ceiling is real.

Three files, all under /logs/agent.

`hazard_register.json` is parsed downstream, so use the shape exactly: a top-level object with
`incidents`, `patterns` and `summary`. One entry per report, appearing once, carrying
report_no, brand_family, failure_mode, harm_level, severity_conflict, company_posture,
evidence_grade, pattern_id and a rationale specific enough to audit that determination on its
own. Each pattern entry carries pattern_id, brand_family, failure_mode, incident_count,
countable_count, trigger_rule, trigger_date, filing_deadline, exposure_days, disposition,
member_report_nos and a basis note. The summary carries at least total_incidents,
total_patterns, severity_conflict_count, grade_counts, disposition_counts,
triggered_pattern_count, board_slots_used, board_backlog_count and max_exposure_days, all
consistent with the arrays.

`board_docket.csv` has a header and one row per seated pattern, carrying the columns:
board_slot, board_date, pattern_id, brand_family, failure_mode, trigger_rule, trigger_date,
filing_deadline, exposure_days, countable_count.

`hazard_review_memo.md` is the document I present. In order: Executive Summary; Corpus
Overview; Method; Failure-Mode Classification; Harm Substantiation and Coded-Severity
Conflicts; Company Posture and Evidence Grading; Hazard Pattern Consolidation; Reportability
Triggers and Exposure; Board Docket and Capacity; Pattern Determinations; Recommendations and
Escalation.

Real figures throughout, no placeholders. Register, docket and memo must agree with each other
and with the method. All three files must exist and be complete under /logs/agent when you
stop; keep scratch in /workspace.
