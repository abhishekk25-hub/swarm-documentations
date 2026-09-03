You are the research-information lead for a doctoral programme in learning sciences. Faculty are preparing a seminar called **Evidence, Design, and Evaluation in AI-Supported Learning** and need an auditable account of Professor Bruce M. McLaren's research programme.

Work from `/workspace`. Write the complete deliverable package under `/logs/agent/output/`.

This is a research task, not a scraping task. Start with the official publications page in `/input_artifacts/source_registry.md`. It is a real, live corpus with more than 200 outputs across journals, conference proceedings, book chapters, workshops, and preprints. Browse the official page and the public sources it links to. Use paper-level material whenever you assert a study's design, population, intervention, finding, or limitation. Do not infer those facts from a title or a search-result snippet.

Write only the finished research artifacts under `/logs/agent/output/`. A program is not a requested deliverable. We need your scholarly judgment: reconcile genuine ambiguities, explain relationships across papers, distinguish findings from speculation, and make defensible curriculum choices.

**Corpus-control requirement.**

Map at least 240 distinct entries from the official publication page in `corpus_map.csv`. First capture the current ordered official list and divide it into 24 consecutive, non-overlapping shards as evenly as possible. Every mapped row must identify its `shard_id` (`SHARD-01` through `SHARD-24`). This is essential coverage control, not a substitute for reading sources.

Use these columns exactly:

```text
record_id,shard_id,official_list_position,title,year,work_type,authors,official_url,doi_or_stable_url,evidence_level,primary_theme,historical_phase,version_group,status,uncertainty_note
```

Use `paper_or_abstract_read`, `bibliography_only`, or `unresolved` for `evidence_level`. Use `canonical`, `duplicate_or_version`, `nonresearch`, or `unresolved` for `status`. A preprint and its published version must not inflate the corpus.

**Evidence cards.**

Create `/logs/agent/output/evidence_cards/` containing exactly 72 Markdown evidence cards. Every shard contributes exactly three cards, and all cards must concern distinct canonical works.

Every card must include a canonical citation and stable URL; research problem and educational setting; method/design and population or data where reported; source-supported finding or contribution; one concrete limitation/boundary/uncertainty; two short excerpts with exact URLs; and connections to at least two other card IDs.

A work without enough public paper-level evidence may be mapped but must not be an evidence card. “More research is needed” is not a specific limitation.

**Method comparison.**   

Only create an evidence card when publicly retrievable, readable paper-level text supports its excerpts and claims. Do not quote from a binary response, redirect page, search snippet, or source text you cannot read. Use one canonical card-ID system: every final card filename stem is its `card_id`, and that exact ID must be used in the matrix, all card links, theme synthesis, trajectory, seminar plan, claim audit, and index. Do not leave draft files, placeholder IDs, or alternative record-ID schemes in the final package. Before delivery, reconcile every cross-artifact card reference to the final 72-card directory and remove any unsupported statistic, quotation, or relationship.

Create `method_comparison_matrix.csv`, exactly one row per evidence card, with these columns:

```text
card_id,research_problem,intervention_or_system,learning_domain,learner_population,setting,study_design,comparison_condition,outcome_measure,reported_result,causal_claim_boundary,transferability_limit,source_url,evidence_excerpt
```

Use `not_reported` rather than guessing. The causal boundary must state what the source permits a faculty member to claim and what it does not.

**Synthesis and seminar design.**

Create `theme_synthesis.md` defining six evidence-grounded themes. Each theme needs at least ten cards from at least three historical phases. For every theme, define its boundary and overlap, compare at least three methods/populations/settings, identify a development or disagreement, and distinguish its justified conclusion from overreach.

Create `research_trajectory.md`, 3,500–4,500 words. Divide the work into at least four historical phases. Make at least 24 cross-paper claims about continuity, change, transfer, replication, design evolution, or unresolved tension. Every claim cites two or more cards; at least eight compare methods or evidence boundaries from the method matrix. Include at least 20 explicit pairwise comparisons and a “claims we should not make” section with at least eight plausible but unsupported generalizations.

Create `seminar_plan.md` for exactly 14 weeks. Every week has two evidence-card readings, a central question, an activity, a source-backed relationship between readings, and a methodological caveat. The 28 readings collectively cover all six themes and four phases, include at least 12 journal articles or full peer-reviewed papers, use at least eight corpus works, include a substantial primary-source reading from every historical phase, contain no duplicate/version pair, and contain no more than four works from one year, venue, or project cluster. Include eight reserves with a precise pedagogical reason for reserve status.

Create `claim_audit.csv` for every substantive claim in the three written artifacts, with:

```text
claim_id,artifact,claim_text,card_ids,source_urls,claim_type,support_status,qualification_or_caveat
```

`support_status` is `directly_supported`, `careful_synthesis`, `tentative`, or `not_supported`. Do not use a `not_supported` claim as an affirmative conclusion.

Finally create `index.html`, a lightweight local faculty-review page linking every artifact, all cards, a theme-by-phase matrix, and the weekly sequence. Every local link must resolve.

**Evidence discipline.**

- The official McLaren page establishes the candidate corpus. Preserve an official URL for every mapped record.
- The CV and CMU profile establish professional context only, not paper-level findings.
- Use a paper, official abstract, publisher/DOI record, proceedings, or repository for substantive claims.
- DBLP and OpenAlex are reconciliation sources, not automatic truth. Disclose meaningful year, title, DOI, type, or version conflicts.
- Do not use Wikipedia, ResearchGate, Google Scholar, snippets, or blogs as sole support for substantive claims.
- Do not invent access, participants, results, or causal effects when a source is unavailable.

The finished work should help faculty teach and critically evaluate a real research programme. A generic syllabus or a large title list will not meet that bar.
