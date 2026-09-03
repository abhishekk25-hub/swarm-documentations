Audit the trials under `/input_artifacts/trials/` for outcome reporting, using
`/input_artifacts/trial_index.csv` as the list of what is in scope. Each trial directory holds the
registry record as it stood at the trial's start date, the record as it stands today, and the full
text of the publications reporting that trial.

I need two files back.

`/logs/agent/outcome_ledger.csv`, one row per outcome, with these columns in this order: nct,
unit_type, registry_measure, registry_role, registry_timeframe, reported, reporting_document,
reported_label, reported_instrument, reported_role, role_evidence_quote, result_quote.

Cover both directions. Every outcome in a trial's pre-specification needs a row, including the ones
that were never reported. Every outcome a publication reports a result for that the
pre-specification does not contain needs a row as well.

Where an outcome was reported, say which publication reports it, and describe it in that
publication's own terms rather than the registry's: the label it uses, the instrument it names, and
the role it gives the outcome. Back the role with the heading or sentence that establishes it, and
back the result with the sentence or table row carrying the reported number. Both quotes must be
copied exactly from the publication named in that row. A sentence saying only that an outcome was
measured is not a result.

Where an outcome was not reported anywhere in that trial's publications, say so and leave the
reporting columns empty.

`/logs/agent/prespecification_basis.csv`, one row per trial, with the columns nct,
registry_version_used, version_date, prespecified_outcome_count.

Work only from the supplied files. Write both deliverables to their full paths under `/logs/agent/`.
