Maritime Compliance Office
MLC 2006 domestic transposition crosswalk standard, revision 2
Legal records office, flag-state review programme

This standard is what our publishing pipeline reads. Every rule below is applied literally by the
pipeline and by the method audit, so follow it to the letter. Where a value is described as
computed, compute it; where it is described as written, write it yourself.

1. What we hold, and what is authoritative

The crosswalk maps forty-two MLC 2006 provisions across twelve flag jurisdictions as of 2026-07-30.

1.1 /input_artifacts/provisions_registry.csv lists the forty-two provisions with columns
provision_id, mlc_title, mlc_regulation, mlc_standard, cluster_id and band_id. Provision order for
every deliverable is ascending provision_id, P001 to P042. There are four clusters C1 to C4 and
twenty-four provision bands B01 to B24, six bands per cluster.

1.2 /input_artifacts/jurisdictions.csv lists the twelve jurisdictions with columns iso3,
common_name and federal_structure. Jurisdiction order for every deliverable is the iso3 order
AUS, BHS, CAN, IND, KEN, LBR, MLT, MHL, PHL, SGP, ZAF, GBR.

1.3 /input_artifacts/mlc_2006_authoritative.txt is the consolidated MLC 2006 text. It is the
authority for what each provision requires. Domestic wording that the staged corpus does not carry
does not enter the crosswalk, however plainly it exists in national law outside the staging.

1.4 /input_artifacts/domestic_sources/<ISO3>/ holds each jurisdiction's staged instruments.
/input_artifacts/source_manifest.json lists every staged file with iso3, relative_path,
instrument_type, in_force_as_of and retrieval_note. Section 14 says what the coverage trail owes
the manifest.

1.5 The as-of cutoff is 2026-07-30 for every transposition status, amendment note and in-force
claim. Instruments whose staged text shows repeal or replacement after that date are treated as in
force on the cutoff only where the file itself says they were in force on that date.

2. Provision bands

Each provision band is the smallest partition of the crosswalk research, and each band is written
up in one band file.
The band assignments are fixed in provisions_registry.csv via band_id.

    Cluster C1, minimum requirements for seafarers (P001 to P011):
        B01: P001, P002
        B02: P003, P004
        B03: P005, P006
        B04: P007, P008
        B05: P009, P010
        B06: P011

    Cluster C2, conditions of employment (P012 to P021):
        B07: P012, P013
        B08: P014, P015
        B09: P016, P017
        B10: P018, P019
        B11: P020
        B12: P021

    Cluster C3, accommodation, food, medical and welfare (P022 to P031):
        B13: P022, P023
        B14: P024, P025
        B15: P026, P027
        B16: P028, P029
        B17: P030
        B18: P031

    Cluster C4, compliance and enforcement (P032 to P042):
        B19: P032, P033
        B20: P034, P035
        B21: P036, P037
        B22: P038, P039
        B23: P040, P041
        B24: P042

A band covers every provision it lists across all twelve jurisdictions. Five hundred four cells
exist in total: forty-two provisions times twelve jurisdictions.

3. Transposition status

For each provision_id and iso3 pair assign exactly one transposition_status from:

    full          staged domestic law carries the MLC obligation in terms that account for it
    partial       staged domestic law carries part of the obligation or qualifies it materially
    none          no staged instrument accounts for the obligation
    delegated     primary law empowers subsidiary legislation and the staged subsidiary text carries
                  the obligation
    reserved      staged ratification or reservation material records a formal reservation
    unclear       staged material is insufficient to classify and the gap is recorded honestly

Every cell must name at least one domestic instrument in Instruments unless the status is none.
Every cell except none must cite at least one evidence passage in Evidence unless the Unresolved
sheet records why evidence could not be located.

Every Mapping notes value is 25 to 100 words of authored, provision-specific legal analysis.
For a none or unclear finding, an Unresolved row is mandatory and must document the staged files
searched; a negative or uncertain status is not supported merely by the absence of Evidence rows.

4. Instrument citation

4.1 An instrument row names one domestic legal instrument cited in the crosswalk. instrument_id is
a stable token you assign, unique across the workbook, formed as <ISO3>-I<number> with three-digit
number per jurisdiction starting at 001.

