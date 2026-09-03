# Ashfield Regional Education Cooperative: vertical articulation standard

This is the standard our curriculum office holds an articulation audit to. It states exactly
what a unit concept sheet contains, what a concept dossier contains, how the derived fields
of a dossier are computed, and what the two roll-up deliverables look like. Our review
pipeline reads these files directly, so a file that does not follow this standard cannot be
filed with the adoption submission.

## 1. Deliverables and their paths

| Deliverable | Path |
| --- | --- |
| One unit concept sheet per lesson unit | `/logs/agent/units/<unit_id>.json` |
| One concept dossier per concept | `/logs/agent/concepts/<concept_id>.json` |
| Progression index for the whole set | `/logs/agent/progression_index.json` |
| Articulation report for the whole set | `/logs/agent/articulation_report.md` |

`<unit_id>` is the `unit_id` column of `/input_artifacts/units.csv`, used exactly as it
appears there, for example `/logs/agent/units/G68-STEM-02.json`.

`<concept_id>` is the identifier you assign to a concept. It is a slug of between two and
six words joined by single hyphens, in lower case, using only the letters a to z and those
hyphens, for example `insect-life-cycle` or `how-a-plant-takes-in-water`. The file name is
the `concept_id` and nothing else.

The band order used everywhere in this standard is `K-2`, then `3-5`, then `6-8`, then
`9-12`. A band is *higher* than another when it comes later in that order.

## 2. What a concept is here

A concept is one idea that the reading set teaches more than once, at more than one grade
band, in more than one unit. It is not a topic label and it is not a word. `water` is a
word. `Water is carried up through a plant` is a concept, because a passage can treat it
shallowly at K-2 and rigorously at 9-12 and a reviewer can see the difference.

A concept qualifies for this audit only when the passages themselves carry it. Two passages
treat the same concept when a teacher reading both would say they are about the same idea,
not when the same string occurs in both. The corpus contains words that carry different
concepts in different clusters: an *order* in a botany passage and an *order* in an
architecture passage are two concepts, not one, and they must not be filed under one
`concept_id`. The same holds for *scale*, *key*, *plate*, *cell*, *shell* and *Jupiter*.
Filing two senses under one dossier is the single most damaging error in this audit,
because the adoption reviewer reads it as evidence of a progression that does not exist.

## 3. The unit concept sheet

Each unit concept sheet is a single JSON object with these keys and no others.

```json
{
  "unit_id": "<YOUR_VALUE_HERE>",
  "grade_band": "<YOUR_VALUE_HERE>",
  "subject_cluster": "<YOUR_VALUE_HERE>",
  "source": {
    "title": "<YOUR_VALUE_HERE>",
    "author": "<YOUR_VALUE_HERE>",
    "gutenberg_ebook_number": 0,
    "source_slug": "<YOUR_VALUE_HERE>"
  },
  "passage_summary": "<YOUR_VALUE_HERE>",
  "observations": [
    {
      "concept_id": "<YOUR_VALUE_HERE>",
      "evidence_quote": "<YOUR_VALUE_HERE>",
      "treatment_note": "<YOUR_VALUE_HERE>",
      "demand_level": 0,
      "demand_reason": "<YOUR_VALUE_HERE>"
    }
  ]
}
```

Field by field:

`unit_id`, `grade_band`, `subject_cluster` repeat that unit's row in `units.csv` exactly.

`source` records the passage the sheet is about. `title`, `author` and
`gutenberg_ebook_number` are the values printed in that passage file's own bibliographic
block; `source_slug` is the `source_slug` column of `units.csv`.

`passage_summary` is between forty and ninety words, in your own words, saying what this
particular passage is about. It is read by a reviewer who has not opened the passage.

`observations` holds exactly three entries. The three carry three different `concept_id`
values, so one unit contributes to three concepts and never twice to the same one.

Within an observation:

`concept_id` is the slug of the concept this passage treats, in the form section 1 gives.
Every `concept_id` used anywhere in the release must have a dossier under
`/logs/agent/concepts/`, and every dossier must be named by some sheet. There are no
concepts without dossiers and no dossiers without units.

