I am Elena Vasquez, senior legal counsel at the Maritime Compliance Office. Our flag-state review
programme must show, for every MLC 2006 obligation we track, which domestic instrument carries it in
each of twelve jurisdictions and what evidence supports that link as of 30 July 2026. The last
crosswalk we published mixed ratification dates with in-force domestic text, cited instruments that
had already been repealed, and treated "substantially equivalent" as fully transposed when the
statute only delegated rule-making power. The settlement that followed is why my office now
requires a crosswalk every cell of which can be traced to staged source material on this machine.

This is a transposition study with an audit trail, not a checklist. For each of forty-two MLC
provisions and each of twelve jurisdictions I hold the MLC text and the domestic sources staged for
that jurisdiction, and nothing else counts as authority. Where domestic law carries the obligation
the cell is fully or partially transposed; where no instrument accounts for it the cell is none or
unclear; where the state reserved the matter or implements through delegated legislation the cell
says so and names the instrument that carries the reservation or delegation. I would rather publish
a row with an honest gap than a row that reads smoothly and cannot be traced, and I would rather
record the affected cells as unresolved than let an untraceable mapping into the workbook.

The twelve jurisdictions are Australia (AUS), Bahamas (BHS), Canada (CAN), India (IND), Kenya
(KEN), Liberia (LBR), Malta (MLT), Marshall Islands (MHL), Philippines (PHL), Singapore (SGP),
South Africa (ZAF) and the United Kingdom (GBR). The as-of date for every transposition status,
amendment note and coverage claim is 2026-07-30. Domestic law in force after that date does not
enter the crosswalk however easy it would be to cite it.

Your working directory is /workspace and everything is staged on this machine. You have no network
access and you do not need any: the staged corpus is the only evidence the compliance office is
allowed to cite, and a provision the corpus does not support does not enter the workbook however
plausible a mapping would be. /input_artifacts/provisions_registry.csv lists the forty-two
provisions with provision_id, mlc_title, mlc_regulation and cluster_id. /input_artifacts/
jurisdictions.csv lists the twelve jurisdictions with iso3, common_name and federal_structure.
/input_artifacts/mlc_2006_authoritative.txt is the MLC 2006 consolidated text the registry
references. /input_artifacts/domestic_sources/ holds each jurisdiction's staged statutes,
regulations, orders and guidance under /input_artifacts/domestic_sources/<ISO3>/, and
/input_artifacts/common/ holds the two ILO documents that belong to no single flag, the Article 22
reporting form and the ratification compendium. /input_artifacts/
source_manifest.json lists every staged file with iso3, relative_path, instrument_type and
retrieval_note. /input_artifacts/crosswalk_standard.md is our transposition standard: how a cell
is classified, how instruments and evidence are cited, the amendment cutoff rule, and the exact
contract for every deliverable. Our pipeline reads your files with nobody in between, so follow it
literally. /input_artifacts/corpus_note.md is the archivist's account of the condition the corpus
arrived in, and it will save you mistaking a property of the evidence for a fault in your own work.

What I need back, all of it under /logs/agent. The transposition workbook at
mlc_transposition_workbook.xlsx with six sheets named exactly Mapping, Evidence, Instruments,
Amendments, Unresolved and Summary. The article lineage graph at article_lineage_graph.json
linking MLC provisions to domestic instruments across jurisdictions. The unresolved research
queue at unresolved_research_queue.csv for cells that could not be settled from staged material.
The source coverage trail at source_coverage.csv accounting for every file in source_manifest.json.
The method audit at method_audit.json documenting how the crosswalk was built and what it does not
claim. The comparative legal memorandum at comparative_legal_memorandum.md and
comparative_legal_memorandum.pdf. And twenty-four intermediate band files under /logs/agent/shards/,
one per provision band, named as section 12 of the standard specifies. Section 9 gives the shape
and exact filename of each deliverable; sections 11 through 20 govern its writing and reconciliation.

The comparative memorandum is the part I expect to be done badly, so let me say why I want it.
Worked provision by provision, this job is forty-two small jobs and the crosswalk that comes out
of it is forty-two rows without a view of the fleet. The facts that matter to the board are not
visible from any one row. The twelve jurisdictions ratified on different dates, implement through
different instrument types, and split federal and flag-state competence differently, and until you
know which structure you are holding you cannot tell whether a partial cell is ordinary or
indefensible. The same is true of delegated legislation, of recurring none cells across small
flags, and of provisions where every jurisdiction transposes through subsidiary rules rather than
primary statute. Section 18 asks for that comparative reading across all twelve jurisdictions, for
the provisions where no jurisdiction carries the obligation in primary law, and for a synthesis of
what the corpus shows that no single band shows. Every figure in it has to reconcile with the
workbook and the method audit it was drawn from, so leave it until those are settled and then
actually recompute it.

The writing has to carry the same weight as the mapping, and it has to be about the jurisdiction
in front of you. These twelve flags are twelve different legal systems, and a memorandum paragraph
that does not know which jurisdiction it discusses is no use to a reviewer. The comparative analysis
must draw evidence-backed patterns across jurisdictions rather than repeat workbook counts. An
unresolved queue entry has
to state what staged material was searched and what was missing, not that "further research is
needed." The method audit narrative has to name jurisdictions, name transposition statuses the
audit records, and state the federal-structure split in figures.

Two reconciliations are the ones the board will re-run, so they matter more to me than anything
else in the audit. Every Mapping sheet row has to appear exactly once across the twenty-four band
files with the same transposition_status, and the Summary sheet totals have to be the counts of the
Mapping rows you wrote, not a second reckoning. Recompute them from the MLC text, the domestic
sources and your own files. An audit that repeats a total it did not check is the exact failure we
settled a complaint over. The lineage graph also has to be one graph rather than twenty-four
fragments. Section 17 fixes that: one node per provision and per domestic instrument cited, edges
carrying the transposition relationship the Mapping sheet records, and no edge whose endpoints
disagree with the workbook cell they connect.

Getting the filenames and the field names right is necessary and nowhere near enough. All
forty-two provisions and all twelve jurisdictions are required, and a cell that is present but
hollow is no more use to me than a missing one. A status that is not supported by staged evidence,
an instrument cited without a manifest path behind it, a none cell rewritten as partial with
confident wording, an amendment note that ignores the as-of cutoff, a memorandum paragraph that
would fit any jurisdiction, a lineage graph whose edges disagree with the Mapping sheet, or a
Summary row that disagrees with the Mapping rows it summarizes are each worse for me than an honest
gap, because they survive a spot check and fail a real one. Where the standard cannot be met for a
provision band, say so in the Unresolved sheet and in the method audit, and withhold only a positive
legal conclusion; the required band file must still be delivered with those unresolved cells.
