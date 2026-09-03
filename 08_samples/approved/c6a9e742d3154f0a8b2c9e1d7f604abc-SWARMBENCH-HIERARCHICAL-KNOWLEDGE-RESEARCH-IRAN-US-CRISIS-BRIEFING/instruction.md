You are preparing a crisis-intelligence package for a nonpartisan international risk advisory team. Leadership wants to know what can responsibly be said, from public sources, about the June 2025 Iran-US escalation.

Cover the U.S. strikes on Iranian nuclear facilities, Iran's retaliation against Al Udeid Air Base, the ceasefire sequence, competing damage assessments, regional reactions, and second-order effects for diplomacy, energy, shipping, aviation, humanitarian risk, and public communications.

Treat this as a professional research assignment, not a commentary piece. Separate confirmed events, official claims, contested claims, expert assessments, and unresolved questions. Do not provide tactical military advice, targeting guidance, cyber guidance, sanctions evasion guidance, propaganda strategy, or recommendations intended to help any belligerent conduct operations.

## Inputs

Use `/input_artifacts/source_manifest.csv` as the seed list. It contains 100 URLs and marks each source as `substantive_article_or_document`, `primary_document_pdf`, `discovery_or_index`, or `reference_background`.

You may consult `/input_artifacts/briefing_style_guide.md` for citation and neutrality guidance. You may browse beyond the seed list if needed, but the package must still account for every seed URL.

The working directory is `/workspace`. Save final outputs under `/logs/agent/`.

## Source Expectations

Inspect and account for all 100 seed URLs in `source_audit.csv`. Use at least 70 distinct seed URLs as support somewhere in the final analytical package. The threshold is 70, not 100, because some seed URLs may be inaccessible, paywalled, duplicate, index-only, or useful only as background; those still need to be audited rather than silently dropped. Do not treat a manifest row as evidence by itself.

Create stable IDs across the package:

- Evidence IDs: `EV001`, `EV002`, ...
- Claim IDs: `CL001`, `CL002`, ...
- Timeline event IDs: `EVT001`, `EVT002`, ...
- Contradiction IDs: `CON001`, `CON002`, ...

The client should be able to trace major report claims back through source IDs, evidence IDs, claim IDs, event IDs, and contradiction IDs.

Use clear confidence labels consistently. Claim status values should be `confirmed`, `disputed`, `unsupported`, or `unclear`.

## Deliverables

Save all deliverables under `/logs/agent/`.

1. `/logs/agent/source_audit.csv`

One row for every seed URL, S001-S100. Record access status, whether it was used, useful facts or claims, up to two short direct quotes when available, linked evidence/claim/event IDs, limitations, and linked deliverables.

2. `/logs/agent/source_evidence_ledger.csv`

250-350 evidence rows from the browsed sources. Include evidence or retrieval-status notes from at least 70 distinct seed URLs, with direct quoted evidence from at least 45 distinct seed URLs. Each row should include evidence ID, source ID, URL, retrieval status, direct quote or reason no quote was available, extracted claim, topic, linked claim/event IDs, deliverables supported, confidence, and limitations.

3. `/logs/agent/event_timeline.csv`

At least 35 events covering pre-strike context, the U.S. operation, immediate reactions, the Al Udeid retaliation, ceasefire events, and post-strike assessment disputes. Include event IDs, dates, location, actors, summary, evidence IDs, source IDs, conflicts, confidence, and notes.

4. `/logs/agent/claim_matrix.csv`

At least 50 claims spanning facility damage, uranium stockpile status, advance notice, missile counts, casualties, radiation risk, ceasefire timing, regional reactions, and economic or shipping effects. Include claim IDs, status, evidence IDs, supporting and contradicting sources, confidence, and treatment in the final report.

5. `/logs/agent/contradiction_ledger.csv`

At least 25 factual conflicts or source disagreements. Cover damage assessment, uranium stockpile status, missile counts, advance warning timing, ceasefire sequence, radiation or safety implications, casualty figures, regional reactions, energy or shipping effects, and inspection access. Link both sides of each conflict to source IDs and evidence IDs.

6. `/logs/agent/actor_positions.csv`

At least 20 actors, including the United States, Iran, Israel, Qatar, Saudi Arabia, UAE, Oman, Russia, China, UK, France, Germany, the UN, IAEA, EU, and at least four others. Attribute positions neutrally and link to source and evidence IDs.

7. `/logs/agent/impact_register.csv`

At least 30 impacts across diplomatic, legal, nuclear safety, energy market, shipping, aviation, humanitarian, domestic politics, regional security, and information-environment domains. Include severity, confidence, source IDs, and evidence IDs.

8. `/logs/agent/uncertainty_register.csv`

