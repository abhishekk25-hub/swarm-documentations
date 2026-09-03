I am the trade-compliance lead for an AI-infrastructure OEM that ships advanced compute
accelerators and high-bandwidth training servers. Before we clear the next multi-country
shipment wave, I need a grounded atlas of what each relevant export-control regime actually
requires: licences, exceptions, end-user screening, destination limits, catch-all language,
recordkeeping, deemed export, brokering and transit, penalties, classification, applications,
internal compliance expectations, technical assistance, software/technology controls, military
versus dual-use lines, re-export, temporary export, and government or WMD end-use red flags.

You work in `/workspace`. Write every deliverable under `/logs/agent/`. That output root is
not `/workspace/logs/agent/`, and it is not a relative `logs/agent/` path.

Read these inputs first:

- `/input_artifacts/claim_catalog.json` - 180 identity-only claims across ten jurisdictions.
  Each claim names a `claim_id`, `jurisdiction_id`, `control_theme`, `source_url`,
  `locator_hint` and `focus_prompt`. The catalog does not tell you the answer.
- `/input_artifacts/screening_rulebook.md` - binding closed vocabularies and the
  `control_tightness_score` arithmetic.
- `/input_artifacts/source_manifest.json` - primary URLs and fallbacks.

Fetch the instruments live from each claim's `source_url`. Do not invent instrument text. If
a theme is not present in the fetched document, classify it `NOT_FOUND` with an honest note
rather than fabricating a quote.

Deliverables

1. `/logs/agent/export_screening_matrix.csv` with exactly the rulebook columns, one row per
   catalog claim, no duplicates. Keep each row's `jurisdiction_id` and `control_theme` equal
   to the catalog assignment for that `claim_id`. Each substantive row needs your own
   paraphrase, a verbatim `evidence_quote` of 12 to 60 words that appears in full in the
   fetched instrument (not a padded fragment), the closed-list classifications, a
   recomputable `control_tightness_score`, a `crosswalk_group_id`, and a short note.

2. `/logs/agent/jurisdiction_control_atlas.json` of the form:

```json
{
  "jurisdictions": [
    {
      "jurisdiction_id": "",
      "claims_reviewed": 0,
      "control_class_counts": {},
      "mean_tightness_score": 0.0,
      "jurisdiction_arc": ""
    }
  ],
  "crosswalk_groups": [
    {
      "crosswalk_group_id": "",
      "claim_ids": [],
      "jurisdictions_covered": [],
      "reconciliation_note": ""
    }
  ]
}
```

Each `jurisdiction_arc` is 80 to 180 words about that jurisdiction's own rows. Each
`reconciliation_note` explains how linked claims agree or diverge on control class. The atlas
must reconcile with the matrix: per-jurisdiction counts and means, and each crosswalk group's
`claim_ids` / `jurisdictions_covered`, must recompute from the CSV.

3. `/logs/agent/exception_conflict_ledger.csv` with the rulebook columns. Record real
   conflicts where two claims on the same theme carry different control classes that would
   mislead a single global compliance statement. Every cited claim must exist in your matrix,
   the two claims must differ, and the two classes must disagree. Empty agreeing filler is
   worse than an honest short ledger of genuine conflicts.

4. Chart set under `/logs/agent/`:
   - `control_class_distribution.png`
   - `tightness_score_histogram.png`
   - `theme_coverage_by_jurisdiction.png`
   - `conflict_density.png`
   and `/logs/agent/chart_data.json` with keys `control_class_counts`,
   `tightness_score_histogram`, `theme_coverage_by_jurisdiction`, and `conflict_density`.
   All four series must recompute from the matrix. Each PNG must be a real, distinct plot of
   its own series, not a blank canvas or four copies of one image.

5. `/logs/agent/counsel_briefing.json`:

```json
{
  "claims_reviewed": 0,
  "jurisdictions_covered": [],
  "control_class_counts": {},
  "mean_tightness_score": 0.0,
  "highest_tightness_themes": [],
  "most_conflicted_jurisdiction_pairs": [],
  "regime_comparison": "",
  "recommended_actions": [],
  "summary": ""
}
```

Headline figures must recompute from the whole matrix. `highest_tightness_themes` lists
themes that truly score highest in your rows. `most_conflicted_jurisdiction_pairs` lists
regimes that collide on the same control theme with different classes.
`regime_comparison` (150 to 300 words) walks the kinds of control you actually recorded and
ranks the regimes against each other on overlapping themes without inventing classes that
never appeared. Use the matrix's `jurisdiction_id` names when making comparative statements
so each comparison is traceable. `recommended_actions` is three to five concrete shipment-desk instructions,
each a full sentence, no two the same action reworded. `summary` is at most 200 words.

How you go about it is entirely up to you. What I need is an atlas grounded in the fetched
instruments, with paraphrases that are yours and quotes I can check.
