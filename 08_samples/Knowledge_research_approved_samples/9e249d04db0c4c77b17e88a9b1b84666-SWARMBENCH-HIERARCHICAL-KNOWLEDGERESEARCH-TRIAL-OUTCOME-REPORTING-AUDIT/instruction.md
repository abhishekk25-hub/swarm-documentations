I coordinate evidence synthesis for a clinical guideline group, and we have hit a problem that keeps
stalling our panels. When a panel weighs an effect estimate, it needs to know whether the outcome
that estimate came from is the outcome the trial said it would report before it started. Often it is
not. An outcome gets measured with a different scale, moves between primary and secondary, quietly
disappears, or a new one turns up that nobody registered. Almost none of this is flagged by the
papers themselves, so we currently do it by hand, one trial at a time, and we are far behind.

I want the reconciliation done properly for the 23 trials in this batch so we can hand the panel a
single ledger instead of a pile of PDFs.

Everything you need is already on disk. `/input_artifacts/trial_index.csv` lists every trial, its
start date, the registry record version I am treating as the pre-specification, that version's date,
and the full path of every publication file for that trial. Each trial has its own directory named
for its registry identifier, holding `registry-prespecification.txt`, which is the registry record
as it stood when the trial started, `registry-current.txt`, which is the record as it stands today,
and a `publications/` folder with the full text of every publication we could obtain for that trial.
The pre-specification is the version named in the index and nothing else. The current record is
there because it is often revised long after the fact, and a difference between the two is itself
worth seeing, but it is not the baseline.

Please write the ledger to `/logs/agent/outcome_ledger.csv` with exactly these columns, in this
order:

nct, unit_type, registry_measure, registry_role, registry_timeframe, reported, reporting_document,
reported_label, reported_instrument, reported_role, role_evidence_quote, result_quote

One row per outcome. Set `unit_type` to `prespecified` for an outcome that appears in the
pre-specification, and to `additional` for an outcome that a publication reports a result for but
that the pre-specification does not contain. Every outcome in every trial's pre-specification needs
a row, including the ones that turn out never to have been reported, because a panel needs to see
what went missing. Every additional outcome you find needs a row too.

For a `prespecified` row, copy `registry_measure` and `registry_timeframe` exactly as the
pre-specification states them and set `registry_role` to primary, secondary or other to match. For
an `additional` row leave those three columns empty.

Set `reported` to yes or no. If it is yes, `reporting_document` is the PMC identifier of the
publication where you found the result, written the way the filename is written, and the remaining
columns describe how that publication treats the outcome rather than how the registry does.
`reported_label` is the wording the publication itself uses. `reported_instrument` is the
measurement instrument or scale the publication names, in the publication's own words, and is empty
if it names none. `reported_role` is primary, secondary, exploratory, safety or other, as that
publication presents it, and `role_evidence_quote` is the heading or sentence in that same
publication that establishes it, copied exactly. `result_quote` is a sentence or table row from that
same publication carrying the actual reported number for the outcome, copied exactly. A sentence
saying only that the outcome was or would be measured is not a result and does not belong in that
column.

If `reported` is no, leave every column from `reporting_document` onward empty. Do not name a publication for an outcome you could not find reported in one.


Two things matter more than anything else about the quotes. They must be copied character for
character out of the publication named in that same row, because we check them against our own
copies, and a quote that has been tidied up or reconstructed from memory is worse than no quote at
all. And they must come from the publication that actually reports the result, not from a protocol
paper or a methods section that only says an outcome was planned. Several of these trials have a
published protocol among their papers and it names outcomes that were never reported anywhere.

Also write `/logs/agent/prespecification_basis.csv` with the columns nct, registry_version_used,
version_date, prespecified_outcome_count, one row per trial, so we can see which baseline each
trial's audit was built against.

Everything the audit needs is in `/input_artifacts/`, and the copies there are the ones we hold
on file, so the result stays reproducible against them.

