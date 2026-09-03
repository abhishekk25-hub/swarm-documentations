The division navigation branch has to lodge the winter 2026-27 major-maintenance outage programme.
Seventy-two work items are on the table across the Upper Mississippi, the Illinois Waterway and the
Ohio, the districts want all of them, and the season is 119 days long. Build the programme we can
actually defend: what has to be done this winter, what we can seat inside the season without cutting
a river off longer than the rules allow, and what we are telling industry.

Work in `/workspace`. Write the finished package to the absolute `/logs/agent` paths listed below.
Do not use a relative `logs/agent` folder. Everything you need is packaged:

- `/input_artifacts/ntad_waterway_locks.json`: the pinned NTAD/USACE lock-characteristics extract.
  Chamber identity, river, river mile, chamber count, usable dimensions, district and status come
  from here and nowhere else.
- `/input_artifacts/programme_rules.md`: the programming rules in force. These are the only rules.
- `/input_artifacts/candidate_work_items.csv`: the 72 nominated work items.
- `/input_artifacts/condition_findings.jsonl`: 140 inspection findings written against them.
- `/input_artifacts/tow_commitments.csv`: 66 committed tow movements for the season.
- `/input_artifacts/bulkhead_sets.csv` and `/input_artifacts/dewatering_crews.csv`: the resources.
- `/input_artifacts/district_season_windows.csv`: each district's outage window.
- `/input_artifacts/source_manifest.json`: provenance, hashes and record counts.

## Deliverables

- `/logs/agent/chamber_assessment.csv`
- `/logs/agent/outage_programme.json`
- `/logs/agent/severance_ledger.csv`
- `/logs/agent/bulkhead_itinerary.tsv`
- `/logs/agent/deferral_register.csv`
- `/logs/agent/programme_chart.svg`
- `/logs/agent/navigation_notice.md`

### chamber_assessment.csv

One row for every candidate chamber on the three rivers, sorted by river then descending river
mile, with exactly these columns in this order:

`ndc_code,chamber_name,river,river_mile,district,chamber_count,usable_length_ft,usable_width_ft,operational_status,closure_effect_class,double_lock_tow_count,mandatory_work_item_ids,eligibility`

Use the extract's `PMSNAME` for `chamber_name` and write `river_mile` to one decimal.
`mandatory_work_item_ids` is a `;`-joined ascending list, empty when the chamber carries none.

### outage_programme.json

A single JSON object with `season`, `outages` and `summary`.

`season` carries `start` and `end`. Each entry in `outages` carries exactly:

`outage_id`, `work_item_id`, `ndc_code`, `chamber_name`, `river`, `river_mile`, `district`,
`start_date`, `end_date`, `duration_days`, `closure_effect_class`, `bulkhead_set_id`, `crew_id`,
`notice_publication_date`, `affected_tow_ids`, `finding_ids`

Outage IDs run `OP-01` upward in start-date order. Dates are ISO `YYYY-MM-DD`. `affected_tow_ids`
and `finding_ids` are JSON arrays; leave `bulkhead_set_id` an empty string when the item needs no
set. `finding_ids` must be exactly the governing findings behind that work item, meaning the findings
that put it in the programme rather than every finding filed at the chamber.

`summary` carries `outage_count`, `full_closure_count`, `restricted_passage_count`,
`total_outage_days`, `severed_days_by_river` (an object keyed by river), `mandatory_work_item_count`,
`programmed_mandatory_count`, `deferred_work_item_count` and `affected_tow_count`. Every one of
these must be recomputable from the rows you actually wrote.

### severance_ledger.csv

One row per river per season week, so three rivers by seventeen weeks gives 51 rows, sorted by river
then week, with exactly these columns:

`river,week_index,week_start,severed_days,driving_outage_ids,cumulative_severed_days,restricted_days`

`driving_outage_ids` is a `;`-joined ascending list and is empty in a week with no full closure.

### bulkhead_itinerary.tsv

Tab-separated. One row per movement leg for every set that is used, in leg order, with exactly:

`bulkhead_set_id	leg_index	from_site	to_site	outage_id	depart_date	arrive_date	system_distance_miles	travel_days	idle_days`

`leg_index` starts at 1 for each set. The first leg's `from_site` is `HOME`; afterwards it is the
`ndc_code` the set is coming from. `to_site` is the `ndc_code` it is going to.
`system_distance_miles` is written to one decimal. Sets that carry no work produce no rows.

### deferral_register.csv

One row for every work item that is not in the programme, sorted by work item ID, with exactly:

`work_item_id,ndc_code,river,condition_class,mandatory_this_season,deferral_reason_code,earliest_feasible_season,supporting_finding_ids`

`mandatory_this_season` is `TRUE` or `FALSE`. `supporting_finding_ids` is a `;`-joined ascending
list of that item's governing findings, and it carries every finding that governs the item, not
one of them. `earliest_feasible_season` is the earliest date the item could next be taken,
written `YYYY-MM-DD`; write `NONE` only where the chamber is not in service and there is no
such date. Give one reason code per row and
make it the real one. A mandatory item that would still have fitted is not deferred, it is missed.

### programme_chart.svg

A standalone schedule chart of the programme, no external references of any kind. Root
`<svg>` with `viewBox="0 0 1120 H"`. Draw one `<rect>` per programmed outage carrying
`data-outage-id`, `data-river` and `data-effect`, with `height="14"`. Place the bars on a linear
day scale across the season: `x` = 60 + 8 × (whole days from 2026-11-30 to the outage's start) and
`width` = 8 × `duration_days`. Stack them top to bottom in start-date order at
`y` = 90 + 22 × rank, so `H` = 120 + 22 × the number of outages. Each bar needs a `<text>` label
carrying its outage ID, and the chart needs a visible `<text>` naming each of the three rivers with
that river's severed-day total. The geometry is the point of the chart: a bar has to sit where its
dates say it sits.

### navigation_notice.md

The notice industry actually reads. Open with a `## Season summary` section stating the programmed
outage count, the full-closure count, the total chamber-days and the severed days on each river,
all matching the programme. Then one `## OP-nn ...` section per outage, in the same order, each
stating that outage's chamber name, river mile, district, start and end dates, effect class, notice
publication date, how many committed tows hold windows across it and which ones, the longest of
those tows in feet against the chamber's usable length, and the governing finding IDs behind the
work. Where a full closure severs a reach, say what that means for the traffic actually held.

Write each section from its own case. Sections that repeat one paragraph with the identifiers
swapped are not a notice, and a section that states a figure the programme contradicts is worse
than one that says nothing.

## Ground rules

Every ID is case-sensitive and comes from the packaged records. Do not invent chambers, tows,
findings, crews, sets, rules or thresholds. If the rules file does not contain a criterion, it is
not a criterion. Do not carry a work item into the programme twice, and do not pad the register with
rows that have no work item behind them. The seven files describe one programme and must agree with
each other on every date, count, resource and identifier. Each file must be non-empty and under
3 MB.
