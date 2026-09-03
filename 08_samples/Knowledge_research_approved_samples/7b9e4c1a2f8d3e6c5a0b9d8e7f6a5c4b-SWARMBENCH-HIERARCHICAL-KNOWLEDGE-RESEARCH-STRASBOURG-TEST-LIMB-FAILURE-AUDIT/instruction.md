I head the comparative case-law unit at an intergovernmental legal service. Ten of our member
States have asked us the same question this year and we have been answering it badly. They ask:
when we lose in Strasbourg, what exactly do we lose on? The answer they get today is an article
number, and an article number tells a ministry nothing it can act on. A State that loses because
its law was too vague to be law at all has a legislative problem. A State whose law was sound and
whose courts then weighed nothing has a judicial-practice problem. A State that lost because it
never protected the applicant from a private party in the first place has neither - it has a gap in
what it does, not in what it forbids. All three get the same sentence in our current reports, and
they are not the same case.

So I want this audit done at the level the Court actually decides at: the limb of the test. For
every merits finding in this corpus I need to know which limb of that article's test the case
turned on, which limbs the Court found satisfied, and which it never reached. Then I need it
aggregated, so I can put a table in front of ten legal advisers showing where their exposure really
sits.

This is case coding, not a digest of the case-law. A finding coded to the wrong limb sends an
adviser to fix the wrong thing, and a coded finding with no paragraph behind it is one a lawyer
cannot check. Either is a row that gets the whole audit sent back.

Your working directory is /workspace; use it for scratch and intermediate files. Everything you
need is staged on this machine and you do not need network access. Read these inputs before you
start:

- /input_artifacts/respondent_states.json - the 10 respondent States in this review, each with its
  `respondent_state` name, its short `slug`, and the exact list of `case_ids` belonging to it.
  Every State holds exactly 4 judgments, 40 in all. Read the grouping from this file; do not guess
  it.
- /input_artifacts/judgments/<case_id>.txt - one judgment of the European Court of Human Rights per
  case, named by case id (for example /input_artifacts/judgments/001-231738.txt), as the Court
  published it. Each carries the Court's own headings (INTRODUCTION, THE FACTS, THE LAW, and
  FOR THESE REASONS, THE COURT), its numbered paragraphs, the Registry's keyword summary at the
  head of the document, and in some cases separate opinions after the operative provisions.
- /input_artifacts/limb_standard.md - our own coding standard. It fixes what counts as a finding,
  the closed limb vocabulary, the verdict values, the field contract for every deliverable and the
  constraints the finished set has to satisfy. Follow it literally, because our review pipeline
  reads these files without a human in between.
- /input_artifacts/data_provenance_note.md - where the texts came from, what the conversion to
  plain text did to them, and how the 10 States and the 4 judgments each were chosen.

**What a finding is.** A finding is one merits ruling in a judgment's operative provisions - an
item beginning `Holds` that holds there has or has not been a violation of a named article. A
ruling on just satisfaction, on admissibility, on joining applications or on the remainder of a
claim is not a finding. Two cases catch people out, and section 1 of the standard governs both: an
operative item naming two articles jointly is two findings, and an item naming one article in
conjunction with another is one. Findings are numbered in the order the operative provisions give
them, because one judgment can hold both a violation and a no-violation on the same article.

**What a limb is.** Every finding belongs to a family fixed by its article, and every family has a
closed set of limb codes that section 2 of the standard prints in full. Give every limb in the
family a verdict of `failed`, `satisfied` or `not_examined`, then name the one limb the finding
turned on. A no-violation finding is coded on the same terms as a violation: the Court still
applied the test, and which limb the State satisfied is exactly as informative as which limb it
failed.

The first thing I need is the findings files. For each of the forty judgments write
/logs/agent/findings/<case_id>.json, named by that judgment's own `case_id`, to the field contract
in section 4 of the standard. Read the operative provisions first and enumerate the merits findings
there. Then, for each one, go to the Court's assessment under THE LAW and work out what it actually
turned on:

- `limb_verdicts` - one verdict for every limb code in that finding's family, and no other keys.
- `decisive_limb` - the single limb the finding turned on, always a code from its own family.
- `quote` and `paragraph_no` - at least fifteen words of the Court's own wording, copied exactly
  from the paragraph in which it states that limb's outcome, with that paragraph's number. The
  quotation has to come from the Court's assessment, after THE LAW and before the operative
  provisions, and it is a quotation rather than a paraphrase. No two findings anywhere in the
  review may rest on the same wording.
- `turning_point` - in your own words, between 25 and 60 words: what the case turned on at that
  limb. Name the safeguard that was missing, the material the domestic authority refused to weigh,
  the reason the justification failed or held. The article number, the limb code's own definition
  and the fact that the State lost name nothing a reader had to open THE LAW to find.

The second thing I need is the cross-corpus table, and it is the point of the audit. Write
/logs/agent/limb_matrix.csv to the field contract in section 5 of the standard, one row per limb
code that decided at least one finding anywhere in the corpus and no row for any other code. It
covers all forty judgments, so it cannot be written until every findings file exists.

The third thing is the per-State picture. Write /logs/agent/state_profile.csv to the field contract
in section 6 of the standard: exactly ten rows, one per State, carrying that State's finding and
violation counts, its dominant limb, and a `pattern` of between 25 and 60 words naming what its
four judgments have in common at the limb level, concretely enough that a reader can see it is the
same failing twice. Where nothing recurs, say so and say what the four have instead.

The last thing is what goes in front of the advisers. Write /logs/agent/limb_brief.md, a brief of a
few hundred words with a level-1 heading and these three headed sections, in this order:

- `## Where the States are losing` - which limbs carry the adverse findings across the corpus.
- `## Procedure against substance` - what the split between procedural and substantive limbs shows.
- `## What to put right first` - the limb a ministry should act on, and why that one.

Every figure in the brief has to be one your own deliverables support. Derive it yourself rather
than repeating a number from the matrix without checking it.

Two things matter more than the rest.

**A limb's words appearing in a judgment is not that limb failing.** The Court routinely records
that an interference was prescribed by law and pursued a legitimate aim, and then finds against the
State on necessity. That is one failed limb and two satisfied ones. A finding coded as failing on
all three because all three were discussed tells the adviser the opposite of the truth, and it is
the single error that would make this audit worse than the reports it replaces. Code what the Court
held, not what it mentioned.

**The same article is not always the same test.** Article 8 covers an interference by the State and
a failure by the State to protect someone from another private party, and the Court does not
analyse those the same way: the second is not a legality-aim-necessity case at all, and the
standard gives it its own limb. The same split runs through Articles 2 and 3, where the substantive
obligation and the duty to investigate are separate and a State can lose on one while winning the
other. Deciding which of these a judgment is doing takes reading the assessment. The article
number will not tell you, and neither will the keyword summary at the top of the file.
