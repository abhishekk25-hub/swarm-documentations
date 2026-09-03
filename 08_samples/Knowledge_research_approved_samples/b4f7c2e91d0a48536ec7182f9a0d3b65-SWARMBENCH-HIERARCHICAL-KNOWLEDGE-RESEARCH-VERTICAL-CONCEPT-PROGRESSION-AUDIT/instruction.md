I am Ruth Okonkwo, director of curriculum articulation for the Ashfield Regional Education
Cooperative. Nine districts pooled their budgets last year to license one public-domain
reading set, sixty units across four grade bands and three subject clusters, and the state
adoption panel meets at the end of this term. The panel does not care how good any single
unit is. It asks one question: is this a curriculum, or is it sixty unrelated readings
filed in the same cabinet?

Answering that means showing the panel where an idea enters the set, where it comes back,
and what it is doing differently the second and third time. We have never had that
evidence. Every teacher in the cooperative believes the set spirals, and not one of us can
produce a page proving it.

Your working directory is /workspace. Everything you need has been staged on this machine
and you do not need network access.

This is what has been staged for you:

- /input_artifacts/units.csv lists the sixty lesson units with columns unit_id,
  grade_band, subject_cluster, source_slug and source_file. There are fifteen units in
  each of the K-2, 3-5, 6-8 and 9-12 grade bands, and twenty in each of the STEM,
  HUMANITIES and ARTS subject clusters.
- /input_artifacts/sources/<source_slug>.md is the passage assigned to a unit, one file
  per unit, named by the source_slug column. Each file opens with the bibliographic block
  Project Gutenberg publishes for that work and then carries one continuous extract from
  the book itself.
- /input_artifacts/articulation_standard.md is our own standard. It gives the exact
  contract for every field of every deliverable, the demand scale, the rules for the
  derived fields, and the constraints the release as a whole has to satisfy. Follow it
  literally, because our review pipeline reads these files without a human in between.
- /input_artifacts/data_provenance_note.md records where the staged material came from.

What I need from you:

1. One unit concept sheet per lesson unit, written to /logs/agent/units/<unit_id>.json,
   sixty in all. Each sheet says what that passage is about and records exactly three
   concepts the passage treats. Every concept recorded has to be anchored to the place in
   that unit's own passage where it is treated, quoted verbatim, and each one carries your
   reading of how demanding that treatment is on the scale in section 4 of the standard,
   with your reason. Section 3 gives the shape.

2. One concept dossier per concept, written to /logs/agent/concepts/<concept_id>.json,
   twenty-four in all. A dossier gathers every unit that named that concept into rungs in
   band order and says, rung by rung, what each treatment adds over the one below it.
   That field is the reason this audit exists. Section 5 gives the shape, and section 6
   gives the three fields you compute from the rungs rather than choose.

3. The progression index at /logs/agent/progression_index.json, covering all twenty-four
   concepts and all sixty units. Section 8 gives its shape. Every count in it has to be
   compiled from the delivered files rather than asserted.

4. The articulation report at /logs/agent/articulation_report.md, in the five sections
   section 9 names. The band counts, the concepts named as spanning and the concepts named
   as broken must agree with the dossiers themselves after you recompute their bands, span
   classes and regression flags. An index that misstates a dossier does not make the report
   true; write the report from the dossiers, not from an index that merely echoes itself.

The part of this that is not yours to decide one unit at a time is which concepts exist.
Sixty passages read independently will name a hundred and fifty different concepts, most of
them with one rung, and a set of one-rung concepts is exactly the finding I am trying to
avoid handing the panel. Section 7 of the standard fixes what the release has to come to:
sixty sheets, three observations each, one hundred and eighty observations in total, falling
across exactly twenty-four dossiers of between four and twelve rungs, each dossier reaching
at least two bands and at least four units, with at least eight reaching three bands, at
least seven crossing a cluster boundary, and each cluster leading at least six. Those
numbers do not come out of independent readings by themselves. They have to be settled
across the set and the sheets brought into line with what was settled.

Two things in this audit are the ones the panel will actually re-run, and I care about them
more than anything else in the release. The first is the rungs: a dossier's rungs are
exactly the observations that named it, with the same bands and the same demand levels, so
a dossier and the sheets behind it cannot tell two different stories. The second is the
derived fields: bands_covered, span_class and regression_flags come out of the rungs by the
rules in section 6, and a dossier whose derived fields do not match its own rungs is worse
than one that reports an ugly result honestly.

Getting the field names and the file paths right is necessary and nowhere near sufficient. A
sheet that is present but hollow is no more use to me than a missing one: a passage summary
that would fit any passage, a quote that is not actually in the assigned file, a treatment
note that says the passage develops the concept without saying what it does with it, a
demand level with a reason that does not mention anything the passage contains, or an
advance_over_previous saying the next passage goes deeper are all worse for me than an
honest gap, because they are the things that survive a spot check and fail a real one.

The one error I want to name outright is the false vertical. This set contains words that
mean different things in different clusters, and an order in a botany passage is not an
order in an architecture passage. Filing two senses under one concept invents a progression
that is not there, which is precisely the claim the panel is convening to test.

If something in the standard cannot be met for a unit or a concept, say so in the report
rather than papering over it. I would far rather file twenty-two clean concepts and two
recorded findings than twenty-four that claim to spiral.
