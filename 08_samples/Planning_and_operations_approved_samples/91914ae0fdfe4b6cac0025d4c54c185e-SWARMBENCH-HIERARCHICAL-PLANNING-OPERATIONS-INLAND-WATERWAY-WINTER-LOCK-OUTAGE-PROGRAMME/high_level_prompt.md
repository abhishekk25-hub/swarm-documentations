Lodge our winter 2026-27 lock maintenance outage programme. Season is 2026-11-30 to 2027-03-28.
Everything is in `/input_artifacts`: the pinned NTAD lock extract, the 72 nominated work items, the
140 inspection findings, the 66 committed tows, the crews, the bulkhead sets, the district windows,
and the rules file. The rules file is the only rulebook; do not import criteria from anywhere else.

Put all seven files in `/logs/agent`:

- `chamber_assessment.csv`: every candidate chamber on the Mississippi, Illinois and Ohio, with its
  closure effect class, usable dimensions, how many committed tows have to double-lock there, and
  which of its work items are mandatory this season.
- `outage_programme.json`: season block, one entry per programmed outage (dates, duration, effect
  class, crew, bulkhead set, notice date, affected tows, governing findings), and a summary block
  that reconciles with those entries.
- `severance_ledger.csv`: river by week for all 17 weeks: severed days, restricted days, which
  outages drive them, running severed total.
- `bulkhead_itinerary.tsv`: each set's legs in order, with distance, travel days and idle days.
- `deferral_register.csv`: every work item not programmed, with its condition class, whether it was
  mandatory, and one honest reason code.
- `programme_chart.svg`: standalone schedule chart, bars on a linear day scale, no external refs.
- `navigation_notice.md`: season summary plus one section per outage written for industry.

Exact column orders and the chart geometry are set out in the task file; follow them.

Only mandatory work goes into the programme. Do not sever a river past the limits. If something
mandatory cannot be seated, defer it and say honestly why, but do not defer work that would still
have fitted. The seven files describe one programme and have to agree with each other. No invented
chambers, tows, findings or thresholds.
