Working set is the 45 appeals listed in /input_artifacts/appeal_pairs.csv. Each row pairs one
Civil Remedies Division ALJ decision with the Departmental Appeals Board decision that reviewed
it, and names the two files under /input_artifacts/decisions/ that carry it. Report only what
those documents say.

I need an issue-by-issue map of what the Board did to each ALJ ruling.

First deliverable, one JSON file per appeal at /logs/agent/pair_records/dab<NNNN>.json, where
<NNNN> is the Board decision number. Each file carries the facility and state, the Board and ALJ
docket numbers, both decision dates, how the ALJ disposed of the case, which party sought Board
review, the immediate jeopardy trajectory across CMS, the ALJ and the Board, and the civil money
penalty at three stages: as CMS imposed it, as the ALJ sustained it, and as it stands after the
Board. Break each penalty into its components, giving the kind, rate, start, end, inclusive day
count and total for each, plus a grand total.

Each file also carries a units list, one entry per issue the Board rules on, including issues it
upholds without discussion because nobody challenged them. Every unit gives the issue category,
the 42 C.F.R. citation it turns on, the period it concerns, how the ALJ ruled, how the Board
ruled, and the ground the Board decided on. Every unit also carries two quotes, one from the
Board decision and one from the ALJ decision, each copied word for word from the file it is
attributed to.

Second deliverable, /logs/agent/issues_ledger.csv, one row per unit across the whole set, with
columns board_decision, alj_decision, facility, issue_category, reg_cite, alj_ruling,
board_ruling, board_ground.

Anything written outside those two paths does not count.
