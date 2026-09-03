# Output Requirements

Save all outputs under `/logs/agent`. Keep source snapshots concise: include the source URL and enough exact excerpts to support the memo, rather than dumping very large full pages.

## Source Snapshots

For each case, save source snapshots with the source URL inside each saved file. The required snapshots are the official UNESCO page and one independent external public source outside UNESCO/Wikimedia.

Use these paths for each case:

- `retrieved_sources/{case_id}/unesco_property_page.txt`
- `external_context/{case_id}/external_context_source.txt`

## Case Memos

Write one memo per case at `/logs/agent/case_memos/{case_id}.json`.

Use these memo fields: `case_id`, `property_name`, `unesco_site_id`, `state_party`, `danger_year`, `decision`, `visual_risk_theme`, `danger_quote`, `case_specific_entities`, `source_type_findings`, `evidence_summary`, `danger_basis`, `visual_story_angle`, `media_use_decision`, `source_tension_note`, `claim_boundaries`, `visual_verdict`, `source_tension_matrix`, `interpretive_risk_flags`, `rights_note`, `why_not_the_other_decisions`, `external_context`, `curator_questions`, and `source_refs`.

Use one of these decisions: `lead_scene`, `supporting_scene`, `holdback`.

Use one of these visual risk themes: `conflict_or_instability`, `urban_or_development_pressure`, `ecological_or_species_pressure`, `structural_or_archaeological_fragility`, `water_or_climate_pressure`, `governance_or_documentation_gap`.

For consistency:

- `case_specific_entities` should list 5-9 concrete people, places, institutions, object types, threats, or conservation bodies.
- `source_type_findings` should cover `unesco` and `external_context`.
- `claim_boundaries` should give three safe-claim boundaries with source support and a related `do_not_claim`.
- `visual_verdict` should state `media_fit`, `file_subject`, `risk_visibility`, `rights_or_attribution_implication`, and `curator_use`.
- `source_tension_matrix` should compare two source pairs.
- `external_context` should include `source_url`, `retrieved_source_path`, `external_quote`, `source_label`, `relevance_to_case`, and `why_not_sufficient_alone`.
- `curator_questions` should preserve these keys: `likely_misreading`, `which_source_would_mislead_if_used_alone`, `source_unique_contributions`, `what_the_image_can_show`, `what_the_image_cannot_prove`, `what_external_context_changes`, and `how_to_phrase_without_overclaiming`.

When you use a quote, copy the exact text from the saved source snapshot. Do not paraphrase it or normalize its internal whitespace.

## Package Files

Write these package files under `/logs/agent`:

- `retrieval_audit.json`
- `evidence_register.csv`
- `curatorial_quality_review.json`
- `theme_cluster_map.json`
- `selection_rationale.json`
- `final_consistency_audit.json`
- `storyboard_package.json`
- `output.json`

Every case-level table or review file should cover all listed case IDs exactly once, unless it is a slide-level section. The final decision lists should also partition the listed cases exactly once and agree with the per-case memo decisions.

## Retrieval Audit

`retrieval_audit.json` should include one row per case for each required source type: `unesco` and `external_context`.

Use these row fields: `case_id`, `source_type`, `source_url`, `retrieved_source_path`, `retrieval_method`, `retrieval_status`, `http_status`, `retrieved_at_utc_or_note`, `stability_note`, `retrieved_quote`, `live_excerpt_or_error`, and `comparison_note`.

## Evidence Register

`evidence_register.csv` should use this header:

`case_id,decision,visual_risk_theme,danger_year,retrieval_audited,primary_safe_claim,do_not_claim,media_fit,visual_source,visual_rights_note,source_quote_path,source_quote,external_context_url,external_context_quote,citation_paths`

## Review Files

The review files should cover quote accuracy, safe claims, media fit, rights/licensing, overclaim risk, theme clustering, decision rationale, retrieved sources, memo count, quote grounding, CSV/package alignment, citation paths, current-claim caution, and remaining limits.

Use stable review keys for those files:

- Quality rows: `case_id`, `quote_check`, `safe_claim_check`, `media_fit_check`, `rights_check`, `overclaim_risk`, and `clearance_or_repair_note`.
- `theme_cluster_map.json`: a `clusters` list whose entries use `visual_risk_theme`, `cluster_title`, `case_ids`, `shared_visual_logic`, `caution_note`, and `representative_case_ids`.
- Selection rows: `case_id`, `selected_decision`, `evidence_strength`, `visual_specificity`, `license_usability`, `interpretation_risk`, `why_this_slot`, and `closest_alternative_and_why_rejected`.
- Consistency audit entries: `retrieved_sources_check`, `memo_count_check`, `quote_substring_check`, `decision_partition_check`, `csv_package_alignment_check`, `citation_path_check`, `media_license_check`, `current_claim_check`, and `remaining_known_limits`.

## Final Handoff

The final handoff is `/logs/agent/output.json`, mirrored exactly to `/logs/agent/storyboard_package.json`.

It should be a 30-slide museum-style visual learning arc with `deck_title`, `lead_scene_ids`, `supporting_scene_ids`, `holdback_case_ids`, `slides`, `evidence_table`, `media_manifest`, `risk_theme_index`, `regional_balance`, `citation_appendix`, `retrieval_audit_summary`, `interpretation_risk_register`, `curator_handoff`, and `revision_log`.

Each slide should include `slide_no`, `title`, `slide_type`, `case_ids`, `map_callout`, `visual_strategy`, `caption`, `speaker_notes`, `source_refs`, and `uncertainty_flags`.