The full list of files, so nothing is missed. The index is /input_artifacts/trial_index.csv.

  /input_artifacts/trials/NCT02048007/registry-prespecification.txt /input_artifacts/trials/NCT02048007/registry-current.txt /input_artifacts/trials/NCT02048007/publications/PMC11815404.txt /input_artifacts/trials/NCT02048007/publications/PMC12362227.txt /input_artifacts/trials/NCT02048007/publications/PMC6258425.txt /input_artifacts/trials/NCT02048007/publications/PMC6592520.txt /input_artifacts/trials/NCT02048007/publications/PMC8462712.txt /input_artifacts/trials/NCT02048007/publications/PMC8719241.txt /input_artifacts/trials/NCT02048007/publications/PMC8819720.txt /input_artifacts/trials/NCT02048007/publications/PMC8861117.txt /input_artifacts/trials/NCT02048007/publications/PMC9399865.txt
  /input_artifacts/trials/NCT02391337/registry-prespecification.txt /input_artifacts/trials/NCT02391337/registry-current.txt /input_artifacts/trials/NCT02391337/publications/PMC11271403.txt /input_artifacts/trials/NCT02391337/publications/PMC12015011.txt /input_artifacts/trials/NCT02391337/publications/PMC12751528.txt /input_artifacts/trials/NCT02391337/publications/PMC5588987.txt
  /input_artifacts/trials/NCT02409680/registry-prespecification.txt /input_artifacts/trials/NCT02409680/registry-current.txt /input_artifacts/trials/NCT02409680/publications/PMC13150641.txt /input_artifacts/trials/NCT02409680/publications/PMC5415791.txt /input_artifacts/trials/NCT02409680/publications/PMC9993805.txt
  /input_artifacts/trials/NCT02429180/registry-prespecification.txt /input_artifacts/trials/NCT02429180/registry-current.txt /input_artifacts/trials/NCT02429180/publications/PMC12834544.txt /input_artifacts/trials/NCT02429180/publications/PMC5073546.txt /input_artifacts/trials/NCT02429180/publications/PMC5829775.txt /input_artifacts/trials/NCT02429180/publications/PMC6708169.txt
  /input_artifacts/trials/NCT02584283/registry-prespecification.txt /input_artifacts/trials/NCT02584283/registry-current.txt /input_artifacts/trials/NCT02584283/publications/PMC11745596.txt /input_artifacts/trials/NCT02584283/publications/PMC12513034.txt /input_artifacts/trials/NCT02584283/publications/PMC6416838.txt /input_artifacts/trials/NCT02584283/publications/PMC6701560.txt
  /input_artifacts/trials/NCT02747927/registry-prespecification.txt /input_artifacts/trials/NCT02747927/registry-current.txt /input_artifacts/trials/NCT02747927/publications/PMC10077010.txt /input_artifacts/trials/NCT02747927/publications/PMC11646590.txt /input_artifacts/trials/NCT02747927/publications/PMC11797386.txt
  /input_artifacts/trials/NCT02944682/registry-prespecification.txt /input_artifacts/trials/NCT02944682/registry-current.txt /input_artifacts/trials/NCT02944682/publications/PMC11027158.txt /input_artifacts/trials/NCT02944682/publications/PMC11079463.txt /input_artifacts/trials/NCT02944682/publications/PMC11097839.txt /input_artifacts/trials/NCT02944682/publications/PMC11757157.txt /input_artifacts/trials/NCT02944682/publications/PMC12083286.txt /input_artifacts/trials/NCT02944682/publications/PMC12755731.txt /input_artifacts/trials/NCT02944682/publications/PMC13132538.txt /input_artifacts/trials/NCT02944682/publications/PMC13166104.txt
  /input_artifacts/trials/NCT03114917/registry-prespecification.txt /input_artifacts/trials/NCT03114917/registry-current.txt /input_artifacts/trials/NCT03114917/publications/PMC10668454.txt /input_artifacts/trials/NCT03114917/publications/PMC12628620.txt /input_artifacts/trials/NCT03114917/publications/PMC7298803.txt
  /input_artifacts/trials/NCT03148457/registry-prespecification.txt /input_artifacts/trials/NCT03148457/registry-current.txt /input_artifacts/trials/NCT03148457/publications/PMC11775740.txt /input_artifacts/trials/NCT03148457/publications/PMC12339485.txt /input_artifacts/trials/NCT03148457/publications/PMC12866218.txt
  /input_artifacts/trials/NCT03198585/registry-prespecification.txt /input_artifacts/trials/NCT03198585/registry-current.txt /input_artifacts/trials/NCT03198585/publications/PMC13235861.txt /input_artifacts/trials/NCT03198585/publications/PMC6588901.txt /input_artifacts/trials/NCT03198585/publications/PMC8882292.txt
  /input_artifacts/trials/NCT03502616/registry-prespecification.txt /input_artifacts/trials/NCT03502616/registry-current.txt /input_artifacts/trials/NCT03502616/publications/PMC11127290.txt /input_artifacts/trials/NCT03502616/publications/PMC12583238.txt /input_artifacts/trials/NCT03502616/publications/PMC9500130.txt
  /input_artifacts/trials/NCT03574597/registry-prespecification.txt /input_artifacts/trials/NCT03574597/registry-current.txt /input_artifacts/trials/NCT03574597/publications/PMC11271387.txt /input_artifacts/trials/NCT03574597/publications/PMC11271413.txt /input_artifacts/trials/NCT03574597/publications/PMC13190271.txt
  /input_artifacts/trials/NCT03667690/registry-prespecification.txt /input_artifacts/trials/NCT03667690/registry-current.txt /input_artifacts/trials/NCT03667690/publications/PMC11426279.txt /input_artifacts/trials/NCT03667690/publications/PMC11531808.txt /input_artifacts/trials/NCT03667690/publications/PMC12589930.txt
  /input_artifacts/trials/NCT03869177/registry-prespecification.txt /input_artifacts/trials/NCT03869177/registry-current.txt /input_artifacts/trials/NCT03869177/publications/PMC12676765.txt /input_artifacts/trials/NCT03869177/publications/PMC7547488.txt /input_artifacts/trials/NCT03869177/publications/PMC8170939.txt /input_artifacts/trials/NCT03869177/publications/PMC9469513.txt /input_artifacts/trials/NCT03869177/publications/PMC9764492.txt /input_artifacts/trials/NCT03869177/publications/PMC9934504.txt
  /input_artifacts/trials/NCT04033003/registry-prespecification.txt /input_artifacts/trials/NCT04033003/registry-current.txt /input_artifacts/trials/NCT04033003/publications/PMC11328422.txt /input_artifacts/trials/NCT04033003/publications/PMC11572523.txt /input_artifacts/trials/NCT04033003/publications/PMC12527171.txt /input_artifacts/trials/NCT04033003/publications/PMC9508671.txt
  /input_artifacts/trials/NCT04048967/registry-prespecification.txt /input_artifacts/trials/NCT04048967/registry-current.txt /input_artifacts/trials/NCT04048967/publications/PMC11223439.txt /input_artifacts/trials/NCT04048967/publications/PMC12498441.txt /input_artifacts/trials/NCT04048967/publications/PMC12763924.txt /input_artifacts/trials/NCT04048967/publications/PMC7350704.txt
  /input_artifacts/trials/NCT04066881/registry-prespecification.txt /input_artifacts/trials/NCT04066881/registry-current.txt /input_artifacts/trials/NCT04066881/publications/PMC12020760.txt /input_artifacts/trials/NCT04066881/publications/PMC12629454.txt /input_artifacts/trials/NCT04066881/publications/PMC13231623.txt /input_artifacts/trials/NCT04066881/publications/PMC9649006.txt
  /input_artifacts/trials/NCT04224987/registry-prespecification.txt /input_artifacts/trials/NCT04224987/registry-current.txt /input_artifacts/trials/NCT04224987/publications/PMC11956350.txt /input_artifacts/trials/NCT04224987/publications/PMC12246876.txt /input_artifacts/trials/NCT04224987/publications/PMC13004693.txt /input_artifacts/trials/NCT04224987/publications/PMC8082631.txt
  /input_artifacts/trials/NCT04247009/registry-prespecification.txt /input_artifacts/trials/NCT04247009/registry-current.txt /input_artifacts/trials/NCT04247009/publications/PMC10798910.txt /input_artifacts/trials/NCT04247009/publications/PMC11987391.txt /input_artifacts/trials/NCT04247009/publications/PMC12106552.txt
  /input_artifacts/trials/NCT04369326/registry-prespecification.txt /input_artifacts/trials/NCT04369326/registry-current.txt /input_artifacts/trials/NCT04369326/publications/PMC10367260.txt /input_artifacts/trials/NCT04369326/publications/PMC11386379.txt /input_artifacts/trials/NCT04369326/publications/PMC12043179.txt
  /input_artifacts/trials/NCT04424511/registry-prespecification.txt /input_artifacts/trials/NCT04424511/registry-current.txt /input_artifacts/trials/NCT04424511/publications/PMC10648361.txt /input_artifacts/trials/NCT04424511/publications/PMC13254738.txt /input_artifacts/trials/NCT04424511/publications/PMC9809521.txt
  /input_artifacts/trials/NCT05254002/registry-prespecification.txt /input_artifacts/trials/NCT05254002/registry-current.txt /input_artifacts/trials/NCT05254002/publications/PMC11556932.txt /input_artifacts/trials/NCT05254002/publications/PMC12315800.txt /input_artifacts/trials/NCT05254002/publications/PMC12722168.txt
  /input_artifacts/trials/NCT05485402/registry-prespecification.txt /input_artifacts/trials/NCT05485402/registry-current.txt /input_artifacts/trials/NCT05485402/publications/PMC11123861.txt /input_artifacts/trials/NCT05485402/publications/PMC11970529.txt /input_artifacts/trials/NCT05485402/publications/PMC12963666.txt

Output location - read before you start writing files

Your shell's current working directory is `/workspace`. That directory is temporary scratch space
only. Clone repositories there, run builds there, and do any intermediate work you need there.
Nothing written under `/workspace` is preserved after this session ends.

Every deliverable this task asks you to produce MUST be written using its full absolute path
starting with `/logs/agent/`, for example `/logs/agent/outcome_ledger.csv`. Do not write
deliverables to `./`, `~/`, `/workspace/`, or any path that is not explicitly under `/logs/agent/`.

If a file is not physically present under `/logs/agent/` when this session ends, it does not exist
for grading purposes. There is no partial-credit or `/workspace` exception. Before finishing, run
`ls -la /logs/agent/` and confirm every requested deliverable is listed there with a non-zero size.
