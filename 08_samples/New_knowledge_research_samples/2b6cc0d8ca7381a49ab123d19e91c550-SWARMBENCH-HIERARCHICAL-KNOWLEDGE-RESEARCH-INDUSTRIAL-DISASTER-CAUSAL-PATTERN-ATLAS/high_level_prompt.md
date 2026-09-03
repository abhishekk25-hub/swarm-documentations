Build a cross-industry causal-pattern atlas covering 138 real industrial and infrastructure
disasters spanning six industries: mining, maritime, aviation, structural engineering, chemical
and industrial plants, and rail. The real source dossier for each disaster is staged at
/input_artifacts/corpus/<slug>.md, listed in /input_artifacts/disaster_index.csv, and every
disaster must be classified against the fixed eight-category causal-pattern taxonomy and record
schema defined in /input_artifacts/causal_pattern_taxonomy.md.

Deliverables, all under /logs/agent/:

1. One causal-chain record per disaster at /logs/agent/records/<slug>.md: a heading, an identity
   block, a five-part causal chain (root cause, contributing factors, failure point, consequence,
   reform triggered), and a causal-pattern classification citing a real supporting quote for each
   pattern that genuinely applies. All 138 records are required.

2. /logs/agent/causal_pattern_register.csv, one row per disaster-pattern pairing, with the exact
   nine columns: entry_id, disaster_slug, disaster_name, industry_domain, real_date,
   causal_pattern, key_finding, supporting_quote, cross_industry_link. supporting_quote must be
   copied verbatim from that disaster's own source dossier. cross_industry_link must identify,
   for pairs that genuinely share the same underlying mechanism across two DIFFERENT industries,
   the other row's entry_id; otherwise it is exactly NONE.

3. /logs/agent/cross_industry_synthesis.md, at least 900 words, organized by causal pattern
   rather than by industry, naming specific disasters and entry_ids and explaining which
   cross-industry mechanisms are genuinely shared versus superficially similar.

4. /logs/agent/pattern_taxonomy.json, a JSON object with the eight causal-pattern names as keys,
   each mapped to the array of entry_ids from the register that carry that pattern.

Every fact must come from that disaster's own real source dossier -- do not write from a
disaster's name and general knowledge of the event. A shallow, generic, or unsupported record
earns no content credit even if the file and headings exist.
