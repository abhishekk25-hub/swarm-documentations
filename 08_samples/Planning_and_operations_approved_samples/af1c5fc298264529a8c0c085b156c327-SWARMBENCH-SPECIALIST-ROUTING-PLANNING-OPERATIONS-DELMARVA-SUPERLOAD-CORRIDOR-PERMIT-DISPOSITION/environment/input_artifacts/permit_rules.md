# Hauling Permits Section — Superload Corridor Disposition Rules

In force for the spring 2026 docket. Docket date **2026-04-06**. Re-rating programme window:
eight weeks, `week_index` 1 through 8, week 1 beginning **2026-04-13**.

These are the only rules that apply to this docket. A criterion that does not appear here is not a
criterion. All weights are metric tonnes, all lengths and clearances metres, all corridor positions
and detour lengths kilometres, matching the units coded in the pinned NBI extract.

---

## 1. The application as it stands

`/input_artifacts/permit_applications.csv` is what each haulier filed on the day. It is a starting
point, not the answer. `/input_artifacts/applicant_correspondence.jsonl` carries everything that
has come in since, in free prose: re-measurements, corrected gross weights, route changes,
withdrawals, and a good deal of traffic that changes nothing at all.

Work out, for each application, the figures that stand on the docket date:

- A message binds only if it was received on or before the docket date. Anything later is noted
  and ignored.
- Where two messages amend the same field, the later one governs.
- A message that states a new figure replaces the filed figure. A message that states a change to
  the filed figure (so many metres more or less) is applied to the figure on the filed
  application, not to an earlier amendment.
- A message that says nothing has changed changes nothing, whatever figures it happens to
  mention, including figures belonging to another application.
- A withdrawal ends the matter: the application is decided `WITHDRAWN`, it carries no conditions,
  no escort class beyond `NONE`, no blocking structures and no reason code, and it does not go in
  the refusal register.

Everything downstream - the path, the controlling structure, the decision, the conditions, the
escort class and the letter - runs on the figures that stand, never on the filed row.

## 2. Structure facts

Structure identity, position, geometry, condition ratings, ratings, posting status and bypass
detour length are taken from `/input_artifacts/nbi_structure_extract.json` and from nowhere else.
A structure's `corridor_id` and `kilometerpoint` fix where it sits on a corridor.

## 3. Governing condition rating

For each structure, take items `deck_condition`, `superstructure_condition`,
`substructure_condition` and `culvert_condition`. Ignore any of them coded `N`. The **governing
condition rating** is the lowest of those that carry a digit. Where all four are coded `N`, the
governing condition rating is taken as 5.

## 4. Condition derate

| Governing condition rating | Derate factor |
| --- | --- |
| 7 or above | 1.00 |
| 6 | 0.90 |
| 5 | 0.75 |
| 4 or below | 0.60 |

`derated capacity = operating_rating_t × derate factor`, rounded to one decimal.

## 5. Posting cap

Where `structure_open_posted_closed` is `P`, the derated capacity is capped at that structure's
`inventory_rating_t`. Any other value of that field leaves the derated capacity unchanged.

## 6. Interim field restrictions

`/input_artifacts/field_restriction_memos.jsonl` carries the district field memos. A memo is
evidence only for the structure whose `structure_number` it is filed under.

These are free notes written by different engineers over two years. There is no house style: a
tonnage may be written `34.0 tonnes`, `34 t` or `thirty-four tonnes`, a date may be written
`2026-11-30`, `30 November 2026`, `30 Nov 2026` or `30/11/2026`, the clauses may come in any
order, and a note may omit the inspector or the district. What matters is the act the note
performs, not the words it performs it in.

An interim gross crossing limit **binds** a structure on the docket date when all of the following
hold:

- a memo filed under that structure imposes or revises a limit and records that the District
  Engineer concurred;
- no later memo filed under that structure rescinds the limit;
- the memo's stated review-by date is not earlier than the docket date.

Where more than one binding memo exists for a structure, the one with the latest `filed_date`
governs. A limit a memo describes as recommended, proposed, requested, pending concurrence or with
concurrence withheld does not bind. A limit a memo quotes for a different structure never binds the
structure the memo is filed under. A memo that states no limit changes nothing.

**Effective capacity** is the lower of the derated (and, where applicable, posting-capped) capacity
and any binding interim limit, rounded to one decimal.

## 7. Geometry limits

- **Width limit** is `total_horizontal_clearance_m`. A coded value of 99.9 means no width limit.
- **Height limit** is `min_vertical_clearance_over_bridge_roadway_m`. A coded value of 99.99 means
  no overhead restriction.

## 8. The path of a movement

Each application in `/input_artifacts/permit_applications.csv` states one to three legs. A leg is a
corridor and an entry and exit kilometre. The **path** is every structure in the pinned extract that
lies on a named corridor with `kilometerpoint` between that leg's entry and exit kilometres
inclusive, counted once even where two legs overlap, ordered by corridor then kilometerpoint then
structure number.

The **controlling structure** is the structure on the path with the smallest
`effective capacity − gross weight`. Where two tie, the lower structure number controls.

## 9. Disposition ladder

Apply in order. The first rule that matches decides the application.

1. **`REROUTE_CLEARANCE`** — any structure on the path has a height limit below the load's overall
   height. The blocking structures are all structures on the path whose height limit is below it.