4.2 instrument_title is the short title as the staged file carries it. instrument_type is one of
statute, regulation, order, circular, guidance, declaration, ratification, reservation and equals
the instrument_type for that path in source_manifest.json. manifest_path is the
relative_path from source_manifest.json for the staged file that attests the instrument. citation
is the citation form the jurisdiction uses in the staged material, or the section reference where
no formal citation exists. A title must contain at least two alphanumeric tokens. A citation must
contain at least two alphanumeric tokens, or a section/paragraph symbol followed by a number. Both
values must occur in the staged source after the normalisation in section 8; generic one-word labels
such as "Act" or "section" are not identifying metadata.

4.3 Every one of the twelve jurisdictions carries at least one instrument row. The corpus stages
domestic maritime law for all twelve, so a jurisdiction with no instrument row is read as research
that was not done rather than as a jurisdiction with no law.

4.4 in_force_on_cutoff is true when the staged file supports that the instrument was in force on
2026-07-30, and false otherwise. in_force_note carries the note: one sentence saying what the staged
file shows about force when in_force_on_cutoff is false, and empty when it is true.

5. Evidence passages

5.1 An evidence row ties one Mapping cell to one quoted passage from staged material. evidence_id
is unique across the workbook, formed as <provision_id>-<ISO3>-E<number> with two-digit number per
cell starting at 01.

5.2 passage_text is a verbatim excerpt of fifteen to one hundred twenty words from the staged
file. manifest_path names the file the excerpt comes from. location is the section, rule or
paragraph identifier the staged file gives, or "unnumbered" when it does not. The manifest_path
has to be a file the manifest records for that row's own iso3, or one of the three files the
manifest records under iso3 GLOBAL. A passage taken from another jurisdiction's material does not
evidence this cell however apt the wording is.

5.3 relevance_note is one or two sentences in your own prose stating which part of the MLC
obligation the passage carries. Copying the MLC text instead of writing the note fails review.

6. Amendment notes

6.1 An amendment row records a change to a cited instrument that affects how the provision reads on
the cutoff. instrument_id is the instrument_id of a row that appears on the Instruments sheet; an
amendment to an instrument the crosswalk never cites has no place here. amendment_id is unique,
formed as <instrument_id>-A<number>.
The number is a positive integer, begins at 1 for each instrument, and increases without gaps.

6.2 amending_instrument is the title or number of the amending instrument exactly as the staged
material carries it. effect_on_provision is a substantive sentence of at least ten words on how the amendment changes the transposition
reading for the provision it concerns. manifest_path is the relative_path from source_manifest.json
for the staged file that carries the amendment, so every amendment row is anchored to the corpus the
same way an instrument row is. The described effect must use at least three substantive terms that
occur in that staged source; generic amendment boilerplate is not a grounded effect.

Every material amendment, commencement provision or effective-date change visible in the staged
sources that affects a cited instrument or its classification at the cutoff must be represented in
the Amendments sheet and linked from each affected shard cell. Do not list source references that
have no bearing on a cited instrument or cutoff classification.

6.3 effective_date is ISO 8601 yyyy-mm-dd and has to be a real calendar date the staged file
supports. after_cutoff is a boolean that is true exactly when effective_date falls after 2026-07-30
and false on every other row; a row whose after_cutoff disagrees with its own effective_date is
treated as an amendment note the pipeline cannot read. Where after_cutoff is true,
effect_on_provision has to say that the amendment falls after the cutoff and does not change the
status reported for the provision.

7. Unresolved cells

7.1 A cell belongs on the Unresolved sheet when transposition_status is none or unclear, or when
evidence could not be located despite searching every manifest file for that jurisdiction.

7.2 Each unresolved row carries provision_id, iso3, reason_code and research_note. reason_code is
one of missing_source, ambiguous_text, split_competence, after_cutoff_only, not_searchable.

7.3 research_note is 40 to 100 words naming which staged files were searched and what was missing.
A note that says only that further research is needed fails review.

8. Normalisation before comparison

Before comparing MLC wording to domestic wording for your own notes, fold whitespace to single
spaces, normalise Unicode to NFKC, and lower-case for comparison only. Catalogue and evidence
passages remain verbatim from the staged files.

9. Deliverables

Everything the pipeline reads goes under /logs/agent, at these paths and under these names.

A field carried with an empty value is not a field the pipeline can read unless this standard
expressly permits the empty value: in_force_note is empty when the instrument is in force;
instrument_ids may be empty only under rule 15; evidence_ids and amendment_ids may be empty when
the cell has no corresponding rows; amendments and unresolved lists may be empty when research
supports that result; and reconciliation.mismatches is empty when reconciliation succeeds. Every
other named string holds text, and every count that stands for work done reflects the rows written.
A file whose keys are all present and whose values are all blank is treated as not delivered.

