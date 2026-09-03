221 blocks of carbon credit are on the table and we need 4,000,000 tonnes cancelled against the group's 2024 to 2026 CORSIA offsetting requirement. Clear them against the ICAO Council's own eligibility document rather than against what the sellers or the registries call CORSIA eligible, and give the audit committee something it can sign.

Inputs are the pinned Council documents and summary under `/input_artifacts/sources/`, the block list at `/input_artifacts/candidate_pool.csv`, the activity dossiers at `/input_artifacts/activity_dossiers.md`, and the programme labelling at `/input_artifacts/programme_labelling_extract.csv`.

Five deliverables:

`/logs/agent/clearance_register.csv`: one row per block, the five eligibility tests recorded separately, a verdict of CLEARED, REFERRED or REFUSED, and the sentence from the Council document that decides that block quoted exactly with its source id.

`/logs/agent/referrals.json`: one object per referred block, carrying the programme's position and the Council's position with a verbatim quote for each, and your recommendation.

`/logs/agent/cancellation_schedule.csv`: cleared blocks only, in ascending vintage then block id, to the 4,000,000 tonnes, splitting the final block rather than overshooting.

`/logs/agent/eligibility_map.html`: one self-contained page, every block a visible mark carrying `data-block-id`, the three verdicts readable apart, with the register and schedule embedded as JSON under the ids `register-data` and `schedule-data`.

`/logs/agent/committee_note.md`: 1,500 to 2,600 words under the headings named in `instruction.md`, including the keyed disposition table and a block-by-block argument on the referrals.

Exact column lists, heading names and table keys are in `instruction.md`. The five files must agree with each other on block ids, verdicts and tonnages.
