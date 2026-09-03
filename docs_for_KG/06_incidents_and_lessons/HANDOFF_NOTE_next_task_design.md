# HANDOFF NOTE — everything learned from seven dead designs, for the next task build

Written 2026-07-29 at the close of the corpus-selection rounds. **Read this end to end before designing
anything.** It is the consolidated record of what was tried, what killed each attempt, what the exact
kill numbers were, and the one mechanism in this workspace that demonstrably produced a large gap.

Nothing here is a guess. Every number below came from a script in this workspace, and every claim points
at the artefact that produced it. Where a previous conclusion was later found wrong, the correction is
kept visible rather than edited out, because the pattern of *how* I was wrong is more useful than the
conclusions.

---

## 1. Scoreboard — what died and exactly why

| # | Design | Killed by | Number |
|---|---|---|---|
| 1–3 | Interdependence / contention / dependency-carrying-levels variants | Score was a **function of coverage**; sharding buys coverage | fan-out won 9/14 deterministic checks, lost 0 |
| 4 | Release-cycle triage at 700 items | Single agent **built its own swarm** with the injected key | 700/700 coverage, zero tail degradation, 18 fan-out call sites |
| 5 | **C2** — NTSB recommendation interdiction | Corpus **prints a field that decides the answer** (operating rule Part 121/135/91) | 57.0% macro vs 35.0% kill bar |
| 6 | **C3** — registry↔publication reconciliation | **The published rubric was itself the decision procedure** | 57.2% macro (43.0% excluding thin class) vs 35.0% bar |
| 7 | **D1** — drug-shortage mitigation | Claimed cascade was a **parallel join**; no quantity field exists to create contention | 0.0% conflict rate across 5 stricter variants |

Two of these had *pre-registered predictions that were wrong in opposite directions* (C2 was predicted
to pass and failed; C3 was predicted to fail a cheap string attack and survived it). That is the single
strongest argument in this note: **do not reason about whether a task is scriptable — measure it.**

---

## 2. The five hard constraints, in priority order

These are decision rules, not aspirations. Each one is derived from a specific death above.

**C1. If the score is essentially a function of coverage, the design is already dead.**
Ask before designing: *would a submission with 100% coverage and 25% per-item error score well?* If yes,
stop. A single agent with the injected inference key always wins a coverage race, because sharding buys
coverage. "Interdependence", "contention" and "dependency-carrying levels" all failed for this one
reason.

**C2. Anything shaped "generate candidates cheaply, then judge each candidate independently" is
fan-out-able, at any size.** Volume, cross-referencing and clustering are all this shape. This was tested
on real data, not assumed: genuine cross-area issue groups existed, but plain TF-IDF surfaced them at
rank ~10 within a pool of only ~3,000 candidates, and 3,000 independent pair judgements is *less* work
than the 700 deep assessments the agent had already completed.

**C3. Distinguish a parallel join from a cascade before writing anything.** This is the newest and most
reusable rule. Take one graded decision and ask whether computing it needs another decision's **output**,
or merely another record's **content**.
- *Content* → it is a JOIN. A sharded agent reads all the facts in parallel and merges. Worth **zero**
  for fan-out resistance, no matter how large or how many hops the graph has.
- *Output* → it is a cascade, and it requires **contention**: a shared resource whose commitment to B
  denies it to A.

**C4. Contention needs a numeric quantity field. Locate it before designing.** D1 died here. The
substitution story looked like a textbook cascade, but openFDA has no volume or capacity field anywhere;
the only proxy, `availability`, was absent for every presentation of 171/277 substances and
*self-contradictory across presentations* for another 54, leaving ~52 usable. Inventing the missing
numbers would be fabrication — an integrity violation, not a shortcut. Check field **coverage and
internal consistency**, never presence in one sample record.

**C5. Do not publish a decision procedure and then grade whether it was executed.** C3's four-class
precedence rule ("check absence, else measure identity, else timepoint identity, else consistent") is an
algorithm. Because it is part of the task statement, any attacker may implement it, leaving only fuzzy
string matching — which deterministic code does adequately. **The rubric, not the corpus, was the leak.**
Corollary: a closed answer set of N classes hands the attacker a 1/N floor for free.

---

## 3. The one thing that actually worked — and its honest caveat

Recorded in the lessons log as a durable win. At **1,050 real interlinked issues (~408k tokens)**:

- single agent: ran out of step/context budget mid-write, produced **zero deliverables** — reward
  **0.0167**, clean `step_finish`, a valid empty run and not an infra failure
- multi agent (Model B topology): decomposed the corpus and **completed** — reward **0.5276**,
  `degraded=false`, coverage/schema/audit all 1.00
- **gap 0.5109**, from a real capability difference with no cap or scoring trick

The mechanism was **pure scale plus required output volume**, not cascade structure and not fan-out
resistance. Two specifics worth copying: the binding constraint was **generation across ≥6 separate
responses with file state carried between them** (~165k output tokens, 127k of it one JSON array) — a
different failure mode from context overflow — and the deterministic **depth-of-coverage band** graded on
the full output is the most reliable natural gap lever measured here (an approved task hit SA 0.633 / MA
0.933 / gap 0.30 on it).

