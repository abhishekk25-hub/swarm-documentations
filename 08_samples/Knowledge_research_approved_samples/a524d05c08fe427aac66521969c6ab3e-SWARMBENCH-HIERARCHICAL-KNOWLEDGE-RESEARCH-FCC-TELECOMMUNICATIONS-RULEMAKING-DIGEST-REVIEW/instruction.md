Keeping up with Federal Communications Commission rulemakings

I sit on a spectrum-and-communications policy desk. Whenever the FCC adopts a rule, whether it frees up a
band, rewrites service rules for a licensee class, tightens equipment limits, or resolves a petition, I want
a single page that tells a colleague what the Commission actually adopted and why, so they need not open the
whole Federal Register release. Please build that page for each of 72 releases, then read the 72 as a set and
write up what you see.

The 72 releases are stored as plain text under `/environment/input_artifacts/releases/`, named `a01.txt`
through `a72.txt`. Each file carries one FCC release as adopted, starting with a short header (the subject of
the rule, the Federal Register document number and citation, and the date) and then the release's own text:
the spectrum bands, licensee classes, or equipment at issue, the problem the Commission is addressing, the
rules it adopts and the limits or obligations they impose, the comments it responds to, and the reasoning
behind the decision. A companion listing at `/environment/input_artifacts/proceeding_roster.csv` gives, per
file, the digest id, the rule subject, the document number, the responsible Bureau, and the year; it does not
give the radio service or the kind of action, so you must work those out yourself from the body of the
release - which service the rule most concerns, and which kind of Commission action it is. `/environment/input_artifacts/source_manifest.csv`
records where each release came from. Keep every digest to its own release: do not move a band, a limit, or a
finding from one rule into another's digest, and state nothing the release does not.

Work to the digest layout at `/environment/input_artifacts/record_format.md`, and start each digest with the
digest id, the rule subject, and the document number. In your own words, put down what the rule is about,
which spectrum, licensees, or equipment it reaches, and the radio service it falls under; the kind of action
the Commission took and the substance of the rules it adopted, including the specific limits, eligibility, or
obligations; the problem or record the Commission was responding to; and the reasoning it gave for the
choices it made. A digest bland enough to describe any FCC release is of no use; fix it to this rule, these
bands or licensees, and these specific requirements, and add nothing the release leaves out. The releases run
long, so a real digest usually runs a few hundred words.

When the digests are done, write the set-level reading and save it. Over the 72, gather the radio services
and licensee classes that recur, the balance among the kinds of Commission action, the spectrum bands and
technical limits that keep appearing, the Bureaus that dominate, and where releases group together or stand
apart, each point tied back to the releases behind it by digest id, document number, or subject. Then get
concrete: where several rules meet on a shared band, service, or obligation, where they pull apart, and which
services, actions, or bands the set barely reaches or leaves open.

Give the releases at the end of the roster the same care as the ones at the start, and never supply what a
release does not say. What I want is your own reading of each release, in your own words, from the release in
front of you, so each digest holds what the Commission actually adopted. Take the set through in a single
pass, with all 72 digests and the set-level reading finished.

You are working in the `/workspace` directory. Put every deliverable under `/logs/agent/output/`:

- `digests/a01.md` through `digests/a72.md`: one digest per release, saved as you finish each so one late
  failed write cannot cost you the batch. Start each with the digest id, the rule subject, and the document
  number.
- `spectrum_survey.md`: the set-level reading described above.
- `rule_register.csv`: one row per release, columns
  `report,rule_subject,document_number,fcc_bureau,radio_service,action_type,note_status`, where rule_subject
  is the subject of the rule, document_number is the Federal Register document number, fcc_bureau is your
  short tag for the responsible Bureau, radio_service is the service the release most concerns as the record
  gives it (wireless, broadcast, satellite, wireline, public_safety, or media), action_type is the kind of
  action the record gives (report_and_order, memorandum_opinion_and_order, order_on_reconsideration, or
  further_notice), and note_status is complete or partial.

Finally, open `/logs/agent/output/digests/` and confirm all 72 digests are present, none empty, each a real
reading of the release rather than a stub.
