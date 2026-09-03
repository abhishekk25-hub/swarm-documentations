I run remedial project management for our state cleanup program and the next round of five year reviews opens in the autumn

Before the review team can support a protectiveness determination at any site it has to know what the operative remedy actually is today rather than what the original decision said when it was signed

At most of our sites the signed decision has been modified since by later explanations of significant differences and by decision amendments and nobody has ever reconciled the original against what came after it

Work in /workspace

The docket covers twenty sites under the identifiers SITE-01 through SITE-20 and /input_artifacts/docket_manifest.csv lists for each of them the site name the agency site identifier the region and every decision document attached to that site with its document identifier the category it was filed under its signature date and the path to its text under /input_artifacts/decision_documents

Two shared references sit alongside the docket and /input_artifacts/decision_document_guidance.txt is the agency guidance fixing what each kind of decision document is meant to contain while /input_artifacts/cited_standards_register.csv is a pinned snapshot giving the text of each standard as it stood on the as of date recorded there

Write /logs/agent/remedy_change_register.csv with one row for every combination of a decision document and a medium that the document affects so a document touching two media gets two rows

A document affects a medium only where it changes what is required for that medium so a medium the document merely mentions or carries forward untouched does not earn a row

For a document that does not alter any requirement established by an earlier decision at that site include one coverage row with affected_medium none. Use change_class restatement for an initial decision or a document that only carries forward the operative remedy and use administrative-correction for a clerical or presentation correction that does not change the operative remedy. In either case use superseded_requirement NONE.

If a document makes more than one kind of change to the same medium keep one row for that document-medium pair and use the change_class that best describes the change that most directly alters the operative remedy. Summarize any secondary refinements in stated_basis. Cleanup-level retirement or replacement still belongs in full in the cleanup level crosswalk.

Use these column names in this order site_id document_id signature_date affected_medium change_class superseded_requirement stated_basis evidence_anchor

Write signature_date as YYYY-MM-DD

The allowed values for affected_medium are groundwater soil sediment surface-water soil-vapor air and none

The allowed values for change_class are scope-narrowing deferral substitution level-revision restatement and administrative-correction

The category a document was filed under records how it entered the administrative record and not what it did to the remedy so decide change_class from what the document itself changes

Put in superseded_requirement whatever the earlier decision at that site required and this document no longer requires and write NONE where nothing was dropped

Keep stated_basis to the reason the document gives for the change in no more than forty words of your own wording

Put in evidence_anchor the section number or table label as printed in that document together with the page number as printed in that document

Write /logs/agent/cleanup_level_crosswalk.csv with one row for every numeric cleanup level that currently controls and one row for every numeric cleanup level that a later document retired

Only a level the decision adopts as a cleanup level belongs here so leave out detected concentrations screening values background figures cost figures and standards a document quotes without adopting

Use these column names in this order site_id medium contaminant value_as_written unit_as_written normalized_value normalized_unit controlling_document_id superseded_by basis_family basis_citation_as_written conflict_note evidence_anchor

Copy value_as_written and unit_as_written exactly as the source document prints them and use the same medium vocabulary as the register

Normalize into ug/L for groundwater and surface-water into mg/kg for soil and sediment and into ug/m3 for soil-vapor and air and round normalized_value to three significant figures

The controlling document for a level is the document that selected it so where a later document repeats a level without changing it the earlier document still controls and superseded_by stays NONE

Where a later document did replace a level put the identifier of the replacing document in superseded_by on the row carrying the retired level

Where the documents at one site state the same level differently in narrative and in a table record the level the decision actually selected and give the reason in conflict_note and write NONE in conflict_note everywhere else

Use basis_family to group the standards behind these levels into one vocabulary reading the same way at every site written as lowercase words joined by hyphens and put the citation exactly as that document writes it in basis_citation_as_written

Write NOT-STATED in any cell the docket does not settle rather than filling it with a value the documents do not support

Write /logs/agent/review_readiness_memo.md for the review team

Name the sites where a documented inconsistency between the current remedy and the standards cited for it has to be resolved before anyone can support a protectiveness determination and for each of those sites point to the register rows and the crosswalk rows the problem rests on

Include a section setting out where one basis_family is cited under different wording across the docket and what that does to any comparison between sites

Close with what the docket leaves unsettled

Every site identifier and every document listed in the manifest has to appear in the register and every site has to appear in the crosswalk

When this is finished the register the crosswalk and the memo should be in place at the three paths above
