I run the records desk for an interagency preparedness review, and I need the official
numbers on eleven US disasters put straight before our lessons learned meeting.

Every one of these events was investigated more than once. The National Hurricane Center
writes a Tropical Cyclone Report, the National Weather Service writes a Service Assessment,
and depending on what happened, NIST, the NTSB, the USGS or FEMA writes its own report as
well. Each body counts what it is chartered to count, so the same event comes out of the
process with two or three sets of numbers that were never reconciled against each other.
Our review keeps citing whichever figure someone happened to have open, and twice now we
have put two different death tolls for the same storm on facing pages. I need one working
record that shows, fact by fact, what each report actually says and how the statements fit
together.

The corpus is staged under /input_artifacts, one directory per event, one text file per
report. Work from these files only. They are the exact documents our review cites.

/input_artifacts/ida-2021/nhc-tropical-cyclone-report.txt
/input_artifacts/ida-2021/nws-service-assessment.txt
/input_artifacts/harvey-2017/nhc-tropical-cyclone-report.txt
/input_artifacts/harvey-2017/nws-service-assessment.txt
/input_artifacts/matthew-2016/nhc-tropical-cyclone-report.txt
/input_artifacts/matthew-2016/nws-service-assessment.txt
/input_artifacts/irene-2011/nhc-tropical-cyclone-report.txt
/input_artifacts/irene-2011/nws-service-assessment.txt
/input_artifacts/florence-michael-2018/nhc-tropical-cyclone-report-florence.txt
/input_artifacts/florence-michael-2018/nhc-tropical-cyclone-report-michael.txt
/input_artifacts/florence-michael-2018/nws-service-assessment.txt
/input_artifacts/sandy-2012/nhc-tropical-cyclone-report.txt
/input_artifacts/sandy-2012/nws-service-assessment.txt
/input_artifacts/sandy-2012/fema-after-action-report.txt
/input_artifacts/joplin-tornado-2011/nws-service-assessment.txt
/input_artifacts/joplin-tornado-2011/nist-technical-investigation.txt
/input_artifacts/table-rock-lake-2018/nws-service-assessment.txt
/input_artifacts/table-rock-lake-2018/ntsb-marine-accident-report.txt
/input_artifacts/sc-floods-2015/nws-service-assessment.txt
/input_artifacts/sc-floods-2015/usgs-flood-report.txt
/input_artifacts/colorado-floods-2013/nws-service-assessment.txt
/input_artifacts/colorado-floods-2013/usgs-flood-report.txt
/input_artifacts/camp-fire-2018/nws-service-assessment.txt
/input_artifacts/camp-fire-2018/nist-technical-investigation.txt

Note that the Florence and Michael directory holds one Service Assessment covering both
storms alongside a separate report for each storm. Both storms belong in the one file named
for that directory, and each unit inside it should concern one storm, named in its summary
line.

Work in /workspace and write the deliverables to the paths below.

Write one file per event into /logs/agent/reconciliation/, named for the event directory:

/logs/agent/reconciliation/ida-2021.json
/logs/agent/reconciliation/harvey-2017.json
/logs/agent/reconciliation/matthew-2016.json
/logs/agent/reconciliation/irene-2011.json
/logs/agent/reconciliation/florence-michael-2018.json
/logs/agent/reconciliation/sandy-2012.json
/logs/agent/reconciliation/joplin-tornado-2011.json
/logs/agent/reconciliation/table-rock-lake-2018.json
/logs/agent/reconciliation/sc-floods-2015.json
/logs/agent/reconciliation/colorado-floods-2013.json
/logs/agent/reconciliation/camp-fire-2018.json

Each file is an object with an "event" string and a "units" array. A unit is one fact that
the reports of that event address, and it carries these fields.

"category", one of: fatalities_total, fatalities_split, injuries, damage_usd, peak_wind,
min_pressure, landfall, rainfall_max, surge_or_crest, warning_timing, outage, evacuation,
structures, tornado_or_rating, timeline_event, other.

"qualifier", a short phrase of your own that says which fact this is, for example the total
death toll, or the peak gust measured at the airport. This is how a reader tells two units
in the same category apart.

"sources", an array with one entry per report that states the fact. Each entry has
"document", the file name of the report as it appears above, "stated_value", the value the
way that report frames it, and "quote", a passage copied exactly as it appears in that
report and containing the value. Take the quote straight out of the file rather than
retyping it, and keep it long enough to show the fact in context, roughly one to three
sentences.

"verdict", one of: agree_exact when the reports state the same value the same way,
agree_after_mapping when they state the same underlying fact under different partitions or
units so that arithmetic or a category map connects them, discrepant when the reports give
genuinely different values, times or framings for the same fact, and single_source_only when
one report states a fact its counterpart covers the topic of but never gives.

"mapping_arithmetic", a short string showing the relation for a mapping or a discrepancy.
Write out the connection you actually derived, whether that is the component figures one
report gives adding to the combined figure the other reports, a conversion between the units
the two use, or the offset between two stated times. Use null when the verdict is agree_exact
or single_source_only.

Then write /logs/agent/reconciliation_ledger.csv over every unit in every event, with the
header row event,category,verdict,documents and one row per unit, where documents is the
file names of that unit's sources joined by semicolons in the order they appear in the unit.

What the review actually needs from this is the reconciliation, so weight your effort there.
The paired reports rarely contradict each other outright. Far more often they partition the
same total differently, one counting by cause and the other by phase of the event, or they
attribute the same measurement to different clock times, and the work is seeing that two
statements are about one fact before deciding whether they agree. A record that lists each
report's numbers side by side without saying how they relate is the state we are already in.

Three things I have to insist on because they are what makes the record usable. A quote must
appear verbatim in the report it is attributed to, since our citations get checked. A passage
may back only one unit, so if you find yourself reusing the same sentence for a second fact,
find the passage that actually states that second fact. And no unit may draw two sources from
the same report, since the point is what different bodies said.

Cover every event and go as deep into each as the reports support. Save each event file as
you finish it rather than holding the whole record to the end, so that a long run still
leaves us something usable.
