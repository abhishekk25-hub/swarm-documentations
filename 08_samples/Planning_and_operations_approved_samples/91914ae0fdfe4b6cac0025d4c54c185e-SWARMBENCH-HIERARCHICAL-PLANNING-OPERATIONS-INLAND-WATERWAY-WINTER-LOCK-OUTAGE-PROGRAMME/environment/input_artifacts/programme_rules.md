# Division navigation branch: winter major-maintenance programming rules

These are the rules the division applies when it builds a winter outage programme. They are the
only rules in force. Nothing outside this file governs the programme.

## 1. Season and scope

- The winter season runs **2026-11-30 through 2027-03-28** inclusive: 119 days, 17 whole weeks
  beginning on a Monday.
- Week 1 starts 2026-11-30. Week *n* starts 2026-11-30 plus 7 × (*n* − 1) days.
- The programme covers only lock chambers on the **MISSISSIPPI**, **ILLINOIS** and **OHIO**
  rivers as those rivers are named in the pinned lock extract.

## 2. Chamber screening

For each candidate chamber, taken from the pinned extract:

- `operational_status` is `IN_SERVICE` when the extract's `STATUS` field is `1` or `2`.
  Any other value makes the chamber `OUT_OF_SERVICE`.
- `closure_effect_class`:
  - `NONE` when the chamber is `OUT_OF_SERVICE`;
  - `FULL_CLOSURE` when `NOCHMB` is 1. There is no second chamber, so closing it stops
    navigation past the site;
  - `RESTRICTED_PASSAGE` when `NOCHMB` is 2 or more. Traffic continues through the remaining
    chamber at reduced throughput.
- `eligibility` is `ELIGIBLE` for an `IN_SERVICE` chamber and `NOT_IN_SERVICE` otherwise.
  Only `ELIGIBLE` chambers may carry programmed work.

Usable chamber dimensions are the extract's `CHMBUL` (length, feet) and `CHMBUW` (width, feet).

## 3. Tow geometry

A committed tow's route is given in `route_segments` as one or more `RIVER:low-high` mileage
segments separated by `;`. A tow passes every candidate chamber whose river matches a segment
and whose river mile lies within that segment's mileage range, inclusive of both ends.

At a chamber a tow's lockage mode is:

- `SIZE_EXCLUDED` when `tow_width_ft` exceeds the usable width, or when `tow_length_ft` exceeds
  `2 × usable_length_ft − 30`;
- `SINGLE_LOCK` when `tow_length_ft` is at most the usable length;
- `DOUBLE_LOCK` otherwise. The tow has to be broken and locked through in two cuts.

A chamber's `double_lock_tow_count` is the number of committed tows that pass it and must
`DOUBLE_LOCK` there.

## 4. Condition standing

Inspection notes are supplied one JSON object per line. A note carries the date of the visit, the
inspecting party, a `survey_outcome`, an optional `supersedes` array, a note reference and the
inspector's written narrative. Inspectors do not assign condition classes; the division does, from
the measurements the notes report.

### 4.1 Weight given to a note

The division gives no weight to a note that a later survey has retired. A re-survey of a chamber
commonly retires notes written against other work items at that chamber, and the retired note
references are listed in the re-survey's `supersedes` array.

An `ABORTED` survey did not obtain a reading and carries no standing at all. Where an item has
both completed and partial-access surveys still standing, the division works from the completed
ones; partial-access notes are used only when nothing else survives for that item.

### 4.2 The measurement that counts

Each standing note reports a measurement of the governing metric for its component, taken on that
visit. Inspectors routinely record more than that in the same narrative: readings from earlier
survey cycles, which they attribute to the year taken, and readings from a different component at
the same chamber, which they name as such. Neither bears on this item's standing. The governing
metric by component is:

| Component code | Governing metric | Unit |
| --- | --- | --- |
| `MITER_GATE_DOWNSTREAM`, `MITER_GATE_UPSTREAM` | section loss | inches |
| `CULVERT_VALVE` | pitting depth | inches |
| `LOWER_SILL` | undermining | inches |
| `GUIDE_WALL` | settlement | inches |
| `HYDRAULIC_SYSTEM` | rod drift | inches |
| `BULKHEAD_SLOT` | seal-face deformation | inches |
| `CHAMBER_WALL_ARMOR` | plate separation | inches |

### 4.3 Division condition bands

The division reads a measurement as `CRITICAL` from the critical floor upward, `DEGRADED` from the
degraded floor up to the critical floor, and `MONITOR` below the degraded floor.

