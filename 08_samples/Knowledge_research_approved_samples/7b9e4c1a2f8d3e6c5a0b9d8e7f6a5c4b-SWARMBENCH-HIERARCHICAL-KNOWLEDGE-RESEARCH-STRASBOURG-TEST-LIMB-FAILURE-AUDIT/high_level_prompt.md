We hold forty recent judgments of the European Court of Human Rights, four each against ten
respondent States. Code every merits finding at the level the Court actually decided it: the limb
of the test, not the bare article. Work from the staged material in /input_artifacts; no network
needed.

Four deliverables.

First, a findings file per judgment at /logs/agent/findings/<case_id>.json. Enumerate the merits
rulings in that judgment's operative provisions, and for each one give every limb in that article's
family a verdict of failed, satisfied or not examined, name the limb the case turned on, and anchor
that with a verbatim quotation of at least fifteen words from the Court's own assessment, with the
number of the paragraph it sits in. Say in your own words what the finding turned on.

Second, /logs/agent/limb_matrix.csv, one row per limb code that decided at least one finding, with
the counts that follow from the findings files.

Third, /logs/agent/state_profile.csv, ten rows, one per State, with its finding and violation counts,
its dominant limb, and what its four judgments have in common.

Fourth, /logs/agent/limb_brief.md, in the three sections the standard names.

/input_artifacts/limb_standard.md fixes what counts as a finding, the closed limb vocabulary, the
verdict values, the field contract for every deliverable and the constraints the finished set must
satisfy. Follow it literally.

One thing above all: code what the Court held, not what it mentioned. A judgment that records an
interference as lawful and legitimately aimed before losing on necessity has one failed limb, not
three.
