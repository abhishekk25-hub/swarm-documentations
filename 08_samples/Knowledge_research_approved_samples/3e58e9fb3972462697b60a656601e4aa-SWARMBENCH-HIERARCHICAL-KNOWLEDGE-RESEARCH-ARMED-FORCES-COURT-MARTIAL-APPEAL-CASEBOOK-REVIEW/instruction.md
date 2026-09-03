Court-martial convictions: coding what happens to guilt and punishment after trial

I run the appellate shop for a trial-defense division, and my counsel keep coming back to one practical
question: after a service member is found guilty at court-martial and handed confinement, a punitive
discharge, or forfeitures, how much of that guilt finding and that punishment is still standing once the
service's highest court is done, and what tipped it. So we code each decided case into a small structured
record my counsel can sort and count: the offenses of conviction and the punishment the members or the
military judge handed down, the single error the defense got taken up, the yardstick used to weigh it, and
what became of the guilt findings and the punishment. Each record entry is coded strictly off the case as
decided and nothing past it, not the record of trial we never see, not how the same error landed for some
other member, not a study-guide version of the rule.

The decided cases sit under `/environment/input_artifacts/orders/` as `m01.txt` through `m72.txt`, one case
each, running from the convictions and the adjudged sentence through what the court did with them.
`/environment/input_artifacts/case_roster.csv` lists, per case, the report id, the convicted member, the
court, the case number, and the decision date, and `/environment/input_artifacts/source_manifest.csv` records
where each case was pulled from. Each staged case is the whole file for that one member: build its record entry
from that document alone, keep out anything you know about the member or the unit from elsewhere, state no
offense, measure, or ruling the case does not itself set out, and never carry a ruling from one member's case
into another's.

Code each case into a record entry laid out per `/environment/input_artifacts/record_format.md` so the files
stay uniform, headed with the report id, the convicted member, and the case number. In your own words, pin
down: who the member is, the service, whether the trial was a general or special court-martial, and the
convening posture; the offenses and punitive articles of conviction, and the confinement, discharge,
forfeitures, or reduction adjudged; the one error the defense got taken up, be it a faulty members
instruction, thin proof of guilt, defense counsel below standard, command pressure on the process, an
unlawful search or a squeezed-out statement, a denied speedy trial, a guilty plea taken without a proper
providence inquiry, or a sentence too steep for the offense; the yardstick brought to bear on that error and
how it drove to a result; and the fate of the findings and the punishment, whether left standing, a
conviction wiped, the punishment cut or re-figured, the case ordered retried, or sent back down. An entry
that would fit any member on the roster has missed the point; anchor it to this record of trial. These cases
run dense, so a real entry usually spans a few hundred words.

Once the entries are coded, write the division's standing survey and save it. Read the counts back across all
72 cases: which raised errors actually move the outcome and which get waved through, how the chosen yardstick
drives the result, how often guilt stays intact while the punishment still gets cut, where the cases cluster
by kind of error raised or by offense of conviction, and how the stays-intact versus wiped-out versus
sent-back split lands. Note where the cases run together and where they split, and mark the questions the set
still leaves open for the division. Every thread ties back to the entries under it by report id, member name,
or case number.

A short summary affirmance near the bottom of the roster gets coded with the same care as a splashy reversal
up top; a case where nothing moved is still a data point the counts need. Where a case simply leaves a point
open, code it that way in a line rather than guessing. Each entry is your own read of the one document in
front of you. Finish all 72 entries and the standing survey.

You are working in the `/workspace` directory. Put all deliverables under `/logs/agent/output/`:

- `case_files/m01.md` through `case_files/m72.md`: one record entry per case, saved as each case is finished so
  a single failed write late in the run cannot sink the batch. Head each with the report id, the convicted
  member, and the case number.
- `term_survey.md`: the division's standing survey across the whole set described above.
- `case_tracker.csv`: one row per case, columns
  `report,accused,docket,issue_type,disposition,sentence_relief,note_status`, where accused is the convicted
  member, docket is the case number, issue_type is your short tag for the error the court decided, disposition
  is affirmed, affirmed_in_part, reversed, set_aside, remanded, or dismissed, sentence_relief is a short note
  of any relief the court gave the punishment or none if it left it standing, and note_status is complete or
  partial.

As a last step, open `/logs/agent/output/case_files/` and confirm all 72 entries are present, none empty, and
each is a genuine read of the case rather than a stub.