Numbers shown inside the examples below show the type of the field, not its value.

9.1 /logs/agent/shards/SHARD-<cluster>-<band>.json, twenty-four band files, one per band, each
carrying the SHARD- filename prefix the office has used since revision 1:

    SHARD-C1-B01.json through SHARD-C1-B06.json
    SHARD-C2-B07.json through SHARD-C2-B12.json
    SHARD-C3-B13.json through SHARD-C3-B18.json
    SHARD-C4-B19.json through SHARD-C4-B24.json

Each band file is one JSON object:

    {"cluster_id": "C1", "band_id": "B01", "as_of": "2026-07-30",
     "provisions": ["P001", "P002"],
     "cells": [ {
        "provision_id": "P001", "iso3": "AUS", "transposition_status": "full",
        "instrument_ids": ["AUS-I001"], "evidence_ids": ["P001-AUS-E01"],
        "amendment_ids": [], "notes": ""
     } ],
     "instruments": [ {
        "instrument_id": "AUS-I001", "instrument_title": "...",
        "instrument_type": "statute", "manifest_path": "...",
        "citation": "...", "in_force_on_cutoff": true, "in_force_note": ""
     } ],
     "evidence": [ {
        "evidence_id": "P001-AUS-E01", "provision_id": "P001", "iso3": "AUS",
        "manifest_path": "...", "location": "...",
        "passage_text": "...", "relevance_note": "..."
     } ],
     "amendments": [ {
        "amendment_id": "AUS-I001-A1", "instrument_id": "AUS-I001",
        "amending_instrument": "...", "effective_date": "2019-03-01",
        "after_cutoff": false, "manifest_path": "...", "effect_on_provision": "..."
     } ],
     "unresolved": [],
     "band_summary": "..."}

Every provision in the band appears once per jurisdiction in cells. band_summary is 60 to 120 words
on what this band's mapping found, written from the band's own cells only. It has to name at least
two of the band's own provision_ids and at least two iso3 codes, and it has to read as that band's
own findings: two band files whose summaries are substantially the same text are both rejected, so a
paragraph padded to the word count and reused across bands earns nothing.

Each shard cell's notes value is the same authored note later published for that cell in Mapping.
Each amendment_id in a shard cell resolves to an amendment object in that shard and to the final
Amendments sheet, and that amendment's instrument_id is one of the cell's instrument_ids. Across
the twenty-four shards, every amendment object published to the workbook is referenced by at least
one affected cell.

9.2 /logs/agent/mlc_transposition_workbook.xlsx, one workbook with six sheets:

    Mapping       one row per cell: provision_id, iso3, transposition_status, instrument_ids
                  (semicolon-separated), primary_citation, notes
    Evidence      one row per evidence row across all band files
    Instruments   one row per instrument row across all band files
    Amendments    one row per amendment row across all band files
    Unresolved    one row per unresolved cell across all band files
    Summary       one row per provision_id with counts of cells by transposition_status and
                  unresolved_count

For Mapping, primary_citation equals the citation of one Instruments row named in instrument_ids;
on a none cell with no instrument_ids it is the single word none.

Every sheet carries a header row with the column names exactly as above. Five hundred four rows on
Mapping. Summary has forty-two rows.

9.3 /logs/agent/article_lineage_graph.json, one JSON object:

    {"as_of": "2026-07-30",
     "nodes": [ {"node_id": "P001", "node_type": "mlc_provision", "label": "..."},
                {"node_id": "AUS-I001", "node_type": "domestic_instrument", "iso3": "AUS",
                 "label": "..."} ],
     "edges": [ {"edge_id": "E001", "source": "P001", "target": "AUS-I001",
                 "relationship": "transposed_full", "provision_id": "P001", "iso3": "AUS"} ],
     "meta": {"node_count": 0, "edge_count": 0}}

relationship is one of transposed_full, transposed_partial, transposed_delegated, reserved or
unclear. Every Mapping row with a status other than none has at least one edge; a none row has no
edge. Each MLC node uses node_id equal to its provision_id. Each domestic node uses node_id equal
to an Instruments.instrument_id and carries that instrument's iso3. Every edge source is its
provision_id node and every target is an instrument_id cited by that same Mapping cell. Edge IDs
and node IDs are unique. Edges must agree with the Mapping status for the same cell.

