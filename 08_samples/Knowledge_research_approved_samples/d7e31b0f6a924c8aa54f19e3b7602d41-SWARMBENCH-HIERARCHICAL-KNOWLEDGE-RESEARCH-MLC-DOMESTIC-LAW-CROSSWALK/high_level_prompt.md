Build an offline transposition crosswalk mapping all 42 MLC 2006 provisions against all 12
flag-state jurisdictions (Australia, Bahamas, Canada, India, Kenya, Liberia, Malta, Marshall
Islands, Philippines, Singapore, South Africa, United Kingdom) as of the stated cutoff. Use only
the material staged under /input_artifacts, whose crosswalk standard governs classification,
citation and deliverable shape. No network access.

Deliver, all under /logs/agent:

- mlc_transposition_workbook.xlsx with six sheets: Mapping, Evidence, Instruments, Amendments,
  Unresolved, Summary
- article_lineage_graph.json linking each MLC provision to the domestic instruments that transpose
  it
- unresolved_research_queue.csv for provision/jurisdiction cells the staged corpus cannot settle
- source_coverage.csv accounting for every file listed in source_manifest.json
- method_audit.json documenting how the crosswalk was built and what it does not claim
- comparative_legal_memorandum.md and comparative_legal_memorandum.pdf, comparing transposition
  patterns across jurisdictions rather than restating workbook totals
- 24 shard files under /logs/agent/shards/, one per provision band

Every one of the 504 provision/jurisdiction cells needs a transposition status from the standard's
closed set. Every cell but none must name a domestic instrument and cite evidence unless an
unresolved record carries it; none and unclear cells owe an honest account of what was searched and
what was missing. All 42 provisions and 12 jurisdictions are required — no partial coverage, no
plausible-sounding status without a citation behind it. The lineage graph, Summary sheet and method
audit must each reconcile exactly with the Mapping sheet's own rows rather than report a second,
independent count. Domestic law that only takes effect after the cutoff does not belong in the
crosswalk.