`evidence_quote` is one continuous run of between fifteen and sixty words copied verbatim
out of **this unit's own passage file**, and it is the place in that passage where the
concept is actually treated. It is the only field in the release that may reproduce source
text. No two observations anywhere in the release may use the same quote.

`treatment_note` is between twenty-five and sixty words, in your own words, saying what
this passage does with this concept: what it asserts, assumes, explains or asks the reader
to do. A note that would be true of any passage treating the concept is not a treatment
note.

`demand_level` is a whole number from 1 to 5 on the scale in section 4. It is a judgement
about **this passage's treatment**, not about the unit's grade band, and the two are allowed
to disagree; where they disagree that is a finding this audit exists to surface.

`demand_reason` is between fifteen and forty-five words, in your own words, saying why the
treatment sits at that level, referring to what the quote and the passage actually do.

## 4. The demand scale

| Level | The passage's treatment |
| --- | --- |
| 1 | Names the thing or shows it, with no explanation. A reader learns that it exists. |
| 2 | Describes it in everyday terms, using observation a child could make unaided. |
| 3 | Explains how or why it works, introduces the technical term, or gives a worked example. |
| 4 | Relates it to a system of other ideas, classifies it, or reasons from a stated principle. |
| 5 | Argues about it, weighs evidence or competing accounts, or treats it as a matter still open. |

Judge the passage in front of you. A 9-12 passage that only names a thing is a level 1
treatment sitting in the 9-12 band, and recording it as a 4 because of where it sits
defeats the whole audit.

## 5. The concept dossier

Each concept dossier is a single JSON object with these keys and no others.

```json
{
  "concept_id": "<YOUR_VALUE_HERE>",
  "concept_name": "<YOUR_VALUE_HERE>",
  "concept_statement": "<YOUR_VALUE_HERE>",
  "primary_cluster": "<YOUR_VALUE_HERE>",
  "rungs": [
    {
      "unit_id": "<YOUR_VALUE_HERE>",
      "grade_band": "<YOUR_VALUE_HERE>",
      "demand_level": 0,
      "advance_over_previous": "<YOUR_VALUE_HERE>"
    }
  ],
  "bands_covered": ["<YOUR_VALUE_HERE>"],
  "span_class": "<YOUR_VALUE_HERE>",
  "regression_flags": [
    {"lower_unit_id": "<YOUR_VALUE_HERE>", "higher_unit_id": "<YOUR_VALUE_HERE>"}
  ],
  "teacher_note": "<YOUR_VALUE_HERE>"
}
```

`concept_id` repeats the file name.

`concept_name` is between three and ten words naming the concept as a teacher would say it.

`concept_statement` is between twenty-five and sixty words, in your own words, stating the
idea itself: what a pupil who has it knows. It is not a description of the passages and not
a list of the units.

`primary_cluster` is `STEM`, `HUMANITIES` or `ARTS`: the cluster this concept mainly
belongs to. It has to be a cluster some rung of this dossier actually sits in.

`rungs` is the heart of the dossier and is not yours to choose freely. **The rungs of a
dossier are exactly the observations that named this `concept_id`, one rung per observation,
and no others.** If eight unit sheets name `insect-life-cycle`, that dossier has those eight
rungs, no more and no fewer, and each rung's `unit_id`, `grade_band` and `demand_level`
repeat that unit sheet's values exactly. A dossier that quietly drops a rung it finds
inconvenient, or adds a unit that never claimed the concept, is describing a set that was
not delivered.

Rungs are listed in band order, lowest band first. Within a band the order is yours.

`advance_over_previous` is between twenty and sixty words, in your own words, and is the
field this whole audit is for. For every rung after the first, it says what this treatment
adds over the rung before it in the list: the new distinction, the new mechanism, the new
term, the new obligation on the reader. For the first rung it says instead what the concept
starts as in this set, which is where a pupil first meets it. Two rungs of one dossier may
not carry the same `advance_over_previous`, and no two dossiers may either. `Treats the
concept in more depth` is not an advance; it is the sentence written by somebody who did not
read the second passage.

