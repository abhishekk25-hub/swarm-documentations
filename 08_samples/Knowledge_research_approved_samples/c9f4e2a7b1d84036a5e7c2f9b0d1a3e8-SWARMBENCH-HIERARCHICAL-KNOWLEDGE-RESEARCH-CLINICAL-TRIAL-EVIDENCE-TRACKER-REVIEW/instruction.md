Reading trial read-outs into a clinical evidence tracker

I sit on an evidence-synthesis desk inside a health-technology assessment group. My reviewers decide what to
tell payers and guideline panels, and that decision rests on what a trial demonstrated when it actually read
out, not on the protocol's ambitions or the sponsor's headline. The document that settles the matter is the
full results record: the results publication or clinical study report that states who was enrolled, what was
given against what comparator, which endpoint was pre-specified as primary, what effect was measured, and how
much uncertainty sits around it. We keep a living tracker built from those records, and it exists so a reviewer
can see at a glance whether a therapy's pivotal read-out landed, how big the effect was, and whether the safety
signal complicates the story.

There are two things I need from you. First, a worked entry for every trial in the batch. Second, once those
entries exist, a single synthesis memo that reads across the whole batch. Both must come strictly from the
staged records; a registry stub, a conference abstract, or a company statement is not evidence for our
purposes, and nothing you happen to know about a compound from outside these files belongs in an entry.

The records live under `/environment/input_artifacts/trials/`, one plain-text file per trial, named `t01.txt`
through `t72.txt`. Most are efficacy read-outs from randomized controlled trials, and they will give you the
enrolled population, the randomized arms and the intervention, the primary and key secondary endpoints, the
measured effect with its confidence interval or p-value, and the adverse-event and discontinuation profile. A
handful are not primary-efficacy read-outs at all but the records that frame how a result is interpreted, a
pre-specified interim or futility look, an open-label extension or long-term safety follow-up, a pooled or
subgroup reanalysis, or a notice that a trial was halted before completion. Whatever a given file is, take it
on its own terms and report what it establishes; when the record simply does not pin down a piece, such as a
primary effect size, the honest entry says so in a sentence instead of inventing a figure. Two companion files
help you place each record: `/environment/input_artifacts/trial_roster.csv` lists, per report, its id, the
sponsor or trial name, the phase, the condition, the registry identifier, and the completion date, and
`/environment/input_artifacts/source_manifest.csv` records where each file came from. Confine each entry to its
own file, and never let one trial's numbers or conclusions migrate into another's.

Follow the shared layout in `/environment/input_artifacts/note_format.md` so every entry reads the same way,
and write in your own words rather than pasting the record back. Open each entry with a heading that carries the
report id, the sponsor or trial name, and the registry identifier. Then cover, in your own phrasing: the trial
and its population (the sponsor, the condition and phase, whether the design was randomized, blinded, and
controlled, and against what comparator); the question and endpoints (the pre-specified primary endpoint, the
key secondary endpoints, and the hypothesis they were meant to test); the population and exposure (the number
randomized, the arms and their dosing or intervention, the follow-up window, and the eligibility the record
states); and the results and safety (the primary-endpoint effect with its confidence interval or p-value, the
secondary signals worth flagging, and the notable adverse events or discontinuations). Where a record carries
no primary endpoint, describe the analysis or change it does report in place of that. Finish with the verdict:
whether the trial met its pre-specified primary endpoint, missed it, came in mixed, or was terminated early,
reading a record that establishes the primary endpoint as met and one that clears only some of several
co-primary or hierarchical endpoints as mixed. A genuine entry is specific to its trial; if the paragraph could
be swapped onto any other read-out without anyone noticing, it has not told us what this trial found, and a
careful one usually runs a few hundred words given how much these records pack in.

The synthesis memo comes after the entries and draws only on them. Pull out what recurs across the batch, the
band the effect sizes fall in, the endpoints and comparators that show up repeatedly, how the met and missed
read-outs divide, and the way trials group by phase, by condition, or by verdict, citing the reports that carry
each pattern. Be candid about where the evidence lines up and where it pulls apart, and set down the questions
the batch still leaves unresolved. Tie every observation back to the specific records behind it, by report id,
by sponsor or trial name, or by registry identifier.

Treat the last trial on the roster as carefully as the first; a quiet read-out can carry as much signal as a
marquee one. Do the whole batch in a single sustained effort, finishing all 72 entries and the synthesis before
you stop, and where a record leaves a question open, mark it open rather than smoothing it over.

Work in `/workspace`, and write every deliverable under `/logs/agent/output/`:

- `digests/t01.md` through `digests/t72.md`, one file per record, saved as you finish each so a single bad write
  near the end does not cost you the batch. Each begins with a heading carrying the report id, the sponsor or
  trial name, and the registry identifier.
- `evidence_review.md`, the across-the-batch synthesis described above.
- `trial_tracker.csv`, one row per record with columns
  `report,sponsor,registry_id,phase,verdict,primary_result,note_status`. Phase is your short tag for the trial
  phase; verdict is one of met_primary, missed_primary, mixed, or terminated; primary_result is the headline
  primary-endpoint effect the record states (an effect size, hazard ratio, response rate, or p-value, as the
  record gives it) or none where the record states none; note_status is complete or partial.

Before you finish, list `/logs/agent/output/digests/` and confirm all 72 files are there, none is empty, and
each is a real reading of its record rather than a placeholder.
