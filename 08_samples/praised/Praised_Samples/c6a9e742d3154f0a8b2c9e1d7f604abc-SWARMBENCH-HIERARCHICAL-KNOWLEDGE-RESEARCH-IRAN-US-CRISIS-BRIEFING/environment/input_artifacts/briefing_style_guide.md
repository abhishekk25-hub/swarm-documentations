# Crisis Briefing Style Guide

## Purpose

This task evaluates whether an analyst can transform a large, heterogeneous source set into a neutral crisis-intelligence package. The final outputs should help a policy, risk, humanitarian, market, or communications team understand what is known, what is disputed, and what should be monitored next.

## Citation Rules

- Use source IDs from `source_manifest.csv` and `source_audit.csv`, e.g. `S001`, `S042`.
- Use stable evidence, claim, event, and contradiction IDs where required: `EV001`, `CL001`, `EVT001`, `CON001`.
- Cite every major factual claim.
- Do not treat a source ID by itself as proof that a source was inspected. Substantive use should usually connect to quote-backed evidence in `source_evidence_ledger.csv`.
- High-confidence claims should normally have at least two source IDs unless the claim comes from a primary source about that actor's own statement.
- Do not use uncited phrases such as "many analysts say" or "reports indicate" for important claims.
- If a URL is paywalled or inaccessible, record that in `source_audit.csv` and avoid relying on it for substantive claims unless enough metadata or syndicated text is available from another usable source.
- Keep direct quotes short and auditable. A quote should be copied from the browsed source, not rewritten as a paraphrase.

## Confidence Labels

Use only these labels:

- `high`: Multiple credible sources agree, or a primary source establishes its own statement/action and no credible contradiction appears.
- `medium`: Evidence is credible but incomplete, source types are narrow, or details differ across accounts.
- `low`: Evidence is thin, indirect, contested, or based on early reporting.

Do not label damage assessments, casualty counts, missile counts, ceasefire timing, or uranium stockpile status as high confidence if the cited sources materially disagree.

## Neutrality Rules

- Use "the United States", "Iran", "Israel", "Qatar", "the IAEA", and similar actor names instead of loaded labels.
- Attribute legal claims to the actor or institution making them.
- Avoid endorsing any actor's characterization, including "obliterated", "aggression", "self-defense", "victory", or "devastating", unless quoted and attributed.
- Do not recommend military action, targeting, cyber operations, sanctions evasion, propaganda, or influence tactics.
- Monitoring recommendations must be public-source and non-operational.

## Required Cross-Artifact Consistency

- If `claim_matrix.csv` marks a claim as `disputed`, the final report must describe it as disputed or uncertain.
- If `claim_matrix.csv` marks a claim as `disputed`, link it to a relevant row in `contradiction_ledger.csv` when a specific conflict can be identified.
- If `uncertainty_register.csv` lists an open question, the executive briefing must not present that question as resolved.
- If `event_timeline.csv` gives a date or sequence for a major event, the full report and slides must use the same sequence.
- If `impact_register.csv` identifies a high-severity impact, the final report should explain why it matters and cite sources.
- `appendix_citation_index.csv` should make it possible to trace important report sections back to source IDs, evidence IDs, claim IDs, event IDs, and contradiction IDs.
- IDs should resolve across ledgers. Do not invent `EV###`, `CL###`, `EVT###`, or `CON###` references in narrative deliverables unless the corresponding CSV row exists.

## Deliverable Tone

Write as a professional analyst, not as a commentator. Prefer:

- "U.S. officials said..."
- "Iranian officials disputed..."
- "The IAEA stated..."
- "Reuters reported, citing..."
- "The available public evidence does not resolve..."

Avoid:

- Unattributed certainty
- Advocacy
- Mockery or inflammatory language
- Operational advice to any party
- Overconfident claims about classified assessments