`bands_covered`, `span_class` and `regression_flags` are **derived**, not chosen. Section 6
gives the rules. Our pipeline recomputes all three from the rungs and rejects a dossier
whose derived fields do not match, because a derived field that disagrees with its own rungs
tells the reviewer the file was assembled rather than compiled.

`teacher_note` is between thirty and eighty words, in your own words, addressed to a teacher
who has to place this concept in a scheme of work: where the concept is strong in this set
and where a teacher will have to supply something the set does not.

## 6. The derived fields

`bands_covered` is the distinct `grade_band` values of the rungs, in band order, with no
repeats.

`span_class` is one of exactly three strings:

- `full_span` when `bands_covered` holds all four bands.
- `continuous` when `bands_covered` holds two or three bands that are next to one another in
  band order with no band skipped between the lowest and the highest, for example `K-2` and
  `3-5`, or `3-5` and `6-8` and `9-12`.
- `interrupted` when `bands_covered` holds two or three bands with a band skipped between
  the lowest and the highest, for example `K-2` and `6-8`, or `K-2` and `3-5` and `9-12`.

`regression_flags` lists every pair of rungs where the set goes backwards: a rung in a lower
band whose `demand_level` is **strictly greater** than the `demand_level` of a rung in a
higher band. `lower_unit_id` is the unit in the lower band and `higher_unit_id` is the unit
in the higher band. Two rungs in the same band are never a regression pair. Every qualifying
pair is listed, once each, ordered by `lower_unit_id` and then by `higher_unit_id`. When
there are none the list is empty.

## 7. What the release as a whole has to satisfy

These are the constraints that no single sheet and no single dossier can satisfy by itself.
They are the reason this is an audit of a set rather than sixty readings, and the reason the
set has to be reconciled before it is filed.

1. Exactly sixty unit concept sheets, one per row of `units.csv`.
2. Exactly twenty-four concept dossiers. Not twenty-three and not twenty-five.
3. Exactly three observations per sheet, so the release carries exactly 180 observations,
   and therefore exactly 180 rungs spread over the twenty-four dossiers.
4. Every dossier carries at least four and at most twelve rungs. With 180 rungs over 24
   dossiers the average is seven and a half, so a dossier of four and a dossier of twelve
   can both exist, but a release cannot give every concept four rungs and still place all
   180.
5. Every dossier's rungs come from at least four different units and cover at least two
   different grade bands. A concept found in only one band is a topic, not a progression,
   and does not belong in this audit.
6. At least eight of the twenty-four dossiers cover three or more bands, so
   `span_class` is `full_span` or a three-band `continuous` or `interrupted` for at least
   eight of them.
7. At least seven of the twenty-four dossiers are cross-cluster: their rungs come from units
   in two or more subject clusters. The set is full of ideas that cross the clusters, and an
   audit that files every concept inside one cluster has not looked.
8. Each of `STEM`, `HUMANITIES` and `ARTS` is the `primary_cluster` of at least six
   dossiers.
9. No two dossiers are the same concept under two names. Two dossiers whose statements a
   teacher would call the same idea are one concept, however differently the slugs are
   spelled, and splitting one concept in two to make the counts work is the same defect as
   merging two into one.

Constraint 3 with constraint 4 is the one that has to be settled across the whole release
rather than unit by unit: which concepts exist, and how the 180 observations fall across
them, is a decision about the set. Sixty sheets written independently, each naming whichever
three concepts seemed natural to its own writer, will produce far more than twenty-four
concept ids and a long tail of concepts with one or two rungs, and reconciling that is part
of the work rather than an accident to be papered over at the end.

## 8. The progression index

`/logs/agent/progression_index.json` is one JSON object:

