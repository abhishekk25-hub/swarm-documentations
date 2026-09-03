I am Priya Kessler, a research lead at an independent safety-engineering institute that advises
regulators and insurers on systemic accident risk. Our founding premise is that catastrophic
failures are not random: the same handful of underlying causal patterns keep recurring across
completely unrelated industries, and organizations that treat each disaster as a one-off never
see it. I am building the institute's first cross-industry causal-pattern atlas, covering 138 real,
well-documented disasters spanning six different industries, and nobody has read all 138 case
histories and cross-referenced them against each other yet. That is the job.

Your working directory is /workspace. The real source material for all 138 disasters has been
staged on this machine. Read these inputs before you start:

- /input_artifacts/disaster_index.csv - the 138 disasters, with columns disaster_name,
  industry_domain, slug, source_file, real_date. There are exactly 23 disasters in each of six
  industry domains: mining, maritime, aviation, structural, chemical, rail.
- /input_artifacts/causal_pattern_taxonomy.md - the fixed set of eight causal-pattern categories
  you must classify every finding into, with a real definition and worked examples for each, plus
  the exact contract for every deliverable below.
- /input_artifacts/corpus/<slug>.md - one real source dossier per disaster (named by the slug
  column), each built from that disaster's actual English Wikipedia article. Some dossiers include
  a real Wikidata QID and description where the article is linked to a matching Wikidata item;
  where present, it identifies the disaster's own entity, not a candidate to disambiguate.

Read every disaster's own source dossier in full before writing anything about it. These are real
historical events; every fact you record about a specific disaster must come from that disaster's
own dossier, not from general knowledge of the event, not from another disaster's dossier, and not
invented to fill a gap the source doesn't cover.

Your job has four parts.

**Part 1 - Per-disaster causal-chain dossiers.** For each of the 138 disasters, write one file at
/logs/agent/records/<slug>.md (the slug from disaster_index.csv) with these sections, in order:

1. A level-1 heading: `# <disaster_name>`.
2. `## Identity` - the real date, real location, industry_domain, and (if the source dossier
   states one) the real death/injury toll and the real Wikidata QID.
3. `## Causal chain` - the actual sequence the source documents, as five labeled parts: Root
   cause (the deepest systemic condition that made the failure possible), Contributing factors
   (specific circumstances, decisions, or omissions that compounded the root cause), Failure
   point (the specific event or moment where the failure became physically unstoppable),
   Consequence (what actually happened - the real outcome, not a generic "people died"), and
   Reform triggered (a real regulation, design standard, procedural change, or institutional
   change that followed, if the source documents one; state plainly if the source documents none).
   Every part must be specific to this disaster and grounded in what its own dossier actually
   says - do not write a generic causal chain that would describe half the disasters in the
   corpus equally well.
4. `## Causal pattern classification` - which of the eight causal patterns in
   causal_pattern_taxonomy.md genuinely apply to this disaster (most disasters have two or three,
   not one and not all eight), each with one real supporting sentence or quote from this
   disaster's own dossier. Do not assign a pattern just because the disaster is severe or
   well-known; assign it because the source's own account of what happened actually shows that
   pattern.

**Part 2 - Causal pattern register.** Assemble /logs/agent/causal_pattern_register.csv, one row
per disaster-pattern pairing from every dossier's Part 1 classification (a disaster with three
patterns contributes three rows). Use exactly these column headers: entry_id, disaster_slug,
disaster_name, industry_domain, real_date, causal_pattern, key_finding, supporting_quote,
cross_industry_link. entry_id is a sequential identifier you assign. causal_pattern is exactly
one of the eight category names from causal_pattern_taxonomy.md. key_finding is one plain
sentence stating what in this disaster's real history shows this pattern. supporting_quote is
copied EXACTLY, word-for-word, from that disaster's own source dossier - not paraphrased, not
reconstructed from memory, and substantive (a bare label or a one-word fragment is not an
acceptable quote).

cross_industry_link is the part of this task that cannot be done by reading any single disaster's
dossier alone. If - and only if - this row's disaster and pattern combination is genuinely the
same underlying causal mechanism as some OTHER row you have already logged for a disaster in a
DIFFERENT industry_domain, cross_industry_link holds that other row's own entry_id. Two disasters
merely sharing a causal_pattern label is not enough on its own to link them - the link is only
real when the actual mechanism (not just the category name) is comparable: a regulator that
knew about a hazard and declined to act is the same underlying mechanism whether it happened at a
mine or a chemical plant, but "operator error" caused by fatigue is not the same underlying
mechanism as "operator error" caused by an untrained temporary worker, even though both would be
tagged with the same pattern name. Otherwise cross_industry_link is exactly NONE. Do not link two
rows in the SAME industry_domain to each other - that is not a cross-industry finding. Do not
force links to inflate the count, and do not skip real ones because they take more work to find.

**Part 3 - Cross-industry synthesis.** Write /logs/agent/cross_industry_synthesis.md, at least
900 words, organized around the eight causal patterns, not around the six industries. For each
pattern that genuinely recurs across at least two different industries in your register, name the
specific disasters (with entry_ids), what actually happened in each, and why the underlying
mechanism - not just the category label - is genuinely the same. Where a pattern looks like it
recurs but the underlying mechanism is actually different in each case (a false cognate), say so
explicitly rather than forcing a connection. Point to specific entry_ids and direct quotes from
your own register to back every claim; a pattern you assert but cannot tie back to real rows in
the register is not usable. A synthesis that just walks through the six industries one at a time,
or restates each disaster's own causal chain without ever connecting it to another industry's
disaster, is not what is being asked for here.

**Part 4 - Pattern taxonomy file.** Write /logs/agent/pattern_taxonomy.json: a JSON object with
one top-level key per causal pattern (all eight, even if one has few or no genuine entries), each
holding an array of the entry_ids from your register that carry that pattern. Every entry_id
appearing anywhere in this file must be a real row in causal_pattern_register.csv, and every
disaster-pattern pairing in your register must appear under its own pattern's array here - the
two files must agree with each other.

Getting the file structure and section headings right is necessary but nowhere near sufficient.
The value of this atlas is in correctly and specifically capturing what actually happened in each
disaster and finding the cross-industry mechanisms that are genuinely real, not superficial. Do
not write a causal chain or pattern classification generic enough to apply to any disaster in the
corpus; do not state a fact the source dossier does not support; do not invent a cross-industry
link between two rows that only share a category label rather than a real mechanism. All 138
records are required and a missing record receives no credit for that disaster, but a complete,
well-formed record that is shallow, generic, or not genuinely grounded in that disaster's own
source dossier also receives no content credit merely because the file and headings exist. Read
the actual source of every disaster you write about; do not write from the disaster's name and
what you already know about it.
