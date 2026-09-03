Prepare an HHS priority-recommendation closure-planning portfolio for the 24 selected GAO recommendations using only the supplied frozen reports and May 2025 status excerpts. The package supports leadership decisions about accountable owners, closure evidence, dependencies, and implementation waves; it must not claim later status or invent unavailable dates.

Deliver nine linked files under `/logs/agent/`:

1. `recommendation_register.csv`, with one canonical row per recommendation covering current status, date basis, accountable owner, wave, dependency count, and gap summary.

2. `/logs/agent/recommendation_dossiers.jsonl`, with the selected recommendation, exact report and status evidence, reconciled current gap, closure criterion, owner, and decision notes for every unit.

3. `closure_actions.csv`, with five source-anchored implementation actions per unit spanning governance, process, data, workforce, and validation.

4. `closure_evidence_plan.csv`, with design, operating, and outcome evidence requests and observable acceptance tests for every recommendation.

5. `dependency_register.csv`, with one justified internal or cross-unit prerequisite per unit and the operational risk if it remains unmet.

6. `implementation_wave_plan.csv`, with a dependency-valid wave, readiness state, owner, rationale, and next gate for every unit.

7. `priority_arbitration.csv`, completing all 72 supplied two-unit decisions under closure-readiness, dependency-leverage, and evidence-burden lenses with source-anchored tradeoffs and recommendation-specific deferral consequences.

8. `traceability_graph.json`, linking all units, actions, evidence, dependencies, arbitrations, six cross-portfolio patterns, and twelve scoped decision claims.

9. `executive_decision_memo.md`, with the decision request, complete portfolio posture, arbitration leaders and deferral exposure, exact wave rosters, cross-portfolio patterns, closure governance, limitations, and claim register.

Keep identifiers, owners, status classes, dates, waves, predecessor counts, arbitration counts, pattern rosters, and claim declarations consistent across all files. Preserve source gaps as `unknown` and use unit-specific evidence rather than generic program language.