```json
{
  "compiled_by": "<YOUR_VALUE_HERE>",
  "concepts": [
    {
      "concept_id": "<YOUR_VALUE_HERE>",
      "rung_count": 0,
      "bands_covered": ["<YOUR_VALUE_HERE>"],
      "span_class": "<YOUR_VALUE_HERE>",
      "clusters": ["<YOUR_VALUE_HERE>"],
      "regression_count": 0,
      "peak_demand": 0
    }
  ],
  "units": [
    {"unit_id": "<YOUR_VALUE_HERE>", "concept_ids": ["<YOUR_VALUE_HERE>"]}
  ],
  "summary": {
    "concepts_indexed": 0,
    "observations_indexed": 0,
    "units_indexed": 0,
    "full_span": 0,
    "continuous": 0,
    "interrupted": 0,
    "concepts_with_regression": 0,
    "cross_cluster_concepts": 0
  }
}
```

`compiled_by` is a non-empty string naming whoever compiled the index.

`concepts` holds one entry per dossier, twenty-four in all. `rung_count` is that dossier's
number of rungs. `bands_covered` and `span_class` are that dossier's derived values.
`clusters` is the distinct subject clusters its rung units sit in, in the order `STEM`,
`HUMANITIES`, `ARTS`. `regression_count` is the length of its `regression_flags`.
`peak_demand` is the highest `demand_level` among its rungs.

`units` holds one entry per lesson unit, sixty in all, with that sheet's three `concept_id`
values.

`summary` counts the release: `concepts_indexed` the dossiers, `observations_indexed` the
observations across all sheets, `units_indexed` the sheets, `full_span`, `continuous` and
`interrupted` the dossiers of each span class, `concepts_with_regression` the dossiers with
at least one regression flag, and `cross_cluster_concepts` the dossiers whose rungs sit in
two or more clusters.

Every number in this index is recomputed by our pipeline from the sheets and the dossiers.
Compile it from the delivered files rather than from what you intended to deliver, because
an index that disagrees with the files it indexes is the artifact the adoption reviewer will
find first.

## 9. The articulation report

`/logs/agent/articulation_report.md` opens with a level-1 heading and then carries these
five level-2 sections, in this order and with no others:

- `## Scope of this review`
- `## Concepts that span the bands`
- `## Where the progression breaks`
- `## Clusters and their coverage`
- `## What to build next`

The report runs to at least 500 words and no section is shorter than 40 words.

`Concepts that span the bands` carries these four lines, replacing each `<number>` with the
count obtained by recomputing from the delivered files:

- `K-2: units=<number>; observations=<number>`
- `3-5: units=<number>; observations=<number>`
- `6-8: units=<number>; observations=<number>`
- `9-12: units=<number>; observations=<number>`

where `units` is the number of that band's sheets delivered and `observations` is the number
of rungs sitting in that band across all dossiers. The section then names, by `concept_id`,
every dossier whose `span_class` is `full_span`, and no dossier that is not one.

`Where the progression breaks` names, by `concept_id`, exactly two things: every dossier
whose recomputed `span_class` is `interrupted`, and every dossier carrying at least one
recomputed regression flag. It names no dossier that is neither. Where the set has neither
an interrupted concept nor a regression, it says so plainly instead and names no dossier at
all: a statement that there is nothing, pairing a word such as no, none, nothing or zero
with what there is none of, as in `no interrupted concepts and no regressions` or `none of
the twenty-four concepts breaks`. That statement is only looked for in the case where it is
true, so the ordinary word no may be used freely when writing up real breaks. One of the two
cases holds, never both, so a section that lists concepts and also says there are none
satisfies neither.

`Clusters and their coverage` accounts for how the concepts fall across `STEM`,
`HUMANITIES` and `ARTS`, including which concepts cross a cluster boundary, and does it with
the counts the delivered dossiers actually carry.

`What to build next` is your own reasoning about which gap in this set a curriculum office
should close first and why. When the sheets and dossiers are separately authored and
mechanically consistent you may say the audit is ready to file. When many sheets share one
observation shell, repeat authored fields, or carry hollow prose that does not name their own
passages, do not call the audit ready to file or claim the set articulates cleanly even if
the mechanical break list is empty; say what has to be rewritten first.

## 10. Writing rules

