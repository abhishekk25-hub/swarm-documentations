You are preparing an export-control atlas for a shipment desk. Work from the identity-only
claim catalog, screening rulebook, and source manifest available under `/input_artifacts/`.
The finished package must be grounded in the cited instruments and must distinguish an absent
theme from a rule that the source actually states.

Write these deliverables under `/logs/agent/`:

- `export_screening_matrix.csv`, with one catalog-faithful row per claim, the rulebook columns,
  original paraphrases, full round-tripping evidence quotes, closed-list classifications,
  recomputable tightness scores, crosswalk identifiers, and concise notes.
- `jurisdiction_control_atlas.json`, reconciling jurisdiction counts, class counts, mean scores,
  jurisdiction-specific arcs, and crosswalk membership with the matrix.
- `exception_conflict_ledger.csv`, containing only real same-theme class conflicts and the
  evidence and shipment risk needed to explain each conflict.
- `chart_data.json` plus four distinct plots: `control_class_distribution.png`,
  `tightness_score_histogram.png`, `theme_coverage_by_jurisdiction.png`, and
  `conflict_density.png`. Every series and image must be derived from the matrix.
- `counsel_briefing.json`, reconciling headline figures with the matrix and providing genuine
  top themes, conflicted jurisdiction pairs, a 150-300 word comparison, three to five distinct
  shipment-desk actions, and a concise summary.

Keep classifications and crosswalks traceable to rows, preserve the catalog assignments, and
avoid unsupported conclusions. The package should be usable by counsel without treating an
exception as a prohibition or a screening duty as blanket authorization.