9.4 /logs/agent/unresolved_research_queue.csv with header:

    queue_id,provision_id,iso3,reason_code,research_note,priority

One row per Unresolved sheet row, carrying the same reason_code that sheet gives for the same cell.
queue_id is Q001 upward in provision order then iso3 order, so the first row is Q001, the second
Q002 and so on with no gaps. priority is deterministic: high for wage provisions P012-P014 and
accommodation provisions P022-P025; medium for the other Title 2 and Title 3 provisions P009-P027;
and low for P001-P008 and P028-P042.

9.5 /logs/agent/source_coverage.csv with header:

    iso3,manifest_path,instrument_type,consulted,provision_ids_touched,notes

One row per entry in source_manifest.json. consulted is true exactly when an Evidence or Instruments
row cites that file by manifest_path. provision_ids_touched lists semicolon-separated provision_ids
from Evidence rows citing the file, or the single word none. instrument_type is exactly the value
for that path in source_manifest.json. notes is 5 to 80 words specific to the source: it explains
how a consulted source was used or why an unconsulted source was not cited. Every field carries a
value; no cell in this file is left blank.

9.6 /logs/agent/method_audit.json, one JSON object:

    {"as_of": "2026-07-30", "jurisdictions": 12, "provisions": 42,
     "shards_expected": 24, "shards_received": 0,
     "cells_total": 504, "cells_mapped": 0, "cells_unresolved": 0,
     "status_counts": {"full": 0, "partial": 0, "none": 0, "delegated": 0,
                       "reserved": 0, "unclear": 0},
     "federal_structure_counts": {"unitary": 0, "federal": 0, "mixed": 0},
     "coverage": {"manifest_files": 0, "files_consulted": 0},
     "reconciliation": {"mapping_rows": 504, "shard_cell_rows": 504, "mismatches": []},
     "narrative": {"scope": "...", "what_the_audit_found": "...",
                   "what_to_research_next": "..."}}

Recompute every count from the workbook and band files. narrative fields are your own prose: scope 90 to
200 words, what_the_audit_found 120 to 260 words naming at least four jurisdictions and three
transposition statuses, what_to_research_next 90 to 200 words prioritising real unresolved rows.
cells_unresolved is the number of distinct provision_id/iso3 keys on the Unresolved sheet and
cells_mapped is 504 minus cells_unresolved. coverage.files_consulted is the number of
source_coverage.csv rows whose consulted value is true. All six status_counts equal the counts
recomputed from Mapping, and shards_received equals the number of required shard files delivered.

9.7 /logs/agent/comparative_legal_memorandum.md, markdown with sections:

    # MLC 2006 Domestic Transposition Comparative Memorandum
    ## Executive summary
    ## Jurisdiction profiles (one subsection per iso3, in csv order)
    ## Cross-jurisdiction themes
    ## Provision clusters (one subsection per cluster_id)
    ## Recommendations

Executive summary is 150 to 250 words. Each jurisdiction profile is 100 to 180 words naming at
least two provisions by provision_id and at least one transposition_status the workbook records
for that jurisdiction. Cross-jurisdiction themes is 200 to 350 words on patterns visible only when
all twelve jurisdictions are read together.

9.8 /logs/agent/comparative_legal_memorandum.pdf, a PDF whose text layer can be read back, carrying
the same section structure and substantially the same wording as the markdown memorandum. The PDF
must span at least three pages, carry at least eight hundred extractable words in its text layer,
and include the title line "MLC 2006 Domestic Transposition Comparative Memorandum" on the first
page.

10. Comparative synthesis

The memorandum's comparative analysis draws evidence-backed patterns across jurisdictions and
provision groups. It does not satisfy this standard by repeating workbook counts or substituting
jurisdiction names into otherwise identical profiles.

11. Writing

Prose fields must be about the jurisdiction or provision they report on. A band_summary that would
fit any band, a research_note that does not name staged files, or a memorandum profile copied between
jurisdictions with names changed fails review. Quote nothing longer than a phrase in your own prose
except in passage_text, which must be verbatim from staged material.