The passage files are the evidence base, not a phrase bank. `evidence_quote` is the only
field that may reproduce a passage. Every other written field of the release is covered by
the rules below: the `passage_summary`, every `treatment_note`, every `demand_reason`, every
`concept_name`, every `concept_statement`, every `advance_over_previous` and every
`teacher_note`.

- No such field may reproduce a long unbroken run of the passage's own consecutive words.
  Write the observation, do not transcribe the sentence that prompted it.
- No such field may be the passage in disguise. A sentence lifted from the passage and then
  softened by swapping a word here and there is still the passage's sentence, and is read as
  a reproduction however much of its surface has moved. Prose written from the passage rather
  than out of it keeps only the subject's own terms, which is a small part of what it says;
  prose written out of the passage keeps the passage's phrasing between those terms, and that
  is what is looked for.
- The longer fields, which in practice means the `passage_summary`, the longer
  `treatment_note`s and the `teacher_note`, are held to the same standard against the passage
  as a whole rather than against any one sentence of it: a field whose vocabulary is largely
  accounted for by some single stretch of the passage is that stretch restated, not a reading
  of it.

Every unit sheet is read on its own by a reviewer placing that unit, so each one has to be
written for its own passage. No `passage_summary`, `treatment_note` or `demand_reason` may
be word for word the same as that field in another sheet, and no `concept_statement`,
`teacher_note` or `advance_over_previous` may be word for word the same as that field
anywhere else in the release.

Placeholder filler is never acceptable in any field, and the filler looked for is this closed
list: `lorem ipsum`, `TBD`, `TODO`, `N/A`, `not applicable`, `xxxx`, `sample text`,
`placeholder`, `text goes here`, `add description`, `insert here`, `coming soon`, `example
objective`, `your value here`, `your_value_here`, `<your`, `to be completed` and `to be
determined`. Each is
looked for as a whole word or whole phrase, so a real word that happens to contain one of
them is not filler.

Naming no marker is not the same as saying something, so each written field also has to carry
a minimum number of its own subject's words. For a field on a unit sheet, count the words of
four letters or more in the field that are neither ordinary English function words nor
general schoolroom vocabulary, and keep only those that also occur in that unit's assigned
passage. For `advance_over_previous`, count against the passage of that rung's unit. A field
clears this when that count reaches:

| Field | Words of its own passage |
| --- | --- |
| `passage_summary` | 4 |
| each `treatment_note` | 3 |
| each `demand_reason` | 2 |
| each `advance_over_previous` | 2 |

`concept_name`, `concept_statement` and `teacher_note` are exempt, because a concept belongs
to several passages at once and is meant to be stated in language none of them is tied to. A
sentence like `This passage develops the concept further and builds on prior learning` names
nothing from any passage and clears none of these; a sentence about what the passage actually
contains clears them without trying.

Being sixty readings rather than one reading issued sixty times is measured too, so here is
that measure. Take a sheet's `passage_summary`, its three `treatment_note`s and its three
`demand_reason`s together, keep the words of four letters or more that are not ordinary
English function words and not general schoolroom vocabulary, keep only those that the unit's
own passage also uses, and drop the unit's own source title and author. What remains is that
sheet's signature: what this sheet says about its own passage, in that passage's own subject
matter. A signature has to be substantial in its own right, and it has to stay clearly
distinct from every other sheet's signature, measured as the shared words against the words
in either signature. Two sheets written for two different passages clear this comfortably;
the same sheet issued twice with the nouns changed does not. Sharing a house register is
expected and is deliberately not what this measures, which is why the signature is confined
to words the passage itself carries. Writing every
sheet in the same voice costs nothing here; writing every sheet about the same nothing costs
everything, because a sheet that names little of its own passage fails the size floor before
its overlap is ever reached.

The same measure applies to the dossiers, with one difference: a concept belongs to several
passages at once, so a dossier's signature is not confined to any one passage. Take a
dossier's `concept_statement`, its `teacher_note` and all of its `advance_over_previous`
fields together, keep the words of four letters or more that are not ordinary English function
words and not general schoolroom vocabulary, and drop its own `concept_name` words. That
signature has to be substantial in its own right and stay clearly distinct from every other
dossier's signature.
