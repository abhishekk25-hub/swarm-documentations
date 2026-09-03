Regulatory clock change-control rulebook

The snapshot contains Federal Register rule documents published from 1 August 2024 through
31 July 2026. Some frozen files preserve neighboring material that appeared on a shared Federal
Register page. The target document begins at the title and `AGENCY` block matching its catalog
record and ends at its own `[FR Doc. <document_number> Filed ...]` line; ignore material outside
those boundaries. Treat that bounded target text as the authority for what the document says. Do not infer
that a delayed provision is withdrawn, that an unaffected provision is delayed, or that a later
document applies to a whole rule when its operative language identifies only named provisions.

Each casefile is a JSON object with exactly these top-level keys:

`record_id`, `document_number`, `agency`, `publication_date`, `action_class`,
`affected_authority`, `prior_effective_date`, `new_effective_date`, `compliance_dates`,
`referenced_predecessors`, `operative_scope`, `disposition`, `confidence`, `exception_flags`,
and `evidence`.

Use these action classes only:

- `INITIAL_DELAY`: this document postpones an effective/applicability/compliance date and does
  not state that it is a further extension, partial delay, withdrawal, or correction.
- `FURTHER_DELAY`: the document expressly extends or further delays an earlier postponement.
- `PARTIAL_DELAY`: only named provisions, amendatory instructions, parties, uses, or conditions
  receive the date change while other provisions retain a different clock.
- `WITHDRAWAL_AND_DELAY`: at least one provision is withdrawn and at least one date is delayed.
- `CORRECTION_AND_DELAY`: the same document both corrects an earlier publication and changes a
  regulatory clock, without a withdrawal taking priority.
- `OTHER_CLOCK_CHANGE`: use only when the source changes a regulatory clock but none of the
  preceding descriptions is accurate. Explain the distinction in `disposition`.

Apply the first matching class in this precedence order so overlapping language has one answer:
`WITHDRAWAL_AND_DELAY`, `CORRECTION_AND_DELAY`, `FURTHER_DELAY`, `PARTIAL_DELAY`,
`INITIAL_DELAY`, then `OTHER_CLOCK_CHANGE`. Withdrawal or correction must be an operative action
of the target document, not a historical, conditional, quoted, or rejected possibility. A further
delay takes precedence over partial scope when the target expressly extends an earlier postponement.

`affected_authority` is a sorted array of the CFR title/part citations, named amendatory
instructions, or named rule provisions whose clock actually changes. `prior_effective_date` is
the immediately superseded effective/applicability date in `YYYY-MM-DD`, `INDEFINITE`, or
`NOT_STATED`. `new_effective_date` uses the same convention. When named provisions are delayed
indefinitely while the remainder receives a dated effective clock, use `INDEFINITE` for the changed
provisions and explain the split in `operative_scope`. `compliance_dates` is a sorted array
of distinct `YYYY-MM-DD` dates expressly described as compliance dates, not every date in the
document. `referenced_predecessors` is a sorted array of Federal Register citations in the form
`90 FR 12345`; omit the current document's own citation. Do not turn a docket number, CFR
citation, page range, comment deadline, or judicial date into a predecessor.

`operative_scope` is 45 to 120 words and must distinguish changed provisions from unaffected,
withdrawn, corrected, or already-effective provisions. `disposition` is 30 to 90 words and states
what a change-control owner should record now, without offering legal advice. `confidence` is one
of `HIGH`, `MEDIUM`, or `LOW`; use `LOW` only when the frozen text genuinely leaves the immediate
predecessor, new date, or affected scope unresolved.

Evidence is an array of three to seven objects. Every object has `role`, `quote`, and
`source_file`. Roles are `ACTION`, `PRIOR_CLOCK`, `NEW_CLOCK`, `SCOPE`, and `RATIONALE`. Include
ACTION, NEW_CLOCK, and SCOPE for every record, plus PRIOR_CLOCK when a predecessor date is stated.
Each quote must be a contiguous 8 to 70 word passage from that record's own frozen source. A quote
may support two roles only if it independently conveys both; otherwise use separate passages.

Exception population

Apply the following closed rules to every case. These are triggers, not severity scores:

- `NO_PREDECESSOR_CITATION`: no predecessor Federal Register citation is stated in the bounded
  target document.
- `MULTIPLE_CLOCK_DATES`: four or more distinct month-day-year dates appear in the source and at
  least two are regulatory effective, applicability, or compliance clocks.
- `PARTIAL_SCOPE_CHANGE`: the clock change is limited to certain provisions, named amendatory
  instructions, named uses, or a subset of the rule.
- `WITHDRAWAL_PRESENT`: the target document operatively withdraws a provision; historical,
  conditional, contemplated, or rejected withdrawal language does not trigger the flag.
- `CORRECTION_PRESENT`: the target document operatively corrects earlier regulatory text or dates;
  a historical reference to an earlier correction does not trigger the flag.
- `INDEFINITE_DATE`: the new clock is expressly indefinite.
- `COMPLIANCE_DATE_CHANGE`: an express compliance date is delayed, extended, or replaced.
- `LONG_PREDECESSOR_CHAIN`: three or more distinct predecessor Federal Register citations are
  stated in the source.

`change_control_exceptions.json` has `snapshot_date`, `population`, and `cases`. `population` is
the sorted list of every record_id that triggers at least one flag. Each case contains record_id,
sorted flags, a 35 to 100 word immediate_action addressing every triggered flag, and at least two
evidence paths of the form `RCC-001#evidence[0]`. Do not include a non-triggered case as filler.

The master CSV has this exact header:

`record_id,document_number,agency,publication_date,action_class,prior_effective_date,new_effective_date,predecessor_count,affected_authority_count,exception_flag_count,chain_id,clock_risk`

`chain_id` is the lexicographically smallest normalized predecessor citation when one exists;
otherwise use the document number. `clock_risk` is `HIGH` for indefinite dates, withdrawals, or
three or more flags; `MEDIUM` for partial scope, compliance-date change, correction, or two flags;
otherwise `LOW`. Counts and classifications must agree with the casefile and exception file.

`clock_atlas_data.json` contains `action_class_counts`, `agency_counts`, `monthly_counts`,
`clock_risk_counts`, and `exception_flag_counts`, all recomputed from the completed register and
casefiles. The SVG must visibly encode all five named series, use real text labels and values, and
include a title, legend, and accessible description. It must not embed a raster image or script.