| Governing metric | `CRITICAL` from | `DEGRADED` from |
| --- | --- | --- |
| section loss | 0.50 in | 0.20 in |
| pitting depth | 1.50 in | 0.60 in |
| undermining | 12.0 in | 5.0 in |
| settlement | 6.0 in | 2.0 in |
| rod drift | 3.0 in | 1.0 in |
| seal-face deformation | 2.0 in | 0.75 in |
| plate separation | 1.5 in | 0.50 in |

An item's `condition_class` is the most severe band among the notes that still count for it,
ranking `CRITICAL` above `DEGRADED` above `MONITOR`. Where nothing counts for an item - every note
retired or aborted, or none reporting the governing metric - its condition class is `NONE`.

### 4.4 Mandatory work

Work on an `OUT_OF_SERVICE` chamber is never mandatory. On an `IN_SERVICE` chamber, the division
treats work as mandatory this season where any note that counts reads `CRITICAL`, or where two or
more such notes read `DEGRADED` on different visit dates, or where an item already carrying two or
more deferrals has any note reading `DEGRADED`.

The condition standing is an input to the season, not the season itself. What the division is
judged on is the programme it builds from it.

## 5. What may be programmed

Only mandatory work items may be programmed. Each programmed work item appears once.

An outage is feasible only when all of the following hold.

1. `duration_days` equals the item's `requested_duration_days`, and
   `end_date` = `start_date` + `duration_days` − 1.
2. `start_date` and `end_date` both fall inside the season **and** inside the window that
   `district_season_windows.csv` gives for the chamber's district.
3. `notice_publication_date` = `start_date` − 120 days.
4. Full closures only:
   - no outage may sever a river for more than **30 consecutive days**;
   - two full closures on the same river must be separated by at least **3 clear days** and may
     never overlap;
   - the full-closure days programmed on any one river must not exceed **70** across the season.
5. A dewatering crew is assigned. Its `crew_class` matches the item's `crew_class`, its
   `districts_served` list contains the chamber's district, the outage lies inside the crew's
   availability, and the crew is not assigned to an overlapping outage.
6. When `requires_dewatering` is `Y`, a bulkhead set is assigned. Its `bulkhead_class` matches the
   item's `bulkhead_class`, the outage lies inside the set's availability, and the set is not
   assigned to an overlapping outage. Sets that are not required are left blank.

## 6. Bulkhead movement

A bulkhead set is physical and can only be in one place. It arrives the day before an outage
starts and is released the day after that outage ends.

- `arrive_date` = the outage's `start_date` − 1 day.
- `system_distance_miles` between two points is the river mileage between them. On one river it is
  the difference in river miles. Between rivers, route through the confluences: the Illinois
  Waterway meets the Mississippi at Mississippi mile 218.0 and Illinois mile 0.0; the Ohio meets
  the Mississippi at Mississippi mile 0.0 and Ohio mile 981.0.
- `travel_days` = `system_distance_miles` ÷ 60, rounded up, minimum 1 for any move between two
  different points, and 0 when the set does not move.
- `depart_date` = `arrive_date` − `travel_days`.
- For a set's first assignment, `depart_date` must be on or after its `available_from`.
- For any later assignment, `depart_date` must be on or after the day after the previous outage's
  `end_date`.
- `idle_days` is the whole days between the set becoming free and its `depart_date`: measured from
  `available_from` for the first leg, and from the day after the previous outage's `end_date`
  afterwards.

## 7. Deferral

Every work item that is not programmed carries exactly one reason code:

- `CHAMBER_NOT_IN_SERVICE`: the chamber is `OUT_OF_SERVICE`.
- `NOT_MANDATORY`: the item is not mandatory this season.
- `NO_SEASON_WINDOW`: mandatory, but no start date puts the whole outage inside both the season
  and the district window.
- `RIVER_SEVERANCE_LIMIT`: mandatory and it fits a window, but every such placement breaks a
  full-closure rule in section 5.4 against the outages actually programmed.
- `NO_BULKHEAD_SET`: mandatory and otherwise placeable, but no bulkhead set of its class is free
  and reachable for any surviving placement.
- `NO_CREW`: mandatory and otherwise placeable, but no crew of its class serving that district is
  free for any surviving placement.

Test the codes in that order and record the first that applies. A mandatory item for which some
feasible placement still exists, against the programme as submitted, has not been validly
deferred. It should have been programmed.

## 8. Severance accounting

For each river and each of the 17 season weeks:

- `severed_days` counts the days of that week covered by at least one `FULL_CLOSURE` outage on
  that river;
- `restricted_days` counts the days covered by at least one `RESTRICTED_PASSAGE` outage on that
  river;
- `driving_outage_ids` lists the full-closure outages touching that week;
- `cumulative_severed_days` is the running total of `severed_days` for that river from week 1.

## 9. Affected traffic

A committed tow is affected by an outage when its transit window overlaps the outage dates by at
least one day **and** its route passes that chamber.
