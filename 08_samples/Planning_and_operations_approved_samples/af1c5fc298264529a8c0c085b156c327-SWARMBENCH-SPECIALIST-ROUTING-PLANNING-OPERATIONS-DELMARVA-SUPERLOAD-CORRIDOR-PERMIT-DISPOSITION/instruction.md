Handover note from the Hauling Permits Section, spring 2026 superload docket.

Seventy-two superload applications are sitting on the counter and the season starts in a
fortnight. Every one of them wants to cross bridges we are not sure of. Half the corridor file is
district memos that impose, revise, rescind or merely propose interim crossing limits, and nobody
has reconciled them since the autumn. The application table is worse: it is what the hauliers
filed on the day, and half of them have written in since with re-measurements, corrected
weights, route changes and cancellations that nobody has worked through. On top of that the
division has twenty engineer-weeks of
load-rating time for the whole programme, which is nowhere near enough to clear everything that is
blocked, so somebody has to decide what buying those weeks actually buys. I need the disposition
the section can sign and defend to an applicant who appeals it.

Work in `/workspace`. Everything is packaged and nothing is fetched. The files are:

* `/input_artifacts/nbi_structure_extract.json`, the pinned FHWA National Bridge Inventory extract
  for the eighty-eight structures on our six corridors. Every structure fact (identity, position,
  condition ratings, operating and inventory rating, posting status, clearances, spans, traffic,
  bypass detour) comes from here and from nowhere else.
* `/input_artifacts/nbi_prior_deliveries.json`, the same eighty-eight structures as FHWA
  published them in the 2022 and 2023 deliveries, for reading which way a structure has moved
  since.
* `/input_artifacts/permit_rules.md`, the rules in force for this docket. They are the only rules.
* `/input_artifacts/corridor_definitions.csv`, the six corridors, their extents and how they join.
* `/input_artifacts/permit_applications.csv`, the seventy-two applications as filed. Treat
  this as the starting position, not the answer.
* `/input_artifacts/applicant_correspondence.jsonl`, five hundred and ninety letters and emails
  the hauliers have sent in since they filed. Some amend what was filed, some withdraw the
  movement, most change nothing at all.
* `/input_artifacts/field_restriction_memos.jsonl`, three hundred and thirty-one district field
  memos. They are free prose written by different engineers over two years, so figures and dates
  are written however the writer wrote them.
* `/input_artifacts/rating_engineers.csv`, the nine load-rating engineers and their availability.
* `/input_artifacts/source_manifest.json`, provenance, hashes and record counts.

Seven files come back, at these absolute paths. Not a relative `logs/agent` folder, the absolute
`/logs/agent` paths below.

| Path | Shape | Carries |
| --- | --- | --- |
| `/logs/agent/structure_capacity_register.csv` | 88 rows | what each structure can actually carry today |
| `/logs/agent/permit_dispositions.json` | 72 entries | the decision on each application |
| `/logs/agent/rerating_programme.csv` | one row per re-rating | how the twenty engineer-weeks are spent |
| `/logs/agent/corridor_bottleneck_ledger.tsv` | 30 rows | where each corridor gives out, band by band |
| `/logs/agent/refusal_register.csv` | one row per application not issued | why, and whether re-rating would fix it |
| `/logs/agent/capacity_profile.svg` | one chart | the corridor capacity picture |
| `/logs/agent/permit_decision_letter.md` | the letter | what each applicant is told |

The seven files describe one docket. They must agree with each other on every identifier, figure,
count and date.

**structure_capacity_register.csv.** One row for every structure in the pinned extract, sorted by
`corridor_id`, then ascending `kilometerpoint`, then `structure_number`. Header exactly:

```
structure_number,corridor_id,kilometerpoint,route_label,county,facility_carried,features_intersected,year_built,design_load_code,operating_rating_t,inventory_rating_t,governing_condition_rating,condition_derate_factor,posting_status,standing_restriction_t,governing_memo_id,effective_capacity_t,width_limit_m,height_limit_m,bypass_detour_km,material_class,rerate_eligible,rerated_capacity_t,rerate_engineer_weeks,condition_trend
```

Write `kilometerpoint` to three decimals and `condition_derate_factor` to two.
`standing_restriction_t`, `effective_capacity_t`, `operating_rating_t`, `inventory_rating_t`,
`rerated_capacity_t` and `width_limit_m` go to one decimal, `height_limit_m` to two.
`posting_status` is the extract's own `structure_open_posted_closed` code and `rerate_eligible` is
`TRUE` or `FALSE`. Leave `standing_restriction_t` and `governing_memo_id` empty where no interim
limit stands, and `rerated_capacity_t` empty where the structure is not eligible.
`governing_memo_id` is the single memo the rules make govern, not every memo filed against the
structure. `condition_trend` is `DETERIORATED`, `IMPROVED` or `STABLE`, read off the prior
deliveries against the pinned extract.

**permit_dispositions.json.** One JSON object with `docket_date`, `dispositions` and `summary`.
Each entry in `dispositions` carries exactly these keys:

```
application_id  applicant  gross_weight_t  structures_crossed  controlling_structure
controlling_headroom_t  decision  condition_codes  escort_class  blocking_structures
detour_km  refusal_reason_code  governing_memo_ids
```

