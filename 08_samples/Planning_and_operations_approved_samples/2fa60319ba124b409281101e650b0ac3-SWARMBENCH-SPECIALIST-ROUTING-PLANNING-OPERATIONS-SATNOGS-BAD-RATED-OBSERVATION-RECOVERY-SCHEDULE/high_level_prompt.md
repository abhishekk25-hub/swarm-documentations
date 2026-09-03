We need the make-good plan for the observations that came back bad on the 22 July shift, and it has to be one the stations will actually honour. Everything you need is in `/input_artifacts`, including a note from every ground station saying what it can take during the 22-25 July window. Those notes are the part that matters and they are not tidy: a site may state several restrictions at once, and some describe arrangements that have since been cancelled or lifted, so go by everything each note actually declares for the recovery window itself.

Put everything in `/logs/agent`.

I want five things.

A station declaration register at `station_constraints.csv` covering every station in the snapshot, with a row for each restriction a station declares, quoting the operator's own words as evidence for that particular restriction.

The schedule itself at `recovery_schedule.csv`, matching bad-rated cases to later good passes. Recover as many cases as possible, and where there is a choice, take the pass that gets us back on the air soonest. No candidate may be used twice, and nothing may be booked at a station that cannot host it.

A disposition ledger at `backlog_disposition.csv` covering all 96 cases, saying for each one whether it was recovered and, if not, exactly why — distinguishing cases with no later pass at all from cases where the passes existed but the station ruled them out.

A constraint impact ledger at `constraint_impact.csv` listing every case-candidate pairing that would have worked on the observation data alone but was removed by a station's declaration, with the reason.

An operator handover at `operations_handover.md`, 1,200 to 2,800 words, covering the outcome, the constraint picture, control totals, station load, what is still open and what the next shift should chase. Be straight about what the data does and does not establish, and cite the documentation where it matters.

All five must exist under exactly those names in `/logs/agent` when you stop, and they must agree with each other. Exact column lists, reason-code vocabulary, the matching rules and the handover headings are in `instruction.md` — follow them precisely, because operations reads these as a set.
