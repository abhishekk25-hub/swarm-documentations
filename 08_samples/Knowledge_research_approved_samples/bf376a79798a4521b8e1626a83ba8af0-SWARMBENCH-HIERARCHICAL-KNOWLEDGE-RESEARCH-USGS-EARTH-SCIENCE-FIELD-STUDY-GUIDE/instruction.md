We are building a method-provenance knowledge graph for a research group. The idea is simple to state and
hard to do: for every study our group cites, capture which investigative techniques it truly leaned on,
so a colleague planning new work can ask "who has actually paired an aquifer test with solute-transport
modeling in a fractured setting?" and get an answer from the graph rather than from memory or from
skimming PDFs. The pieces are staged on this machine; what is missing is the resolution step - deciding,
study by study, which techniques were genuinely used and tying each study to them with an honest write-up.

Your working directory is /workspace. Sixty-six studies are staged here, sorted into six investigative
areas. Start by reading these inputs:

- /input_artifacts/report_roster.csv - the 66 studies (columns report, index_id, title, year,
  discipline). The six areas are unequal in size: Water Quality and Geochemistry holds 21, Groundwater
  Flow Modeling 15, Aquifer Characterization and Hydrogeology 10, Surface Water and Watersheds 9,
  Geophysics and Subsurface Imaging 6, and Data Synthesis and Mapping 5.
- /input_artifacts/discipline_roots.csv - the graph node id standing for each area (columns discipline,
  root_id, root_label, report_count). Use these ids verbatim.
- /input_artifacts/reports/<report>.md - one file per study, named by the report column: the study's full
  text, then a Candidate methods block. That block is a mixed shortlist - some techniques the study
  really ran, padded out with plausible techniques it never touched. The text is the only thing that
  tells the two apart.
- /input_artifacts/study_index_guidelines.md - the resolution rules and the exact shape of every output.

For each study, decide what it actually did and record it. Write one markdown file per study at
/logs/agent/records/<report>.md (keyed by the report id, e.g.
/logs/agent/records/simulation-of-groundwater-flow-in-the-silurian-a-r002.md), with these parts in order:

1. A level-1 heading: `# <title> - <index_id>`.
2. `## Study identity` - the index_id, the investigative area it sits in, and the publication series it
   was issued in (the guidelines list the series labels and their full names).
3. `## Setting and objective` - where the work happened, the resource or problem it went after, and the
   question the authors were trying to answer, specific to this study.
4. `## Findings and interpretation` - what the study measured or modeled, the results that mattered, and
   the reading the authors gave them, put in your own words rather than quoted.
5. `## Applied methods` - the techniques this study genuinely used, each one chosen from that study's
   Candidate methods block, each with a line on what it contributed. Drop the padding; do not echo the
   whole block.

When all 66 records exist, fold them into two consolidated artifacts:

6. /logs/agent/method_map.jsonld - valid JSON-LD: a top-level @context and an @graph of exactly 72 nodes,
   one per area root (6) and one per study (66). A root node carries its @id (the root_id from
   discipline_roots.csv), @type "Discipline", and a label. A study node carries its @id (the index_id),
   title, discipline, and exactly one classified_under edge to its own area's root_id. The study-node
   count in each area must match report_count in discipline_roots.csv, with nothing duplicated.

7. /logs/agent/validation_log.json - a JSON array, one object per study (66 or more), each carrying
   worker_id (a non-empty name for whoever produced it), discipline, index_id, series, and
   methods_verified. Set series to the study's real publication series, and set methods_verified to true
   only when the techniques your record lists are ones the study used and every one came from that
   study's Candidate methods block.

Judge each record only against its own study. The index_id, series, and section layout are cheap and earn
little by themselves; the value is in getting right, precisely, what the study did and by what techniques.
Avoid anything that would read the same on any water-science study, and never claim what the text does not
carry. Because the candidate blocks fold real techniques in with padding, the resolution has to come from
the study itself, not from whatever the block offers.

All 66 records are required and gaps earn nothing. Coverage is not a substitute for accuracy: a thin,
one-size, copied, or unsupported record earns no real credit just for having its file and headings in
place. Read the study behind every record; do not work from the title alone.