2. **`ISSUE`** — the gross weight is within effective capacity at every structure on the path and
   the overall width is within the width limit at every structure on the path.
3. **`ISSUE_WITH_CONDITIONS`** — the gross weight exceeds effective capacity nowhere, but the
   overall width exceeds the width limit somewhere.
4. **`ISSUE_WITH_CONDITIONS`** — the gross weight exceeds effective capacity somewhere, but at every
   such structure it is within 1.20 × effective capacity.
5. **`REROUTE_LOAD`** — the gross weight exceeds 1.20 × effective capacity at one or more
   structures, and every one of those structures has a `bypass_detour_km` of at least 1 and at most
   25. Those are the blocking structures, and the detour is the sum of their bypass detour lengths.
6. **`REFUSE`** — otherwise. The blocking structures are those where the gross weight exceeds
   1.20 × effective capacity.

## 10. Condition codes

Set only on `ISSUE_WITH_CONDITIONS`, from this closed list, in alphabetical order, no duplicates:

- `CENTERLINE_CROSSING`, `CRAWL_8KMH`, `NO_MEET` — all three, when the gross weight exceeds
  effective capacity at any structure on the path.
- `LANE_CLOSURE` — when the overall width exceeds the width limit at any structure on the path.
- `POLICE_ESCORT` — when the overall width exceeds 4.9 m, or when `NO_MEET` applies.
- `NIGHT_MOVE` — when the highest `average_daily_traffic` on the path is 20000 or more.

## 11. Escort class

Set for every application, whatever the decision.

- `DOUBLE` when overall width exceeds 5.5 m or gross weight exceeds 110.0 t.
- otherwise `SINGLE` when overall width exceeds 4.3 m or gross weight exceeds 60.0 t.
- otherwise `NONE`.

## 12. Weight bands

For corridor reporting, the bands are `<=45.0`, `45.1-60.0`, `60.1-80.0`, `80.1-110.0` and
`>110.0`. A corridor is passable in a band when the lowest effective capacity among that corridor's
structures is at or above the band's lower bound.

## 13. Re-rating eligibility and yield

A structure is **eligible for re-rating** when all of the following hold:

- its governing condition rating is 5 or above;
- its `structure_open_posted_closed` is `A`;
- its `design_load_code` appears in the ceiling table below;
- the resulting re-rated capacity is above its effective capacity.

| `design_load_code` | Re-rating ceiling (t) |
| --- | --- |
| 4 | 55.0 |
| 5 | 72.5 |
| 6 | 80.0 |
| 9 | 90.0 |
| A | 100.0 |

Any other code is not re-ratable. **Re-rated capacity** is the lower of the ceiling and the
structure's `operating_rating_t`, rounded to one decimal: a completed refined rating removes the
condition derate and lifts the interim restriction, and is bounded by the design load the structure
was built to.

## 14. Re-rating effort

Material class comes from `structure_type_main_material_code`: codes 1, 2, 5 and 6 are `CONCRETE`,
codes 3 and 4 are `STEEL`, code 7 is `TIMBER`, and anything else is `OTHER`.

Base effort is 2 engineer-weeks for `CONCRETE` and `TIMBER` and 3 for `STEEL` and `OTHER`. Add one
week where `number_of_spans_in_main_unit` is 4 or more, and one week where `structure_length_m` is
100.0 or more.

## 15. Re-rating programme constraints

- The programme may not spend more than **20 engineer-weeks** in total.
- Each re-rating is assigned to one engineer from `/input_artifacts/rating_engineers.csv` whose
  `specialty_class` is `ANY` or matches the structure's material class.
- A re-rating occupies consecutive week indices beginning at its stated `week_index`, and must
  finish on or before week 8.
- One engineer may not work two re-ratings in the same week, and may not be assigned more weeks in
  total than their `available_weeks`.
- A structure may appear in the programme at most once, and only if it is eligible under §12.

## 16. What a re-rating relieves

An application is **relieved** by the programme when it was decided `REROUTE_LOAD` or `REFUSE`,
every one of its blocking structures is in the programme, and re-running §8 with those structures at
their re-rated capacity yields `ISSUE` or `ISSUE_WITH_CONDITIONS`. A `REROUTE_CLEARANCE` cannot be
relieved by re-rating: refined analysis does not raise an overhead clearance.

## 17. Rating trend

`/input_artifacts/nbi_prior_deliveries.json` carries the same eighty-eight structures as FHWA
published them in the 2022 and 2023 deliveries. Compare the **2022** delivery with the pinned 2024
extract, applying §2 to each delivery's own coded items:

- `DETERIORATED` when the governing condition rating is lower in 2024 than in 2022, or the
  operating rating is lower.
- otherwise `IMPROVED` when either is higher.
- otherwise `STABLE`.

Where the 2022 delivery carries no record for a structure, it is `STABLE`.

## 18. Refusal reason codes

One code per refused or rerouted application, from this closed list:

- `HEIGHT_CLEARANCE` — decided under §8 rule 1.
- `CAPACITY_BYPASS_AVAILABLE` — decided under §8 rule 5.
- `CAPACITY_NO_BYPASS` — decided under §8 rule 6 where at least one blocking structure has a
  `bypass_detour_km` of 0.
- `CAPACITY_BYPASS_TOO_LONG` — decided under §8 rule 6 where no blocking structure has a
  `bypass_detour_km` of 0, so every one of them is bypassed only by a detour above 25 km.
