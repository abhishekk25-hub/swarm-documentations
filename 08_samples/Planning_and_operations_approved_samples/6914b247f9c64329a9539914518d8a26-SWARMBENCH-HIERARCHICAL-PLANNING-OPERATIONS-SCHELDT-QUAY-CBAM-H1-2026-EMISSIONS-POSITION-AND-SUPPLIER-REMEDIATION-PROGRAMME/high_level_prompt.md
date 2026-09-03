Settle our carbon border position for consignments released between 1 January and 30 June 2026 and
give me the package below. The case file and the pinned tables are under `/input_artifacts/`; work
in `/workspace` and write everything to `/logs/agent/`.

Eight files, exact paths, and they have to agree with each other.

`/logs/agent/consignment_ledger.csv`, one row per goods line: whether it is inside the mechanism
and on what ground, the country of origin that governs and on what ground, net mass in tonnes, the
basis on which its emissions are figured, the direct, indirect and applied specific emissions, the
embedded emissions, and a document identifier with a verbatim passage from it behind the row.

`/logs/agent/installation_dossier.csv`, one row per installation: the reporting period, activity
level and attributed emissions, the own and precursor components of its specific emissions and
their sum, the governing verification report, whether we may rely on the communication, and the
first condition that fails.

`/logs/agent/precursor_chain.csv`, one row per reported precursor, with the consumption per tonne,
the basis its figure rests on, and what it contributes.

`/logs/agent/carbon_price_schedule.csv`, one row per claim: converted amount, admitted or not, the
condition that fails, the deduction in tonnes and the importers it reaches.

`/logs/agent/importer_position.csv`, one row per importer: lines and cumulative mass, threshold
status, embedded and adjusted emissions, deduction, certificates due and to buy.

`/logs/agent/remediation_programme.csv`, one row per unusable communication: action, slots,
earliest wave, exposure released, rank, wave assigned or the reason it was not.

`/logs/agent/position_memo.md`, at least 6,000 characters.

`/logs/agent/exposure_exhibit.md`, at least 2,000 characters.

Word count: 250.