Entries run in ascending `application_id`. `gross_weight_t` is the weight that stands after the
correspondence, not the filed figure. `controlling_headroom_t` is that structure's effective
capacity less the gross weight, to one decimal, so it is negative where the load is over the
structure. `structures_crossed` is a JSON array in path order.
`condition_codes` and `blocking_structures` are JSON arrays, ascending and without repeats, empty
where the rules put nothing in them. `governing_memo_ids` is the ascending, de-duplicated list of
the governing memos of those structures on the path that carry a standing limit.
`refusal_reason_code` is an empty string on an issued application, and `detour_km` is `0.0` except
on a load reroute. A withdrawn application is decided `WITHDRAWN`: it carries no condition codes,
no blocking structures, no reason code, an escort class of `NONE`, a controlling structure of `""`
and a headroom of `0.0`, and it does not appear in the refusal register. `summary` carries exactly:

```
application_count  issued_count  issued_with_conditions_count  reroute_load_count
reroute_clearance_count  refused_count  withdrawn_count  structures_assessed
structures_with_standing_restriction  distinct_controlling_structures  total_detour_km
relieved_application_count
```

Every one of those must be recomputable from the rows you actually wrote.

**rerating_programme.csv.** One row per structure you re-rate, sorted by `week_index` then
`structure_number`. Header exactly:

```
structure_number,corridor_id,material_class,engineer_id,week_index,engineer_weeks,capacity_before_t,capacity_after_t,applications_relieved,relieved_application_ids
```

`relieved_application_ids` is a `;`-joined ascending list without repeats, empty where the row
relieves nothing, and `applications_relieved` is its length. An application that needs two
structures re-rated is attributed to whichever of them finishes last, meaning the highest
`week_index + engineer_weeks`, and on a tie the lower structure number. No application may be
claimed on more than one row.

**corridor_bottleneck_ledger.tsv.** Tab-separated. Six corridors by five weight bands, thirty
rows, sorted by `corridor_id` then by the band order given in the rules. Header exactly:

```
corridor_id	weight_band	band_ceiling_t	structures_below_ceiling	lowest_effective_capacity_t	bottleneck_structure	applications_in_band	applications_blocked_on_corridor	detour_available
```

`band_ceiling_t` is `45.0`, `60.0`, `80.0`, `110.0` and `999.9` for the five bands in order.
`structures_below_ceiling` counts that corridor's structures whose effective capacity is below the
ceiling. `bottleneck_structure` is the corridor's lowest-capacity structure, ties to the lower
structure number. `applications_in_band` counts applications whose gross weight falls in the band
and whose path touches this corridor, and `applications_blocked_on_corridor` counts those of them
with a blocking structure on this corridor. `detour_available` is `TRUE` when the bottleneck
structure's bypass detour is at least 1 km and at most 25 km.

**refusal_register.csv.** One row for every application not issued, meaning the clearance
reroutes, the load reroutes and the refusals, sorted by `application_id`. Header exactly:

```
application_id,decision,refusal_reason_code,blocking_structures,shortfall_t,detour_km,rerate_would_relieve,earliest_relief_week,supporting_memo_ids
```

`blocking_structures` and `supporting_memo_ids` are `;`-joined ascending lists without repeats.
`shortfall_t` is the gross weight less the lowest effective capacity among the blocking
structures, to one decimal, and `0.0` on a clearance reroute. `rerate_would_relieve` is `TRUE` or
`FALSE` on the evidence, whether or not your programme actually does it.
`earliest_relief_week` is the week the last of that application's blocking structures completes
under the programme you submitted, and empty where the programme does not relieve it.

**capacity_profile.svg.** A standalone chart with no external references of any kind. Root `<svg>`
with `viewBox="0 0 1200 780"`. Draw one `<rect>` per register row carrying `data-structure`,
`data-corridor` and `data-role`. `data-role` is `RERATED` where the structure is in your
programme, otherwise `BOTTLENECK` where it is its corridor's bottleneck, otherwise `NORMAL`. Lanes
run in ascending `corridor_id` order with rank 0 to 5. For each bar, `width` is `6`, `height` is
the structure's effective capacity rounded to the nearest whole number, `x` is
80 + 20 × `kilometerpoint`, and `y` is 170 + 110 × lane rank − `height`. The geometry is the point
of the chart: a bar has to sit where its corridor and kilometerpoint say it sits and stand as tall
as its capacity. Each lane needs a visible `<text>` naming its `corridor_id` and that corridor's
lowest effective capacity to one decimal, and the chart needs a visible `<text>` stating the total
engineer-weeks the programme spends.

**permit_decision_letter.md.** Open with a `## Docket summary` section stating the application
count, each of the six decision counts, how many structures carry a standing interim limit, the
total engineer-weeks programmed and how many applications the programme relieves, all matching the
other six files. Then one `## APP-nnn ...` section per application, in ascending application
order. Each section states that application's applicant and commodity, its gross weight, overall
width and height, the corridors it runs on, how many structures its path crosses, its controlling
structure and what that structure can carry, and the decision. Where the decision is not a plain
issue, name the blocking structures and say what actually stops the move. Where a standing interim
limit governs any structure on the path, name the memo it comes from. Write each section from its
own case. Sections that repeat one paragraph with the identifiers swapped are not a letter, and a
figure that contradicts the disposition is no use to anybody.

A few things will get the packet sent back. An identifier that is not in the packaged records:
every structure number, application id, memo id and engineer id is case-sensitive and comes from
the file. A criterion, threshold or test that `permit_rules.md` does not state. A structure
assessed twice, an application disposed twice, or a refusal row for an application that was
issued. A programme that spends more than twenty engineer-weeks, puts an engineer on two
re-ratings in the same week, gives work to an engineer whose specialty does not cover it, runs
past week eight, or re-rates a structure the rules do not make eligible. And any of the seven
files empty, missing, or over 3 MB.
