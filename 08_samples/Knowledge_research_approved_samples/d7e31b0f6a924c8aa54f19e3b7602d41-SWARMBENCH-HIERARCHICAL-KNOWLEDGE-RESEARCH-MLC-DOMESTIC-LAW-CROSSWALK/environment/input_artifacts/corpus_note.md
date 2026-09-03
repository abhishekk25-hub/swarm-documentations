Archivist's note on the corpus
Maritime Compliance Office, MLC 2006 domestic-law crosswalk programme

This note is what the records office knows about the condition of the staged material. Read it
before you start, because several of the things it describes look like faults in your work when
they are in fact properties of the evidence.

On the MLC text. /input_artifacts/mlc_2006_authoritative.txt is a consolidated extract of the
Maritime Labour Convention 2006 as referenced by provisions_registry.csv. It carries the
regulation and standard wording the registry points to. It is not a ratification instrument for any
flag state and attests nothing about domestic transposition by itself.

On the jurisdictions. The twelve bundles under /input_artifacts/domestic_sources/ were archived on
different dates between 2019 and 2026 and they are not uniform. Some jurisdictions stage primary
statute and subsidiary rules together; others stage only the maritime code and expect you to follow
cross-references named in source_manifest.json. Federal states may stage federal text without
provincial or state implementing rules, and the manifest says when that is so. None of the bundles
was edited after staging; a provision that appears repealed in the file is repealed for this
crosswalk if the repeal date in the file is on or before 2026-07-30.

On instrument types. Statutes, regulations, statutory instruments, department orders and maritime
authority circulars are staged in two formats, and source_manifest.json records which applies to
each file. Most arrive as plain text, and where the retrieval_note says the text was extracted from
a published PDF the extraction may have dropped table rulings and footnote markers, leaving columns
run together on one line. The rest arrive as HTML and may carry navigation chrome between sections
of the instrument. Quote what the file actually holds when you locate an evidence passage, and do
not treat either kind of format noise as absence of law.

On the manifest. /input_artifacts/source_manifest.json is the inventory of what was staged, not a
claim that every file is complete for every provision. Some jurisdictions have gaps the manifest
flags in retrieval_note. A gap in the manifest is a property of the corpus, not an invitation to
infer domestic law from the MLC text alone.

On partial and delegated transposition. Several jurisdictions implement MLC obligations through
empowering clauses that authorize subsidiary legislation rather than restating the obligation in
primary law. A cell that records delegated is not a failure of research when the staged statute
genuinely delegates; a cell that records full when only a delegation clause exists is a failure of
classification. Reserved matters appear in ratification documents for some flags; where the staged
material includes a reservation, the cell must say reserved and cite the reservation instrument.

On amendments. Amendment history in the staged files is not aligned across jurisdictions. Some
files carry a consolidated "as at" date in the header; others carry amending instrument lists at
the foot. The as-of cutoff is 2026-07-30 everywhere. An amending instrument dated after that cutoff
does not change the transposition status you report, even if you know it was enacted.

On repair. Do not edit anything under /input_artifacts. The MLC text and the domestic sources are
the evidence, and the audit trail we have to stand behind cites them as they are. Everything you
produce goes under /logs/agent.
