# Study-index resolution rules and output shape

## What a resolved record is

Each record stands in for one report inside the index. Someone who never opens the PDF should be able to
read the record and know where the study took place and what it investigated, what it found, and which
field, laboratory, and modeling methods the study ran on. Compose the prose yourself. A short quoted
phrase is fine, but a record that is mostly lifted text has done none of the resolution work. So has a
record that names the study area and then states what would be true of any water-science report.

## Reading the report

Every bundle at `/input_artifacts/reports/<report>.md` is the full report followed by a
`## Candidate methods` pool. That pool is a menu, not an answer key: it folds methods the study used
together with unrelated methods pulled from other corners of earth science. Only the report itself tells
you which ones it relied on. Read for the study area and setting, the resource or problem under
investigation, the objective, the key results and measured quantities, the interpretation, and the
methods the study actually applied.

## The five parts of every record file

`/logs/agent/records/<report>.md`, in this order:

1. `# <title> - <index_id>` — level-1 heading.
2. `## Study identity` — index id; discipline (one of the six); publication series, named as the series
   the report was actually issued in (Scientific Investigations Report, Open-File Report, Professional
   Paper, Techniques and Methods, Scientific Investigations Map, Circular, Data Series, and the like).
3. `## Setting and objective` — the study area/setting, the resource or problem, and the objective,
   grounded in the report and specific to it.
4. `## Findings and interpretation` — the key results, measured or modeled quantities, and the
   interpretation, composed yourself and faithful to the report.
5. `## Applied methods` — the field/laboratory/modeling methods the study used, each drawn from this
   report's candidate pool, each with a short note on the part it played. List every method the study
   genuinely relied on (most studies combine several substantive methods, not just a single routine
   reconnaissance technique). Do not include decoys; do not paste the pool.

## method_map.jsonld

Valid JSON-LD. Top-level `@context`, then `@graph` of exactly 72 nodes:

- 6 discipline root nodes: `{"@id": "<root_id>", "@type": "Discipline", "label": "<discipline>"}` using
  the root ids from `discipline_roots.csv` verbatim.
- 66 report nodes: `{"@id": "<index_id>", "title": "...", "discipline": "...",
  "classified_under": "<root_id of its discipline>"}`. Exactly one `classified_under` edge per report,
  pointing to its own discipline's root. The number of report nodes in each discipline must match the
  report_count column in `discipline_roots.csv`. No duplicate report nodes.

## validation_log.json

A JSON array, one object per report (>= 66), each:
`{"worker_id": "...", "discipline": "...", "index_id": "...", "series": "...",
"methods_verified": true|false}`. `series` is the report's actual publication series. `methods_verified`
is true only when your record's listed methods are ones the study applied and all came from that report's
candidate pool.

## No credit for shortcuts

Missing records score zero. So do records that copy the report, that are padded or mechanically mangled
to slip past copy detection, that restate the title without substance, or that assert what the report
does not support. Coverage without accuracy earns nothing.