**The caveat, stated plainly because it decides how much to trust this.** This is the *same task family*
where the fan-out exploit was observed at 700-item scale. At 1,050 the single agent failed outright, but
nothing prevents a future single-agent run from choosing to fan out instead. So the win is real and
reproducible-on-record, but it rests on scale exceeding the point where the agent's own budget breaks
rather than on any property that forbids fan-out. Treat it as the best available option, not a solved
problem.

**Also relevant to scale:** at 1,050 the multi-agent run takes ~2.5h, and flake exposure grows with
runtime — one Daytona 502 anywhere in 2.5h voids the run and still burns a daily slot. A 700-scale MA
completed and scored in far less time. Prefer the smallest scale that still breaks the single agent.

---

## 4. The pre-build gate battery — run these before investing in a build

Ordered cheapest-first. Each has a pre-registered kill threshold. **Write the pre-registration before
computing any metric**, and include your prediction so being wrong stays visible.

| Gate | Question | Kill threshold | Cost |
|---|---|---|---|
| **Cascade-depth** | Do decisions depend on derived outputs, or only on content? | conflict-free ≥90% under an independent per-unit greedy | ~1h |
| **Gate 0 compressibility** | Does the reasoning survive summarisation? | survival >50% @20x compression | ~1h |
| **Gate 1 scripted extraction** | Can a keyless deterministic script answer the graded items? | best unfitted attack > chance + 10pp | ~1 day (needs labels) |
| **Gate 2 retrieval** | Can lexical/embedding retrieval answer them? | same margin-over-chance rule | ~half day |
| **Gate 3 projected gap** | Do weak and strong fixtures separate? | weak ≥0.30 or strong ≤0.70 | ~half day |
| **Fan-out per-check delta** | Does any rubric check resist a stateless per-item fan-out? | fan-out wins the total | ~half day |

Rules that make the gates trustworthy:

- **Kill criteria must be margin-over-chance, never absolute accuracy.** "Stop if a script exceeds 30%"
  is meaningless on a 4-class problem where chance is 25%.
- **Freeze labels before writing any attack.** A rule hand-written after seeing items is contaminated
  and its result must be voided.
- **Print the per-class table, never just the macro number.** Macro-averaging over a thin class
  manufactures both passes and fails: in C3 a two-item class contributed 25 of 57.2 macro points, and the
  winning attack's *flat* accuracy (53.6%) was **worse** than always guessing the majority class (64.3%).
- **Stress-test a kill under stricter variants, and pre-commit that a survivor does not reverse it.**
  D1's M3 was re-run under five tightening definitions (+route, +dosage form, +exclude scarce, +exclude
  fragile suppliers): 0.0% every time, which turned "my rule happened to succeed" into a structural
  finding. Choosing the definition after seeing the result is the exact post-hoc fitting gates prevent.
- **Never rescue a candidate by narrowing the graded set.** "Grade only the 9 in-scope items" and "drop
  the class the heuristic wins" are how four earlier designs shipped a gap that evaporated.
- **Size the DECIDING SLICE, not the corpus.** A 2.9M-character corpus had only **14k characters** that
  actually decided the answers; the "merge that cannot fit in one context" fit ~73 times over. Extract
  only the fields that determine each graded answer and measure *those* in tokens.
- **A symmetric relation cannot express a chain, so graph depth will lie.** D1's depth metric returned 11
  and "survived", but the component was 11 keys collapsing to ~5 molecules at **71% edge density** — a
  near-clique walked in circles. Always print edge density and dedupe nodes to distinct real entities.
- **Measure the broken fraction of the FALLBACK pool.** D1's recursion never fired because only 8.5% of
  the substitutable universe was short. Below ~30%, "the fallback may also be broken" premises don't fire.

---

## 5. Two verified harness facts that constrain any design

**The single agent can build its own swarm.** The harness injects the model key under **two** independent
names: the run config passes `--ae FIREWORKS_API_KEY=...` and `single_opencode.py:259-262` aliases it to
`OPENAI_API_KEY` (`multi_opencode.py:307-310` does the same for the multi arm). The observed agent
authenticated with `$FIREWORKS_API_KEY` directly, so a mitigation touching only the `OPENAI_API_KEY`
alias changes nothing. Air-gapping does not help: `allow_internet=false` sets `network_mode:none`, which
also stops the agent reaching its own model and fail-closes every LLM judge, since the verifier shares
the container. This was escalated separately as a platform blocker; it was observed **once**, in one
single-agent execution log, so it is real but rare. Do not use it as an excuse — design around it.

**The MA runtime is OpenCode, not Kimi-CLI.** `kimi-k2p6` is the model, not the runtime.

---

## 6. Infrastructure gotchas that cost real time

