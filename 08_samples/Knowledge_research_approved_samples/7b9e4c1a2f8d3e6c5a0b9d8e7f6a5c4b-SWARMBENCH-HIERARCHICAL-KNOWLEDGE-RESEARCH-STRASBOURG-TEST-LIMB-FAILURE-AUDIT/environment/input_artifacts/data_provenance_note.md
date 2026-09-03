# Provenance of the judgments in this review

## What the corpus is

`judgments/<case_id>.txt` holds 40 judgments of the European Court of Human Rights, downloaded from
the Court's own HUDOC database at `https://hudoc.echr.coe.int/`. The `case_id` is HUDOC's item
identifier for that judgment, so any file here can be looked up directly at
`https://hudoc.echr.coe.int/eng?i=<case_id>` - for example
`https://hudoc.echr.coe.int/eng?i=001-245073`.

Every judgment in the corpus is:

- a **judgment** (not a decision, a communicated case, or an advisory opinion),
- delivered by a **Section of the Court sitting as a Chamber or a Committee**,
- in **English**, as published by the Court,
- delivered **from 2024 onwards**, so the corpus is recent case-law rather than the leading cases a
  reader may already know,
- against a **single respondent State**, so the ledger's per-State grouping is unambiguous.

## Where the text came from and what was done to it

Each file is the text of the judgment as HUDOC serves it, converted from the Court's HTML rendering
to plain text: block-level tags became line breaks, character entities were decoded, and runs of
four or more blank lines were collapsed to two. Nothing else was changed. The Court's own headings
(`INTRODUCTION`, `THE FACTS`, `THE LAW`, `FOR THESE REASONS, THE COURT`), its numbered paragraphs, its
footnote markers, its award figures and the Registry's keyword summary at the head of the document
are all present as published, including the variation between them: some judgments are followed by
separate, concurring or dissenting opinions and some end at the operative provisions, some list the
applicants in an appendix and some name them in the text, some hold the finding of a violation to be
sufficient just satisfaction in itself and some order a sum, some reserve a question of just
satisfaction, and the spelling of a respondent State's name follows the Court's own usage of the
day.

No judgment was abridged, and no judgment was selected or excluded on the strength of what it holds.

## How the 10 respondent States and 4 judgments each were chosen

`respondent_states.json` names the 10 States and the 4 judgments in each. The States are those whose
recent docket is deep enough to choose from while spanning several different Convention rights, so
that no ledger is four variations on one right. Within a State the four were chosen to spread the
Convention rights, the outcomes and the sums ordered as widely as that State's docket allows, and to
keep the rights shared across States, so that the cross-State tables aggregate over material that
genuinely overlaps rather than over ten unrelated dockets. What any individual judgment holds, and
what if anything it orders paid, is whatever that judgment says.

## Licence and reuse

Judgments of the European Court of Human Rights are public documents. The Court publishes HUDOC
content for free consultation and reuse subject to its own conditions
(`https://www.echr.coe.int/documents/d/echr/Disclaimer_ENG`); the texts are reproduced here
unaltered save for the format conversion described above, and the Court is not associated with this
exercise in any way.