At least 15 unresolved questions. Include underground damage, uranium stockpile status, missile count discrepancies, ceasefire sequencing, radiation or safety implications, and future inspection access. Link uncertainties to evidence and contradiction IDs where relevant.

9. `/logs/agent/appendix_citation_index.csv`

A citation map from source IDs, evidence IDs, claim IDs, and event IDs to deliverables, sections or rows, and supported findings. It must show at least 70 distinct seed source IDs used across the package.

10. `/logs/agent/executive_briefing.md`

A 2-4 page leadership briefing with an executive summary, what happened, what is confirmed, what is disputed or uncertain, main implications, near-term indicators, and confidence labels.

11. `/logs/agent/full_analytical_report.md`

A 6,000-10,000 word report covering scope and method, source limitations, limits of public evidence and classified/intelligence uncertainty, pre-strike context, strike timeline and rationale, Iranian response, Al Udeid retaliation, ceasefire sequence, damage disputes, nuclear safety, IAEA/UN context, legal/diplomatic framing, regional reactions across Gulf, European, Russian, Chinese, Israeli, Iranian, and international actors, energy/shipping/aviation/market effects, humanitarian implications, information environment, key uncertainties, and non-operational monitoring. Cite source IDs plus claim or event IDs for major factual claims; cite contradiction IDs for disputed claims.

12. `/logs/agent/stakeholder_briefing_slides.md`

A 12-18 slide-style Markdown deck for leadership. Include timeline, actor positions, disputed claims, impacts, uncertainties, and monitoring indicators.

13. `/logs/agent/one_page_talking_points.md`

Neutral internal talking points with concise points, avoid-saying notes, Q&A pairs, and source IDs for factual points.

14. `/logs/agent/monitoring_plan.md`

A non-operational 7-14 day public-source monitoring plan with indicators, stakeholder categories, why each indicator matters, source categories to watch, escalation or de-escalation signals, and an explicit note excluding tactical or operational guidance.

## Quality Bar

Keep the package neutral, source-grounded, internally consistent, and clear about uncertainty. Do not present disputed claims as settled facts. Explain inaccessible, paywalled, duplicate, background-only, or irrelevant seed URLs instead of dropping them silently.

## Required CSV Schemas By File

Each CSV deliverable has its own schema. Use the exact column names listed after that file name.

- `source_audit.csv`: `source_id`, `url`, `source_title`, `publisher`, `source_category`, `publication_date`, `access_status`, `used_in_final_package`, `key_facts_or_claims`, `direct_quote_1`, `direct_quote_2`, `evidence_ids_extracted`, `claim_ids_supported`, `event_ids_supported`, `limitations_or_bias_notes`, `linked_deliverables`
- `source_evidence_ledger.csv`: `evidence_id`, `source_id`, `url`, `source_category`, `retrieval_status`, `direct_quote`, `extracted_claim`, `topic_area`, `supports_claim_ids`, `supports_event_ids`, `supports_deliverables`, `confidence`, `limitations`
- `event_timeline.csv`: `event_id`, `date_time_local`, `date_time_utc_if_available`, `location`, `actors`, `event_summary`, `evidence_ids`, `confidence`, `supporting_source_ids`, `conflicting_source_ids`, `notes`
- `claim_matrix.csv`: `claim_id`, `claim`, `claimant_or_origin`, `topic_area`, `status`, `evidence_ids`, `supporting_source_ids`, `contradicting_source_ids`, `confidence`, `treatment_in_final_report`
- `contradiction_ledger.csv`: `contradiction_id`, `topic_area`, `claim_a`, `claim_a_source_ids`, `claim_a_evidence_ids`, `claim_b`, `claim_b_source_ids`, `claim_b_evidence_ids`, `why_they_conflict`, `current_treatment`, `report_section`
- `actor_positions.csv`: `actor`, `actor_type`, `position_summary`, `key_statement_or_action`, `source_ids`, `evidence_ids`, `stance_category`, `change_over_time`
- `impact_register.csv`: `impact_id`, `impact_domain`, `impact_summary`, `affected_stakeholders`, `time_horizon`, `severity`, `confidence`, `source_ids`, `evidence_ids`
- `uncertainty_register.csv`: `uncertainty_id`, `open_question`, `why_it_matters`, `current_best_assessment`, `evidence_gap`, `related_contradiction_ids`, `evidence_ids`, `sources_that_disagree_or_are_incomplete`, `what_public_evidence_would_reduce_uncertainty`, `confidence`
- `appendix_citation_index.csv`: `source_id`, `evidence_id`, `claim_id`, `event_id`, `url`, `deliverable`, `section_or_row_reference`, `claim_or_finding_supported`

For quoted evidence, keep `direct_quote` short and source-specific, usually about 8-40 words. The cited source set should cover official/IGO, wire news, regional sources, think tanks, market/shipping/aviation sources, and reference/background sources.