12. Band file name index

    B01 -> SHARD-C1-B01.json     B13 -> SHARD-C3-B13.json
    B02 -> SHARD-C1-B02.json     B14 -> SHARD-C3-B14.json
    B03 -> SHARD-C1-B03.json     B15 -> SHARD-C3-B15.json
    B04 -> SHARD-C1-B04.json     B16 -> SHARD-C3-B16.json
    B05 -> SHARD-C1-B05.json     B17 -> SHARD-C3-B17.json
    B06 -> SHARD-C1-B06.json     B18 -> SHARD-C3-B18.json
    B07 -> SHARD-C2-B07.json     B19 -> SHARD-C4-B19.json
    B08 -> SHARD-C2-B08.json     B20 -> SHARD-C4-B20.json
    B09 -> SHARD-C2-B09.json     B21 -> SHARD-C4-B21.json
    B10 -> SHARD-C2-B10.json     B22 -> SHARD-C4-B22.json
    B11 -> SHARD-C2-B11.json     B23 -> SHARD-C4-B23.json
    B12 -> SHARD-C2-B12.json     B24 -> SHARD-C4-B24.json

13. Summary sheet computation

For each provision_id, status_counts count Mapping rows for that provision by transposition_status.
unresolved_count is the number of Mapping rows for that provision whose status is unclear plus
Unresolved sheet rows for that provision. Summary totals must equal Mapping counts.

14. Source coverage trail

Every manifest entry must appear in source_coverage.csv. A false consulted value means that no
Evidence or Instruments row cites the file; notes explain why it was not used.

Both audit fields are claims we check against the workbook rather than take on trust. consulted is
true for exactly those files an Evidence or Instruments row cites by manifest_path, and false for
every file no row cites. provision_ids_touched is exactly the set of provision_ids on the Evidence
rows citing that file, semicolon-separated, and is the single word none when no Evidence row cites
it. A coverage row that overstates or understates either field is a wrong row.

15. Reconciliation rules

Before publishing the workbook, every cell in every band file must appear exactly once on the Mapping
sheet with the same transposition_status. Every id in a Mapping row's instrument_ids must name an
Instruments row for that same iso3; only a none cell may leave instrument_ids empty.
The lineage graph must contain an edge for every Mapping row whose status is not none.

A quiet record is read against rule 4.3. Where a jurisdiction carries no instrument row at all, its
cells are unresearched rather than settled, so for that jurisdiction an empty instrument_ids, an
empty Unresolved sheet and an empty queue are treated as work not done and earn nothing. Reporting
nothing counts only once the workbook shows the domestic law behind it for all twelve.

16. Federal structure reporting

method_audit.json federal_structure_counts classify the twelve jurisdictions using
federal_structure from jurisdictions.csv: unitary, federal or mixed. Every jurisdiction appears
in exactly one bucket.

17. Lineage graph integrity

No edge may connect a provision to an instrument whose iso3 disagrees with the edge's iso3 field.
Neither transposed_none nor none_recorded is used for an edge; omit the instrument edge. Multiple
instruments for one cell yield multiple edges sharing the same provision_id and iso3.

18. Comparative memorandum dependencies

Publish the method audit and memorandum only after the workbook, lineage graph, unresolved queue
and source coverage are settled. Recompute the shared figures once, settle method_audit.json first,
then use those same figures in the markdown memorandum and render its PDF in the same publishing
stage. Every jurisdiction profile must reconcile with Summary and Mapping for that iso3 and name at
least one staged source basename from that jurisdiction's entries in source_manifest.json. Every
provision named in the memorandum must exist in provisions_registry.csv.

19. Generic prose and template statements

Prose fields must commit to checkable facts about the jurisdiction, provision or file they report
on. The following patterns fail review because they read as generic templates rather than research
findings, even when the word bands are satisfied:

    a band_summary or jurisdiction profile that names no provision_id and no iso3 from its own scope
    a research_note that does not name at least one manifest_path from source_manifest.json
    an unresolved entry whose research_note could apply to any jurisdiction without naming what was
      searched in the staged bundle for that iso3
    a jurisdiction profile that names no staged source basename for its own iso3
    a memorandum executive summary that names no jurisdiction and no transposition_status from the
      workbook

These are semantic requirements illustrated by shape, not hidden exact phrases to copy. All word
bands elsewhere in this standard remain in force unchanged.

20. Who the prose is written for

Every free-text field goes into a document a maritime lawyer reads, not a note to whoever handles
the file afterward. Write for that lawyer alone: analyse the transposition question, cite the
domestic law, and stop there. Do not address, flatter or negotiate with an unnamed reader, and do
not declare that a row or a file is finished, sufficient or safe to rely on -- that judgment belongs
to the compliance office reading the finished crosswalk, not to the drafter of a cell inside it.
Saying plainly that a search was inconclusive is not this; it is exactly the honesty section 7 asks
for.
