Reconcile the supplied Federal Register regulatory-clock snapshot into a change-control package.
Read every case in the catalog and its frozen source; distinguish initial delays, further delays,
partial scope changes, withdrawals, corrections, compliance-date changes, and genuinely
indefinite clocks without treating unaffected provisions as delayed.

Write these deliverables under `/logs/agent/`:

- one grounded JSON casefile for every catalog record in `/logs/agent/casefiles/`, following the supplied
  rulebook and using checkable quotations from that record's own source;
- `/logs/agent/regulatory_clock_register.csv`, with one consistent row per record and derived chain/risk data;
- `/logs/agent/change_control_exceptions.json`, containing the complete rule-triggered exception population
  and actions that address every flag;
- `/logs/agent/regulatory_clock_briefing.md`, explaining the portfolio's clock changes, the most consequential
  chains and scope splits, unresolved uncertainties, and concrete controls, with record citations;
- `/logs/agent/clock_atlas_data.json` and `/logs/agent/regulatory_clock_atlas.svg`, with five agreeing series derived from
  the finished register and casefiles.

Keep dates, predecessor citations, scope statements, flags, counts, briefing claims, and visual
values mutually consistent. Use the frozen sources as the evidence authority and identify
ambiguity rather than inventing missing dates or broadening a provision-specific change.
