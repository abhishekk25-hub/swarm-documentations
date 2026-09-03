Read the twenty signed Chief of Engineers reports packaged at /input_artifacts/chiefs_reports/ (CR-01.pdf through CR-20.pdf), using chiefs_reports_manifest.csv and source_provenance.md as the index and provenance record for that cohort.

Deliver two files:

1. /logs/agent/authorization_tracker.xlsx, containing:
   - A conditions_register sheet with one row per unit (20 rows, no duplicates): unit_id, project_name, report_date, project_purpose, nonfederal_sponsor, recommended_plan, estimated_first_cost, cost_price_level, benefit_basis, environmental_commitments, implementation_dependencies, authorization_matters, document_relationship, related_unit_id, and citations (page-level, citing that unit's own report).
   - A sponsor_readiness sheet with one row per unit: unit_id, sponsor_named, sponsor_obligations, outstanding_dependency, readiness_label, readiness_rationale, and supporting_citation.
   - Every value must come from that unit's own signed report; where a report does not state something, write not_stated rather than inferring it from another project or from general practice.
   - Citations must actually support recommended_plan and estimated_first_cost.

2. /logs/agent/legislative_briefing.md, a briefing for agency leadership that:
   - States which projects need action from a local sponsor before the next authorization cycle, which need technical clarification from the Corps district, and which need federal advocacy.
   - Names every project discussed by its unit_id and project_name, consistent with the register.
   - Notes recurring obligations across the portfolio.
   - States plainly where the reports do not settle a question, rather than guessing.

Both deliverables must be fully populated for all twenty units and internally consistent with each other and with the source reports.