- **Prefer the bulk export over any paginated API.** Per-substance openFDA lookups stalled at 50/276 with
  nothing competing. `api.fda.gov/download.json` lists dated bulk exports; the entire NDC directory is
  one 27 MB zip (137,468 rows). Offline rebuild took **7 seconds** and was strictly better — class
  membership became *exact*, where the API route capped each class at `limit=1000` and would have
  silently truncated the largest classes. Check for a bulk export before writing any per-item fetch loop.
- **Tier filters by cost or the build will not finish.** One HTTP round trip per candidate over 1,748
  candidates projected to ~7 hours; batching (150 ids/request for titles, 12 for full text, per-item only
  for survivors) finished 130 pairs in 14 minutes. 32% died on the title alone.
- **`| Out-String` buffers the whole stream and defeats `python -u`.** A progress-printing diagnostic
  showed zero output for 190s. Redirect to a file (`*> run.log`) and read the file.
- **Killing the `py` wrapper leaves the `python` child running**, and it keeps writing your cache. A
  stale builder silently overwrote a parser repair. Identify processes by `Get-CimInstance Win32_Process`
  **command line** — the IDE's own python extension processes look identical by name and must not be
  killed. Sweep background processes when concluding a candidate: two from an abandoned candidate were
  still alive 2.5 hours later, starving the next build.
- **Check XML tags for attributes before concluding a field is sparse.**
  `<outcomeMeasure>` vs `<outcomeMeasure id="...">` nearly killed a live candidate on a regex bug.
- **`\b` does not match before a plural `s`, and it does match before a hyphen** — two opposite regex
  failures, one root cause. The second shredded batched XML into 11-character fragments.
- **Registries can have two schemas and the structured one may be the minority.** 120 of 130 ISRCTN
  records stored outcomes as free-text prose; only 10 were structured. A parser reading only the
  structured form silently discarded 168 records.
- **"Pin the historical version" is an assumption, not a capability — probe it.** ISRCTN silently ignores
  `version=`, 404s on `api/trial/<id>`, 400s on `format/full`, and its public record is a 1,206-byte
  JavaScript shell.
- **Never retry into a 429, and never trust `DEMO_KEY` for bulk.** govinfo's died after ~8 requests;
  regulations.gov requires a real key (this parked candidate C1 entirely).
- **PowerShell does not chain with `&&`** — use `;`. Filenames with brackets or em-dashes need
  `-LiteralPath` or a wildcard.

---

## 7. Recommendation for the fresh chat

Start from the **validated scale mechanism** (§3), not from another search for cascade structure. Seven
designs have now died looking for a structural property that forbids fan-out; the one success never
relied on one. Concretely:

1. Pick a domain with a large, real, freely fetchable corpus and a genuine professional deliverable.
2. Design for **required output volume across multiple responses with carried file state**, since that
   was the actual binding constraint — not input size.
3. Scale to the **smallest** unit count that still breaks the single agent, to limit the ~2.5h MA runtime
   and its flake exposure.
4. Grade **correctness against a frozen reference**, with a deterministic depth-of-coverage band on the
   full output; add points, never multiply.
5. Before building, run the cheap gates: the coverage question (C1), the fan-out shape question (C2), and
   the deciding-slice measurement.

If instead you want to keep the cascade thesis alive, the only honest route is a corpus that **already
contains real quantities** — CMS Medicare/Medicaid utilisation volumes are public and would supply the
demand numbers openFDA lacks — and then re-run the cascade-depth gate against it. Do not proceed on a
cascade without first locating the numeric field that proves contention.

---

## 8. Where the artefacts live

- **Lessons log** (append one line per issue, always): `PlanningOperations_Phase2_TaskCreationPrompt.md`,
  section `LESSONS LOG (BUILD -> SHIP)`
- **C2 / C3 gate results**: `phase_2_tasks/phase_2_1_tasks/_corpus_selection_v2/GATE_RESULTS.md`, with
  `PRE_REGISTRATION_C3_ADDENDUM.md`, `c3_labels.json`, `gate1_c3_labelled.py`
- **D1 cascade gate**: `phase_2_tasks/phase_2_1_tasks/_corpus_selection_v3/` —
  `PRE_REGISTRATION_CASCADE_GATE.md`, `CASCADE_GATE_RESULTS.md`, `cascade_gate.py`,
  `cascade_robustness.py`, `diag_m1_depth.py`, `build_graph_offline.py`, plus `cache/` (shortage +
  NDC snapshots, both dated 2026-07-29)
- **Platform blocker escalation**:
  `ESCALATION - Single agent self-parallelisation via injected OPENAI_API_KEY.md`
- **Binding specs**: `[Harbor] Multi-Agent Swarm Benchmark — Trainer Guidelines.txt` (v1.0, 2026-06-26 —
  authoritative; the `-V3.txt` file is superseded Phase 1), `Quality_dimensions_phase_2.md` (QD-01..09),
  `rubric_scale_presentation.pdf` (read before writing any check)
- **Feedback streams to design around**: `Feedbacks.txt`, `LLM_Review_Issues.txt`,
  `MAS Client Feedback Document.txt`
