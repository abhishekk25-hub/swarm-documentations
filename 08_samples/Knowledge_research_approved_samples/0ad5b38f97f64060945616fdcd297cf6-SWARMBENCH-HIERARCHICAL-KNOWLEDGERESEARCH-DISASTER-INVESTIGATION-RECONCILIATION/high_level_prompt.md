Reconcile the official investigation records for the eleven disasters staged under
/input_artifacts. Each event directory holds two or three reports on the same event from
different federal bodies, and their published figures were never squared against each other.

Deliverables:

One JSON file per event at /logs/agent/reconciliation/<event>.json, named for the event
directory. Each file holds the event id and a list of reconciled facts. A fact carries its
category, a short summary line naming which fact it is, one entry per report that states it,
a verdict, and the arithmetic that reconciles the entries when one is needed.

A report entry gives the report file name, the value as that report frames it, and a passage
copied exactly from that report containing the value.

The verdict is one of agree_exact, agree_after_mapping, discrepant, or single_source_only.
Categories are fatalities_total, fatalities_split, injuries, damage_usd, peak_wind,
min_pressure, landfall, rainfall_max, surge_or_crest, warning_timing, outage, evacuation,
structures, tornado_or_rating, timeline_event, other.

One ledger at /logs/agent/reconciliation_ledger.csv covering every fact from every event,
with the header event,category,verdict,documents and the source file names joined by
semicolons.

Requirements: quotes must appear verbatim in the report they are attributed to, a passage may
support only one fact, and a fact may not take two entries from the same report. Cover all
eleven events, and go as deep into each as its reports support.
