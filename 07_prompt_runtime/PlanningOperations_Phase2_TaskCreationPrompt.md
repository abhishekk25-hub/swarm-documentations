# Planning-Operations — SwarmBench Phase 2 Task Creation Prompt

> Autonomous, self-driving prompt for authoring SwarmBench **Phase 2**
> `planning-operations` tasks end-to-end. Successor to
> `PlanningOperations_TaskCreationPrompt.md` (the Phase 1 prompt).
>
> AUTHORITATIVE SPEC: this prompt is reconciled to three `00_authority/` docs:
> (1) **Trainer Guidelines v1.1** (`[Harbor] … Trainer Guidelines (2).txt`) —
> package/delivery contract;
> (2) **Verifier & Rubric Manifest Standards (Effective Immediately).txt** —
> `verifier_type` / manifest fidelity / hybrid grading;
> (3) **Production Rework Requirements.txt** — production rework wave
> (pause new authoring; `multi_noplan`; `high_level_prompt.md`;
> structural ≤40% / content ≥60%; three log packages; ≥20pp SA–multi gap).
> (4) **SwarmBench_Verifier_Template.zip** (2026-08-11 team template) —
> current reference plumbing for `tests/verify.py`, W&B judge calls,
> four-field numeric `reward.json`, `reward_debug.json`, and
> `judge_justification.txt`.
> Where this prompt disagrees with any of them, those authority docs WIN —
> fix this file (STANDING DUTY 0). Precedence on scoring share: Production
> Rework's **content ≥60% / structural ≤40%** SUPERSEDES the earlier
> Verifier Standards "content ≥40%" floor (stricter). If authority docs
> otherwise conflict, ESCALATE — do not silently pick.
>
> VERSION NOTE (do not get confused by the numbers): the LATEST, authoritative
> spec is the Phase 2 guidelines **v1.1 (2026-07-20)** — the "Phase 2.1"
> revision — carried in the `... Trainer Guidelines (2).txt` file. The
> earlier `... Trainer Guidelines.txt` is **v1.0 (2026-06-26)** and is
> SUPERSEDED by v1.1 (archived under workspace `_archive/duplicate_docs_root/`).
> The separate file `[Harbor] Multi-Agent Swarm Benchmark — Trainer Guidelines
> -V3.txt` (same archive) is the OLDER **Phase 1** guidelines (v3 of the
> Phase-1 line, oracle/golden-answer based).
> "V3" is a higher number but an EARLIER product line — it is SUPERSEDED for
> Phase 2 and is consulted ONLY for still-generic instruction.md /
> decomposition / time-management machinery, NEVER for scoring (its oracle
> model is forbidden now).
>
> PHASE 2.1 HEADLINE (v1.1, 2026-07-20 + Production Rework): the client
> accepted Phase 2's creativity and moved to a scaled PRODUCTION/EVAL batch,
> but rejected verifiers that graded SHAPE not SUBSTANCE. Every task now ships
> a `tests/rubric_manifest.json` mirrored 1:1 by `tests/verify.py` (static /
> reward-hacking / partial-oracle). Scoring follows P21-5 + Verifier Standards
> + **Production Rework**: content ≥ **60%** / structural ≤ **40%**; prefer
> category 1/2/3 (or an equivalent multiplicative content signal exposed in
> the manifest and debug files); honest manifest; `verifier_type = "hybrid"` when mixing
> deterministic + LLM. Also required for production rework: `high_level_prompt.md`,
> three log modes (`single` / `multi` / `multi_noplan`), ≥20pp SA–multi gap.
> Inputs under `environment/input_artifacts/`; exact `/logs/agent/...` paths.
> Sources RECENT / less-canonical. EVAL calibration: SA very low AND MA
> challenged. See PHASE 2.1 UPDATE, P21-12, and P21-13.
>
> It keeps
> the still-binding governance from Phase 1 (INTEGRITY MANDATE, SCORING
> INTEGRITY, AUTONOMY MODE, packaging discipline) and RE-SHAPES the task
> design to the Phase 2 requirements: the OpenCode harness, load-bearing
> browsing, HIERARCHICAL DAG with depth >= 2, 20-50+ sub-agents, diverse
> real artifacts, and a human-like `instruction.md`.
>
> CURRENT HEADLINE: Phase 2 tasks are realistic, long-horizon, multi-stage,
> externally-grounded workflows graded by a transparent rubric of static,
> reward-hacking, and partial-oracle checks. The verifier must use the
> 2026-08-11 template plumbing unless there is a task-specific reason not to:
> W&B judge via `WANDB_API_KEY`, robust JSON extraction, non-empty
> `judge_justification.txt`, diagnostic detail in `reward_debug.json`, and a
> four-field numeric `reward.json`. Any weights, multipliers, gates, or blended
> formulas must be explicitly mirrored in `rubric_manifest.json`; never hide
> them, and never use them to manufacture the single-vs-multi gap. The gap
> must arise naturally from genuine task difficulty (scale, breadth,
> coordination), never from a hidden restriction or engineered timeout.
>
> Copy the block below verbatim into a fresh agent chat to start a new
> Phase 2 planning-operations task.

---

```text
Create a new SwarmBench PHASE 2 planning-operations task end-to-end,
following the same gated discipline we used in Phase 1 but applying the
NEW Phase 2 client requirements. Do NOT compromise on any phase: idea
validation, scenario/class selection, source assembly, multi-stage
workflow design, rubric implementation, QD audit, similarity gate, or
zip packaging.

============================================================
ENTRY ROUTING -- DO THIS BEFORE READING OR RESEARCHING ANYTHING ELSE
============================================================
Spend only one short inspection pass on the conversation and supplied task
materials, then select exactly one route:
  A. CLAIMED route: use this only when a complete, accepted claim record is
     actually present. It must include `decision: accept` (or an unambiguous
     true/accepted equivalent), a scenario/query, sources or real entities,
     expected outputs, a coordination/hardness brief, and a verifier/test
     blueprint. Parse it as the locked brief under CS-1 through CS-4.
  B. SCRATCH route: use this when no usable claim/seed information was
     supplied. This is NOT a blocker and is NOT permission to invent a claim,
     similarity score, approval, source, entity, or execution result. Create
     an original, real-world design brief under CS-S, record
     `authoring_mode: scratch` and the absent-input reason in trainer-only
     HANDOFF.md and NOTES.md, then proceed through Gate 0's scratch procedure.
  C. PARTIAL route: use this only when a purported claim supplies some but not
     all of the required claim fields, or when its decision/status is unclear.
     Pause once with a concise list of the missing/contradictory fields; do
     not silently discard, repair, or fabricate a claimed record.

An identifier alone, an empty form, or a `decision` value without the design
brief is not a usable claim. It takes the SCRATCH route. Do not spend the
task's working budget reading the full workflow before making this routing
decision. A scratch task must still obtain any required labeling-tool UUID,
complete the normal similarity check, and meet every later source, integrity,
quality, execution, and packaging requirement before submission.

============================================================
THE TWO ACCEPTANCE CRITERIA (if both hold, the client won't reject)
============================================================
Everything in this prompt serves exactly two goals (2026-06-26 DM note --
"if it satisfies these two, we will never get issues from the client"):
  1. THE GAP IS REAL. The single-agent and multi-agent scores are
     genuine measurements of a true capability difference -- never
     manufactured by a scoring trick, a hidden restriction, an
     engineered timeout, or a hallucinating judge. You can name in
     writing WHY the single agent naturally fails, and you have manually
     verified both runs' real outputs.
  2. THE TASK IS CREATIVE + REAL-WORLD. It is an original, realistic work
     scenario a real operator would actually face -- not a Phase-1
     reskin, not a template variation, not a synthetic exercise, and not
     yet-another spreadsheet. Diverse, real deliverable formats.
If a design choice does not advance one of these two, reconsider it.

============================================================
PRODUCTION REWORK WAVE (effective now — READ BEFORE ANYTHING ELSE)
============================================================
Authority: `00_authority/Production Rework Requirements.txt`.

IMMEDIATE ACTION:
  - Every task currently in Completed moves back to Rework.
  - PAUSE new task authoring. Prioritise bringing EXISTING tasks into line
    with the requirements below (and P21-13) before submitting again.

P-RW summary (full detail in P21-13 + the authority file):
  1. Force-reinstall `mascloud` so `multi_noplan` AND `verify-only` exist
     (pipx `--force` / pip `--force-reinstall`; `mascloud --help` must list
     both; run modes single / multi / multi_noplan).
  2. Capture THREE fresh execution-log packages on the SAME final package:
     `single`, `multi`, and `multi_noplan`. Keep all three ZIPs. multi_noplan
     has no gap/reward target but must finish with usable logs (crash /
     unrecovered rate-limit is not evidence). Keep instruction / verifier /
     logs aligned — stale logs after brief changes are not ship evidence.
  2b. `verify-only` ONLY for reward-reporting refreshes (static /
      partial-oracle / reward-hacking fields in reward.json) against VALID
      existing logs. NEVER for instruction / HLP / decomposition / inputs /
      requirements / agent-behavior changes — those need a full mode re-run.
  3. Add `high_level_prompt.md` (~250 words; band ~100–450; record word
     count) — terse requester voice; deliverables only; no persona/method/
     tools/decomposition/verifier. Independent restatement of instruction.md
     (keep instruction.md; do not delete it). Deliverables must match.
  4. Verifier: expose static / partial_oracle / reward_hacking components in
     reward.json; structural ≤ 40%; content ≥ 60%; ≥3–5 content rubrics;
     multiplicative content-quality signal so formatting cannot wash out
     failed grounding/anti-gaming.
  5. SA vs planned-multi gap ≥ 20 percentage points under identical package /
     env / verifier / budget — improve the TASK, never tune the verifier to
     invent the gap.
  6. Final static checker + LLM Quality Gate review report required with
     resubmission; address every valid finding.

============================================================
LATEST CLIENT + TEAM FEEDBACK (2026-07-17) -- MANDATORY, REJECTION CRITERIA
============================================================
Distilled from the Batch-16 client review (FAIR SAGE - V2 Turing Batch-16
Data) and the team directive that followed. QA leads treat every item below as
a REJECTION criterion for future deliveries. Design around ALL of them up front.

  A. STRUCTURAL CHECKS ALONE ARE NOT ENOUGH -> AUTO-REJECT. A verifier that
     grades only shape (row/column counts, header presence, JSON keys, chart
     PNG exists, string length, keyword-prefix, format regex) lets a single
     agent type ANYTHING in the right structure and bank reward ~1.0 -- a
     poisonous training signal ("produce well-shaped output", not "do the
     task"). Every deliverable and every claim asked for in instruction.md
     MUST have a SUBSTANCE check (correct VALUES vs a real reference, resolved
     citation URLs, IDs validated against a frozen snapshot, verbatim-quote
     round-trip, coverage vs ground truth), PLUS LLM-judge checks where quality
     needs reading. The test suite must COVER EVERYTHING the instruction asks
     for -- not a structural subset.

  B. CONTENT SHARE + HONEST MANIFEST (Production Rework + Verifier Standards).
     Binding: `00_authority/Production Rework Requirements.txt` (stricter
     share) and `00_authority/Verifier & Rubric Manifest Standards
     (Effective Immediately).txt`. AUTO-REJECT if:
       (1) content share (reward_hacking + partial_oracle / content rubrics)
           is < **60%** of total score, OR structural checks exceed **40%**
           (Production Rework SUPERSEDES the earlier ≥40% content floor);
       (2) fewer than 3–5 real content-based rubrics;
       (3) `rubric_manifest.json` misrepresents verify.py (fake equal weights
           when weighted/multiplicative; duplicate `check_function`; omitted
           gates / multipliers / alternate paths).
     Prefer category weights 1/2/3 and/or a multiplicative content-quality
     signal so easy formatting cannot wash out failed grounding/anti-gaming
     (reward.json must expose component scores + final score). ALWAYS
     FORBIDDEN: per-check tuning, anything > 3 as a category weight, tiers,
     score caps/floors that invent the SA/MA gap, step-bands. Composition
     still matters: cut presence checks; add held-out RH/PO substance.

  C. NO SINGLE-CALL LLM JUDGING ON A RUBRIC DUMP -> AUTO-REJECT. One giant LLM
     call grading a huge list of rubric items in one shot is a major
     reward-hacking risk and is unjustifiable as stable/reliable. The accepted
     standard is a WELL-DECOMPOSED rubric graded with MULTIPLE independent LLM
     judge calls (>=3 groups, e.g. one per deliverable/theme; no single call >
     60% of reward). See QD-03.3 / ledger L1.

  D. LLM-CALL FAILURES SCORE 0.0 FOR THAT CHECK AND MUST BE LOUD
     (2026-08-11 verifier template update). An API / network / missing-key /
     parse failure is an INFRA fault, NOT a content judgement, but the failed
     judge check remains in the bucket denominator and contributes 0.0. Never
     exclude failed judge calls from the average. Required handling: (1) retry
     transient failures; (2) score the affected check 0.0 after retries; (3)
     print a WARNING to stdout; (4) write an `INFRASTRUCTURE FAILURE` entry in
     `/logs/verifier/judge_justification.txt`; (5) record the failed check and
     errors in `/logs/verifier/reward_debug.json`; (6) investigate / verify-only
     only when the package itself did not change. This supersedes the older
     Batch-16 "never score 0.0 on infra" wording for individual LLM checks.

  E. FINISH METADATA AFTER THE RUNS, FROM THE REAL TRAJECTORIES. Once
     execution_logs exist, REWRITE the metadata to match what actually
     happened: `why_multi_agent` must explain HOW THE SINGLE AGENT ACTUALLY
     FAILED (read the SA trajectory -- timeout, premature self-completion,
     attention degradation, fabrication -- not the pre-run hypothesis); and
     `dag_depth` / `dag_width` must reflect the MA's ACTUAL SPAWNED tree
     (count observed spawn levels + widest level), NOT the pre-execution
     estimate. Prefer managerial / observed spawn depth over longest
     `depends_on` path node-count when they disagree (official QG needs
     ≥2 and a non-flat star; path-length equality is not required). A
     declared-vs-realized mismatch that invents depth is a reject (ledger L5).

  F. A REAL BUT NARROW GAP NEEDS MORE COMPLEXITY. Every Batch-16 borderline was
     a genuine, substance-verified gap that landed at 23-28 pp only because the
     SA baseline was high (60-75%) -- SA banks a partial-credit floor on the
     scriptable/mechanical backbone while collapsing on the hard reading core.
     The fix is to RAISE DIFFICULTY (more sources under a tighter budget, harder
     non-scriptable core, more hard checks by count) so SA's floor drops -- not
     to discard the task and not to reweight (item B).

============================================================
PHASE 2.1 UPDATE (GUIDELINES v1.1, 2026-07-20) -- SUPERSEDES CONFLICTING TEXT BELOW
============================================================
This block folds in the Phase 2.1 client requirements from the updated
Trainer Guidelines v1.1 (2026-07-20), the 2026-07-20 Onboarding call, the
MAS 2.0 onboarding notes, the Kimi-CLI limitation analysis, and the latest
client feedback batch. It is AUTHORITATIVE: wherever any older text further
down this file conflicts with an item here, THIS BLOCK (and the official
v1.1 guidelines) WIN. The through-line: the reward must MEASURE THE ACTUAL
WORK. A well-shaped file is worth nothing unless its VALUES, EVIDENCE,
COVERAGE, and CONCLUSIONS are checked too.

P21-1. ONE STANDARD PACKAGE CONTRACT (paths are now fixed and enforced).
  - INPUTS: every packaged file the agent must read lives under
    `environment/input_artifacts/` and is referenced in instruction.md by
    its agent-visible `/input_artifacts/...` path. No orphaned inputs; every
    referenced input must exist; every shipped input must be referenced.
  - OUTPUTS: every deliverable is written to an EXACT `/logs/agent/...` path
    that is stated in instruction.md, declared in the manifest, and opened
    directly by verify.py. The three must be byte-identical strings. The
    verifier NEVER searches arbitrary folders for an output. (This is the
    fix for Phase-1/2 "false failures" where the agent wrote a correct file
    to the wrong place and lost all reward.)

P21-2. ONE STANDARD GRADER: `tests/verify.py` (judge.py is retired).
  - `tests/test.sh` invokes `/tests/verify.py`, and verify.py writes
    `/logs/verifier/reward.json` (required) and may also write
    `/logs/verifier/reward.txt` (legacy harness). If BOTH exist, the
    numeric `reward` MUST be identical in the two files.
  - If verify.py uses any LLM judge, it MUST write the complete
    human-readable judge reasoning to `/logs/verifier/judge_justification.txt`
    (singular `.txt`). Never write `judge_justification.txt` under
    `/logs/agent/`; `/logs/agent/` is only for agent-created deliverables.
    The current template's canonical diagnostic sidecar is
    `/logs/verifier/reward_debug.json`; older `reward_details.json` /
    `judge_justifications.json/jsonl` names are legacy debugging aids only.
  - Required `reward.json` fields (platform schema, 2026-08 team update;
    2026-08-11 verifier template):
        reward                              (the OVERALL run score — same
                                            number as reward.txt)
        total_static_check_score            (structural / static bucket;
                                            announcement alias: structural_check_score)
        total_reward_hacking_check_score    (announcement: reward_hacking_check_score)
        total_partial_oracle_check_score    (announcement: partial_oracle_check_score)
    HARD HARBOR TYPE RULE (measured 2026-08-06, Outcome-Drift SA): Harbor's
    `VerifierResult.rewards` is `dict[str, float | int]` ONLY. Every value in
    `reward.json` MUST be a number. Current team template standard: write
    EXACTLY the four fields above and nothing else. Nested lists/dicts
    (`excluded_checks`, `grader_errors`, `per_check`, `checks`), path strings
    (`llm_item_justifications_file`), or nulls cause pydantic ValidationError
    and the platform UI / `mascloud runs` falls back to reward **0.0** even
    when the verifier's true score is non-zero. Put per-check breakdowns,
    LLM justifications, and other diagnostics in a SIBLING file (e.g.
    `reward_debug.json`, `llm_item_justifications.jsonl`, stdout) — not
    inside `reward.json`. Also write `reward.txt` with the same overall
    number. The three bucket fields are the reported bucket scores used by
    the verifier formula; if the formula is weighted or multiplicative, that
    exact formula must be mirrored in `rubric_manifest.json` and the debug
    file. Do not hand-patch a completed arm into a different formula.
  - Use the 2026-08-11 `SwarmBench_Verifier_Template.zip` judge plumbing for
    all new submissions unless you have a documented task-specific reason not
    to. Keep `call_judge()`, robust backward JSON extraction (`_last_json_object`
    style), `write_reward()`, `write_justification()`, stdout logging, and
    `reward_debug.json`; replace only the example task checks. The only runtime
    secret/config a normal task should require is `WANDB_API_KEY`. Hardcode the
    intended W&B judge model in `verify.py`, defaulting to
    `Qwen/Qwen3.6-35B-A3B` when appropriate.
  - Judge-call failures after retries score `0.0` for that specific check and
    remain in that bucket's denominator. They are not excluded. The
    infrastructure problem must still be loud: print a warning to stdout, write
    an `INFRASTRUCTURE FAILURE` entry in `judge_justification.txt`, and record
    the failed check(s) in `reward_debug.json`.
  - Judge JSON parsing must not assume the provider returns pristine JSON.
    First try `json.loads`; if that fails, scan backward for the last balanced
    parseable `{...}` so markdown fences, `<think>` blocks, or unexpected
    reasoning text do not make an otherwise valid verdict disappear.
  - On verify.py crash, `test.sh` must still write a four-field all-zero
    `reward.json` (and matching reward.txt if you keep that file).
  - Do NOT ship `judge.py`, `verifier.py`, or any other verifier-named
    script at the root of `tests/`. The SOLE verifier-named script at
    `tests/` root is `verify.py`. Combine deterministic checks AND any
    LLM-as-judge calls INSIDE `verify.py` (an independent LLM is called
    inline for genuinely qualitative checks). Optional helper modules live
    under `tests/test_logic/`. This REPLACES the old "executable ->
    verify.py / llm-judge -> judge.py" split for *file layout*: there is
    still ONE file, verify.py. Manifest `verifier_type` (Verifier Standards,
    effective immediately):
      * `"hybrid"`     — REQUIRED when the task mixes deterministic/
        structural checks WITH LLM-judge RH or partial-oracle checks
        (the normal Phase 2.1 case).
      * `"executable"` — ONLY when every check is purely deterministic.
      * `"llm-judge"`  — ONLY when every check is performed by the judge.
    Do NOT leave a hybrid grader labelled `"executable"`.

P21-3. `tests/rubric_manifest.json` IS NOW MANDATORY (client-readable rubric).
  It is a complete, natural-language MIRROR of verify.py. QG rejects a task
  without it. Exact shape:
    - top-level: `task_id`, `verifier_type`, `total_checks`, `checks`.
    - `checks` is keyed by entries in THREE required categories, numbered
      sequentially from 1 with NO gaps:
        static_checks_<n>, reward_hacking_checks_<n>, partial_oracle_checks_<n>
      At least ONE entry in EACH category is required.
    - EACH entry has EXACTLY these FIVE fields (no more, no fewer):
        detailed_explanation_of_checks   (a real explanatory sentence or two,
                                          not a checkbox -- describe WHAT is
                                          counted/compared and HOW)
        weight                            (must exactly match `CHECK_WEIGHTS`
                                          or the equivalent scoring table in
                                          verify.py. Flat `1` is allowed when
                                          composition alone hits content ≥60%;
                                          category weights 1/2/3 are allowed
                                          when declared honestly. Never
                                          per-check tune and never exceed 3.)
        agent_output_path                 (one `/logs/agent/...` path OR a list
                                          of them; every path starts /logs/agent/)
        check_function                    (the EXACT function name in verify.py /
                                          tests/test_logic/ that implements it;
                                          each check_function appears ONCE —
                                          duplicates auto-reject under S-08)
        how_it_prevents_task_authenticity_violation
                                          (how this check stops a fabricated /
                                          plausible-but-wrong output from
                                          scoring)
    - `total_checks` MUST equal both the number of manifest entries AND the
      number of checks registered by verify.py. Every check_function must
      resolve to real code. Manifest <-> verify.py is a strict 1:1 mirror.
      If scoring uses non-uniform weights, multipliers, gates, caps, or blended
      paths, the manifest MUST explicitly represent that behavior — never
      imply an equal-weight average when one does not exist (Verifier Standards
      §5). If the template `CHECK_WEIGHTS` dict changes, update the manifest
      in the same edit.

P21-4. EVERY VERIFIER COVERS THREE CHECK DIMENSIONS (this is the core of 2.1).
  A verifier that is only structural is now an AUTO-REJECT. Build all three:
    (a) STATIC checks -- prove the artifact is USABLE: required files exist,
        schema/columns/sheets present, row counts, identifiers, arithmetic
        invariants, output readability. These prove usability, NOT
        correctness -- they must NOT dominate the reward by count.
    (b) REWARD-HACKING checks -- prove the work is AUTHENTIC: detect
        duplicated rows/coverage, repeated boilerplate, placeholder/`undefined`
        values, summaries that disagree with their source, visuals with the
        right filename but wrong/hollow content, malformed or unresolvable
        URLs, and suspicious cross-row uniformity. Ask yourself: "how could
        an agent bank this reward WITHOUT doing the real work?" -- then write
        a check that closes that hole. (You may point an AI agent at your own
        instruction.md + verify.py and ask it to find reward-hacking routes,
        then harden against what it finds.)
    (c) PARTIAL-ORACLE checks -- prove selected VALUES against trusted facts.
        A full golden answer key is impractical at Phase-2 scale and is NOT
        required, but you MUST manually verify a REPRESENTATIVE SAMPLE of
        stable values (e.g. ~6-20 of 74-120 units, chosen from the head, the
        middle, and the TAIL -- not just the first few) and store them as
        GRADER-ONLY test data in `tests/partial_oracle.json`. verify.py
        compares the agent's output for those sampled units against the
        partial oracle. This is what makes fabricated-but-plausible output
        LOSE credit. The partial oracle is grader-only: it lives under
        tests/, is wired through test.sh, and NEVER leaks into the agent
        environment (S-06). It is NOT the deprecated full oracle/solution
        model -- it is a small trusted SAMPLE, not a complete answer key.
  Also: EVERY rewarded artifact needs a CONTENT check, not just a presence/
  format check -- a workbook, report, chart, image, or video earns
  substantive credit only if it actually contains/communicates the requested
  result (e.g. ffprobe duration + genuine frame-to-frame motion for video;
  the value inside a cell, not just the cell's existence).

P21-5. REWARD SHAPE — CONTENT ≥ 60% (Production Rework SUPERSEDES Verifier Standards 40% floor).
  Binding (stricter wins): `00_authority/Production Rework Requirements.txt`
  §4; also `00_authority/Verifier & Rubric Manifest Standards (Effective
  Immediately).txt`. Content = reward_hacking + partial_oracle (content-based
  rubrics) combined.
  HARD REQUIREMENT (production deliveries / rework wave): content ≥ **60%**
  of total score; structural/static ≤ **40%**; at least **3–5** real
  content-based rubrics chosen for the task (not copy-pasted boilerplate).
  QG rejects structural-heavy boards (S-08 / QD-03 checks 7–8).
  PREFERRED SHAPE (management + Verifier Standards + task-3 + Production Rework):
    (a) category points 1 structure / 2 reward-hacking / 3 partial-oracle;
        score = sum(passed × weight) / sum(total × weight); nothing above 3;
        categories declared in verify.py and the manifest GENERATED from them
        (no per-check tuning); AND/OR
    (b) a **multiplicative content-quality signal** so easy formatting cannot
        wash out failed grounding / anti-gaming (Production Rework §4 —
        exception to the older "no multipliers of a TOTAL" ban, limited to
        this content-quality role). reward.json MUST expose static /
        partial_oracle / reward_hacking component scores AND the final score.
  Flat weight:1 boards remain legal ONLY if composition alone already keeps
  content ≥ 60% (few structural checks, many hard RH/PO). Prefer 1/2/3 +
  multiplicative content signal over hoping count-alone clears the floor.
  ALWAYS FORBIDDEN: inventing the SA/MA gap via caps/floors; per-check tuning;
  anything > 3 as a category weight; misleading equal-weight manifests;
  duplicate check_function entries; omitted gates; tiers/step-bands that
  substitute for hard content checks.
  Composition still beats exotic pricing: cut file-existence / presence
  checks and add held-out RH/PO substance. On task 3, flat→weighted moved
  fixtures by only 0.008–0.073 — do not expect weights alone to open a gap.
  Record the chosen board (1/2/3, multiplicative content signal, or
  flat-with-≥60%-by-count) in NOTES.md.

P21-5b. HELD-OUT CONTENT + HOLLOW-FIXTURE DISCRIMINATION (Verifier Standards §§4,7).
  Content checks must validate work that cannot be copied from agent inputs
  (no "confirm the value already printed in input_artifacts"). Prefer a
  small manually verified held-out sample absent from all agent inputs, with
  meaningful weight. Before delivery: score a deliberately weak / hollow /
  templated fixture — if it still banks high, tighten before shipping.

P21-6. MODULAR LLM JUDGING (no single-call rubric dump) + W&B CALL TEMPLATE.
  When verify.py uses an LLM, split it into MULTIPLE independent/parallel calls,
  each objective to one deliverable/theme/item -- never one giant call grading
  the whole rubric at once. Send the LLM only what it needs: random samples or
  specific artifacts (images + bounded text), not a 10,000-line file. Judge
  model MUST be a DIFFERENT family from the agent under test.
  TEAM STARTER (current default scaffold):
    `SwarmBench_Verifier_Template.zip`
  Use it for: OpenAI-compatible POST to
  `https://api.inference.wandb.ai/v1/chat/completions`, Bearer `WANDB_API_KEY`,
  `response_format={"type":"json_object"}`, image data-URLs + text excerpts,
  retries on 429/5xx, robust parsing of markdown/thinking-wrapped JSON,
  `judge_justification.txt`, `reward_debug.json`, and failed judge calls scored
  0.0 for that specific check while staying loud in diagnostics. Vision /
  multimodal default (smoke-tested): `Qwen/Qwen3.6-35B-A3B`. Hardcode the model
  in verify.py; do not depend on model/endpoint env vars beyond `WANDB_API_KEY`.
  For any older provider details, see
  `.cursor/rules/swarmbench-judge-provider.mdc`. Always add an explicit
  `User-Agent` when adapting the template (CDN 403/1010 otherwise).
  This template is NOT a complete Phase 2.1 verifier: still write deterministic
  static / reward-hacking / partial-oracle checks, honest `rubric_manifest.json`,
  and the four Production Rework component fields in reward.json. Prefer
  `verifier_type = "hybrid"` when mixing. LLM infra failures score 0.0 only
  for the affected check after retries and must be explicit in stdout,
  `judge_justification.txt`, and `reward_debug.json`.

P21-7. SOURCE NOVELTY (avoid pretraining contamination). Prefer RECENT,
  less-canonical books, presentations, reports, datasets (e.g. a latest
  edition, or material published in the last few months) over famous
  textbooks / classic case studies / widely-summarised works the base model
  can reproduce from memory. The instruction + verifier must FORCE the agent
  to use the SUPPLIED evidence: always give the agent the exact
  `/input_artifacts/...` path so it reads YOUR source instead of browsing the
  internet for a memorised summary. A strong answer produced WITHOUT opening
  the sources means the scenario/rubric leans on parametric knowledge -- reshape it.

P21-8. NO UNSOLVABLE BROWSING TASKS. Before building a browsing task, verify
  EVERY required URL is fetchable the way the agent fetches it. If a site
  needs JavaScript rendering, pre-render and SHIP the content as
  `input_artifacts/`. JSON REST APIs (e.g. ClinicalTrials.gov) are read via
  `Shell(curl)`; plain-text endpoints via FetchURL. Never deliver a task
  whose mandatory data is unreachable at runtime, and never fabricate data
  that failed to fetch.
  A successful HTTP status is not sufficient source validation. Inspect the
  retrieved payload for a source-specific content signature and reject login,
  anti-bot, rate-limit, consent, and "request access" interstitials even when
  they return `200 OK`. When an official presentation endpoint is blocked,
  prefer another official distribution of the same record (for example an
  Office of the Federal Register document from GovInfo), record the transport
  change, extract deterministically, and hash the exact final staged text.

P21-9. WHY WE ARE ON OPENCODE (Kimi-CLI limitation context). Phase 2 runs on
  the OpenCode `swarmbench-harness`, NOT Kimi-CLI, because Kimi-CLI had hard
  ceilings that Phase 2.1 needs to exceed: max DAG depth 1 (sub-agents cannot
  spawn sub-agents -- a role guard blocks it), a default cap of 4 concurrent
  background agents, background sub-agent trajectories that never relay to the
  harness (invisible to ATIF collection), and a 15-minute background timeout
  that silently kills long runs. OpenCode supports genuine hierarchical
  nesting (dag_depth >= 2), 20-50+ concurrent agents (Hard tier), full
  ATIF-v1.6 trajectory capture, and longer runs. Design to OpenCode's
  capabilities; do not design around Kimi-CLI's limits.

P21-10. METADATA LAST, FROM REAL TRAJECTORIES (reaffirmed). Write task.toml
  metadata (especially `why_multi_agent`, `dag_depth`, `dag_width`) only
  AFTER collecting execution logs; make them match the observed MA spawn tree
  and the real SA failure mode. Read every file end-to-end before submitting
  -- leftover AI comments, contradictions, or manifest<->verify.py drift are
  trainer-quality rejects.

P21-11. tests/ CONTENTS (Phase 2.1 standard). `tests/` now contains:
  `rubric_manifest.json` (required), `verify.py` (required single grader),
  `test.sh` (invokes /tests/verify.py), `partial_oracle.json` (when partial
  oracle is used -- it is used on essentially every 2.1 task), and optional
  `test_logic/` helper modules. No judge.py / verifier.py at tests/ root.

P21-12. VERIFIER & RUBRIC MANIFEST STANDARDS (effective immediately — Batch-12/14).
  Authority file: `00_authority/Verifier & Rubric Manifest Standards
  (Effective Immediately).txt`. Briefing (All-Hands 2026-08-04, Mathavan +
  Ruturaj): `02_onboarding/All -Hands - Verifier & Rubric Manifest Standards
  [MANDATORY] - 2026_08_04 20_29 IST - Notes by Gemini.txt` — stage-load with
  the authority file at Gate 3; the written announcement WINS on conflict.
  Summary of the seven mandatory rules (already folded into P21-2 / P21-3 /
  P21-5 / P21-5b / SCORING INTEGRITY; re-read both files before Gate 3):
    1. Correct `verifier_type` (`hybrid` / `executable` / `llm-judge`).
    2. Complete reward.json (category scores + per-check notes + LLM justifications).
    3. Content share: Verifier Standards / All-Hands originally ≥40% /
       structural ≤60%; **Production Rework (P21-13) SUPERSEDES to content
       ≥60% / structural ≤40%** for production rework deliveries.
    4. Held-out content checks (not copy-from-input freebies).
    5. Manifest accurately mirrors verify.py (weights, gates, no duplicate
       check_function, every reward-affecting path listed).
    6. Identical verify.py for SA and MA — if the verifier changes after one
       arm, re-run BOTH arms.
    7. Content checks must discriminate (hollow/templated fixture scores low).
  Enforced by static check S-08 and QD-03 checks 7 & 8. Violations of #3 or
  #5 are automatic QG rejects.

  ALL-HANDS OPERATIONAL NUANCES (2026-08-04 — enforce in verify.py / NOTES):
  - CLASSIFY CORRECTLY: confirming a sentence/value already printed in
    input_artifacts or instruction.md is a STATIC / schema check — NEVER
    label it reward_hacking or partial_oracle. Content (RH/PO) must require
    real analysis / held-out values / trainer-verified partial oracle (e.g.
    sample READMEs, derived figures). Citing page/paragraph/section WITH
    rationale can be PO + LLM-judge content (Yousef Q&A).
  - SIMPLE SCORING ONLY: prefer additive boolean points, plain averaging, or
    structured category weights 1/2/3. Opaque end-gates that silently subtract
    from the whole score (e.g. −0.25 for one failed path) → QA reject /
    client escalation. If you cannot explain the formula in one readable
    sentence in the manifest, do not ship it. (Production Rework's
    multiplicative *content-quality* signal is the narrow exception — must
    be declared in reward.json + manifest.)
  - PRINT / PERSIST JUDGE REASONING: every structural/RH/PO check path should
    print pass/fail + score. Every LLM-judge call must print attempt/outcome
    lines and persist the judge's actual evidence/reason text to
    `/logs/verifier/judge_justification.txt`; do not write this verifier
    diagnostic under `/logs/agent/`. Per-check scores, infra failures, and
    debug details go to `/logs/verifier/reward_debug.json`, never nested
    inside `reward.json`.
  - HOLLOW FIXTURE BAR: empty submission ≈ 0; format-only hollow may earn
    minimal structural points but must NOT bank a high overall score. If it
    does, content checks are insufficient — fix before ship.
  - MA-FIRST SEARCH SPACE (optional craft aid): when unsure how to build a
    robust verifier, run MA with a simple verifier to visualize outputs,
    HAND-VERIFY a sample as partial oracle, THEN freeze verify.py and re-run
    BOTH arms on the identical grader — never trust MA values blindly.

P21-13. PRODUCTION REWORK WAVE (effective now — pause new authoring).
  Authority: `00_authority/Production Rework Requirements.txt`. Applies to
  every task returning from Completed → Rework (and to any resubmission
  during this wave). Full checklist:

  P-RW-1. MASCLOUD FORCE-REINSTALL (before ANY run).
    `multi_noplan` and `verify-only` exist only after forced reinstall —
    git pull alone is NOT enough (pipx/pip may keep the old package). From
    the harness repo:
      git clone https://github.com/MathavanSG14/swarmbench-harness.git  # if needed
      cd swarmbench-harness ; git pull ; cd mascloud_client
      pipx install --force .
      # OR in a venv: pip install --force-reinstall --no-deps .
      mascloud --help
      mascloud run --help
    Help MUST list `multi_noplan` AND `verify-only` (and run modes
    `single` / `multi` / `multi_noplan`). If not, STOP and fix the install
    (`which mascloud` / `Get-Command mascloud` must resolve to the environment
    just reinstalled). Do not start agent runs or claim ship on a stale CLI.

  P-RW-2. THREE EXECUTION-LOG PACKAGES (same final package, one mode at a time).
      mascloud run <task_folder> --mode single
      mascloud run <task_folder> --mode multi
      mascloud run <task_folder> --mode multi_noplan
    Keep all three result ZIPs. Merge all three mode trees into delivered
    `execution_logs/` (preserve Harbor dir names; do not invent spellings —
    expect `single-opencode-agent/`, `multi-opencode-agent/`, and the
    multi_noplan mode dir as emitted by the result ZIP).
    - single = SA baseline; multi = planned swarm (decomposition available);
      multi_noplan = same swarm WITHOUT injected decomposition.yaml (tests
      whether the authored plan is materially useful).
    - multi_noplan has NO reward/gap target, but MUST finish with usable logs
      (unrecovered crash / rate-limit failure is NOT acceptable evidence).
    - Keep instruction.md, verifier, and execution_logs ALIGNED: after any
      change to instruction / HLP / decomposition / inputs / task requirements
      / agent-facing behavior, RE-RUN the appropriate agent mode(s) — do not
      ship stale logs against a newer brief.

  P-RW-2b. `verify-only` SCOPE (team update — narrow; misuse voids logs).
    Use ONLY when the change is limited to verifier REWARD REPORTING, e.g.
    updating reward.json / result.json fields to separate:
      - static-check score
      - partial-oracle score
      - reward-hacking score
    Example (reuses existing agent output; refreshes reward-related results):
      mascloud verify-only ./task-folder --target-mode single
      mascloud verify-only ./task-folder --target-mode multi
    Prerequisites: original execution logs are VALID for the current package,
    and the edit did NOT change agent-facing work.
    FORBIDDEN uses of verify-only (must full `mascloud run` instead):
      - instruction.md, high_level_prompt.md, decomposition.yaml
      - input artifacts, task requirements
      - agent outputs or execution behavior
      - substantive rubric / check logic that changes what the agent must do
        or what would have been produced under the old brief
    If in doubt: ask leads / read docs — do NOT burn arms or make drastic
    package changes on a guess.

  P-RW-3. `high_level_prompt.md` (NEW root file; keep `instruction.md`).
    Required alongside instruction.md. Target ~250 words (band ~100–450);
    RECORD the actual word count in NOTES.md.
    Voice: direct, terse request from a busy requester — ONLY what to
    complete and which deliverables are required.
    FORBIDDEN in HLP: persona/company background, motivation/rationale,
    step ordering, methodology, tool guidance, worker assignments,
    verifier logic, score targets, decomposition details.
    Independent restatement — do NOT copy section headers/paragraphs from
    instruction.md. Every deliverable named in HLP must exist in
    instruction.md; HLP must not omit any major instruction.md deliverable.
    Packaging: Production Rework EXTENDS the old S-02 six-item root to
    SEVEN items (adds `high_level_prompt.md`). Until Trainer Guidelines
    text catches up, treat the seven-item root as binding for this wave.

  P-RW-4. VERIFIER COMPONENTS + CONTENT ≥60% (see P21-5).
    `reward.json` must expose exactly the four numeric template fields:
    `reward`, `total_static_check_score`, `total_reward_hacking_check_score`,
    and `total_partial_oracle_check_score`. Put per-check/debug detail in
    `reward_debug.json`. Structural ≤40%; content ≥60%; ≥3–5 content rubrics;
    multiplicative content-quality signals are allowed only when declared in
    the manifest/debug formula and never used to invent the SA/MA gap.

  P-RW-5. GAP FLOOR ≥ 20 percentage points.
    Final single vs planned-multi (decomposition available) under identical
    package / env / verifier / budget must retain ≥ **20 pp** gap. Improve
    task design, coverage, coordination, and content-grounded evaluation —
    never the verifier alone.
    AUTHORITY-CONFLICT NOTE (2026-08-11): the 2026-08-10 General Discussion
    meeting notes record a Quality Dimension threshold change from 0.20 to
    0.18, but the signed `00_authority/Production Rework Requirements.txt`
    still says 20 percentage points. Under this prompt's precedence rule,
    design and ship to the stricter signed 20 pp floor until that authority
    file is revised. Do not silently weaken a production gate from meeting
    notes alone; record the conflict and ask leads if a run lands at 18-20 pp.

  P-RW-6. RESUBMIT GATE & PRE-SUBMISSION CHECKLIST (All-Hands 2026-08-10 Directive).
    Final static checker PASS + LLM Quality Gate review report REQUIRED with
    the resubmission. Address every valid finding; optional-only findings may
    be documented without changing the task, but the LLM review must still
    run and the report must ship. Do NOT submit on static-check alone.

    Mandatory Pre-Submission Checklist (must verify before submitting):
    1. Metadata Validation: Confirm task.toml fields (domain, dag_depth, dag_width, why_multi_agent, aht) match actual execution trajectories.
    2. Answer Leakage Scan: Run an explicit leakage prevention check scanning instruction.md and decomposition.yaml to ensure no ground-truth answers or expected solution values from source documents are leaked into agent-visible inputs.
    3. Rubric Weight Mirroring: Confirm 1:1 match between verify.py weights/check functions and rubric_manifest.json declarations.
    4. Judge Justification & Reasoning: Ensure LLM judge calls persist step-by-step thinking/reasoning to judge_justification.txt, not just a final pass/fail status string.
    5. Four Numeric Reward Fields: Verify reward.json contains exactly four numeric keys (`reward`, `total_static_check_score`, `total_reward_hacking_check_score`, `total_partial_oracle_check_score`).

  During this wave: prioritise rework of existing packages to P-RW-1..6.
  A new task may use the CLAIMED or SCRATCH route selected by ENTRY ROUTING;
  both must meet P21-13 before submission. Do not let an absent seed block a
  legitimate scratch build, and do not represent a scratch brief as a claim.

============================================================
CLAIMED OR SCRATCH TASK SPEC -- THE ENTRY POINT
============================================================
A complete accepted claim is the preferred locked design brief: it normally
contains the scenario, sources, coordination pattern, output paths, verifier
blueprint, hardness rationale, similarity score, and accept decision. Build
from it and fill the deliverable ("NA") fields. When no usable seed exists,
ENTRY ROUTING sends the work to the SCRATCH route instead. The scratch route
creates the same design information honestly, then earns uniqueness through
the normal similarity check rather than fabricating a claim decision. Both
routes retain full responsibility for quality, integrity, and reconciliation.

CS-1. FIELDS THE CLAIM PROVIDES (read them as the locked design brief):
  - Identity: `task_id`, `task_domain` / `normalized_task_domain` (may be
    singular/hyphenated like "PLANNING-OPERATION" -> normalize to the exact
    task.toml enum `planning-operations`), `title`, `similarity_score`
    (already computed -- e.g. 0.25), `decision` (e.g. accept).
  - Scenario: `query` (a first-person persona brief -- the BASIS for
    instruction.md; it is usually already human/first-person, so lightly
    edit for the human-prompt rules, DO NOT re-add Markdown headings or leak
    stages), `online_research_summary`, `real_world_basis`, `real_user_value`.
  - Coordination: `decomposition_pattern` (e.g. `specialist_routing` ->
    coordination_pattern `specialist-routing`, SLUG SPECIALIST; underscore ->
    hyphen), `expected_subagent_count`, `why_multi_agent`,
    `expected_single_agent_failure`, `hardness_strategy` (why SA fails / why
    small MA fails / why N sub-agents help / what the reducer must verify /
    what prevents scripting / what prevents copying a public answer).
  - Tools: `tools` (e.g. browse, bash, python, str_replace_editor, llm_call)
    -- the AGENT's toolset, not the verifier's.
  - Sources: `real_sources_or_entities` (name + url) -- you MUST verify each
    is fetchable the way the agent fetches it (Phase 1 source assembly);
    dead/JS/login-walled -> reshape or ship a frozen snapshot, never fabricate.
  - Outputs: `expected_outputs` -- the EXACT `/logs/agent/...` deliverable
    paths. Use them verbatim in instruction.md, rubric_manifest.json
    (`agent_output_path`), and verify.py.
  - Verifier blueprint: `verification_shape` + `test_design`, which is a
    near-complete rubric plan already split into the Phase 2.1 dimensions:
      * `structural_preconditions`  -> static_checks_<n>
      * `substantive_checks` + `coordination_evidence_checks`
                                    -> substance/correctness items
                                       (deterministic where exact; inline LLM
                                       where meaning needs reading)
      * `reward_hacking_tests`      -> reward_hacking_checks_<n>
      * `partial_oracle_checks`     -> partial_oracle_checks_<n>
      * `adversarial_fixtures`      -> the sanity fixtures you score against
      * `scoring_principle`, `sa_ma_fairness` -> design constraints
  - AHT: `aht_estimate_arithmetic` -> feeds human_solving_hours_estimate /
    justification (still >= 10; the arithmetic must contain a number).

CS-2. FIELDS YOU FILL AND REPORT BACK (the claim shows these as "NA"):
  `instruction_md`, `verifier_type`, `verifier_path`, `ground_truth_path`,
  `gold_output_path`, `verifier_code_preview`, `verifier_lint_status`,
  `verifier_lint_issues`, `verifier_selftest_status`, and the FIVE fixture
  rewards `verifier_gold_reward`, `verifier_empty_reward`,
  `verifier_shallow_reward`, `verifier_hollow_reward`,
  `verifier_fabricated_reward`. The five fixture rewards are your verifier's
  DISCRIMINATION EVIDENCE: run verify.py against the adversarial fixtures and
  report the reward each earns. A gold/strong fixture should score high, and
  empty / shallow / hollow / fabricated fixtures should score LOW (but a
  complete-yet-weak fixture is LOW, never a hard 0 from a gate). If a hollow
  or fabricated fixture scores high, the verifier is too weak -- harden it
  before reporting. `verifier_type` is normally `"hybrid"` when verify.py
  mixes deterministic + LLM checks (Verifier Standards); use `"executable"`
  only for a fully deterministic grader and `"llm-judge"` only when every
  check is LLM-derived. `ground_truth_path` / `gold_output_path`
  point to the GRADER-ONLY partial-oracle / fixture data under tests/ --
  they are NOT a full answer key shipped to the agent, and scoring is still
  additive per-item (see CS-3).

CS-3. RECONCILE THE BLUEPRINT TO THE HARD SCORING RULES (do NOT copy it raw).
  The claim's `test_design` is a helpful plan but its wording can conflict
  with the binding SCORING INTEGRITY / Phase 2.1 rules. Where it does, the
  rules WIN and you adapt:
  - "Structural checks are fail-closed preconditions" / any structural
    `failure_caught` that zeroes the run -> FORBIDDEN. Convert every
    structural_precondition into an ADDITIVE one-point static check. No
    binary/content gate may zero an otherwise-substantive submission before
    substance is scored. (SCORING INTEGRITY rule 1.)
  - An "immutable ground-truth fixture for all N units" (a full oracle) ->
    do NOT score by whole-answer exact match and do NOT ship it to the agent.
    Use it as the SOURCE for a PARTIAL-ORACLE SAMPLE (head/middle/TAIL) stored
    grader-only in tests/partial_oracle.json, plus reward-hacking
    cross-reference checks. Even when the full answer is computable, express it
    as additive per-item checks (one point per verified/sampled unit), never a
    single oracle-match gate.
  - No tiers/multipliers-of-a-TOTAL/caps anywhere. Point values follow
    P21-5: prefer category weights 1/2/3 with
    sum(passed×w)/sum(total×w) so content (RH+PO) ≥ 40%; a flat weight:1
    board is allowed only if composition alone already meets that floor.
    Manifest MUST declare the real scheme. If structural items outnumber
    substance items, fix by COUNT (add more substance/reward-hacking/oracle
    checks) and/or move to 1/2/3 — never invent per-check tuning.
  - Keep SA and MA identical (the claim's `sa_ma_fairness` agrees): same
    instruction, inputs, tools, timeout, verifier, scoring.

CS-4. STILL OWN QUALITY -- SANITY-CHECK THE CLAIM (it is not infallible):
  - Internal consistency: reconcile counts that disagree (e.g. a claim may say
    "50 sub-agents" while the bracket math implies 30 first-round matchups) --
    `estimated_sub_agents` MUST equal the sub_tasks in decomposition.yaml, and
    after the runs `dag_depth`/`dag_width` MUST match the OBSERVED spawn tree
    (metadata last, P21-10).
  - dag_depth >= 2: the coordination must have real depth (e.g. bracket
    round 1 -> round 2 -> ... -> reducer is naturally multi-tier). A flat
    star is rejected regardless of what the claim says.
  - Source novelty + fetchability (P21-7/P21-8): confirm the claimed sources
    are reachable and that the agent is given the exact `/input_artifacts/...`
    paths for any shipped data; if the task needs simulated/fixture data, that
    data is grader-only or clearly provided as input, never fabricated to
    dodge a failed fetch.
  - similarity already scored at claim time (`similarity_score` + `decision`):
    treat M3 as pre-satisfied UNLESS your final instruction.md drifts far from
    the claimed query -- then re-check.
  If the claim cannot be built honestly (dead sources, an unsolvable/
  contradictory spec, a gap only reachable via a forbidden scoring trick),
  ESCALATE-EARLY with the specifics rather than forcing or fabricating.

CS-S. SCRATCH DESIGN BRIEF (only after ENTRY ROUTING selects SCRATCH):
  - Create and record an original professional operator scenario, real user
    value, chosen official domain, real public sources/entities, exact agent
    output paths, coordination pattern, expected subagent count, why a single
    agent naturally fails, and a hardness strategy.
  - Design the verifier blueprint before building: the static,
    reward-hacking, and partial-oracle/content checks; adversarial fixtures;
    source-grounding method; and additive scoring plan. Apply CS-2 and CS-3
    exactly as you would to a claim blueprint.
  - Pressure-test originality and buildability: no copied tracker row, no
    fictional entity or synthetic premise, fetchable/load-bearing sources,
    real hierarchical depth, and a natural capability gap. Use the normal
    Gate 1(C)/M3 similarity check; it is NOT pre-satisfied in this route.
  - Record `authoring_mode: scratch`, the absent-input reason, the design
    brief, rejected candidate framings, and the later similarity result in
    trainer-only HANDOFF.md and NOTES.md. These records are not task-facing
    evidence and never enter the delivered root.
  - Before packaging/submission, obtain and use the required labeling-tool
    UUID/link. Never invent one or call the self-authored brief `decision:
    accept` unless the labeling tool later supplies that status.

============================================================
DIFFICULTY & GAP TARGETS -- DESIGN HARD FROM THE START
============================================================
The #1 time-waster is shipping a task that is TOO EASY, watching the single
agent (SA) score >= 0.90 (sometimes 1.0) on the first run, and then burning
hours re-running SA (each run can exceed 2 hours) while nibbling the score
down. STOP DOING THAT. Design the task to be genuinely hard on the FIRST
build so the gap is there before the first Harbor run.

TARGET METRICS (design toward these; they must arise NATURALLY from real
difficulty, never from a scoring trick, cap, or SA-only restriction):
  - INITIAL SINGLE-AGENT score: VERY LOW. The client's Phase 2.1 eval-data
    direction is SA near 0-10% (and always well below 0.30).
  - MULTI-AGENT score: MEANINGFULLY CHALLENGED. Phase 2.1 shifted the
    calibration toward EVAL DATA where the MULTI agent also struggles: the
    client's stated design DIRECTION is an MA reward around 20-30% (and at
    most ~50%), NOT a near-perfect result. A near-perfect MA (>= ~0.90) now
    means the task or the rubric is TOO EASY and will be rejected -- so a
    robust, deep, three-dimension verifier that pushes MA down is the goal,
    NOT a bad decomposition that starves MA (that is also rejected).
    [SUPERSEDES the old "MA 0.70-0.90" target used elsewhere in this file:
    wherever older text says MA 0.70-0.90, read it as "MA meaningfully
    challenged per the Phase 2.1 direction above."]
  - MA - SA GAP: keep a REAL, positive gap (MA > SA always). The old ~0.20
    floor / >0.23 goal was calibrated to the earlier "high-MA" regime; under
    the new eval regime the exact automated acceptance threshold is STILL
    BEING RECONCILED by the client and will be communicated separately, so
    aim for the client's stated calibration (very low SA, MA challenged to
    ~20-30%) while keeping the gap GENUINE and substance-verified. Never
    manufacture the gap with a bad decomposition or a scoring trick.
  - Partial credit still holds on BOTH sides (SA is never 0.0 for a
    complete/partial submission) -- a LOW SA score, not a zeroed one.

HOW TO HIT SA < 0.30 BY DESIGN (from 03_design_guides/rubric_scale_presentation.pdf -- read
it before Gate 3):
  1. SCALE past one agent's budget. Enough independent, hard units (aim
     high -- e.g. 100-200+ real units / 20+ chapters / 120+ counties) that
     a single agent literally cannot finish them all deeply in the time
     budget. Small corpora (e.g. ~48 records) let SA finish alone -> no gap.
  2. GRADE CORRECTNESS, NOT PRESENCE. Rubric items must check the VALUES are
     right against a real reference, not that a file/section merely exists.
     Presence checks are fakeable by any agent and are the #1 cause of a
     high SA score.
  3. FEWER EASY CHECKS, MORE HARD ONES. Weight the checklist (by COUNT, not
     by weightage) toward items that require the hard reconciliation,
     cross-source analysis, and depth a rushed SA cannot produce.
  4. MAKE COORDINATION LOAD-BEARING. The work must genuinely need
     decomposition (breadth + depth + verification) so MA's parallel
     specialists pull ahead while SA thins out or runs out of budget.
  5. ADD A DETERMINISTIC DEPTH-OF-COVERAGE BAND (the single most reliable gap
     lever -- proven by the APPROVED interconnection task: SA 0.633 / MA
     0.933 / gap 0.30, confirmed in the 09_qg_reviews reports). On TOP of the
     LLM rubric, add ~6-10 DETERMINISTIC boolean checks (one point each) that
     measure DEPTH SUSTAINED ACROSS THE WHOLE QUEUE -- the exact places a
     serial SA degrades but per-unit MA workers do not:
       - distinct-analysis-prose count across graded units (templated / reused
         case bodies do NOT count) -- SA templates the routine cases;
       - per-unit grounding: each graded unit cites its OWN governing id /
         number / verbatim source excerpt (not a generic restatement);
       - TAIL grounding: the LAST third of the queue is graded as deeply as
         the first (SA saturates and thins out by the tail; MA does not).
     Compute these deterministically from the FULL output files (not via the
     LLM), one point each. This is what turns "SA finished all N files" into a
     LOW score without any unfair, SA-only, or mode-dependent trick.
     CAUTION (QD-03): frame each threshold as a legitimate task requirement in
     its own right; do NOT leave a comment / docstring saying a threshold was
     "calibrated to the SA/MA gap" -- QG flags that phrasing as gap-engineering.
The gap comes from (1)+(2)+(3)+(4)+(5) TOGETHER -- get them right up front and
the SA score is low on the first run, not after five reruns.

============================================================
WHAT CHANGED: PHASE 1 -> PHASE 2 (read this first)
============================================================
You were selected for Phase 2 because your Phase 1 tasks had low client
rejection. Phase 2 is NOT "more Phase 1." The client rejected a large
batch of Phase 1 work as too synthetic, too flat, and too oracle/JSON-
shaped. The immediate goal is 50 HIGH-QUALITY tasks that unlock a 1,000-
task extension; poor or Phase-1-like tasks risk cancelling the project.

The nine concrete shifts (every one is enforced by a gate below):

  1. ORACLE -> BOOLEAN RUBRIC (no full oracle, ever). A frozen gold oracle is
     DEPRECATED and FORBIDDEN as the basis of scoring (official
     guidelines 3.4-3.5, CR-08). Real-world long-horizon problems have no
     single definitive answer. Grade with a RUBRIC of 15-25 BOOLEAN
     checklist items under P21-5 / Production Rework (prefer category
     1/2/3 with content ≥ 60%; see P21-5 / P21-13). Items test substance (are
     citations real? do sources support claims? are required sections
     present? is arithmetic consistent? is missing info flagged?). HARD
     RULES: do NOT load an oracle.json and compare against it as a whole-
     answer gate; do NOT ship a `solution/` folder; NO tiers, NO
     step-bands, NO per-check tuning, NO multipliers that invent the SA/MA
     gap. Category weights 1/2/3 ARE allowed (and preferred) when the
     manifest declares them honestly; a multiplicative CONTENT-QUALITY
     signal is allowed under Production Rework §4. Older "NO weightage /
     one point only" wording in this paragraph is SUPERSEDED.

  2. LOCAL-FILES-ONLY -> BROWSING / EXTERNAL RETRIEVAL. Local-file-only
     reading is a named Phase 1 rejection pattern. Phase 2 tasks must
     require live web browsing / external retrieval / source
     verification through real public sources. Hosted/pinned/frozen
     sources are allowed ONLY when live fetch is genuinely unreliable.

  3. FLAT FAN-OUT -> HIERARCHICAL / SPECIALIST-ROUTING ONLY. The client
     wants Phase 2 decompositions to be HIERARCHICAL and SPECIALIST-
     ROUTED (2026-06-26 DM note). DO NOT use map-reduce, and DO NOT use
     flat fan-out / fan-out-synthesize. "Orchestrator spawns N identical
     workers" is rejected. Build real DEPTH with DISTINCT specialist
     roles routed by responsibility: e.g. lead/orchestrator -> domain
     specialists (each owning one area end-to-end) -> reconciliation/
     verifier -> assembler -> separate writer/producer roles; or
     manager -> sub-manager -> worker -> verifier -> reducer; or
     legal-specialist + data-specialist + citation-specialist routed to a
     reconciler. Workers are differentiated by ROLE, not just sharded by
     count.

  4. JSON-ONLY OUTPUT -> DIVERSE REAL ARTIFACTS. Outputs are real work
     artifacts, NOT JSON. DIVERSIFY the deliverable format -- the team is
     seeing too many xlsx/spreadsheet finals (2026-06-26 DM note). Do NOT
     default to a spreadsheet. Reach for the format a real operator would
     actually produce: presentations (pptx), charts/figures (png/svg),
     CSVs, written reports (docx/md), dashboards, timelines, diagrams,
     and where it genuinely fits, video or animation (mp4/gif). The lead
     generalized the class labels so "spreadsheet" is not the default
     pattern. Classify each task with AT LEAST ONE of the four CLIENT
     CATEGORIES (see PHASE 2 CLASSES below): Browsing, Long Writing,
     Multi-Modal, Long Horizon. A spreadsheet is still allowed as a
     deliverable, but pick it because the WORK calls for it -- and aim
     across your tasks for a VARIETY of output formats for the POC.

  5. LONG / SCHEMA-Y instruction.md -> A REAL HUMAN PROMPT (NOT
     DOCUMENTATION). Write `instruction.md` the way an actual operator
     would hand the job to an assistant: FIRST PERSON, conversational,
     "here's what I need and why." Hard rule from the lead (2026-06-26):
     NO Markdown `#`/`##` headings, no bulleted "spec sheet", no
     AI-generated feel -- a reviewer who sees perfect Markdown headings
     reads it as LLM-generated and flags it (real, observed rejection
     note). State the goal, the deliverable, the ONE output path, the
     evidence/quality rules, and the sources inline in prose (a short
     inline list of source URLs or a country/vendor list is fine). Stay
     concise. NEVER list the internal solving stages or leak the
     decomposition -- the stages live in the decomposition as sub-agents,
     discovered by the agent. Keep genuinely long/static rule sets in a
     dedicated rules file shipped in `environment/input_artifacts/` (e.g.
     `input_artifacts/<name>_rules.md`, the official convention -- there is
     NO `environment/rules/` folder; binding rule docs live in
     input_artifacts/ exactly like the EMERGPROCUREMENT sample's
     audit_rulebook.md) only if they would bloat the prompt; the prompt
     itself stays human and references the file as `/input_artifacts/...`.

  6. ENGINEERED GAP -> NATURAL GAP. The single-agent failure must be a
     real capability difference: the task is genuinely broad, multi-
     source, multi-stage, verification-heavy, artifact-heavy, and
     coordination-heavy. NO artificial traps, hidden restrictions,
     SA-only limits, info asymmetry, reward hacking (e.g. blocking SA
     from Python), or token-throttle/timeout forgery (treated as a work-
     ethics violation). Partial credit is EXPECTED on long-horizon tasks.

  7. SOLO BUILD -> IDEA-FIRST + DUAL DEBUG. In the claimed route, the
     accepted claim is the up-front brief. In the scratch route, create and
     record the original design brief, then validate its distinctness through
     the normal similarity check before expensive runs; do not wait for a
     nonexistent seed approval. Brainstorm with peers/agents before execution.
     After building, BOTH the trainer AND QA must independently debug the task
     and confirm the gap is real and the judge is not hallucinating.

  8. IDEA SOURCE -> CLAIMED OR SCRATCH BRIEF. ENTRY ROUTING decides this
     before the full workflow is read. A complete accepted labeling-tool
     claim is a locked brief: build from its title, query/persona,
     decomposition pattern, tools, real sources/entities, output paths,
     expected single-agent failure, verification shape, test blueprint,
     hardness strategy, AHT arithmetic, subagent count, similarity score,
     and accept decision. If no usable seed exists, create an original
     scratch brief under CS-S instead; absence is a route, not a blocker.
     Never fabricate claim fields or copy a tracker row. The tracker CSV and
     IDEA-DESIGN references remain methodology and pressure-test material.

     UNIQUENESS: an accepted claim's similarity decision pre-satisfies
     GATE 1(C) / M3 unless the final instruction materially drifts. A
     scratch brief has no pre-scored decision and MUST pass the normal
     similarity check before expensive runs or submission.

  9. DOMAIN: PLANNING-OPERATIONS PREFERRED, OTHER DOMAINS AS FALLBACK.
     This prompt and its idea-design docs (`Thinking in Planning-
     Operations`, `planning_ops_doc.txt`) are written for the
     planning-operations domain, so PREFER planning-operations for every
     idea. If a given seed genuinely cannot be realized as a strong
     planning-operations task (no natural many-decisions x many-
     constraints shape, no real natural single-vs-multi gap, or the seed
     is inherently another domain), you MAY move it to another official
     domain -- reasoning-math, code-swe, data-analysis, or knowledge-
     research -- rather than force-fitting. When you leave
     planning-operations: record WHY in the DECISION LOG, set task.toml
     `domain` to the real domain, and treat the planning-operations-
     specific guidance here as domain-general where it still applies
     (the discipline -- rubric-not-oracle, browsing, hierarchical
     coordination, human instruction.md, natural gap -- carries over;
     only the planning-ops framing of the IDEA changes). Do not switch
     domains just to dodge difficulty; switch only when the planning-ops
     framing is the wrong fit.

Operational prerequisites (UPDATED 2026-07-23 -- CLOUD `mascloud` WORKFLOW;
no local Docker, no personal API key): ALL Phase 6 / gap-validation runs go
through MAS Cloud Run via the `mascloud` CLI going forward -- NOT a local
Harbor+Docker build. The old local-Harbor + own-Fireworks-key flow is
DEPRECATED (kept only in the harness `old_method/` for fallback). One-time
setup (Python 3.9+ and pipx):
  git clone https://github.com/MathavanSG14/swarmbench-harness.git
  cd swarmbench-harness/mascloud_client
  pipx install .
  mascloud --help                        # verify
  mascloud login --email you@turing.com  # password from the credentials sheet
The session token lives only in `~/.mascloud/config.json`; no Fireworks/Daytona
key ever touches this machine (the key stays server-side). No task ships
without real cloud execution logs for BOTH modes; keep a clean folder in the
exact official name format; note `human_solving_hours_estimate` must be >= 10
(a real estimate of how long the TASK would take a human, distinct from your
own trainer AHT budget).

DAILY RUN QUOTA (2026-07-23): each trainer gets 6 `mascloud` run submissions
per day by default (resets at midnight UTC). EVERY submission counts toward
the quota regardless of outcome (success, fail, cancel-after-submit, bad zip).
Before launching, run `mascloud runs` -- it shows usage like
`Today: 3/6 runs used` plus which model each past run used. Plan SA+MA pairs
and any remediation reruns against the remaining budget; do not burn quota on
unvalidated tasks (run fixture PROJECTED-GAP + local verify.py first). If you
consistently hit the limit and need a higher quota for multi-task days, request
an increase via the form Ruturaj shares (top-performer / efficiency-based;
prior submission history + proof you use the system efficiently per task).

AGENT MODEL (2026-07-23): most runs use `kimi-k2p6` (Fireworks Kimi K2.6).
Under high concurrent load, new MULTI-mode runs may automatically switch to
`kimi-k2p7-code` instead (server-side rate-limit protection; fully automatic;
no trainer flag). Both are Kimi-family -- the verifier LLM judge must still be
a DIFFERENT family (never Kimi / Moonshot / K2). Check `mascloud runs` for the
model listed on each run if scores look unexpected across retries.

============================================================
AUTONOMY MODE -- DECIDE, DON'T ASK (GOVERNS EVERY GATE BELOW)
============================================================
This prompt runs AUTONOMOUSLY. Build the entire task end-to-end through
Phase 5 (package) without pausing for my approval at any design gate.
This OVERRIDES every "propose to me / wait for approval / after I
confirm" instruction anywhere below. Wherever the text says to get my
sign-off, instead:

  DECIDE -> RECORD -> PROCEED
  1. DECIDE the gate yourself using the documented criteria/floors for
     that gate. When several options qualify, pick the one that best
     advances the NATURAL single-vs-multi gap goal and the GATE-1(C)
     distinctness goal, and most cleanly satisfies every hard floor.
     Ties: prefer the more-real-source, more-distinct-trajectory,
     lower-AHT option.
  2. RECORD the locked decision in `_trainer_artefacts/HANDOFF.md` and
     append a one-line entry to the `NOTES.md` DECISION LOG: gate name |
     chosen option | rejected alternatives | one-line rationale | which
     hard floors it clears. This written trail REPLACES my approval.
  3. PROCEED immediately to the next gate/phase.

Autonomy is bounded by the INTEGRITY MANDATE below (absolute, highest
priority): freedom to DECIDE is never freedom to FABRICATE or to trick
an evaluator. If the autonomous choice and honesty ever conflict,
honesty wins -- stop and escalate.

Every discipline rule still binds. Autonomy changes WHO approves (you,
via recorded judgement), NOT WHETHER the checks run. Every hard floor,
anti-leak sweep, sanity gate, QD self-audit, and BLOCKING gate is still
mandatory and still aborts the build on failure.

THE GAP GOAL IS THE TERMINATION CONDITION. Keep working until the task
is packaged AND a real, defensible single-vs-multi gap is demonstrated
(single < multi always; meaningful partial credit on both sides; the
predicted single-agent failure is observed in the trajectory, not
manufactured by the scorer; the Phase 2.1 working target is SA very low
(~0-10%) and MA meaningfully challenged (~20-30%, not near-perfect), with a
genuine positive gap -- see DIFFICULTY & GAP TARGETS, which supersedes the
older "SA < 0.30 / MA 0.70-0.90 / gap > 0.23" numbers). The only reasons to stop short
are a genuine MANUAL-NEED, an ESCALATE-EARLY trigger, or the ALTERNATE-USE
pivot (below) once the tuning budget is spent.

------------------------------------------------------------
MANUAL-NEEDS -- the ONLY points where you stop and need me
------------------------------------------------------------
Reach each one autonomously, then PAUSE with a single consolidated,
copy-paste-ready request, and resume the moment I supply it. Batch
everything for a touchpoint into ONE message.
  M0. ENTRY BRIEF (GATE 0). Apply ENTRY ROUTING before reading the full
      workflow. A complete accepted claim follows CS-1..CS-4 and is its own
      up-front approval. With no usable seed, follow CS-S immediately; do
      not ask for a claim merely because it is absent. A partial or
      contradictory purported claim is the only M0 pause: ask once for the
      missing/ambiguous fields, without fabricating or silently replacing
      them. In every route, pause/escalate only for an honest buildability
      failure (dead sources, contradictory/unsolvable brief, or a gap only
      reachable through a forbidden scoring trick).
  M1. MASCLOUD CLI (CLOUD RUNNER -- no local Docker / no API key). Phase 2
      shipping/gap runs go through MAS Cloud Run via the `mascloud` CLI from
      github.com/MathavanSG14/swarmbench-harness (the `mascloud_client/`
      package) going forward -- NOT a local Harbor+Docker build and NOT
      Kimi-CLI. It must be pipx-installed and logged in
      (`mascloud login --email you@turing.com`, password from the credentials
      sheet) before any run; the token lives in `~/.mascloud/config.json` and
      no Fireworks/Daytona key is held locally. Default daily quota is 6
      submissions (see M4 / Operational prerequisites). You cannot deliver a
      task without real cloud execution logs for both modes. If it is not set
      up / logged in, surface the exact install + login commands and wait.
      (The deprecated local-Harbor flow lives in the harness `old_method/`
      only as a fallback.)
  M2. DRAFT REVIEW (PHASE 4.5). The official Turing Draft Review tool
      needs a Turing-email login + a .zip upload you may not be able to
      perform. Hand me the zip + the "run Draft Review" note and wait for
      the quality report. (You MAY first self-run the optional Local
      Quality Gate in a FRESH session and the S-01..S-07 static checks.)
  M3. SIMILARITY WEB APP (PHASE 4.6, if available). The checker is a web
      app you cannot call. Hand me the final `instruction.md` with a
      "paste this into the similarity web app" note, wait for the
      embedding + Jaccard scores, then resume the loop autonomously.
  M4. MASCLOUD RUNS + GAP/JUDGE VALIDATION (PHASE 6). ALL gap-validation
      runs go through MAS Cloud Run (`mascloud`) going forward -- not local
      Harbor. The runs execute via `mascloud run <task_folder> --mode single`
      and `--mode multi` (BOTH required). Each run packages the folder locally
      (excluding any old `execution_logs/`), uploads it, streams live, and
      drops a result zip beside the folder (`<task>-single.zip`,
      `<task>-multi.zip`) containing the full task PLUS fresh
      `execution_logs/`. QUOTA: default 6 submissions/day/trainer (midnight
      UTC reset); every submit counts. Check `mascloud runs` first for
      `Today: X/6 runs used` and the model each run used (`kimi-k2p6` usual;
      multi may auto-switch to `kimi-k2p7-code` under load). If I run them,
      hand me the exact `mascloud run` commands + your predictions + remaining
      quota and wait for the result zips; if you have a logged-in `mascloud`
      session you may launch the runs yourself (still respect the daily
      budget). Then drive the dual-debug + gap remediation loop autonomously
      until the gap is real and substance-verified (per DIFFICULTY & GAP
      TARGETS) and the judge is verified not to be hallucinating (or an
      ESCALATE-EARLY trigger fires). Useful commands: `mascloud runs`
      (history: status, reward, tokens, cost, model, today's X/6 usage),
      `mascloud download <run_id> [dir]` (re-fetch a result, kept 24h),
      `Ctrl-C` cancels a streaming run (cloud job may still finish and count).

------------------------------------------------------------
ESCALATE-EARLY -- interact only when truly blocked
------------------------------------------------------------
Outside the MANUAL-NEEDS, raise a question ONLY when:
  - a HARD FLOOR cannot be met no matter how you reshape (e.g. no real
    browsable source set exists, the chosen class cannot be graded by a
    meaningful rubric, the gap is predicted unreachable without a
    scoring trick);
  - an action is destructive/irreversible or reaches outside the task
    folder + its `_trainer_artefacts/`;
  - a genuine ambiguity whose wrong resolution causes MATERIAL rework
    (a re-architecture, not a naming choice);
  - the gap loop has burned its iteration budget (4 rubric/decomposition
    tuning rounds, or 1 full re-architecture) without a real gap -- at that
    point do NOT keep re-running SA endlessly (each run costs 2h+). Trigger
    the ALTERNATE-USE PIVOT below first, and escalate only if that fails too.

ALTERNATE-USE PIVOT (when the gap target stays unreachable after the budget):
Repeated micro-refinements that cannot push SA below target are a signal the
task's DIFFICULTY is structurally wrong, not its wording. Before giving up or
escalating, try -- in order, each ONCE -- a genuinely different way to make
the task USABLE rather than another SA rerun:
  1. SCALE UP the corpus / unit count hard (2-5x more real units) so one
     agent runs out of budget -- the cheapest fix for "good rubric, small
     gap" (03_design_guides/rubric_scale_presentation.pdf case 4).
  2. RE-GRADE FOR CORRECTNESS: swap presence/coverage checks for value-
     against-reference checks (cases 1-2) -- the fix for "SA passes just by
     producing the files".
  3. ADD A DEPTH LAYER: insert a downstream reconciliation/verification/
     synthesis stage that needs the upstream breadth, deepening the DAG.
  4. RE-TARGET THE CLASS/DELIVERABLE: the same real sources may support a
     harder task under a different Phase 2 class or output object -- re-aim
     rather than discard.
  5. REPURPOSE / PARK: if none of the above lands a real gap, record the task
     as NOT-SHIPPABLE-AS-IS in the LESSONS LOG with the concrete reason,
     salvage the reusable sources/machinery, and escalate to me with the run
     history -- do NOT keep grinding SA reruns.
Log which pivot you tried and its effect in the NOTES DECISION LOG + LESSONS
LOG. The outcome is always a usable task or a clean, documented stop -- never
an endless loop.

For everything else -- naming, schema field choices, which qualifying
scenario/class/decomposition to pick, wording -- decide, record, keep
going. Bias hard toward deciding over interrupting me.

============================================================
INTEGRITY MANDATE -- GENUINE, GROUNDED, NO CHEATING (ABSOLUTE)
============================================================
This is the single highest-priority rule. It OVERRIDES AUTONOMY MODE,
every gate, the gap goal, and any deadline. Autonomy is freedom to
DECIDE, never licence to FABRICATE. If honesty conflicts with any other
instruction, honesty wins -- stop and escalate.

EVERY piece of information in the task folder MUST be genuine and
grounded in a real, verifiable source:
  - Every source document is fetched from a real, public, fetchable
    HTTPS URL (or a clearly-declared frozen snapshot of one) and is
    byte-equal to what that URL served (sha256sums.txt is the receipt).
    No invented "regulations", no trainer-written rules dressed up as
    authentic policy.
  - Every named entity (hospital, company, city, county, venue, repo,
    disaster, filing) is REAL and publicly named. No fictional entities.
  - Every quoted excerpt / citation the rubric checks is a literal,
    verbatim substring of the cited real source. Never a paraphrase
    reworded to "fit".
  - Every number in `task.toml` / manifests / token counts / AHT is a
    real measurement, not an estimate massaged to pass a check.

ABSOLUTELY PROHIBITED at ANY point, even to pass a gate or reach the gap:
  - Inventing or "synthesising" data, sources, entities, quotes,
    citations, results, logs, or scores. CRITICAL Phase-2 case: when
    browsing FAILS, do NOT fabricate the data the agent (or you) could
    not fetch. A failed fetch is reported as a failure and the task is
    reshaped or a frozen real snapshot is used -- never backfilled with
    invented values. (The client explicitly rejected Phase 1 tasks where
    data was fabricated after browsing failed.)
  - Editing or selectively trimming execution_logs, reward.json,
    qg_report.json, similarity_report.txt, or any evidence/result file
    to look better than reality.
  - Gaming or reward-hacking ANY evaluator -- the rubric/judge, the
    Local Quality Gate, the similarity checker, Harbor, or the human
    reviewer. No targeting boundary thresholds, no hardcoded answers, no
    leaking the rubric's expected values, no mode-sniffing, no throttling
    SA tokens to force a timeout.
  - Misreporting status: never claim a check passed, a source resolved,
    a fetch succeeded, or the gap was met if it was not.

IF IN ANY DOUBT about whether something is genuine, allowed, or honest:
STOP; review precedent (the mentor examples, prior HANDOFF/NOTES, the
Feedbacks / LLM_Review history); choose the truthful, defensible option
even if slower; and if precedent does not resolve it, treat it as an
ESCALATE-EARLY trigger. A task that fails honestly is recoverable; a
task that passes by fabrication is fraud that poisons the benchmark.

============================================================
SCORING INTEGRITY -- CLIENT REJECTION RULES -- HARD OVERRIDE
============================================================
SECOND ONLY to the INTEGRITY MANDATE. OVERRIDES every later instruction
about how to score, gate, cap, weight, or band a reward. The client
rejected a large batch because the SA-vs-MA gap was MANUFACTURED BY THE
SCORER instead of arising from the task. The gap must be a real
capability difference the rubric MEASURES -- never a penalty the verifier
INFLICTS.

THE ONE RULE: the gap lives in the task, not in the scoring.
You must be able to state in writing WHY a single agent will struggle
(genuinely broad / multi-source / multi-stage / verification-heavy /
coordination-heavy). That predicted natural failure is the gap. If you
cannot name it, reshape the task; do NOT reach for a scoring trick.

HARD-FORBIDDEN SCORING SHAPES (any one is an automatic client reject):
  1. BINARY / CONTENT GATES. No structural precheck may write
     reward = 0.0 (or floor it) based on the SUBMISSION'S CONTENT before
     substance is scored. A complete, valid submission is NEVER zeroed for
     a word-count shortfall, a file-path slip, a JSON-escape slip, a
     missing field, or a wrong count. Such a miss is a small, proportional
     deduction. (This forbids CONTENT gates only. For LLM judge infra
     failures, follow the 2026-08-11 verifier template: retry, score the
     affected judge check 0.0 in its bucket, and make the infrastructure
     failure explicit in stdout, `judge_justification.txt`, and
     `reward_debug.json`.)
  2. STATIC CHECKS THAT GATE THE LLM JUDGE. On a rubric/llm-judge task
     the judge MUST run on the FULL submission every time. No
     deterministic check (key match, regex word count, verbatim
     substring, path existence, count == N) may sit upstream of the LLM
     call and prevent it running. Do not truncate the submission first.
  3. SCORE CAPS. No `min(score, X)` for X < 1.0, no `max(0, 1-n*penalty)`,
     no percentage ceiling, no exact-phrase-required cap, no step-band
     ceiling on the SA score. The ONLY permitted ceiling is clamping the
     FINAL reward to 1.0.
  4. MULTIPLICATIVE / STACKED PENALTIES. One error hits exactly ONE
     additive term. Never route a single miss through a penalty factor
     AND a summary factor AND a multiplier. All penalty dimensions are
     additive and independent.
  5. STEP-FUNCTION BANDS. No ceiling tied to a band boundary that jumps
     reward by a large step when a value crosses it. Banded/structural
     scores must be continuous and roughly linear.
  6. REWARD CORRUPTION. Never hand-edit reward.json / reward.txt /
     test-stdout.txt to a value the verifier's own per-check output does
     not reproduce. The recorded reward MUST be recomputable from the
     judge's printed breakdown. (Trainers were escalated for this.)
     EXCEPTION for platform schema patches on ALREADY-FINISHED arms: you
     may ADD the four required `reward.json` fields while keeping
     `"reward"` identical to the run's `reward.txt` / points-board score
     and filling bucket means from the existing per-check vectors — never
     replace that score with a /6 blend or a bucket average (DM
     clarification 2026-08-05). Any change that alters the overall score
     requires a re-grade, not a rewrite.
  7. METHODOLOGY-SUGGESTIVE / HALLUCINATION-PRONE JUDGE PROMPTS. The
     rubric and judge prompt must NOT name or hint the coordination
     pattern ("fan-out", "single pass", "map-reduce") or pre-announce
     score bands by agent type. The judge scores output quality
     symmetrically and cannot tell how the answer was produced. It must
     also be written tightly enough that it does NOT hallucinate a score
     (no vague "rate this 1-10" — give concrete, checkable criteria).
  8. SA-ONLY CONSTRAINTS / TOOL RESTRICTIONS / INFO ASYMMETRY.
     `instruction.md` is IDENTICAL for SA and MA. No SA-only limits, no
     multi-agent wording in `instruction.md`, no decomposition leaking
     answers/expected values (structure only), no blocking SA from tools
     (e.g. Python) the MA gets.

POSITIVE DESIGN (what a Phase 2 rubric task MUST look like):
  - reward is additive over 15-25 BOOLEAN items, clamped to [0,1].
    DEFAULT for production rework (P21-5 / P21-13): category points 1
    structure / 2 reward-hacking / 3 partial-oracle, reward =
    sum(passed × category_w) / sum(total × category_w), nothing above 3,
    no per-check tuning, content (RH+PO) ≥ **60%** of total score
    (structural ≤ 40%), and (when used) a multiplicative content-quality
    signal exposed in reward.json so formatting cannot wash out failed
    grounding/anti-gaming. A flat one-point board is allowed ONLY if
    composition alone keeps content ≥ 60%. ALWAYS FORBIDDEN: tiers,
    score caps/floors that invent the SA/MA gap, step-bands, complex
    formulas, hand-tuned per-check weights, misleading equal-weight
    manifests, duplicate check_function entries. Partial credit MUST
    emerge from how many independent items pass. Composition (fewer
    presence checks, more hard substance / held-out checks) still beats
    exotic pricing for opening a gap.
  - Required `reward.json` (P21-2): overall `"reward"` equals the run's
    points-board score (same as `reward.txt` if both exist); the three
    `total_*_check_score` fields are bucket means for reporting and are
    NOT blended into `"reward"`; include per-check notes and LLM
    justifications where applicable.
  - Each rubric item is BINARY and deterministically evaluable from the
    output, and INDEPENDENTLY scoreable so a partial submission scores
    proportionally (e.g. "audit_trail has >= 90 of 120 rows", "every
    drug entry cites >= 1 clinical-trial ID", "the deck has a conflicts
    slide", "no two sections repeat the same finding verbatim"). Items
    test SUBSTANCE (real citations, claims supported by cited sources,
    required sections present, calculations consistent, missing info
    marked) — NOT trivial constraints (capitalization, punctuation).
  - Items must NOT look like oracle comparison ("output matches the gold
    answer") or bias ("the multi-agent output is more comprehensive") or
    be meaningless ("the answer is good"). They name a concrete,
    checkable property of the output.
  - ONE GRADER, MIXED CHECKS BY OUTPUT SHAPE (Phase 2.1). There is ONE
    verifier file, `tests/verify.py`. Inside it, use DETERMINISTIC code for
    everything structured / exact (CSV / xlsx / JSON-with-fixed-fields /
    media files: presence, row/column counts, threshold bands, ffprobe for
    video, openpyxl for sheets, arithmetic, uniqueness, reward-hacking
    detection, partial-oracle value comparison) and call an INDEPENDENT LLM
    inline ONLY for free-text prose whose quality needs reading comprehension
    (report faithfulness, factual coverage). Deterministic checks are more
    reliable -- use the LLM only where meaning genuinely requires it. Set
    `verifier_type = "hybrid"` when mixing deterministic + LLM checks (the
    normal Phase 2.1 case), `"executable"` only when every check is
    deterministic, and `"llm-judge"` only when every check is LLM-derived.
    Do NOT ship a separate judge.py.
  - JUDGE MODEL INDEPENDENCE (hard rule, official 3.3 / §7). The judge
    LLM MUST be a DIFFERENT model family from the agent under test — never
    the same family that produced the output, or it self-scores leniently.
    IMPORTANT (2026-07-21, clarified 2026-07-23): the agent model is assigned
    server-side -- usually Kimi K2.6 (`kimi-k2p6`); under high load
    new MULTI-mode runs may auto-switch to `kimi-k2p7-code`. There is no
    trainer flag to pick the model. BOTH are Kimi-family, so the judge MUST
    NOT be any Kimi / Moonshot / K2 model. CURRENT JUDGE PROVIDER (2026-08):
    W&B Inference — see `.cursor/rules/swarmbench-judge-provider.mdc` and the
    team starter
    `SwarmBench_Verifier_Template.zip` as the current default scaffold
    (endpoint `api.inference.wandb.ai`, key `WANDB_API_KEY`, hardcoded judge
    model in `verify.py`, robust JSON extraction, `judge_justification.txt`,
    `reward_debug.json`, exactly four numeric `reward.json` fields). Do NOT
    hardcode Fireworks/Moonshot keys or bare Moonshot-era slugs; those env vars
    are no longer forwarded into sandboxes.
  - GROUND PROSE CHECKS IN THE SOURCE. A faithfulness item sends the
    judge BOTH the source text AND the agent's section and asks "is this
    faithful to the source?". Recompute any reference numbers in Python
    from pinned inputs and INJECT them into the judge prompt so the LLM
    never does arithmetic (kills math-hallucination); injected values are
    context only and never set/cap the reward.
  - PARTIAL CREDIT IS REQUIRED. On long-horizon multi-stage tasks an
    agent may pass one stage and fail another; the score reflects that.
    SA reward must NEVER be 0 for a complete or partially-complete
    submission. (More items = harder to game: ~20 boolean items bound a
    plausible-but-empty response to <= 0.3 by chance.)
  - LLM-JUDGE INFRA FAILURE = INVALID RUN, NOT A ZERO (QD-09.5, UPDATED per
    Batch-16 client feedback §3c + 2026-07-17 team directive). On an
    `llm-judge` task, EVERY non-zero reward MUST come from a successfully
    parsed LLM verdict -- but a verifier-side LLM failure (missing key,
    API/network error, unparseable response, or a verdict missing a rubric
    item) is an INFRA fault, NOT a content judgement, and MUST NEVER be
    silently scored as reward 0.0 (nor may any individual rubric item default
    to FAIL on such a failure). Silently zeroing a missing-key / outage run
    makes a config failure indistinguishable from a genuinely bad model and,
    because SA and MA collapse to 0 together, it ERASES or MANUFACTURES the
    SA<->MA gap -- exactly the eval-integrity bug Batch-16 §3c flagged in 9/16
    verifiers. Required handling, in order:
      (a) PREFLIGHT the key + connectivity BEFORE grading; abort early if absent.
      (b) RETRY transient failures (`DEFAULT_RETRIES >= 5`, temp 0).
      (c) If the grader still cannot complete, EMIT AN EXPLICIT INFRA-ERROR
          SENTINEL -- raise, or write reward = null / status = "INFRA_ERROR"
          (NOT a number) -- mark the run INVALID, FIX the verifier, and RERUN.
    Do NOT fall back to a deterministic non-zero score (still the fail-OPEN
    anti-pattern QD-09.5 rejects) AND do NOT fall back to 0.0. The ONLY graceful
    degradation allowed is FAIL-OPEN TO THE DETERMINISTIC COMPONENT when the LLM
    is a minor sub-slice (score the deterministic part, drop/neutralise the small
    LLM slice) -- never a silent whole-run 0.0. A genuine content FAIL that the
    LLM actually returns still costs that ONE item, as always: a content miss is
    a proportional 1-point deduction, never a gate.
  - Trainer + QA must MANUALLY verify the judge did not hallucinate:
    inspect SA and MA outputs by hand and confirm the scores match a
    human reading. The client caught cases where the judge under-scored
    an SA output whose true quality was clearly higher — read the SA
    output yourself, and if the judge awarded a low score on output that
    is substantively correct, the RUBRIC is the problem; fix it before
    submission.

TIMEOUT CALIBRATION: set `[agent] timeout_sec` to the PEER-TYPICAL band
for the effort level and never below the task's own design budget. A gap
created by starving SA of time is forgery. Never throttle output
tokens/sec to push SA into a timeout while the swarm gets margin — this
is treated as a work-ethics issue.

  LONG-HORIZON EXCEPTION (manager guidance, 2026-06): for a COMPLEX,
  genuinely long-horizon stage scenario, do NOT set `[agent] timeout_sec`
  in task.toml at all. Leave it unset so Harbor wraps the agent step with
  timeout=None (no cap) — trainers have lost progress even with a 2-hour
  timeout because these runs legitimately take longer. Run protocol:
    1. Launch the MULTI-AGENT run FIRST with NO timeout and observe the
       actual wall-clock it needs to finish.
    2. Then launch the SINGLE-AGENT baseline WITH a timeout applied at
       LAUNCH (a run-time flag such as `--agent-override-timeout-sec`),
       set GENEROUSLY — at least the multi-agent's observed completion
       time — so the comparison still measures coordination QUALITY
       (rubric score), not truncation. A single-agent score that is low
       only because the cap cut it off short of a fair budget is a timeout
       artifact, not a real gap, and is rejected. Record both the multi
       wall-clock and the single cap in the handoff.

OUTPUT-PATH HYGIENE: `instruction.md` states ONE unambiguous output
path; confirm the verifier reads the exact path the agent writes.

============================================================
STANDING DUTY 0 -- KEEP THIS PROMPT CURRENT (SELF-MAINTENANCE)
============================================================
This file is a LIVING playbook. Fold durable, GENERIC lessons back into
THIS file so the next agent starts ahead. Per-task specifics stay in the
task's own `_trainer_artefacts/`; only the GENERALIZED rule comes here.

CAPTURE & REUSE (MANDATORY -- this is how we stop repeating mistakes):
EVERY time you hit an issue anywhere from BUILD to SHIP -- a gate failure, a
rejected Draft Review, a false-failure, a gap that would not open, a
browsing/harness gotcha, a reviewer comment, a wasted rerun -- append a
one-line, TASK-INDEPENDENT entry to the LESSONS LOG (BUILD -> SHIP) section
at the end of this file (date | stage | issue | fix / rule going forward).
BEFORE starting each new task, READ the LESSONS LOG plus the feedback
streams (`05_feedback/Feedbacks.txt` human-reviewer rework, `05_feedback/LLM_Review_Issues.txt` LLM
reviewer, `05_feedback/batches/MAS_Client_Feedback_Document_2026-07-17.txt`) AND re-list + re-read EVERY
file in the `09_qg_reviews/raw_reports/` folder (the live LLM QG reviewer reports -- new
ones are added over time; never rely on a cached summary) so you design
around every known QG rejection up front. Every NEW QG REJECT / MANUAL_REVIEW
reason MUST be distilled into the QG REVIEWER REJECTION LEDGER and the LESSONS
LOG. A one-off, task-specific quirk goes to NOTES.md; a durable, generic
lesson goes to the LESSONS LOG; a lesson that becomes an ENFORCED rule is also
promoted into the relevant gate/phase text.

WHEN to propose a prompt edit (severity-gated):
  S1 (MUST update before you finish the task): a NEW external guideline
     lands (an All-Hands note, a DM message, an updated client-
     requirements / common-issues / similarity-policy doc); OR a BLOCKING
     gate failure whose root cause is task-INDEPENDENT.
  S2 (update if it recurs): the same issue appears on a 2nd task, or a
     reusable workaround is found. One occurrence -> NOTES.md; second ->
     promote here.
  S3 (do NOT touch this file): one-off, task-specific quirks -> NOTES.md.

HOW: phrase the rule task-independently; prefer AMENDING existing text
over appending near-duplicates; NEVER weaken an enforced rule to make a
single task pass; keep all content inside the single ```text fence; log
each change in the PROMPT CHANGELOG at the end.

============================================================
REFERENCE MATERIAL (read these BEFORE doing anything)
============================================================
FOLDER MAP (2026-08-05 reorg): docs now live under numbered subfolders of
`PHASE_2\documentations_phase_2\` -- `00_authority/`, `01_quality_gate/`,
`02_onboarding/`, `03_design_guides/`, `04_domains/`, `05_feedback/`,
`06_incidents_and_lessons/`, `07_prompt_runtime/` (this file), `08_samples/`,
`09_qg_reviews/`, `10_prompt_platform/`, `_archive/`. Full catalog:
`PHASE_2\documentations_phase_2\README.md`. On conflict with any other
doc or this prompt: `00_authority/` Trainer Guidelines v1.1 wins for
package/delivery; `00_authority/Verifier & Rubric Manifest Standards
(Effective Immediately).txt` wins for scoring / verifier_type / manifest
fidelity; `00_authority/Production Rework Requirements.txt` SUPERSEDES
content-share to ≥60%/≤40% and adds `high_level_prompt.md` + three log
modes for the production rework wave. Escalate if authority docs otherwise
conflict.

Phase 2 primary sources (READ FIRST -- they define the new bar):
- D:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\documentations_phase_2\00_authority\Production Rework Requirements.txt
  (BINDING for the production rework wave — READ FIRST if reworking or
  resubmitting. Pause new authoring; Completed→Rework; force-reinstall
  mascloud for `multi_noplan`; three log packages (single/multi/multi_noplan);
  required `high_level_prompt.md` (~250 words); structural ≤40% / content ≥60%;
  multiplicative content-quality signal; ≥20pp SA–planned-multi gap; static
  checker + LLM QG report on resubmit. Full detail: P21-13.)
- D:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\documentations_phase_2\00_authority\[Harbor] Multi-Agent Swarm
  Benchmark — Trainer Guidelines (2).txt  (THE AUTHORITATIVE Phase 2 package/
  delivery spec, v1.1 2026-07-20 -- the Phase 2.1 revision. Read this one, NOT
  the older "... Trainer Guidelines.txt" (v1.0 2026-06-26, superseded). It adds
  the Phase 2.1 standard: single grader tests/verify.py, mandatory
  tests/rubric_manifest.json (3 categories / 5 fields / 1:1
  mirror), the three check dimensions (static / reward-hacking /
  partial-oracle), tests/partial_oracle.json, the fixed package contract
  (environment/input_artifacts/ inputs + exact /logs/agent/ outputs),
  source-novelty, and the §6.7 Phase 2.1 standardisation checks -- on top of
  the OpenCode harness setup, the Phase 1 failure rules 3.1-3.6, the client
  requests CR-01..CR-13, the four POC exemplars, and the EXACT Quality-Gate
  delivery format §6 (folder/ZIP naming, root whitelist, task.toml valid
  values, decomposition fields, execution_logs structure, static checks
  S-01..S-07), common-mistakes §7, submission §8. If anything here conflicts
  with that file on packaging/delivery, that file wins — EXCEPT Production
  Rework's required `high_level_prompt.md` and three log modes, which EXTEND
  the root whitelist / log set for this wave.)
- D:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\documentations_phase_2\00_authority\Verifier & Rubric Manifest Standards (Effective Immediately).txt
  (BINDING scoring/manifest law from Batch-12/14. Effective immediately.
  Mandates: correct verifier_type (hybrid when mixed), complete reward.json
  with category scores + per-check notes + LLM justifications, content
  (RH+PO) share + structural ceiling (original ≥40%/≤60%; Production Rework
  SUPERSEDES to ≥60%/≤40% for this wave), held-out content checks,
  manifest↔verify.py fidelity (no misleading equal weights, no duplicate
  check_function, every reward path listed), identical verify.py for SA and
  MA, hollow-fixture discrimination. QG enforces via S-08 and QD-03 checks
  7–8; violations of content-share or manifest accuracy are AUTO-REJECT.
  SUPERSEDES older "no weighting / always executable for hybrid graders"
  wording. Re-read before Gate 3; apply P21-5 / P21-13 share numbers.)
- D:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\documentations_phase_2\02_onboarding\All -Hands - Verifier & Rubric Manifest Standards [MANDATORY] - 2026_08_04 20_29 IST - Notes by Gemini.txt
  (All-Hands briefing for the Verifier Standards announcement — Mathavan +
  Ruturaj, 2026-08-04. Companion to the authority file above (announcement
  WINS on conflict). Extra operational rules distilled into P21-12: classify
  copy-from-input as static not RH/PO; simple additive/1-2-3 scoring only
  (opaque −0.25 whole-score gates → reject); print every check + LLM
  score/justification into test-stdout; hollow fixtures must score low;
  optional MA-first search-space then hand-verify partial oracle. Meeting
  taught content ≥40%; Production Rework later raises to ≥60% for the
  rework wave — do not treat the transcript's 40% as the current delivery
  floor.)
- D:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\documentations_phase_2\02_onboarding\MAS__Turing - Kimi-Cli-Limitation.txt
  (WHY we run on OpenCode not Kimi-CLI: Kimi-CLI caps -- DAG depth 1 (role
  guard), 4 concurrent background agents, invisible background trajectories,
  15-min background timeout, browsing quirks (FetchURL strips JSON structure;
  SearchWeb disabled without a Moonshot key; JSON APIs need Shell(curl)), no
  native media tool. Design to OpenCode's capabilities, not Kimi's limits.)
- D:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\documentations_phase_2\02_onboarding\Onboarding for MAS 2.0 - 2026_07_20 17_52 IST - Notes by Gemini.txt
  and D:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\documentations_phase_2\02_onboarding\MAS_2.0_Trainer_Onboarding_Expanded.txt  (the 2026-07-20 Phase 2.1
  onboarding call + expanded notes: three-dimension verifiers, partial
  oracles, rubric_manifest.json, verify.py standardisation, /logs/agent
  output path, modular LLM judging, source novelty,
  metadata-after-runs, and the EVAL-data difficulty recalibration -- SA very
  low AND MA also challenged. NOTE: older "no rubric weightage" lines in these
  notes are SUPERSEDED by Verifier Standards + Production Rework content share
  / honest-manifest rules — category 1/2/3 + multiplicative content signal
  are now the preferred default.)
- D:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\documentations_phase_2\02_onboarding\phase2_meeting_presentation_brief.ipynb
  (the Phase 2 standards deck: mandatory baseline, the four optional
  classes, what strong Phase 2 tasks look like, what to avoid,
  instruction.md guidance, decomposition guidance, verifier/rubric
  guidance, the Phase 1 rejection-risk list, pilot expectations)
- D:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\documentations_phase_2\02_onboarding\MAS2 - Onboarding call - 2026_06_25 16_27 EEST - Notes by Gemini.txt
  (THE INITIAL Phase 2 ONBOARDING / REQUIREMENTS call -- read it as the
  baseline definition of what a Phase 2 task IS before Gate 0. It sets:
    * the mission: 50 high-quality tasks -> 1k extension; poor / Phase-1-like
      tasks risk cancellation, so quality is non-negotiable;
    * long-horizon, multi-stage, hierarchical DAG (real coordination, not a
      flat fan-out / map-reduce);
    * human-readable instruction.md -- no AI-generated style, no over-
      explaining, no step-listing that leaks the solving strategy;
    * ORACLE is replaced by rubric-based evaluation tied to the instructions;
    * a REAL gap only (single agent must struggle NATURALLY from breadth +
      coordination -- never engineered);
    * mandatory browsing / external retrieval (no local-file-only tasks) and
      long-writing outputs (100k-200k tokens), plus creative-visualization
      outputs (slides / charts / dashboards / video);
    * the two demo shapes: 120 counties / 10 states browsing, and the
      34-chapter book summarization + reducer;
    * PROHIBITED: local file reading, synthetic data, SA-only restriction,
      information asymmetry, reward hacking, decomposition leakage (no oracle
      in the YAML), token throttling, and complex formulas / caps / floors /
      ceilings in the reward;
    * process discipline: rerun logs after ANY instruction.md change,
      UUID `domain/task` folder format, partial credit is allowed, 7h/task
      budget, QA-spreadsheet PASS before build, trainer accountability for
      all AI-generated content, and contest unfair (formatting-only)
      rejections.)

Phase 2 IDEA-DESIGN + CREATIVITY references (READ BEFORE GATE 0 -- they
define HOW to shape the idea now that ideas are USER-DIRECTED -- my own
seed or a CSV row I name):
- D:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\documentations_phase_2\03_design_guides\MAS2 Initial 50 Tasks Tracker - llm_generated_prompts (1).csv
  (a METHODOLOGY / PATTERN reference ONLY -- NOT an idea bank to pick from.
  Do NOT pick, claim, copy, or auto-run a picker over it. Study a few rows
  to LEARN how the team leads design tasks: how a query maps to a
  multi-node DAG, how they set DAG depth and width, how they stage a
  multi-stage workflow, how they scale/expand the corpus, and how the
  columns (query, real_sources_or_entities, expected_outputs,
  why_multi_agent, expected_single_agent_failure, hardness_strategy /
  corpus-expansion steps, grader_rationale, verification_shape,
  novelty_rationale) hang together. Then set the sheet aside and apply
  that METHOD to a UNIQUE idea of my own. The columns also show the
  reference FORMAT for the Gate 0 QA spreadsheet row. Every task I build
  must stay distinct from every sheet row -- a similarity check runs on
  each task.)
- D:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\documentations_phase_2\04_domains\planning_operations\Thinking in Planning-Operations — Ideas for Designing Real Tasks.txt
  (THE primary idea-generation guide: "many decisions x many constraints"
  as the source of the single-vs-multi gap; what "constraints" and
  "decisions" really mean; the wide canvas of industries; the three
  structural single-agent failures (constraints fade, late decisions go
  generic, cross-unit reasoning collapses); the feel-check for a good
  task; cross-domain sparks; and how to start from a blank page. Use this
  to SHAPE and PRESSURE-TEST the user's idea before Gate 0.)
  (NOTE: `planning_ops_doc.txt` is a byte-identical duplicate archived at
  `PHASE_2/documentations_phase_2/_archive/duplicates/planning_ops_doc.txt` --
  read the Thinking-in-PO file above, not both.)
- D:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\documentations_phase_2\02_onboarding\LLM_gennerated_tasks_guidelines_video_transcript.md
  (the delivery-manager KT video transcript: the creativity gate must be
  claimed + QA-approved BEFORE task-file creation; complexity must live in
  the DECOMPOSITION/coordination pattern, not in model-intelligence
  puzzles; persona is a first-class creativity lever; read any seed idea
  as a real-world operator, understand persona/keywords/end-goal, then
  BUILD ON TOP of it -- never paste a seed into instruction.md; embed the
  rules/regulations that break the single agent into the prompt itself
  since there is no oracle. This describes the CSV-seed flow -- but the
  idea now is always MY OWN ORIGINAL idea, never picked/copied from the
  sheet; the sheet is only for learning the leads' design method. Keep
  every creativity/coordination lesson here and apply it to my own idea.)
- The 2026-07-01 all-hands notes (`All_Hands_Meta_Multi_Agent_Swarm - ... -
  Notes by Gemini.txt`) now live under "Phase 2 RUBRIC-DESIGN references"
  below, because they are primarily the RUBRIC-CREATION + gap call. The
  CREATIVITY takeaway to carry into Gate 0/1: make the task complex in
  COORDINATION, not model-intelligence (no simple bug-fix / puzzle tasks) --
  ask "is my decomposition.yaml genuinely complex?" -- and do NOT repeat
  Phase-1 patterns (e.g. paper-DB Q&A over a GitHub list).

Phase 2 QUALITY + REVIEW references (the bar the Draft Review / Quality
Gate grades against -- build to pass these):
- D:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\documentations_phase_2\01_quality_gate\Quality_dimensions_phase_2.md
  (the Phase-2 reviewer Quality Dimensions in one file:
  instruction completeness/authenticity, domain/persona/artifact match,
  rubric/verifier soundness, the LLM-judge infra-failure rule (updated by the
  2026-08-11 verifier template: failed judge checks score 0.0 but must be loud
  in stdout / justification / debug files), AHT
  justification -- the single source of truth for the local + upstream
  review. This SUPERSEDES the Phase-1 QD-01..QD-14 for Phase 2 tasks.)
- D:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\documentations_phase_2\01_quality_gate\LocalQualityGate_ReviewerPrompt_Phase2.md
  (the Phase-2 successor to the Phase-1 Local Quality Gate: spawns 4
  sub-agents across QD-01..QD-09 from Quality_dimensions_phase_2.md, no
  oracle/solution expected -- paste into a FRESH session at Phase 4.5.
  Use THIS, not the Phase-1 LocalQualityGate_ReviewerPrompt.md, for
  Phase 2 tasks.)

Phase 2 RUBRIC-DESIGN references (the dedicated rubric doc + the rubric-
creation call -- MANDATORY reads BEFORE you write ANY rubric, judge.py, or
verify.py checklist at Gate 3 / Phase 2):
- D:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\documentations_phase_2\03_design_guides\rubric_scale_presentation.pdf
  (the "the whole game is the rubric" deck: five real tasks dissected for
  WHY the single-vs-multi gap collapsed and how to fix it. The five lessons
  are the core of difficulty design: (1) grade CORRECTNESS not PRESENCE --
  checking a file exists is fakeable by any agent; grade the values against
  a reference (Sovereign: gap +4.6 -> ~+25). (2) FEWER easy "is it present"
  checks, MORE hard checks that require the correct reconciliation/analysis,
  so passing means doing the work (Drug Shortage: gap -10 -> ~+25). (3) ADD
  points, never MULTIPLY, and never derive the answer key from the agent's
  own output (NYC Restaurant: gap -48 -> ~+25). (4) if the rubric is good but
  the gap is small, it is a SIZE problem -- scale the work up (200+ units)
  until one agent runs out of budget (Capital Ledger: gap +2 -> ~+25).
  (5) grade "like a tough professor" across many hard pieces at genuine
  scale = what good looks like (Finance Slides: single 0.53, team 0.85).
  SHIP TEST: if an agent could pass just by producing the files in the right
  format, the rubric is too weak; if a single agent ever beats the team, the
  rubric is UNFAIR -- fix that first.)
- D:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\documentations_phase_2\02_onboarding\All_Hands_Meta_Multi_Agent_Swarm - 2026_07_01 20_59 IST - Notes by Gemini.txt
  (THE "how to create rubrics + achieve the gap" call -- the same five cases
  as the deck above, in the leads' own words, PLUS the operational detail the
  deck omits:
    (a) rubrics must verify CONTENT VALIDITY / data integrity, NEVER mere file
        existence (file-existence checks are reward hacking and are the #1
        cause of SA scoring ~0.90);
    (b) WEIGHTAGE / multiplier rubrics are strictly PROHIBITED -- additive
        point-per-check only (a weightage rubric earns the trainer a warning);
    (c) if the rubric is already robust but the gap persists, the CORPUS /
        task SIZE is the problem -> add sub-task layers in decomposition.yaml
        and SCALE the corpus, don't add more checks;
    (d) DEBUG BOTH single and multi trajectories -- read the logs + output
        files, never trust the score blindly -- BEFORE abandoning a task;
        skipping this is why trainers waste hours in a rerun loop;
    (e) apply every check EQUALLY to both agents (no unfair, SA-only checks);
    (f) browsing rubrics use a HYBRID "relevant-URL-hit" check, never hardcoded
        URLs; OpenCode supports both predefined-URL and natural-language-query
        browsing;
    (g) EMBED detailed format/quality requirements (document format, color
        codes, chapter coverage, depth-of-search) into the task input/sources
        so a rushed agent cannot pass with nonsense output;
    (h) REFERENCE-ANSWER TECHNIQUE for building a complex rubric with NO oracle:
        run the MULTI-AGENT first, cross-verify a RANDOM SAMPLE of its outputs
        against the real sources, use those validated values as test cases,
        then re-run BOTH single and multi (never blindly trust the MA output --
        you must be able to justify each value to the client).
  Consult this at Gate 3 (writing the rubric) and during the Phase 6 gap loop
  (fixing a small gap).)

Phase 2 CLIENT-FEEDBACK / REJECTION-PATTERN references (read to internalize
what gets rejected; mine them for LESSONS):
- D:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\documentations_phase_2\05_feedback\batches\MAS_Client_Feedback_Document_2026-07-17.txt
  (the full client feedback log -- the concrete reasons real tasks were
  rejected; the definitive "what not to do" corpus.)
- D:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\documentations_phase_2\02_onboarding\MAS - All Hands Call.txt
  (the client's four target orchestration shapes -- WildSearch, Batch
  Download, WideRead, Long-Form Writing -- and why "read N files -> emit
  JSON, same pattern twice" undersells multi-agent capability. Use to keep
  the coordination genuinely varied.)
- D:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\documentations_phase_2\_archive\outdated_phase1_era\AgentSwarmBench - Common Issues Report.txt,
  D:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\documentations_phase_2\05_feedback\LLM_Review_Issues.txt (the LLM-reviewer
  issue log), and D:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\documentations_phase_2\05_feedback\Feedbacks.txt
  (the human-reviewer rework log) -- the running feedback streams. Consult
  these AND the LESSONS LOG (below) before each new build; fold every
  recurring issue into the LESSONS LOG (STANDING DUTY 0 / requirement).
- D:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\documentations_phase_2\09_qg_reviews\raw_reports\  (FOLDER -- the actual
  Quality-Gate reports from the LLM QG reviewer, one file per task/decision,
  named `QG Report — <task-id> — <APPROVE|REJECT|MANUAL_REVIEW>.txt`. This is
  the GROUND TRUTH of what the automated gate accepts and rejects, and it
  GROWS OVER TIME -- new files are dropped in continuously. MANDATORY: at the
  START of every build, LIST and READ EVERY file currently in this folder
  (do not rely on a cached summary -- always re-read so newly added reports
  are picked up). For each REJECT / MANUAL_REVIEW, read the "Rejection
  Reasons" block at the bottom (check id, evidence, required rule, fix) and
  design so the SAME check passes this time; for each APPROVE, treat it as a
  worked template of what passes. Distil every new REJECT reason into the QG
  REVIEWER REJECTION LEDGER + LESSONS LOG (below). The distilled, always-check
  summary of the reports seen so far lives in the QG REVIEWER REJECTION LEDGER
  near the end of this file -- read it, but ALSO re-read the folder for
  anything newer.)

Still-binding Phase 1 references (the DISCIPLINE carries over; the SCORING
and QUALITY dimensions do NOT — for those, use the Phase 2 docs above):
- D:\Abisheik\Projects\swarmbench\Tasks\_archive\duplicate_docs_root\[Harbor] Multi-Agent Swarm
  Benchmark — Trainer Guidelines -V3.txt   (the PHASE 1 guidelines, v3 of the
  Phase-1 line — SUPERSEDED by the Phase 2 v1.0 guidelines above. Use ONLY
  for still-generic instruction.md rules, decomposition rules, false-failure
  Section 5.6, and time management. Do NOT take SCORING from it: it is
  oracle/golden-answer based, which Phase 2 forbids.)
- D:\Abisheik\Projects\swarmbench\Tasks\_archive\cleanup_2026-08-05\workspace_root_clutter\Quality_dimensions  (QD-01 ..
  QD-13) and D:\Abisheik\Projects\swarmbench\Tasks\skills\ (QD-01 ..
  QD-14, the upstream reviewer's skill files) — the PHASE 1 Quality
  Dimensions, SUPERSEDED for Phase 2 by `Quality_dimensions_phase_2.md`
  (QD-01..QD-09) above. Consult only as background; NEVER audit a Phase 2
  task against the Phase-1 QD list — the Phase 2 QD file is the sole bar.
- D:\Abisheik\Projects\swarmbench\Tasks\_archive\cleanup_2026-08-05\workspace_root_clutter\LocalQualityGate_ReviewerPrompt.md
  (the PHASE 1 Local Quality Gate prompt + Windows path mapping) —
  SUPERSEDED for Phase 2 by `LocalQualityGate_ReviewerPrompt_Phase2.md`
  above; use the Phase 2 gate for any Phase 2 self-review at Phase 4.5.
- D:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\documentations_phase_2\_archive\outdated_phase1_era\AgentSwarmBench - Common Issues Report.txt
  and D:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\documentations_phase_2\05_feedback\LLM_Review_Issues.txt
  (esp. 3.1 schema drift, 3.4 answer leakage, 3.6 process-cap reward
  hacking, 3.8/S-07 instruction/log sync, 3.10 log tampering, 3.11
  Dockerfile leakage, 3.12 mode-dependent scoring, 3.13 score >1.0)
- D:\Abisheik\Projects\swarmbench\Tasks\MAS - LT Similarity Checker.txt
  (the similarity checker scores the SWARM TRAJECTORY, not the domain;
  governs GATE 1(C) distinctness and PHASE 4.6)
- D:\Abisheik\Projects\swarmbench\Tasks\_archive\cleanup_2026-08-05\workspace_root_clutter\PlanningOperations_TaskCreationPrompt.md
  (the Phase 1 prompt -- the source of the gate/phase scaffold,
  build_task.py tooling discipline, sanity-gate catalogue, and the
  baked-in lessons; reuse its MACHINERY, replace its oracle-centric
  core)

EXAMPLE-TASK DISCIPLINE:
- Phase 2.1 packaging exemplars: `PHASE_2\documentations_phase_2\08_samples\`
  (`phase_2_1/`, `praised/`, `approved/` -- study structure; never copy
  instruction text). Live Phase 2 working packages live under
  `PHASE_2\phase_2_tasks\{planning_operations,knowledge_research}\` (see
  that folder's README.md).
- The blessed Phase 1 planning-operations exemplars are in
  D:\Abisheik\Projects\swarmbench\Tasks\planning_resource_domain_examples\.
  Study them for source-pack shape, provenance manifest layout, evidence
  rules, and scoring weights -- BUT note they are Phase 1 (oracle-heavy,
  often local-file). For Phase 2, keep their realism + provenance bar and
  REPLACE their oracle-centric, flat structure with rubric-based,
  browsing, hierarchical design.
- Do NOT use Phase 1 in-progress builds under
  D:\Abisheik\Projects\swarmbench\Tasks\Tasks\planning_and_resource_tasks\
  as structural templates (some are mid-iteration / unapproved). They are
  a source of LESSONS only.
- Estifanos' two Phase-2 demo tasks (the 120-county / 10-state browsing
  spreadsheet task; the ~1,000-page / 34-chapter book summarization +
  reducer task) are the canonical Phase 2 shapes -- request and study the
  shared demo artifacts before Gate 1 if available.

DOCUMENT-TO-STAGE MAP (which doc to open at which step -- paths are under
`PHASE_2\documentations_phase_2\` unless noted; see that folder's README.md
for the numbered catalog. Trainer Guidelines v1.1 in `00_authority/` wins
for package/delivery at EVERY stage; Verifier & Rubric Manifest Standards
in `00_authority/` wins for scoring/manifest; Production Rework Requirements
SUPERSEDES content share to ≥60%/≤40% and adds HLP + three log modes for
this wave):
  - GATE 0 (entry routing / idea / rework triage): FIRST perform the short
    ENTRY ROUTING decision before reading this full map. Then read
    `00_authority/Production Rework Requirements.txt` if any Completed→Rework
    or resubmit is in scope (prioritise rework; do not block the SCRATCH
    route solely because no seed was supplied). Then
    `02_onboarding/MAS2 - Onboarding call ... .txt` (INITIAL Phase 2
    requirements baseline), then
    `04_domains/planning_operations/Thinking in Planning-Operations —
    Ideas...txt`, `02_onboarding/LLM_gennerated_tasks_guidelines_video_transcript.md`,
    the tracker CSV in `03_design_guides/` (METHOD only, never an idea source),
    and `02_onboarding/MAS - All Hands Call.txt` (the four client shapes) to
    keep the coordination varied.
  - GATE 1 (scenario / class / distinctness): `02_onboarding/phase2_meeting_
    presentation_brief.ipynb`; `MAS - LT Similarity Checker.txt` (workspace
    root) for the distinctness bar.
  - GATE 2 (sources): the passed-samples browsing lessons (`08_samples/`) +
    the guidelines' CR-01 (load-bearing, reproducible browsing).
  - GATE 3 + PHASE 2 (RUBRIC + verifier): FIRST read
    `00_authority/Production Rework Requirements.txt` §4 (content ≥60% /
    structural ≤40% / multiplicative content signal / ≥3–5 content rubrics)
    AND `00_authority/Verifier & Rubric Manifest Standards (Effective Immediately).txt`
    (hybrid type, manifest fidelity, held-out checks, hollow fixtures), THEN
    the All-Hands briefing
    `02_onboarding/All -Hands - Verifier & Rubric Manifest Standards [MANDATORY] - 2026_08_04 20_29 IST - Notes by Gemini.txt`
    (print→test-stdout, simple scoring, classify copy-from-input as static),
    THEN `03_design_guides/rubric_scale_presentation.pdf` (MANDATORY craft), then
    `02_onboarding/All_Hands_Meta_Multi_Agent_Swarm ... .txt` (content-validity
    checks, embed requirements in inputs, hybrid URL-hit browsing checks),
    QD-03 in `01_quality_gate/Quality_dimensions_phase_2.md`, and
    `03_design_guides/new_verifier_reward_system.md` (1/2/3 category worked
    rationale — use with Production Rework's 60% content floor). When any
    check needs LLM (esp. charts/images), also open
    `03_design_guides/verifier_templates/WANDB_Qwen_Vision_Verifier_Template/`
    (W&B call shape; no temperature).
  - GATE 4 (decomposition): the guidelines' decomposition rules + QD-06.
  - PHASE 3 (build / task.toml / high_level_prompt.md): the guidelines' §6
    delivery format + P21-13 HLP rules (~250 words, deliverables only).
  - PHASE 4 (QD self-audit): `01_quality_gate/Quality_dimensions_phase_2.md`
    (QD-01..QD-09; include QD-03 checks 7–8 for manifest/content share ≥60%).
  - PHASE 4.5 (quality gate): `01_quality_gate/LocalQualityGate_ReviewerPrompt_
    Phase2.md` + the static checks S-01..S-08; `_archive/outdated_phase1_era/
    AgentSwarmBench - Common Issues Report.txt` + `05_feedback/LLM_Review_
    Issues.txt` for known failure modes; and the `09_qg_reviews/raw_reports/`
    folder + the QG REVIEWER REJECTION LEDGER -- verify your task would pass
    every check that a prior report REJECTED on. Production rework:
    LLM QG report is MANDATORY with resubmission (P-RW-6).
  - PHASE 4.6 (similarity): `MAS - LT Similarity Checker.txt` (workspace root).
  - PHASE 5–6 (package + three-mode runs): P21-13 — force-reinstall mascloud;
    run single + multi + multi_noplan; merge three log trees; keep three ZIPs;
    ≥20pp SA–planned-multi gap.
  - PHASE 6 (gap / dual-debug): `03_design_guides/rubric_scale_presentation.pdf`
    (the gap fixes) + `02_onboarding/All_Hands_Meta_Multi_Agent_Swarm ... .txt`
    (debug BOTH trajectories before abandoning; scale the corpus if the rubric
    is already strong; reference-answer technique when there is no oracle) +
    `05_feedback/batches/MAS_Client_Feedback_Document_2026-07-17.txt` (why real
    tasks were rejected).
  - CONTINUOUS (lessons capture/reuse): `05_feedback/Feedbacks.txt` (human-
    reviewer rework), `05_feedback/LLM_Review_Issues.txt` (LLM reviewer),
    `05_feedback/batches/MAS_Client_Feedback_Document_2026-07-17.txt`, the
    `09_qg_reviews/raw_reports/` folder (re-read EVERY file each build -- it
    grows over time), the QG REVIEWER REJECTION LEDGER, and the LESSONS LOG
    (BUILD -> SHIP) below -- read before each build, append to during/after
    each build.

After reading, write a one-paragraph confirmation into HANDOFF.md (and
echo once in chat) restating: (a) the nine Phase-1->Phase-2 shifts and
which ones your candidate exercises (including that the idea is MY OWN
ORIGINAL idea -- restate it in your own words, confirm it is not picked
from the sheet and is unique vs existing tasks -- and the chosen domain,
planning-operations unless I approved a fallback), (b) which optional
Phase 2 class(es)
you will use, (c) how the gap will arise NATURALLY (the named single-
agent failure), (d) the realism/provenance invariants you will keep
(real public sources, real entities, verbatim evidence, provenance
manifest), and (e) the one coordination/decomposition element that makes
your task a genuinely different SWARM TRAJECTORY (not a dataset reskin).
Record it and PROCEED (AUTONOMY MODE).

============================================================
PHASE 2 MANDATORY BASELINE (every task must satisfy ALL of these)
============================================================
B1. LONG-HORIZON MULTI-STAGE WORKFLOW. The task naturally requires
    multiple stages (collect evidence -> verify evidence -> analyze /
    classify -> reconcile conflicts -> produce final artifact ->
    summarize risks/findings). These stages are NOT listed in
    `instruction.md`; they live in the decomposition as sub-agents and
    are discovered by the agent. `instruction.md` describes WHAT to solve
    and the goal, human-like and concise.

B2. HIERARCHICAL / SPECIALIST-ROUTING COORDINATION (MANDATORY PATTERN).
    The client requires HIERARCHICAL and SPECIALIST-ROUTING patterns and
    has explicitly RULED OUT map-reduce and fan-out/synthesis for Phase 2
    (2026-06-26 DM note). The task must benefit from different ROLES and
    LAYERS of agents (a real DAG with depth), where each agent is
    differentiated by responsibility, not just a shard of the same job.
    Use: lead/orchestrator -> domain specialists (each owns one area
    end-to-end with a consistent method) -> reconciliation/verifier ->
    assembler -> separate writer/producer roles; or manager ->
    sub-manager -> worker -> verifier -> reducer. Do NOT set
    `coordination_pattern` to `map-reduce` or `fan-out-synthesize`, and do
    NOT design "split N files across N identical workers."
    DAG DEPTH >= 2 is mandatory (CR-07): at least one sub-task consumes
    another sub-task's output before the final synthesizer (a flat star
    is dag_depth=1 and rejected). Aim for SCALE -- ~20-50+ sub-agents;
    Hard tier is dag_width >= 20. Declare dag_depth/dag_width in task.toml
    and make `estimated_sub_agents` equal the sub_tasks count.

B3. REAL-WORLD / REALISTIC DESIGN. It feels like a real work request.
    Sources are real and externally verifiable. No synthetic data, no
    sensitive data, no AI-generated-looking prompts, no artificially
    complex test cases. If live fetch is unreliable, hosted/pinned
    sources (Drive / S3 / GitHub release / public docs / public PDFs /
    frozen snapshots) are allowed.
    HOSTED-FROZEN-COPY FALLBACK (lead-approved, 2026-06-26 Estifanos): when
    a live source is bot-protected (returns a challenge/apology page
    instead of the content), drifts week to week, or has patchy Wayback
    coverage, you MAY host a frozen copy of the REAL source (a pre-
    extracted plain-text or PDF capture) on a PUBLICLY-ACCESSIBLE GitHub
    repo/release and have the agent fetch it via its URL (the `text_url`
    pattern used by initial sample 95dec0ee...). Rules: the hosted copy
    must be a faithful capture of a real public source (never fabricated
    or edited to fit), recorded in the source manifest with the original
    URL + retrieval date + sha256; the host must be public (no auth); and
    browsing stays LOAD-BEARING (the data is NOT in the local packet --
    the agent still has to fetch it). Prefer a clean official API where
    one exists (e.g. openFDA) over scraping a bot-protected portal.

B4. RUBRIC-BASED EVALUATION (15-25 BOOLEAN CHECKS, NO ORACLE). Evaluate
    against the visible requirements in `instruction.md` with a checklist
    of 15-25 boolean items; reward shape per P21-5 / Production Rework
    (prefer category 1/2/3 so content ≥ 60%; flat only if composition
    alone meets that floor; multiplicative content-quality signal OK).
    NO tiers/gap-inventing caps, NO oracle.json, NO solution/, NO
    per-check tuning. Checks are meaningful
    (real citations, claim support, required sections, internal consistency,
    per-row evidence, missing-info marking, rule adherence, held-out values).
    Grade with ONE grader, `verify.py`, covering all three Phase 2.1
    categories (static / reward-hacking / partial-oracle), mirrored 1:1 by
    `rubric_manifest.json`, with `verifier_type = "hybrid"` when LLM checks
    are mixed in. Deterministic code owns structured/exact facts; an INLINE
    LLM (a DIFFERENT family from the agent's Kimi — current provider wiring
    in `swarmbench-judge-provider.mdc`) owns only qualitative prose checks.
    No separate judge.py. Ensure the LLM does not hallucinate (concrete
    criteria; inject computed numbers; modular per-item calls; system/user
    roles + untrusted-data fence).

B5. CLEAR, NATURAL SINGLE-AGENT FAILURE MODE. SA struggles because the
    task is genuinely broad / multi-source / multi-stage / verification-
    heavy / artifact-heavy / coordination-heavy — NOT because of traps,
    hidden info, SA-only restrictions, formatting-only failures, parser
    failures, or timeout artifacts.

B6. TRAINER + QA VALIDATE THE TRUE GAP. The trainer debugs the task; QA
    independently debugs the same task. Both confirm the gap is real and
    the judge is not hallucinating. Do not blindly trust the LLM judge —
    manually inspect SA and MA outputs, the rubric, and verifier
    behavior.

============================================================
PHASE 2 CLIENT CATEGORIES (pick AT LEAST ONE; declare at Gate 1)
============================================================
The lead generalized the categories (2026-06-26 DM note) so trainers
design for the END GOAL, not a fixed output template. Use these labels
consistently; if unsure which fits, ask before finalizing. Most strong
tasks combine TWO (commonly Browsing + Long Horizon).

BROWSING. The task primarily involves searching, navigating, or
  gathering information from the web: public portals, APIs, hosted files,
  public docs/PDFs, regulatory filings, registries, procurement portals,
  source verification through links. Browsing must be LOAD-BEARING -- the
  needed facts are NOT duplicated in a local packet, so the agent has to
  fetch and read real sources and cite the exact URL. If specific URLs
  are intended, constrain the sub-agents to them in the decomposition.
  This is the main fix for "looks too much like Phase 1."

LONG WRITING. The agent generates a substantial amount of content.
  TARGET output > 100k tokens; 50k+ tokens is the MINIMUM expectation.
  Do NOT label a task "Long Writing" unless the written deliverable
  genuinely reaches that scale (a one-page memo does not). The writing
  must depend on EVIDENCE and show analysis/synthesis, not generic
  prose. Good fits: large multi-section reports, full literature
  syntheses, chapter-by-chapter study guides, book-length briefings.

MULTI-MODAL. The OUTPUT includes images, video, or audio (e.g. a
  generated slide deck with real charts, an annotated figure set, a
  narrated/audio artifact, a video walkthrough, an animation/gif).
  Charts/decks rendered as real image files count here; a plain
  spreadsheet does not. This is the category to lean into when you want
  format variety -- the team needs more presentations, charts, video, and
  animation outputs and fewer spreadsheets.

LONG HORIZON. The task spans multiple stages of a realistic workflow --
  several interconnected steps to reach the final outcome. Example: an
  ML-engineer workflow (data analysis -> data visualization -> model
  training), or collect -> verify/reconcile -> analyze -> produce ->
  summarize. This is the category for genuine multi-stage operations work
  even when no single stage is huge.

Deliverables are real artifacts (pptx / docx / md / png|svg charts / csv
/ mp4|gif / dashboards / diagrams), never JSON. DIVERSIFY: do not default
to xlsx -- too many tasks already end in a spreadsheet. Choose the format
a real operator would actually hand over, and aim for variety across your
POC tasks. A spreadsheet is allowed when the WORK genuinely calls for it,
described under whichever category fits (Browsing and/or Long Horizon).

In task.toml these map to `secondary_classification`, an ARRAY using the
EXACT lowercase-underscore enum values only: "browsing", "long_writing",
"multi_modal", "long_horizon" (NOT "Browsing", "multi-modal", "long
writing", etc.). At least one is required; most tasks list two, e.g.
`["browsing", "long_horizon"]`.

============================================================
GATE 0 -- SELECT THE ENTRY ROUTE + LOCK/PRESSURE-TEST THE BRIEF (BLOCKING -- before any build)
============================================================
Run ENTRY ROUTING first, before deep reading or research. Gate 0 is passed
only when the selected route produces an honest, pressure-tested design brief:
either a complete accepted claim parsed into a locked brief, or an original
scratch brief created under CS-S because no usable seed was supplied. A
partial/ambiguous claimed record triggers M0; genuine absence does not.

CLAIMED ROUTE -- USE THE CLAIM AS THE LOCKED BRIEF (CS-1..CS-4). The claim supplies
the persona/query, decomposition_pattern, tools, real_sources_or_entities,
expected_outputs (/logs/agent paths), why_multi_agent,
expected_single_agent_failure, verification_shape, the full test_design
blueprint, hardness_strategy, aht_estimate_arithmetic,
expected_subagent_count, similarity_score, and the accept decision. Parse
each field per CS-1; you will FILL the NA deliverable fields per CS-2.

UNIQUENESS is pre-scored only in the accepted claimed route
(`similarity_score` + `decision: accept`). Treat GATE 1(C) / M3 as
pre-satisfied there unless the final instruction.md materially drifts. In the
scratch route, run the normal similarity check before expensive runs.

DOMAIN: normalize the claim's `task_domain` to the exact task.toml enum
(e.g. "PLANNING-OPERATION" -> `planning-operations`). Keep the claim's
domain; do not switch domains unless the claim itself is mis-domained (rare
-- escalate rather than silently re-domain).

PRESSURE-TEST THE CLAIMED SPEC (claimed route only; read the IDEA-DESIGN references --
`Thinking in Planning-Operations`, the KT video transcript, the all-hands
notes -- to UNDERSTAND the spec, not to invent a new one):
  - Read the query as the real-world OPERATOR would: persona, their Tuesday,
    the end goal. Lightly rewrite it into instruction.md as a first-person
    human prompt (no Markdown headings, no stage-listing, no decomposition
    leak); do NOT paste it verbatim if it reads AI-generated.
  - Confirm the "many decisions x many constraints" engine is really there
    (the claim's hardness_strategy should name it). If the claim's stated
    single-agent failure is not actually forced by the design, the task is
    too easy -- deepen it (more units, tighter budget, harder substance
    checks) before building.
  - Confirm the coordination has genuine DEPTH (dag_depth >= 2): the claimed
    decomposition_pattern must map to a real multi-tier DAG (e.g. bracket
    round1 -> round2 -> ... -> reducer), not a flat star.
  - Confirm the sub-class(es): which of Browsing / Long Writing / Multi-Modal
    / Long Horizon the claim implies (from tools, sources, outputs), and pick
    the deliverable format the claim's expected_outputs already fix.
  - Restate, in writing, the concrete single-agent failure the design forces
    (constraints fade past ~decision 10; late decisions go generic;
    cross-unit reasoning collapses) -- that named failure IS the gap.

CLAIMED-ROUTE PROCEDURE (AUTONOMY MODE -- the claim is the up-front approval):
  1. CONFIRM the `mascloud` CLI is installed + logged in (MANUAL-NEED M1 if
     not). Confirm the task folder will follow the exact official name
     format, with SLUG derived from the claim's decomposition_pattern
     (specialist_routing -> SPECIALIST, hierarchical -> HIERARCHICAL, etc.).
  2. PARSE THE CLAIM into the locked brief (CS-1): scenario, sources,
     output paths, coordination, tools, verifier blueprint, AHT. Record the
     parsed brief in HANDOFF.md + NOTES.md.
  3. RECONCILE the test_design blueprint to the hard scoring rules (CS-3):
     convert any "fail-closed structural precondition" into an ADDITIVE
     one-point static check; treat any full "immutable ground-truth fixture"
     as a grader-only PARTIAL-oracle sample + reward-hacking cross-reference,
     never a whole-answer exact-match gate; weight:1 everywhere.
  4. SANITY-CHECK the claim (CS-4): reconcile inconsistent counts
     (estimated_sub_agents == decomposition sub_tasks; dag_depth/dag_width
     from the OBSERVED spawn tree after runs), verify every claimed source is
     fetchable, and confirm the task can be built HONESTLY. If not, ESCALATE
     with specifics rather than forcing/fabricating.
  5. PROCEED to Gate 1. (No separate QA "pass"/"revise" loop is needed for
     the accepted brief. Escalate only on a genuine buildability blocker.)

SCRATCH-ROUTE PROCEDURE (no usable claim/seed was supplied):
  1. Confirm the `mascloud` CLI is installed + logged in (MANUAL-NEED M1 if
     not). Do not invent a task UUID; obtain the required labeling-tool UUID
     and link before packaging/submission.
  2. Create and record the CS-S design brief in trainer-only HANDOFF.md and
     NOTES.md, including `authoring_mode: scratch` and the absent-input
     reason. Generate 3-4 candidate framings, reject weak/similar ones, and
     lock the strongest original real-world scenario.
  3. Assemble and validate real, load-bearing sources; define exact agent
     output paths, a genuine hierarchical coordination shape, the natural
     single-agent failure, and a verifier/test blueprint. Reconcile that
     blueprint under CS-2 and CS-3 before building.
  4. Pressure-test buildability, source fetchability, real depth, and the
     natural gap exactly as strictly as a claimed brief. Never use synthetic
     entities/data or a scoring trick to make the route succeed.
  5. PROCEED to Gate 1 and complete the normal similarity check before any
     expensive run. Record its result; only an actual accepted claim may
     pre-satisfy that check.

Record the selected route, final brief, reconciliation notes, and any
similarity result in HANDOFF.md and NOTES.md.

============================================================
GATE 1 -- LOCK SCENARIO + CLASS + DISTINCTNESS
============================================================
For the scratch route, root every candidate in MY OWN ORIGINAL IDEA (Gate 0),
never a picked or copied sheet row. For the claimed route, preserve the
accepted scenario unless a buildability defect requires escalation. Develop
3-4 candidate FRAMINGS only when the scratch brief calls for them; vary the
high-value axes -- scale, the constraint mix, the deliverable/sub-class, or
the coordination shape -- rather than jumping to unrelated industries; each
must be a genuine, distinct, UNIQUE planning-operations task (or, only
where I approved a domain fallback, a task in the chosen fallback domain)
that is not similar to a sheet row, an approved sample, or another task.
(Only if my idea is deliberately open-ended -- e.g. "pick a good healthcare
ops task" -- may the candidates span different sub-verticals; the industry
list below is then a menu: crisis/incident, healthcare, engineering/SRE,
logistics/supply chain, construction, retail, events/broadcasting,
education, NGO/humanitarian, finance ops, manufacturing, government/
public sector, open-source repo ops, market/competitor research, etc.)
For each candidate fill in:

  Field                         | What it must contain
  ------------------------------|----------------------------------------
  scenario_short_name           | snake_case, <= 40 chars
  industry / sub-vertical       | e.g. emergency-procurement-research
  operator persona              | who would do this on a Tuesday
  real-world objective          | the human work request (1-2 sentences)
  client_category(ies)          | >= 1 of Browsing / Long Writing /
                                | Multi-Modal / Long Horizon (most tasks
                                | combine Browsing + Long Horizon)
  external sources / browsing   | the REAL public sources the agent will
                                | fetch/verify (URLs, portals, APIs, repos,
                                | PDFs). State whether live-fetched or
                                | frozen, and why. Every source must be
                                | real, public, and authoritative.
  multi-stage workflow          | the natural stages (collect -> verify ->
                                | analyze -> reconcile -> produce ->
                                | summarize). 4+ stages expected. (These
                                | go in the decomposition, NOT instruction.)
  final artifact(s)             | the deliverable(s) per chosen class
                                | (report / deck / xlsx / structured doc)
  predicted SA failure (natural)| WHY a single agent struggles: breadth /
                                | multi-source / multi-stage / verification
                                | load / artifact size / coordination. Name
                                | the concrete failure (e.g. "loses source
                                | coverage past ~county 40 and starts
                                | guessing values").
  predicted MA advantage        | which roles/layers recover it
  rubric plan                   | the meaningful checks (real citations,
                                | claim support, sections present, per-row
                                | evidence, consistency, missing-info
                                | marking). No trivial constraints.
  reward-hacking risk           | what shortcut would let SA score high
                                | without doing the work, and how the
                                | rubric blocks it WITHOUT a gate/cap
  distinctness_vs_prior         | per (C) below

Hard rules for the candidates:
  - When candidates are framings of MY seed they share its vertical (that
    is expected) but MUST differ on a high-value axis (scale, constraint
    mix, deliverable/sub-class, or coordination shape) -- never the same
    task twice. Only when my seed is open-ended should no two candidates
    share an industry vertical.
  - Every candidate MUST require browsing/external retrieval OR a
    genuinely external-grounded artifact; pure local-file reading is
    rejected here.
  - Every candidate MUST be a long-horizon multi-stage workflow that
    benefits from hierarchical/specialist coordination — not a flat
    fan-out and not "read N docs, emit JSON".
  - All sources must be REAL, public, and authoritative. No synthetic
    data, no sensitive data, no fictional entities, no paywalled-only
    sources.
  - The deliverable must be a real artifact of the chosen class (a PLAN /
    report / deck / sheet), not a survey extraction.

(C) DISTINCTNESS -- DIFFERENT SWARM TRAJECTORY, NOT A NEW DATASET
(MANDATORY; read `MAS - LT Similarity Checker.txt` first). The biggest
rejection risk is building a task whose SWARM BEHAVIOUR duplicates an
existing task. The checker and the client score the trajectory
(decomposition / coordination / delegation / synthesis / verification /
failure modes), not the topic. Swapping only the domain/dataset/persona
will be REJECTED and can devalue your prior tasks. For each candidate
state: (1) the closest existing task's one-line skeleton, (2) this
candidate's one-line skeleton, (3) the ONE high-value axis on which the
swarm trajectory materially differs (e.g. cross-document contradiction
reconciliation, dependency-graph construction, global-compute-before-
unit, multimodal perception, multi-step simulation/feedback, generate-
and-execute, a deep reducer over hundreds of artifacts). If you cannot
name a structural difference, it is a reskin -- redesign before locking.

Pick the strongest candidate yourself (clearest NATURAL SA failure,
strongest distinctness, most-real browsable sources, cleanest rubric,
within AHT). Record the pick + why the others lost in HANDOFF.md + NOTES
DECISION LOG, then proceed (AUTONOMY MODE).

============================================================
GATE 2 -- LOCK SOURCES + MULTI-STAGE WORKFLOW
============================================================
For the picked scenario, lock the source plan and the stage graph (into
`_trainer_artefacts/draft/`, not the task folder yet):

  A. SOURCE PLAN. A table of every external source the agent will
     browse/verify (or that you will freeze):
       - source_id, url/portal/endpoint, publisher, retrieval mode
         (live-browse / API / frozen-snapshot), retrieval date
       - what stage(s) consume it
       - whether it is authoritative and stable
     Rules:
       - REAL-SOURCE FRACTION: ~100% real public sources is the target.
       - If live fetch is unreliable, freeze a dated snapshot under
         `environment/input_artifacts/snapshots/` (byte-frozen, hashed in
         sha256sums.txt) and record the exact request/URL + timestamp so
         it is reproducible. Frozen snapshots are still REAL data.
       - When browsing is intended, the agent PRESERVES what it fetched
         to `/logs/agent/source_archive/` so the rubric can verify the
         evidence chain (path-exists + min-bytes + URL-syntax + claim-
         support checks).
       - Never backfill a failed fetch with invented data (INTEGRITY
         MANDATE).

  B. MULTI-STAGE WORKFLOW GRAPH. The DAG of stages the task naturally
     requires (collect -> verify -> analyze/classify -> reconcile ->
     produce artifact -> summarize). For each stage: input, output,
     which sources/roles it touches, and how it feeds the next stage.
     Confirm at least one stage requires CROSS-SOURCE work (verification,
     reconciliation, or synthesis) that a single pass would degrade on.
     These stages live ONLY in the decomposition (Gate 4) and the rubric
     (Gate 3) — NOT in `instruction.md`.

  C. ENVIRONMENT RULES MODULE. List the hard rules/constraints the agent
     must follow (output format, evidence requirements, source
     constraints, quality bar). Ship these as a rules markdown file inside
     `environment/input_artifacts/` (e.g.
     `input_artifacts/<name>_rules.md`) — the official structure has NO
     `environment/rules/` folder; binding rule docs live in input_artifacts/
     (as in the EMERGPROCUREMENT sample). Keep them OUT of `instruction.md`
     (which stays human and references them as `/input_artifacts/...`).

Record the locked source plan + stage graph + rules module in HANDOFF.md
+ NOTES DECISION LOG, then proceed (AUTONOMY MODE).

============================================================
GATE 3 -- RUBRIC + ARTIFACT/OUTPUT DESIGN (NO oracle)
============================================================
Design the deliverable schema and the SCORING RUBRIC before writing any
verifier code. The rubric REPLACES the oracle entirely — there is no
oracle.json and no solution/ folder in Phase 2.

  ARTIFACT/OUTPUT CONTRACT. Define the exact deliverable(s) for the
  chosen class and ONE unambiguous output path:
    - C-SHEET: `output.xlsx` (or csv) with named sheets/columns; each row
      carries evidence (source_id + locator + supporting_excerpt) and
      flags/notes; a header/meta block naming sources used.
    - C-R4: a structured long-form document (sections, headings) written
      to the stated output path; every substantive claim cites a real
      source; a references section resolves every citation.
    - C-R7: the visual artifact (deck/chart/dashboard file) PLUS the
      underlying evidence-backed data and a short written rationale so
      the rubric can check the viz communicates the real findings.
    - C-BROWSE: a source ledger / evidence file plus the analysis
      artifact; every ledger row resolves to a preserved fetched source.
  Keep keys/sheets/sections EXHAUSTIVE and stated crisply in
  `instruction.md`'s output block; push the long rules into a rules file in
  `environment/input_artifacts/`.

  RUBRIC DOC FIRST (MANDATORY). Before writing a single rubric item or any
  `verify.py` check (Phase 2.1: the single grader), RE-READ THESE sources in
  order: (0) `00_authority/Production Rework Requirements.txt` §4 +
  `00_authority/Verifier & Rubric Manifest Standards (Effective
  Immediately).txt` (binding: hybrid type, content≥60%/structural≤40% for
  this wave, manifest fidelity, held-out checks, hollow fixtures); (1)
  `PHASE_2\documentations_phase_2\
  03_design_guides\rubric_scale_presentation.pdf` (the dedicated rubric doc
  -- apply its five lessons); and (2) `PHASE_2\documentations_phase_2\
  02_onboarding\All_Hands_Meta_Multi_Agent_Swarm - ... - Notes by
  Gemini.txt` (content-validity over existence, additive checks applied
  equally to both agents, embed requirements into the inputs, hybrid
  relevant-URL-hit browsing checks — note: older "NO weightage" lines there
  are SUPERSEDED by Verifier Standards + Production Rework). A rubric that only checks
  presence/format is the #1 reason SA scores >= 0.90 -- the grader is what
  decides whether the gap exists at all ("the whole game is the rubric").

  REFERENCE-ANSWER TECHNIQUE (when the task has NO oracle -- the All-Hands
  method): run the MULTI-AGENT first, cross-verify a RANDOM SAMPLE (e.g.
  10-20) of its outputs against the real sources, then use those VALIDATED
  values as the rubric's test cases; re-run BOTH single and multi afterward.
  Never trust the MA output blindly -- you must be able to justify every graded
  value to the client.

  DESIGN A DISCRIMINATIVE, GRANULAR RUBRIC (this is what creates the gap):
    - GRADE CORRECTNESS, NOT PRESENCE. Each item checks the VALUES / analysis
      are RIGHT against a real reference, not merely that a file or section
      exists.
    - GRANULAR = one point per INDEPENDENT unit of real work (one point per
      store / case / chapter / county graded on its own correctness), so the
      score tracks how much correct work was actually done and cleanly
      separates a partial SA answer from a complete MA answer.
    - LOAD THE CHECKLIST TOWARD HARD ITEMS (by COUNT and by category weight
      under P21-5): more correctness / reconciliation / depth / reward-hacking /
      partial-oracle / held-out items than easy presence items, so content
      (RH+PO) is ≥ 60% of total score and a rushed single agent lands VERY LOW
      while even a thorough swarm is meaningfully challenged
      (Phase 2.1 eval calibration: SA ~0-10%, MA ~20-30% not near-perfect --
      supersedes the older "MA 0.70-0.90" number). Aim the item mix so a
      weak/partial answer is clearly separated from a complete one BEFORE the
      first Harbor run.
    - DISCRIMINATION TEST: predict the pass-count of a strong answer vs a
      rushed/partial answer; if the two predictions are close, the rubric is
      not discriminative -- rewrite items until they clearly separate.
    - SHIP TEST (from the doc): if an agent could pass just by producing the
      files in the right format, the rubric is too weak; if SA could ever
      match or beat MA, the rubric is UNFAIR -- fix that before anything else.

  SCORING RUBRIC (15-25 BOOLEAN ITEMS; P21-5 / Production Rework). Write
  the rubric as a checklist of 15-25 TRUE/FALSE items. Prefer category
  weights 1 (static) / 2 (RH) / 3 (PO) so content ≥ 60% of total score
  (structural ≤ 40%); reward = sum(passed × w) / sum(total × w), clamped
  to [0,1]. Optionally apply a multiplicative content-quality signal
  (Production Rework §4) so formatting cannot wash out failed grounding —
  expose components + final score in reward.json. A flat one-point board
  is allowed ONLY if composition alone already meets the 60% content floor.
  There is NO tier, NO score cap/floor that invents the SA/MA gap, NO
  step function, NO per-check tuning, NO category weight > 3.
  Manifest must describe the real scheme (S-08 / QD-03). Older "NO
  weightage / one point only or auto-reject" and "content ≥40%" wording
  here is SUPERSEDED by Production Rework.

  WRITE THE ITEMS so the checklist naturally spans the work:
    - PRESENCE & COUNT first (deterministic, zero-cost, unfakeable):
      "output.xlsx exists", "audit_trail has >= 90 of 120 rows", "all 16
      .mp4 files present in /logs/agent/reels/", "the deck contains a
      slide titled 'Conflicts'", "compliance_matrix.csv has columns
      X,Y,Z". Prefer THRESHOLD BANDS ("at least N of M") over exact
      counts so expected browsing failures are tolerated.
    - EVIDENCE & GROUNDING: "every row carries a source URL on the
      allowlisted domain", "each cited excerpt is a verbatim substring of
      the fetched source", "claims are supported by the cited source".
    - CROSS-SOURCE / CONSISTENCY: "FDA-vs-ASHP conflicts are flagged with
      a rationale", "no internal arithmetic contradiction", "missing info
      is explicitly marked".
    - SUBSTANCE / FAITHFULNESS (LLM-judge items, only where reading
      comprehension is required): "this chapter summary is faithful to
      the source chapter", "the executive summary covers >= 3 of the 5
      designated areas". Send the judge the SOURCE plus the agent's
      section; never let it grade against a gold answer.
  Spread items across coverage, evidence, consistency, and artifact
  quality so a strong submission scores high and a partial one scores
  proportionally. No single item may zero the run.

  SPLIT THE LLM JUDGE INTO >=3 INDEPENDENT CALLS (QG hard rule, ledger L1 --
  QD-03.3). NO single LLM judge call may control more than 60% of the total
  reward. Group the LLM-scored items into >=3 independent calls (e.g. one per
  deliverable or theme) and combine the parsed verdicts; keep the largest
  single call comfortably under 60% of total points (the APPROVED task used 4
  groups, largest 31%). Moving deterministic/depth items (SA<0.30 lever #5)
  out of the LLM call also pushes the LLM share down. On any LLM-call INFRA
  failure, retry; if it still cannot complete, score that specific check 0.0
  while keeping it in the denominator, and make the failure loud in stdout,
  `judge_justification.txt`, and `reward_debug.json` (2026-08-11 verifier
  template). Never exclude the failed check, and never hide the failure inside
  a bare low reward.

  DO NOT TRUNCATE CONTENT THE LLM GRADES (QG hard rule, ledger L3 --
  QD-07.13). When the LLM judge scores >=50% of the reward, any per-unit
  character cap you apply before sending content to the judge MUST be large
  enough to hold a COMPLETE unit (a full case/card/section) and MUST be
  applied UNIFORMLY to every unit -- a cap that silently cuts scored content
  for most units is an automatic reject. If a unit is genuinely huge, score
  it with deterministic checks on the full text instead of truncating.

  NO ORACLE, NO solution/. Do not author a gold answer, do not load
  oracle.json in the verifier, do not compare to a gold value, do not
  ship a solve.sh. Any honest run against the real sources produces a
  correct result; fabricated values fail because they do not match what
  the live sources actually contain.

  VERIFIER (Phase 2.1: ONE grader file, three check dimensions):
    - There is ONE verifier, `tests/verify.py`, mirrored 1:1 by
      `tests/rubric_manifest.json`. It MUST contain all three check
      categories -- static, reward-hacking, and partial-oracle (see P21-4) --
      plus a content check for every rewarded artifact.
    - DETERMINISTIC code owns everything structured / exact (CSV / xlsx /
      JSON-fixed-fields / media): open and parse the artifact (openpyxl /
      csv / json / ffprobe), evaluate each boolean item, print a per-item
      PASS/FAIL breakdown, write reward = passed/total. Deterministic checks
      cannot hallucinate -- use them wherever the fact is exact, and for the
      reward-hacking and partial-oracle comparisons.
    - INLINE LLM checks (inside verify.py, no separate judge.py) only where
      quality needs reading (prose, decks, briefings). The LLM returns
      PASS/FAIL for those items; reward is derived SOLELY from parsed
      verdicts. Use MODULAR calls (one per deliverable/theme/item), W&B via
      `WANDB_API_KEY`, retries, and robust JSON extraction. On an unrecoverable
      LLM infra failure (no key / API error / unparseable / missing items),
      score the affected check 0.0 and record the failure in stdout,
      `judge_justification.txt`, and `reward_debug.json`. LLM MODEL MUST BE A
      DIFFERENT FAMILY from the agent's Kimi K2.6 (never Kimi / Moonshot / K2).
      Use the 2026-08-11 SwarmBench verifier template as the default plumbing;
      do not leave Fireworks/Moonshot-era defaults in a new package.
    - `verifier_type` in task.toml + manifest: use `"executable"` when
      verify.py owns the scoring (the normal Phase 2.1 case, even with inline
      LLM checks) and `"llm-judge"` only when scoring is purely LLM-derived.
    - HYBRID rule (QD-09.5-safe): each check contributes points from exactly
      the mechanism that owns it -- deterministic code owns static /
      reward-hacking / partial-oracle / injected-evidence extraction; the LLM
      owns only its qualitative items. For an LLM item, code only EXTRACTS
      and INJECTS grounding evidence (parsed header, row counts, chart
      dimensions, slide/note counts, source text) -- it must NOT score that
      item. The LLM always runs on the FULL relevant submission slice; no
      static check upstream-gates it.

  JUDGE/VERIFIER SANITY QUARTET (run before any Harbor spend):
    - strong/complete answer -> high fraction of checks pass
    - answer with ~30% of evidence stripped -> clearly fewer checks pass,
      still > 0
    - all-units-templated weak-but-complete answer -> LOW but > 0
    - partially-truncated answer (the predicted SA failure) -> non-zero,
      clearly fewer checks than a strong answer. If this lands at 0, you
      have a gate/cap — remove it.
  PROJECTED-GAP CHECK (do this on the sanity fixtures, BEFORE any 2h+ Harbor
  run): the templated / partial fixtures (predicted SA behavior) should land
  VERY LOW and clearly below a strong fixture; the rubric must SEPARATE a
  weak/partial answer from a complete, grounded one. If the weak/partial
  fixture already scores high, the rubric is not discriminative and the task
  is too easy -- return to GATE 3 (more correctness / reward-hacking /
  partial-oracle items, scale up, deeper DAG) NOW rather than discovering it
  after a live SA run. [Phase 2.1 calibration: aim for the eval-data direction
  -- SA near 0-10%, MA meaningfully challenged (~20-30%, not near-perfect) --
  per DIFFICULTY & GAP TARGETS, which supersedes the older "MA 0.70-0.90"
  numbers still present in some fixtures/text.]
  Confirm there is NO input by which a complete, schema-valid submission
  scores 0.

Lock schema + rubric (the explicit list of 15-25 boolean items, tagged by
category: static / reward-hacking / partial-oracle) + the sanity quartet,
record in HANDOFF.md + NOTES, and begin implementing the single grader
`tests/verify.py` plus its 1:1 `tests/rubric_manifest.json` and
`tests/partial_oracle.json` (AUTONOMY MODE).

============================================================
GATE 4 -- DECOMPOSITION SHAPE (hierarchical DAG, not flat)
============================================================
Decide and lock (record in HANDOFF.md + NOTES, then proceed):
  - UUID (32 lowercase hex, no dashes: `uuid.uuid4().hex`) + folder name
    in the EXACT official format (S-01):
      `<32hex>-SWARMBENCH-<SLUG>-<DOMAIN>-<TASKNAME>`
    where SLUG is derived from coordination_pattern (hierarchical ->
    HIERARCHICAL, specialist-routing -> SPECIALIST), DOMAIN and TASKNAME
    are ALL CAPS hyphen-separated (no spaces, no underscores, no
    lowercase). For this domain: `...-SWARMBENCH-HIERARCHICAL-PLANNING-
    OPERATIONS-<TASKNAME>`. The slug MUST match coordination_pattern in
    task.toml (S-05) and the ZIP name MUST equal the folder name.
  - coordination_pattern MUST be `hierarchical` (or `specialist-routing`,
    a shape with real depth). The client wants HIERARCHICAL / SPECIALIST-
    ROUTING for Phase 2 (2026-06-26 DM note) -- do NOT use `map-reduce`
    or `fan-out-synthesize`. Justify the hierarchy + the specialist
    routing in 2 sentences.
  - DAG DEPTH >= 2 IS MANDATORY (CR-07 / S-04). At least one sub-task
    must depend on another sub-task that itself has a downstream
    consumer. A flat star (all sub-tasks point only to a final
    synthesizer) is dag_depth = 1 and is auto-rejected. Declare
    `dag_depth` (>= 2) in task.toml and BUILD the chain in
    decomposition.yaml.
  - SCALE / DAG WIDTH. The client wants genuinely harder tasks: target
    ~20-50+ sub-agents. Set `dag_width` to the count at the widest
    parallel level (Hard tier = dag_width >= 20). `estimated_sub_agents`
    MUST EQUAL the number of sub_tasks in decomposition.yaml (S-04).
    Widen by batching real units across specialist workers (e.g. N
    reader workers each owning a batch under a domain lead), not by
    cloning one identical worker.
  - `decomposition.yaml` skeleton:
      * top-level `version` and `coordination_pattern` (must match
        task.toml), then a `sub_tasks` list.
      * EVERY sub-task MUST carry the FOUR official required fields (S-04;
        missing any one = reject): `id` (unique string), `description`
        (non-empty; never references /tests/ paths or oracle/answer
        values), `depends_on` (list of existing sub-task ids, or []),
        `parallel_group` (group label). QG also checks: no duplicate ids,
        all depends_on resolve, no cycles, sub-task count ==
        `estimated_sub_agents`, and dag_depth >= 2.
      * specialist sub-agent GROUPS with depth (e.g. orchestrator ->
        domain managers -> workers -> verifiers -> reducer), each with
        what it receives, what it emits, and what feeds the next stage
      * ALSO declare `subagent_type` on every sub-task (use `explore` for
        OpenCode compatibility). Without it the harness cannot assign the
        right agent tier and the run misbehaves (2026-06-26 review note).
      * THE FINAL ARTIFACT WRITE MUST NOT HARD-DEPEND ON THE VERIFIER. A
        sequential verifier tail that the assembler waits on will zero the
        whole run if the verifier times out. Instead: let the
        assembler/reducer write the deliverable incrementally from the
        upstream specialist outputs (so a usable artifact always exists),
        and run the VERIFIER in PARALLEL, time-boxed, ALWAYS emitting a
        partial defect list that a downstream finalizer/writer applies if
        present and skips if absent. A reducer that never runs = zero
        score; never make it wait on a long sequential bottleneck.
      * if specific sources are required, CONSTRAIN the sub-agents to
        those sources (free browsing follows wrong/invalid links)
      * fallback behavior for empty/failed sub-agent results so the
        orchestrator adapts instead of silently producing nothing
      * ALL descriptions self-contained (sub-agents do NOT see
        `instruction.md`)
      * NO leakage of expected answers / rubric values / gold citations
        (structure only); NO step-by-step "first X then Y" walk; NO
        multi-agent-only guidance that explains the gap
      * `parallel_group` correct (same-group cannot depend on same-group)

============================================================
PHASE 0 -- SCAFFOLD + TOOLING
============================================================
CRITICAL DELIVERY RULE (official §6.2 / static check S-02, EXTENDED by
Production Rework P21-13): the delivered task folder root must contain
EXACTLY these SEVEN items and NOTHING else -- any extra file or directory
at root (README.md, .DS_Store, solution/, scratch/, notes.txt,
_trainer_artefacts/, oracle.json) is an automatic reject:
    decomposition.yaml  instruction.md  high_level_prompt.md  task.toml
    environment/        execution_logs/  tests/

(`high_level_prompt.md` is REQUIRED by Production Rework; keep instruction.md.
Until Trainer Guidelines §6.2 text is updated, treat seven-item root as
binding for this wave — the old six-item whitelist without HLP is REJECT.)

So keep ALL trainer working files OUTSIDE the delivered folder. Lay out a
WORKSPACE that contains the clean task folder plus a sibling artefacts dir
(the sibling is never zipped and never lives inside the task folder):

  <workspace>/
    _trainer_artefacts/         (SIBLING -- never inside the task folder)
      HANDOFF.md                (locked spec from Gates 0-4)
      NOTES.md                  (live RESUME CHECKPOINT + DECISION LOG)
      idea_review.md            (* QA spreadsheet row + QA verdict, Gate 0)
      rubric_design.md          (* the 15-25 boolean items + sanity quartet)
      draft_review.md           (* Draft-Review report + S-01..S-07 results)
      similarity_report.txt     (* distinctness check, if used)
      tooling/
        requirements.txt
        fetch_sources.py        (* fetch/verify real sources; freeze
                                 snapshots + hashes when needed)
        build_rules.py          (* render the input_artifacts/ rules file +
                                 manifests)
        build_task.py           (renders instruction.md / high_level_prompt.md /
                                 decomposition.yaml / task.toml /
                                 tests/verify.py /
                                 tests/rubric_manifest.json /
                                 tests/partial_oracle.json / tests/test.sh
                                 from the locked spec — NEVER hand-edit
                                 production files; fix the builder + re-run.
                                 Emits NO solution/ and NO full oracle)
        scrub_api_keys.py       (redact secrets in execution_logs before zip)
        zip_task.py             (single-root archive of the 7-item folder)

    <32hex>-SWARMBENCH-<SLUG>-<DOMAIN>-<TASKNAME>/   (THE DELIVERED FOLDER)
      decomposition.yaml        (hierarchical; every sub-task has the 4
                                 required fields: id, description,
                                 depends_on, parallel_group)
      instruction.md            (SHORT, human-like, hand-written)
      high_level_prompt.md      (REQUIRED Production Rework: ~250 words,
                                 band ~100–450; terse requester voice;
                                 deliverables only — see P21-13 / P-RW-3)
      task.toml                 (Phase-2 schema -- see PHASE 3)
      environment/
        Dockerfile              (python:3.12-slim + minimal deps; if
                                 llm-judge, pip install openai; if charts/
                                 video, pip install matplotlib + ffmpeg;
                                 clone any repo at a PINNED commit and
                                 remove .git, leave codebase UNSOLVED; COPY
                                 input_artifacts/ ONLY -- never copy
                                 instruction.md / task.toml /
                                 decomposition.yaml / tests/ / any verifier
                                 or answer-key content (S-06))
        input_artifacts/        (the ONLY subfolder of environment/ besides
                                 Dockerfile -- holds the agent-facing hard
                                 rules file AND any frozen snapshots/
                                 provenance. There is NO separate rules/
                                 folder; binding rules ship here as markdown.
                                 For a pure-live-browse task this may hold
                                 just the rules file + a source manifest):
                                 <name>_rules.md   (* hard rules: output
                                   format, evidence rules, source
                                   constraints, quality bar; keeps
                                   instruction.md lean)
                                 source_manifest.tsv (source_id / filename /
                                   publisher / url / retrieval_date / sha256
                                   / token_count / role)
                                 sha256sums.txt    (when snapshots are frozen)
                                 snapshots/<...>   (* frozen real captures)
      tests/
        rubric_manifest.json    (REQUIRED Phase 2.1: client-readable rubric,
                                 1:1 mirror of verify.py; three categories
                                 static/reward_hacking/partial_oracle, five
                                 fields each, weight:1, total_checks matches)
        verify.py               (REQUIRED single grader: static + reward-
                                 hacking + partial-oracle checks, 15-25
                                 boolean items, reward = passed/total; may
                                 call an independent LLM inline for
                                 qualitative checks -- judge model != agent
                                 family. This is the ONLY verifier-named
                                 script at tests/ root -- no judge.py)
        partial_oracle.json     (grader-only trusted SAMPLE of hand-verified
                                 values; wired via test.sh; NEVER shipped to
                                 the agent environment)
        test_logic/             (optional verifier helper modules)
        test.sh                 (entrypoint; invokes /tests/verify.py; writes
                                 /logs/verifier/reward.txt strictly; frozen
                                 before runs)
      execution_logs/           (populated from the mascloud result zips -- see below)

  NO full oracle.json answer key. NO solution/ folder. NO solve.sh. (The
  full/golden oracle is deprecated in Phase 2 -- S-06 also rejects any
  answer-key content under environment/.) The Phase 2.1 `tests/partial_oracle.json`
  is DIFFERENT and ALLOWED: it is a small, grader-only SAMPLE of hand-verified
  values (not a complete answer key), it lives under tests/, and it never
  reaches the agent environment.

  execution_logs/ MUST end up with THREE OpenCode mode directories (Production
  Rework P-RW-2), each with at least one cloud trial. Merge logs from
  `<task>-single.zip`, `<task>-multi.zip`, and `<task>-multi_noplan.zip`
  (or whatever names mascloud drops). Preserve Harbor-emitted mode dir
  names exactly — typically:
    execution_logs/
      single-opencode-agent/
        result.json  config.json  [job.log]
        <32hex>__<id>/            (trial dir -- do NOT rename)
          result.json  config.json  [trial.log]
          agent/
            opencode.txt          (non-empty; raw JSON event stream, JSON on line 1)
            trajectory.json       (non-empty; ATIF-format top-level keys)
            raw_trajectory/orchestrator_*.json   (single: orchestrator only)
          verifier/
            reward.json           (or reward.txt + test-stdout.txt; consistent)
      multi-opencode-agent/       (same structure, plus
            raw_trajectory/subagent_*.json  -- one file per spawned subagent)
      <multi_noplan mode dir>/    (name as emitted by the multi_noplan result
            ZIP — do not invent a spelling; same trial/agent/verifier shape.
            Usable logs required; no gap/reward target for this mode.)
  Exact mode dir names for single/multi are `single-opencode-agent` and
  `multi-opencode-agent` -- any other spelling fails S-02. (The multi run's
  presence of `subagent_*.json` files is the concrete proof the swarm spawned;
  single has orchestrator files only.) Keep all three result ZIPs beside the
  task for delivery evidence.

Tooling discipline: all production artefacts are GENERATED by
`build_task.py`; never hand-edit (instruction.md prose is hand-written by
you, then assembled). Maintain `NOTES.md` RESUME CHECKPOINT after every
batch and a TodoWrite list throughout (one in_progress at a time).

============================================================
PHASE 1 -- SOURCE ASSEMBLY + (OPTIONAL) FREEZING
============================================================
For every source in Gate 2's plan:
  - Verify it resolves today the way the AGENT will fetch it: REPLAY the
    OpenCode `webfetch` request (`curl` with a Chrome User-Agent +
    `Accept-Language: en-US,en;q=0.9`) and inspect the BODY, not just the
    status. Confirm it is not (a) JS-rendered (200 shell, data via
    client-side scripts) or (b) login/WAF-walled (302 -> SSO, or hard 403
    from Cloudflare). webfetch runs NO JavaScript and has no browser TLS
    fingerprint, so either case means the agent gets nothing usable ->
    switch to the underlying JSON API / static file or ship a frozen
    snapshot. Record HTTP status + a JS/login note + timestamp. If a
    source fails this, SURFACE it and revise Gate 2 — never silently
    substitute or fabricate.
  - For LIVE-BROWSE sources: confirm they are publicly reachable and
    stable enough for the agent to fetch at runtime; record the canonical
    URL in the manifest and (if applicable) `metadata.reference_link`.
  - For FROZEN sources: capture a dated snapshot, store under
    `input_artifacts/snapshots/`, hash into `sha256sums.txt`, and record
    the exact request/URL + timestamp so the bytes are reproducible.
  - Render `input_artifacts/source_manifest.tsv` (one orientation row per
    source + the locator format to use).
  - Render the `input_artifacts/<name>_rules.md` hard-rules file from
    `build_rules.py` (this is where the rules module lives — NOT a separate
    `environment/rules/` folder).

Hard rules:
  - WINDOWS LINE-ENDING DISCIPLINE: all builders write text artefacts via
    `write_bytes` with explicit LF normalisation (or `newline="\n"`).
    `Path.write_text` on Windows emits CRLF and silently breaks Harbor's
    S-07 raw-byte substring check.
  - 100% real sources; no synthetic noise filler to pad size; no
    paywalled-only sources; snapshot bytes byte-equal to what the URL
    served (sha256sums.txt is the receipt).

============================================================
PHASE 2 -- RUBRIC + VERIFIER IMPLEMENTATION
============================================================
Implement the verifier as ONE standard grader, `tests/verify.py` (Phase 2.1:
judge.py is retired). Score 15-25 BOOLEAN checks (reward clamped [0,1]).
Point values follow P21-5: either flat 1 each (passed/total) OR category
1/2/3 (sum passed×w / sum total×w) after an EXPLICIT owner choice — never
pick silently. No caps, no full oracle, no per-check tuning. Before coding
the checks, RE-CONFIRM them against `03_design_guides/rubric_scale_presentation.pdf`: every
check grades CORRECTNESS against a real reference (not presence/format),
the checklist is GRANULAR (one point per independent unit of real work) and
LOADED TOWARD HARD ITEMS, and the predicted weak-answer score stays low. The
shipped `verify.py` must implement exactly the discriminative rubric locked at
Gate 3 AND be a strict 1:1 mirror of `tests/rubric_manifest.json`.

verify.py MUST cover the THREE Phase 2.1 check dimensions (see P21-4), and
`test.sh` invokes `/tests/verify.py`, which writes `/logs/verifier/reward.json`
(required four-field schema — see P21-2) and may also write `reward.txt`
with the SAME numeric overall score:

  (a) STATIC / DETERMINISTIC checks (usability + exact facts). Open and parse
    the real artifact (openpyxl for xlsx, csv, json, python-pptx for decks,
    ffprobe for video) and evaluate each boolean item: presence, row/column
    counts, threshold bands ("at least N of M"), verbatim-excerpt substring
    after NFKC + whitespace-collapse, URL-on-allowlisted-domain,
    evidence-path-exists + min-bytes, arithmetic invariants, uniqueness.
    These prove USABILITY, not correctness -- do not let them dominate by count.

  (b) REWARD-HACKING checks (authenticity). Deterministically detect the
    shortcuts that let an agent bank reward without doing the work: duplicated
    rows/coverage, repeated boilerplate, placeholder / `undefined` values,
    summaries that disagree with their source, visuals with the right filename
    but hollow/wrong content, malformed or unresolvable URLs, suspicious
    cross-row uniformity. Enumerate "how could this be gamed?" and write a
    check per hole.

  (c) PARTIAL-ORACLE checks (selected values vs trusted facts). Load the
    grader-only `tests/partial_oracle.json` (a hand-verified SAMPLE spanning
    head/middle/TAIL of the unit queue) and compare the agent's output for
    those sampled units. Fabricated-but-plausible values lose credit. Never
    leak partial_oracle.json into the agent environment.

  CONTENT check per rewarded artifact: every workbook/report/chart/image/video
  earns substantive credit only via a check of what it CONTAINS/communicates,
  not merely that it exists (e.g. ffprobe duration + genuine frame-to-frame
  motion; the value inside a cell).

  LLM checks INSIDE verify.py (only where meaning needs reading — prose or
  images/charts): start from `SwarmBench_Verifier_Template.zip`, then replace
  the example checks with task-specific criteria. As of 2026-08-11: W&B
  Inference `https://api.inference.wandb.ai/v1/chat/completions`, key
  `WANDB_API_KEY`; vision/multimodal default `Qwen/Qwen3.6-35B-A3B`; NEVER the
  same family as the agent; hardcode the model in `verify.py`; keep robust
  JSON extraction and failed-check 0.0 behavior. Use MODULAR calls -- multiple
  independent/parallel calls, each objective to one deliverable/theme/item;
  NEVER one giant call grading the whole rubric. Send only what the call
  needs (criterion prompt + exact `/logs/agent/...` images/text). ALWAYS send
  an explicit `User-Agent` (Cloudflare returns 403/1010 on urllib's default UA
  before auth — measured on FAA-AD-WAVE). Resolve the served model list at
  grade start; walk an ordered different-family candidate list for text;
  log `judge_model_resolved` into reward.json. Prompt hygiene (reviewer-
  checked on task 3): grading standard in the SYSTEM role; agent cells in the
  USER role, sanitised + length-capped + wrapped in an untrusted-data fence;
  name the graded unit (one row / one criterion); make the judge state its
  own answer BEFORE the verdict; anchor source excerpts POSITIONALLY. Prefer
  pinning `requests` in `tests/test.sh` (or Dockerfile) so the grader does
  not silently fall back to blocked urllib. The LLM emits structured JSON
  (score / verdict / evidence / reason); overall reward still derives from the
  full Phase 2.1 points board (static + RH + PO), not from judge-only mean
  unless every check is LLM (`verifier_type = "llm-judge"`). Retry with
  backoff on 429/5xx. On unrecoverable infra failure: follow the 2026-08-11
  verifier template rule: the affected judge check scores 0.0, remains in the
  denominator, and is reported loudly in stdout, `judge_justification.txt`, and
  `reward_debug.json`. Ground each
  LLM item by EXTRACTING evidence in Python and INJECTING it — context only;
  never score an LLM item in deterministic code.

Across all checks: each item is independent and binary; partial credit emerges
from how many items pass; reward clamped to <= 1.0; no mode/trajectory bonuses;
no reward-zeroing structural gate; no full-oracle comparison. Run
`python tests/verify.py --self-check` (the embedded sanity quartet). Fix the
verifier before spending any API budget.

============================================================
PHASE 3 -- BUILD PRODUCTION ARTEFACTS (`build_task.py`)
============================================================
`build_task.py` renders: instruction.md (lean human prose + crisp output
block with the EXACT `/logs/agent/...` output path), decomposition.yaml
(hierarchical, self-contained, no leakage, no HOW, four required fields +
`subagent_type` per sub-task), environment/input_artifacts/* (Dockerfile +
the rules file + any snapshots), tests/verify.py (the single grader),
tests/rubric_manifest.json (the 1:1 client-readable mirror),
tests/partial_oracle.json (grader-only trusted sample), and tests/test.sh
(invokes /tests/verify.py). It emits NO full oracle.json answer key and NO
solution/. Keep instruction.md's output path, rubric_manifest.json's
agent_output_path, and the path verify.py opens BYTE-IDENTICAL and all under
/logs/agent/.

task.toml MUST use the exact Phase-2 schema and valid values (official
§6.3; wrong type / enum / out-of-range = reject). Render under the right
tables:
  [task]
    name        = "swarmbench/<full-folder-name>"   (matches folder
                  exactly, including the 32-hex uuid)
    description = "..."                              (10-500 chars; tight)
  [metadata]
    verifier_type            = "executable" | "llm-judge"
    domain                   = "planning-operations"  (exact)
    coordination_pattern     = "hierarchical"         (exact; matches SLUG)
    secondary_classification = [...]   (>=1; EXACT underscore enums only:
                               "browsing", "long_writing", "multi_modal",
                               "long_horizon" -- NOT "multi-modal" etc.)
    dag_depth                = 2        (integer >= 2)
    dag_width                = 20       (integer >= 1; widest level)
    human_solving_hours_estimate      = 12.0   (float >= 10)
    human_solving_hours_justification = "..."  (must contain a number)
    estimated_sub_agents     = N        (EQUALS sub_tasks count in
                               decomposition.yaml)
    input_token_estimate     = 150000   (integer >= 1000)
    why_multi_agent          = "..."    (>= 50 chars; a SPECIFIC breakdown
                               of where a single agent's context runs out)
    reference_link           = "https://..."   (singular; starts http(s))
  [agent]      timeout_sec = 3600   (float 300-7200; OMIT entirely for a
                               complex long-horizon task -> no cap, see
                               LONG-HORIZON EXCEPTION / Phase 6)
  [verifier]   timeout_sec = 600    (float 60-1800 HARD MAX — Harbor
                               schema rejects >1800; size JUDGE_SAMPLE so
                               ceil(sample/batch)×majority×axes×sec/call
                               fits under this cap with margin. Do NOT set
                               5400 to "fix" an oversize sample.)
  [environment] cpus = 2 (1-8); memory_mb = 4096 (1024-16384);
                build_timeout_sec = 600 (60-1800)
Set `network_enabled = true` whenever the agent must reach live sources at
runtime; ALSO set `[environment] allow_internet = true` (that is the field
Harbor actually reads for outbound internet — without it the container has
no egress and a browsing task fails; `network_enabled` is metadata only).
Set `agent.timeout_sec` to the peer-typical band for the effort and never
starve SA -- EXCEPT for a long-horizon task, where you leave it UNSET (no
cap) and apply a generous timeout to the single-agent baseline at launch
(see LONG-HORIZON EXCEPTION). When unset, Harbor wraps the agent step with
timeout=None.

Phase 3 sanity gates (must pass before Harbor) — carry over the Phase 1
catalogue, adapted to the Phase-2 official rules:
  - `python tests/verify.py --self-check` — sanity quartet passes (single
    grader; no judge.py).
  - poison-pill: replace half the items with templated/empty content ->
    reward LOW but > 0 (partial credit preserved).
  - `_g_boolean_rubric` (HARD, Phase-2 core): the verifier scores 15-25
    BOOLEAN items. Flat board: each worth 1, reward = passed/total, and
    assert no `* weight` on a TOTAL / no tiers / no caps. Weighted board
    (only after explicit P21-5 choice): each check is worth its CATEGORY
    value (1/2/3), reward = sum(passed×w)/sum(total×w), nothing > 3,
    manifest weights GENERATED from category constants and EQUAL to what
    verify.py applies — forbid per-check tuning and total-multipliers, not
    the token `weight`.
  - `_g_no_oracle` (HARD): no full `oracle.json` answer key anywhere, no
    `solution/` folder, no `solve.sh`, and the verifier never loads or
    compares to a complete gold answer file. (Full oracle is deprecated;
    S-06 also forbids answer-key content in environment/.) NOTE: the Phase
    2.1 `tests/partial_oracle.json` is a small grader-only SAMPLE and is
    ALLOWED under tests/ -- assert it is under tests/ (never in environment/)
    and holds only a subset of hand-verified values, not a full key.
  - `_g_rubric_manifest` (HARD, Phase 2.1 / CR-08): `tests/rubric_manifest.json`
    exists and parses; has top-level task_id / verifier_type / total_checks /
    checks; EVERY entry has EXACTLY the five fields
    (detailed_explanation_of_checks, weight, agent_output_path, check_function,
    how_it_prevents_task_authenticity_violation); `weight` is either ALWAYS 1
    (flat) OR exactly the category value 1/2/3 matching the check's prefix
    (weighted — P21-5); numbering within each category is sequential from 1
    with no gaps; `total_checks` equals BOTH the manifest entry count AND the
    number of checks registered in verify.py; every `check_function` resolves
    to real code in verify.py / tests/test_logic/.
  - `_g_three_check_categories` (HARD, Phase 2.1): the manifest contains at
    least one `static_checks_<n>`, one `reward_hacking_checks_<n>`, and one
    `partial_oracle_checks_<n>` entry, and verify.py implements all three
    dimensions. A structural-only verifier is an auto-reject.
  - `_g_verify_py_single_grader` (HARD, Phase 2.1): the SOLE verifier-named
    script at `tests/` root is `verify.py`; NO `judge.py` / `verifier.py` at
    tests/ root; `test.sh` invokes `/tests/verify.py`; verify.py writes
    `/logs/verifier/reward.json` with the four required fields (P21-2) and
    may also write `reward.txt` with the SAME overall `reward` number.
  - `_g_reward_json_schema` (HARD, 2026-08): `reward` equals the verifier's
    overall run score (identical to reward.txt if both exist); the three
    `total_*_check_score` fields are bucket MEANS for reporting only — they
    are NOT averaged or DM-blended into `reward`. Manual patches of completed
    arms must preserve that equality (DM clarification 2026-08-05).
  - `_g_output_path_logs_agent` (HARD, Phase 2.1): every `agent_output_path`
    in the manifest begins with `/logs/agent/`; the identical path string
    appears in instruction.md and is the exact path verify.py opens; the
    verifier does not search arbitrary folders.
  - `_g_content_check_per_artifact` (Phase 2.1): every rewarded artifact has
    at least one CONTENT/substance check (not only presence/format).
  - `_g_source_novelty` (Phase 2.1): the primary sources are recent /
    less-canonical (not a famous textbook / classic case study the base model
    memorised); the agent is given the exact `/input_artifacts/...` path so it
    must read the supplied evidence rather than answer from memory.
  - `_g_judge_model_independent` (if the verifier calls an LLM): the LLM
    model is a DIFFERENT family from the agent's Kimi K2.6; assert it is
    NOT a Kimi/Moonshot/K2 slug. Pin endpoint / key env (`WANDB_API_KEY`)
    / ordered candidates per `swarmbench-judge-provider.mdc`; assert an
    explicit User-Agent is sent; assert served-model resolution runs
    before the first grade call.
  - `_g_no_reward_zeroing_gate` (HARD): no structural/static path sets or
    floors reward to 0. Only a genuinely empty/unparseable submission may
    produce a total 0.0. For LLM infra failures, only the affected judge
    check scores 0.0 and the failure must be visible in stdout,
    `judge_justification.txt`, and `reward_debug.json`.
  - `_g_no_score_cap`: no `min(score,X)` for X<1, no `max(0,1-n*penalty)`,
    no band ceiling; only permitted clamp is `min(final_reward, 1.0)`.
  - `_g_no_static_gate_before_llm`: the LLM judge (when used) runs on the
    full submission every time; no static check sits upstream and blocks
    it.
  - `_g_partial_credit`: an 80%-complete submission passes ~80% of the
    boolean checks.
  - `_g_llm_failure_tolerance`: retries, backoff, robust JSON parsing, and
    no exclusion of failed judge calls from the denominator.
  - `_g_description_length`: `[task].description` is 10-500 chars
    (assert, do not just remind); keep it a tight 1-3 sentence summary;
    push rationale into `why_multi_agent` / AHT justification.
  - `metadata.reference_link` is a SINGULAR string holding one fetchable
    canonical URL; regex-anchor it and assert the plural `reference_links
    = [` token is absent.
  - anti-leak grep across instruction.md + decomposition.yaml +
    environment/input_artifacts/ + Dockerfile + task.toml for any
    expected-answer / rubric-value / gold strings.
  - Dockerfile grep: must NOT COPY instruction.md / task.toml /
    decomposition.yaml / tests/ / any verifier or oracle/gold file (S-06).
  - test.sh / verify.py have NO process_cap / delegation_bonus
    / mode-dependent references; reward clamped with explicit `min(.,1.0)`.
  - `_g_lf_only_eol`: every rendered text/JSON artefact has ZERO `\r`.
  - `_g_output_path_single`: instruction.md states ONE output path and
    the verifier reads that exact path (with a defensive
    `/workspace/logs/agent/output.json` fallback so a path-trap is graded
    on content, not zeroed).
  - `_g_coordination_pattern`: assert `task.toml` / `decomposition.yaml`
    `coordination_pattern` is `hierarchical` (NOT `map-reduce`, NOT
    `fan-out-synthesize`) and that the sub-agents are role-differentiated
    (more than one distinct role; not N identical shard workers).
  - `_g_subagent_type`: assert EVERY sub-task in `decomposition.yaml` has
    a `subagent_type` field (OpenCode needs it to assign the agent tier).
  - `_g_network_enabled`: if the task requires live browsing/fetch at
    runtime, assert `task.toml` sets `network_enabled = true`. (Skip only
    for fully-frozen-snapshot tasks that need no runtime network.)
  - `_g_no_blocking_verifier_tail`: assert the deliverable-writing
    sub-task does NOT hard-depend on the verifier; the verifier runs in
    parallel / time-boxed and emits partial defects, so a verifier
    timeout can never zero a run that already produced the artifact.
  - `_g_instruction_human_like`: instruction.md reads as a FIRST-PERSON
    human request, has NO Markdown `#`/`##` headings (assert the rendered
    instruction.md contains zero lines matching `^#{1,6}\s`), NO step-by-
    step solving stages, NO "each agent / your shard / the synthesiser"
    role wording, NO decomposition leakage, states ONE output path, and
    is concise. Perfect Markdown documentation reads as LLM-generated and
    is a real observed rejection note.
  - `_g_task_toml_table_layout`: each required key read from its correct
    table ([task].name/description, [metadata].* , [agent].timeout_sec,
    [verifier].timeout_sec, [environment].*); plus the Phase-2 ranges
    (dag_depth>=2, dag_width>=1, human_solving_hours_estimate>=10 with a
    number in its justification, input_token_estimate>=1000,
    why_multi_agent>=50 chars, verifier timeout within band). NOTE:
    `[agent].timeout_sec` is OPTIONAL and is expected to be ABSENT for a
    long-horizon task (no cap); only range-check it when present.
  - `_g_folder_name_format` (S-01/S-05): folder (and ZIP) name matches
    `^[0-9a-f]{32}-SWARMBENCH-(FANOUT|MAPREDUCE|SPECIALIST|PIPELINE|HIERARCHICAL|DEBATE)-[A-Z][A-Z0-9-]+$`,
    the SLUG equals coordination_pattern in task.toml, and
    `[task].name == "swarmbench/<full-folder-name>"`.
  - `_g_seven_item_root` (S-02 + Production Rework): the delivered task folder
    root contains EXACTLY decomposition.yaml, instruction.md,
    high_level_prompt.md, task.toml, environment/, execution_logs/, tests/
    -- and nothing else (no _trainer_artefacts/, no solution/, no oracle.json,
    no stray files). high_level_prompt.md word count in band ~100–450.
  - `_g_secondary_classification_enum`: `secondary_classification` is a
    non-empty array drawn ONLY from {"browsing","long_writing",
    "multi_modal","long_horizon"} (exact underscores).
  - `_g_estimated_sub_agents_match` (S-04): `estimated_sub_agents` equals
    the number of sub_tasks; every sub-task has id/description/depends_on/
    parallel_group; no duplicate ids; all depends_on resolve; no cycles.
  - `_g_dag_depth_2` (S-04/CR-07): at least one sub-task depends on
    another sub-task that itself has a downstream consumer (not a flat
    star); declared `dag_depth` is an integer ≥ 2. Official QG does NOT
    require declared depth == longest `depends_on` node-count (task 3:
    managerial tiers = 3 while the longest path was ~7). Prefer reporting
    managerial spawn levels (or post-run observed MA tree per item E);
    do not force a local gate that rejects a valid hierarchical DAG
    solely because path-length ≠ declared depth.
  - `_g_env_no_scoring_content` (S-06): nothing under environment/ is a
    verifier or answer key (no verify.py/judge.py/oracle/gold/test files
    copied in); Dockerfile leaves the codebase UNSOLVED and removes .git.

============================================================
PHASE 4 -- QD SELF-AUDIT (run BEFORE Harbor)
============================================================
Walk every PHASE-2 Quality Dimension (QD-01 .. QD-09 in
`PHASE_2\documentations_phase_2\01_quality_gate\Quality_dimensions_phase_2.md` -- the SOLE
Phase 2 quality bar; do NOT audit against the deprecated Phase-1
QD-01..QD-14) and produce `_trainer_artefacts/qd_self_audit.md` with
PASS/FAIL per check, verbatim quotes on FAIL, and the fix. Iterate until all
PASS or NOT_APPLICABLE. Pay particular attention to:
  - QD-01 Task Quality, Instruction & Authenticity (human, role-neutral, no
    leaked stages, real sources/entities);
  - QD-02 Instruction–Verifier Alignment (every must/must-not in
    instruction.md + rules is enforced by the verifier; output keys match
    the stated schema);
  - QD-03 Verifier Rubric Integrity (boolean checks; flat 1-pt OR category
    1/2/3 per P21-5 after an explicit choice; CORRECTNESS-not-presence,
    GRANULAR + DISCRIMINATIVE -- the difficulty and the gap live here;
    cross-check against 03_design_guides/rubric_scale_presentation.pdf);
  - QD-04 Reward-Hacking Resistance (no template/duplicate/keyword-stuff/
    null-fill shortcut);
  - QD-05 Multi-Agent Necessity (COORDINATION, not just parallelism);
  - QD-06 Decomposition Soundness (WHAT not HOW; hierarchical depth >= 2);
  - QD-07 Benchmark Validity & Fairness (timeouts equal both sides, no
    SA-only limits, no engineered gap);
  - QD-08 Infrastructure & Harbor Compliance (seven-item root, task.toml
    schema, execution_logs structure);
  - QD-09 Coordination Value & Gap Integrity (the gap is REAL and MEASURED,
    not manufactured; Phase 2.1 calibration SA ~0-10% / MA meaningfully
    challenged ~20-30% / genuine positive gap arise naturally -- see
    DIFFICULTY & GAP TARGETS, superseding older "MA 0.70-0.90").

============================================================
PHASE 4.5 -- STATIC CHECKS + DRAFT REVIEW (BLOCKING)
============================================================
Phase 2's Quality Gate is the official Turing Draft Review plus the
automated static checks S-01..S-07. Both must be clean before submission.

  A. SELF-RUN THE STATIC CHECKS (S-01..S-07) -- these run FIRST on the
     real gate and any one failing stops the review (official §6.6):
       S-01 folder/ZIP name matches the regex and the SLUG matches
            coordination_pattern.
       S-02 the six root items exist, nothing extra at root, both
            execution_logs mode dirs present with every required file.
       S-03 task.toml parses; all required fields present + correct type;
            dag_depth>=2; description 10-500; reference_link a URL;
            human_solving_hours_estimate>=10; estimated_sub_agents>=2;
            input_token_estimate>=1000.
       S-04 decomposition.yaml parses; sub_tasks present; each has id/
            description/depends_on/parallel_group; no dup ids; no dangling
            depends_on; no cycle; count == estimated_sub_agents; depth>=2.
       S-05 folder slug == coordination_pattern.
       S-06 no scoring file (oracle.json/verify.py/judge.py) or answer-key
            content inside environment/.
       S-07 execution_logs are NOT stale (regenerated against the current
            instruction.md).
     The Phase 3 build gates already assert most of these; re-confirm on
     the assembled folder before review.

  B. DRAFT REVIEW (LLM reviewer, MANUAL-NEED M2). Use the official Turing
     Draft Review tool: log in with the Turing email, click Draft Review,
     upload the task as a .zip, run it, and read the quality report. Fix
     every issue that ACTUALLY exists, re-run the builder, re-zip, and
     re-review until clean. Save the report to
     `_trainer_artefacts/draft_review.md`.

  C. OPTIONAL local pre-check: run the PHASE-2 Local Quality Gate
     (`PHASE_2\documentations_phase_2\01_quality_gate\LocalQualityGate_ReviewerPrompt_Phase2.md`,
     which spawns sub-agents across the Phase-2 QD-01..QD-09 from
     Quality_dimensions_phase_2.md, in a FRESH session) to catch issues
     BEFORE the Draft Review. Do NOT use the Phase-1
     LocalQualityGate_ReviewerPrompt.md for a Phase 2 task. The Draft Review
     + S-01..S-07 remain the binding Phase-2 gate.

REJECT -> fix via builder edits + re-run the builder, then re-run; loop
until clean. Phase 5 is BLOCKED until the static checks pass and the
Draft Review is clean.

============================================================
PHASE 4.6 -- INSTRUCTION.MD SIMILARITY / DISTINCTNESS (SUPPLEMENTARY)
============================================================
Not part of the official §6 Quality Gate, but a strong safeguard against
the #1 rejection risk: a task whose SWARM TRAJECTORY duplicates an
existing one. If the similarity web app is available (MANUAL-NEED M3),
run it after the FINAL `build_task.py` run and a clean Phase 4.5. Hand the
final `instruction.md` to me with a "paste this into the similarity web
app" note; record the returned embedding + Jaccard scores + verdict +
timestamp in `similarity_report.txt`.
  - PASS -> Phase 5.
  - FAIL -> diagnose the triggering metric. JACCARD = literal token
    overlap (reword shared sentences/labels). EMBEDDING = same MEANING /
    SWARM TRAJECTORY as the match (the dangerous one). Embedding is
    driven by the trajectory, not vocabulary: rewording persona/keys
    barely moves it. Re-shape so the document FOREGROUNDS the genuinely
    distinctive activity (the high-value axis from Gate 1(C)); if prose
    edits prove futile (embedding rises while Jaccard falls), the flag is
    genre-level — RE-ARCHITECT what the swarm does (keep the frozen real
    sources, change the verb + output object + rubric), then re-run.
    Budget ~3-4 wording iterations after a re-architecture; log every
    run's max% + nearest match; escalate to the DM with the run history
    rather than thrashing.
  - Never lower similarity by deleting an enforced MUST clause (it
    desyncs instruction.md from the verifier). Diverge PROSE, keep
    SEMANTICS.
  - If instruction.md changed after Phase 4.5, RE-RUN Phase 4.5; if
    Harbor already ran, delete execution_logs/* and re-run (S-07).
If the similarity checker is available, clear it before Phase 5; if it is
not, rely on the Gate 1(C) distinctness analysis and the Draft Review.

============================================================
PHASE 5 -- PACKAGE + SUBMIT
============================================================
Preconditions: the static checks S-01..S-08 pass and the Draft Review is
clean (and, if available, the similarity check passed); for production
rework, the LLM QG report is also ready (P-RW-6).
The `execution_logs/` now come from the CLOUD runs: each `mascloud run`
(see M4 / Phase 6 / P21-13) drops a result zip beside the task folder
(`<task>-single.zip`, `<task>-multi.zip`, `<task>-multi_noplan.zip`) that
contains the full task PLUS a fresh `execution_logs/`. Merge the
`single-opencode-agent/` logs from the single result zip, the
`multi-opencode-agent/` logs from the multi result zip, and the multi_noplan
mode tree from the multi_noplan result zip into the delivered task folder's
`execution_logs/` (do NOT rename the Harbor-generated trial dirs; preserve
the multi_noplan mode dir name as emitted).
The DELIVERY zip MUST contain the task folder AT THE TOP LEVEL (not nested
in another directory), with the SEVEN root items (including
`high_level_prompt.md`) and the populated `execution_logs/` (single + multi
+ multi_noplan cloud runs with their trial subfolders, result.json,
config.json, agent/opencode.txt + trajectory.json + raw_trajectory/
(orchestrator_*.json for single; orchestrator_*.json + subagent_*.json for
multi modes), verifier/reward.json). Because runs are cloud-side
now, no personal Fireworks/Daytona key is ever written locally; still run
`tooling/scrub_api_keys.py --fix` on `execution_logs/` and confirm `--check`
reports 0 matches (defensive: any stray secret or trainer-machine absolute
path), then `tooling/zip_task.py --task-root <task-folder>
--include-execution-logs` (it re-runs the scrub `--check` preflight and ABORTS
if any secret remains). The ZIP file name MUST EQUAL the task folder name
exactly (`<32hex>-SWARMBENCH-<SLUG>-<DOMAIN>-<TASKNAME>.zip`). NEVER include
the sibling `_trainer_artefacts/` (or solution/ or oracle) in the zip --
recall the root is a strict seven-item whitelist for this wave. Keep the
three mode result ZIPs as delivery evidence.

SUBMIT: upload the .zip to the shared delivery Google Drive folder, and
register the task on the Turing platform with its labeling-tool link (a
task without the labeling-tool link is not approved or paid). Two trainers
must sign off on every task (official §9).

============================================================
PHASE 6 -- MASCLOUD RUNS + DUAL DEBUG (CLOUD)
============================================================
Stop after Phase 5. Hand back: the zip path; the qd_self_audit result;
the Draft Review result (clean); the similarity result (if run); the
chosen secondary_classification(s); the predicted natural SA failure;
predicted SA and MA reward bands; the QA idea-approval verdict.
ALL Phase 6 runs go through MAS Cloud Run via the `mascloud` CLI going
forward (MANUAL-NEED M4) -- do not fall back to local Harbor for shipping
logs:
  mascloud runs                              # check Today: X/6 + models used
  mascloud run <task_folder> --mode single
  mascloud run <task_folder> --mode multi
BOTH modes are required; each streams live and drops a `<task>-single.zip` /
`<task>-multi.zip` result beside the folder with fresh `execution_logs/`.
DAILY QUOTA: 6 submissions/trainer/day (midnight UTC reset); every submit
counts regardless of outcome -- finish fixture projected-gap + local
verify.py BEFORE burning a cloud slot. AGENT MODEL: usually `kimi-k2p6`;
under high concurrent load new MULTI-mode runs may auto-switch to
`kimi-k2p7-code` (server-side protection; no trainer flag). Confirm the
model on `mascloud runs` if comparing retries. `swarm-opencode-single`
denies the `task` tool (no subagents, 1 session); `swarm-opencode-multi`
allows it (general coordinator + explore leaf workers, hierarchical,
~13-20 agents). Then drive the DUAL-DEBUG + GAP loop autonomously:

  RUN ORDER FOR LONG-HORIZON TASKS (manager guidance): run the MULTI-AGENT
  mode FIRST with NO timeout (task.toml leaves `[agent].timeout_sec` unset)
  and record the actual wall-clock it takes to finish — these runs can exceed
  2 hours and a premature cap loses progress. THEN run the SINGLE-AGENT
  baseline with a GENEROUS budget (>= the multi's observed completion time).
  QUOTA CAUTION: a long MA + SA pair is already 2 of 6 daily slots; do not
  launch speculative extra reruns until trajectories + per-check scores say
  the next change will move the gap. NOTE: `mascloud` exposes no documented
  per-run model or timeout override flag (model is server-assigned, possibly
  auto-switched under load), so timeout is governed by task.toml; if a
  long-horizon task needs a fair SA cap >= the multi wall-clock and mascloud
  offers no launch-time override, escalate (M4) rather than starve SA. The gap
  must remain a rubric-QUALITY difference; a single-agent low score caused
  only by an unfairly tight cap is a timeout artifact and is rejected.

  GAP TARGETS (rubric-based; a real, defensible difference):
    - single < multi ALWAYS, with a clear margin. PHASE 2.1 WORKING TARGET:
      SA very low (~0-10%) and MA meaningfully challenged (~20-30%, NOT
      near-perfect; a near-perfect MA means the task/rubric is too easy),
      with a genuine positive gap. The exact automated acceptance threshold
      is being reconciled by the client (see DIFFICULTY & GAP TARGETS, which
      supersedes the older "MA 0.70-0.90 / gap > 0.23" numbers). If you
      designed for difficulty per DIFFICULTY &
      GAP TARGETS (scale + correctness rubric + depth), this should hold on
      the FIRST run rather than after repeated SA reruns.
    - meaningful PARTIAL CREDIT on both sides (no 0.0 for complete/
      partial submissions).
    - the predicted SA failure is OBSERVED in the trajectory (not
      manufactured by the scorer). Read both trajectories: SA must have
      genuinely ATTEMPTED the full task (real tool calls across the full
      scope), MA must have FOLLOWED the decomposition and the reducer
      produced correct aggregated output. Confirm the gap is genuine work,
      not a spec misread, broken verifier, or hallucinated judge.

  FALSE-FAILURE CLASSIFICATION (run FIRST on every 0.0): open
  `verifier/reward.txt` + `agent/output.*` + `agent/trajectory.json`.
  If the agent produced a substantively-complete output but reward is
  0.0, it is a FALSE FAILURE (path-trap, strict LLM-fail gate, boundary
  gate, output-shape mismatch) — PATCH the task, do not ship. Only an
  empty/invalid output or real analytical incompetence is an INTENDED
  failure.

  JUDGE-HALLUCINATION CHECK (Phase 2 mandatory, trainer + QA): manually
  read the SA and MA outputs and confirm the rubric scores match a human
  reading. If the judge under- or over-scored, tighten the judge prompt
  with concrete criteria and re-grade. Do not blindly trust the judge.

  If single is too high: the task is too easy or leaks — deepen the
  multi-stage/verification load, broaden sources, sharpen the rubric to
  require substantive evidence. Never add a gate/cap.
  If multi is too low: improve the DECOMPOSITION first (deepen the
  hierarchy, strengthen the verifier + reducer roles, constrain sources);
  only then ease instruction.md. Never widen the rubric to fake a gap.
  If the gap is timeout-driven: for a normal task confirm timeouts are
  EQUAL both sides; for a long-horizon task (multi run uncapped, single
  capped) confirm the single cap was at least the multi's observed
  wall-clock so SA had a fair budget. Either way you must not throttle SA
  (throttling is a work-ethics violation), and a gap that exists ONLY
  because SA was truncated short of a fair budget is not a real gap.

Record every iteration in the NOTES DECISION LOG. Iterate until the gap
is real or an ESCALATE-EARLY trigger fires. If SA stays above target after
the iteration budget (4 rubric/decomposition tuning rounds, or 1 full
re-architecture), do NOT keep re-running SA (each run costs 2h+) -- invoke
the ALTERNATE-USE PIVOT (scale the corpus up / re-grade for correctness /
add a depth layer / re-target the class / park + escalate with the run
history) and record it in the LESSONS LOG. Perform deep TRAJECTORY ANALYSIS
to understand WHY SA failed and WHY MA succeeded — this lowers future
rejection rates and improves task design; capture any durable, generic
finding in the LESSONS LOG (STANDING DUTY 0).

============================================================
THINGS YOU MUST NOT DO (Phase 2)
============================================================
- Do NOT build a local-file-only task, a flat fan-out task, or a
  Phase-1-style "read N docs -> emit JSON" task. (Top Phase 2 rejects.)
- Do NOT use `map-reduce` or `fan-out-synthesize` coordination. The
  client requires HIERARCHICAL / SPECIALIST-ROUTING only (2026-06-26 DM
  note). `coordination_pattern` must be `hierarchical`; sub-agents are
  distinct ROLES routed by responsibility, not N identical shard workers.
- Do NOT default the final deliverable to xlsx/spreadsheet. The team has
  too many spreadsheet finals (2026-06-26 DM note) -- diversify across
  presentations, charts, CSVs, reports, dashboards, video, animation, and
  pick the format the real-world scenario actually demands.
- Do NOT use synthetic, sensitive, or fabricated data; do NOT backfill a
  failed browse with invented values.
- Do NOT write an AI-generated-looking, >100-line, step-by-step
  instruction.md; do NOT leak the stages/decomposition; do NOT inline a
  long hard-rules block (ship it as a rules file in
  environment/input_artifacts/). There is NO environment/rules/ folder.
- Do NOT manufacture the gap: no SA-only restrictions, no info
  asymmetry, no blocking SA from tools, no token throttling, no
  engineered timeouts, no hidden traps.
- Do NOT use score caps, floors, ceilings, step bands, binary fail-closed
  gates, hidden multipliers, hidden weights, or per-check tuning. A flat
  additive rubric is allowed when content share clears the current bar; category
  weights 1/2/3 and multiplicative content-quality signals are allowed only
  when verify.py, `rubric_manifest.json`, `reward.json`, and `reward_debug.json`
  all describe the same formula honestly.
- Do NOT ship an oracle.json, a solution/ folder, or a solve.sh, and do
  NOT compare to a gold answer in the verifier (oracle is deprecated). Do
  NOT use the same model family as the agent for the LLM judge.
- Do NOT omit `high_level_prompt.md` or use the wrong folder/ZIP name; the
  delivered root is the current seven-item package and the name must match
  `<32hex>-SWARMBENCH-<SLUG>-<DOMAIN>-<TASKNAME>` with the slug matching
  coordination_pattern.
- Do NOT fabricate, hand-edit, or ship stale execution logs; runs must be
  REAL OpenCode single + multi runs against the current task, with both
  trajectories personally reviewed.
- Do NOT let a static check gate the LLM judge or zero a complete
  submission; do NOT default-accept unparsed judge output; do NOT exceed
  reward 1.0.
- Do NOT add mode-dependent scoring or hint the coordination pattern in
  the rubric/judge prompt; do NOT let the judge hallucinate (use
  concrete, checkable criteria and verify manually).
- Do NOT leak expected answers / rubric values / gold into
  instruction.md, decomposition.yaml, environment/input_artifacts/, the
  corpus, or the Dockerfile; do NOT COPY production files into the
  Dockerfile.
- Do NOT use fictional named entities; every entity is real and public.
- Do NOT edit execution_logs/; do NOT modify verify.py / judge.py /
  test.sh between the single and multi runs; do NOT edit instruction.md
  or decomposition.yaml after a run without deleting execution_logs/ and
  re-running (S-07).
- Do NOT submit stale execution logs or a failed Draft Review; do NOT skip the
  trainer+QA dual debug or the judge-hallucination check.
- Do NOT start building before Gate 0 has selected and documented the CLAIMED,
  SCRATCH, or PARTIAL route. Parse and reconcile a claimed brief (CS-1..CS-4)
  or create and reconcile a scratch brief (CS-S); never invent or fabricate a
  claim/spec; do NOT submit without a labeling-tool link.
- Do NOT blindly submit AI-generated instructions/rubrics — the trainer
  is fully accountable for human-readable, logically-sound, verified
  content.

============================================================
WORKING STYLE
============================================================
- Pipeline mode: while I run one task through Harbor, build the next.
- Brainstorm MY OWN ORIGINAL idea with peers/agents BEFORE building
  (Phase 2 ask). Do not pick or copy an idea from the sheet; study the
  sheet only to learn how the leads design DAG depth/width + multi-stage
  workflows, then apply that method to a unique idea of my own.
- TodoWrite list throughout; one in_progress at a time. Maintain
  NOTES.md RESUME CHECKPOINT after every batch.
- Run from PowerShell. PowerShell does NOT chain with `&&`; use `;` or
  `&` with absolute paths.
- Reuse the trainer venv from prior tasks; add Phase-2 deps (browser/
  fetch libs, openpyxl for xlsx, python-pptx for decks, matplotlib for
  charts) and pin them in `tooling/requirements.txt`.

============================================================
LESSONS FROM PASSED PHASE 2 SAMPLES (2026-06-26 approved sheet)
============================================================
These are distilled from the task ideas that PASSED creative-idea review
(maternal-health board pack, transit Title VI equity, municipal ACFR
fiscal health, ECG-transformer lit review, municipal bond workbook, IT
vendor compliance audit) and the reviewer's verbatim comments:
- WRITE instruction.md AS A PERSON. Every passed task opens in first
  person with a real persona and motive ("I run service planning at
  County Connection and the Board votes next month..."; "I do research
  for a nonprofit that works on city budgets..."; "I'm on the
  procurement team here..."). The one task that used a `#` heading got a
  "doesn't look human enough, looks LLM generated" comment. No headings.
- DELIVER REAL ARTIFACTS, NOT JSON. Passed outputs are output.xlsx +
  briefing.docx + chart PNGs (+ .md syntheses). The explicit reviewer
  note: "Please remove json outputs, they don't represent real world
  task." Sub-agents MAY pass JSON between each other internally; the
  FINAL deliverable to the user is a real document.
- DECOMPOSITION DOES NOT RESTATE instruction.md. Reviewer note: "No need
  to mention structures from instruction.md. The multi agent will get
  instruction.md alongside decomposition.yaml." Describe ROLES + I/O, not
  the spec.
- SPLIT THE PRODUCE STEP. Reviewer note: separate producing the deck/
  charts from writing the document from assembling the workbook into
  DIFFERENT sub-agents; do not let one overloaded reducer do all of it.
  Passed shape: intake-lead -> domain specialists (by area, each owning a
  consistent categorization across all units) -> reconciliation/verifier
  -> workbook-assembler -> chart-producer + report-writer (parallel).
- VERIFIER MUST PARSE CONTENT, NOT COUNT. Reviewer note: "checking only
  slide count for pptx is weak -- parse the slides and use an LLM judge
  on your rubric." Same for xlsx/docx: open and read it.
- DETERMINISTIC CHECKS ARE JUDGE CONTEXT, NOT A GATE. Passed rubrics
  recompute reference numbers in Python from pinned inputs and INJECT
  them into the judge prompt so the LLM never does arithmetic (kills
  judge math-hallucination); the recomputed values are context only and
  do not set/cap the reward. NOTE: under the official Phase-2 rule the
  rubric is now FLAT BOOLEAN -- one point per check, no weighting -- so
  lean the checklist toward substance/accuracy items (more of them) and
  keep only a few format/chart items, rather than weighting dimensions.
- BROWSING STAYS LOAD-BEARING + REPRODUCIBLE. The binding facts are NOT
  in the local packet; the agent must fetch them. Pin dead-link-prone
  sources to Internet Archive / Wayback snapshots (or a frozen GitHub-
  release corpus) and ship only a small pointer list (sources.csv) so a
  network blip never zeroes a correct run -- but the data itself is never
  shipped locally. When a live source is BOT-PROTECTED (returns a
  challenge/apology page to non-browser clients), drifts, or has patchy
  Wayback coverage, host a faithful frozen copy on a PUBLIC GitHub
  repo/release and fetch via `text_url` (the lead-approved pattern from
  initial sample 95dec0ee...); record original URL + date + sha256 in the
  manifest.
- KNOW HOW THE AGENT ACTUALLY FETCHES (OpenCode `webfetch`), AND REPLAY
  ITS EXACT REQUEST BEFORE LOCKING ANY SOURCE. Verified from the harness
  + opencode source (2026-06-29): the agent's `webfetch` tool sends a real
  Chrome User-Agent (`Mozilla/5.0 ... Chrome/143 Safari/537.36`) plus
  `Accept-Language: en-US,en;q=0.9`, and on a Cloudflare `cf-mitigated:
  challenge` 403 it retries once with UA `opencode`. So plain
  User-Agent gating is NOT your problem -- opencode already sends a
  browser UA. BUT `webfetch` is a plain HTTP GET -> HTML-to-markdown with
  NO JavaScript execution and NO browser TLS fingerprint, a 5 MB cap, and
  a 30 s default / 120 s max timeout. (The agent also has a Shell tool, so
  it can `curl` JSON APIs directly.) Before locking a source, REPLAY that
  exact request yourself (`curl` with the same UA + Accept-Language) and
  inspect the BODY, not just the status:
    * JS-RENDERED page (status 200 but the data is loaded by client-side
      scripts -- many `<script>` tags, an `id="root"`/`__NEXT_DATA__`
      shell, an empty data table) -> the agent gets only the shell. Use
      the underlying JSON/AJAX endpoint or static data file instead, or
      pre-render and ship the content as `input_artifacts/` (official
      CR-01). E.g. the FDA shortages PORTAL and the Orange Book portal are
      JS-rendered; the openFDA API (`api.fda.gov/drug/shortages.json`) is
      clean JSON that the agent can use directly.
    * LOGIN / WAF wall (302 -> SSO login, or a hard 403 from Cloudflare/
      Akamai with no `cf-mitigated: challenge`) -> NOT fetchable headless,
      even with the right UA, because the WAF also checks TLS fingerprint
      / session. Replace the source or ship a frozen dated snapshot. E.g.
      ASHP current-shortages now 302-redirects to `login.ashp.org` behind
      Cloudflare -- unusable as a live source.
  PREFER OFFICIAL JSON APIs (openFDA, RxNav/RxNorm, DailyMed all return
  clean JSON to the agent) over scraping any portal. Record each probe's
  status + a note on JS/login in the source plan so a reviewer sees the
  source was verified the way the AGENT fetches, not the way a browser
  does.
- CONTAMINATION GUARD. If you cite a real published worked example for
  method/thresholds, the task scenario must NOT mirror or reuse that
  example's conclusions.

============================================================
LESSONS CARRIED OVER FROM PHASE 1 (still generic + binding)
============================================================
- The gap lives in the task, not the scoring; partial credit always; no
  boundary-equal gates; retries + failure tolerance for LLM-judge calls;
  LF-only line endings; singular `reference_link`; tight
  `[task].description` (10-500 chars); Dockerfile copies only
  input_artifacts/ (the rules file + any snapshots live there; there is NO
  environment/rules/ folder) and never any verifier/answer-key content
  (S-06); never leak the expected answer; re-run logs after any
  instruction.md edit (S-07); classify every 0.0 as INTENDED vs FALSE
  before concluding. (Phase-2: no oracle, no solution/, no DERIVE-vs-cp
  concern -- there is no gold answer to derive.)
- The full Phase 1 lesson archive lives in
  `PlanningOperations_TaskCreationPrompt.md` (the "LESSONS BAKED IN"
  blocks). Consult it for the detailed sanity-gate catalogue; promote any
  Phase-2-specific lesson you learn into THIS file (STANDING DUTY 0).

============================================================
QG REVIEWER REJECTION LEDGER (distilled from 09_qg_reviews/raw_reports/ -- always-check)
============================================================
The distilled, DE-DUPLICATED list of every reason the LLM Quality Gate has
REJECTED or FLAGGED a task in the `09_qg_reviews/raw_reports/` folder. This is the pre-flight
checklist: satisfy EVERY entry before you ship. RULE: at the start of each
build, re-read the whole `09_qg_reviews/raw_reports/` folder (it grows over time); whenever a
report shows a rejection reason NOT already covered here, ADD it (check-id |
what triggered it | rule going forward) and, if enforceable, promote it into
the relevant gate/phase. Each entry names the QD check so you can trace it.

  L1. [QD-03.3 no_single_shot_judge_majority_score] A SINGLE LLM judge call
      scored all rubric items -> that one call controlled >60% of the reward
      -> REJECT. RULE: split the LLM rubric into >=3 INDEPENDENT judge calls
      (RUBRIC_GROUPS, e.g. one per deliverable/theme), so NO single call
      exceeds 60% of total points; and/or move enough items into the
      deterministic band that the largest single LLM call is well under 60%.
      (The APPROVED task used 4 groups; the largest call was 31%.)
  L2. [QD-06.6 what_not_how] decomposition.yaml sub-task descriptions leaked
      HOW: step-by-step algorithms, running-total walkthroughs, behavioural
      ordering ("write your outputs IMMEDIATELY before anything else"),
      memory-management hints ("write INCREMENTALLY, do not hold in memory"),
      threshold/tier-mapping definitions ("stale update = high slippage",
      "R2 + bad status -> enrollment_hold"), and failure-recovery hints
      ("re-query the NPI registry where a worker left it unconfirmed") ->
      REJECT. RULE: sub-task descriptions carry SCOPE + INPUTS + OUTPUTS +
      COORDINATION ONLY. All domain method, thresholds, tier logic, and
      recovery steps live in instruction.md or the input_artifacts rulebook
      (equally visible to SA and MA) -- NEVER in the decomposition.
  L3. [QD-07.13 llm_judge_input_not_truncated] When the LLM judge scores >=50%
      of the reward, per-item caps (e.g. CARD_CAP=1500) silently truncated
      scored content (~30% of most cards cut) -> REJECT. RULE: any truncation
      cap applied to content the LLM grades must be large enough to hold a
      COMPLETE unit (match/raise it to the deep cap and apply it UNIFORMLY to
      all units), or compute those items deterministically on the full text.
  L4. [QD-01.10 real_world_data_only] sources.json labelled inputs
      "(declared-synthetic)" -> REJECT (synthetic data is NEVER acceptable,
      no matter the justification). RULE: every input artifact is REAL (real
      registries, real documents, real public data). Never ship, and never
      LABEL, anything as synthetic/declared-synthetic.
  L5. [QD-05.5 dag_depth_at_least_2 -- declared vs realized] task.toml /
      decomposition.yaml declared dag_depth=6 but the orchestrator spawned
      every stage directly, so the REALIZED depth was ~3 -> REJECT for the
      mismatch. RULE: declared dag_depth / dag_width / estimated_sub_agents
      must MATCH the realized MA spawn tree. After the MA run, count the
      actual spawn levels/children and reconcile task.toml + the
      decomposition header to the realized structure (or restructure the
      orchestrator so the declared chain is actually realized).
  L6. [QD-03.5 rubric_weights_no_gap_engineering -- WARN] A depth-check
      docstring said thresholds were "calibrated between an observed
      saturated single agent and a swarm" -> WARN (reads as gap-engineering).
      RULE: keep flat one-point items; justify every threshold as a genuine
      task requirement; never leave a comment/variable naming a threshold as
      tuned to the SA/MA differential.
  L7. [QD-09 / QD-07 quality -- WARN, fix before ship] MA itself failed hard
      checks it should pass (verbatim-excerpt match rate below the 0.80
      threshold; missed a cross-site canonical merge) and a binary fail-closed
      0.0 for SA overstated the gap. RULE: after the MA run, CONFIRM MA
      actually passes the depth/grounding checks (tighten sub-agent prompts to
      copy source excerpts VERBATIM, not paraphrase); prefer proportional /
      per-unit points over one binary gate so the score reflects real content.
  L8. [QD-09.5 llm_infra_failure_not_zero -- Batch-16 §3c, UPDATED] 9/16
      verifiers forced reward=0.0 when the LLM grader was unreachable (missing
      key / network / parse fail) -> a perfect submission scored 0, and because
      SA and MA both collapsed to 0 the gap was silently erased -> eval-integrity
      REJECT. RULE: an LLM-call infra failure is NOT a content judgement and
      must NEVER be scored 0 (item or whole reward). Preflight the key/
      connectivity; retry (>=5); if still failing, emit an EXPLICIT INFRA-ERROR
      SENTINEL (reward=null / raise / status="INFRA_ERROR"), mark the run INVALID,
      fix the verifier, and RERUN. Never a silent 0.0, never a non-zero fallback;
      fail-open to the deterministic component only when the LLM is a minor slice.
  L9. [QD-10 structure_only_verifier -- Batch-16 TL;DR] A verifier grading only
      shape (counts / headers / JSON keys / chart-exists / length / regex) lets
      an agent type anything in-structure and score ~1.0 -> REJECT. RULE: every
      deliverable and claim in instruction.md needs a SUBSTANCE check (values vs
      a real reference, resolved citation URLs, IDs vs a frozen snapshot,
      verbatim-quote round-trip, coverage vs ground truth) plus LLM-judge checks
      where quality needs reading; tests must cover EVERYTHING the instruction
      asks, not a structural subset.
  L10. [QD-05.5 metadata_from_realized_trajectory -- Batch-16 §2/§6] Metadata
      left at pre-run estimates: `why_multi_agent` restated the a-priori
      hypothesis and dag_depth/dag_width didn't match the spawn tree (6 of 12
      "Hierarchical" samples actually ran flat depth-2) -> metadata REJECT.
      RULE: after execution_logs exist, REWRITE `why_multi_agent` from the ACTUAL
      SA trajectory (name the real failure: timeout / premature completion /
      attention degradation / fabrication), and set dag_depth/dag_width to the
      OBSERVED MA spawn tree (count real spawn levels + widest level).
  L11. [QD-03.5 near_miss_raise_difficulty_not_reweight -- Batch-16 §1] A real
      substance-verified gap landed at 23-28 pp because SA banked a partial-credit
      floor (0.60-0.75) on the scriptable/mechanical backbone while collapsing on
      the hard reading core. RULE: fix by RAISING DIFFICULTY (more sources under a
      tighter budget, harder non-scriptable core, more hard checks BY COUNT, fewer
      mechanical ones) so SA's floor drops -- do NOT discard the task and do NOT
      reweight the backbone (weighting is a hard reject, ledger B / no-weightage).

============================================================
LESSONS LOG (BUILD -> SHIP) -- CAPTURE & REUSE (living, append-only)
============================================================
>>> START HERE IF YOU ARE BEGINNING A NEW TASK: read
>>> `HANDOFF_NOTE_next_task_design.md` (same folder) FIRST. It consolidates the
>>> seven dead designs, the exact kill numbers, the five hard design
>>> constraints, the pre-build gate battery with thresholds, and the ONE
>>> mechanism that actually produced a large gap (scale + output volume, gap
>>> 0.5109). This log is the raw append-only detail behind that note.

This is the running log of issues hit during the process, from build to
ship, so we never repeat them. RULE (STANDING DUTY 0 / CAPTURE & REUSE):
every time you hit an issue -- a gate failure, a rejected review, a
false-failure, a gap that would not open, a browsing/harness gotcha, a
reviewer comment, a wasted rerun -- append ONE task-independent line here.
READ this whole log (plus 05_feedback/Feedbacks.txt, 05_feedback/LLM_Review_Issues.txt, and
05_feedback/batches/MAS_Client_Feedback_Document_2026-07-17.txt) BEFORE starting each new task and design
around every entry. Format: `date | stage | issue | fix / rule going
forward`.
- 2026-07-09 | Gate 3 / Phase 6 | SA scored >= 0.90 on the first run because
  the rubric graded PRESENCE (files/sections exist) not CORRECTNESS | grade
  values against a real reference; load the checklist toward hard
  correctness items; run the PROJECTED-GAP CHECK on fixtures before any live
  run.
- 2026-07-09 | Gate 3 | good rubric but SA ~= MA because the corpus was
  small enough for one agent to finish alone | SCALE the unit count past one
  agent's budget (100-200+ units / 20+ chapters / 120+ counties) -- size,
  not a new check (rubric deck case 4).
- 2026-07-09 | Phase 6 | hours wasted re-running SA (2h+ each) nibbling the
  score down after shipping a too-easy task | design HARD from the start
  (DIFFICULTY & GAP TARGETS: SA<0.30 / MA 0.70-0.90 / gap>0.23); after the
  tuning budget, invoke the ALTERNATE-USE PIVOT instead of more SA reruns.
- 2026-07-09 | Gate 3 | reward multiplied factors and/or derived the answer
  key from the agent's own output -> scores collapsed and became unfair |
  ADD points, never multiply; freeze the reference; never derive the key
  from the submission (rubric deck case 3).
- 2026-07-10 | Gate 3 | the deterministic DEPTH-OF-COVERAGE band (distinct-
  prose count / per-unit grounding / TAIL grounding, scored on the FULL output)
  is the most reliable NATURAL gap lever -- APPROVED task hit SA 0.633 / MA
  0.933 / gap 0.30 with it | add ~6-10 such full-text deterministic checks
  (SA<0.30 lever #5); frame each threshold as a genuine task requirement,
  never "calibrated to the SA/MA gap" (QD-03 flags that).
- 2026-07-10 | Gate 3 / verifier | QG REJECT: one LLM judge call scored all
  items and controlled >60% of reward (QD-03.3) | split the LLM rubric into
  >=3 INDEPENDENT judge calls, largest <60%; push items into the deterministic
  band. See QG REJECTION LEDGER L1.
- 2026-07-10 | Gate 4 | QG REJECT: decomposition.yaml leaked HOW (running-total
  algorithms, tier/threshold definitions, ordering + recovery hints) (QD-06.6)
  | sub-tasks carry SCOPE + INPUTS + OUTPUTS + COORDINATION only; all method
  lives in instruction.md / the input_artifacts rulebook. See LEDGER L2.
- 2026-07-10 | Gate 3 / verifier | QG REJECT: LLM-judge input truncated below a
  full unit while judge weight >=50% (CARD_CAP=1500 cut ~30% of most cards)
  (QD-07.13) | caps on graded content must hold a COMPLETE unit and apply
  uniformly, else score that unit deterministically on full text. See LEDGER L3.
- 2026-07-10 | Gate 0-1 | QG REJECT: an input was labelled "(declared-
  synthetic)" (QD-01.10) | every input is REAL; never ship or label synthetic
  data. See LEDGER L4.
- 2026-07-13 | client reject / rework | a stacked DEPTH band of graduated
  aggregate thresholds (0/8 for SA vs 8/8 for MA) whose docstring said
  "calibrated between an observed saturated single agent and a swarm" was
  rejected: cutoffs placed BETWEEN the two runs = post-hoc calibration, and that
  one block was ~90% of the gap | make depth PROPORTIONAL: one flat point per
  unit of real work (per graded case/store/county), score = count grounded, NO
  aggregate cutoff. Never leave "calibrated" in a comment; never place a band
  between the observed SA and MA scores.
- 2026-07-13 | client reject / rework | making the depth band proportional
  COLLAPSED the gap (SA 0.63->0.80, MA 0.93 unchanged, gap 0.30->0.13): once the
  cliff was removed the two runs were nearly tied on substance (19 vs 20 of 22
  LLM items, both failing the SAME hard items) and differed only in grounding
  DENSITY (35 vs 48 of 51) | grounding-density alone rarely carries a >0.23
  HONEST gap. Verify the gap survives PROPORTIONAL scoring on fixtures BEFORE
  shipping; if it does not, the fix is harder CONTENT (make SA's routing/decisions
  fail, not just its density), not tuned cutoffs. A depth "band" that looks like a
  natural lever can be a hidden cliff -- audit whether SA earns partial credit.
- 2026-07-13 | client reject / rework | ~4-5 of 25 items were pure presence
  (cards/rows/sections/log exist) -> ~16-20% earnable by well-shaped FABRICATED
  output | convert presence items to CORRECTNESS-GATED items (present AND the
  VALUES match the frozen facts/injected tables), but gate each on a DISTINCT
  signal -- do NOT stack the same root-cause failure (e.g. missing verbatim
  archive) across multiple items; one error hits exactly one additive point.
- 2026-07-17 | client feedback (Batch-16 §3c) + team directive | 9/16 verifiers
  FAIL-CLOSED to reward=0.0 when the LLM grader was unreachable (missing key /
  network / parse fail) -> a perfect run scored 0, SA+MA both collapsed to 0, and
  the SA<->MA gap was silently erased (config failure indistinguishable from a bad
  model) | an LLM-call infra failure is NOT content: preflight key/connectivity,
  retry (>=5), then emit an EXPLICIT INFRA-ERROR SENTINEL (reward=null / raise /
  status="INFRA_ERROR"), mark INVALID, fix + rerun -- never a silent 0.0, never a
  non-zero fallback; fail-open to the deterministic part only for a minor LLM slice.
  REPLACES the old "fail-closed to 0.0" guidance. See LEDGER L8.
- 2026-07-17 | client feedback (Batch-16 TL;DR) | structure-only verifiers let an
  agent type anything in-structure and score ~1.0 (bad training signal) | every
  deliverable + claim in instruction.md needs a SUBSTANCE check plus LLM-judge
  checks where quality needs reading; tests must cover EVERYTHING asked, not a
  structural subset. See LEDGER L9.
- 2026-07-17 | client feedback (Batch-16 §3a) | single giant LLM call grading a
  huge rubric dump = unjustifiable/unstable reward-hack risk | decompose into >=3
  independent LLM judge calls (one per deliverable/theme), no single call >60% of
  reward. Reinforces QD-03.3 / LEDGER L1.
- 2026-07-17 | client feedback (Batch-16 §2/§6) | metadata left at pre-run
  estimates: why_multi_agent restated the hypothesis and dag_depth/dag_width
  didn't match the realized spawn tree (6/12 "Hierarchical" ran flat depth-2) |
  after execution_logs exist, rewrite why_multi_agent from the ACTUAL SA
  trajectory (name the real failure) and set dag_depth/dag_width to the OBSERVED
  MA spawn tree. See LEDGER L10.
- 2026-07-17 | client feedback (Batch-16 §1) | real substance-verified gaps
  landed at 23-28 pp because SA banked 0.60-0.75 on the scriptable backbone;
  client suggested "reweight" -- but weighting is a hard reject for us | fix by
  RAISING DIFFICULTY / more hard checks by COUNT (not by weight): shrink SA's
  partial-credit floor so the honest gap opens. See LEDGER L11.
- 2026-07-20 | Guidelines v1.1 / Phase 2.1 onboarding | structure-only
  verifiers still shipped -> client wants three-dimension verifiers | EVERY
  verify.py must contain static + reward-hacking + partial-oracle checks;
  structural-only is auto-reject. Build a partial oracle (hand-verify a
  head/middle/TAIL SAMPLE of units) and compare sampled values to catch
  fabrication. See P21-4.
- 2026-07-20 | Guidelines v1.1 / Phase 2.1 | separate judge.py / verifier.py
  files caused naming inconsistency + the client disliked the binary
  executable-vs-llm-judge split | ONE grader `tests/verify.py` (test.sh
  invokes it, writes /logs/verifier/reward.txt); combine deterministic + inline
  LLM checks in it; no judge.py at tests/ root. See P21-2.
- 2026-07-20 | Guidelines v1.1 / Phase 2.1 | client needs a human-readable
  rubric to learn each verifier fast | ship `tests/rubric_manifest.json` as a
  1:1 mirror of verify.py -- 3 categories, 5 fields per entry, weight:1,
  sequential numbering, total_checks matches manifest + code. Missing manifest
  = QG reject. See P21-3.
- 2026-07-20 | Guidelines v1.1 / Phase 2.1 | agents wrote correct output to the
  wrong folder -> false failures | fix the package contract: inputs under
  environment/input_artifacts/, outputs to an EXACT /logs/agent/... path shared
  byte-identically by instruction.md, manifest agent_output_path, and verify.py.
  See P21-1.
- 2026-07-20 | Guidelines v1.1 / Phase 2.1 | tasks solvable from pretraining
  memory (famous textbooks / classic cases) | use RECENT / less-canonical
  sources and force the agent to read the supplied /input_artifacts/ evidence;
  a strong answer produced without opening the sources = reshape the task.
  See P21-7.
- 2026-07-20 | Guidelines v1.1 / Phase 2.1 onboarding call | client moved to
  EVAL-data calibration | target SA very low (~0-10%) AND MA meaningfully
  challenged (~20-30%, not near-perfect); a near-perfect MA now means the
  task/rubric is too easy. Push MA down with a ROBUST verifier, never with a
  bad decomposition. Exact automated threshold still being reconciled by client.
  See DIFFICULTY & GAP TARGETS.
- 2026-07-20 | Kimi-CLI limitation analysis | context for why OpenCode | Kimi-CLI
  caps: DAG depth 1 (role guard), 4 concurrent bg agents, invisible bg
  trajectories, 15-min bg timeout. OpenCode removes these; design to OpenCode
  (dag_depth>=2, 20-50+ agents, full ATIF capture). See P21-9.
- 2026-07-21 | swarmbench-harness README | run workflow changed: no local
  Harbor/Docker, no personal Fireworks key | use the `mascloud` CLI (pipx
  install mascloud_client, `mascloud login`, `mascloud run <folder> --mode
  single|multi`); runs execute on the managed cloud (Harbor+Daytona), stream
  live, and drop `<task>-single.zip` / `<task>-multi.zip` result bundles with
  fresh execution_logs/ beside the folder. Merge both into the delivered
  execution_logs/. `mascloud runs` (shows Today: X/6 + per-run model) /
  `mascloud download <run_id>` (kept 24h) / Ctrl-C cancels. Old local flow
  lives in the harness `old_method/` only.
- 2026-07-21 | swarmbench-harness README | agent model is assigned server-side
  (usually Fireworks Kimi K2.6 / kimi-k2p6; no trainer flag) | the verifier's LLM
  judge MUST be a different FAMILY -> never Kimi/Moonshot/K2; use Claude or a
  non-Kimi Fireworks-hosted model. (Clarified 2026-07-23: under load, multi may
  auto-switch to kimi-k2p7-code -- still Kimi-family; see newer lesson.)
- 2026-07-21 | swarmbench-harness README | raw_trajectory naming | single run
  has `orchestrator_*.json` only; multi run also has one `subagent_*.json` per
  spawned subagent -- the presence of subagent_* files is the concrete proof
  the swarm spawned; verifier reward is at `verifier/reward.json`.
- 2026-07-21 | swarmbench-harness README | mascloud exposes no per-run model or
  timeout override flag | the long-horizon "generous SA cap at launch" trick
  may not be available via mascloud; timeout is governed by task.toml -- if a
  fair SA cap >= multi wall-clock is needed and no override exists, escalate
  rather than starve SA. (Model may still auto-switch server-side under load;
  that is not a trainer-controlled override.)
- 2026-07-21 | claim-time task spec | flow now starts from a pre-filled claim
  record, not a self-invented idea | build FROM the spec (query/sources/output
  paths/test_design/hardness) and fill the NA deliverable fields; map
  test_design -> the 3 verify.py categories; report the five fixture rewards
  (gold/empty/shallow/hollow/fabricated) as discrimination evidence. See
  CS-1..CS-4.
- 2026-07-21 | claim-time task spec | the claim's test_design says "structural
  checks are fail-closed preconditions" and references a full immutable
  ground-truth fixture | ADAPT, don't copy: convert fail-closed preconditions
  into ADDITIVE one-point static checks (no gate zeroes substance); use the
  full fixture only as a grader-only PARTIAL-oracle sample + reward-hacking
  cross-reference, never a whole-answer exact-match gate. See CS-3.
- 2026-07-21 | claim-time task spec | claim counts can be internally
  inconsistent (e.g. "50 sub-agents" vs 30 first-round matchups) | still own
  quality: reconcile estimated_sub_agents to decomposition sub_tasks, set
  dag_depth/dag_width from the OBSERVED spawn tree, verify source fetchability;
  escalate if the spec can't be built honestly. See CS-4.
- 2026-07-21 | local harness run (Windows) | swarm-opencode single/multi crashed
  in post-run parsing with UnicodeDecodeError ('charmap' can't decode byte 0x9d):
  agents call Path.read_text()/write_text() with no encoding, so Windows uses
  cp1252 while opencode stdout/trajectory is UTF-8 (cloud/Linux defaults to UTF-8
  so it never surfaces there) | patch the swarmbench agent readers/writers to
  encoding="utf-8", errors="replace" (single_opencode.py + multi_opencode.py);
  run local Harbor from PHASE_2/swarmbench-harness/harbor (NOT repo root or
  mascloud_client) so `uv run harbor` resolves the patched build.
- 2026-07-21 | local SA run / difficulty | scaling 64->128 units did NOT open the
  gap: a single swarm-opencode agent (kimi-k2p6) completed all 128 proposals in
  ~16 min and scored 0.7956 (strong on structural + most judgment; only weak on
  duplicate detection 0.25/0.33 and matchup-reasoning judge 0.0). SIZE alone is not
  difficulty when one agent still finishes within budget | make the task hard by
  JUDGMENT DENSITY / cross-unit interdependence that one agent cannot do well at
  scale (not just more units); measure the REAL SA score early (score the completed
  agent output with verify.py directly -- fast, no re-run) instead of trusting the
  fixture projected-gap; don't burn the ~2h MA run once SA >> 0.30 (gap can't reach
  0.23). Fixture self-test (good=1.0, gap 0.556) badly over-predicted the real gap.
- 2026-07-23 | Phase 6 / mascloud | client update: all shipping runs through MAS Cloud
  Run going forward; daily quota = 6 submissions/trainer (midnight UTC reset);
  every submit counts regardless of outcome | BEFORE each launch run
  `mascloud runs` and read `Today: X/6 runs used`; finish fixture projected-gap +
  local verify.py first; treat SA+MA as 2 slots minimum; avoid speculative
  reruns. If consistently capped and you need more for multi-task days, request a
  higher quota via Ruturaj's form (top-performer / efficiency evidence).
- 2026-07-23 | Phase 6 / mascloud | `mascloud runs` now lists the model per run;
  usual agent is kimi-k2p6, but under high concurrent load new MULTI-mode runs may
  auto-switch to kimi-k2p7-code (server-side rate-limit protection; no trainer
  action) | do not treat a different listed model as a task defect; both are
  Kimi-family so the LLM judge must still be a DIFFERENT family (never
  Kimi/Moonshot/K2). Compare retries only after checking which model each run used.
- 2026-07-27 | Gate 1 / premise test | a cross-item obligation is NOT automatically
  fan-out-resistant: measured a Falcon AD-status-review design where a scripted fan-out
  (162 independent extraction calls, then determinations + policy + consistency computed in
  Python) scored 13/14 = 0.93 -- IDENTICAL to the ideal swarm, gap 0.00, while the cheapest
  one-shot fan-out still scored 0.71 | screening question before writing any check: "could I
  satisfy this with a for-loop over extracted fields?" If yes it is a free point for a scripted
  attacker, not a coordination measurement. Consistency checks, precedent-citation checks and
  rollup-reconciliation checks all fail this test. Only state that CANNOT be reconstructed by a
  script resists fan-out. See PREMISE_TEST_FINDING_falcon_ad_review.md.
- 2026-07-27 | Gate 1 | "rounds / dependency-carrying levels" is not a fan-out defence either
  (kickstart section 2 overstates it) -- a script wraps its worker pool in a loop over levels and
  threads the carried state through the next round's prompts | the defence is the FORM of the
  carried state, not the existence of stages: compact structured state (id sets, resolved graphs,
  class indexes, budgets) is threadable and therefore scriptable.
- 2026-07-27 | Gate 1 | do NOT harden by requiring retroactive revision / inductively-amended
  policy: an agent that reads all instances before writing the rule legitimately needs no
  amendment, so the requirement penalises the BETTER method and is vacuously satisfiable when
  nothing forces a revision | process-prescriptive checks are manufactured gaps; grade outcomes,
  never the order in which the agent reached them.
- 2026-07-27 | Gate 0 / harness | the MA runtime is OPENCODE, not Kimi-CLI -- `kimi-k2p6` is the
  MODEL. Sub-agents are full tool-using agents (`general` may spawn further, `explore` is a leaf
  with `task` hard-denied) with Read/Grep/Glob/Bash/Write/Edit, so real dag_depth >= 2 is
  available | design to OpenCode; the Kimi-CLI limitation memo describes a framework this
  benchmark does not run. Verify against
  `swarmbench-harness/harbor/src/harbor/agents/installed/swarmbench/multi_opencode.py`.
- 2026-07-27 | Phase 1 / sources | federalregister.gov `raw_text_url` and `full_text/text/...`
  are bot-walled and return a "Request Access" HTML page even with a browser UA -- silently, with
  HTTP 200 | fetch the identical document from
  `https://www.govinfo.gov/content/pkg/FR-<pubdate>/html/<fr_doc_number>.htm` (no key, no wall).
  Always assert on CONTENT (expected keyword present), never on status code, when freezing a
  corpus.
- 2026-07-27 | Phase 1 / extraction | parsing an AD's own number as the most frequent
  `AD YYYY-NN-NN` mention in its text is wrong -- a superseding AD cites the AD it replaces more
  often than it names itself, which produced 22 duplicate primary keys and hid 63 of 74 real
  supersession edges | anchor identity extraction on the document's structural heading
  (`^<number> <Manufacturer>: Amendment 39-...`), and always assert primary-key uniqueness on a
  frozen corpus before designing checks on top of it.
- 2026-07-27 | Gate 1 / premise test 2 | "shared mutable state under contention" (20 airframes vs
  40 saturated maintenance-line slots) was the last shape believed to make fan-out actively
  HARMFUL -- a ~30-line deadline-sorted greedy allocator scored 7/7 = 1.00, tying the ideal swarm,
  gap 0.00 | contention is a solver problem, and solvers are exactly what a scripted attacker is
  best at. Do not nominate contention as a fan-out defence.
- 2026-07-27 | Gate 3 | contention/capacity checks are COVERAGE-BLIND by construction: "no double
  booking" and "capacity respected" are easiest to satisfy by committing almost nothing, so a
  truncated serial agent scored the same as the cheap fan-out | any check of the form "no
  violation among what you committed" must be paired with a coverage denominator over the REQUIRED
  population, or it pays a partial run full credit.
- 2026-07-27 | Gate 0 / benchmark validity | **RESOLVED 2026-07-30 — SUPERSEDED, do not design
  around this.** The original finding was that both arms are programs with LLM-oracle access in the
  same container with the same credential, shell and tools, so their COMPUTATIONAL capability is
  identical. The underlying platform issue has since been fixed and the one observed instance
  (`_runs_b1b7/SA1`, a single agent self-issuing parallel calls) is treated as a one-off exception |
  do NOT carry this into new tasks as a live caveat or spend design effort defending against it. The
  durable half of the lesson still holds and is worth keeping: prefer a rubric whose reward sits in
  interpretation rather than in coverage alone, because coverage is the component any parallelism
  buys most cheaply.
- 2026-07-30 | QG draft review / GROUND-TRUTH LEAK VIA THE RULEBOOK'S OWN WORKED EXAMPLES -- the
  single highest-cost defect of this build, and it came from trying to be HELPFUL | the binding rules
  doc that ships in the agent's image illustrated each field spec with an excerpt lifted verbatim from
  a directive in the SCORED corpus. That is two failures at once: it discloses those documents'
  answers (QD-04.1), and it makes the rulebook a grep INDEX into the corpus (QD-04.7) -- `grep -rl
  "<example phrase>" ad_texts/` returns the one file, and several graded fields can then be read off
  it without reasoning. The reviewer found 11 documents by sampling; a scanner found 25 examples
  exposing 24 of 107 | when any rules/spec document ships beside a scored corpus, SCAN every example
  in it against that corpus before shipping, and wire the scan into the static checks so an example
  edited later for clarity cannot reintroduce the leak. Three detection rules, because one naive
  "is this string in the corpus" test both over- and under-reports: (a) COPIED PROSE -- any window of
  >=6 words / >=30 chars present in the corpus; do NOT flag shorter windows, since across ~100
  documents of one genre ordinary phrases like "remove each" land in exactly one document by pure
  chance and flooded the first run with 46 false alarms; (b) IDENTIFIERS -- any digit-bearing token
  >=4 chars (record numbers, foreign ids, part/bulletin numbers, codes), which are locators at ANY
  length; (c) WHOLE EXAMPLE -- catches short lifted phrases too brief to trip (a). Also test
  FRAGMENTS, not just whole examples: the worst offender appeared nowhere verbatim, yet two words
  inside it pinned one document.
- 2026-07-30 | QG draft review / the leak fix must not delete the FIELD DEFINITION with the leaked
  example | the same document must name each field's value domain and triggers (`airplanes`,
  `Final rule; correction`, `before further flight`) or the fields become undefined and completeness
  fails in the other direction. Those strings are in the corpus too | keep an explicit DEFINITIONAL
  allow-list in the scanner with a written justification per entry, and draw the line at: does this
  string state a rule that applies UNIFORMLY to the whole corpus (keep), or does it illustrate ONE
  record's answer (rewrite). Bonus finding: replacing four real "population is zero" phrasings with
  the RULE behind them made the field harder in exactly the right way -- semantic reading instead of
  phrase matching -- so leak removal can raise task quality rather than cost it.
- 2026-07-30 | QG draft review / A LENIENT FALLBACK IS AN EXPLOIT WHEN THE COMMON OUTPUT SHAPE
  TRIGGERS IT | quote-grounding attributed each quotation to the nearest preceding HEADING and, when
  no heading resolved, fell back to testing it against the WHOLE concatenated corpus. A submission
  that wrote flat bullets under two group headings instead of one heading per record -- ordinary LLM
  output economy under batching pressure, not an adversarial shape -- never set an attribution, so
  any verbatim sentence passed as evidence for any record | never ground evidence against a
  corpus-wide union. Attribute by the IDENTIFIER wherever the submission names it (heading, bullet or
  sentence), take the FIRST resolvable identifier on the line (reconciliation prose leads with the
  acting record and then names the one it acts on), and score an unattributable quote ZERO. Measured:
  laundered 1.000 -> 0.667, honest flat-bullet log 1.000 (it had been losing credit under the
  heading-only rule), so the strict fix was also the FAIRER one. Rate an exploit by whether an HONEST
  agent's natural output reaches it, not by whether an attacker would bother.
- 2026-07-30 | QG draft review / `verifier_type` FOR A HYBRID GRADER IS GENUINELY AMBIGUOUS AND I
  FLIPPED IT TWICE | authoring guidance says `executable` whenever verify.py owns the scoring "even
  with inline LLM checks"; the quality gate reads `executable` as a promise that NO correctness
  verdict depends on a model and hard-fails a declared-executable verifier that calls one. Both
  readings are defensible and there is no third value | declare `llm-judge` if ANY verdict comes from
  a model, because over-disclosure is the safe error -- `llm-judge` warns the reader, `executable`
  conceals. Document the deterministic/judged split in `task.toml` and a manifest note so the
  minority-LLM reality is visible, encode the chosen reading in the local static check WITH the
  conflict written down so it is not silently re-litigated, and do NOT "fix" it by deleting the
  judges: prose deliverables must not be scored by exact string matching, so that trades one QD
  failure for another.
- 2026-07-30 | QG draft review / DECOMPOSITION PROSE IS AUDITED AS A CONTRACT, not as flavour text |
  two nodes were failed for claiming the same determination with no disambiguating clause, and two
  `depends_on` edges were failed for contradicting their own descriptions -- one node claimed to
  output a "merged register" while sitting UPSTREAM of the workers whose rows it would merge, and an
  auditor checked an artifact produced by a node it did not depend on | every verb in a node's
  description is a claim about that node's I/O. Split overlapping nodes along a real seam (one
  RESOLVES a shared map once, the other APPLIES it per record) and add the explicit "consumes X's
  resolved output only" clause; then re-read each description asking "which node produces every noun
  I just claimed to consume, and is it in my depends_on".
- 2026-07-30 | QG draft review / the rubric manifest is checked line-by-line AGAINST THE CODE, and my
  drift was one word | an entry described a score as the "Mean of" two sub-scores where the function
  returns `min(...)` -- left over from a hardening pass that changed the aggregation and updated the
  docstring and the sibling field but not that sentence | after ANY change to an aggregation, grep the
  manifest for the OLD metric word (`mean`, `average`, `macro`) and fix every hit; a stale metric word
  is read as a false description of the scoring, which is a reject on its own.
- 2026-07-30 | QG draft review / FAILING CLOSED IS NOT ENOUGH -- the zero must be LABELLED | a
  top-level exception handler wrote a bare `{"reward": 0.0}` while the per-check loop tagged its own
  failures with `infra_failure`, so an infrastructure crash was indistinguishable from a submission
  that genuinely earned nothing | every fail-closed path must write the same status/`infra_failure`
  tag as every other, so a reader of the reward file can tell a broken verifier from a bad answer.
- 2026-07-30 | tooling / THE IDE SILENTLY REVERTED A FILE I HAD JUST EDITED, and two tools disagreed
  about what was on disk | seven successive edits to one file were reported applied and were visibly
  applied (a fresh Python process read the new content), then a stale editor buffer flushed over them
  and the file was byte-identical to the original again, while the search index kept serving the old
  text | after any batch of edits to a file that matters, READ IT BACK FROM DISK IN A SUBPROCESS
  (`python -c` printing markers), never trust the edit tool's success report or a cached search
  result, and prefer one whole-file write over many small edits when a file has been seen to revert.
- 2026-07-30 | integrity / shipped claims | `task.toml` asserted the deciding Exceptions paragraph
  sat "often several thousand characters" from the compliance paragraph. Measuring it found a MEDIAN
  OF 429 -- the claim was qualitatively wrong and had propagated into `rubric_manifest.json` and
  `decomposition.yaml`. A reviewer can check a claim like that against the corpus in minutes | every
  quantitative statement in reviewer-facing files must come FROM a script, not from intuition formed
  while reading samples. Measure, then write the number. The correction also improved the argument:
  the real difficulty was not distance but VARIANCE -- 17 distinct phrasings over 59 directives with
  14 occurring exactly once -- which is a far better justification for a cross-boundary resolver
  tier than "it is buried" ever was.
- 2026-07-30 | packaging / Windows | `Compress-Archive` on PowerShell 5.1 writes BACKSLASH path
  separators into the ZIP, but APPNOTE 4.4.17.1 requires forward slashes -- a Linux `unzip` then
  produces 118 files with literal backslashes in their NAMES instead of a directory tree, so the
  harness finds no `task.toml` and no `tests/` and the task fails before the agent starts. Invisible
  from Windows, where Explorer and Expand-Archive both open it fine | never package with
  `Compress-Archive`. Zip with Python `zipfile` (always forward slashes), write an explicit
  `dir/` entry for empty directories like `execution_logs/` or they vanish from the archive, and
  ALWAYS re-open the finished archive to assert: no backslashes, a single top-level folder, only the
  six whitelisted root entries, and the corpus count matching the manifest.
- 2026-07-29 | rubric size | "add many more checks" is the wrong lever and the newest management
  deck says so explicitly (`03_design_guides/rework-common-mistakes.txt`, slide 16/19): "More checks. Stricter checks.
  A harsher judge. Anything that makes the rubric tougher is paid for equally by BOTH arms, so the
  difference between them stays exactly where it was." Slide 15 has the measured case -- a judge
  hardened from 0.875 to 0.000 on SA moved SA's total UP 0.057 | scale the WORK and the denominators
  (this task: 22 reported checks over 3,030 graded cells), and change the check MIX (easy -> hard),
  never the check COUNT. Also note the 15-25 range is stated in the task-creation prompt, NOT in the
  official Trainer Guidelines, which give no count range at all -- do not cite it as a spec limit.
- 2026-07-29 | packaging / test.sh | `test.sh` wrote only a `reward.txt` fallback when `verify.py`
  died, leaving `reward.json` absent or stale -- the two reward files can then disagree, which reads
  as an edited reward file (an automatic permanent exclusion under guidelines 3.4) | mirror the
  sanctioned executable sample's test.sh exactly: capture `${PIPESTATUS[0]}`, and on failure write
  BOTH `reward.txt` and a `reward.json` carrying `status: verifier_error`. Run the verifier with
  `python3 -B` + `PYTHONDONTWRITEBYTECODE=1` so grading cannot leave `__pycache__` in the package.
- 2026-07-29 | gap defence / scriptability | the "a single agent could just write a script" objection
  is answerable by MEASUREMENT instead of argument: build a fixture that emits exactly what a
  throwaway regex extractor recovers (sized from a pre-build per-field scriptability probe) and score
  it. On a task whose reward sits in interpretation rather than identity it scored 0.1533 with 16 of
  22 checks at exactly 0, i.e. BELOW the 0.276 of an agent that reads only a third of the corpus |
  the property to aim for is not "unscriptable" (unprovable) but "scripting scores WORSE than
  reading". State the unmeasured upper bound -- a determined attacker holding the shipped rulebook,
  which is a field-by-field spec for an extractor -- rather than implying it is defended.
- 2026-07-29 | rubric shape | shipped a rubric on flat weight 1 per check while ISSUE 06 of
  `03_design_guides/rework-common-mistakes.txt` lists "ad-hoc weights outside the agreed point values" under NOT
  ALLOWED and puts "1 for structure, 2 for reward-hacking, 3 for partial oracle" under REQUIRED |
  the optional 1/2/3 CATEGORY point scale is the SAFE default, not flat 1. Flat weighting is
  itself an off-scale choice under that table. Adopt the scale unless there is a measured reason
  not to, and state points available (sum of weights) in `reward_formula`.
- 2026-07-29 | rubric shape | decided the 1/2/3 weights by MEASUREMENT rather than by reading the
  trigger condition: recomputed every frozen fixture both ways from the per-check scores the
  verifier already writes (`weight_study.py`, ~60 lines, no verifier change, no rerun). Structural
  checks were only 2 of 22 and 5.7-9.1% of score, so the "structure is dominating" trigger did NOT
  apply -- but the weights still widened 4 of 5 separations (projected gap +0.401 -> +0.410, gold
  minus hollow +0.422 -> +0.446, and 60%-coverage minus hollow +0.091 -> +0.108) | never adopt or
  refuse an optional scoring change on argument. Per-check scores in reward.json are enough to
  replay any additive reweighting offline in seconds, so measure first and record both columns.
- 2026-07-29 | rubric shape | the fixture that lost the most to the weights was HOLLOW (-0.041,
  full coverage with every hard field stamped) -- it was the one banking undiluted structural
  credit | the weights' real benefit is separating a hollow-but-complete submission from a
  partial-but-honest one. If `shallow_60pct - hollow` is thin under flat scoring, the point scale
  widens it for free without removing or hardening a single check.
- 2026-07-29 | static checks | a self-written guard `verifier contains no \*\s*weight` blocked the
  SANCTIONED scale, and after rewriting it a naive "exactly one `* weight` occurrence" assertion
  false-failed on the harmless per-check `points` field in reward.json | forbid the SHAPE, not the
  token: assert reward is `earned / available`, that a weight only ever multiplies a single
  check's SCORE and never a total, that every weight equals its category value and none exceeds 3,
  and that verify.py's CHECKS table and the manifest weights are EQUAL so they cannot drift.
- 2026-07-29 | packaging | changing the reward denominator silently invalidated every score quoted
  in prose -- `task.toml.why_multi_agent` and NOTES.md carried nine stale fixture figures | after
  ANY scoring-shape change, grep the package for quoted rewards and re-quote from a fresh fixture
  run. A reviewer who recomputes one number and finds it stale distrusts all of them.
- 2026-07-29 | reward-hacking audit | the "hollow" fixture was not hollow: it was built from the
  GOLD reference with only the 10 hard fields overwritten, so it modelled a submission that DID
  read all 107 documents, and its 0.4465 was quietly treated as the ship-test result | build the
  no-reading attack EXPLICITLY: every required file, every required row, every header correct,
  assembled only from what is free (manifest, filenames, instruction) with nothing opened. It
  scored 0.3065 -- ABOVE the 0.2644 for honestly reading a quarter of the corpus. A fixture named
  "hollow" is not the ship test unless it was written without reading the corpus.
- 2026-07-29 | rubric metric | ROOT CAUSE of that failure: macro-AVERAGING per-class recall pays a
  non-discriminating answer 1/k of the check -- exactly 0.500 on every yes/no field -- so five
  checks handed out half a point each for stamping one value across the wave. Four more checks
  hand-rolled the same average between a "recorded where present" and a "correctly blank
  elsewhere" term, and their docstrings CLAIMED a blanket answer could not carry them | use
  WEAKEST-per-class F1, not mean-per-class recall: precision charges every misclaim and the lowest
  class sets the score, so a constant answer scores 0 while an honest partial read scores MORE
  than before (~0.40 vs ~0.25) because its precision is perfect. Whenever a docstring says "both
  directions are scored so a blanket answer cannot carry this", check the arithmetic actually
  takes the MINIMUM -- averaging two directions guarantees the opposite.
- 2026-07-29 | rubric metric | self-consistency was worth 2 full points: the cross-file check paid
  1.000 for three files agreeing on the same INVENTED AD number, which is the cheapest possible
  attack (write one fabricated row, copy it everywhere) | credit agreement only where the agreed
  value is also the CORRECT value, and skip the "no orphan rows" terms entirely when no row is
  correctly identified. Consistency among fabrications is worth zero, not full marks.
- 2026-07-29 | rubric metric | four more leaks, all the same shape -- a label scored beside a value
  that was never read: coverage counted rows keyed to the FREE document number; the reconciliation
  check paid 1.000 for emitting empty "## Retired"/"## Amended" headings; the code-scheme label
  (JASC on nearly every directive) scored independently of the code; and chain rows scored their
  authority and clock without naming the document they belong to | ANCHOR every cheap field on an
  expensive one from the same row. Ask of each sub-score: could this be written without opening
  the document? If yes, it must be counted only alongside a field that could not.
- 2026-07-29 | reward-hacking audit | the three hardening passes moved gold 0.8929 -> 0.8929 ->
  0.8929 while no-read went 0.3065 -> 0.1136 -> 0.0221 and the projected gap went 0.410 -> 0.432
  -> 0.449 | keep the gold fixture as the positive control in the SAME run as every attack
  fixture, and quote all of them together. If a hardening pass moves gold at all it broke a
  correct answer; if it does not move the attacks it was not a hardening pass. The gap widening
  was a side effect of honest hardening, which is the only legitimate way to widen it.
- 2026-07-29 | packaging | after the metric change, 15 rubric_manifest entries were factually
  wrong and one advertised the DEFECT as the defence ("a blanket 'none' scores 0.5 ... neither
  blanket answer can carry the check") | the manifest is a scoring CONTRACT, not documentation:
  grep it for the name of any metric you change and re-derive each affected rationale. A reviewer
  reading that sentence would have found the bug before the client did.
- 2026-07-29 | positive control | the gold fixture's prose deliverable satisfied only 8 of its own
  10 LLM-judge criteria (it named no sole-source station and gave no retired-vs-amended split), and
  this went unnoticed because the judges fail closed to 0.0 without an API key -- so every local
  run reported gold's ceiling as the DETERMINISTIC max and never tested the judged half at all |
  when judges fail closed locally, the gold fixture is only a positive control for the
  deterministic checks. Write a separate offline control that tests the gold prose against each
  judged criterion's ground-truth requirement (count within tolerance, named entity present,
  required distinction drawn). Otherwise "gold = 0.89" silently means "gold cannot reach 1.0".
- 2026-07-29 | positive control | the thin gold brief was ~230 words while the rubric asks for a
  position on schedulability, immediate action, sequencing, exposure, mitigation and programme
  reconciliation -- six judged topics | size the gold prose to the number of judged criteria, not
  to what looks like enough. Ten criteria needed ~620 words; a brief short enough to skim is
  evidence the criteria were never checked against it.
- 2026-07-30 | rubric metric | A POOLING GUARD THAT DOES NOT ASSERT THE POOL'S OWN SIZE IS
  DECORATIVE, and any aggregation that takes a MINIMUM needs a population floor under every
  term. `class_accuracy` pooled classes below a floor of 3 into one rare group but never
  checked that the POOL reached the floor -- where only a single class is rare the "pool" is
  that same tiny class, so 2 documents of 107 still decided a 3-point check. Separately,
  `weakest(parts)` took a min over named groups with no floor at all, and one group had
  exactly ONE member. Five documents out of 107 could swing 13.4% of the score, and it worked
  AGAINST a correct submission, not for a cheating one | when a check returns min() or a
  weakest-class score, print every group's SIZE, not just its accuracy; assert that each
  scored group meets the floor after pooling, and fold a still-undersized pool into the
  smallest qualifying group (merge numerators and denominators so each group's own pass
  condition is untouched). Anti-hacking is unaffected -- a blanket answer fails the pooled
  group on recall exactly as it failed the small one -- while honest partial work goes UP.
- 2026-07-30 | review method | "the code handles this edge case" and "this edge case can be
  scored fairly" are different claims, and only the second one matters | for every edge case
  the verifier handles, measure HOW MANY corpus documents exercise it, then prove the exposure
  by corrupting only that group in the GOLD fixture and rescoring the real check. A class the
  corpus barely exercises is a fairness liability, not a feature. Also print the reference
  parse's own unresolved-field counts: a field the grader could not resolve is a row where
  every agent is graded against nothing.
- 2026-07-30 | integrity / A CLAIM-CHECKER THAT SCANS FOR DECIMALS WILL NOT SEE A PERCENTAGE, and
  that is exactly where a stale number hid | a `claims_recheck.py` matching `r"0\.\d{2,4}"`
  verified all 12 fixture scores while `task.toml` still described the LLM judges as "~9% of
  reward" -- true under flat weights (2 of 22 checks), wrong under the point scale (6 of 56 = 10.7%),
  and the rubric manifest had the right figure all along. Percentages, ratios and "N of M" phrasings
  need their own pass: recompute each share from the verifier's CHECKS table and match every
  percentage written near "of reward" / "share of the score", selecting BY CONTEXT so probe
  accuracies and profile hit-rates written as percentages do not drown the signal.
- 2026-07-30 | integrity / A CLAIM IS ONLY VERIFIED IF THE TEST A REVIEWER WOULD ACTUALLY RUN
  REPRODUCES IT | a manifest asserted a blanket answer "scores 0.0" on three checks. Two do; the
  third is a MEAN of two sub-scores, so stamping the class-valued field alone leaves the other
  sub-score intact and returns 0.5. The claim was true for the coherent version of that submission
  and false for the literal experiment, which is the one a reviewer runs. When a check aggregates
  sub-scores, state the number the obvious experiment returns AND the number the intended reading
  returns, and say why they differ -- "true under the reading I meant" is how a correct statement
  still fails a review.
- 2026-09-01 | Phase 6 / verifier | an agent-authored identifier reached an unguarded `int()` conversion inside one additive content check, aborting all checks and turning a completed trajectory into an invalid compatibility-zero payload | treat malformed agent fields as local criterion failures with explicit diagnostics; reserve whole-run infrastructure failure for verifier-owned inputs or unavailable evaluation, and regression-test representative type mismatches before live runs.
- 2026-09-02 | verifier | a `reward.json` payload carried a fifth STRING key (`scoring_formula`) alongside the four required numeric fields; Harbor's pydantic `VerifierResult` rejected the whole trial as a `ValidationError`, so a genuinely healthy `0.77` score was recorded as an infrastructure exception instead of a valid SA result | never let a string/list/dict metadata field reach the literal dict written to `reward.json` (success path AND every exception/crash-fallback path, including `test.sh`'s `printf` literals); keep exactly the four numeric fields there and put the formula/provenance only in `reward_debug.json` / `verifier_status.json` / stdout; add a one-line type-assert on every value written to `reward.json` before shipping.
- 2026-09-02 | difficulty / task hardening | a single agent scored 0.746 on a package whose "hard" corpus was actually 8 sources, several thin (~19KB) or duplicative, all from ONE regulatory family (biobank practice only), with volume floors (30 controls / 16 risks / 10 decisions) small enough for one well-run agent to fully satisfy | when re-hardening after a too-easy SA result, don't just raise numeric minimums on the SAME corpus -- swap in sources from MULTIPLE UNRELATED regulatory/practice families (e.g. add FDA tissue regs, CLIA lab-quality regs, OSHA physical-safety publications, and a deliberately non-domain-native NIST IT-continuity guide) and add ONE new required deliverable that forces genuine cross-family reconciliation (a source-grounded conflict/complementarity register citing >=2 families per row); that is what actually defeats scripting, not bigger numbers on a single-topic corpus.
- 2026-09-02 | browsing / source selection | `cdc.gov`, `stacks.cdc.gov`, `fema.gov`, and `fda.gov` ALL timed out or 403'd against a plain `requests`-style fetch with a browser User-Agent on repeated independent tries today, while `www.osha.gov`, `www.ecfr.gov`, `www.govinfo.gov`, and `nvlpubs.nist.gov` (NIST) all returned clean HTTP 200 with substantial real content on the first try | the known WAF-block list for automated verifier fetches is broader than just cdc.gov/fema.gov -- also avoid fda.gov and any stacks.cdc.gov mirror; prefer ecfr.gov/govinfo.gov for regulatory text and osha.gov/nist.gov (nvlpubs) for safety/continuity guidance, and re-verify EVERY candidate URL with the verifier's own fetch pattern (not just a browsing tool) before locking a source catalog, since two of the OLD catalog's own 8 URLs (both on dctd.cancer.gov) started intermittently timing out on re-check even though they had worked at original catalog-build time.
- 2026-09-02 | verifier / PDF sources | the original `verify.py` decoded PDF response bytes as UTF-8 text, producing unusable garbage that made every PDF-sourced excerpt nearly impossible to ground (exact-substring match against garbage never succeeds) -- this silently capped how much real difficulty a PDF-heavy corpus could add | any task whose source catalog includes `content_type: application/pdf` needs real PDF text extraction in the verifier (e.g. `pypdf`) BEFORE writing grounding checks, pinned in `test.sh`'s pip install line; raise the fetched-text retention cap well past the old ~20K-char default for multi-hundred-page PDFs, since truncating too early makes legitimate late-document excerpts fail grounding through no fault of the agent.
- 2026-09-02 | decomposition | a single synthesis sub-task was asked to emit BOTH the full control crosswalk (70 rows) AND the full risk register (36 rows) in one turn after scaling volume floors up ~2.3x from the previous version | when raising volume floors substantially, re-check every "assembly" sub-task's total output burden and split any single node whose combined row/word count materially exceeds what the smaller, already-validated version of that same node used to produce -- cheap insurance against MA-side truncation that the deterministic row-count checks would otherwise punish for the wrong reason.
- 2026-09-02 | difficulty / anti-script | raising source count and row floors does NOT stop a single agent from writing a fetch-extract-emit script: exact-substring grounding and "any two families plus three overlapping tokens" are satisfied by copying first-N paragraphs and pairing convenient IDs | if the last SA run was a script, the next hardening pass must add named operator questions whose correct source ID, locator, verbatim needle, and closed answer are held out in tests/verifier_inputs (Harbor path: Path(__file__).parent/verifier_inputs), including at least one NONE/negative probe where a keyword-related source is the wrong answer (e.g. an IT RTO is not a biobank freezer RTO); grade those cells deterministically; do not leave "conflict" credit on token overlap alone.
- (append new lessons below -- newest last)

============================================================
PROMPT CHANGELOG
============================================================
- 2026-06-26 | S1 | trigger: 2026-06-25 MAS2 onboarding call + phase2
  brief | NEW FILE | created the Phase 2 prompt: oracle->rubric,
  local->browsing, flat->hierarchical DAG, JSON->diverse artifacts,
  long->human-like instruction.md with externalized rules, engineered->
  natural gap, added Gate 0 QA idea-approval + trainer/QA dual debug +
  judge-hallucination check; preserved INTEGRITY MANDATE, SCORING
  INTEGRITY, AUTONOMY MODE, Local Quality Gate, similarity gate, and
  packaging discipline from the Phase 1 prompt.
- 2026-06-26 | S1 | trigger: DM note + approved task-idea sheet | classes
  + instruction.md + sanity gates + lessons | generalized the four
  client categories to Browsing / Long Writing / Multi-Modal / Long
  Horizon (spreadsheet is no longer its own class; Long Writing >=50k,
  target >100k tokens); hardened the instruction.md rule to FIRST-PERSON
  human prose with NO Markdown headings + the `_g_instruction_human_like`
  no-heading assertion; added the "LESSONS FROM PASSED PHASE 2 SAMPLES"
  block (real artifacts not JSON, decomposition doesn't restate the spec,
  split the produce step, parse-don't-count verifier, deterministic
  checks as judge context, load-bearing reproducible browsing,
  contamination guard).
- 2026-06-26 | S1 | trigger: DM note | coordination pattern | client
  requires HIERARCHICAL / SPECIALIST-ROUTING only; map-reduce and
  fan-out/synthesis are RULED OUT. Updated WHAT-CHANGED #3, baseline B2,
  Gate 4, MUST-NOT-DO, and added the `_g_coordination_pattern` build gate.
- 2026-06-26 | S1 | trigger: DM note | output diversity + acceptance
  criteria | added the "TWO ACCEPTANCE CRITERIA" header (real gap +
  creative real-world = no client rejection); WHAT-CHANGED #4 and the
  categories now mandate DIVERSE output formats and forbid defaulting to
  xlsx/spreadsheet (use pptx/charts/csv/video/animation/reports).
- 2026-06-26 | S2 | trigger: teammate task review | OpenCode + robustness
  | Gate 4 + Phase 3 now require `subagent_type` on every sub-task,
  `network_enabled = true` for live-browse tasks, and a non-blocking
  parallel/time-boxed verifier (artifact write must not hard-depend on
  it); added `_g_subagent_type`, `_g_network_enabled`, and
  `_g_no_blocking_verifier_tail` build gates.
- 2026-06-26 | S1 | trigger: Estifanos approval (Slack) | hosted-frozen
  sources | B3 + the passed-samples lesson now document the lead-approved
  GitHub `text_url` fallback for bot-protected / drifting / patchy-Wayback
  live sources (public host, faithful capture, manifest with URL+date+
  sha256, browsing stays load-bearing), and the browser-User-Agent
  requirement + prefer-official-API (openFDA) note.
- 2026-06-29 | S1 | trigger: official "SwarmBench Phase 2 — Trainer
  Guidelines v1.0" (2026-06-26) | full reconciliation to the authoritative
  spec | (1) SCORING: replaced the weighted-band rubric with a FLAT
  15-25 BOOLEAN checklist, one point each, reward = passed/total (no
  weightage/tiers/multipliers/caps) across the header, WHAT-CHANGED #1,
  SCORING INTEGRITY positive design, Gate 3, Phase 2/3, baseline B4, the
  passed-samples lesson, and MUST-NOT. (2) ORACLE fully removed: no
  oracle.json, no solution/, no solve.sh, no gold comparison; added
  `_g_no_oracle`. (3) DELIVERY FORMAT: rewrote Phase 0 to the strict
  SIX-ITEM root whitelist with `_trainer_artefacts/` moved OUTSIDE the
  delivered folder; folder/ZIP name `<32hex>-SWARMBENCH-<SLUG>-<DOMAIN>-
  <TASKNAME>` with SLUG==coordination_pattern; OpenCode execution_logs
  structure (single/multi-opencode-agent, opencode.txt, trajectory.json,
  raw_trajectory/, reward.txt). (4) task.toml Phase-2 schema: dag_depth>=2,
  dag_width, exact secondary_classification underscore enums,
  estimated_sub_agents==sub_tasks, human_solving_hours_estimate>=10,
  input_token_estimate, why_multi_agent, timeout bands; added gates
  `_g_folder_name_format`, `_g_six_item_root`,
  `_g_secondary_classification_enum`, `_g_estimated_sub_agents_match`,
  `_g_dag_depth_2`, `_g_env_no_scoring_content`, `_g_boolean_rubric`,
  `_g_judge_model_independent`. (5) VERIFIER split: executable verify.py
  for structured data vs llm-judge judge.py for prose; judge model must be
  a different family from the agent. (6) HARNESS/REVIEW/SUBMIT: OpenCode
  swarmbench-harness local setup (M1), Phase 4.5 now the static checks
  S-01..S-07 + Turing Draft Review (Local QG demoted to optional pre-
  check), Phase 4.6 similarity demoted to supplementary, Phase 5
  packaging + Google-Drive/Turing submission + two-trainer sign-off,
  Phase 6 gap target >= 20pp + mandatory both-trajectory review; added the
  official Trainer Guidelines as the AUTHORITATIVE reference at the top of
  REFERENCE MATERIAL.
- 2026-06-29 | S4 | trigger: sample-structure review (Updated-POC-Samples) +
  official Section 6 | environment layout | corrected the rules-module location:
  there is NO `environment/rules/` folder anywhere in the official spec or the
  four POC samples. Binding hard-rule docs ship as markdown INSIDE
  `environment/input_artifacts/` (e.g. `<name>_rules.md`, exactly like the
  EMERGPROCUREMENT sample's audit_rulebook.md), and the Dockerfile copies only
  `input_artifacts/`. environment/ contains just `Dockerfile` + `input_artifacts/`.
  Updated WHAT-CHANGED #5, Gate 2(C), Gate 3, the scaffold tree, Phase 1/3
  builders, the anti-leak grep, THINGS-YOU-MUST-NOT-DO, and the Phase-1 carryover.
- 2026-06-29 | S3 | trigger: manager guidance on long-horizon run timeouts |
  timeout calibration + Phase 6 run order | for a complex long-horizon task,
  LEAVE `[agent].timeout_sec` UNSET in task.toml (Harbor then wraps the agent
  step with timeout=None -> no cap), because trainers lose progress even with a
  2-hour cap. Run protocol: multi-agent FIRST with no timeout (record actual
  wall-clock), then single-agent baseline WITH a generous timeout applied at
  launch (>= multi's observed time) for comparison. Added a LONG-HORIZON
  EXCEPTION to TIMEOUT CALIBRATION, relaxed `_g_task_toml_table_layout` to treat
  agent.timeout_sec as optional/absent, updated the task.toml schema note (and
  clarified `[environment].allow_internet` is the real egress switch, not
  `network_enabled`), and added the run-order + fair-cap rules to Phase 6.
- 2026-06-29 | S2 | trigger: OpenCode webfetch source review + live source
  probe on a browsing task | browsing source verification | documented how
  the agent actually fetches (OpenCode `webfetch`: real Chrome UA +
  Accept-Language, Cloudflare-challenge retry with UA `opencode`, but NO
  JS execution, no browser TLS fingerprint, 5 MB cap, 30s/120s timeout;
  Shell tool can curl APIs). Added the rule to REPLAY the agent's exact
  request and inspect the BODY before locking any source -- JS-rendered
  pages return only a shell (use the JSON/AJAX endpoint or ship a
  snapshot) and login/WAF walls (302->SSO, hard Cloudflare 403) are
  unfetchable even with the right UA. Updated the passed-samples browsing
  lesson and the Phase 1 source-assembly step; concrete findings: openFDA/
  RxNav/DailyMed APIs are clean JSON for the agent, while the FDA/Orange-
  Book portals are JS-rendered and ASHP is login-walled.
- 2026-06-29 | S5 | trigger: Phase 4 QD self-audit (QD-09.5 vs the reference
  ECON-SLIDES llm-judge sample) | llm-judge fail-closed contract | corrected
  the prompt's verifier guidance, which had told trainers to use a "graded
  non-zero fallback on infra outage" and to SUM deterministic code points with
  LLM points -- both are the fail-OPEN anti-pattern QD-09.5 auto-rejects (the
  canonical sample writes reward=0.0 on missing key / dependency / LLM error /
  unparseable / no usable scores, and derives every non-zero reward solely from
  a parsed LLM verdict). Reworded HARD-FORBIDDEN #1 to forbid CONTENT gates
  only (an INFRA fail-closed-to-0 is REQUIRED, not forbidden); replaced the
  outage-fallback rule with an explicit LLM-JUDGE FAIL-CLOSED rule; rewrote the
  Gate-3 llm-judge + HYBRID bullets and the Phase-2 judge.py section so the LLM
  emits the verdict for EVERY rubric item, deterministic code only extracts/
  injects grounding evidence (never scores or contributes points), and a true
  code+LLM summed reward is only valid as `verifier_type = "executable"` (no
  LLM, structured output only -- never a prose/deck deliverable per QD-10.9).
  Applied the same fix to the drug-shortage task: rewrote tests/judge.py as a
  fail-closed pure-LLM 22-item rubric (reward = LLM-PASS/22), moved the
  self-check to _trainer_artefacts/ (stub LLM) so the shipped verifier has no
  non-LLM scoring path, restored the empty tests/test.sh (fail-closed trap),
  recalibrated AHT 12h->30h to match the 150K-token band (QD-07.4), and fixed
  dag_depth 6->7 to match the built 7-stage longest chain.
- 2026-07-08 | S1 | trigger: user directive (idea must be OUR OWN; sheet is
  a methodology reference only, not an idea source) + folder-doc audit |
  idea source + domain policy + uniqueness + references |
  (1) added WHAT-CHANGED shift #8 (pick-from-sheet -> OWN ORIGINAL idea):
  the idea for every task is the user's own invention; the tracker CSV is a
  METHODOLOGY / PATTERN reference ONLY (study how the leads shape a
  multi-node DAG, DAG depth/width, multi-stage workflows, corpus scale) and
  is NEVER picked/copied/auto-selected as the idea; added the mandatory
  UNIQUENESS clause (idea and swarm trajectory must be distinct vs sheet
  rows, approved samples, and prior tasks -- a per-task similarity check
  runs). (2) added shift #9 (domain: planning-operations PREFERRED, other
  official domains as a fallback only when the idea cannot become a strong
  planning-ops task, recorded in the DECISION LOG). (3) Rewrote GATE 0 with
  a "THE IDEA IS MY OWN" + UNIQUENESS + domain + "HOW TO SHAPE MY OWN IDEA"
  block and reframed GATE 0 step 2 + M0 + the confirmation paragraph +
  WORKING STYLE around an own, unique idea (sheet used only to learn the
  method). (4) GATE 1 candidates root in the user's own original idea (never
  a picked sheet row), each required distinct/unique; industry menu only for
  open-ended ideas; relaxed the "no two candidates share a vertical" rule.
  (renumbered header "seven" -> "nine" shifts.) (5) REFERENCE MATERIAL:
  added the previously-unreferenced folder docs -- the tracker CSV itself
  (as a METHODOLOGY/PATTERN reference only, never an idea bank to pick
  from), `Thinking in Planning-Operations` (+ its duplicate
  `planning_ops_doc.txt` noted),
  `LLM_gennerated_tasks_guidelines_video_transcript.md`, the
  `All_Hands_Meta_Multi_Agent_Swarm` 2026-07-01 notes, `Quality_dimensions_
  phase_2.md`, and `LocalQualityGate_ReviewerPrompt_Phase2.md`; fixed the
  onboarding-call reference extension (.pdf -> .txt).
- 2026-07-09 | S1 | trigger: user directive (too-easy tasks -> SA >= 0.90 on
  first run, hours wasted re-running SA; use latest guidelines + the rubric
  doc + Phase 2 QD; capture/reuse lessons) | difficulty-first design +
  rubric doc + Phase 2 QD + lessons capture | (1) VERSION: added a header
  VERSION NOTE clarifying the Phase 2 guidelines are v1.0 (latest,
  authoritative) and the "-V3" file is the OLDER Phase 1 line (superseded,
  non-scoring only); marked the Phase-1 Trainer Guidelines -V3, Phase-1 QD
  (Quality_dimensions / skills), and Phase-1 Local Quality Gate as SUPERSEDED
  in REFERENCE MATERIAL. (2) DIFFICULTY: added the "DIFFICULTY & GAP TARGETS"
  block (SA < 0.30, MA 0.70-0.90, gap > 0.23, hit by SCALE + correctness
  rubric + hard-item mix + load-bearing coordination, from the start); wired
  the targets into THE GAP GOAL and Phase 6 GAP TARGETS. (3) RUBRIC DOC: added
  `rubric_scale_presentation.pdf` as the dedicated MANDATORY rubric reference
  (five case studies); Gate 3 and Phase 2 now require reading it first and
  building a GRANULAR, DISCRIMINATIVE, correctness-not-presence rubric; added
  a Gate-3 PROJECTED-GAP CHECK on the sanity fixtures before any live run.
  (4) ESCALATION: added the ALTERNATE-USE PIVOT (scale up / re-grade for
  correctness / add depth / re-target class / park+escalate) so a stuck gap
  loop stops re-running SA endlessly; referenced it from ESCALATE-EARLY, THE
  GAP GOAL, and Phase 6. (5) QUALITY: rewrote Phase 4 to audit against the
  Phase-2 QD-01..QD-09 (Quality_dimensions_phase_2.md) instead of the
  Phase-1 QD-01..QD-13, and pointed Phase 4.5's optional local pre-check at
  LocalQualityGate_ReviewerPrompt_Phase2.md. (6) DOC MAP: added a
  DOCUMENT-TO-STAGE MAP and CLIENT-FEEDBACK/REJECTION-PATTERN references
  (MAS Client Feedback Document, MAS - All Hands Call, Common Issues,
  LLM_Review_Issues, Feedbacks); repointed the Common Issues / LLM_Review
  paths to the documentations_phase_2 copies. (7) LESSONS: added the living
  LESSONS LOG (BUILD -> SHIP) section (seeded) and a mandatory CAPTURE &
  REUSE duty in STANDING DUTY 0. Workflow, gates, and integrity/scoring rules
  unchanged.
- 2026-07-09 | S1 | trigger: user question (are the two meeting-notes docs --
  All-Hands 2026-07-01 and MAS2 Onboarding 2026-06-25 -- wired in correctly,
  since one is the rubric-creation call and the other the initial Phase 2
  requirements onboarding) | reposition + deepen both meeting-notes docs |
  (1) ALL-HANDS 2026-07-01: promoted from the "IDEA-DESIGN + CREATIVITY"
  section (a mismatch) into "Phase 2 RUBRIC-DESIGN references" beside
  `rubric_scale_presentation.pdf`, with the full operational detail the deck
  omits (content-validity not existence; weightage strictly prohibited ->
  additive points; scale the corpus when the rubric is already strong; debug
  BOTH trajectories; equal checks; hybrid URL-hit browsing; embed requirements
  in inputs; the REFERENCE-ANSWER technique). Left a creativity pointer
  (coordination-not-intelligence; no Phase-1 patterns) in the idea section.
  Wired the All-Hands + reference-answer technique into the Gate-3 "RUBRIC DOC
  FIRST (MANDATORY)" block and the Phase-6 gap-loop map entry. (2) ONBOARDING
  2026-06-25: expanded its primary-source entry into the explicit INITIAL
  Phase 2 REQUIREMENTS baseline (mission, long-horizon DAG, human-readable
  instructions, rubric-replaces-oracle, real-not-engineered gap, mandatory
  browsing + long-writing + creative-viz, the two demo shapes, the full
  prohibited list, and process discipline) and moved it to READ-FIRST at
  Gate 0 in the DOCUMENT-TO-STAGE MAP. No workflow/gate/scoring changes.
- 2026-07-10 | S1 | trigger: user questions ((a) is the HOW-to-hit SA<0.30 /
  MA 0.70-0.90 / gap>0.23 actually mechanized at creation time, not just
  stated? (b) wire the live QG_reviews/ folder in so the agent designs around
  prior LLM-QG rejections and stays current as files are added) | concrete gap
  mechanism + QG-reviews feedback loop | (1) HOW-TO: added lever #5 to "HOW TO
  HIT SA < 0.30 BY DESIGN" -- the deterministic DEPTH-OF-COVERAGE band
  (distinct-prose / per-unit grounding / TAIL grounding, scored on full output),
  the proven natural gap lever from the APPROVED task (SA 0.633/MA 0.933/gap
  0.30), with a QD-03 caution not to phrase thresholds as "calibrated to the
  gap"; updated the closing to (1)-(5). (2) QG FOLDER: added the `QG_reviews/`
  folder to REFERENCE MATERIAL as a MANDATORY per-build re-read (grows over
  time), and to STANDING DUTY 0 CAPTURE & REUSE, the DOCUMENT-TO-STAGE MAP
  (Phase 4.5 + Continuous). (3) LEDGER: added the QG REVIEWER REJECTION LEDGER
  (seeded L1-L7 from the six current reports: single-shot judge >60% (QD-03.3),
  what_not_how decomposition leakage (QD-06.6), LLM-judge truncation (QD-07.13),
  declared-synthetic data (QD-01.10), declared-vs-realized dag_depth (QD-05.5),
  calibrated-threshold WARN (QD-03.5), MA-quality/verbatim + fail-closed-cliff
  WARN (QD-09/07)), each traceable to its QD check and set to grow. (4) GATE 3:
  wired the two build-time hard rules -- split the LLM judge into >=3
  independent calls (largest <60%) and never truncate content the LLM grades
  when judge weight >=50%. (5) LESSONS LOG: added six 2026-07-10 entries. No
  workflow reordering; gates strengthened, not changed.
- 2026-07-17 | S1 | trigger: client feedback (FAIR SAGE - V2 Turing Batch-16
  Data) + team directive on LLM-judge failure handling | LLM-judge infra-failure
  reversal + Batch-16 rejection criteria | (1) FAIL-CLOSED REVERSAL: the biggest
  change -- REVERSED the prior "FAIL CLOSED to 0.0 on any infra failure" contract
  (set 2026-06-29 S5) per Batch-16 §3c, which found 9/16 verifiers silently zeroed
  a missing-key/outage run and thereby erased/manufactured the SA<->MA gap. An
  LLM-call infra failure (no key / network / API error / unparseable / missing
  item) must now NEVER be scored 0 (item or whole reward): preflight the key +
  connectivity, retry (>=5), then EMIT AN EXPLICIT INFRA-ERROR SENTINEL
  (reward=null / raise / status="INFRA_ERROR"), mark the run INVALID, fix the
  verifier, and RERUN; never a silent 0.0, never a non-zero fallback; fail-open to
  the deterministic component only for a minor LLM slice. Rewrote all four spots
  (the SCORING LLM-JUDGE rule, the split-the-judge bullet, the Gate-3
  verifier-type bullet, and the Phase-2 judge.py section). (2) NEW HEADLINE BLOCK:
  added "LATEST CLIENT + TEAM FEEDBACK (2026-07-17)" after the two acceptance
  criteria (A structure-only reject; B no-weightage reject + near-miss fix is
  count/difficulty not reweight; C no single-call rubric dump; D LLM-call failures
  never 0; E finish metadata from real trajectories; F narrow gap -> more
  complexity). (3) LEDGER: added L8 (llm_infra_failure_not_zero), L9
  (structure_only_verifier), L10 (metadata_from_realized_trajectory), L11
  (near_miss_raise_difficulty_not_reweight). (4) LESSONS LOG: added five 2026-07-17
  entries. NOTE for maintainers: the workspace .cursor/rules .mdc files still say
  "FAIL CLOSED to 0.0" and need the same reversal to stay consistent.
- 2026-07-20 | S1 | trigger: Trainer Guidelines v1.1 (2026-07-20 / Phase 2.1),
  the 2026-07-20 MAS 2.0 onboarding call + notes, the Kimi-CLI limitation
  analysis, and the latest client feedback batch | Phase 2.1 reconciliation |
  (1) HEADER: reconciled the authoritative spec from Guidelines v1.0 (2026-06-26)
  to v1.1 (2026-07-20, "Trainer Guidelines (2).txt"); added a Phase 2.1 headline
  to the version note. (2) NEW AUTHORITATIVE BLOCK "PHASE 2.1 UPDATE (GUIDELINES
  v1.1, 2026-07-20)" inserted before DIFFICULTY & GAP TARGETS, items P21-1..P21-11:
  standard package contract (input_artifacts/ + exact /logs/agent/ output paths);
  single grader verify.py (judge.py retired); mandatory tests/rubric_manifest.json
  (3 categories, 5 fields, weight:1, 1:1 mirror); three check dimensions
  static/reward-hacking/partial-oracle + content check per artifact;
  tests/partial_oracle.json grader-only sample; modular LLM judging; source
  novelty; no-unsolvable-browsing; OpenCode-vs-Kimi rationale; metadata last;
  tests/ contents. This block SUPERSEDES conflicting older text. (3) DIFFICULTY &
  GAP TARGETS: shifted to the EVAL-data calibration (SA ~0-10%; MA meaningfully
  challenged ~20-30%, not near-perfect; near-perfect MA = too easy; exact
  automated threshold reconciling) and marked the old "MA 0.70-0.90 / gap>0.23"
  numbers superseded in every active spot (termination condition, granularity,
  projected-gap check, QD-09 recap, Phase-6 gap targets). (4) PACKAGING/VERIFIER:
  updated the tests/ tree, the PHASE 2 verifier-implementation section, the Gate-3
  verifier-type block, and build_task.py renders to the single-grader + manifest +
  partial-oracle model; clarified partial_oracle.json is allowed (grader-only)
  while the full oracle stays forbidden. (5) SANITY GATES: added _g_rubric_manifest,
  _g_three_check_categories, _g_verify_py_single_grader, _g_output_path_logs_agent,
  _g_content_check_per_artifact, _g_source_novelty; amended _g_no_oracle. (6)
  LESSONS LOG: added seven 2026-07-20 entries. No workflow reordering; gates
  strengthened, not changed.
- 2026-07-21 | S1 | trigger: swarmbench-harness README (mascloud cloud runner)
  | run-workflow migration to the managed cloud | (1) OPERATIONAL PREREQS:
  replaced the local Harbor+Docker+own-key setup with the `mascloud` CLI (pipx
  install mascloud_client, `mascloud login`, token in ~/.mascloud/config.json,
  no local Fireworks/Daytona key). (2) MANUAL-NEEDS: rewrote M1 (mascloud CLI
  install/login, not local Docker build) and M4 (`mascloud run --mode
  single|multi`, result zips, `mascloud runs`/`download`/Ctrl-C). (3) PHASE 5:
  execution_logs now merged from the `<task>-single.zip` / `<task>-multi.zip`
  result bundles; scrub step softened (no local key) but kept as a defensive
  preflight. (4) PHASE 6 renamed HARBOR RUNS -> MASCLOUD RUNS; added the run
  commands, fixed server-side model (Kimi K2.6), single/multi agent
  differences, and a note that mascloud has no documented model/timeout
  override flag (escalate if a fair long-horizon SA cap is unavailable). (5)
  EXECUTION_LOGS TREE: updated raw_trajectory to orchestrator_*.json (single) +
  subagent_*.json (multi) and reward.json. (6) JUDGE INDEPENDENCE: the agent is
  now fixed to Fireworks Kimi K2.6, so every judge-model rule now says NOT
  Kimi/Moonshot/K2 -- use Claude or a non-Kimi Fireworks-hosted model (updated
  all four spots + _g_judge_model_independent). (7) LESSONS LOG: added four
  2026-07-21 entries. No gate reordering.
- 2026-07-21 | S1 | trigger: new claim-time task spec provided by the labeling
  tool on task claim | spec-driven build flow | (1) NEW SECTION "CLAIM-TIME TASK
  SPEC (CS-1..CS-4)" inserted after the PHASE 2.1 UPDATE block: the flow now
  starts from a pre-filled claim record (query, decomposition_pattern, tools,
  real_sources_or_entities, expected_outputs /logs/agent paths, verification_shape,
  test_design blueprint, hardness_strategy, aht_estimate_arithmetic,
  expected_subagent_count, similarity_score, decision) -> build from it and fill
  the NA deliverable fields (instruction_md, verifier_type/path, ground_truth/
  gold_output paths, verifier_code_preview, lint + selftest status, and the five
  fixture rewards gold/empty/shallow/hollow/fabricated). CS-3 maps test_design ->
  the 3 verify.py categories and RECONCILES its "fail-closed preconditions" +
  full-oracle language to the additive one-point-per-check / partial-oracle rules
  (adapt, never copy raw). CS-4 keeps trainer ownership (internal-consistency,
  dag_depth>=2, source fetchability, similarity pre-satisfied). (2) Updated item 8
  (idea source -> claim spec, supersedes "invent from scratch") and M0 (QA idea
  approval -> claim spec is the up-front approval). (3) LESSONS LOG: added three
  2026-07-21 claim-spec entries. No gate reordering.
- 2026-07-21 | Phase 6 / build | a fully-specified deterministic pipeline (fixed
  queries + closed-form formula) scored SA=1.0 in minutes -> ZERO gap: such work is
  SCRIPTABLE, so no amount of scale or verifier-tightening opens a gap | make the
  per-unit work IRREDUCIBLE JUDGMENT over real free text (no field to fetch, no formula
  to apply) at context-swamping scale (100+ real units), graded mostly on VERIFIABLE
  extracted facts (verbatim-substring evidence, hand-labeled partial oracle) + fail-
  closed LLM depth checks; before any live run, PROJECT the gap on good/empty/hollow/
  fabricated/reaction-only fixtures.
- 2026-07-21 | Gate 3 / verify.py | balanced-accuracy and directional-pair checks gave
  ~0.5 credit to RANDOM/constant guessing, floating hollow/fabricated fixtures above
  0.30 | chance-correct per-check skill (informedness = max(0, 2*frac-1) for directional
  pairs and winner-consistency; (recall-1/k)/(1-1/k) for balanced accuracy) and return
  0 for constant/all-null predictions; a coin-flip then scores ~0 while a perfect answer
  still scores 1.0 -- this is per-check skill measurement, NOT a reward cap/floor.
- 2026-07-21 | Gate 3 / verify.py | copy-paste rationales slipped through a distinctness
  check that AVERAGED rationale + justification uniqueness (distinct justifications
  masked identical rationales) | score distinctness as the WEAKEST-LINK (min) of the two
  uniqueness ratios so copy-pasting either field is penalized.
- 2026-07-21 | build / harness | the in-container LLM judge died with `No module named
  'openai'` | install the judge client in environment/Dockerfile AND make every LLM
  check FAIL CLOSED to 0.0 on any infra failure (no key / missing lib / API error /
  unparseable) -- never fail OPEN to 1.0 (the canonical example's fail-open is the
  anti-pattern to avoid).
- 2026-07-21 | build / scope | fixing a scriptable claim task by SWAPPING the whole scenario
  (domain, persona, data) is an over-correction that reads as "a new random task" | the claim
  spec is a STARTING POINT: keep the core (persona, deliverables, coordination pattern) and
  MODIFY only the mechanism that made it scriptable (here: change the judgment basis to
  irreducible reading of real free text). Prefer a source the claim already lists.
- 2026-07-21 | build / data | reused the 128-issue design's "sort-by-👍 is the trap" anti-gaming
  axis on GOVERNMENT/civic repos where 👍 reactions are ~0 (nonzero=3/323) -> the anti-reaction
  pairs had no signal | pick the demand/engagement axis that actually VARIES in the chosen
  corpus (here `comment_count`, max 33) and build the anti-popularity oracle pairs on THAT;
  always run `stats` on the frozen snapshot before designing the gaming-resistance checks.
- 2026-07-21 | Gate 3 / reward-hacking QA | ran an adversarial subagent to find ways to score
  without doing the task (manager's suggestion): confirmed the zero-reading ceiling (~0.46) and
  that semantic oracle labels are NOT metadata-derivable, then hardened by grading grounding on
  ALL units (no sampling), enlarging LLM samples, and raising the reading-dependent oracle
  weight (more priority + anti-comment pairs) | make an adversarial reward-hack review a
  standing pre-ship step; it is cheap and catches mechanical ceilings the self-test alone misses.
- 2026-07-21 | build / gap-hardening | harness was DOWN so SA/MA could not be run; rather than
  guess the outcome, strengthened the task via the one sanctioned lever -- SCALE (doubled the
  real backlog 64 -> 128 units) -- with NO rubric reweighting | when you cannot run live, the
  safe way to raise confidence in the gap is more REAL units (context/budget swamp), not new
  checks or heavier weights. Make the re-freeze APPEND-ONLY: keep the existing units' ids +
  hand-labels byte-for-byte (verify with a diff) and only READ + hand-label the newly-added
  units, so prior verified labels are never invalidated and integrity is preserved.
- 2026-07-21 | Gate 4 / task.toml vs decomposition | claim spec (and a prior build) set
  `estimated_sub_agents` to the estimated REALIZED session count (~50: leads + all
  dynamically-spawned per-matchup analysts), but a specialist-routing org chart of only ~9
  declared nodes VIOLATES the binding S-04 gate (estimated_sub_agents == sub_tasks count) AND
  a 9-vs-dozens gap fails the post-run realized-tree reconciliation | ENUMERATE the genuine
  parallel fan-out as explicit sub_tasks (e.g. one reader per small batch) so the declared
  count both satisfies S-04 and approximates the realized swarm, hitting the Hard tier
  (dag_width>=20); still reconcile UP to the observed spawn tree after the MA run (P21-10).
- 2026-07-21 | Gate 3 / self-test fixture | after scaling, the "good" fixture's priority FORMULA
  ranked a well-written DUPLICATE above its weaker CANONICAL, failing a canonical>duplicate oracle
  pair (fixture bug, not a label bug) | the good fixture must obey the rulebook, not just a
  heuristic: post-process it so every duplicate is forced strictly below its own canonical before
  scoring; a failing oracle pair in the good fixture means the FIXTURE is wrong, re-check it before
  suspecting the oracle.
- 2026-07-21 | Gate 3 / gap-hardening | after a real SA scored 0.7956, deepened the deliverable
  (added a first-class cross-backlog `related_features` axis + full-128/127 deterministic TAIL-DEPTH
  checks) and rebalanced by COUNT (structural 4->3, added cross-cutting + tail-depth + a 6th LLM
  judge = 24 checks) rather than reweighting | when SA is high, the durable fix is MORE hard
  cross-cutting/tail work the deliverable now REQUIRES (O(n^2) reading one context cannot hold),
  not heavier weights; keep reward = mean of booleans. Note the structural+reward-hacking+self-
  consistency checks form a ~0.46 "valid-but-shallow" FLOOR (comment_only fixture), so SA<0.30 is
  often unreachable with an honest structural minimum -- treat gap>0.23 as the binding target and
  lower the floor only by shrinking the free structural SHARE, never by a trick.
- 2026-07-21 | run / harness | a SET FIREWORKS_API_KEY can still be INVALID: opencode exited in
  ~90s with NonZeroAgentExitCodeError and agent/opencode.txt showed `AI_APICallError: The API key
  you provided is invalid` (401 UNAUTHORIZED from api.fireworks.ai) -- and the same bad key would
  also fail-close every LLM judge to 0.0 | before launching a ~16-min SA (or ~2h MA) run, PROBE the
  key with one cheap chat/responses call; an agent that dies in <2 min is almost always a credential/
  network failure (read agent/opencode.txt for the real error), not a task defect -- do not
  interpret its 0.0 as an SA score.
- 2026-07-21 | build / tooling | a quick regex that parsed the hand-label python lists broke because
  a list COMMENT contained `[maybe]` (the `]` closed the non-greedy `\[(.*?)\]` early), silently
  dropping half the labels and giving false "no-overlap"/"missing-label" results | never trust a
  regex scrape of source-of-truth label lists -- import the module (or json) and read the real
  objects, and keep literal brackets out of list comments.
- 2026-07-21 | Phase 6 / mascloud | live cloud runs after gap-hardening: SA=0.7232, MA=0.7835 ->
  gap=0.06 (MA burned 13.4M tok / 44m / $5.38, ~10x SA). Per-check diff showed the ONLY large
  MA>>SA axes were matchup-justification quality (tail-depth +0.67, matchup-reasoning judge +0.60)
  and, smaller, use_case (+0.27) / spec (+0.17); MANY checks were near-1.0 for BOTH (all structural
  + reward-hacking + ranking-consistency + dup-validity + evidence ~11 checks) and SEVERAL had SA>MA
  (related-recall via link-spam +0.11, rationale-tail-depth +0.13, depth-judge +0.20, priority +0.10)
  which actively COMPRESS the gap | LESSON: an "assess-N-short-items + sort + justify" task is
  intrinsically single-agent-friendly -- one capable model does ~90% of it, so the gap collapses no
  matter how the rubric is balanced. A real >=0.23 gap needs MANY (>=12) INDEPENDENT axes where a
  swarm genuinely beats one agent; if only ONE axis (here: sustaining free-text justification quality
  across 127 units = a token-budget/stamina effect, not coordination quality) shows the gap,
  amplifying it to hit 0.23 is OVER-WEIGHTING = a scoring trick (forbidden). Diagnose the gap's
  DIMENSIONALITY from the SA-vs-MA per-check delta BEFORE more reruns; if it is one-dimensional,
  invoke the ALTERNATE-USE PIVOT (re-target the deliverable/class) or park + escalate with the run
  history -- do NOT curve-fit the rubric to two runs.
- 2026-07-21 | Phase 6 / mascloud | practical run facts: `uv run mascloud run <task_folder> --mode
  single|multi` runs entirely server-side (no local Fireworks key needed; token in ~/.mascloud), zips
  the folder EXCLUDING execution_logs, streams to `[DONE ...]`, and drops `<name>-<mode>.zip` beside
  the task folder with a full execution_logs tree incl. verifier/test-stdout.txt (per-check scores).
  SA ~10m/$0.5, MA ~44m/$5.4 | budget for it: a single MA gap-diagnosis run costs ~$5 and ~45m, so
  get the per-check delta from ONE SA + ONE MA and reason offline; don't re-run blindly.
- 2026-07-21 | Phase 6 / gap-ceiling arithmetic | after SA/MA per-check data, PROJECT the achievable
  gap before building a re-target: reward=mean(24) has an unavoidable ZERO-GAP FLOOR = the required
  anti-cheating checks (~3 structural + 4 reward-hacking = 7/24 ~= 0.29, both agents ~0.95) PLUS any
  correctness/consistency checks the SINGLE agent already does well (here ranking-consistency=1.0 both,
  assessment-depth & ranking-rationale judges SA~0.85-1.0, priority pairs SA 0.81). With MA genuinely
  strong on only ~2 substantive axes (sustained free-text quality: matchups + dependency edges) and
  MEDIOCRE on judgment (use_case 0.31, duplicates 0.25 -- kimi-k2 caps low swarm-or-not, and per-item
  judgment is independent so a focused SA matches a divided swarm), the blended gap tops out ~0.11-0.18
  no matter how the deliverable is deepened | LESSON: compute floor_share + (non-floor checks the SA
  aces) FIRST; if (# checks where MA>>SA) is too few to overcome that, the TASK CLASS ("assess N short
  items + sort + justify") has a structural gap ceiling < 0.23. Removing the SA-strong checks to force
  the gap is curating-to-a-trick (forbidden). The only honest fixes are a DIFFERENT deliverable class
  with many independent MA-winnable axes, or a DIFFERENT corpus where judgment itself is coordination-
  hard -- i.e. re-architect the task, don't keep deepening this one. Park + escalate with the run
  history and this arithmetic.
- 2026-07-22 | Phase 6 / mascloud | RE-TARGETED the same 128-item 18F corpus from a tournament to a
  "global dependency-graph + capacity-constrained delivery-wave plan" (new deliverable class chosen
  specifically for coordination: O(n^2) edge-building + graph/wave/readiness self-consistency).
  Live: SA=0.6323, MA=0.7873 -> gap=0.155 (SA $1.3/36m, MA $3.4/~90m). The coordination thesis FAILED
  empirically: (a) MA built a SPARSER, worse graph than SA -- edge_f1 MA 0.33 (37 edges/14 oracle
  pairs) < SA 0.47 (69 edges/27 pairs); the single agent handled the ~47-pair graph fine, so "MA holds
  the global DAG SA can't" never materialized at n=128; (b) the wave/readiness CONSISTENCY checks
  (wave_respects_deps, readiness_consistency, wave1_foundational) were 1.0 for BOTH -- a sparse-enough
  graph is trivially SELF-consistent, so self-referential consistency adds free points to both sides
  and opens ZERO gap; (c) ~9/24 checks pinned near 1.0 for both (structural+anti-fab+consistency1-3+
  memo+assessment-llm) compressed the mean; (d) MA even LOST sequencing-reasoning-judge (0.0 vs 0.67).
  The only real MA>>SA axes were AGAIN free-text quality (distinctness +0.95, anti-comment +0.82,
  grounding +0.45, use_case +0.39) -- the identical one-dimensional ceiling as the tournament | LESSON:
  a coordination gap requires the GLOBAL STRUCTURE to exceed one context's capacity; re-targeting the
  DELIVERABLE on the SAME small corpus does not create that -- if a single agent can hold the whole
  graph, no graph/consistency rubric will discriminate (and SELF-referential consistency checks never
  discriminate at any scale -- grade consistency against the oracle ground truth, not the agent's
  own sparse graph. To open this class you must SCALE the real units so the graph itself overflows one
  context (>=300-500 interlinked units), or pick a corpus where the dependency structure is genuinely
  large; otherwise park + escalate. Do NOT delete the both-pass checks to inflate the gap (curate-to-a-
  trick, forbidden).
- 2026-07-22 | Gate 3 / Phase 6 | on Windows PowerShell `mascloud run` streams via rich and crashes mid-run
  with UnicodeEncodeError ('charmap' cp1252) when a log line has non-latin-1 chars -- the local CLI dies
  (exit 1, no auto-download) but the CLOUD run keeps going | set `$env:PYTHONIOENCODING="utf-8"` before
  every mascloud call; the run continues server-side, so recover the result with `mascloud runs` +
  `mascloud download <run_id>` rather than re-running.
- 2026-07-22 | Gate 3 | consistency-coverage multiplier keyed on UNDIRECTED edge recall let an SA that
  emitted 566 overlaps/cross_references but ZERO depends_on edges (all-Ready) still score wave1-foundational
  = 1.0 (vacuously true with no deps) | key the coverage multiplier on the DIRECTED depends_on recall, and
  make each vacuous check earn 0 when its structure is absent (readiness over the dependency-ACTIVE set
  only; front-load credit only for priority pairs SEPARATED across waves) so a one-wave / dependency-free
  dump scores 0.
- 2026-07-22 | Phase 6 | edited verify.py AFTER launching the cloud SA/MA runs -> the in-flight runs bundle
  the stale verifier, so their official rewards are not apples-to-apples with the fix | FREEZE verify.py
  before launching; if a fix is unavoidable mid-flight, re-score the DOWNLOADED agent artifacts locally with
  the final verifier (deterministic checks + the run's already-logged LLM verdicts) to get a valid gap
  without paying for a re-run, then do ONE final official SA+MA pass with the locked verifier for the
  shipped execution_logs (S-07).
- 2026-07-22 | Phase 6 | SCALING the corpus to 400 real interlinked issues (18F+VA+cfpb+GSA, ~140k tokens)
  STILL did not open the gap: live SA=0.43 / MA=0.59 (gap 0.165, 3rd attempt after tournament 0.06 and
  wave-128 0.155 -- a hard ~0.10-0.17 ceiling for this class). Root cause: even at 400 items BOTH agents
  build SPARSE graphs (SA 566 edges/0 depends_on; MA 61 edges/24 depends_on), so the single agent is not
  catastrophically worse; and the MA pipeline actually REGRESSES on free-text (a single reconciler
  templated all 400 readiness_notes -> distinctness 0.045 vs SA 1.0; MA also lost per-item priority/dup),
  wiping out its real wins on consistency, edge-validity/sequencing LLM judges, and edge evidence | LESSON:
  scale ALONE is insufficient if the per-item deliverable can still be produced acceptably by one agent and
  the multi pipeline degrades the free-text; a real coordination gap needs the CORRECT global artifact to be
  UNPRODUCIBLE by one agent (not merely large), AND the decomposition must not hand a single reconciler the
  per-item prose. After the scale-up pivot fails, PARK + ESCALATE with the run history instead of re-running.
- 2026-07-22 | Gate 3 | tying the consistency-coverage multiplier to DIRECTED depends_on recall (vs
  undirected) back-fired: it throttled the MA's legitimate consistency win (MA graph sparse in depends_on)
  and shrank the gap 0.165->0.099 |   key coverage on UNDIRECTED related-pair recall (measures real structure
  found) and instead close the vacuity hole at the check itself (wave1-foundational returns 0 when there are
  zero depends_on edges; readiness scored over the dependency-active set only).
- 2026-07-22 | Gate 3 (BREAKTHROUGH) | the gap finally opened NOT by more corpus but by grading CORRECTNESS
  not PRESENCE + fixing the MA pipeline. Diagnosis from the real logs: SA scored 0.43 by SKIPPING the whole
  dependency analysis (0 depends_on edges, all 400 "Ready") yet banking full credit for 567 well-grounded
  overlaps/cross_ref edges + distinct per-item prose; MA scored 0.59 but its graph-reconciler TEMPLATED the
  readiness_note for 377/400 items (distinctness 0.045) and its batch-siloed readers scored WORSE than SA on
  duplicates/priority. Two legitimate, doc-aligned fixes moved SA 0.43->0.37 and MA 0.59->0.62 (gap
  0.165->0.249 on the SAME downloaded outputs, projecting ~0.31 after the MA note-fix): (1) refocus the two
  edge-QUALITY checks (explanation depth, evidence grounding) onto the DIRECTED depends_on edges -- the
  load-bearing deliverable -- so an all-overlaps/all-Ready plan earns 0 there while relatedness is still
  graded for correctness by edge-F1; (2) recalibrate anti-degenerate to catch the all-Ready/no-deps skip
  (drop the auto-true waves>=17 guard; guards = spread>=15, depends_on>=15, blocked>=15) | LESSON: when both
  SA and MA build SPARSE graphs and the gap is stuck, the fix is usually in HOW you grade (kill presence
  credit for the hard artifact the SA skipped) and in the DECOMPOSITION (a single reconciler templating a
  per-item field, or batch-siloed readers that can't dedup/normalize globally, silently sink the MA) -- NOT
  in adding more corpus. Verify by re-scoring the DOWNLOADED SA+MA outputs under each candidate rubric before
  spending on a live re-run.
- 2026-07-22 | Gate 3 | the confirming SA run exposed a SECOND, opposite gaming strategy: instead of
  skipping the graph, it SPAMMED 1162 edges (147 depends_on, 145 Blocked) with precision 0.04 (edge F1=0.06),
  then made its waves internally respect its own garbage edges -- scoring 0.52 because the consistency
  coverage multiplier was RECALL-based (spam inflates recall to 0.23 -> cov 0.93) and edge-evidence just
  checks "is this a verbatim quote" (trivial to copy a real substring onto a wrong edge). FIX: make the
  coverage multiplier F1-based (precision AND recall) instead of recall-only, and F1-scale the two
  edge-QUALITY checks too. Result: spam-SA 0.52->0.42, skip-SA 0.37, MA 0.63 (0.69 note-fixed) | LESSON:
  internal consistency is ALWAYS cheap (any agent can make its plan respect its own edges), so the ONLY thing
  making consistency/edge-quality meaningful is gating them on the graph's F1 vs ground truth -- gate on
  RECALL and an agent games it by link-spam; gate on F1 and both spam (low precision) and skip (low recall)
  collapse. Always red-team BOTH failure modes (empty graph AND spammed graph) before locking a graph rubric.
- 2026-07-22 | Gate 3 | tuning the DECOMPOSITION has non-obvious cross-effects: fixing the reconciler's
  templated readiness_note (depth 0.0->0.995) and adding cross-batch dedup (0.18->0.45) worked, but the SAME
  edit told edge-specialists to pursue "comprehensive/denser coverage" -- which made them OVER-produce (82
  edges/F1 0.33 -> 313 edges/precision 0.17/F1 0.21), tanking edge-validity judge (1.0->0.2), sequencing
  judge (0.875->0.0) and, via F1-coverage, consistency + edge-quality. Net MA went DOWN (0.63->0.55) |
  LESSON: in a precision-graded graph task, instruct edge/link workers to prioritise PRECISION over volume
  (the rulebook already says a spurious edge is an audit finding); "be thorough / find more" reliably
  degrades precision-sensitive metrics. Change ONE decomposition lever at a time and re-score each against
  the locked verifier -- a note/dedup win can be silently erased by an edge-density regression in the same edit.
- 2026-07-22 | Gate 3 (DECISIVE) | after fully hardening the rubric (skip-SA->0.37, spam-SA->0.42, both
  gaming holes closed) the FINAL apples-to-apples pair still gave SA=0.593 vs MA=0.667 -> gap 0.074. Root
  cause is STRUCTURAL, not rubric: 400 items ~= 140k tokens FITS in one modern context, so a competent single
  agent reads everything and builds a self-consistent global graph + wave plan by itself (SA range across all
  runs 0.37-0.63); MA is high-variance (0.55-0.79) and only narrowly better on LLM-judged validity + distinct
  notes, which its own run-to-run failures (issue# mislabel 0.50, dedup 0.09, sparse edges, sequencing 0.12)
  erase | LESSON (the big one, now proven twice): a coordination gap CANNOT be manufactured by rubric design
  when the whole task fits in one context -- no amount of correctness-grading separates a competent SA from
  MA. The ONLY genuine fix is to make the global artifact EXCEED one context (token volume >~250-300k so the
  SA physically cannot hold the whole backlog while reasoning about cross-item structure), which is the
  documented coordination mechanism, NOT random count-padding. Confirm the corpus token total vs the context
  window BEFORE building; if it fits, the gap will not hold regardless of rubric quality.
- 2026-07-22 | Scale-to-overflow build | executed the context-overflow fix: appended F401-F700 (300
  rich unused cached issues, body>=600 chars, depth-first dense clusters) to the frozen F001-F400
  (preserved byte-for-byte), taking the corpus to 700 items / ~289k tokens -- now EXCEEDS one context.
  Labeled the 300 new items via a dump (spec/use_case/dup/related); rebuilt the partial oracle (700/700
  labelled, 356 related pairs) with all builder asserts passing; rescaled verify.py (N=700, selftest
  good=0.99 / shallow=0.37 / degenerate=0.18, det-gap 0.62); rebalanced decomposition to 32 readers x
  ~22 (est_sub_agents stays 43, dag intact); updated instruction/rules/task.toml/sources/manifest/
  Dockerfile (400->700, >=17->>=30 waves, ~140k->~290k, hours 62->104). Launched SA run_572c8a0c5aabbb44
  + MA run_4707e57bc7dfa355 (700-item). LESSON: reusing the append-only freeze + dump-labeling +
  oracle-builder-asserts pipeline made a 1.75x corpus scale-up a ~1-session job with ZERO fabrication
  (the builder asserts are the integrity backstop: Well/Under & Yes/No disjoint, valid fids, dup
  canonical rules, anti-comment monotonic). Delegating the 300-item read+label to a subagent (strict
  no-fabrication prompt + template + builder-assert verification) kept the main context free for the
  rescale/runs without weakening integrity.
- 2026-07-22 | Gate 3 (BREAKTHROUGH) | at 700 items BOTH SA and MA first scored 0.0 -- but for opposite,
  non-rubric reasons. SA (100k tok, ~7 min) went script-mode, wrote 150 edges to /workspace and voluntarily
  ENDED its session with nothing in /logs/agent (genuine non-completion at scale, no timeout involved). MA
  (24M tok, ~1.9h) SOLVED THE WHOLE TASK -- 700 assessments, 5482 edges, 33 waves, all 9 consistency checks
  PASS, files complete in /workspace -- then the orchestrator hit the harness STEP CAP (step 38, "exiting
  loop") mid-deliberation, one `cp` before the final plan-writer stage that was to copy /workspace ->
  /logs/agent. Empty /logs/agent -> verifier 0/700 -> 0.0. FIX (fair, no trick, instruction.md unchanged):
  make the agents that PRODUCE each deliverable write it DIRECTLY to /logs/agent (reconciler ->
  assessments.json + dependency_graph.json; wave-planner -> delivery_plan.json + audit_trail.log), delete
  the stranded copy stage. Re-run: MA 0.0 -> 0.7171, SA 0.0 (x2) -> gap 0.717 (SA<0.30, MA in band) |
  LESSON: a pipeline that STAGES the final artifact in /workspace and defers the graded write to a terminal
  agent is a single point of failure -- the orchestrator's fixed step budget can strand a fully-correct
  solution and score it 0.0. ALWAYS write graded deliverables to the graded path (/logs/agent) the moment
  each is produced; never make the only copy-to-graded-path step the last thing in a long spawn chain. Also:
  a downloaded result package captures ONLY /logs/agent + execution_logs, NOT /workspace -- so a step-capped
  0.0 CANNOT be re-scored offline; you must re-run to recover the number. And note the harness per-agent step
  cap (~38) is the real reason MA needs many agents: parallel agents multiply the total step budget, which is
  itself part of the genuine coordination advantage.
- 2026-07-22 | Gate 3 (QD-03.1) | a verifier that field-by-field diffs the whole output against a hand-built
  partial_oracle.json (balanced-accuracy on spec_quality/use_case/duplicates + directional priority pairs +
  edge-F1 vs related_pairs) is an ORACLE/answer-key comparison and a hard QD-03.1 reject -- EVEN THOUGH the
  difficulty guidance says "grade correctness vs a real reference." The two reconcile via QD-04.12(iii): keep
  grading correctness but move the DECISION to a DIFFERENT-family LLM judge handed the REAL source text at
  grading time; deterministic code may only ground quotes/ids and check INTERNAL consistency, never score a
  semantic item against a stored value. FIX pattern: convert each oracle field-diff into a real-text judge
  (spec/use_case/duplicates/priority), delete partial_oracle.json, drop any oracle-F1 consistency multiplier
  (rely on an anti-degenerate volume guard + the edge-validity judge for precision), and re-base "front-load"
  on the agent's OWN priority_score (internal). Keep total LLM-judge weight <50% (here 7/23=30%).
- 2026-07-22 | Gate 5 (QD-05.5/06.7/07.5) | a "hierarchical" task realized as a FLAT orchestrator fan-out (all
  ~46 workers spawned directly, parent_id=orchestrator) even though multi_opencode.py ENABLES nesting
  (permission task:allow). Root cause: the realized tree is the orchestrator LLM's runtime choice, and marking
  EVERY decomposition node `subagent_type: general` gives no manager/leaf signal. FIX (task-side lever, raises
  the odds but is still stochastic per run): tier the types to the harness's two-tier contract -- managers that
  must spawn workers = `general`, leaf workers = `explore` (task tool hard-blocked). Realization must still be
  confirmed on the actual multi run; re-run if it flattens.
- 2026-07-22 | Gate 5 (QD-07.10) | SA runtime prompt differed from instruction.md by a trailing " because
  single_opencode.py passes the prompt as `-- "$(cat /tmp/oc-instruction.txt)"` while multi_opencode.py uses
  clean stdin `< /tmp/oc-instruction.txt`. This is a shared-HARNESS quirk affecting every single run, not a
  task-file bug -- flag it (or align single to multi's stdin form); do not try to "fix" it inside the task.
- 2026-07-22 | Gate 8 (QD-07.8/08.3/08.5/08.8/08.11) | if verify.py calls an LLM, verifier_type MUST be
  "llm-judge" (not "executable"); and the judge client (openai) is a TEST-ONLY dep -> install it PINNED in
  tests/test.sh, never in environment/Dockerfile (which ships into the agent image). Four separate QD rejects
  all trace to this one mistake.
- 2026-07-23 | Gate 3 (CEILING, 4th confirmation) | after the oracle->judge rework, a re-run SA on the 700-item
  wave-plan COMPLETED (17 min, heavy prompt cache) and scored 0.659 -- NOT the 0.0 seen before. Diagnosis via
  per-check re-scoring of BOTH SA and the prior 0.7171 MA on the SAME current verifier (judges fail-closed
  locally): the deterministic gap is only ~0.116 and the REAL discriminators are per-item QUALITY (evidence
  grounding 0.09 vs 0.85, distinctness 0.08 vs 1.0, readiness-note depth 0.006 vs 1.0) plus the 3 quality
  judges (SA=0) -- these lift MA UP, they do NOT push SA DOWN. The 4 internal-consistency checks are VACUOUS
  for BOTH agents because BOTH emit a near-empty depends_on graph (SA=3, MA=6 edges) and dump everything into
  order-free `overlaps` (742 / 99). KEY LESSON 1: a "depends_on recall / de-vacuum consistency" fix is a TRAP
  here -- it subtracts equally from MA, so it cannot open the gap; always re-score the BEST KNOWN MA
  deliverable on the candidate verifier (deterministic-only is enough) BEFORE committing to a rubric fix.
  KEY LESSON 2: the large gap this task ever showed came ONLY from SA STOCHASTICALLY failing to complete
  (0.0), never from the rubric separating two COMPLETING agents -- a completing single Kimi-K2 genuinely does
  the per-item labeling/plan acceptably, so no oracle-free rubric change pushes a completing SA below 0.30 on
  this deliverable. A stochastic non-completion gap is NOT a shippable capability gap. PIVOT/ESCALATE rather
  than tune further. KEY LESSON 3 (harness cost): `mascloud` has NO cancel command -- killing the local
  streamer stops your wait/download but the cloud job may finish and bill anyway; only launch the SA first
  (cheap, ~17 min) to read the gap before paying for the ~2h MA. Also counts against the
  daily 6-run quota either way -- check `mascloud runs` (`Today: X/6`) before every submit.
- 2026-07-23 | S1 | trigger: client Slack update (MAS Cloud Run quota + model list) |
  cloud-run-only shipping + daily quota + auto model switch | (1) OPERATIONAL PREREQS /
  M4 / PHASE 6: all shipping/gap runs go through MAS Cloud Run (`mascloud`) going
  forward; documented daily quota = 6 submissions/trainer (midnight UTC reset; every
  submit counts); require `mascloud runs` before launch for `Today: X/6 runs used` and
  per-run model. (2) AGENT MODEL: usual `kimi-k2p6`; under high concurrent load new
  MULTI-mode runs may auto-switch to `kimi-k2p7-code` (automatic; no trainer flag) --
  clarified judge independence still forbids any Kimi/Moonshot/K2 judge. (3) Quota
  increase: escalate via Ruturaj's form when consistently capped (top-performer /
  efficiency evidence). (4) LESSONS LOG: added two 2026-07-23 mascloud entries. No
  gate reordering.
- 2026-07-23 | ALTERNATE-USE PIVOT (deliverable re-target) | after confirming the gap ceiling, pivoted the
  700-item task from a pure delivery-wave plan to a "Consolidation Dossier + fundable shortlist" WITHOUT
  changing the corpus. KEY LESSON (rubric arithmetic, do this BEFORE building): reweighting an existing
  verifier CANNOT open the gap if too few checks discriminate. Re-scored the real SA=0.659 / MA~0.85 per-check
  data: only ~7 of 23 checks actually separated the two (verbatim grounding 0.09/0.85, distinctness 0.08/1.0,
  readiness-note depth 0.006/1.0, + 3 quality judges 0/0.85); the other ~16 were cheap-1.0 (valid structure /
  copied identity / copied quote) or vacuous (consistency over a sparse depends_on graph). Dropping the 16 to
  let the 7 dominate leaves <15 checks (below the guideline floor) AND removes legit structural validation, so
  the fix MUST be to ADD more DISTINCT discriminating checks, not just delete. So the pivot ADDED grounded
  per-item + global-consolidation work: a `capability_statement` field (grounded+distinct+judge-correct),
  `consolidation.json` initiatives (deterministic distribution + LLM merge-PRECISION + merge-RECALL where
  candidate near-dup pairs are extracted deterministically from the frozen text and only judge-confirmed SAME
  pairs count), and a fundable shortlist (justification judge). Final rubric = 21 checks, only 3 cheap presence
  checks, 8 judges (38%), edge checks now grade ALL edges (so overlap-spam is penalized, not ignored). KEY
  LESSON 2 (the real target is the GAP, not SA<0.30): a COMPLETING single Kimi-K2 lands ~0.35-0.42 on ANY fair
  oracle-free rubric for this data (valid structure + short labels are within one agent's reach); do NOT chase
  SA<0.30 by cutting legit checks -- instead make MA reach ~0.85 by dominating the rubric with grounded-at-scale
  + consolidation work, giving a gap of ~0.45 (SA~0.38, MA~0.85) which clears >0.23 with margin. KEY LESSON 3
  (self-test the deterministic subset offline first): a templated-vs-grounded fixture pair, judges failing
  closed, scored 0.20 vs 0.53 on deterministic-only -- confirming the floor is small and grounding dominates
  BEFORE spending a single cloud run. Build the fixture generator from the REAL corpus so grounding checks are
  exercised truthfully.
- 2026-07-23 | SA run on pivoted task (run_27e95a83c37e34cf) = 0.0, but from MODEL DEGENERATION, not a task
  wall. The single kimi-k2p6 read proposals and started planning (initiatives/consolidation, todowrite/bash),
  then its FINAL message derailed into a ~200k-char degenerate repetition loop (a pipe-separated synonym
  cascade "Vigor|Vibrancy|Animation|Life|..."), hit reason=stop, and wrote NOTHING to /logs/agent/ -> all 21
  checks 0. No exception; 156k in / 41k out tokens (never ingested the full ~290k corpus). KEY LESSON: a 0.0
  from a single-agent run is NOT automatically a "task too big / coordination" signal -- inspect
  agent/opencode.txt: a repetition-loop/degeneration (common when kimi-k2p6 is handed a near-context-limit
  prompt) is a STOCHASTIC model failure that neither validates nor refutes the gap. Do NOT log it as evidence of
  a capability gap and do NOT rely on it; a shippable gap needs a COMPLETING SA baseline. One inconclusive SA
  still costs 1/6 daily quota + bill. Read the gap from a completing SA, and only treat repeated
  non-completions as a signal if they reproduce across several runs (else it is model noise).
- 2026-07-23 | COMPLETING SA baseline on pivoted task (run_233cbe890c4559b2) = 0.5128 (30 min, 1.64M in / 157k
  out, NonZeroAgentExitCodeError but deliverables produced). CRUCIAL per-check finding: a completing Kimi-K2
  does the DETERMINISTIC FORM checks WELL -- evidence grounded 0.997, capability_statement grounded+distinct
  0.86, consolidation STRUCTURE 0.82 (654 initiatives, 15 merges), wave-memo depth 1.0, spec-quality label 0.85
  -- so the grounding/structure checks I expected to be SA-killers were NOT (my "templated" self-test fixture
  was too pessimistic vs a real completing agent). What a completing SA STILL fails is CORRECTNESS + distinctness
  + depth: distinctness 0.04, readiness-note depth 0.0, edge explanation 0.06, and the judges assessment-depth
  0.0 / sequencing 0.0 / capability-correct 0.30 / edge-validity 0.20 / merge-precision 0.07 / shortlist-just 0.0.
  KEY LESSON 1: pair every deterministic FORM check with a judge CORRECTNESS check -- SA banks form (grounded,
  distinct-looking, structurally valid) but the judge catches that its content is WRONG; the gap lives almost
  entirely in the correctness judges + distinctness + note-depth (~8 checks), not in grounding/structure. KEY
  LESSON 2: the pivot lowered completing-SA from 0.66 -> 0.51 (real progress) but did NOT break the ceiling to
  <0.30, because a completing agent genuinely grounds and structures ~half the task; the >0.23 gap now depends on
  MA reliably reaching ~0.78+ on the correctness axes, and MA on this corpus is historically VARIABLE (0.57-0.79
  completing). Projected gap ~0.27-0.29 = clears 0.23 but THIN; a weak MA run sinks it. KEY LESSON 3: do NOT
  over-trust an offline templated-fixture self-test to predict SA -- a real completing agent scores much higher
  on form checks than a naive templated fixture, so   the offline gap (0.20 vs 0.53) OVERSTATED the live SA-kill.
- 2026-07-23 | To LEGITIMATELY lower a completing SA (no caps/tricks), only tighten checks where SA's
  PASS is UNDESERVED (low-quality) but a genuine MA still passes -- never blanket-penalize. Three MA-safe
  levers that worked here: (1) a "free" LLM-judge point (merge-recall returned 1.0 because the candidate
  near-dup pairs were too weak, Jaccard>=0.18, so no true duplicate was ever tested) -> RAISE candidate
  strength (Jaccard>=0.30, sample from the strongest band) so it becomes a real recall test the piecemeal
  SA fails; (2) a structure check that rewards WRONG work (consolidation-distribution gave 0.82 while the
  merge-precision judge gave 0.07) -> only count a multi-member merge as genuine if members are same-repo
  AND share real content tokens (rulebook: dups almost always share a repo), so padded/cross-repo merges
  earn nothing; (3) pair every deterministic FORM check with a CORRECTNESS judge -> added an
  initiative-summary-correctness judge so a structurally-valid-but-semantically-wrong consolidation cannot
  bank the structure points. GOTCHA: an LLM-judge that returns 1.0 when its candidate set is empty is a
  silent free point -- always make the judge's candidate generation strong enough that the denominator is
  real. LIMIT: with the SA deliverables NOT shipped in the result package and the API key revoked, these
  hardenings can only be ESTIMATED offline (self-test + known per-check breakdown), not measured against the
  real SA output; the live number requires the next SA re-run.
- 2026-07-23 | PRE-RUN P0 FAIL-PROOF AUDIT (do this before EVERY paid run to protect quota). (1) CRASH-SAFETY:
  wrap the WHOLE verifier so reward.txt is ALWAYS written -- each check in try/except (fail closed to 0.0),
  build_context() in try/except, main() in try/except, and test.sh keeps a `[ -f reward.txt ] || echo 0`
  fallback. A missing reward.txt = the harness wastes the run on a VALID submission. Prove it with a hostile
  edge-suite (empty dir, empty strings, malformed JSON, wrong types, missing fields, degenerate one-bucket,
  inf/nan) -- all must emit a reward and never traceback. (2) HARDENING-INTRODUCED FAIRNESS BUG: a "genuine
  merge" gate that required members be SAME-REPO would have zeroed the exact CROSS-ORG consolidation the task
  asks for -- always re-check a new gate against the deliverable's own spec (this task's cross-org section
  explicitly wants cross-repo merges); made it REPO-AGNOSTIC (shared-content only) and left same-capability
  precision to the judges. (3) Confirm the corpus actually SUPPORTS the rubric's thresholds before trusting
  them (measured 2635 same-repo Jaccard>=0.30 pairs, so merge-recall has a real denominator and >=40 genuine
  merges is achievable). (4) A wasted run is either MINE (verifier crash / schema-path mismatch / unfair gate
  -- all fixable pre-run) or INFRA (Fireworks rate-limit, model degeneration/repetition, context overflow --
  NOT fixable, only mitigated by symmetric 'write deliverables incrementally' guidance so partial progress is
  graded instead of an empty 0.0). Separate the two classes explicitly when reporting run risk to management.
- 2026-07-23 | To pull a COMPLETING single agent under 0.30 WITHOUT a scoring trick, the lever is rubric SHAPE,
  not penalties (rubric_scale_presentation.pdf: FEWER easy checks, MORE hard ones; grade CORRECTNESS not
  presence). A completing agent genuinely earns the EASY SHELL -- valid schema, 700 coverage, verbatim-substring
  grounding, spec labels, a structurally-valid consolidation -- which was ~9 of 22 checks and anchored SA at
  ~0.41 no matter how many hard checks were added (the floor is an asymptote you cannot out-add). Fix: MERGE the
  easy shell into the minimum coherent floor (here 2 checks: completeness+validity [coverage+schema+audit] and
  grounding integrity [anti-fab+evidence]) and DROP deterministic FORM checks that a correctness judge already
  covers (capability_grounded->capability_correct judge, wave_memo_depth->sequencing judge) plus non-
  discriminating easy checks (spec-quality label both agents get right). Result: 16 checks (8 det + 8 judges),
  the rubric now DOMINATED by distinctness + note depth + all-edge quality + consolidation + 8 correctness
  judges where a serial agent fails; projecting the real completing-SA per-check scores onto it gives ~0.27.
  Merging cheap presence checks into fewer composite checks (each still an equal-weight average, partial credit
  intact) is legitimate rubric shaping, NOT a cap/tier/multiplier. INTEGRITY CHECK caught mid-task: do NOT claim
  "deterministic checks alone give >0.23 gap" unless the numbers support it -- projected det-only gap here is
  ~0.17-0.25 (depends on the swarm building a dense grounded graph), so the claim was softened to "meaningful
  gap if judges fail; full gap realized with the correctness judges." Never ship an unbacked quantitative claim.
- 2026-07-23 | BIG FINDING (run_db8c3b07, CLEAN completing SA, 0 exceptions, 38min) = 0.4967, NOT the projected
  ~0.27. WHY the projection failed: a completing single agent does a SMALL amount of work VERY WELL and PASSES
  the sample-based CORRECTNESS judges -- it built only 40 edges (edge-validity judge 0.95), 4 merges
  (merge-precision 1.0, and merge-recall 0.75 because only 4 candidate pairs were judge-confirmed SAME out of a
  15-sample), and decent capability statements (0.60 tail-biased). LESSON: a PRECISION/VALIDITY judge that
  samples the AGENT'S OWN OUTPUT rewards quality-of-effort, NOT coverage-at-scale, so a single agent games it by
  producing few-but-good items. These judges are NON-discriminating (they can even FAVOR SA, whose tiny graph is
  95% valid vs a swarm's larger 85%-valid graph). The axes a completing SA GENUINELY fails are only: distinctness
  (0.03), readiness-note depth (0.01), assessment-depth/sequencing/shortlist judges (0.0 -- generic filler), and
  consolidation SCALE (made 691 near-singletons -> band 0.18). BIGGER LESSON: a COMPLETING single agent on this
  task legitimately earns ~0.50 on a FAIR rubric (it really does ~half the work); SA<0.30 for a COMPLETING agent
  is NOT reachable without weighting the rubric so hard toward SA's specific failures that it becomes a penalty
  the verifier INFLICTS (auto-reject). SA is effectively BIMODAL here: ~0.50 when it completes, ~0.0 when it
  degenerates/overflows. The GAP is real (SA ~0.50 vs projected MA ~0.87 = ~0.37 > 0.23) but the "SA<0.30"
  difficulty guideline conflicts with an honest score for a completing agent -> this is ALTERNATE-USE-PIVOT /
  park-escalate territory (4th+ round), not more SA reruns. To make a recall judge bite, its candidate denominator
  must be LARGE (sample ~40 strong pairs, not 15) so a piecemeal agent with few merges clearly misses them.
- 2026-07-23 | GAP MEASURED, root-caused (SA run_db8c3b07=0.4967 clean vs MA run_bdc81b4a=0.6982 clean -> gap
  0.2015, just under 0.23). The gap is REAL & large on the axes that matter (distinctness +0.94, assessment-depth
  +0.95, shortlist +0.93, notes +0.76, capability +0.35, summary +0.50) but is SUPPRESSED by 5 checks where MA
  scores WORSE than SA: edge-validity (SA 0.95 vs MA 0.20), merge-precision (1.0 vs 0.33), grounding (1.0 vs 0.66),
  edge-evidence (0.60 vs 0.39), merge-recall (0.75 vs 0.50). ROOT CAUSE = an MA-pipeline defect, NOT a task
  ceiling: the overlap/cross-ref specialists CLIQUE-SPAMMED ~13 near-identical GitHub ISSUE-TEMPLATE files (all
  titled "Analytics Feature Request/Bug Report") -> ~150 spurious "overlaps"/"cross_references" edges whose
  evidence_quote was the shared TEMPLATE BOILERPLATE, and emitted BOTH an overlaps AND a cross_references edge for
  the same pair (dup padding). The validity judge correctly rejected them (0.20). SA "avoided" this only by being
  lazy (40 edges, never found the clique). LESSON: when a corpus contains boilerplate issue-TEMPLATE files, a
  thorough swarm will link them into a false clique and get punished by a precision judge -> the DECOMPOSITION must
  explicitly tell edge/consolidation specialists that shared template/boilerplate text is NOT evidence of overlap,
  forbid emitting both overlaps+cross_references for one pair, and prefer precision. This is a legitimate
  pipeline-side fix (recovers MA edge-validity/precision/grounding) and needs ONLY an MA rerun -- do NOT touch
  verify.py or the SA baseline (0.497) stays valid without a re-score (LLM judges can't run locally w/o an API key).
- 2026-07-23 | Local QG LLM-review fix round (gap-0.2015 zip) | the reviewer flagged 11 items across QD-01/02/03/04/
  06/07/08. Two structural lessons: (1) INSTRUCTION-MANDATED-BEHAVIOUR COVERAGE (QD-02.3/QD-03.2): every judgement
  the rulebook demands MUST have a NAMED scored item, but wiring each omitted check in separately DILUTES the gap
  because a completing SA's deterministic script ACES the structural wave checks (capacity/deps-order/wave1/
  readiness) one-by-one -> the fix that satisfies coverage AND protects the gap is an AGGREGATOR check (mean of
  named sub-scores) -- QG explicitly allows "fold into aggregators". Built two: `check_wave_plan_correctness`
  (5 wave constraints -> 1 check) and `check_assessment_label_correctness` (spec/use-case/dup/priority judges ->
  1 check). Kept judges at exactly 50% (9/18) so QD-03.3 stays clean. Verified the deterministic-subset gap held
  (templated 0.12 vs grounded 0.35 = 0.23) with selftest_consolidation.py. (2) HIDDEN-THRESHOLD vs INSTRUCTION-CLEAN
  tension (QD-01.5 wants magic guards disclosed; QD-04.3 forbids leaking verifier VALUES): resolve by disclosing the
  EXPECTATION QUALITATIVELY in the rulebook (e.g. "collapses well below 700 but not to a handful", "genuine deps /
  blocked work / priority spread, not an all-Ready empty-graph plan") with NO exact numbers (150/650/>=15). (3)
  DECOMPOSITION HYGIENE (QD-06.4/06.6/06.8): describe ROLES/SCOPE/OUTPUT only -- move all HOW rules (edge precision,
  no template-clique, no dual overlaps+cross_references, no merge-on-template) into the RULEBOOK (agents read it, so
  behaviour is preserved AND QD-06.6 passes); make depends_on truthful (edge specialists that read the whole backlog
  must depend on ALL readers, not 4); and never put a depends_on link BETWEEN two nodes in the same parallel_group
  (moved consolidation-reconciler to the wave-planner's group since both only depend on graph-reconciler). (4)
  REALIZED-vs-DECLARED items (QD-06.7 realized spawn depth 3 vs declared 8; QD-07.10 SA prompt trailing-quote
  harness-serialization artifact) CANNOT be closed by editing the task folder -- they need a live SA+MA re-run to
  re-observe (and QD-07.10 may be a harness bug in single_opencode.py, not the task). RULE going forward: author the
  rubric with aggregators from the start so coverage never fights the gap; keep decomposition how-free; disclose
  guard EXPECTATIONS qualitatively; and after any decomposition/instruction/verifier edit, regenerate execution_logs
  (S-07) -- the shipped logs must match the edited 18-check rubric, so a combined SA+MA re-run is required before the
  next QG submission.
- 2026-07-23 | Second QG draft review (structure-only, no-logs zip -> REJECT) | the reviewer split into (A) LOG-ONLY
  fails that a structure-only zip can NEVER pass and (B) real verifier bugs. (A) QD-07.10 + all four QD-09 (SA trace /
  MA trace / gap-integrity / coordination-verdict) + several QD-08 N/A + a QD-08 WARN ALL reduce to "no execution_logs/
  raw_trajectory/result.json present" -- the draft skill treats MISSING logs as a hard-stop VIOLATION, so a no-logs zip
  is auto-REJECT on QD-07/09 regardless of design quality. LESSON: never submit a logs-stripped zip for a full/draft
  gate expecting a pass; only ship logs-free for a design-only sanity read, and always regenerate + include real SA+MA
  logs for the CURRENT rubric before a scored submission. (B) Real bugs it caught that I fixed in verify.py/manifest:
  (1) DEAD CHECKS (QD-10.1) -- 3 fully-implemented deterministic checks (capability_grounded, wave_memo_depth,
  graph_wave_structural) were defined but NOT in the scored CHECKS list, so main() never ran them; an LLM re-tracer
  greps "def check_* absent from CHECKS" -> ALWAYS wire every implemented check in (or delete it). (2) EXACT-STRING
  DEDUP is trivially gamed (QD-10.4): _norm-only dedup (whitespace+lowercase) is defeated by appending the feature_id/
  one throwaway word to boilerplate -> replace with NEAR-DUP detection (content-token Jaccard >= 0.85, _NearDupTracker)
  across distinctness + every per-item depth check. (3) SUBSTRING != RELEVANCE (QD-10.2): a verbatim evidence_quote
  check passes on any >=12-char fragment -> also require the quote to share a content token with the CLAIM it supports
  (rationale/capability for assessments, explanation for edges). (4) REGEX != CROSS-CHECK (QD-10.3): a Blocked note's
  "names a blocker" test was a bare F-id regex (a fixed decoy passes) -> require the cited F-id to actually be in that
  item's own blocked_by set. (5) UNCOVERED MECHANICAL FIELDS (QD-02.3/QD-03.2): every rulebook field with a single
  correct value must be graded -- added repo + demand_tier (derived from comment_count) correctness to anti_fabrication;
  a schema/enum-membership check is NOT a correctness check. (6) PRECISION-ONLY graph (QD-02.3): "don't skip real
  dependencies" needs a RECALL item -- added deterministic dependency_recall over strong same-repo pairs (Jaccard >=
  0.65; loose 0.30 gives ~2.6k unreachable candidates that floor BOTH agents -> tune the threshold so the candidate set
  is genuinely linkable, ~130 pairs). (7) CONFLICT RECORDING (QD-02.3): "record the conflict rather than break order"
  -> folded a conflict_recording sub-score into the wave-plan aggregator. (8) MANIFEST DRIFT (QD-03.6): when you bump
  _SAMPLE_* constants, the manifest's stated sample sizes MUST be updated in lockstep -- the re-tracer diffs them and
  fails on any mismatch; cite the exact constant (min(_SAMPLE_ASSESS=40,N)). (9) FULL-COVERAGE (QD-04.10): sampled
  judges look gameable -> the honest defence (documented, not a scoring trick) is unpredictable per-run seeding (sample
  pass-fraction is an unbiased estimator of the true full-set rate) PLUS full-coverage DETERMINISTIC checks that grade
  all 700 / all edges as the backstop; scaling reward by sample/700 would crush judges to ~0 and destroy the rubric, so
  don't. Net effect: 18 -> 22 checks (13 deterministic + 9 judges = 41%, still <=50% for QD-03.3), deterministic-subset
  self-test gap held/grew (templated 0.157 vs grounded 0.409 = 0.25). RULE: build the rubric CORRECTNESS-not-presence
  from day 1 (enum-membership, verbatim-substring, and bare-regex checks are all gameable proxies -- pair each with a
  value/relevance/cross-field assertion), grade every mechanical field, include a recall item wherever you have a
  precision item, and keep manifest sample sizes byte-synced to the constants.
- 2026-07-23 | Third QG draft review (still logs-stripped -> REJECT; log-only QD-07.10/07.15/09.1-4 unchanged) | the
  re-tracer found a class of bug the first pass missed and it ALL traces to ONE root cause: a SHADOWED duplicate
  `def _uniq_ratio` -- my new near-dup version at L185 was silently overwritten by an OLD exact-match copy at L319, so
  check_distinctness ran the WEAK function the whole time (QD-02.7/03.6/10.1). LESSON: after replacing a helper, GREP
  `def <name>` for a second definition -- Python keeps the LAST binding, so a stray old copy defeats your fix AND makes
  the manifest a lie; run a tiny empirical probe (`_uniq_ratio(['x','x y'])` should be <1.0) as a regression guard.
  Other real bugs fixed: (1) NEAR-DUP EVADABLE VIA DOMAIN VOCAB (QD-10.4): stopword-stripped content-token Jaccard is
  beaten by a template built from the task's OWN schema words (depends/blocked/readiness/priority) + 1 varying word ->
  add a SECOND signal (RAW-word Jaccard, NO stopword strip, all 3+ char words) and treat dup if EITHER >= 0.85. (2)
  VACUOUS RELEVANCE GATE (QD-10.3): `if (qtok & claim) or not qtok` auto-passes any token-poor quote -> drop the escape
  (`if qtok and (qtok & claim)`); a verbatim >=12-char substring almost always has a 6+ word so legit agents are
  unhurt. (3) FIXED ABSOLUTE FLOORS don't scale (QD-10.2): anti_degenerate `>=15` and a wave1 check vacuously true for
  isolated Ready items let a ~15-edge ISLAND max out several sub-scores over 700 items -> scale guards to N
  (max(15,N//20) etc.) and require wave1 items to be dependency-CONNECTED (an endpoint of a real edge). (4) UNENFORCED
  PROHIBITION (QD-02.3): rulebook said "one relationship per ordered pair, never overlaps+cross_references on the same
  pair" with NO verifier -> add a pair-uniqueness sub-score (every rulebook prohibition needs a matching assertion).
  (5) RULEBOOK EXAMPLES LEAK GRADED ANSWERS (QD-03.2): the illustrative schema used F001's REAL repo/issue#/demand_tier
  and a real F077->F011 dependency -> use OUT-OF-RANGE placeholder ids (F901+) and angle-bracket values, never a real
  row, in any example. (6) METADATA SELF-CONTRADICTION (QD-01.20): input_token_estimate 1.5M vs the file's own "~290k
  tokens" (measured 289k) -> set the estimate to the MEASURED corpus size; a reviewer literally measures title+body/4.
  (7) DECOMP "WHAT-NOT-HOW" (QD-06.6): "if X missing, reconstruct it from /workspace/" is conditional RECOVERY = a HOW
  -> describe only role/output/coordination; strip every "if ... then rebuild" clause (also from the auditor). (8)
  FULL-COVERAGE, ROUND 2 (QD-04.10): a FIXED small judge sample still reads as under-sampled-batch-grading even with
  unpredictable seeding -> make the sample COVERAGE-PROPORTIONAL (`_sample_size`= max(base, 15% of pool) capped 60; one
  batch/call so cost scales with tokens not calls) AND document that EVERY sampled axis has a full-coverage
  deterministic companion. (9) why_multi_agent cited a stale "16/18-check" rubric while shipping 22 (QD-07.15 internal
  half) -> keep the check-count + self-test numbers in why_multi_agent BYTE-CURRENT with the shipped verify.py; re-ran
  self-test = templated 0.16 vs grounded 0.38 = 0.22 deterministic-only (judges widen live). RULE: one helper = one
  definition (grep before trusting an edit); scale every guard/sample to corpus size; every example is fictional; every
  metadata number is the measured value; and re-run the self-test after ANY verifier edit and copy its EXACT numbers
  into task.toml.
- 2026-07-23 | Fourth QG draft review (qg_49xa6n4r; QD-01/03/08 now PASS, QD-05 WARN) | remaining REAL bugs fixed, plus
  a GAP-vs-REVIEW tension worth remembering. (1) CROSS-ORG RECALL BLIND SPOT (QD-10.1): recall/duplicate candidate pools
  were all `by_repo`-only, so an agent could skip the task's own stated crux (same capability filed in DIFFERENT repos)
  for free -> add cross-org candidates, BUT the naive version (rare-token overlap >=3, df<=5%) produced 4511 pairs =
  the classic "thousands of unreachable candidates floor BOTH agents" trap (grounded fixture fell 0.38->0.33 with ZERO
  discrimination). FIX: build cross-org candidates from an inverted index over RARE subject-specific tokens (df<=5% so
  GitHub-template boilerplate words are excluded by construction, NOT rewarding the template-clique spam the precision
  checks punish), then use only a STRONG BOUNDED slice (>=6 shared rare tokens, top-60) as the deterministic recall
  denominator; the judge-protected merge-recall can use a looser slice because the LLM filters false pairs. LESSON: any
  recall denominator must be small + genuinely-linkable; a big candidate set is a floor, not a signal. (2) duplicate_of
  is INTENTIONALLY same-repo per the rulebook ("duplicates almost always live in the same repo") -> do NOT "fix"
  check_duplicates_llm to cross-repo; cross-org belongs in CONSOLIDATION (initiatives), so make merge-recall repo-agnostic
  instead. Match the check's scope to the RULEBOOK, not to a reviewer's blanket "same-repo=blind" heuristic. (3)
  KEYWORD-STUFF GROUNDING (QD-10.2): `bool(_content_tokens(raw) & tok)` passes on ONE shared word -> `_shared_enough`
  requires >=2 shared content tokens (fallback to 1 only when a side genuinely has <2 tokens). (4) OR-BRANCH SPECIFICITY
  (QD-10.4): wave-memo `(refs>=2 or attr)` passes on generic vocab alone -> change to `and`. (5) DECOMP OVERLAP/HOW
  (QD-06.1/06.5/06.6): wave-planner AND plan-writer both authored audit_trail.log, plan-writer re-did the auditor's
  consistency job, and wave-planner leaked "do not schedule greedily" (an algorithm HOW absent from instruction.md) ->
  one artifact = one owner, strip duplicate roles, delete any algorithmic hint not in instruction.md. (6) SILENT
  FAIL-CLOSED (QD-02.5): a bare-float reward.txt makes a judge-infra 0.0 look identical to a poor submission -> also
  write reward.json with per-check scores + a `degraded` flag + the infra-failed check names (reward.txt stays the bare
  float the harness reads; failing closed to 0.0 is still correct, we just make it OBSERVABLE). (7) QD-04.10 is
  effectively UNWINNABLE the reviewer's preferred way: their "discount score by ungraded fraction" is a MULTIPLIER =
  banned by scoring-integrity, and LLM-grading all 700 in one call is infeasible -> the only permitted lever is raising
  coverage (cap 60->90, frac 15%->20%) + full-coverage deterministic companions; log it as a known irreducible tension.
  BIG LESSON (gap): review-driven hardening (>=2-token grounding, cross-org recall, memo AND) LOWERS the synthetic
  deterministic self-test gap (0.22 -> 0.18) because the fixtures build no real edges/cross-org links and fire no judges
  -- but it should HOLD-or-WIDEN the LIVE gap since it makes the single agent's templated/shallow/piecemeal tail fail
  harder on exactly the axes the fixture can't exercise. NEVER read the deterministic-only self-test as the live gap;
  it is a floor that the 9 correctness judges (41% of reward) + real cross-org edges sit on top of. Only a live SA+MA
  run settles it -- self-test now templated 0.15 vs grounded 0.33.
- 2026-07-24 | First live run on the 22-check rubric | SA (run_9ed061d1) SUCCEEDED = 0.4391 with 307k input tokens (single
  context genuinely overflowed) and, per the new reward.json, degraded=false / all 9 judges fired live -> a CLEAN, trusted
  SA baseline. SA scored ~0 on exactly the MA-favoring depth axes (distinctness 0.003, readiness-note depth 0.0,
  anti-degeneracy 0.0 with only 8 deps/8 blocked built, wave-memo 0.0, assessment-depth/sequencing/shortlist judges 0.0,
  cross-org recall 0.02) while doing the easy breadth well -- i.e. the rubric discriminates cleanly. BUT both MA attempts
  died on CLOUD INFRA, not the task: run_ad62 CANCELLED early ($2.05), and run_d86f "SUCCEEDED" at 0.0167 because the
  Fireworks endpoint returned `AI_APICallError: rate limit exceeded ... isRetryable=false` across EVERY session
  (explore/general/primary) at 05:47Z, disposing the instance mid-reading-tier so nothing reached /logs/agent/ (verifier
  correctly saw empty deliverables). The partial trajectory PROVES the MA pipeline works (reading-lead-a dispatched 16
  readers writing grounded, schema-valid, self-validated assessments) -- it just never finished. LESSONS: (a) a 0.0
  "SUCCEEDED" MA with ~140k tokens / ~$0.13 (vs a real ~2.4M tokens / ~$11) is an INFRA kill, not an agent capability
  result -- always check in_tok/cost + the tail of agent/opencode.txt for `rate limit exceeded` before concluding anything
  about the gap or re-architecting. (b) reward.json degraded=false is CORRECT here even though the run was infra-killed:
  the emptiness is absent deliverables (agent/run side), not a verifier API failure, so the flag rightly separates "judge
  couldn't run" from "nothing to judge". (c) mascloud's live streamer crashes on Windows with UnicodeEncodeError (cp1252)
  -- cosmetic only, the cloud run is unaffected; set PYTHONUTF8=1 / PYTHONIOENCODING=utf-8 for the client next time. (d)
  Do NOT burn the daily quota re-running into an active rate-limit wall; re-run MA at off-peak. Gap still UNMEASURED live
  (need one clean MA); projection from SA's headroom remains ~0.23-0.31.
- 2026-07-24 | tune / offline re-grade | Hypothesised two checks (readiness_note_depth, sequencing judge) were
  "mis-designed" because they zeroed BOTH SA and MA and thus compressed the gap. Built an offline re-grade harness
  (set AGENT_DIR/INPUT_DIR/REWARD_DIR, run verify.py on the already-downloaded real SA+MA deliverables; judges fail
  closed locally, substitute the KNOWN cloud judge scores from reward.json) -- it reproduced the cloud reward EXACTLY
  (SA 0.4391 / MA 0.6102 / gap 0.1711), validating the harness. Then probed the two checks and DISPROVED the hypothesis:
  both agents wrote TEMPLATED boilerplate -- readiness_note was the SAME sentence per Ready item ("F### has no unbuilt
  prerequisites ... can begin delivery immediately", 698/700 near-dup, 1/700 grounded), and MA's wave memos were a fixed
  statistical template ("Wave N delivers 24 proposals. Top repo: (11). X well-specified ... Key items: F###, F###") that
  the sequencing judge CORRECTLY fails as "filler that fits any wave". Both checks are FAIR; relaxing them to pass
  boilerplate would be a QD scoring trick. LESSON: before calling a both-zero check "mis-designed", OPEN THE ACTUAL
  AGENT OUTPUT -- a check that both agents fail is usually catching a shared degeneracy, not a bug; only a check that
  zeros GENUINELY-GOOD output is a real defect. An offline re-grade harness is the cheapest way to test verifier
  hypotheses at ZERO quota, but it can only legitimise verifier fixes -- it can NEVER open the gap by loosening a
  correct check.
- 2026-07-24 | tune / gap diagnosis | Root cause of the 0.17 (not 0.23+) gap is NOT the verifier: (1) both agents share
  boilerplate weaknesses (readiness notes + wave memos), so several axes zero BOTH and dilute the gap; (2) MA REGRESSES
  vs SA on edge/merge precision -- MA emitted 389 edges (319 depends_on) vs SA's 100, so edge-validity 0.00 vs 0.15 and
  merge-precision 0.208 vs 0.542 (classic template-clique edge-spam: each edge-specialist over-produces low-precision
  links with no global precision gate). The only HONEST lever is improving MA's actual output quality (a decomposition
  change that caps/precision-gates edges + forces per-item distinct memos), which REQUIRES a live MA run to measure and,
  by bounded projection, only reaches ~0.23 IF SA does not also rise -- i.e. this task class remains near its ~0.15-0.17
  gap ceiling. RULE: when the offline re-grade shows the checks are fair and both agents share the weakness, the gap is
  a TASK/decomposition-capability problem (ALTERNATE-USE PIVOT territory), not a scoring problem -- escalate the
  spend/park decision rather than burning quota on a marginal decomposition tweak.
- 2026-07-24 | tune / decomposition edge-spam fix WORKED | After the offline diagnosis, sharpened decomposition.yaml
  ONLY (SA untouched, so no SA re-run needed -- SA stays 0.4391): edge-specialists emit an edge ONLY with a concrete
  quotable FROM->specific-TO basis (shared topic / same repo / bare issue-number mention is NOT enough; depends_on
  reserved for a true build-order prerequisite; padding is a defect); graph-reconciler keeps ONE relationship per
  ordered pair and actively prunes generic/boilerplate edges; readiness_note must name the specific blocker (Blocked)
  or concrete deliverability reason (Ready), not a fixed sentence with the id swapped; wave memo must reason about
  THAT wave's named members, not a statistical template. One clean MA run (run_9e1c05c25ee3055b, kimi-k2p7-code, 28.1M
  tok, $10.71, 42m, degraded=false) -> MA 0.6774 (was 0.6102), gap = 0.6774-0.4391 = 0.2383, CLEARS the >0.23 floor.
  The fix reversed exactly the diagnosed failure: edge-validity 0.00->0.85, edge-explanation 0.12->0.93, edge-evidence
  0.04->0.59, distinctness 0.13->0.95, readiness-note 0.00->0.92, wave-memo 0.57->1.00. LESSONS: (a) even when the
  decomposition ALREADY nominally instructs a quality bar, making the failure mode CONCRETE and naming the exact
  anti-pattern to avoid ("a bare issue-number mention is NOT a depends_on", "a fixed sentence with only the id swapped
  does not count") measurably changed a kimi swarm's behaviour where the abstract rule did not. (b) A precision-first
  edge instruction has a SIDE EFFECT on the consolidation tier: merge_recall fell 1.00->0.083 and
  shortlist_justification 0.958->0.0 (the swarm became over-conservative about merging) -- when tightening edge
  precision, EXPLICITLY reassure the consolidation/merge role that genuine duplicate merging is still required, or the
  precision message bleeds across tiers. (c) Margin is thin (+0.0083); it held on one clean run but the merge/shortlist
  volatility means a re-run could move it either way -- LOCK IN a clean passing run rather than re-rolling under a tight
  quota.
- 2026-07-24 | static gate S-08 / CR-08 | rubric_manifest.json check keys MUST use ONLY the three mandatory categories
  static_checks_<n> / reward_hacking_checks_<n> / partial_oracle_checks_<n>, each numbered from 1 with NO gaps, and ALL
  THREE categories must have >=1 entry. Ad-hoc buckets (structural_/graph_quality_/consolidation_/consistency_/depth_/
  llm_judge_) are auto-rejected. verify.py CHECKS names must equal the manifest keys (our _validate.py asserts
  manifest<->verify name+fn), so rename in BOTH. Renaming does NOT change reward values (same functions/order), so map:
  files/schema/coverage/structural -> static_checks; dedup/anti-boilerplate/anti-fabrication/non-degeneracy ->
  reward_hacking_checks; correctness-vs-trusted-text (deterministic recall + LLM judges) -> partial_oracle_checks. RULE:
  author every new task's rubric in these three prefixes from the start.
- 2026-07-24 | static gate S-03 | task.toml [task].description must be 10-500 chars (ours was 1558 -> rejected). Keep
  the description a tight 1-2 sentence deliverable summary; put the long rationale in why_multi_agent /
  human_solving_hours_justification / [verifier] comments, NOT in description.
- 2026-07-24 | E-04 / agent output-cap | An SA can die producing NOTHING even when the instruction already says "write
  progressively": at 700-item scale kimi tried to emit all deliverables inline in ONE turn, hit the 32,768 output-token
  cap (step_finish reason="length"), was truncated before any file-write tool call, and wrote zero files -> reward ~0.017
  (empty submission), all content checks 0. Diagnose via trajectory.json step metrics (a step with completion_tokens ==
  the model's max output = an inline-dump overrun) + confirm no deliverables on disk. FIX (integrity-safe, identical both
  sides): make the instruction FORCEFUL -- explicitly warn that a single-reply dump WILL truncate and lose everything, and
  require incremental file writes with on-disk verification. A gentle "write progressively" is NOT enough; agents ignore it.
- 2026-07-24 | SA crashes empty at scale (not a task defect) | At 700 heavy-JSON-object scale the single agent can fail
  to produce ANY deliverable in three different ways: (a) inline-dump -> output-length cap; (b) after a forceful "write
  incrementally" instruction it instead hits the opencode write/bash tool's JSON PAYLOAD limit ("writing a large script
  causes JSON truncation errors") and burns the whole budget fighting it; (c) a provider-side response.failed stream error
  kills opencode (exit 1 -> NonZeroAgentExitCodeError). All three yield an empty submission (~0.017), which is invalid as an
  SA baseline AND trips E-04/exception gates. This is agent-runtime/provider instability, not a verifier/task bug, and it
  structurally VALIDATES the swarm (MA readers emit small ~22-item payloads and never hit the wall). LESSON: a completing SA
  is not reliably reproducible at extreme scale -- if you already have ONE genuine complete SA run, prefer an E-04 exception
  on it over repeatedly re-rolling SA (each re-roll is a quota slot likely to crash empty). Keep per-item deliverable
  payloads modest so a completing SA is attainable.
- 2026-07-24 | durability via zero-run re-grade | To test whether a thin gap is durable WITHOUT spending quota, re-grade
  EVERY complete SA/MA deliverable you have on the CURRENT verifier (deterministic recompute; judges fail closed). Two
  completing SAs here both landed deterministic 0.25-0.29 (full ~0.44-0.48), proving a completing SA is consistently
  ~0.45 and the "median 0.52" was a stale-weaker-verifier artifact. This turns "will a re-run break the gap?" from a
  gamble into a measured estimate before you pay for a run.
- 2026-07-24 | widen the gap by improving MA, not hobbling SA | When the offline per-check table shows a piecemeal SA
  MATCHING or BEATING MA on a check (here consolidation merge-recall SA 1.0 vs MA 0.083, precision SA 0.542 vs MA 0.292),
  that is an MA-quality gap, not a verifier flaw. Do NOT tighten that check (SA is already >= MA, and MA is weak on many
  others, so tightening shrinks the gap). Instead fix the DECOMPOSITION tier responsible (role/scope wording only, no
  algorithm/leak) so MA does that work better. Grading is fair; the honest lever for a bigger gap is a better swarm.
- 2026-07-24 | execution gate E-04 | A run can be verifier-SUCCEEDED with a real reward yet still FAIL E-04 if its
  shipped agent/opencode.txt (trajectory) does not end with step_finish+stop -- e.g. the agent degenerated into a giant
  hallucinated dump and hit its step/loop budget mid-stream (our SA kimi-k2p6 spewed a fake brand x tech array and
  exited at step 16 with a trailing step_start). result.json can show finished_at + reward + exception_info=null and the
  trajectory still be truncated. E-04 forces a re-run of that trial regardless of the reward, so a low-scoring SA whose
  trajectory is truncated cannot be shipped as-is even though the low score is genuine. LESSON: after every SA/MA run,
  check the tail of agent/opencode.txt ends cleanly (step_finish+stop) BEFORE staging it as an execution log; budget a
  possible re-run when an agent visibly degenerates.
- 2026-07-25 | false-failure triage | a FOURTH way an SA dies empty (beyond inline-dump cap / tool JSON limit /
  response.failed): the model returns a REASONING-ONLY step with no tool call and no text, so opencode logs
  `message="exiting loop"` and ends the session with zero files written. Signature: tiny `n_output_tokens` (~600) in
  result.json, agent wall-clock ~7 min, last trajectory event is a `reasoning` part with a multi-minute
  start->end span, and verifier notes read `coverage: 0/N | <deliverable> missing`. RULE: a 0.0 with NO deliverable is a
  NULL run, never an SA score -- read `n_output_tokens` + the opencode.txt tail BEFORE recording any gap. Corollary: if
  the task CLASS has a known completing-SA baseline (this "assess-N-items + sort + justify" class measured SA 0.72-0.80),
  a 0.0 is definitionally infrastructure, so re-run rather than bank the gap.
- 2026-07-25 | thin-gap diagnosis | when the gap is short of the floor, DIFF THE TWO reward.json PER-CHECK VECTORS before
  changing anything -- sort the 20-odd checks by (MA - SA) and read the NEGATIVE tail first. On be59 six checks ran
  negative and cost 2.035 points = 0.0925 of reward, so MA merely TYING SA on them would have moved 0.183 -> 0.276. The
  instinct is "SA is too strong / scale the corpus"; the measurement usually says "MA is silently losing checks it owns"
  (there: shortlist-justification MA 0.000 vs SA 0.875, merge-recall MA 0.083 vs SA 0.889 -- a decomposition role-coverage
  failure, fixable with ZERO runs). Costs nothing and it is the one diagnosis that distinguishes a decomposition bug from
  a real capability ceiling. Corollary: any check where BOTH sides score ~1.0 or ~0.0 is dead weight paying no gap.
- 2026-07-25 | judge hardening | a "justification/rationale" judge will PASS templated restatement unless its prompt
  explicitly rejects it. be59's shortlist judge passed 87.5% of SA lines shaped `Fund <id> because it delivers <title>:
  <raw body excerpt>` -- a restatement, not an argument. Rewrite such prompts to FAIL any justification that only
  restates what the item IS and require the named decision criteria (impact / specification / unblocking). This is a
  measurement-validity fix, symmetric across SA and MA, NOT gap engineering -- but never drop or reweight a check because
  the SA happens to win it; fix WHAT it measures instead.
- 2026-07-25 | reward-hack audit | before hardening any task, script a NO-READING fixture (labels from metadata, tiers
  from published thresholds, quality proxied by body length, evidence sliced off the head of each body, priority sorted
  by the popularity field) and grade it with the task's own verify.py, judges failing closed. On the retired 60dd
  tournament this banked 7.99/8 structural+reward-hacking points = 0.4768 total; even an all-constant hollow fixture took
  all four static checks and scored 0.306. A verbatim-substring evidence check is ALWAYS script-passable -- pair it with a
  relevance requirement (>=2 content words shared with the claim it supports) or it is a free point.
- 2026-07-25 | local re-grade gotcha | CHECK THE JUDGE KEY IS ALIVE before trusting any local verify.py run:
  `curl -H "Authorization: Bearer $FIREWORKS_API_KEY" https://api.fireworks.ai/inference/v1/models` must return 200.
  A key with the right `fw_` shape can still be expired/revoked (401), and because the judges FAIL CLOSED by design every
  LLM check then reads 0.0 -- an offline re-grade looks like a catastrophic score instead of an infra failure, and a
  fail-closed 0.0 is indistinguishable from a genuinely bad answer in the output. Same trap as the null-run rule: read the
  `FAILED CLOSED` note text, never just the number.
- 2026-07-25 | windows/pwsh | the `openai` SDK in an older local venv raises
  `TypeError: Client.__init__() got an unexpected keyword argument 'proxies'` against newer httpx. For a one-off local
  judge/diagnostic script do NOT repin the venv -- POST to the OpenAI-compatible `/chat/completions` endpoint with stdlib
  `urllib.request` instead. Keeps the shipped verify.py (which runs in the container, where the SDK is fine) untouched.
- 2026-07-25 | idea validation | PROBE THE DELIVERABLE'S PREMISE AGAINST THE REAL CORPUS BEFORE DESIGNING ANYTHING. A
  consolidation/dedup deliverable needs genuine duplicates to exist; an actively-triaged single repo has almost none by
  construction, because maintainers close duplicates on sight. Measured on 3,455 open `microsoft/vscode` feature-requests:
  0 strong near-duplicate pairs, 9 moderate, 25 weak across 112,775 comparisons. Cross-ORG corpora (several independent
  trackers that never see each other) are what accumulate duplication -- a single repo is the opposite case. Spend the
  15 minutes on the probe; discovering this after building the rubric wastes the whole build.
- 2026-07-25 | rubric design | A DETERMINISTIC CHECK THAT REWARDS THE HEURISTIC A LAZY AGENT WOULD USE IS SELF-FULFILLING
  AND MUST BE CUT. A "specification quality must correlate with body length" check paid 1.00 to a fixture that assigned the
  label BY body length -- it measured the shortcut rather than the reading. If a check's expectation can be satisfied by the
  same one-line rule that fakes the field, it is not a correctness check.
- 2026-07-25 | anti-reward-hack | Evidence grounding needs a NON-CONTAINMENT clause, not just verbatim + relevance: if the
  quote is a substring of the rationale it supposedly supports, the rationale IS the source text and the grounding is
  circular. Pair it with an ANTI-EXTRACTION check (share of the claim's 6-word shingles already present verbatim in the
  source; >=0.40 = extract). Without it, "copy the first two sentences of each body" passes grounding, relevance,
  distinctness AND substance simultaneously -- four checks at once, and it out-scores a crude template.
- 2026-07-25 | rubric design | DRAW LLM-JUDGE SAMPLES FROM THE REQUIRED SET, NEVER FROM WHAT THE AGENT WROTE, and count an
  unassessed sampled item as a failure. Sampling `by_fid` means a submission covering 220 of 700 items is judged only on the
  220 it finished, so the judges reward it for stopping early.
- 2026-07-25 | rubric design | COLLAPSE MECHANICALLY-COMPUTABLE CHECKS INTO ONE POINT. Tier-from-a-count, area-from-labels
  and the rollup arithmetic are all scriptable without opening a single record; paying three points for them handed a
  no-reading fixture 0.43. Merging them (and merging capacity with anti-popularity) plus moving the freed slots onto
  full-coverage prose checks dropped the same fixture to 0.26 while the strong fixture stayed at 0.92.
- 2026-07-25 | build workflow | RUN THE PROJECTED-GAP FIXTURE CHECK BEFORE ANY LIVE RUN, and include an adversarial fixture
  per known hack (templated, extractive, partial, and a DEGRADING profile that is genuine for ~200 items then templates the
  tail -- the realistic serial-agent shape). On this task it caught four rubric defects in one pass, each of which would
  have cost a live SA+MA run to discover.
- 2026-07-25 | corpus building | The GitHub search API caps EVERY query at 1000 results (10 pages x 100), so a >1000-item
  corpus must be gathered by partitioning on `created:` date windows and unioning. Unauthenticated search allows ~10 req/min
  and returns 403 on the secondary limit: back off and retry rather than aborting, and checkpoint the cache after EVERY page
  (not every window) plus a completed-window list, because a long crawl gets killed and re-fetching finished windows burns
  the rate limit twice.
- 2026-07-27 | Draft Review prep | Before Draft Review, mechanically enumerate EVERY field the rulebook mandates and grep each
  one against the per-check bodies in verify.py: any field that appears ONLY inside the schema/completeness check is graded for
  existence but not correctness, and any field appearing nowhere is a requirement the verifier silently ignores. This audit
  found three on an otherwise 50/50-passing task (an effort band, a rollup count, and a per-area top-3 list). Fix by folding
  internal-consistency fields into an existing mechanical check and routing judgement fields into an existing LLM judge's
  payload -- coverage rises with no change to the check count and no new deterministic proxy to game.
- 2026-07-27 | packaging | A pre-zip secret/path scrubber MUST separate "this trainer's machine" from "verbatim third-party
  source text", or it blocks on the corpus itself: real GitHub issue bodies are full of `C:/Users/<name>/...` because reporters
  paste their own paths. Hard-fail on the trainer's own identifiers (username, workspace path) in ANY file and on credential
  VALUE patterns anywhere, but treat generic user paths inside the frozen corpus as informational -- editing them to satisfy a
  scrubber would silently break the verbatim-vs-live guarantee. Confirm provenance against the live source before waiving.
- 2026-07-27 | packaging | ZIP for Draft Review BEFORE any execution: execution_logs/ is legitimately absent at that point
  (the six-item root whitelist permits it, it is not mandatory), so a packager should note its absence rather than fail, and
  the task must be re-packaged after the SA and MA runs so S-07 holds at delivery.
- 2026-07-27 | Draft Review triage | Sort findings into DESIGN DEFECTS vs PRECONDITION GAPS before touching anything. On a
  pre-execution submission, roughly half the findings (QD-05.7, QD-07.10, QD-08.24, all of QD-09) are one fact restated --
  "no execution_logs" -- and are closed by RUNNING the task, not by editing it. Fixing the genuine defects first means the
  live run measures the final rubric, so the gap does not have to be revalidated twice (Delivery Pipeline Phase 11).
- 2026-07-27 | Draft Review triage | NEVER edit an honest admission out of task.toml to silence a finding. The reviewer quoted
  why_multi_agent's own "a live SA+MA run is pending" as evidence for three FAILs; deleting that sentence while still having
  no logs would convert a disclosed precondition into a concealed one. Leave it and run the task.
- 2026-07-27 | Draft Review triage | An LLM reviewer's WARN can be simply WRONG -- verify every finding against the artefact
  before fixing it. A flagged "PROCESS_LABELS drift" (verify.py containing a label absent from the published rulebook) was
  refuted by a 20-line set-comparison: both lists were byte-identical at 27 entries. Ship the comparison script as the
  justification rather than making a cosmetic edit that pretends the finding was real.
- 2026-07-27 | rubric design | PHANTOM COLUMNS: any field the rulebook mandates in a Markdown-table deliverable but the
  verifier never reads is free for the agent to fill with anything, and it silently contradicts an instruction that demands
  the deliverables agree. Grade them as cross-file consistency (objective corpus facts + values the submission already
  committed to elsewhere) folded into an EXISTING mechanical point, with denominators floored at the REQUIRED row counts so
  omitting rows cannot raise the ratio. Adversarial check: corrupt only those cells and confirm the point drops (1.00 -> 0.76).
- 2026-07-27 | rubric design | SELF-SELECTED DENOMINATORS are a reward-hacking vector: if a check grades "quality of field X
  among the items the agent labelled Y", the agent shrinks its own workload by labelling fewer items Y. Two fixes together --
  floor the denominator at a baseline PUBLISHED in the rulebook (never a hidden threshold), and move the judged population to
  the whole corpus with a prompt that grades BOTH sides of the label (a vague item waved through with no gap fails on its own
  terms). Probe it: an under-caller fixture must lose points (0.83 -> 0.54), not save effort.
- 2026-07-27 | verifier engineering | "Judges sample 90 of 700" reads as under-coverage to a reviewer even when the estimator
  is statistically sound. FULL COVERAGE is affordable: pack items into batched calls under a per-call CHARACTER budget
  (~120k chars ~= 30k tokens) and run the batches concurrently -- a complete 700-request dossier cost 53 calls / ~1.5M input
  tokens / ~6 min at 4 workers. Never satisfy an under-coverage finding by capping the achievable score to the sampled
  fraction: caps are forbidden by the reward shape. Raise retries (5 -> 8) with exponential backoff first, since fail-closed
  semantics multiply infra exposure by the number of batches.
- 2026-07-27 | verifier engineering | When a judge population comes from agent-authored rows, DEDUPE on the verdict key
  inside the batch driver: otherwise repeating one well-argued row N times fills the population and scores 1.0.
- 2026-07-27 | verifier engineering | A trainer-side static validator that asserts on source LITERALS ("for _ in range(5)")
  fails the moment the constant is named, reporting a regression where the value actually improved. Assert on the RESOLVED
  value (parse `_JUDGE_RETRIES = (\d+)` and compare) so the gate tracks intent, not spelling.
- 2026-07-27 | pre-run analysis | RUN A COVERAGE SWEEP BEFORE THE FIRST SA RUN: grade honest-quality submissions truncated at
  10/20/35/55/80/100% of the corpus and plot the curve. The fixture set (hollow/extract/partial/degrading/strong) only samples
  ONE coverage level and hides how much credit an incomplete run collects. The sweep found a 10%-coverage dossier projecting
  0.41 -- above the sub-0.30 SA target -- which would have wasted the iteration and produced a too-small gap.
- 2026-07-27 | rubric design | COVERAGE-BLIND DENOMINATORS are the partial-run analogue of the self-selected denominator: any
  check computing "of the records supplied, what fraction was correct" pays a FULL point to a dossier that did a tenth of the
  work accurately. Grep every check for a denominator derived from `len(agent_records)` and re-denominate over the REQUIRED
  population. Two such (grounding integrity; the null side of the blocking-gap check) were worth 1.5 free points at 10%
  coverage; fixing them moved that projection from 0.41 to 0.36 and left the complete-dossier score untouched at 0.89.
- 2026-07-27 | rubric design | A long-writing task whose deliverables need ~165k output tokens WILL be cut off mid-write, and
  `json.load` on a truncated array returns nothing -- zeroing every check and violating the partial-credit rule. Add a brace-
  balanced salvage that recovers the complete objects from a truncated file (a cut at 72% recovered 500/700 records, 0.46
  instead of ~0.05). Without it the first SA run measures a truncation artifact, not a capability limit, and QD-09 rejects it.
- 2026-07-27 | packaging (COST: one 2-hour cloud run) | A CRLF `tests/test.sh` makes the kernel look for an interpreter named
  `/bin/bash\r`; bash reports "cannot execute: required file not found", the verifier NEVER RUNS, no reward file is written and
  the trial reports RewardFileNotFoundError -> 0.0 for a submission that may be perfect. Files authored on Windows are CRLF by
  default. Add a static check that `tests/test.sh` starts with exactly `#!/bin/bash\n` and that no shipped script/doc contains
  any CR byte. When normalising, leave a frozen JSON corpus BYTE-IDENTICAL: a raw CR inside a JSON string is illegal, so a
  corpus that parses carries CR only as inter-token whitespace, which is inert -- rewriting it would risk the verbatim claim.
- 2026-07-27 | GAP-KILLER, harness-level (read before designing any scale-based task) | A "single" agent can BUILD ITS OWN SWARM.
  The harness injects the model key into the container as OPENAI_API_KEY (single_opencode.py) because the agent needs it to reach
  its own model, so the agent can `pip install openai` and fan out. Observed on a 700-item task: 18 script-level
  chat.completions.create sites, max_workers=5, across FIVE models (kimi-k2p6, deepseek-v3, llama-3.1-70b/8b, qwen2.5-72b),
  producing 700/700 coverage with ZERO tail degradation and 648KB of JSON from only 86k orchestrator output tokens.
  Consequence: "irreducible reading volume against a fixed context window" IS NOT A DURABLE GAP THESIS -- a 40-line script
  bypasses the context window entirely. Air-gapping does not fix it (allow_internet=false sets network_mode:none, which also
  stops the agent reaching its own model AND fail-closes every LLM judge, since the verifier shares the container). No approved
  sample task sets allow_internet at all, so the exposure is systemic; it only bites once a task is big enough that writing the
  fan-out is worth the agent's while. Design the gap around something a STATELESS PER-ITEM FAN-OUT cannot do, and escalate the
  key exposure rather than trying to out-engineer it in the task.
- 2026-07-27 | gap design (premise test, saved a full build) | The natural answer to the fan-out exploit is to move the gap onto
  CROSS-ITEM work (find the underlying need several requests share), because a shard cannot see members outside itself. Tested on
  the real corpus first: genuine cross-area groups DO exist (RTL text rendering spans F496 accessibility / F562 workbench-ux /
  F573 chat-ai) but plain TF-IDF surfaces them at rank ~10 of the cross-area pairs, inside a candidate pool of only ~3,000. That
  KILLS the thesis: candidate generation is cheap and deterministic, and candidate VERIFICATION is per-pair independent -- the
  exact shape a fan-out eats, and 3,000 pair judgements is LESS work than the 700 deep item assessments the agent already
  completed. GENERAL RULE: any task that decomposes into "generate candidates cheaply, then judge each candidate independently"
  is fan-out-able, no matter how large. Volume, cross-referencing and clustering are all this shape. Only work whose parts depend
  on the RESOLVED answers of other parts resists it -- and that same property erodes the multi-agent arm's breadth advantage,
  which is why this needs a platform fix rather than a cleverer task.
- 2026-07-27 | pre-run analysis | Measure REQUIRED OUTPUT VOLUME, not just input size, when predicting whether a single agent
  struggles. This task needs ~165k output tokens (127k of it one JSON array) against a ~431k-token input and a 262k context:
  the binding constraint is generation across >= 6 separate responses with file state carried between them, which is a
  different failure mode from context overflow and is what the depth band actually catches.
- 2026-07-27 | Gate 1 / premise test 3 | RUN THE FAN-OUT COMPARISON PER CHECK, not just on the total. A total of
  "swarm 0.540 vs fan-out 0.631" says the design lost; the PER-CHECK table says WHY and whether anything is salvageable.
  Ours: fan-out wins 9/14 deterministic checks and loses 0 -- i.e. the rubric has NO fan-out-resistant surface, so no amount
  of retuning the existing checks helps. Build the per-check delta table (`fanout_delta.py`) as a standing Gate-1 artefact.
- 2026-07-27 | Gate 1 / root cause across THREE dead designs | If a rubric's score is essentially a FUNCTION OF COVERAGE, a
  single agent with the injected inference key always wins it, because sharding buys coverage. "Interdependence", "contention"
  and "dependency-carrying levels" all failed for this one reason. Before designing, ask: WOULD A SUBMISSION AT 100% COVERAGE
  AND 25% PER-ITEM ERROR SCORE WELL? If yes, the design is already dead -- the resistant property is not interdependence, it is
  work whose correct answer is UNAVAILABLE at shard time (real external state, real ordering, real latency), which the current
  harness does not provide.
- 2026-07-27 | Gate 3 / correlation test | A single shared error dial in the fixture generator makes the correlation test
  MEANINGLESS: every quality check moves with it, so genuinely-redundant checks are indistinguishable from merely
  coverage-linked ones. Give the generator ONE DIAL PER FAILURE MODE (quote / date / verdict / evidence / set-padding) and
  hold coverage constant across those profiles. Ours went 11/14 clustered -> 4/14 with no rubric change beyond one real fix.
- 2026-07-27 | Gate 3 / rubric design | BIJECTION CHECKS ARE FREE POINTS. If field B is a pure function of field A in the
  reference recomputation (here `basis` was one-to-one with `verdict`), grading both is one point of duplicated signal that
  inflates every profile equally. Diff the reference function's outputs pairwise before finalising the check list.
- 2026-07-27 | Phase 1 / integrity gate | A source verifier that only checks the DOCUMENT corpus leaves the other input
  artifact unverified. Ours proved 156 directives verbatim against govinfo and confirmed the registry URL returned 200 --
  but never matched the 24 shipped airframes to actual registry rows, so those named entities had nothing behind them.
  Enumerate EVERY input artifact containing real-world named entities and verify each against its own source (here:
  registration, model designation, ICAO type code, serial and icao24 matched row-by-row against the OpenSky CSV). A URL
  returning 200 is not evidence that the rows you shipped came from it.
- 2026-07-29 | Gate 2 / DOCUMENT-LEVEL STRUCTURE AVERAGES HIDE A FORMULAIC ANSWER SITE | The shard probe scored federal
  appellate opinions at 0.21 labelled headings per 1k tokens with 7,542-char spans -- correctly, they ARE continuous prose.
  Then the scripted-extraction control hit **85.2% macro accuracy against a 33.3% chance floor** on the graded outcome
  judgment, and 0 of 19 hand-labelled cases defeated every extractor. Reason: the graded answer does not live in the average,
  it lives at a FORMULAIC ANSWER SITE ("We REVERSE the district court's denial of summary judgment"), and disposition
  semantics compose mechanically (reverse + denial-of-X = X granted). A document can be prose everywhere and formulaic
  exactly where the graded answer sits. So measure structure AT THE ANSWER SITE, not across the document.
- 2026-07-29 | Gate 2 / SELF-REPORTED vs CONSTRUCTED checks -- the distinction that actually predicts scriptability | A check
  is scriptable when the source STATES THE ANSWER ABOUT ITSELF (disposition, prong, procedural posture, effective date,
  applicability). A check resists scripting when the TASK CONSTRUCTS the comparison and no sentence in the corpus addresses
  it -- e.g. whether a precedent is distinguishable from a client fact pattern that exists only in the task input. Audit every
  rubric item with: "does any single source document state this answer?" If yes, a script will extract it. Both dead designs
  were built almost entirely out of self-reported checks.
- 2026-07-29 | Gate 2 / KILL CRITERIA MUST BE MARGIN-OVER-CHANCE, never absolute accuracy | "Stop if a script answers >30% of
  graded items" is meaningless for a BINARY judgment, where guessing scores 50% and trips the gate by construction. State
  every scriptability gate as: script accuracy must not exceed the chance floor for that item's class count by more than ~10
  points (macro-averaged). Compute the chance floor explicitly per item and write it next to the threshold.
- 2026-07-29 | Gate 1 / A DOMAIN THAT STANDARDISED ITS OWN REPORTING HAS ALREADY BUILT THE ATTACKER'S INDEX | Measured three
  candidate corpora against the dead AD corpus as a negative control (`phase_2_1_tasks/_corpus_selection/`). Randomised
  clinical trial reports -- which FEEL judgment-heavy because risk-of-bias assessment is judgment -- scored 2.08 reasoning
  connectives/1k tokens, LOWER THAN THE FAA DIRECTIVES (2.26), with 4.09 labelled headings/1k and 28.6x compression. Cause:
  CONSORT. Allocation concealment, blinding and attrition are reported in labelled bounded fields precisely so they can be
  extracted mechanically. BEFORE choosing a corpus, ask whether the domain has a REPORTING STANDARD (CONSORT, PRISMA, XBRL,
  an agency template, a regulatory paragraph scheme) and treat its existence as disqualifying. Winner was published federal
  appellate opinions (CAP static.case.law, keyless, full text + real `cites_to` citation graph): 0.21 labels/1k with
  7,542-char spans, 5.32 connectives/1k, 9.1x compression. ALSO: use two lexicon-INDEPENDENT measures (labelled-heading
  density, shared connective lexicon) so the cross-corpus comparison does not just reflect whichever anchor list you wrote.
- 2026-07-29 | Gate 1 / CAPACITY IS NEVER THE DISCRIMINATOR -- stop designing for context overflow | Post-index shard size is
  fan_in x (break_even/4) tokens, and indexing buys ~10x, so fan-in can grow ~10x and the shard fits again. Measured for the
  winning corpus: 14,000 tokens. So "the single agent runs out of context" cannot be the gap mechanism in ANY corpus. The only
  thing low compressibility buys is FIDELITY LOSS -- degraded shards produce worse judgments -- and that converts to score
  ONLY IF the rubric grades the JUDGMENT (holding vs dicta, is this authority distinguishable on our facts) and NOT the
  extractable facts (name, date, disposition, citation). Grading extractable facts reproduces the failure exactly.
- 2026-07-29 | infra / never retry into a 429, and never trust DEMO_KEY for bulk | govinfo's api.data.gov DEMO_KEY died after
  a few requests; the retry-with-backoff loop burned the hourly quota and the fetch hung ~8 min printing nothing. Two fixes,
  both permanent: (1) raise a distinct RateLimited error on HTTP 429 and STOP -- retrying deepens the ban; (2) prefer keyless
  bulk mirrors over keyed APIs for corpus work (static.case.law, federalregister.gov API, NCBI E-utilities, and govinfo
  /content/pkg/ paths are all keyless; govinfo /search and /packages are not). Also: `| Out-String` buffers the WHOLE pipeline,
  so progress prints are invisible -- redirect to a log file with `*>` and read the file instead.
- 2026-07-29 | Gate 1 / THE SHARD PROBE — run this BEFORE choosing a corpus, it is ~1 hour and it would have killed all
  three of our dead designs | Two measurements, and the second is the one that is easy to skip and fatal to skip. Tool:
  `phase_2_1_tasks/task2/_trainer_artefacts/shard_probe.py` (corpus-agnostic, point it at an input_artifacts dir).
  (Q1) FAN-IN: how many source documents must ONE OUTPUT UNIT integrate, x median document length. If that shard fits in
  one context, a fan-out worker reproduces the swarm's per-unit work exactly and the gap is 0 BY CONSTRUCTION. Ours: best
  output unit had fan-in 18 (max 33) x 4,462 tokens = 147k worst case, fits 262k; we would have needed fan-in 59.
  (Q2) COMPRESSIBILITY — THE DECIDER: build the most compact per-document extract that still answers every graded field and
  measure it against full text. Ours compressed **22x (4.5% of full text) with every graded field intact**, so the worst
  shard rebuilds from extracts at 6,864 tokens. **Q2 failing makes Q1 irrelevant**: a two-stage fan-out indexes first, then
  shards over the index, so no achievable fan-in rescues a compressible corpus.
  DOMAIN-SELECTION COROLLARY: avoid corpora whose documents are DESIGNED for mechanical extraction — regulatory directives,
  spec sheets, structured filings, anything checklist-shaped — because their compression ratio is enormous by design. Hunt
  for domains where the REASONING IS THE CONTENT and a summary provably loses the basis for the judgment (judicial opinions,
  audit findings, clinical assessments). Target compression ratio near 1x, not 22x.
- 2026-07-29 | Gate 0 / TWO INDEPENDENT ATTACK CLASSES — do not let a verified platform exposure become the excuse for a
  design failure it did not cause | (A) KEY-DEPENDENT: the agent finds the injected inference credential and fans out.
  Verified in `run_78db99ab49695894` — command #2 of the run was `env | grep -i openai; env | grep -i api; env | grep -i key`,
  then `pip install openai`, then `nohup python3 /workspace/worker.py 0 88 &` in 88-item shards; 66 `chat.completions.create`
  sites, 83 `api.fireworks.ai`, 0 `api.openai.com`, and a tool histogram of **read:3 / bash:34 / write:19** over a 431k-token
  corpus. Scoping the key kills this class. (B) KEY-INDEPENDENT: a deterministic script or a TF-IDF lookup answers the graded
  item with ZERO model calls — measured at 85.2% (extraction) and 4.5x chance (retrieval), plus 22x lossless corpus
  compression. NO platform change touches class B. RULE: before escalating a harness exposure as the cause of a dead gap,
  test class B separately; if a zero-inference script wins, the platform is not your blocker and the fix will not open the gap.
  COROLLARY on evidence hygiene: distinguish what the agent DID (measured from the trajectory) from what it WOULD have scored
  without the key (inference). We never ran the key-withheld counterfactual, so the latter was never measured — say so in the
  escalation rather than letting the strong trajectory evidence carry an unmeasured claim.
- 2026-07-29 | Gate 2b / CONSTRUCTED COMPARISONS ARE ALSO SCRIPTABLE — via RETRIEVAL, not extraction | The fix for a
  self-reported check is to ask something the source never states about itself (given a client fact pattern that exists only
  in the task input, which precedent controls?). That defeats extraction, and it still failed: plain TF-IDF and BM25 hit
  **50.0% macro / 41.7% flat against a 11.1% chance floor** (9 classes). The attack is not extraction, it is
  RETRIEVE-THEN-READ-OFF: find the most lexically similar source, then read its disposition from the formulaic answer site
  gate 2a already showed is 85% extractable. Composite ceiling 50.0% x 85.2% = 42.6%. RULE: when designing a constructed
  check, run a RETRIEVAL attack (TF-IDF / BM25 / Jaccard, ~40 lines) in addition to the extraction attack. A judgment that a
  nearest-neighbour lookup answers is not a judgment. Tool: `_corpus_selection/constructed_control.py`.
- 2026-07-29 | Gate 2b / NEVER WRITE THE ATTACK AFTER WRITING THE TEST SET — I did, and it inflated the kill number by 33
  points | My hand-written rule attack scored 83.3% macro vs the honest TF-IDF 50.0%, because I authored the regexes AFTER
  authoring the fact patterns and unconsciously keyed them to my own vocabulary ("four seconds", "screwdriver", "firm grip").
  That is an oracle in disguise: a real attacker does not hold the test set. It cuts BOTH ways — it can also make a design
  look unsafe and get a good corpus discarded. RULE: freeze the labelled set, then write attacks using ONLY the corpus and
  the task statement; any attack whose features quote the test items is void. Report the best UNFITTED attack as the result.
- 2026-07-29 | Gate 2b / THE ONLY PROPERTY THAT DEFEATED EVERY UNFITTED ATTACK: a material fact differs despite high surface
  similarity | Retrieval recovered 7 of 8 items built on one source's core and scored **0% on the `none_controlling` class** —
  items where vocabulary points hard at a source that does NOT govern because one legally material fact differs (warnings
  were given; the suspect was armed; nobody was injured). This is the seed for any future fan-out-resistant check, and it
  also implies the epistemic-honesty item ("no authority in this set governs") is the single hardest thing to script.
  COUNTER-RULE, learned the expensive way: do NOT then rebuild the rubric out of only the items that survived. Five designs
  died here, each surviving only on a subset selected AFTER watching an attack succeed elsewhere. Selecting the hard subset
  post hoc is goalpost-moving and it is how a task ships with a gap that evaporates on the first real run — invoke the
  ALTERNATE-USE PIVOT and escalate with the run history instead.
- 2026-07-29 | Gate 1 / A PRINTED SCOPE FIELD DECIDES A "COUNTERFACTUAL" — pre-register your expectation, then check it, because
  intuition about scriptability is unreliable in BOTH directions | I pre-registered that C2 (NTSB: which past accidents would this
  safety recommendation have prevented) would PASS the extraction gate, reasoning that "a counterfactual is stated nowhere." It
  FAILED at **57.0% macro vs a 35% bar (32 points over chance)**. Cause: the recommendation is scoped to *14 CFR Part 135
  operators*, and every report prints its operating rule part, so a regex over `Part 121|135|91` decides `out_of_scope` for 20 of
  29 items with zero reasoning. Symmetrically I pre-registered that C3 (registry↔publication outcome reconciliation) would FAIL on
  cheap string comparison; its answer-site similarity came in at **27% median term-recall, 2/10 pairs above 60%** — it survived.
  Both priors wrong, opposite directions. RULE: never substitute a plausibility argument for the gate, and never skip a gate
  because you are confident — write the expectation into the pre-registration so being wrong is recorded rather than absorbed.
  COROLLARY: when a graded judgment is scoped by any printed categorical field (operating rule, jurisdiction, product class,
  eligibility criterion), the majority class is decided by that field alone; check the class-balance-vs-field crosstab BEFORE
  labelling 29 documents.
- 2026-07-29 | Gate 0 / RUN THE COMPRESSIBILITY PROBE OVER THE PAIR, NOT THE LONGER MEMBER | C3 is a *paired* corpus (ISRCTN
  registry record ↔ PMC full text). My probe measured only the paper and reported `0.00 labels/1k tokens` — apparently perfectly
  unstructured prose. The registry half is literally XML: `<variable>`, `<method>`, `<timepoints>`, i.e. maximal structural
  addressability, the exact property that made the FAA AD corpus 22x-losslessly compressible. Gate 0 therefore UNDERSTATED
  addressability and would have waved through a corpus whose answer key is half machine-readable. RULE: for any multi-source
  corpus, compute structure metrics per source and report the MOST addressable one, because that is the one an extractor attacks.
- 2026-07-29 | Gate 1 / CHEAP PRE-CHECKS THAT NEED NO LABELS SHOULD RUN BEFORE THE LABELLING ROUND | Hand-labelling C2 cost a full
  pass over 29 accident reports and the gate then died to a one-line regex. For C3 I inverted the order and ran two label-free
  measurements first: (M1) ANSWER-SITE SIMILARITY — token recall between the two sources' formulaic answer sites, which if high
  means a fuzzy matcher solves the judgment; (M2) TEMPORAL VALIDITY — is the "pre-registered" record still being edited AFTER the
  publication it is supposed to precede, which if true means the ground truth was retro-fitted and there is no deviation to find.
  M2 caught **8 of 21 records edited after their paper published** (one updated the day after), a 38% contamination rate invisible
  to every other metric. Neither pre-check can be contaminated by authoring the test set, since neither uses it. RULE: order gate
  1 as label-free kills first, labelled attack second. Also: whenever a task premise is "source A predates source B", MEASURE the
  dates — do not assume the registry/archive froze when it says it froze.
- 2026-07-29 | infra / A BACKGROUND CORPUS BUILDER WILL SILENTLY OVERWRITE YOUR REPAIR — kill it before you fix its output | I
  fixed a parser bug, re-ran the repair, and the fields came back EMPTY. Cause: the original builder was still running in the
  background and rewriting the whole cache file each iteration from a dict it had loaded at start-up, using the OLD parser still
  resident in its interpreter. Editing the source does not change a running process. RULE: before repairing a cache in place,
  confirm no writer is live (`Get-Process -Id <pid>`), and prefer append-or-merge writers over whole-file rewrites for anything
  long-running. Symptom to recognise: a repair script that reports success while the consumer still sees stale/empty data.
- 2026-07-29 | Gate 1 / CHECK THE XML TAG FOR ATTRIBUTES BEFORE CONCLUDING A FIELD IS SPARSE — I nearly discarded a live candidate
  on my own regex bug | `re.findall(r"<outcomeMeasure>(.*?)</outcomeMeasure>")` matched nothing because the real element is
  `<outcomeMeasure id="e1f13ce9-...">`. Consequence: 0/18 registered primary outcomes appeared to carry a timepoint, which is the
  single field C3's whole judgment depends on, and I was one step from killing the candidate. After `<outcomeMeasure\b[^>]*>`:
  **38/38**. RULE: when a probe reports a field is 0% present, verify against the RAW payload before acting — a structural-zero is
  far more often a parser bug than a real absence, and killing a candidate is irreversible in a workflow whose stop rule forbids
  rescue. Cheap habit: print the raw head of the containing block alongside every "field absent" finding.
- 2026-07-29 | Gate 1 / **PUBLISHING A DECISION PROCEDURE IS ITSELF THE LEAK — the rubric can be the scriptable part even when
  the judgment is not** | C3 (registry↔publication outcome reconciliation) failed at **57.2% macro vs a 35% bar** and the
  winning attack was not a clever feature: it was *my own four-class precedence rule* ("absence, else measure identity, else
  timepoint identity, else consistent") implemented in 12 lines. The rule is part of the task statement, so any attacker may
  implement it; once implemented, all that remains unspecified is fuzzy string matching at each step, which is exactly what
  deterministic code does adequately. Proof the underlying judgment was still sound: the script misses precisely the items
  that need reading — a trial registering the Olerud–Molander score at *five weeks post-randomisation* vs a paper reporting it
  at *seven weeks post-surgery* (term overlap 5/6, so every similarity method calls it a match), and a registered *medial*
  compartment endpoint reported as *medial or lateral*. RULE: a closed set of N verdict classes plus a stated precedence rule
  hands the attacker a 1/N floor AND the algorithm. Do not gate a class set; gate the ARTEFACT. If the deliverable is "assign
  one of N labels per unit", the rubric is scriptable no matter how unscriptable the underlying reasoning is.
- 2026-07-29 | Gate 1 / MACRO-AVERAGING OVER A THIN CLASS WILL MANUFACTURE BOTH PASSES AND FAILS — always print the per-class
  row and re-check the verdict without the thin class | C3's headline 57.2% macro came 25 points from a **2-item** class the
  absence heuristic happened to get 2/2. Meanwhile the same attack's FLAT accuracy (53.6%) was *worse* than always guessing the
  majority class (64.3%) — i.e. in absolute terms the script reproduced the judgment badly and still cleared the bar. The kill
  only stood because it was re-checked over the three stable classes (43.0%, still > 35%). RULE: declare the thin-class rule
  BEFORE labelling (I did, which is why this was catchable), report macro + flat + per-class together, and never let a verdict
  rest on a class with <3 items. Corollary: with an imbalanced label set, macro and flat can point in OPPOSITE directions;
  decide which one the pre-registration binds you to before you see either.
- 2026-07-29 | corpus hygiene / A TRIAL PUBLISHES ONE PRIMARY REPORT AND MANY SATELLITES, AND EVERY SATELLITE PASSES YOUR
  FILTERS | Of 3,082 PMC candidates citing an ISRCTN, 612 were protocols, 286 reviews, 95 secondary analyses — and after three
  successive hygiene passes, a measured **26% of the 89 survivors were still ancillary** (recruitment analyses, prediction
  models, data-linkage method papers, process evaluations). Each pass found a NEW class only by reading: Cochrane reviews hide
  in the JOURNAL name not the title; BMJ-Open protocols announce themselves with "Methods and analysis" + a SPIRIT checklist,
  not the word "protocol". Why it is fatal rather than annoying: for a satellite, "the reported primary outcome differs from
  the registered one" is trivially true and reflects the paper's SCOPE, not the misconduct being graded. RULE: when the corpus
  unit is "a document about entity X", census the DOCUMENT TYPES before labelling and require a non-circular discriminator for
  the type you want — and if the only discriminator for "the document I want" is the label itself, the corpus is unusable.
- 2026-07-29 | corpus / TWO SCHEMAS IN ONE REGISTRY, AND THE STRUCTURED ONE WAS THE MINORITY (12 of 130) | ISRCTN stores
  outcomes either as structured `<primaryOutcomes><outcomeMeasure><variable>/<timepoints>` or as a free-text prose blob under
  `<primaryOutcome>` — SINGULAR. Reading only the plural/structured form silently discarded **168 records** and made a valid
  corpus look 5x too small. Two consequences beyond the bug: (a) the free-text form embeds its own dated history ("Current
  primary outcome measure as of 23/10/2018: … Previous … as of 14/09/2018: …"), so a pre-publication version is partly
  recoverable even when the API refuses to serve one; (b) it retires an earlier worry that the registry half was "maximally
  addressable XML" — 120 of 130 are prose. RULE: enumerate the DISTINCT SHAPES a field takes across the population
  (`sorted(set(re.findall(r"<(\w*Outcome\w*)[ >/]", raw)))`) before writing the parser, and never generalise a schema from the
  most recent records — recency correlates with the newer schema.
- 2026-07-29 | corpus / "PIN THE HISTORICAL VERSION" IS AN ASSUMPTION, NOT A CAPABILITY — probe it before recommending it | I
  wrote into a results doc that C3's temporal contamination (records edited after publication) could be fixed by "pinning the
  registry version current at submission date". It cannot: ISRCTN ignores `version=`, 404s on `api/trial/<id>`, 400s on
  `format/full`, and serves a 1.2 KB JavaScript shell as the public record. The remedy available was EXCLUSION (253 of 876
  scanned pairs dropped), which is necessary but NOT sufficient — a record last edited before publication can still have been
  edited after results were known, and these carry v9–v100. RULE: any recommendation of the form "we can just retrieve the
  earlier state" must be probed with a real request before it is written down, and if only exclusion is available, state that
  the resulting corpus has a residual integrity weakness rather than calling the problem solved.
- 2026-07-29 | regex / `\b` DOES NOT MATCH BEFORE A PLURAL 's', AND IT DOES MATCH BEFORE A HYPHEN — two opposite failures, one
  afternoon | (1) `primary outcome\b` never matches "primary outcomeS", so a filter built on it rejected papers whose
  declaration was plainly present ("Primary outcomes were final diagnostic accuracy…") — 266 papers excluded as "no declared
  primary". (2) `re.split(r"(?=<article\b)")` shredded every batched PMC response into 11-character fragments, because `\b`
  DOES hold between "article" and "-" in `<article-id>`, `<article-title>`, `<article-meta>`. RULE: for optional plurals write
  `s?\b` explicitly; to match an XML tag name write `<tag[\s>]`, never `<tag\b`. Symptom to recognise for both: a filter that
  rejects ~100% or ~0% of input — always inspect a dozen rejected examples before trusting a filter's count.
- 2026-07-29 | infra / KILLING THE `py` WRAPPER LEAVES THE `python` CHILD RUNNING, AND IT KEEPS WRITING YOUR CACHE | I stopped
  a build by its reported PID, deleted its output, started a fresh run — and the new run reported tier-1 counts containing a
  code only tier 2 can emit. Cause: two orphaned `python` children from earlier "killed" runs were still rewriting the same
  cache. `Get-Process python,py | Select Id,StartTime` showed 7 live interpreters. RULE on Windows: kill by IMAGE NAME
  (`Get-Process python,py | Stop-Process -Force`) and assert the count is zero before touching a shared cache. Recognisable
  symptom: an impossible value in a report — a count attributed to a stage that cannot produce it means a second writer.
- 2026-07-29 | pipeline / TIER YOUR FILTERS BY COST OR THE BUILD WILL NOT FINISH | First build did one HTTP round trip per
  candidate over 1,748 candidates: 3 pairs in 10 minutes, projecting to ~7 hours. Restructured into batched esummary (150
  ids/request → title+date, apply title filters), batched efetch (12 ids/request → full text, apply text filters), then the
  unavoidable per-item registry fetch for survivors ONLY: 130 pairs in 14 minutes. RULE: order filters cheapest-first and put
  every batchable API call in front of every per-item one — 32% of this pool died on the TITLE alone, so fetching full text
  first was paying for 983 documents that a single regex could reject.
- 2026-07-28 | Gate 1 / SIZE THE DECIDING SLICE, not the corpus (this is the single most useful pre-build measurement) |
  A corpus can be 2.9M characters while the information that actually DECIDES the answer is 14k characters. Ours: paragraph
  (b) of all 156 directives -- the whole "cross-corpus reconciliation" the gap thesis rested on -- totals 3,571 tokens, i.e.
  1.4% of one context window; (b)+(c) together are 6.4%. So the "merge that cannot fit in one slice" fit ~73 times over, and
  the 8 relationship readers were covering a one-reader problem. BEFORE building, extract ONLY the fields/paragraphs that
  determine each graded answer and measure THAT in tokens. If the deciding slice fits in one context, the task has a
  correctness trap (punishes carelessness) but NO capacity barrier, and no amount of total-corpus size changes it. Bulk that
  is per-unit input to per-unit writing is parallel work, not coordination work.
- 2026-07-28 | escalation / harness fact | The agent container holds the inference key under TWO independent names: the run
  config passes `--ae FIREWORKS_API_KEY=...` (agent env, its own name) AND `single_opencode.py:259-262` aliases it to
  `OPENAI_API_KEY`; `multi_opencode.py:307-310` does the same for the multi arm. The b1b7 agent authenticated with
  `$FIREWORKS_API_KEY` directly, so a mitigation that only removes the `OPENAI_API_KEY` alias changes nothing. When
  proposing or verifying any credential fix, check BOTH names in BOTH files, and verify by `curl` from the agent shell
  rather than by reading the injection code.
- 2026-07-28 | Gate 1 / integrity | If a measurement falsifies a claim already written into `why_multi_agent`, CORRECT THE
  CLAIM IN PLACE and record the number that falsified it -- do not leave it for the reviewer to catch and do not soften it.
  Ours asserted a merge "cannot be done inside any one reader's slice" when it demonstrably can.
- 2026-07-28 | Gate 1 / two levers that LOOK like fan-out defences and are not | (1) DEPENDENCY DEPTH: a 9-level DAG creates
  ORDERING, not a parallelism requirement -- one agent walks the levels sequentially. (2) RE-KEYING the deliverable so its
  unit cross-cuts the corpus unit (per-airframe output over per-directive corpus) is defeated by a two-stage fan-out: shard
  per corpus unit to build a compact index, then shard per output unit over the index. Any answer that is a RELATIONAL JOIN
  over per-unit facts parallelises, because joins parallelise. Verify a candidate lever exists in the corpus AT SCALE before
  designing on it: our termination-credit idea (per-tail relief depending on another AD's per-tail outcome) had exactly 4
  edges, 1 usable, 0 conditioned.
- 2026-07-27 | Phase 6 / mascloud infra (COST: 2 run slots) | `DaytonaNotFoundError` + "Error stopping sandbox: Sandbox
  with ID or name ... not found" + "Failed to download logs" with **0 trials / 1 exception / 0 tokens** in 1-4 minutes is a
  BACKEND SANDBOX FLAKE, not a task defect -- the run is still billed against the daily quota and still reports
  `SUCCEEDED reward=0.0`, so it is easy to misread as a task failure. Triage before re-architecting anything: (a) `tokens
  in/out=0/0` means the agent never started, (b) diff your `environment/Dockerfile` against a task that has run
  successfully, (c) check the packaged folder size. If all three are clean it is the backend. Launching the single and multi
  arms simultaneously is suspected of provoking it -- prefer SEQUENTIAL launches and keep a slot in reserve.
- 2026-07-27 | verifier engineering (would have zeroed 30% of the rubric) | NEVER hard-code a single judge model slug.
  `qwen3-235b-a22b` now 404s "not found, inaccessible, and/or not deployed", and the b1b7 in-container trajectory shows every
  non-Kimi slug it tried 404ing too. A retired slug fails CLOSED on every judged check, so a provider deployment change reads
  as a submission defect. Resolve the FIRST REACHABLE model from an ordered list of same-rule (different-family) candidates,
  cache it per process, add exponential backoff, and tolerate JSON wrapped in prose -- but never include the agent's own
  family in the list, so "nothing reachable" still fails closed.
- 2026-07-27 | gap tuning / decomposition | OVER-PRUNING INSTRUCTIONS CAN PUSH THE MULTI AGENT BELOW THE SINGLE on a
  recall axis. Telling the edge/graph/consolidation tiers "a smaller graph is correct, drop weak links" (added to fight
  boilerplate spam) made MA emit FEWER genuine edges and FEWER cross-org merges than SA (dep-recall 0.08, merges 22 < SA 27),
  suppressing the very axes MA should win. Fix: instruct for BOTH precision AND recall -- "a missed genuine link is as much a
  defect as a padded one; drop only ungrounded/boilerplate ones" -- and confirm by READING both agents' actual outputs
  (initiative counts, graph size) side by side, not by trusting the check scores alone.
- 2026-07-27 | gap tuning / scale | When a capable model COMPLETES the corpus (SA ~0.55 at 700, no budget overflow), the
  context-overflow thesis does not open a >0.23 gap -- the SA lever is CORPUS SIZE, not decomposition. Scale the frozen corpus
  with MORE REAL verbatim data (here 700 -> 1050 via unauth GitHub REST list API: 100 issues/request, ~60 req/hr rolling +
  stricter secondary 403/429 burst limit, per-repo cap for cross-org diversity, dedupe on (repo, issue_number); VA repos have
  the deepest backlogs for volume). Going past F999 needs 4-DIGIT FIDs: widen BOTH `^F\d{3}$` and `\bF\d{3}\b` to `{3,4}`, and
  fix any lexical `sorted(fids)` to a NUMERIC key (`int(f[1:])`) -- mixed-width strings sort wrong ("F1000" < "F999"), which
  silently scrambles tail-biased judge sampling. `f"F{i:03d}"` already emits F1000+ correctly. Make EVERY 700-tuned verifier
  constant scale with N_FEATURES (count band, merge target, anti-degeneracy floors) so difficulty is preserved. Propagate N
  through instruction.md, the rulebook, sources.json, task.toml, rubric_manifest.json AND the decomposition reader/lead/edge
  FID ranges; grep for stray old-N (excluding `[:700]` slices and `for 700` scaling annotations). Count propagation is STATEFUL
  once applied -- a second bump (946->1050) is an old-N->new-N sweep, not a fresh 700->N one.
- 2026-07-27 | gap tuning / scale REGRESSION (COST: 2 run slots, both empty) | SCALING THE CORPUS TOO FAR BREAKS BOTH ARMS
  INTO EMPTY CRASHES (invalid 0.0167), NOT a valid-low SA. At 1050 items (~388k tokens): SA read the corpus, wrote a helper
  script, then burned a whole step on a ~10-min reasoning spiral and the opencode loop hit its STEP/ITERATION LIMIT (step 10)
  and exited mid-write ("loop exit with orphaned interrupted tool tool=write", "Tool execution aborted interrupted:true") --
  0 deliverables, tokens out=9.2k. This is NOT the output-token cap (reason:"length") and NOT a rate-limit; it is the harness
  step-loop budget. MA was worse: the orchestrator read the decomposition, spent one ~55s reasoning block getting genuinely
  CONFUSED by the routing rules ("I AM the planning lead", "there's a contradiction" between spawn-all-sub_tasks vs
  managers-spawn-their-own-workers), then emitted step_finish reason:"stop" at step 2 and disposed the instance WITHOUT
  DISPATCHING A SINGLE `task` sub-agent -- 215 output tokens, 1m46s, 0 deliverables. Two lessons: (1) The last VALID pair is
  at 700 (SA 0.5515 / MA 0.6667 = 0.1152 gap); a bigger corpus did not open the gap, it just pushed both arms past the point
  where they reliably produce ANY output -- an empty crash is invalid and useless as a baseline, strictly worse than a valid
  low score. Do NOT chase the gap purely with corpus size once the arms start crashing empty; revert to the last-completing
  scale. (2) The MA orchestrator can STALL AND STOP if the decomposition/routing rules read as self-contradictory (orchestrator
  spawns every sub_task directly vs. managers spawn their own workers) -- this is a real clarity bug that suppresses MA
  independent of scale; make the spawn model unambiguous before spending another MA slot.
- 2026-07-28 | decomposition / MA reliability (root cause + fix) | THE HARNESS ORCHESTRATOR PROMPT IS THE SOURCE OF TRUTH
  FOR THE SPAWN MODEL -- read `harbor/.../swarmbench/prompts/opencode_hierarchical.md` before authoring a hierarchical
  decomposition. It enforces: orchestrator -> managers (`subagent_type: general`), managers -> leaf workers
  (`subagent_type: explore`, hard-BLOCKED from spawning), AND "each sub_task = exactly one task call." Those two rules
  CONTRADICT each other for any explore node that has no general-manager parent: the orchestrator can neither leave it
  unspawned nor (per the manager convention) spawn an explore leaf itself, so it stalls debating the ambiguity and stops
  with an empty submission. Our decomposition had only 3 general managers (planning-lead + 2 reading-leads) but 10
  post-reading explore nodes (4 edge specialists + graph-reconciler + consolidation + wave + funding + auditor + plan-writer)
  with NO manager assigned -- ORPHAN EXPLORE NODES. Fix (Model B, preserves realized depth so it does not trip QD-06.7):
  add a general "tier manager" for every orphan cluster (here `graph-lead` owns the 4 edge specialists + graph-reconciler;
  `integration-lead` owns consolidation + wave + funding + auditor + plan-writer), point each cluster's `depends_on` at its
  manager, and add a top-of-file BINDING "ORCHESTRATION MAP" naming exactly who spawns whom + a headless anti-stall rule
  ("every turn except the final gate must make >=1 task call; never end on reasoning/plan/role-debate"). Rule of thumb:
  EVERY explore sub_task must have a general-manager parent, and the orchestrator should spawn ONLY general managers. Update
  task.toml estimated_sub_agents (== sub_task count) and dag_depth (longest depends_on chain) to match, and re-run
  `_validate.py` (no cycles, counts match, manifest<->verify match). This is an MA-only channel (decomposition.yaml is not
  read by the single agent), so it cannot narrow the gap by helping SA.
- 2026-07-28 | Model B VALIDATED + long-run infra exposure (COST: 1 MA slot to a backend flake) | The Model B
  manager-topology fix WORKED: the MA orchestrator that previously stalled at step 2 (1m46s, 0 sub-agents) ran the FULL
  hierarchical pipeline for **2h30m** (agent_execution 08:28:27->10:58:38) -- no stall, real dispatch. Confirmation that
  giving every explore node a general-manager parent removes the orchestrator's spawn-model ambiguity. BUT the run still
  scored 0.0 via a pure backend flake: `exception_type: DaytonaError`, `Failed to get session command: (502) Bad Gateway`
  at 10:58:39 (near the end), `verifier: null`, tokens 0/0, 0 trials / 1 exception, "Failed to download logs". Per the
  existing backend-flake triage this is NOT a task defect and NOT a rate-limit -- it is the Daytona sandbox API 502ing, so
  the run is INVALID (re-run), though it still consumes a daily slot. KEY NEW LESSON: at 1050-scale the MA pipeline (47
  sub-agents) takes ~2.5h, and the LONGER a run lasts the MORE sandbox exec/poll calls it makes, so its exposure to a
  transient 5xx flake scales with runtime. A 2.5h MA is dangerously long -- one 502 anywhere in 2.5h kills the whole run and
  loses all deliverables. Mitigation: prefer a corpus scale where the MA finishes in a shorter window (700-scale MA completed
  and scored 0.6667 in far less time), which both lowers flake exposure AND yields a valid completing pair. Do not read a
  DaytonaError/502 as an orchestrator or task problem; read the agent_execution DURATION first -- a multi-hour agent_execution
  followed by a 5xx at teardown means the pipeline worked and infra dropped it.
- CONTEXT-OVERFLOW GAP LANDED AT SCALE (durable win): after months of a ~0.15-0.20 ceiling where a capable single agent kept
  matching multi, the fix was pure SCALE, not scoring. At 1050 real interlinked issues (~408k tokens) the single agent runs
  out of step/context budget mid-write and produces ZERO deliverables (valid empty run, reward 0.0167, clean step_finish --
  NOT an infra failure, DM-approvable), while the Model B multi-agent decomposes the corpus and COMPLETES (reward 0.5276,
  degraded=false, coverage/schema/audit all 1.00). Gap = 0.5109, honestly earned by a real capability difference, no cap/trick.
  Lesson: when a rubric is clean+discriminative but a good single agent keeps closing the gap, it is a SIZE problem -- scale
  the frozen corpus until one agent genuinely runs out of budget, rather than nibbling the score with rubric penalties.
- A DaytonaError-flaked MA is re-runnable: same task, next slot, retry completed cleanly (run_62a40a3d 502-flaked at teardown
  -> run_2c890d56 same config completed 2h48m and downloaded). Infra flakes do not indict the task; just retry within quota.
- 2026-07-29 | Gate / **THE PARALLEL-JOIN vs CASCADE DISTINCTION — the one question that would have killed four dead designs in
  an hour each** | A dependency where "the answer for A depends on FACTS ABOUT B" is a JOIN: a sharded agent reads all facts in
  parallel and merges, so it is worth ZERO for fan-out resistance. Only "the answer for A depends on the DERIVED DECISION made
  for B" is a cascade, and that requires CONTENTION — a shared resource whose commitment to B denies it to A. Drug shortages
  looked like a textbook cascade (substitute is also short → substitute again) but every such edge is a join on a published
  status field. RULE: before designing anything, write down one graded decision and ask whether computing it needs another
  decision's OUTPUT or merely another record's CONTENT. If it is content, stop — the task is parallel no matter how large.
- 2026-07-29 | Gate / **CONTENTION NEEDS A QUANTITY FIELD, AND CATEGORICAL PROXIES WILL NOT SUBSTITUTE** | The cascade thesis
  died on a schema fact: openFDA carries no volume/capacity anywhere, only `availability` as three categories — and that field
  is absent for every presentation of 171/277 substances and SELF-CONTRADICTORY across presentations for another 54, leaving
  ~52 usable. `shortage_reason` is absent for 191/277. RULE: when a design depends on "X cannot cover both A and B", locate the
  numeric field that proves it BEFORE designing. If it does not exist, the cascade cannot be graded, and inventing the numbers
  is fabrication — an integrity violation, not a design shortcut. Check field COVERAGE and INTERNAL CONSISTENCY, not just
  presence in one sample record.
- 2026-07-29 | Gate / **SPARSITY OF THE FAILING SET IS WHY SUBSTITUTION NEVER BINDS — measure the healthy:short ratio first** |
  Only 208 of the 2,438 substances inside the affected classes were short (8.5%), and median class size was 8, so the expected
  short members per class is well under one: a healthy alternative essentially always exists. 33-40 alternatives were claimed by
  two or more short drugs, yet NOT ONE was itself constrained, so conflicts were exactly 0/196. RULE: for any "the fallback may
  also be broken" premise, compute the broken fraction of the FALLBACK POOL up front. Below ~30% the recursion almost never
  fires and per-unit greedy solves everything independently.
- 2026-07-29 | Gate / A SYMMETRIC RELATION CANNOT EXPRESS A CHAIN, SO "GRAPH DEPTH" WILL LIE TO YOU | My depth metric returned
  11 and "survived", but the path printed the same drug three times: the largest component was 11 keys collapsing to 7 names and
  ~5 molecules at 71% edge density — a near-CLIQUE walked in circles, not a chain. Same-class membership is symmetric; a real
  chain needs an ordering (first-line → second-line) that the data did not carry. The graph was also 39 fragments, largest 11,
  which is itself proof of decomposability. RULE: before reporting depth, print edge DENSITY and dedupe nodes to distinct real
  entities; a long path in a dense symmetric component measures clique size, not dependency. Write the caveat into the
  pre-registration so a nominal "survives" cannot later be quoted as support.
- 2026-07-29 | Gate design / STRESS THE KILL UNDER STRICTER VARIANTS, AND PRE-COMMIT THAT A SURVIVOR DOES NOT REVERSE IT | A
  kill resting on one arbitrary operationalisation is weak evidence, so I re-ran M3 under five progressively stricter
  definitions of a usable alternative (+route, +dosage form, +exclude scarce, +exclude fragile suppliers): 0.0% conflicts in all
  five. That turns "my greedy rule happened to succeed" into a structural finding. RULE: always stress-test a kill, but write in
  the pre-registration that a surviving variant is reported as a CAVEAT and never used to overturn the verdict — choosing the
  definition after seeing the result is the exact post-hoc fitting the gates exist to prevent.
- 2026-07-29 | infra / **PREFER THE BULK EXPORT OVER THE PAGINATED API — one 27 MB file replaced 276 stalling requests** |
  Per-substance openFDA lookups stalled hard (50/276 in ~15 min, then no progress with nothing competing). `api.fda.gov/
  download.json` lists complete dated bulk exports; the whole NDC directory is ONE 27 MB zip (137,468 rows, same export date as
  the shortage snapshot). Offline rebuild took 7 SECONDS and was strictly better: class membership became EXACT, where the API
  route capped each class at limit=1000 and would have silently truncated precisely the largest classes. RULE: check for a bulk
  export before writing any per-item fetch loop, and prefer it even when the API "works" — it removes rate limits, removes
  pagination truncation, and pins both sides of a join to one snapshot date.
- 2026-07-29 | infra / `| Out-String` BUFFERS THE WHOLE STREAM AND DEFEATS `python -u` | A progress-printing diagnostic showed
  ZERO output for 190s because the PowerShell pipe held everything until process exit, so I could not tell a hung request from a
  slow one. RULE: redirect to a file (`*> run.log`) and read the file for anything long-running; never pipe a progress-reporting
  script through Out-String. Related: print progress every N items AND include a heartbeat, since a 25-item interval hid the
  fact that work was continuing.
- 2026-07-29 | infra / STALE PYTHON FROM AN ABANDONED CANDIDATE WAS STILL RUNNING 2.5 HOURS LATER AND STARVING THE NEW BUILD |
  Two python processes from the previous candidate's 05:25 PM run were still alive at 07:55 PM, competing for the same API
  quota; the new build only started progressing after I killed them. Identify by `Get-CimInstance Win32_Process` COMMAND LINE
  (not name or PID alone — the IDE's own python extension processes look identical by name and must NOT be killed). RULE: when
  concluding a candidate, sweep its background processes before starting the next one.
- 2026-07-29 | verifier / NORMALISERS ARE APPLIED TO BOTH SIDES, SO EVERY ONE MUST ACCEPT A NATIVE VALUE AS WELL AS A STRING |
  Three checks silently scored 0.0 with `'bool' object has no attribute 'strip'` because the submission side is always a CSV
  string but the recomputed reference side is a real `bool`/`int`/`None`. The fail-closed wrapper turned a type bug into a
  plausible-looking zero, so it did not announce itself. RULE: give every normaliser a `_s(v)` coercion front door, and always
  read the GOLD fixture's per-check output line by line — a gold fixture that scores "high" can still be hiding dead checks.
- 2026-07-29 | rubric / GRADE THE WHOLE SCHEMA YOU ASK FOR, OR STOP ASKING FOR IT | The rulebook required four columns
  (`product_unit`, `issuing_authority`, `unit_to_apply`, `obtain_before`) that no check scored, which is simultaneously a
  reward hack (fill them with anything) and wasted agent effort. RULE: before shipping, diff every column/section the
  instruction or rulebook mandates against the fields the checks actually read; each one must be graded or removed. Fold the
  extras into an existing check rather than inflating the check count.
- 2026-07-29 | rubric / VERBATIM-QUOTE GROUNDING MUST BE PER-DOCUMENT, NOT AGAINST THE CONCATENATED CORPUS | Testing quotes
  against `" ".join(all_texts)` let a real sentence lifted from ANY document pass as evidence for a different one. Fix:
  attribute each quote to the nearest preceding entity heading and test it against that document's text only. Prove it with a
  dedicated "laundered quotes" fixture (real sentences, wrong owner) — ours went from 28/28 grounded to 0/28.
- 2026-07-29 | rubric / A "NO ORPHANS" OR "IS CONSISTENT" SUB-SCORE PAYS AN EMPTY SUBMISSION UNLESS IT IS GATED ON HAVING ROWS |
  An empty submission scored 0.0227 by earning 1.0 for having no contradictory rows. RULE: any check phrased as an absence of
  errors must return None (excluded from the macro) when the file has no rows, so absence earns nothing.
- 2026-07-29 | packaging / `verifier_type` IS "executable" WHENEVER verify.py OWNS THE SCORING, EVEN WITH INLINE LLM CHECKS |
  Copying `"llm-judge"` from a previous task while 20 of 22 checks were deterministic is a QD-07 mismatch. `"llm-judge"` is
  reserved for a reward that is PURELY LLM-derived. Also: `rubric_manifest.json` entries need EXACTLY the five CR-08 fields
  (detailed_explanation_of_checks, weight, agent_output_path, check_function,
  how_it_prevents_task_authenticity_violation) with weight == 1 and gap-free per-category numbering — an older task's manifest
  shape is not a safe template.
- 2026-07-29 | process / WRITE A static_checks.py THAT MACHINE-VERIFIES S-01..S-07 AND THE MANIFEST↔VERIFIER MAPPING | Eyeballing
  the delivery constraints missed a stale check count, a manifest key mismatch and a wrong `verifier_type`. A ~150-line script
  that recomputes dag_depth from the YAML, diffs manifest ids against the `CHECKS` list, and greps for forbidden scoring shapes
  catches these in 2 seconds per run. Two calibration notes: strip comments before asserting a key is ABSENT (task.toml's own
  prose explaining that `[agent].timeout_sec` is omitted matched the regex), and a bare digit is not a leak — require the count
  to be attached to the population noun, and exclude counts of AGENTS ("10 directive readers").
- 2026-07-29 | integrity / RE-MEASURE EVERY NUMBER IN NOTES/instruction/task.toml AFTER THE LAST BUILD CHANGE | The corpus was
  rebuilt to a narrower window but `instruction.md` still claimed a July end-date and 1.65M characters (actual: April, 2.07M),
  a synthetic artifact still carried the old `last_publication`, and the AHT components summed to 84.5 against a declared 84.0.
  RULE: keep a `corpus_stats.py` / `ref_stats.py` that PRINTS every quoted figure, and re-run them as the last step before
  zipping; never hand-copy a measured number forward.
- 2026-07-29 | gap / BUILD "REALISTIC ARM PROFILE" FIXTURES, NOT JUST gold/empty/shallow/hollow | The mandated five fixtures
  tell you the rubric is monotone but not what the two arms will actually score. Adding two profiles parameterised by (coverage,
  accuracy-on-the-hard-mechanic) — SA at 35%/45%, MA at 88%/85% — produced a directly quotable projected gap (0.401) and
  exposed that 13 of 20 checks were winnable without touching the discriminating mechanic, which is what prompted rebalancing.
```

- 2026-07-30 | scoring / NEVER NAME AN INTERNAL RULE AFTER A FORBIDDEN ONE | A fairness guard that pools reference classes
  with fewer than N members was called `RARE_CLASS_FLOOR` / `_apply_floor()`. It clamps no score -- it is a minimum group
  SIZE -- but "floor" is the name of a prohibited scoring shape (caps/floors/ceilings, min(score,X)) and task.toml itself
  promises "no floors", so a reviewer auditing by keyword finds `_apply_floor` in the scoring path of 12 checks and has to
  reconstruct the innocence of it. RULE: rename to what it measures (`MIN_CLASS_SIZE` / `_pool_small_groups`), keep the
  words cap/floor/ceiling/gate in the package ONLY inside the sentences promising there are none, and add a static check
  asserting exactly that. Costs one rename; can cost a review to keep.
- 2026-07-30 | rubric / RESOLVE "WHICH CHECKS DOES THIS AGGREGATOR AFFECT" FROM THE CALL GRAPH, NOT FROM PROSE | Changing a
  shared helper (`weakest`, `class_accuracy`) silently changes every check that reaches it, including through a wrapper. A
  grep of the manifest's own wording named 13 checks; the AST call graph named 12 -- it missed several that reach the helper
  indirectly and wrongly included one that takes a plain min() of two sub-scores. Documenting that one would have been a NEW
  manifest inaccuracy introduced while fixing an old one (the QD-03.6 "mean" vs "min" REJECT). RULE: walk CHECKS -> function
  -> transitive calls, and assert code-set == documented-set in BOTH directions in static checks.
- 2026-07-30 | integrity / A SCORING CHANGE INVALIDATES EVERY SCORE CLAIM, SO MATCH THEM MECHANICALLY | A fairness fix moved
  the honest fixtures by 0.03 and left task.toml quoting a superseded single-agent score, multi-agent score and gap -- exactly
  the numbers a reviewer spot-checks. Extends the earlier "re-measure every number" lesson with the durable form: extract
  EVERY decimal from the reviewer-facing files and match each, AT THE PRECISION WRITTEN, against a value produced by the last
  fixture run; report anything that matches nothing. Also verify the extractor's own regex matches every spelling used -- a
  size-claim pattern requiring "N-character X" had been silently skipping the "N characters of X" form, so the largest claim
  in the file had never once been checked.

- 2026-07-30 | rubric / A DELIVERABLE THE RUBRIC ONLY MEASURES BY LENGTH IS A DELIVERABLE YOU ARE PAYING NOT TO EXIST | The
  sixth required artifact was scored `len(text) > 200` and nothing else in the verifier read it, so 201 characters of anything
  earned full marks -- while the rulebook prescribed a precise shape for it that was never checked. The reward at stake was
  0.3%, and it still cost a REJECT, because "grade correctness not presence" is audited per DELIVERABLE, not per point.
  RULE: for every artifact the instruction requires, name the check that reads its CONTENT; if the answer is "the length
  test", either grade what the rulebook asked for or stop requiring the file. Grade it proportionally (shape fraction, and
  whether the coverage it claims is backed by another artifact) so an honest short log still scores.
- 2026-07-30 | fixtures / A POSITIVE CONTROL CANNOT DETECT A CRITERION THAT IS TOO EASY | The LLM-judged checks fail closed to
  0.0 without an API key, so all twelve fixtures scored 0 on them and the judged share of the rubric was never exercised by an
  attack. The one control that existed asked "does the GOLD brief satisfy all ten criteria?" -- it did, so the criteria looked
  fine, and a reviewer then found that restating the instruction's own framing with a plausible round number satisfied several
  of them. RULE: every judged criterion needs a NEGATIVE control alongside the positive one -- mirror the criteria
  deterministically, feed them a deliberate boilerplate answer, and gate on it in static checks. Also a mundane trap worth
  naming: if all your fixtures share one placeholder for a file, no fixture is testing that file.
- 2026-07-30 | rubric / DISCLOSING A TRAP FOR FAIRNESS TURNS ITS QUALITATIVE HALF INTO FREE MARKS | Clarity review REQUIRES the
  instruction to disclose the traps, so the brief said in bold that a majority of the wave lacks its own deadline and named the
  clock redirection. Judged criteria then asked whether the submission IDENTIFIED those findings -- which the author had just
  been told -- with numeric bands (+/-8 on 65, +/-3 on 6) loose enough that a plausible estimate passed too. The disclosure
  cannot be withdrawn, so the criteria have to move: demand the derived FIGURE or the specific IDENTIFIERS, tell the judge
  which framing was pre-supplied and that repeating it proves nothing, and keep bands to a few percent as rounding tolerance
  rather than room to guess. Test it by writing the restatement attack yourself and requiring it to score near zero.
- 2026-07-31 | rubric / A BAR SWEPT ON ONE RUN IS A FICTION -- SWEEP IT ON THE WHOLE FIXTURE BATTERY OR YOU WILL PICK A BAR THAT
  KILLS THE HONEST ARM | Recasting a weighted-fractional verifier to the mandated boolean shape looked like a free 0.29: the
  measured SA fell 0.7017 -> 0.4091 at a 0.95 pass bar. Sweeping the SAME bar across all twelve fixtures showed the honest
  multi-agent fixture fell to 0.050 at that bar, i.e. the recast compressed everyone rather than discriminating, and at every bar
  >= 0.85 the SCRIPT OUTSCORED THE HONEST READER. RULE: never choose a pass bar from the arm you are trying to suppress. Require
  the battery to stay ORDERED (gold > MA > SA > attacks > empty) at the chosen bar, and treat any bar where the honest partial
  fixture collapses as disqualified no matter what it does to the SA number.
- 2026-07-31 | rubric / SCRIPTS ARE BIMODAL AND READERS ARE NOT, SO STRICT PASS BARS SUBSIDISE SCRIPTING | Over 17 extraction
  checks a real scripted agent scored mean 0.887 / median 0.953 with NINE checks at >=0.95 and a floor of 0.364 -- near-perfect
  where a regex works, poor where it does not. An honest reader working the same 107 documents scored mean 0.811 / median 0.840
  with ZERO checks at >=0.95: imperfect everywhere. Raising the bar therefore deletes the reader and keeps the script's perfect
  half -- measured reader-minus-script went +1 at bar 0.70, -7 at 0.85 and -11 at 0.90. RULE: set pass bars MODERATE (~0.80) and
  buy discrimination by adding checks the script cannot attempt AT ALL, never by tightening the ones it already wins. Tightening
  is also the QD-09 partial-credit hazard, so the strict-bar instinct fails twice.
- 2026-07-31 | design / THE REAL ANTI-SCRIPT TEST IS "IS THE HONEST DEFINITION EXECUTABLE?", NOT "IS THE FIELD HARD?" | Clarity
  review REQUIRES every graded field to be defined in the rulebook. For a field whose answer is a token pattern, the definition
  IS the parser: this rulebook printed the canonical trigger sentence for the compliance basis, the canonical redirection
  sentence, and five identifier shapes -- and the scripted agent duly scored 0.900 / 0.773 / 0.746 on exactly those three
  "judgement" checks, 80.7% of their points. The two checks it could not touch (0.364 and 0.034) were the ones whose definition
  is fully disclosable but NOT executable: which sentence's SCOPE applies, and which sentence GROUNDS a determination. RULE:
  before locking any field, write the regex its own rulebook paragraph implies. If you can write it, the field is extraction no
  matter what you call it -- either restate the definition operationally (what it means and why it matters, never the canonical
  wording) or drop the field.
- 2026-07-31 | diagnosis / AUDIT THE TRAJECTORY, NOT JUST THE SCORE -- COUNT read CALLS AGAINST CORPUS SIZE | The score said
  "0.70, too easy"; the trajectory said what actually happened. 218 tool calls: 139 bash, 49 read, 18 edit. It opened 14 of 107
  documents with the read tool, never named 73 of them at all, pivoted to regex at 3.7 minutes of a 76.7-minute run, aimed 76
  shell calls at lettered paragraph headings and ZERO at any narrative section, and emitted 51,291 bytes from a 2,070,943-char
  corpus (40:1) under names it invented (0 of 6 prescribed). RULE: for any corpus task, compute read-tool-calls / corpus-units
  and narrative-greps / structural-greps from the trajectory. If an agent produced N rows having opened far fewer than N
  documents, the rows came from code and the rubric is measuring the code. This diagnostic is cheap and it localises the defect
  in a way the reward number never can.
- 2026-07-31 | rubric / A WHOLE-POPULATION BOOLEAN CHECK IS A COVERAGE CLIFF -- SHARD IT, AND SHARD IT ON THE AXIS PARTIAL WORK
  ACTUALLY FOLLOWS | "Correct on >= 80% of the 107 units" as ONE boolean check pays a 60%-complete submission ZERO: the honest
  partial fixture went 0.5522 (weighted) -> 0.050 (boolean), a straight _g_partial_credit / QD-09 failure hiding inside a
  compliance fix. Scoping the same checks to nine SUBJECT-MATTER shards did not help either (still 0.000) because subject matter
  is scattered through the corpus, so a uniformly-partial answer sits under the bar in every shard. Scoping to DOCUMENT-ORDER
  blocks did: at 5 shards the sharded reward tracked true correctness to within 0.005 for both honest profiles (0.598->0.600,
  0.850->0.800). RULE: shard every population check into ~4-5 blocks along the ORDER work is done in (prefix for a serial agent,
  block-per-worker for a swarm), not along a semantic axis. Note the residual and choose it deliberately: shards rescue
  prefix-shaped incompleteness, not scattered sampling, which still scores 0.
- 2026-07-31 | rubric / AN OVERSIZED EASY-EXTRACTION BAND IS THE SCRIPTABILITY DEFECT AND THE FABRICATION DEFECT AT ONCE | The
  fabrication fixture -- reads the cheap fields, invents the compliance mechanic -- still passed 9 of 20 boolean checks (0.450),
  and all nine were easy-extraction checks. The same 17-of-22 band that let a parser reach 0.70 is what makes inventing the hard
  half cheap, because the easy half alone clears a plausible score. RULE: count how many checks a submission can pass while
  fabricating everything that requires reading; if that number is a competitive score, cut the easy band by COUNT rather than
  adding more anti-fabrication checks on top of it. Measured here: 17 -> 5 extraction checks moved the parser 0.591 -> 0.182.
- 2026-07-31 | rubric / MEASURE WHAT FRACTION OF THE CORPUS THE RUBRIC ACTUALLY READS; THAT RATIO IS THE PARSER'S ADVANTAGE | Every
  graded field was lifted from the header block plus the lettered regulatory paragraphs: 34.4% of the corpus by characters. The
  other 65.6% -- narrative, comment disposition, background, service information, where the operational meaning lives -- was worth
  zero, so a script that skipped two thirds of the text still reached 78.6% of the reward. RULE: compute graded-zone chars /
  total chars as a build-time gate. If the rubric reads only the machine-liftable zone, it is an extractor specification no
  matter how strict the individual checks are, and no amount of scale or tightening changes that.
- 2026-07-31 | design / PROBE EACH CANDIDATE REASONING AXIS FOR POPULATION BEFORE DESIGNING ON IT -- MOST PLAUSIBLE ONES ARE DEAD |
  Four obvious "add reasoning" axes were checked against the frozen corpus and two died on counts, not on taste: applicability/
  effectivity matching (median applicability paragraph 215 chars, mostly one-line model names; the 65 "carve-outs" after it were
  the boilerplate incorporation wrapper, with only 1 conditioned on modification state) and deadline arithmetic (34 of 107 carry
  any datable obligation at all). What survived was the axis with no fixed marker: narrative prose, median 10,329 chars/doc, whose
  compliance intervals sat behind 9 distinct lead-ins across 13 clauses. RULE: write throwaway read-only probes that print
  population per axis, and pick the axis by measured count and marker-absence. An axis with no stable marker cannot be regexed;
  an axis under ~60% population cannot carry a check.
- 2026-07-31 | QG / DECOMPOSITION.YAML IS A PROPOSAL, NOT A SCRIPT -- RECONSTRUCT THE REALIZED SPAWN TREE BEFORE SHIPPING THE LOGS |
  A blueprint declaring "the orchestrator dispatches ONLY the five general managers" realized as ONE child: the orchestrator
  spawned the planning lead, which spawned the reading leads and 32 readers, while the graph and integration tiers (12 of 47
  declared roles) never ran as sessions and two undeclared merge nodes appeared instead. The paper DAG passed STEP A-C; STEP D
  failed on shape divergence. RULE: after every multi run, walk raw_trajectory/*.json by id/parentID, print nodes-per-level, and
  diff the realized tree against the blueprint. If the orchestrator collapses a manager fan-out, either flatten the blueprint to
  what it reliably dispatches or re-run -- an aspirational org chart in decomposition.yaml is a QD-06.7 reject.
- 2026-07-31 | QG / TELLING THE AGENT HOW SOMETHING IS SCORED IS A LEAK EVEN WHEN IT PUSHES TOWARD HONEST WORK | An anti-templating
  warning ended "...does not count as real per-item work and is scored as such". The four words "and is scored as such" convert a
  work standard into a disclosed verifier mechanic, and QD-01.5 fails on the existence of scoring-mechanic detail regardless of
  whether any threshold or literal matches tests/. RULE: state expectations in the voice of the persona ("that is not real work"),
  never in the voice of the grader ("that is scored as..."). Grep instruction.md for "scored", "counts toward", "credit", "penalis"
  before packaging.
- 2026-07-31 | verifier / FAIL-CLOSED 0.0 NEEDS AN ERROR FLAG ON *EVERY* PATH, NOT JUST THE PER-CHECK ONE | The per-judge handler
  correctly set infra_failure and wrote degraded/degraded_checks/notes, but the two catastrophic handlers (context build failure,
  top-level crash) called the writer with no details, so reward.json degraded to a bare {"reward": 0.0} -- an infra failure
  indistinguishable from a blank submission (QD-02.5). RULE: make the details argument mandatory in the reward writer, or default
  it to {"degraded": True, "error": ...}, so no code path can emit a bare zero. Fail-closed governs the VALUE; QD-02.5 governs the
  METADATA -- satisfying one does not satisfy the other.
- 2026-07-31 | verifier / AN UNPREDICTABLE SAMPLE SEED IS ONLY HALF OF THE QD-04.10 FIX; THE OTHER HALF IS SCALING THE CEILING |
  Nine judges sampled with a per-run os.urandom seed plus tail bias and a full-coverage deterministic companion per axis -- a real
  defense that still fails the check, because a sampled judge can return 1.0 on 90 of 1050 records. The rubric's escape hatch reads
  "sample independently and unpredictably per run AND scale the maximum achievable reward down by the ungraded fraction"; both
  clauses are required. Also check the cap against the fraction: _SAMPLE_FRAC 0.20 with _SAMPLE_CAP 90 grades 8.6% at N=1050, so
  the "proportional" defense is untrue exactly where scale makes it matter.
- 2026-07-31 | verifier design / IF THE VERIFIER COMPUTES ITS OWN REFERENCE BY REGEX, THE TASK IS SCRIPTABLE BY CONSTRUCTION | An
  evidence review of one SA run found the graded reference for 37 of 56 points was produced by module-level patterns in verify.py
  over the same text the agent reads -- no curated key. The graded question then reduces to "does your regex agree with our regex",
  and the per-check score is a similarity measure between the two parsers, not a measure of comprehension: the agent's scores
  tracked pattern overlap exactly (near-identical template 0.955; matched only the consequent clause 0.773; unlike pattern 0.364).
  RULE: before writing any oracle check, ask what produces the reference. If the answer is a regex over the corpus, a parser can
  reach 1.0 on it by definition and no amount of weakest-class F1 or both-directions scoring changes that. Reserve regex-derived
  references for cheap fields and make the expensive points depend on a reference a regex cannot produce.
- 2026-07-31 | rulebook / PUBLISHING A FIELD'S DECISION PROCEDURE CONVERTS A JUDGEMENT INTO AN ALTERNATION | Same task, same agent,
  same corpus, one variable: seven register fields whose rule the rulebook printed verbatim (heading lists, verb tables, an
  antecedent-consequent template, conversion constants with worked examples) scored mean 0.958; the one field described only by
  worked example, with its trigger set and window withheld, scored 0.364 -- a 0.594 within-task difference. Fairness (QD-01) requires
  publishing what a field MEANS; it does not require publishing HOW TO DECIDE IT. RULE: in the rules doc, define the field and give
  a discriminating example pair, but never enumerate the closed set of surface forms that triggers it -- an enumerated set IS the
  parser. Grep the rulebook for backticked literal lists and pipe-separated headings before shipping.
- 2026-07-31 | axis design / VALIDATE A REASONING AXIS ON THREE THINGS, NOT ONE: PRESENCE, RESISTANCE, AND JOIN STRUCTURE | Five candidate
  axes were probed against a 107-doc corpus before any labelling; three died on structural grounds in under an hour. (a) A composed-date
  axis looked strong because the instruction warns at length about the clock-redirection trap -- but 59 of 66 adopting directives DO
  redirect onto the AD's own effective date, so the trap and the default coincide and "write the effective date everywhere" scores 0.935
  with a discriminating population of 7. (b) A verbatim-span traceability axis died because the median required-actions paragraph is ONE
  sentence of 252 chars, so "cite a span from the paragraph" means "cite the paragraph" and a positional heuristic passes 88/88. (c) A
  blocked-work-backlog axis died because the 66 adopted documents map 1:1 onto the 66 adopting directives -- zero join structure. RULE:
  before designing any check on an axis, measure presence (how many units carry the signal), RESISTANCE (what a constant answer and a
  keyword parser score -- not how many surface forms exist), and for any relational axis the actual fan-out of the join. Surface-form
  variety is NOT resistance: 34 distinct forms mapping onto 8 keyword-reachable classes is a scriptable axis.
- 2026-07-31 | axis design / OPERATIONALLY DANGEROUS IS NOT THE SAME AS STATISTICALLY DISCRIMINATING | The persona's headline risk (planning
  off the wrong clock, "the fourteen-month error") turned out to be the majority case, so grading it rewarded the default answer. Conversely
  the axis that DID discriminate -- which shop capability the work actually needs -- is mundane enough that the instruction never dwells on
  it, yet a rating-lookup parser's ceiling on it measured 0.427 with 21 same-rating directives carrying 14 distinct work-sets. RULE: pick the
  graded axis from the measured class balance, not from the narrative importance of the risk; and when the work description is delegated to a
  document you do not ship, look in the preamble (Discussion / Costs / Summary) before declaring the signal absent -- it was present in 61 of
  66 delegating documents there and in only 20 of 107 in the regulatory paragraph alone.
- 2026-07-31 | measurement hygiene / A LIVE HARNESS ZERO AND AN OFFLINE REGRADE ARE DIFFERENT MEASUREMENTS; NEVER QUOTE ONE FOR THE
  OTHER | A run recorded 0.0/56 live purely because the verifier of that day resolved deliverables by filename and the agent invented
  all six names; the same submission regraded 0.7017 once resolution fell back to content. Both numbers are real and they describe
  different things -- the first measures packaging, the second measures work. RULE: when citing a run's score, state which verifier
  sha produced it and whether judges ran; and when a judged check can early-return before the judge is called (empty artifact), do not
  attribute its zero to "judge failed closed" -- read the per-check note to see which of the two actually happened.
- 2026-07-31 | axis validation / A CONSTANT-ANSWER FLOOR IS THE WEAKEST ATTACK; THE REAL ONE IS CANONICAL-PHRASE PRECEDENCE | A candidate
  axis cleared a majority-class floor of 0.477 and was carried forward, then died on a hand-labelled pilot: a classifier that does nothing
  but match fixed regulator formulas in precedence order was correct on 16/16 of the directives it chose to decide, abstaining rather than
  erring on the rest, for an expected ~0.78. RULE: before trusting an axis, grep the corpus for the FORMULAS that announce the answer and
  count their coverage; if the source is a regulator, a standards body, or any drafting tradition with template sentences, assume the label
  is announced verbatim somewhere and measure a phrase-precedence classifier -- not just a constant guess -- as the parser baseline.
- 2026-07-31 | axis validation / DE-BOILERPLATE THE KEYWORD BASELINE OR YOU WILL CREDIT YOUR OWN BUGS AS THE AGENT'S REASONING GAP | The
  keyword probe that "proved" an axis resistant was firing `\binspect` on "principal inspector" (106/107 documents), `\breplac` on
  "replacing that text with" (28/107) and `\btorque\b` on the part name "torque link". Half the measured disagreements were my probe's
  defects, not the corpus's difficulty; separating them cut the resistance claim in half. RULE: classify every baseline-vs-human
  disagreement as ENGINEERING (boilerplate, case-sensitive section location, rule ordering -- a competent author fixes it) or SEMANTIC
  (domain coinage, wrong CLAUSE chosen, capability implied not named), then re-score granting every engineering fix. Only the semantic
  residue is evidence, and report the residue as the headline.
- 2026-07-31 | axis validation / VALIDATE AN AXIS'S REACH BEFORE ITS RESISTANCE -- A PERFECTLY RESISTANT AXIS THAT GOVERNS 20% OF THE
  BOARD HAS A HARD SCORE FLOOR | Four probes and a hand-label pilot were spent proving an axis un-scriptable, and it passed; then the
  arithmetic showed it re-keys 11 of 56 points, so even a SA scoring ZERO on everything it governs lands at 0.505 against a <0.30 target.
  The ceiling on its contribution was fixed at -0.197 before any of the resistance work began, and a boolean recast to 22x1 does not move
  it (floor 0.364-0.409). RULE: the FIRST question about a candidate axis is "how many points does it govern, and what does the SA bank on
  them today" -- compute (SA points on governed checks)/(board) as the maximum possible drop. If that is smaller than the distance to
  target, the axis is a component and no amount of resistance validation makes it primary. Do this in ten minutes before spending days.
- 2026-07-31 | redesign / RUN THE FLOOR TEST ON A PROPOSED BOARD: EVERY UNMEASURED CHECK IS A CHECK THE SA MIGHT PASS FOR FREE | A 22-check
  board with 5 extraction + 8 measured-hard + 9 plausible-but-unpiloted checks projects a lovely SA of 0.236 -- and a DEFENSIVE floor of
  0.645, because (extraction + unmeasured)/total is what you actually know. Re-architecting so the measured axes alone reach target (4
  extraction + 15 sharded checks on two axes with measured per-unit rates) gave 0.274 with nothing taken on faith. RULE: score every
  proposed board twice -- once assuming unvalidated checks bite, once assuming they are free passes. Ship the allocation whose DEFENSIVE
  floor clears target; let unvalidated axes earn checks by passing a pilot, never by being plausible. Corollary: adding even 2 unpiloted
  checks to a target-clearing core can breach the target, so "we can always add more reasoning checks later" is false.
- 2026-07-31 | rubric / A SINGLE PASS BAR IS A CLIFF WHENEVER YOUR SA ESTIMATE HAS A CONFIDENCE BAND -- USE A BAR LADDER | One 0.70 shard bar
  projected SA 0.236 at the measured parser rate and 0.638 at the same pilot's worst case, because the 0.583-0.750 band STRADDLED the bar.
  Spreading bars across shards of one axis (0.60/0.65/0.70/0.75/0.80/0.85) turned the cliff into a slope: 0.246 measured, 0.517 worst case,
  and genuine graduated partial credit. Every check stays worth exactly 1 point -- varying DIFFICULTY across checks is not a weight and is
  not forbidden. RULE: whenever the per-unit SA rate is an estimate with a band, never put a single bar inside that band; ladder the bars
  across shards so the board degrades gracefully. And state plainly that a ladder does NOT rescue the worst case -- if the parser's true
  rate exceeds your top bar it is simply competent, and only re-measuring the rate resolves that.
- 2026-07-31 | rubric / GRADE EVIDENCE AS AN OFFSET RANGE, NOT AS A QUOTATION -- AN AGENT CAN QUOTE ANYTHING | A verbatim-quotation check is
  satisfied by copying any span, so it measures compliance with a format rather than grounding. Requiring a character-offset range that must
  OVERLAP the reference's own evidence span makes the check measure LOCALISATION: the agent has to point at the passage that supports a
  determination it actually made. Costs nothing extra to label if the labeller records the span while making the judgement. RULE: for any
  traceability check, grade WHERE the agent points, not WHAT it pasted.
- 2026-07-31 | redesign / CHOOSE THE SHARD SIZE AND BAR BY COMPUTING BOTH COLUMNS, NOT BY PICKING A ROUND NUMBER | At n=24 a 0.80 bar looks
  strong (parser 0.009) until you compute the honest-reader column: a 0.75 reader also collapses to 0.247. Dropping to a 0.70 bar kept the
  parser near zero (0.149) while restoring the 0.75 reader to 0.766. RULE: tabulate binomial pass probability across shard sizes x bars for
  BOTH the measured parser rate and a range of reader rates; a configuration is only usable where the parser column is near 0 AND the
  mid-reader column is high. This operationalises the bar-paradox lesson instead of just warning about it.
- 2026-07-31 | task design / THE UNIT OF WORK IS USUALLY WRONG, AND FIXING IT BUYS SCALE, REALISM AND DISAMBIGUATION AT ONCE | A register of
  107 documents under-counted the real work by 1.7x: 50 of them cost two or more distinct actions, 187 in total. Re-basing the task on the
  ACTION rather than the DOCUMENT delivered the 100-200+ unit scale the rubric deck asks for, matched what the practitioner actually plans,
  and reduced (not eliminated) the "which label governs?" ambiguity that comes from forcing one label onto a multi-job document. RULE: before
  scaling a corpus, check whether each document already contains several gradable units -- count the costed/enumerated sub-items. Re-basing
  on the true unit is cheaper than sourcing more documents and it improves realism instead of just inflating volume.
- 2026-07-31 | diagnosis / SCRIPTABILITY IS USUALLY BROAD, NOT CONCENTRATED -- LIST THE UNTOUCHED CHECKS BEFORE COMMITTING TO A FIX | After
  mapping one regex chain that drove 16 points, the residue nobody was fixing held 17 points averaging 0.95 -- every one a canonical heading
  or a template the rulebook printed. A dependency map shows what a fix REACHES; it does not show what it MISSES. RULE: alongside every
  dependency map, print the complement -- the checks the intervention does not touch, with the SA's score on each. If the complement is
  large and high-scoring, a single-axis redesign cannot reach target and the honest verdict is "necessary but not sufficient".
- 2026-07-31 | axis validation / THE STRONGEST EVIDENCE FOR A REASONING AXIS IS THE PARSER PICKING THE WRONG CLAUSE, NOT THE WRONG WORD |
  In four of eight irreducible failures (five under one of the two picking rules tested) the parser named the ON-CONDITION contingency
  instead of the mandatory required action, because both
  sit in one sentence ("inspect... and, depending on the results, REPLACE") and the conditional verb is lexically the stronger. That error
  survives any argument about label vocabulary, which single-labeller judgement calls do not. RULE: when a pilot rests on one non-expert
  labeller at n~24, report the sensitivity band (here 0.583 rising to ~0.75 if four judgement calls flip, which would fail the bar) and
  lean the conclusion on the clause-selection failures that are robust to relabelling.
- 2026-07-31 | reference design / DERIVE THE CLOSED ANSWER VOCABULARY FROM THE CORPUS'S OWN WORDS, NOT FROM DOMAIN IMAGINATION | The costs
  table in each FAA directive names every costed action in one line immediately before its work-hours figure, so the wave's ENTIRE work
  vocabulary -- 205 phrases -- was readable in one sitting and the catalogue was written after reading all of it. A vocabulary invented
  first and checked later leaves holes exactly where the corpus is unusual, which is where labelling ambiguity hurts most. RULE: find the
  corpus's own compact enumeration of the graded quantity (a costs table, an index, a summary clause) and read ALL of it before writing
  the closed list.
- 2026-07-31 | reference design / A FINER ANSWER VOCABULARY SUPPRESSES A PARSER FOR FREE -- GRANULARITY IS A RESISTANCE LEVER | Refining the
  capability catalogue from 15 coarse entries to 23 operational ones dropped the measured keyword-parser accuracy from 0.583 to 0.458 with
  no change to the instruction, the corpus or the verifier, because the parser had been earning credit for coarse labels that no longer
  exist (a swashplate PLAY check is a dimensional measurement, not an inspection; an ISSPU is an avionics LRU, not a "replace"). The finer
  vocabulary also removed several single-labeller judgement calls by giving them unambiguous homes, so it cut resistance AND ambiguity at
  once. RULE: when an axis is close to the bar, try splitting the answer space along real operational distinctions before adding checks or
  scaling the corpus -- it is the cheapest suppression available.
- 2026-07-31 | validation hygiene / A COVERAGE INSTRUMENT IS NOT A LABELLING PROCEDURE, AND A COVERAGE FAILURE MUST BE MEASURED BEFORE IT IS
  BELIEVED | The first coverage run said 82.4% and looked like a catalogue gap; every miss was actually my own extractor's table furniture
  ("Cost per product Cost on U.S. operators") or a SUMMARY clause grabbed from the wrong paragraph. Filtering phrases that name no work at
  all gave 97.1% and no real gap. Separately, the generous regex used to answer "does a home exist for this work" must NEVER be reused to
  generate reference labels -- that is precisely how a parser becomes the oracle. RULE: label the instrument, filter the noise before
  reading the rate, and keep the coverage map and the labelling procedure in different functions with different names.
- 2026-07-31 | reference design / VERIFY EVERY CATALOGUE ENTRY AGAINST THE FULL CORPUS -- AN UNEXERCISED ENTRY IS DEAD VOCABULARY | Three of
  23 entries were never hit by the extracted phrases, so all 107 documents were searched directly; all three turned out real but rare
  (penetrant 1/107, radiographic 3/107, tap-bond 1/107) and were kept. Had any been absent it would have been pure labelling ambiguity with
  no upside. RULE: probe every closed-list entry against the whole corpus, not against your sample, and delete the ones nothing exercises.
- 2026-07-31 | verifier / RESOLVE A DELIVERABLE BY CONTENT AT EVERY LEVEL, NOT JUST THE FILENAME | A live run once recorded 0.0 for work
  worth 0.70 because the agent invented six FILENAMES and the loader read by name only. That was fixed, but the fixture battery then caught
  the same defect one level down: a submission with 0.85 accuracy everywhere and every COLUMN renamed still scored 0.000, because name-
  aliasing only covered abbreviations. RULE: resolve a file by prescribed name then by header, and a column by prescribed name, then
  abbreviation, then the DOMAIN OF ITS VALUES (an id pattern, a closed vocabulary, a locator format), then position -- and grade the
  prescribed names as exactly ONE point so the contract still pays and a packaging slip can never decide substance. Content-based
  resolution can only ever rescue a right answer, since the values must still match the reference.
- 2026-07-31 | verifier / A FRESH GRADING SEED MEANS ONE FIXTURE RUN IS AN ANECDOTE, NOT A MEASUREMENT | Drawing the shard seed at grading
  time (right, so boundaries cannot be tuned to) makes a fixed submission score differently run to run: the same fixtures moved 0.85->0.80,
  0.35->0.25 between two batteries, and I nearly quoted single draws in task.toml and the manifest. RULE: whenever the grader has any
  randomness, report fixture scores as the MEAN over >=7 gradings with the sd, and confirm the residual spread (here sd 0.00-0.046, ~1
  check) is an order of magnitude below the differences the board must resolve.
- 2026-07-31 | projection hygiene / MODEL THE SCRIPTED AGENT WITH THE BEST STRATEGY IT ACTUALLY HAS, NOT A FLATTERING LOW RATE | The
  evidence-locator axis was projected at a 0.10 parser rate, which was invented. A parser that reads the cost table KNOWS the offsets of the
  row it parsed, so its real strategy is to cite that row -- measured, that lands on the establishing passage for 29% of actions (still
  short of both bars, so the projection survived, but only because it was checked). RULE: for every axis, ask what the scripted route can
  derive from what it already extracted, implement THAT as the fixture, and never let a gap claim rest on an assumed-low rate.
- 2026-07-31 | tooling / A NULL FIXTURE THAT SILENTLY BUILDS A PERFECT SUBMISSION WILL REPORT 1.000 AND LOOK LIKE A VERIFIER BUG | A
  variance harness passed `**(kw or {})` for the "write nothing at all" case, which is exactly the signature of the perfect submission, so
  the empty case scored 1.000. RULE: the null/no-op fixture must be asserted to score 0.0 in the harness itself, and any fixture-runner
  refactor must re-check the two anchors (empty = 0.0, reference = 1.0) before any other number in the battery is believed.

- 2026-07-31 | packaging / A PRE-FLIGHT THAT CHECKS THE GATES YOU REMEMBER WILL PASS A TASK THAT FAILS THE ONES YOU DO NOT | The
  local package checker enforced dag_depth >= 2 and never looked at dag_width, so a decomposition with a 13-wide assessor tier
  sailed through every local run and came back from draft review failing the >= 20 swarm-scale gate. The checker was the reason
  the defect survived: a green board reads as "compliant" and stops you re-reading the guideline. RULE: transcribe EVERY numeric
  threshold in the guidelines into the pre-flight script in one sitting, with the guideline's own wording as the check label, and
  when review finds a gate you were not testing, add the gate in the same commit as the fix so it can never regress silently.
- 2026-07-31 | integrity / SYNTHETIC ENVIRONMENT DATA IS A REJECT EVEN WHEN IT IS PLAUSIBLE, AND THE FIX IS USUALLY CHEAPER THAN
  IT LOOKS | A network-capability record was invented -- fictional operator, invented station ids, an invented rating vocabulary
  ("AIRFRAME-CLASS-3") -- because the real thing looked like days of research. It was flagged, and rebuilding it took about two
  hours: the regulator publishes the rating scheme (14 CFR 145.59 and 145.61 plus the inspector guidance explaining what each
  rating authorises), and certificate holders publish their own Operations Specifications A003 as PDFs. RULE: build the
  environment out of real named entities with a fetchable source per entity, and map the task's private vocabulary ONTO the real
  scheme instead of inventing a parallel one -- it costs a morning, it removes an entire class of review finding, and the real
  scheme is invariably more interesting than the invented one (a real network has holes in it that an invented one does not).
- 2026-07-31 | verifier / A SEED DRAWN AT GRADING TIME MAKES THE GRADE AN OPINION; DERIVE IT FROM THE SUBMISSION INSTEAD | Shards
  were partitioned with os.urandom so an agent could not tune to a boundary, which worked, but it also meant one submission
  scored 0.85 on Tuesday and 0.80 on Wednesday and the manifest's claim of determinism was false. Hashing the submitted files
  and seeding from that keeps the partition unguessable in advance -- the agent cannot know its own bytes' hash while it is
  still writing them -- and makes the grade a function of the submission alone. Measured spread went from sd 0.046 to 0.000.
  RULE: no verifier may call urandom, time() or uuid at grading time. If you need pseudo-randomness, seed it from a hash of the
  thing being graded, and prove determinism by re-grading every fixture in a fresh process rather than asserting it in prose.
- 2026-07-31 | rubric / EVERY FIELD THE INSTRUCTION MANDATES AND THE RUBRIC NEVER READS IS A PLACEHOLDER WAITING TO HAPPEN | Two
  columns were required of the agent and graded by nobody, so the cheapest correct-looking submission fills them with one
  repeated string. The temptation is to add a check per orphan field, which quietly drags the board back toward the extraction
  balance the redesign existed to fix. Folding them into checks that already existed cost zero points of judgement reward: the
  source-document number became part of "is this action correctly enumerated", and description distinctness became part of "did
  you count this directive's actions". RULE: diff the deliverable schema against the set of fields the verifier actually reads
  before shipping; for each orphan, fold it into an adjacent check as an AND rather than adding a check of its own.
- 2026-07-31 | rubric / GRADE A DERIVED DELIVERABLE AGAINST THE SUBMISSION'S OWN UPSTREAM FILE, NOT ONLY AGAINST THE REFERENCE |
  The placement file was checked against the reference capability, so an agent could file a weak capability sheet and a plan
  derived from somewhere else and be paid in full for the plan -- while the instruction promised the three files would be
  followed action by action. Requiring the plan's rating to follow from the capability the submission ITSELF recorded closed it:
  the exploit fixture fell from 0.85 to 0.45. RULE: wherever artifact B is documented as the consequence of artifact A, grade B
  against BOTH the reference and the submission's own A, and say so in the rulebook so the requirement is documented, not hidden.
- 2026-07-31 | measurement / ONCE THE GRADER IS SEEDED FROM THE SUBMISSION, ANY UNSEEDED RANDOMNESS IN THE FIXTURE BUILDER
  BECOMES SCORE MOVEMENT | A helper that picked a plausible wrong answer used the global random module instead of the seeded
  generator its caller was using. Harmless while the grader drew its own seed; the moment the partition came from the file
  bytes, the same fixture built different files every process and scored 0.45 in one run and 0.50 in the next -- and the first
  instinct was to suspect the verifier. RULE: a fixture builder must be a pure function of its seed. Before quoting any fixture
  number in a manifest or in task.toml, build and grade the whole battery twice in separate processes and require identity.
- 2026-07-31 | metadata / COST THE READ THE GRADED JUDGEMENT ACTUALLY REQUIRES, NOT THE TIME TO FIND THE FIELD | An AHT of 27.5h
  was derived by costing 107 regulatory documents at 2 minutes each, which is the time to locate a cost table -- but every
  graded determination in the task is read out of the regulatory body, not the table. Review flagged it as implausible for the
  token count and it was: at a defensible 20 minutes per 3,200-word document the same task is 67.8h. RULE: derive AHT from the
  unit of work the RUBRIC grades, publish the per-unit rate for every line so a reviewer can argue with a rate instead of a
  total, and sanity-check the total against the corpus size before submitting rather than after.

- 2026-07-31 | harness / A PROVIDER MIGRATION NOTICE IS NOT AUTOMATICALLY ACTIONABLE -- CHECK WHETHER YOUR GRADER EVEN HAS A
  JUDGE BEFORE PATCHING IT | The team shipped a Moonshot -> W&B Inference migration with a drop-in snippet, and the reflex is to
  paste it into verify.py. On the task in hand that would have ADDED a network call, an API key and a model dependency to a
  grader that had deliberately been made deterministic, breaking verifier_type = "executable", contradicting the manifest and
  tripping the package's own audit gate. RULE: before applying any provider patch, grep the shipped grader for an endpoint, a
  key env var and an HTTP client. No judge means no change. A deterministic verifier is the only kind that is immune to provider
  churn, which is an argument for building one whenever every graded cell has a right answer.
- 2026-07-31 | harness / KEEP A JUDGE-PROVIDER INVENTORY, BECAUSE THE PACKAGES THAT MISS A MIGRATION ARE THE ONES NOBODY IS
  LOOKING AT | Prompted by the second migration in two days, a scan of every tests/verify.py and tests/judge.py in the workspace
  found 26 live graders calling a judge and EIGHT of them in our own task tree still pointing at Fireworks -- two providers
  behind, having silently missed the previous migration as well. None of them announced this; a grader on a dead provider
  fail-opens and returns a reward computed over fewer checks than the manifest declares. RULE: keep a scanner that reports
  endpoint + key env var + model slugs per grader and run it on every migration notice, and pin all three in named constants at
  the top of each verifier so one edit moves a package and a static check can assert it.
- 2026-07-31 | integrity / A PLATFORM'S DEFAULT JUDGE MODEL IS NOT AUTOMATICALLY A LEGAL ONE FOR YOUR TASK | The migration
  snippet defaulted JUDGE_MODEL to the same model family as the agent under test, which the different-family rule forbids --
  adopting the announcement verbatim would have shipped a self-judging grader. The provider catalogue had several compliant
  alternatives and the announcement itself named one. RULE: read the platform default as a starting point, then check it against
  the agent under test, the deprecation list and the context budget (input AND output share the window) before pinning it; if it
  fails any of the three, pick from the catalogue and record why in the verifier.

- 2026-07-31 | scoring / TWO LIVE SCORING RULES CAN CONTRADICT EACH OTHER -- SURFACE THE CONFLICT, DO NOT PICK SILENTLY | The
  standing Phase-2 rule is a flat board, "each check worth exactly ONE point", with "* weight" listed as an auto-reject.
  Management then issued point-value-by-check-type after a five-task zero-gap RCA: 1 structure / 2 reward-hacking / 3
  partial-oracle, score = sum(passed x weight) / sum(total x weight). Both were in force, neither retracted, and a build that
  quietly follows either one can be rejected by the other. RULE: when two governing documents disagree on reward shape, say so
  in writing, put the choice to the owner with the measured consequences attached, and record the conflict in the rule file so
  the next build is not surprised by it.
- 2026-07-31 | scoring / MEASURE WHAT A REWEIGHT ACTUALLY BUYS BEFORE PAYING FOR IT -- ON A WELL-COMPOSED BOARD IT IS ~0.03 |
  Recasting 20 flat checks as 53 weighted points moved every fixture in the battery by 0.008 to 0.073 and changed no ordering:
  the do-nothing submission went 0.050 -> 0.019 and the structural share 5% -> 1.9%. The reweight was cheap only because the
  board was already composed correctly (ONE structural check, not four). RULE: grade the existing pass/fail vectors both ways
  from the same fixtures before touching the grader. If the delta is inside run-to-run variance, the reweight is cosmetic and
  the real lever is composition -- delete file-existence checks rather than reprice them.
- 2026-07-31 | scoring / THE DIAGNOSTIC FOR A SCORING ARCHITECTURE IS THE DO-NOTHING FIXTURE, NOT THE CHECK COUNT | Five tasks
  produced no gap because roughly half the reward was reachable by a submission that was complete, schema-valid and lexically
  derived from the source, so a competent-looking agent banked ~0.5 and there was no room above it for a 0.20 gap. The number
  that predicts this is one fixture: files present, schema valid, nothing read. RULE: build that fixture FIRST and require it
  to score below ~0.10. It costs one fixture and it tells you whether the architecture can express a gap at all, before any
  live run is spent finding out that it cannot.
- 2026-07-31 | scoring / WEIGHTS BELONG TO CATEGORIES, NOT TO CHECKS -- OTHERWISE "WEIGHTED" BECOMES "TUNED" | The only defence
  against a weighted board drifting into per-check score-shaping is that a check is worth exactly what its category is worth.
  RULE: declare the three values as named constants in the grading code, attach a category (never a number) to each check,
  GENERATE the manifest weights from that table, and change the static gate from "no weights exist" to "each check equals its
  category value, nothing exceeds 3, and manifest weights match the ones the grader applies". A gate that only forbids weights
  goes green on a board that has silently acquired them somewhere else.
- 2026-07-31 | verifier / WHEN THE SHARD SEED IS A HASH OF THE SUBMISSION, TWO SUBMISSIONS OF EQUAL QUALITY WILL NOT SCORE
  EQUAL | Hash-derived partitions make each submission's grade perfectly reproducible, but they do NOT make two different
  submissions comparable check-for-check: the same underlying work scored 0.887 with renamed files and 0.811 with renamed
  columns against 0.830 done to the letter, a spread of 4 points where the naming check is worth 1, purely because each file
  set hashes to a different partition and shards sitting near a bar fall either way. RULE: never explain a cross-fixture spread
  as the cost of a specific check; state the partition effect explicitly in the metadata, or a reviewer will read it as a
  premium for the wrong behaviour.
- 2026-07-31 | QG / A LOCAL GATE THAT MIRRORS THE REVIEWER SILENTLY STOPS MIRRORING IT -- RE-DIFF THE DIMENSION LIST AGAINST THE
  LAST HOSTED REPORT | The hosted reviewer gained QD-10 (the exploiter/grader reward-hacking pair) on 2026-07-23 and has failed
  it in every review since, while the local gate kept dispatching nine dimensions in four groups for five weeks -- so the most
  reliably-failing dimension was the one dimension never pre-checked. Its stale "files to read" list (judge.py, ground_truth/)
  also steered sub-agents away from rubric_manifest.json, which is now graded for truthfulness. RULE: after every hosted report,
  diff its emitted dimension and check IDs against what the local gate dispatches, and treat any ID the gate does not produce as
  a gate defect, not a reviewer quirk. Two shapes to carry over deliberately, because they are invisible in the rubric's own
  output blocks: the reviewer appends unnumbered `additional_*` findings past the end of every QD's list (about one reject
  reason in five comes from one), and QD-09's FLAG is reported as WARN and drives MANUAL_REVIEW rather than APPROVE.

- 2026-07-31 | rubric / NEVER SAMPLE A POPULATION YOU CAN AFFORD TO GRADE WHOLE | One check graded 45 of 107 directives while
  every other check covered its full population, and the reviewer rejected the package for it: a sampled check leaves a stretch
  of the corpus where a padded row is never looked at. At n=107 the sample bought nothing -- the bar is a RATE, so 0.80 of 107
  asks exactly what 0.80 of 45 asked -- and it cost coverage plus sampling variance. RULE: sample only when the population is
  genuinely too large to grade, state the reason in the manifest when you do, and audit for the odd check out; a single sampler
  among full-coverage checks is a rejection waiting to happen.
- 2026-07-31 | rubric / A DERIVED AXIS CHECKED THROUGH A LOOKUP CAN SCORE ABOVE THE AXIS IT DERIVES FROM | Placement was graded
  by requiring the submission's own competency to map to the same RATING as the reference competency. Because 178 of 214 actions
  carried a competency sharing a rating with another -- one rating absorbing seven competencies across half the wave -- the
  13-way lookup stood in for a 23-way determination and measured 0.73 where the determination itself measured 0.67. A wrong
  answer in the right bucket was being paid as a right one. RULE: when axis B is derived from axis A through a many-to-one map,
  count the fibre sizes before trusting B as evidence about A, and bind B to A's VALUE rather than to its image under the map.
- 2026-07-31 | rubric / TIGHTENING A CHECK THAT ONLY THE SCRIPTED ROUTE WAS PASSING FOR FREE IS THE RARE CHANGE THAT DOES MOVE
  THE GAP | The deck's warning is that a stricter rubric is paid for equally by both arms. The exception is a check the weaker
  route was clearing by a mechanism unrelated to the work: binding placement to the recorded competency cost the worst-case
  parser a point it had been collecting from the rating bucket and cost an accurate reader nothing, moving the worst-case gap
  from 0.189 to 0.245 and over the floor. RULE: before dismissing a hardening as gap-neutral, check WHICH fixtures were passing
  the check and why -- if the scripted route passes it for a reason unconnected to reading, removing that reason is not chasing.
- 2026-07-31 | review / MOST OF A REJECTION REPORT CAN BE ONE MISSING ARTIFACT -- TRIAGE BY ROOT CAUSE BEFORE READING IT AS A
  LIST | A REJECT with 15 non-passing entries looked like a wall of defects; 13 of them traced to an empty execution_logs/, and
  several rubrics treat a missing trajectory as a VIOLATION rather than an absence, so one unshipped artifact produces failures,
  warnings and not-applicables across four dimensions at once. RULE: group findings by root cause before estimating effort, and
  never regenerate a package for review with execution_logs/ empty -- the report you get back will be mostly noise about it.

- 2026-07-31 | metadata / DECLARE A SECONDARY CLASSIFICATION ONLY IF A DELIVERABLE CARRIES IT | "long_writing" was declared on a
  task whose three deliverables are tables of short fields, the longest cell being a work-order line of six words. The task IS
  long -- 2.07M characters of reading -- but length of INPUT is not what that label describes, and a reviewer who opens the
  deliverables sees the mismatch immediately. RULE: read each label against the OUTPUT the agent must produce, not against the
  effort the task takes; if no artifact carries the label, drop it and say in the file that you dropped it and why.
- 2026-07-31 | rubric / A REQUIRED FREE-TEXT FIELD CHECKED ONLY FOR PRESENCE AND UNIQUENESS IS STILL UNGRADED | Folding a
  description column into an existing check as "non-null and distinct within its parent" felt like closing the hole, and it did
  close the repeated-placeholder route -- but a DIFFERENT plausible string per row satisfies both tests and says nothing, which
  a reviewer found and priced at a full check. RULE: presence and difference are properties of the STRING, not of the content;
  to grade content you must compare against something outside the submission, even loosely.
- 2026-07-31 | rubric / GRADE FREE TEXT WITH A GROUNDING FLOOR, NOT A SIMILARITY SCORE -- AND MEASURE THE HONEST CASE FIRST |
  Two review dimensions pulled opposite ways on the same column: one passed it BECAUSE it was not compared to reference prose,
  the other failed it for not comparing at all. The resolution is one shared content word with the reference for that row --
  enough that filler cannot pass, loose enough that the writer's own words are free. RULE: set the floor from the DATA (median
  description six words, some one word, so a ratio or a two-word floor would charge for phrasing), and prove fairness with a
  fixture that rewords every field: if it does not tie the fixture using the reference wording exactly, the floor is too high.
- 2026-07-31 | rubric / CHECK A CLEVERER DISCRIMINATOR AGAINST THE CORPUS BEFORE BUILDING IT | Matching each description to its
  best-matching sibling within the parent record is a stronger anti-filler test on paper. In this corpus sibling actions differ
  by a single token -- "Replace HPT stage 1 disk" against "Replace HPT stage 2 disk" -- so it would have been a coin flip on
  honest work. RULE: sample the actual reference values for the field before designing a check that depends on how much they
  differ; five minutes of looking beats a fairness bug found in review.
- 2026-07-31 | leaks / YOUR OWN "BAD EXAMPLE" IN A RULEBOOK CAN BE A CORPUS LOCATOR | Adding "do not write rows like `action 1`"
  to a shipped rulebook leaked: that exact string occurs in one directive of 107, so the example narrowed the corpus to a single
  document and the leak scanner flagged it. RULE: every literal you invent for a rulebook -- placeholder examples, format
  samples, forbidden values -- must be grepped against the corpus first and chosen to match ZERO documents.
- 2026-07-31 | tooling / A STALENESS GATE THAT FORBIDS A STRING WILL FIRE ON THE SENTENCE EXPLAINING THE WITHDRAWAL | Adding the
  withdrawn value to a "no superseded claim survives" list broke the build, because the metadata comment recording WHY it was
  withdrawn contains it. RULE: assert staleness on the live DECLARATION (the parsed field), never on the presence of a word in
  prose -- honest packages document their own corrections and a substring gate cannot tell a correction from a leftover.
- 2026-07-31 | gap / A REDESIGN IS PROVED BY THE SHAPE OF THE BOARD, NOT BY THE TOTAL | The SA fell 0.7017 -> 0.1321, but the
  number alone is worthless evidence: a submission that produced no files reaches a low total too. What proves the reward moved
  off extraction is that the SAME submission scored F1 0.991 on enumerating the work units and 0.19-0.55 on every judgement axis.
  RULE: before claiming a redesign worked, read the per-axis board and require the extraction layer to stay HIGH. If the scripted
  layer also collapsed, you made the task harder, not different, and the gap you measure will not survive a stronger agent.
- 2026-07-31 | rubric / BEFORE CREDITING A LOW SCORE TO REASONING FAILURE, PROVE THE VALUES ARE IN-VOCABULARY | An off-catalogue
  spelling and a wrong judgement produce the identical low F1, and one is a fairness bug in your normaliser while the other is the
  measurement working. Checked here: 216 of 216 submitted values were inside the closed catalogue, so the axis had genuinely
  measured wrong answers. RULE: diff the submission's value domain against the reference's before writing the number into any
  report -- it is a ten-line script and it is the difference between evidence and an assumption.
- 2026-08-01 | gap / THE MULTI ARM BEING *WORSE* AT THE SCRIPTABLE LAYER IS THE PROOF THE GAP IS REAL | Measured pair: SA 0.1321,
  MA 0.7547, gap +0.6226. The swarm scored LOWER than the single agent on enumeration (action-set F1 0.955 against 0.991) and far
  higher on every judged axis (capability 0.79-0.84 against 0.45-0.55, urgency 0.73-0.78 against 0.19-0.25). RULE: report the two
  boards axis by axis, and treat the scriptable layer as a CONTROL. If the multi arm leads on every layer, you have measured
  effort or budget; only a gap confined to the layer that requires reading is a capability difference.
- 2026-08-01 | rubric / AN AXIS NEITHER ARM CAN PASS CONTRIBUTES NOTHING -- AND YOU STILL MUST NOT RETUNE IT | The evidence-locator
  bars (0.58/0.78) were cleared by neither arm, so 4 of 53 points separated nothing in the graded pair even though the swarm
  doubled its rate. The temptation is to drop the bar onto the observed multi score. RULE: bars set before the runs stay where
  they are; moving one onto a measured score converts the rubric from a standard into a description of what happened. Record the
  dead axis as a known limitation instead, and only revisit it on a later redesign with fresh evidence.
- 2026-08-01 | tooling / A GATE WRITTEN FOR THE PREVIOUS DESIGN FAILS LOUD AND WRONG, NOT SAFE | After a verifier redesign, three
  gates reported failures against machinery the package no longer had: assertions about five LLM criteria per check, a judge
  endpoint, retries and per-model temperature rules, on a grader that calls no model. Nine reported findings, one root cause --
  a dead regex that matched nothing and reported "0 checks", turning every downstream comparison into a false failure. RULE: when
  a verifier changes SHAPE, re-run every gate and diagnose the FIRST failure's root cause before fixing any of them; and delete
  assertions about removed machinery rather than leaving them to fail, replacing each with its inverse (the judge stays gone).
- 2026-08-01 | tooling / READ A VERIFIER'S BOARD BY IMPORTING IT, NEVER BY REGEX OVER THE SOURCE | CHECKS assembled from list
  comprehensions with %-formatted names cannot be enumerated statically, and the regex that tried returned an empty list rather
  than an error -- so the gate compared a 20-entry manifest against 0 checks and blamed the manifest. RULE: a checker that needs
  the graded board must import the module (an import RAISES when it is wrong); a pattern that silently returns empty is the worst
  failure mode a gate can have, because it looks like a finding.
- 2026-08-01 | tooling / VALIDATE A SCRUB PATTERN AGAINST A KNOWN-CLEAN FILE BEFORE TRUSTING ITS REFUSAL | `[a-z]:\\` as a
  Windows-path scrubber matched every JSON escape in an agent trajectory -- "Steps:\n" reads as a drive path -- and blocked the
  build on 35,635 trainer paths in logs that contained none. Anchoring on a real path component (>=2 chars between separators)
  took it to 0 without weakening it. RULE: a secret/path scanner must be run against a file you KNOW is clean and against one you
  know is dirty; a scanner only ever tested on dirty input cannot distinguish a refusal from a bug, and a noisy gate gets
  --force'd, which is how a real leak ships.
- 2026-08-01 | integrity / A CLAIMS GATE NEEDS A THIRD VERDICT: ATTRIBUTED, NOT JUST OK/UNVERIFIED | Honest metadata cites figures
  the shipped package cannot re-derive -- pilot-study accuracies, and scores from BEFORE the change the text is describing. A
  binary gate marks all of them unverified, and the cheapest way to a clean run becomes deleting the honest history. RULE: let a
  decimal that appears verbatim in a recorded study file pass as ATTRIBUTED with the filename printed, and fail only a decimal
  that traces to NOTHING. Strictness about invented numbers is preserved; the incentive to erase provenance is removed.
- 2026-08-01 | tooling / A STALE MEASUREMENT CORPUS MAKES A TRUTHFULNESS GATE LIE IN BOTH DIRECTIONS | The fixture results file
  was never regenerated after the redesign, so the gate checked today's metadata against last month's scores: it flagged correct
  new figures as unverified AND would have blessed any stale figure that happened to match an old fixture. RULE: the artefact a
  truthfulness gate reads must be written BY the measurement run, not by hand, and only on a complete run -- a partial run that
  overwrites it silently retires the fixtures it did not build.
- 2026-07-31 | rubric / A CLOSED-VOCABULARY AXIS DISCRIMINATES ONLY WHERE THE CLASS HAS NO SURFACE MARKER | The single sharpest
  result in the run: the agent emitted the LARGEST reference class ZERO times (47% of the wave) and stamped one default class on
  96% of rows. That class is precisely the one whose value cannot be found -- the document defers the deadline to an adopted
  service document instead of stating it, so a route hunting for a number finds some other number and stamps the wrong class.
  RULE: when choosing a categorical axis, check what fraction of the population belongs to classes with NO findable marker. That
  fraction, not the class count, is the axis's real discriminating power.
- 2026-08-01 | packaging / `check_function` NAMES THE FUNCTION, NOT THE CHECK | S-08 resolves every
  `rubric_manifest.json` `check_function` against a top-level `def` in `tests/verify.py`. Building checks as
  `lambda ctx: fn(ctx, i)` from a factory leaves 16 of 20 entries with no function to name, so the manifest fell back to the
  check's DISPLAY name and the official gate rejected all 20. RULE: give every rung of a sharded ladder its own named `def` that
  delegates to the parameterised implementation, and emit `fn.__name__` from the generator rather than any hand-written string.
- 2026-08-01 | gates / A LOCAL GATE CAN ASSERT THE DEFECT AND STAY GREEN | The local checker required
  `check_function == check name` -- exactly the thing S-08 rejects -- so it passed while the official gate failed all 20 entries.
  A second gate compared `list.sort()` to `list.sort()`, i.e. `None == None`, and asserted nothing at all. RULE: a gate must
  assert what the OFFICIAL checker resolves, not what the generator happens to emit; and any assert whose two sides could both be
  `None` is not a test. Sanity-check new gates by feeding them a known-bad input once and confirming they go red.
- 2026-08-01 | packaging / `[task].description` HAS A HARD 10-500 CHAR BOUND | Shipped at 1515 chars and was rejected. This log
  already carried the same rejection on an earlier task at 1558 chars: the lesson was written down but never turned into an
  assertion, so it recurred. RULE: when a lesson is about a numeric bound, the same commit must add the gate. Parse the value as
  TOML, never regex it -- it is one long quoted line, which is exactly how it grows unnoticed.
- 2026-08-01 | gates / AUDIT THE DELIVERABLE BY EXACT NAME, NOT `zips[0]` | `zip_audit` took the first `.zip` from `os.listdir`,
  and the downloaded run bundles live beside the deliverable: `<TASK>-multi.zip` sorts BEFORE `<TASK>.zip` because `-` (0x2D) <
  `.` (0x2E). So the audit read a run bundle and passed on the `task.toml` frozen inside it at run time, while the real archive
  went unchecked. RULE: address the deliverable as `TASK + ".zip"`, assert it exists, and print what is being ignored.
- 2026-08-01 | gates / A GATE THAT PRINTS `FAILURES: 1` MUST EXIT NON-ZERO | `zip_audit` reported a failure and returned 0 in the
  same breath, so a suite loop over `$LASTEXITCODE` recorded it as a pass. RULE: every gate ends in `sys.exit(1 if failed else
  0)`, and a check that parses a file must catch its own parse error and report a FAIL -- an uncaught exception aborts the run and
  silently unreports every later check, so one bad character looks like a crash rather than the single thing that is wrong.
- 2026-08-01 | gates / INVERT A PENDING-STATE ASSERTION ONCE THE RUN LANDS | A gate asserting "the multi-agent side is still
  declared unmeasured" was correct while the run was pending and became a guard against the truth the moment it was measured.
  RULE: assertions about work-not-yet-done are dated; when the work lands, flip them to assert the recorded values are present and
  that no stale "unmeasured" caveat survives beside them.
- 2026-08-01 | gates / IMPORTING THE GRADER FROM A GATE WRITES `__pycache__` INTO THE DELIVERED TREE | Reading `verify.CHECKS` by
  import (correct, since a regex cannot enumerate a comprehension-built table) creates `tests/__pycache__`, which trips the
  no-build-artefacts rule -- a gate failing the package while checking it. RULE: set `sys.dont_write_bytecode = True` before the
  import and run ad-hoc probes with `python -B`, since a stray `python -c` that imports the grader leaves the same droppings.
- 2026-08-01 | runs / A WIRING-ONLY VERIFIER CHANGE NEEDS NO RERUN -- PROVE IT BY REGRADING | Renaming/rehoming check callables
  after both arms were spent does not require re-spending them: the agent never reads `verify.py`, `task.toml` or the manifest,
  and S-07 is triggered only by `instruction.md` / `decomposition.yaml`. Re-scoring the two downloaded bundles offline reproduced
  the shard seeds AND both scores exactly (7/53, 40/53), and the fixture battery was unchanged.   RULE: keep a bundle-regrade script
  so post-hoc grader edits can be shown score-neutral instead of argued; and keep ITS regexes current -- a stale pattern here
  printed the right reward to the terminal while persisting `reward: null`, which is worse than failing.
- 2026-08-03 | QD-03.1 / FIELD-EQUALITY AGAINST A FULL HAND-LABELLED REFERENCE IS AN ANSWER KEY | A verifier that
  compared required_capability / urgency / contingency / quantities / evidence_spans field-by-field against
  tests/reference_actions.json (52 of 53 points) hard-failed QD-03 check 1 even though the difficulty deck says
  "grade correctness vs a real reference." The reconciliation is QD-04.12(iii) / the 2026-07-22 lesson: keep
  correctness, move the DECISION to a different-family LLM judge handed the REAL source text; deterministic code
  may ground ids/spans and check INTERNAL consistency only. FIX applied: A/B judged via W&B zai-org/GLM-5.2;
  P = internal lawfulness; E opens the real AD file; X2-X4 use a 6-20 action partial_oracle SAMPLE; full
  reference_actions.json removed from the shipped package.
- 2026-08-03 | QD-01.1 / EM DASHES ARE AN ENUMERATED AI-STYLE FAIL | instruction.md with 11 U+2014 em dashes across
  7 of 9 paragraphs failed authorship_and_professional_framing. Rewrite asides into separate sentences or
  commas/parentheses. Assert `\u2014` absent in the local gate.
- 2026-08-03 | QD-06.7 / CUSTOM subagent_type VALUES ARE INVISIBLE TO THE HARNESS | Declaring specialist/assessor/
  planner/assembler/auditor gives the orchestrator nothing it can spawn: the harness only knows general (manager)
  and explore (leaf, task tool blocked). Result: improvised generic Managers and the final tier absorbed by the
  orchestrator. RULE: every node is `general` or `explore`; put an explicit manager tier above fan-out leaves;
  confirm realization on the actual multi run (stochastic).
- 2026-08-03 | QD-06.4 / depends_on MUST NAME EVERY PRODUCER THE DESCRIPTION CONSUMES | consistency_reviewer said
  it reconciles against the enumerated action set but omitted inventory_builder_* from depends_on. Add them.
- 2026-08-03 | judge / A CATALOGUE-LISTED MODEL SLUG IS NOT A SLUG YOUR SANDBOX KEY MAY USE -- SHIP A FALL-FORWARD LIST |
  `zai-org/GLM-5.2` is documented generally-available and still answered `HTTP 403 Forbidden` from inside the mascloud
  verifier sandbox, fail-closing an entire 29m / $6 single-agent run to 0.0 AFTER the deterministic half had already
  passed 9/42. It was not a bad key: the agent step ran on the same key, and a sibling task's cloud verifier answered
  1061 judge calls on `deepseek-ai/DeepSeek-V4-Flash` against the same endpoint. RULE: pin an ORDERED list of
  different-family candidates and use the first the endpoint actually serves; treat HTTP 400/403/404 as
  "next candidate", retry only transient codes, still fail closed if none answer; put the HTTP response BODY in the
  error and the RESOLVED slug in reward.json -- a bare "403: Forbidden" costs a whole run to diagnose. Verify the
  judge slug with one cheap live call BEFORE spending an arm on it.
- 2026-08-03 | judge / WHEN THE KEY IS SANDBOX-ONLY, MAKE THE VERIFIER ANSWER THE ENTITLEMENT QUESTION ITSELF |
  Follow-on to the 403 above: the recommended "one cheap live call first" is IMPOSSIBLE when the trainer has no
  personal inference key -- the key exists only inside the run -- and `mascloud` has no verify-only/re-grade command
  (`login|logout|run|runs|download`), so every diagnosis attempt costs a fresh paid arm. RULE: have the grader
  resolve its candidate list against the provider's own `GET /v1/models` at the START of grading, print the served
  ids, and record them in reward.json next to the resolved slug. Then even a fail-closed 0.0 returns the
  entitlement list instead of one opaque status code, and the second attempt is informed rather than another guess.
  Corollary: a gap is only valid if both arms recorded the SAME resolved judge -- diff that field before quoting
  MA - SA.
- 2026-08-03 | judge / A 403 FROM AN LLM ENDPOINT IS THE CDN REFUSING YOUR HTTP CLIENT BEFORE IT IS EVER A KEY OR A
  MODEL PROBLEM | Two graded arms (~$11, 55m) were lost to this and the first was MISDIAGNOSED as model entitlement.
  `api.inference.wandb.ai` is behind Cloudflare, which answers urllib's default `Python-urllib/x.y` User-Agent with
  `HTTP 403` + `error code: 1010` BEFORE authentication or model routing. The tells were all in the second run's log:
  three different vendors' models failed with BYTE-IDENTICAL bodies, and `GET /v1/models` failed the same way -- listing
  models cannot be an entitlement question. RULE: send an explicit `User-Agent` on every request from a verifier; treat
  a 1010 body as an EDGE refusal that is neither retried nor walked to the next candidate; and remember a
  "prefer requests, fall back to urllib" transport silently takes the BLOCKED path on a bare `python:*-slim` image that
  has no requests. DIAGNOSE IT FOR FREE: `GET /v1/models` with NO Authorization header -- 401 means you reached the
  API, 403/1010 means you never did. That probe needs no key, no sandbox and no paid arm, and it is the check that
  should have run before either arm.
- 2026-08-03 | rubric / COUNT THE JUDGED ITEMS *PER CHECK*, NOT PER RUN -- A SAMPLED JUDGE CAN BE SWINGIER THAN ITS OWN
  BARS | A board looked well scaled at 218 rows and 42 points, but `JUDGE_SAMPLE = 24` sharded three ways left EIGHT
  judged items deciding each 3-point check: one flipped verdict moves the measured rate 0.125 while the bars sit 0.15
  apart, and the shard draw is reseeded every run from a content hash of the submission. Population size does not make
  a check stable; items-per-check does. RULE: before spending an arm, point the real verifier at a submission with the
  path env vars (`AGENT_LOGS` / `INPUT_ARTIFACTS` / `TESTS_DIR`) and print, per check, the judged-item count, 1/n, and
  the passes needed -- it needs no judge key and no API calls. Require 1/n comfortably below the gap between adjacent
  bars. Raising the sample is cheap (a sibling task answered 1061 judge calls in one verifier run), so the usual fix
  is more sampled items, not friendlier bars.
- 2026-08-03 | projection / AN OFFLINE PROXY THAT SCORES EVERY JUDGED CHECK AS FAILED IS A FLOOR, NOT A FORECAST |
  Reference-exact-match stands in for the judge during offline projection, but a judge asked "is this defensible from
  the source text" is systematically MORE lenient than equality with one frozen label, so the live arm banks judged
  credit the proxy gave it zero for. Quote such a projection as a lower bound with the judged points named as
  unmeasured, and state which specific checks are one item from flipping, rather than presenting the proxy total as
  the expected score.
- 2026-08-03 | rubric / SOFT E+P AFTER QD-03 REBUILD RECREATES THE HIGH SA FLOOR | Converting A/B to an LLM judge
  while leaving evidence as "opens file" and placement as "internally lawful vs own (wrong) capability" let the
  last SA bank ~22/40 (~0.55) with a 95.8% fixed-window stamp. Praised samples (Healthcare quote round-trip,
  North Coast substantive depth) refuse credit for consistent fabrication. FIX: gate E and P on capability
  judge PASS; add urgency stamp RH (max class share < 0.60); majority-vote A/B (3 runs). Offline proxy regrade
  of last CSVs: SA 9/42=0.214, MA 31/42=0.738, gap 0.524. Fresh live SA/MA still required.

- 2026-08-03 | rubric / LLM JUDGE MUST RECEIVE THE TASK'S PUBLISHED DECISION RULES AND THE RIGHT SOURCE WINDOW | An inverted SA/MA pair (SA 0.3095 > MA 0.2619) was not a gap failure in the deliverables: MA whole-file capability accuracy vs the frozen reference was 0.812 vs SA 0.521, and one MA shard was 8/8 reference-correct on both axes while the live judge scored it 2/8 and 3/8. Two verifier bugs, both measured: (1) the capability prompt handed bare catalogue slugs and asked for "best fit", omitting rulebook �4.1's binding choosing rule / rarer-competency tie-break / follow-the-work-ordered guidance, so the judge systematically accepted verb-reachable generics that SA over-produced; (2) both axes were graded against the capability `evidence_locator` window (�4.4), so axis B asked the judge to confirm a document-level negative (`per-adopted-document`) from a capability citation -- SA's B ceiling under that window was 0.167 against bars of 0.50/0.68/0.82 and it scored 0/24. RULE: port the agent's own rulebook definitions and choosing rules into the judge prompt verbatim; grade each axis against the source region that can answer it (Compliance / Required Actions for urgency, not the capability locator); raise `JUDGE_SAMPLE` so items-per-shard beat bar spacing; and write every judged action's verdict/votes/reason/shard/submitted values into `reward.json` `judge_log` so the next disagreement is diagnosable without a re-run. This is calibration to the published standard, not leniency: the same change makes the judge STRICTER on generic-for-specialised substitutions.
- 2026-08-04 | judge / CAPABILITY EXCERPT + ACTION IDENTITY ARE SEPARATE BUGS; FIX BOTH OR MULTI-ACTION DOCS STAY BLIND | After calibration, MA still scored 0.2857 against reference-correct ~0.78 capability / ~0.85 urgency. judge_log + excerpt replay: 16 capability false FAILs never saw the regulatory mandate because _excerpt_for_action still windowed around the agent evidence_locator (72/72 judged rows); urgency already used Compliance but multi-action docs got byte-identical excerpts with only an opaque action_id, and false-FAIL rate rose with actions-per-doc. RULE: both A and B call _compliance_excerpt_for_action; every judge payload/prompt carries ction_description; delete the agent-locator capability builder; assert all three in static checks. Fixing excerpt alone without identity recreates the urgency bug on capability.

- 2026-08-04 | judge / MEASURE THE JUDGE'S FALSE-FAIL RATE SEPARATELY FOR EACH ARM -- A BIASED JUDGE EATS THE GAP FROM
  THE GOOD ARM ONLY | On an inverted pair the reflex reading is "the judge is noisy, raise the sample". Grading the
  logged verdicts against a frozen trainer reference ON THE ROWS THE JUDGE ACTUALLY SAW showed something worse and
  directional: the judge failed correct rows at 0.279/0.324 on the strong arm but only 0.169/0.154 on the weak one,
  because a false fail needs a correct row to land on and the strong arm has far more of them. A real reference gap of
  0.370 and 0.607 was delivered as 0.264 and 0.388. Sampling noise is symmetric and cannot do this. RULE: from
  `judge_log`, compute per arm and per axis the reference-correct rate, the judge PASS rate, FAIL-on-correct and
  PASS-on-wrong. If FAIL-on-correct is materially higher on the better arm, the judge is systematically destroying the
  signal and no bar, weight or sample size will recover it -- fix the prompt and the source window first.
- 2026-08-04 | judge / PROBE THE EXCERPT THE MODEL RECEIVES, NOT THE INTERMEDIATE YOU BELIEVE DETERMINES IT | A probe
  reported 106/107 compliance headings matched and the excerpt builder looked healthy, while the judge kept complaining
  it had been shown only administrative or cost text. The builder anchored on the first match of "Material Incorporated
  by Reference", a heading that appears TWICE in a Federal Register AD -- once in the ADDRESSES front matter and once as
  the regulatory paragraph -- so every excerpt opened with ~2,800 characters of contact details. The probe measured
  whether a heading was FOUND, never whether the excerpt OPENED on the mandate. What found it was printing the first 400
  characters of the actual payload. RULE: assert on the bytes handed to the model (first N characters, does it start on
  the mandate, is it non-empty, is it in bounds) for EVERY unit; a structural landmark that occurs more than once in a
  document family needs a positional constraint, not just a regex.
- 2026-08-04 | judge / TELL THE JUDGE THE UNIT OF ACCOUNT AND MAKE IT STATE ITS OWN ANSWER BEFORE ITS VERDICT | Two
  further defect classes showed up in the logged reasons: the judge failed a row because a DIFFERENT action in the same
  document had a different compliance time (normal for a multi-action regulation, not an error), and it returned FAIL
  under reasoning that agreed with the submitted value. Neither is a knowledge failure. RULE: state in the system role
  that the graded unit is ONE row, that sibling items in the same source are expected and are never by themselves a
  reason to fail it, and require the judge to emit its own answer for the field before its verdict; log both so a
  verdict/reason clash is visible in the artifact instead of needing a re-run to find.
- 2026-08-04 | integrity / SANITISE AND ROLE-ISOLATE EVERY AGENT CELL IN A JUDGE PROMPT, THEN MEASURE WHAT THE
  SANITISER BREAKS | Splicing agent free text into a judge prompt verbatim lets the submission address its own grader,
  and a reviewer will find it. The fix is three-layered: grading standard in the SYSTEM role, agent text stripped of
  control characters, newlines, code fences, role markers and instruction-shaped spans and length-capped, and the result
  wrapped in an untrusted-data fence the judge is told cannot change the rules. RULE: after writing the sanitiser, count
  how many REAL submitted cells it alters beyond whitespace (1 of 218 and 0 of 231 here). A sanitiser that rewrites
  honest answers is a worse defect than the injection hole, and the count is the only way to know.
- 2026-08-04 | rubric / A STAMP GUARD'S BAR MUST BE MEASURED ON THE REFERENCE FIRST -- THE RIGHT ANSWER IS OFTEN
  LOPSIDED | Copying a working urgency stamp guard (max class share < 0.60) onto a contingency column would have FAILED
  a perfect submission: most mandated maintenance is genuinely unconditional, so the reference's own top class is 0.673.
  The signal that separates a decided column from a stamped one was not the share but the VARIETY -- whether a third
  class appears at all. Bar set at 0.85 share plus at least 3 of 4 classes; the reference passes, and the weak arm fails
  on two classes split almost exactly in half. RULE: compute the reference's own distribution before choosing any
  concentration bar, and prefer the statistic that a correct answer satisfies with margin.
- 2026-08-04 | rubric / CLOSE THE FABRICATION FLOOR WITH A GROUNDING CHECK, NOT A STRICTER SCHEMA | Schema plus
  cross-file-consistency checks are satisfiable by internally consistent invented CSVs -- the agent never has to open a
  source document. Adding a check that submitted source ids exist in the frozen corpus AND every citation resolves to a
  real in-bounds non-blank span of THAT document closes it for 2 points, costs an honest submission nothing (both real
  arms scored 1.000) and needs no answer key, because it only asks whether the cited text exists. RULE: for any task
  citing a frozen corpus, price the "did you open it at all" question explicitly; character offsets into a large corpus
  cannot be derived from a manifest.
- 2026-08-04 | harness / RAISING A JUDGE SAMPLE CHANGES THE VERIFIER'S RUNTIME -- SIZE THE SAMPLE TO THE SCHEMA CAP
  | Going from 72 to 108 judged actions took the grader from ~1,280s to ~1,920s of judge calls against a
  `[verifier] timeout_sec = 1800`, which would have killed grading mid-flight and returned a reward that reflected a
  timeout rather than the submission -- indistinguishable from a bad arm in the results table. Harbor's schema HARD MAX
  is 1800 (a ZIP with 5400 was rejected 2026-08-05). RULE: after any change to sample/batch/majority, recompute
  calls × measured sec/call and either shrink the sample or fit under ≤1800 — do NOT "fix" an oversize sample by
  raising timeout above the schema max. The verifier's budget is identical for both arms within that cap; the agent's
  timeout is the one that must not move for gap integrity.
- 2026-08-04 | packaging / PAIR THE ARMS BY GRADER GENERATION, NOT BY RECENCY -- CHECK THE reward.json FINGERPRINT |
  A package was about to ship an SA arm and an MA arm produced by DIFFERENT verifier generations: the MA `reward.json`
  had no `judge_sample` and no `judge_log` at all, because it predated both. Two arms graded by different code are not a
  pair and any difference between them is uninterpretable. RULE: before shipping or quoting a gap, diff the fingerprint
  fields across the two `reward.json` files -- `points_available`, check count, `judge_sample`, `judge_model_resolved`
  and the `judge_log` row schema. Also note that `mascloud runs` renders its table at a fixed 80 columns and TRUNCATES
  every run id, so if the download that carries the id is gone the run cannot be fetched again; keep the run id in the
  notes at download time.
- 2026-08-04 | verifier / PLATFORM reward.json IS FOUR FIELDS — OVERALL `reward` IS THE RUN SCORE, NOT A /6 BLEND |
  Team update requires `/logs/verifier/reward.json` with exactly
  `reward`, `total_static_check_score`, `total_reward_hacking_check_score`,
  `total_partial_oracle_check_score` (means of evaluated checks in each bucket).
  An earlier reading of the DM reference `verify.py` treated
  `reward = (S*1 + RH*2 + PO*3) / 6` as the platform overall score; DM
  clarification (2026-08-05, Mehedi) for completed arms: overall `"reward"`
  MUST equal the run's `reward.txt` / points board score (e.g. SA 22/46 =
  0.4783), and the three bucket means are reported separately — do NOT
  average them into reward and do NOT replace a finished arm's score with
  the /6 blend (that produced 0.5556 vs 0.4783 on the same SA board).
  `reward.txt` alone fails QG; `test.sh` must write an all-zero four-field
  `reward.json` on crash. RULE: ship the four-field schema; assert
  `reward.json.reward == reward.txt` within float noise; when manually
  patching completed logs, copy the verifier's overall score into `reward`
  and fill bucket means from the per-check vectors — never invent a third
  formula. Re-run both arms only when the verifier CODE changed the board.
- 2026-08-04 | task design / LOWER SA WITH STAGED ARTIFACTS, NOT HARSHER CHECKS -- B+M+A |
  Archived SA solved packaging via download→extract→heuristic→generate_deliverables while
  reading checks already crushed substance. Extra charts/rollups raise SA; frozen oracles
  fail QD-03. The lever that matched the failure mode was requiring intermediate per-record
  working files, a dependency chain (rows→cluster profiles→priority→finals), and deep
  priority write-ups for the ten lowest-fidelity rows -- same instruction both arms -- with
  only additive verifier coverage for those new paths. RULE: when SA substitutes a cheaper
  problem, add required intermediate products that ETL cannot fake, mirror them in
  decomposition.yaml, and do not chase the gap by tightening existing judges or weights.
- 2026-08-05 | QG / MANIFEST MUST MATCH CODE; JUDGE OUTAGE FAIL-CLOSED; FIRST-DESIGNATION GATE |
  Local QG REJECTED on QD-03.6 (manifest lied about registration corroboration, derived
  artefacts priority overlap, notes hard-zero), QD-06.6 (decomp recovery how-to), and
  QD-10 (span-first ETL, verdict_weight=1 on empty judge, outcome clone, shape-only
  staging, github cue harvest). Fixes that held: rewrite DOCs from the live function;
  strip recovery language from decomposition; gate grounding/methods on earliest
  primary-designation region; verdict_weight and LLM checks fail closed to 0.0; scale
  staging + availability by reading_truth; github only with deposit context. RULE: after
  any verifier edit, regenerate the manifest from DOC strings; never leave empty
  execution_logs and call the package shippable — QD-05/07/09 need fresh SA+MA logs.
- 2026-08-05 | QG draft / DOCS MUST MATCH FAIL-CLOSED; FENCE JUDGE DATA; SCALE AGREEMENT BY TRUTH |
  Draft review QD-03.6/08.24/10.1-10.3: briefing manifest omitted reading-truth multiply;
  task.toml still said grader failure returns None/excluded while LLM checks returned 0.0;
  evidence vocabulary ignored first_designation_ok; docket/derived scaled by grounded_share
  only; judge_json concatenated system+user undelimited. Fix: align reward_formula/task.toml
  to fail-closed-0.0 (exceptions still None); llm_status degraded when calls==0; gate Methods
  vocab on first_designation_ok; multiply docket+derived by reading_truth_share; system/user
  roles + <submitted_data> fences. RULE: after any fail-closed change, grep task.toml and
  manifest for stale "EXCLUDED"/"never silently zeroed" on LLM outages; keep QD-07 logs as a
  separate hard stop.
- 2026-08-05 | packaging / VERIFIER timeout_sec SCHEMA MAX IS 1800 — DO NOT SHIP 5400 |
  FAA-AD-WAVE zip failed Harbor schema validation with `[verifier] timeout_sec = 5400`
  (needed for a 108-sample judge). Cap is 60–1800. Fix: set 1800 and shrink/keep the
  judge sample so grading finishes inside the cap. RULE: treat 1800 as a hard packaging
  constraint in static checks; size JUDGE_SAMPLE from measured sec/call, never from
  wishful timeout.
- 2026-08-05 | metadata / dag_depth IS MANAGERIAL TIERS (≥2), NOT LONGEST depends_on PATH |
  Local static check required declared `dag_depth` == longest YAML path node-count (~7 on
  task 3) while the owner wanted managerial depth 3; official QG only requires ≥2 and a
  non-flat star. RULE: declare managerial / observed spawn depth; do not reject a valid
  hierarchical package solely for path-length ≠ declared depth; after runs, prefer
  rewriting depth from the MA trajectory (item E) over inventing equality with YAML paths.
- 2026-08-05 | reward.json / DM CLARIFICATION — `"reward"` = reward.txt SCORE; BUCKETS ARE REPORTING |
  Slack (Mehedi): do not average bucket means into the overall score; the example
  `(0.875+0.4825+0.875)/3 ≠ 0.667` in the DM note is illustrative/inconsistent with a plain
  average; for this situation overall score = the run's reward.txt. RULE: when patching
  completed SA/MA logs, set `reward` to the points-board score already earned, fill the three
  `total_*` means from per-check vectors, and keep `reward.json.reward == reward.txt`. The
  2026-08-04 lesson that equated platform reward with `(S*1+RH*2+PO*3)/6` is SUPERSEDED for
  overall scoring (the /6 blend remains a DIFFERENT diagnostic number — do not ship it as
  `reward` on a finished weighted points board without a fresh policy ruling).
- 2026-08-05 | prompt sync / TASK3 EXPERIENCE FOLDED INTO STANDING RULES |
  Gaps found while authoring FAA-AD-WAVE that the creation prompt still contradicted:
  (1) reward.txt-only / flat weight==1 gates vs four-field reward.json + category 1/2/3;
  (2) "raise verifier timeout" vs schema max 1800; (3) dag_depth must equal path length;
  (4) Fireworks-era judge defaults vs W&B + User-Agent 1010; (5) missing judge prompt-hygiene
  and arm-pairing-by-grader-generation as standing checks. Standing sections P21-2/P21-5,
  PHASE 2 verifier, task.toml, `_g_*` gates, and this log were updated — re-read those
  before the next task, do not rely on the superseded /6 overall-score reading.
- 2026-08-05 | S1 | trigger: workspace docs reorg | PATH REPOINT |
  Updated every absolute/relative doc path in REFERENCE MATERIAL, DOCUMENT-
  TO-STAGE MAP, capture/reuse streams, QG ledger, Gate 3 / Phase 4 / Phase 4.5
  citations, and example-task discipline to the numbered catalog under
  `PHASE_2/documentations_phase_2/` (`00_authority`…`09_qg_reviews`). Trainer
  Guidelines filename is now `(2).txt` (v1.1); client feedback is
  `05_feedback/batches/MAS_Client_Feedback_Document_2026-07-17.txt`; QG reports
  are `09_qg_reviews/raw_reports/`. Phase-1 superseded copies pointed into
  workspace `_archive/`. Catalog pointer: `documentations_phase_2/README.md`.
- 2026-08-05 | S1 | trigger: `00_authority/Verifier & Rubric Manifest Standards
  (Effective Immediately).txt` (Batch-12/14) | VERIFIER STANDARDS FOLDED IN |
  Binding client/team announcement now in force (QG S-08 + QD-03 checks 7–8).
  Changes: (1) Item B — replaced "NO RUBRIC WEIGHTING -> AUTO-REJECT" with
  content≥40% / honest-manifest / preferred category 1/2/3. (2) P21-2 —
  `verifier_type = "hybrid"` for mixed deterministic+LLM graders; reward.json
  must include per-check notes + LLM justifications. (3) P21-3/P21-5 —
  unresolved flat-vs-weighted conflict RESOLVED toward Verifier Standards;
  added P21-5b held-out + hollow-fixture discrimination; added P21-12 summary.
  (4) CS-2/CS-3, SCORING INTEGRITY positive design, baseline B4, Phase1→2
  shift #1, Gate 3 rubric docs, DOCUMENT-TO-STAGE, REFERENCE MATERIAL —
  all updated. (5) Older "always executable for hybrid / no weightage"
  onboarding lines marked SUPERSEDED. Re-read P21-2..P21-12 + authority file
  before the next Gate 3.
- 2026-08-05 | S1 | trigger: `00_authority/Production Rework Requirements.txt`
  | PRODUCTION REWORK WAVE FOLDED IN |
  Binding team directive: pause new authoring; Completed→Rework. Changes:
  (1) Header AUTHORITATIVE SPEC now lists three authority docs; Production
  Rework content ≥60% / structural ≤40% SUPERSEDES Verifier Standards 40%/60%
  floor. (2) Opening PRODUCTION REWORK WAVE + full P21-13 (mascloud
  force-reinstall; single/multi/multi_noplan; high_level_prompt.md rules;
  multiplicative content-quality signal; ≥20pp gap; static+LLM QG on
  resubmit). (3) Item B / P21-5 / P21-12 #3 / manifest weight notes aligned
  to 60%/40%. (4) Packaging S-02 EXTENDED to seven-item root
  (+ high_level_prompt.md); execution_logs require three mode trees; Phase 5
  merge of three result ZIPs; `_g_seven_item_root`. (5) REFERENCE MATERIAL +
  DOCUMENT-TO-STAGE MAP updated. Cursor rules scoring-integrity /
  delivery-packaging / task-authoring synced. Re-read P21-5 + P21-13 before
  any rework resubmit.
- 2026-08-05 | S1 | trigger: All-Hands Verifier Standards notes filed |
  ALL-HANDS 2026-08-04 NOTES WIRED |
  Moved `All -Hands - Verifier & Rubric Manifest Standards [MANDATORY] -
  2026_08_04 20_29 IST - Notes by Gemini.txt` into `02_onboarding/`; linked
  from authority announcement header + README + REFERENCE MATERIAL + Gate 3
  DOCUMENT-TO-STAGE. Expanded P21-12 with meeting nuances: copy-from-input
  ≠ content (classify as static); simple additive/1-2-3 scoring (opaque
  whole-score gates reject); print→test-stdout for every check + LLM
  justification; hollow-fixture score bar; optional MA-first search space.
  Meeting's ≥40% content share remains historically accurate; Production
  Rework ≥60% still governs current deliveries.
- 2026-08-05 | S1 | trigger: team W&B Qwen vision verifier template |
  JUDGE CALL TEMPLATE FILED |
  Moved `WANDB_Qwen_Vision_Verifier_Template/` under
  `03_design_guides/verifier_templates/`. Binding usage: copy the HTTP call
  shape (endpoint, json_object, image+text evidence, retries, infra status)
  into task verify.py; **omit temperature**; vision default
  `Qwen/Qwen3.6-35B-A3B` (smoke-tested only — not a mandate to drop DeepSeek
  for text-only criteria). Template is not a complete Phase 2.1 grader —
  still hybrid + deterministic content share. Updated P21-6, Phase-2 LLM
  section, judge-provider cursor rule, and catalog README. Add User-Agent
  when adapting (CDN lesson still applies).
- 2026-08-05 | S1 | trigger: local QG vs updated QD dims drift check |
  LOCAL QG PROMPT RE-SYNCED TO PRODUCTION-REWORK DIMS |
  `LocalQualityGate_ReviewerPrompt_Phase2.md` still pointed at a six-item
  root, two log modes, QD-03 check-6-only framing, silent fail-closed 0.0,
  and a wrong rubric path (`documentations_phase_2\Quality_dimensions…`
  instead of `01_quality_gate\…`). Re-synced to seven-item root +
  `high_level_prompt.md`, three modes incl. `multi_noplan`, QD-03 checks
  6–9 / content≥60%, INFRA sentinel (not silent 0.0), updated line map,
  and QD-10b-before-QD-10a header order. Also truncated accidental
  duplicate QD-07/08/09 paste junk after QD-10a in
  `Quality_dimensions_phase_2.md`. Rule: when QD dims move, update the
  local gate the same day — wrapper facts override sub-agent reading if
  stale.
- 2026-08-05 | production rework / SEVEN-ITEM ROOT + hybrid + THREE LOG MODES |
  Outcome-Drift Phase A: added `high_level_prompt.md` (~221 words), set
  `verifier_type=hybrid`, reward.json aliases `static_checks` /
  `reward_hacking_checks` / `partial_oracle_checks` beside platform
  `total_*_check_score`, fixed build `taskpath` after slot move to
  `knowledge_research/task4/`. Content share already ~83% under /6 blend.
  RULE: Production Rework deliveries need HLP + force-reinstalled mascloud
  with `multi_noplan` + three fresh log packages before resubmit; do not
  claim ship on package edits alone.

- 2026-08-05 | QG rework / verifier exploit closure | Outcome-Drift |
  Local QG REJECTED on QD-10.1–10.5 / QD-08.24 / QD-04.13 with empty logs.
  Closed package-side exploits: drop every `(0.25+0.75*x)` floor to pure
  `× share × truth`; NO_DRIFT Methods cue gated on abstract outcome carry;
  priority set from contested judge+grounding ids (not self-ranked fidelity);
  charts structural × matrix category/ink agreement; dominance onset 0.70→0.55;
  evidence shingles shared if owners>1; persist/print per-item LLM score+why
  into reward.json. RULE: QG exploit findings about floors / self-rank /
  ink-only charts are package bugs — fix before burning Phase B arms; still
  need three fresh execution_logs modes before claiming ship.

- 2026-08-05 | QG residual exploit closure | Outcome-Drift |
  Re-run QG still REJECTED: residual QD-10.1–10.7 + QD-04.13 + QD-08.24
  (logs still empty for QD-05/07/09). Closed: cue-absent first_designation→False;
  Results verbatim×truth; NO_DRIFT abstract bar 0.60; abstract_headline_claim
  grounded evidence (kept drift judge 0.5); charts×vision + registration_gap
  want_cats=2×clusters; CONTENT_GROUNDING_FULL 0.25→0.55; cluster characterisation
  outcome vocab; LLM item whys to llm_item_justifications.jsonl + stdout summary.
  RULE: after a partial exploit fix, re-run QD-10 — residuals (half-credit paths,
  cue-absent True, uncapped Results, ink-only charts) reappear; print-all LLM
  whys belongs in a detail file + summary, not a 12-line sample.

- 2026-08-05 | QG exploit second pass | hybrid verifier / charts / LLM stdout |
  Re-QG after residual pass still FAILED: drift 0.5 farms reading-truth multipliers;
  first-cue span harvest banks PO-3/RH-1/grounding; abstract bag-of-words paste
  unlocks headline gates; priority/ flood of all ids; charts vision against raw
  matrix self-figures; QD-08.24 requires EVERY llm item score+why on stdout (jsonl
  alone is not enough). Closed package-side: binary drift for multipliers (keep
  0.5 only on drift LLM check); effective_grounding / PO-3 / RH-1 Methods gated;
  headline = lead-sentence substring; docket priority exact set + flood penalty;
  article-tied chart figures; print all `_llm_item_log` rows to stdout. RULE: LLM
  half-credit on a reading check must not propagate into multipliers; content-bucket
  charts need article-tied figures not invented-matrix self-consistency; QD-08.24
  = print every judged unit to stdout (detail file additive). Logs still required
  for QD-05/07/09 — do not claim ship until three modes exist.

- 2026-08-06 | QG temporary review / instruction-verifier sync + working-file depth |
  After hardening headline to verbatim substring, QD-01.5 FAILed because instruction
  still said "in your own words"; QD-10 then found next weak fields: word-count-only
  rationales, presence-only conclusion_claim, matrix_fields checking only
  fidelity_score. Closed: align instruction+decomp with verifier; narrative vocab
  grounding on designation/drift/posture/conclusion; conclusion_claim ≥8 words;
  matrix_fields all 15 keys + per-key row agreement. RULE: when a verifier gate
  tightens a field, update instruction.md the same day; after one exploit pass,
  score every mandated nested key and ground every free-text working-file field
  the instruction forbids as id-swappable. Logs still empty — not package-fixable.

- 2026-08-06 | Production Rework / harness CLI + verify-only scope |
  Team: force-reinstall mascloud so help lists `multi_noplan` AND `verify-only`;
  three modes required; verify-only ONLY for reward.json component-score reporting
  refreshes against valid logs — never after instruction/HLP/decomp/input/
  requirement/behavior edits (those need full mode re-runs). RULE: confirm CLI
  capabilities before any arm; do not use verify-only to paper over a changed
  brief; ask leads before burning runs on doubt.

- 2026-08-06 | Harbor reward.json typing / UI shows 0.0 |
  Outcome-Drift SA graded 0.2759 in verifier/reward.json + test-stdout, but
  `mascloud runs` listed reward 0.0 with ValidationError: Harbor
  `VerifierResult.rewards` is `dict[str, float | int]` only; nested
  `excluded_checks` ([]), `grader_errors` ({}), `per_check`/`checks` (dicts/
  lists), and `llm_item_justifications_file` (string path) failed pydantic and
  the platform fell back to 0.0. RULE: `reward.json` values MUST all be
  numbers. 2026-08-11 verifier-template update tightens this to EXACTLY four
  numeric fields; put
  per-check tables, LLM why paths, and other diagnostics in
  `reward_debug.json` / jsonl / stdout. After fixing shape only, refresh
  with `mascloud verify-only --target-mode <mode>` — do not re-burn the agent
  arm. Always trust verifier artifacts over the runs-table reward when they
  disagree.

- 2026-08-11 | team verifier template / judge plumbing + reward contract |
  Team shipped `SwarmBench_Verifier_Template.zip` as the default verifier
  scaffold for new submissions because recent reworks were dominated by judge
  calls not firing, malformed `reward.json`, empty justifications, and
  manifest/formula weight drift. RULE: start new task verifiers from the
  template plumbing and replace only the six example checks. Use W&B through
  `WANDB_API_KEY`; hardcode the intended judge model in `verify.py`; keep the
  robust "last parseable JSON object" extractor for markdown/thinking-wrapped
  responses; write exactly four numeric fields to `reward.json`; write
  per-check/debug detail to `reward_debug.json`; write substantive judge
  evidence/reason to `judge_justification.txt`. Failed judge calls after
  retries score 0.0 for that specific check and remain in the denominator,
  while the infra failure is made loud in stdout, justification, and debug.
  `rubric_manifest.json` weights and check functions must match verify.py
  exactly.

- 2026-08-06 | Windows mascloud stream UnicodeEncodeError (local EXIT 1) |
  Cloud run SUCCEEDs but local `mascloud run`/`verify-only` follow dies with
  `UnicodeEncodeError: 'charmap' codec can't encode…` when Rich prints Harbor
  box-drawing on a cp1252 console (`legacy_windows_render` → WriteConsoleA).
  Download still works; EXIT_CODE=1 is cosmetic-local only. RULE: in
  `mascloud_client` reconfigure stdout/stderr to UTF-8 (`errors=replace`),
  build `Console(legacy_windows=False)`, and wrap stream prints in a
  `_safe_print` that falls back to ASCII-replace — never let console encoding
  abort `_follow`. On install, if `pipx install --force` fails on old uv,
  use `pipx install --force --backend pip .`. Optional belt: `$env:PYTHONUTF8=1`.

- 2026-08-11 | task7 corpus provenance / A LINKED ADVISORY IS NOT A VENDOR
  ADVISORY BY DEFAULT | Building the 48-case KEV reconciliation corpus exposed
  a recurring authority error: several CVE/NVD-linked references resolved to
  independent research or CISA fallback pages after the first vendor URL was
  unusable. Freeze the final resolved URL, preserve failed candidate notes,
  hash the exact staged file, and classify the final host with a disclosed
  closed rule. Never promote a government fallback, distribution advisory, or
  independent researcher to vendor-controlled evidence merely because the
  file is stored in an `advisories/` directory.

- 2026-08-11 | task7 scoring classification / COPYABLE SOURCE VALUES ARE
  STATIC EVEN WHEN A HIDDEN FIXTURE CONFIRMS THEM | CISA dates/actions, CVE
  state/assigner, and NVD status/CVSS/CWE are directly extractable from the
  staged corpus; putting them in partial-oracle would inflate content share.
  Count those checks as static. Reserve RH/PO for hash-locked quotation
  grounding, independently derived flags/classifications, branch preservation,
  reconciliation quality, and synthesis. A flat one-point board of 8 static +
  8 RH + 5 PO checks gives 38.10% structural / 61.90% content before the
  disclosed content-quality multiplier.

- 2026-08-11 | task7 judge coverage / FULL-COHORT JUDGING MEANS PARTITION,
  NOT SAMPLE | Split a large cohort into disjoint portfolio calls whose union
  is every required unit; keep omitted items at zero in the fixed denominator.
  One portfolio call may return several separately named per-unit axes, but
  no single call may control most of reward. Fence trusted references apart
  from angle-bracket-escaped untrusted submissions, recover the last parseable
  JSON object, coerce malformed scores to zero, and print/persist every item's
  score, evidence, and reason, including omissions and infrastructure failure.

- 2026-08-11 | task7 decomposition / REVIEWERS NEED REPAIR AUTHORITY AND
  HARNESS-VISIBLE TYPES | A downstream reviewer that only counts or merges
  incompletes recreates the planned-agent decay discussed on 2026-08-10.
  Give each bounded reviewer authority to reopen its evidence, correct or
  reauthor bad unit files, and hand corrected payloads to the final editor.
  Every decomposition node still needs the harness-visible `subagent_type`:
  `explore` for non-spawning leaves and `general` for reviewers/managers. Never
  invent specialist/assessor type names, and never leak expected flags or
  adjudications into the plan.

- 2026-08-11 | task7 QG hardening / SCORE EVERY MANDATED SEMANTIC FIELD, NOT
  ITS LENGTH ALONE | Random recent QG reports repeatedly found unscored nested
  fields and word-count-only rationales. For evidence rows, validate that
  `supports_field` is role-compatible. For exception queues, recompute a fixed
  population and require each immediate action to address every triggered flag
  with disclosed semantic anchors, in addition to length and evidence paths.
  Run empty, shallow, hollow, and fabricated fixtures after every such change;
  update instruction/rulebook, verifier, manifest, fixtures, and corpus stats
  together so a local green check cannot mask contract drift.

- 2026-08-11 | S1 | trigger: task7 KEV reconciliation build + random recent
  approved-sample/QG review | TASK CREATION PROMPT SYNC | Folded the source-role
  provenance rule, copyable-field classification, full-cohort partitioned judge
  pattern, supported subagent types, repair-capable reviewer rule, semantic
  field coverage, and signed-authority-vs-meeting gap precedence into the living
  lessons log. Also confirmed two pre-ship traps during the build: omit
  `[agent].timeout_sec` for a genuine long-horizon task instead of exceeding the
  7200-second schema maximum, and treat the W&B-missing smoke results as
  invalid-evaluation floors rather than forecasts of live SA/MA performance.

- 2026-08-12 | task8 regulatory-clock build / HTTP 200 CAN STILL BE A BROKEN
  SOURCE | The first Federal Register corpus freeze passed transport checks but
  stored 200-OK `Federal Register :: Request Access` pages after the raw-text
  endpoint rate-limited the curator. The defect surfaced only when a truthful
  quote-round-trip smoke fixture showed 185 duplicate passages across 192
  quotations. Fix: validate content signatures and cross-record duplicate
  rates before trusting hashes; replace anti-bot/interstitial bodies with text
  extracted from each record's official GovInfo PDF; record `pdf_url` and
  `source_transport`; then refresh agent sources, grader copies, SHA-256 values,
  token/AHT metadata, fixtures, and every smoke result together. RULE: `200 OK`
  proves transport, not evidence authenticity. A fallback is acceptable only
  when it is an official distribution of the same record and the final staged
  artifact is re-hashed and re-tested.

- 2026-08-12 | task8 regulatory-clock scoring / COPYABLE IDENTITY IS STATIC,
  DERIVED CLOCK STATE IS CONTENT | Initial verifier drafting placed document
  number, publication date, and agency in a partial-oracle check merely because
  the grader held an API snapshot. Those values already appear in the
  identity-only agent catalog, so the classification would inflate content
  share. Fix: validate catalog identity in schema/static logic; reserve the
  partial oracle for new effective/indefinite state, action/scope
  classification, predecessor-chain F1, fixed exception triggers, and judged
  source-grounded scope/disposition. RULE: classify by the easiest agent access
  path, not by where the verifier happens to store its comparison value.

- 2026-08-12 | S1 | trigger: new regulatory-clock task + random approved/QG
  review | TASK CREATION PROMPT SYNC | Added the HTTP-200 content-signature
  gate and official alternate-distribution rule to P21-8 and the living memory.
  Confirmed that repair-capable portfolio managers, full-cohort partitioned
  judging, exact four-number reward output, five-series data/SVG agreement, and
  empty/hollow/fabricated discrimination work together without a global score
  gate. W&B-missing smoke scores remain infrastructure floors only; real task
  metadata and the required single/multi/multi_noplan evidence must be updated
  from fresh trajectories before submission.

- 2026-08-24 | task14 packet-layer build / TRUSTED GRADING INPUTS MUST MIRROR
  NEW PUBLIC INPUTS | When a new agent-visible work-allocation file is added,
  add the same verifier-safe copy to the immutable tests input corpus and run
  preflight before any trajectory; otherwise a correct package can fail with
  checks_run=0 for a verifier bootstrap error.

- 2026-08-31 | task4 rework self-audit / BOUND COVERAGE SCORES AND DECLARE EGRESS
  | A count-based check can exceed 1.0 when extra rows are supplied, and a
  networked verifier can be locally correct yet Harbor-inaccessible if
  `allow_internet` is omitted. Bound coverage with a denominator that accounts
  for extras, and verify the explicit environment egress flag before packaging.

- 2026-08-31 | workflow / CLAIM ABSENCE MUST ROUTE, NOT BLOCK | The claim-only
  wording made agents consume the full task-creation prompt and then stop at
  Gate 0/M0 whenever no seed was supplied. Added an early ENTRY ROUTING rule:
  complete accepted claims remain locked briefs; truly absent seed information
  creates a documented original scratch brief; partial/ambiguous claims pause
  once for clarification. Scratch work must still pass real-source,
  buildability, similarity, quality, execution, labeling-link, and packaging
  requirements, and must never fabricate a claim decision or similarity score.

- 2026-09-01 | verifier judge-schema remediation / VALIDATE HTTP-200 CONTENT
  INSIDE THE RETRY LOOP | A judge call returned transport-successful JSON that
  omitted required cohort items; validating only after `judge_call()` returned
  bypassed retries and converted completed checks into a whole-run zero
  sentinel. Validate exact IDs, required fields, bounded scores, and non-empty
  justifications before declaring a call successful; retry malformed 200
  responses, and retain an exhausted individual criterion at `0.0` with loud
  infrastructure diagnostics instead of discarding the rest of the board.

- 2026-09-01 | planning-operations scale / CLEAN IDS PLUS JOINABLE APIS ARE NOT
  LONG-HORIZON WORK | A 192-row inspection docket with official Socrata IDs
  collapsed to one fetch-and-template script because the graded work was field
  substitution, not reading. Use frozen unstructured unit files, exact
  contiguous quotes, held-out classification, and many unique two-unit
  authored comparisons so a generator cannot clear content credit.

- 2026-09-02 | local QG / TEMPLATE LEFTOVERS AND SELF-HASHES FAIL THE PACKAGE
  BEFORE ANY RUN | After adapting an approved sample, leftover field names,
  empty phrase maps, and old deliverable paths make the verifier unfaithful;
  `^##` counts fenced memo headings; a file_manifest self-row is always stale;
  declared dag_depth must equal the computed depends_on path. Grep adapted
  names, derive dates/labels from disclosed source rules, omit the manifest
  from its own hash table, and keep decomposition at roles plus I/O only.

- 2026-09-02 | verifier / a genuine SA run silently became invalid infra, not
  a low score | `verify.py` added a `scoring_formula` STRING key straight into
  the four-numeric-field `payload` dict that gets written to `reward.json`;
  Harbor's `VerifierResult` pydantic model rejects any non-numeric reward
  value, so `verifier_result` came back `null` and the trial recorded a
  `ValidationError` exception even though the same run's own `reward_debug.json`
  showed a real, healthy `0.77` score underneath. Never let a string/list/dict
  metadata field reach the `payload` object that gets serialized straight to
  `reward.json`; keep exactly the four required numeric fields there and put
  `scoring_formula` (and any other provenance) only in `reward_debug.json`,
  `verifier_status.json`, the manifest, and stdout. Add a one-line unit check
  that asserts every value written to `reward.json` is `int`/`float` before
  shipping, and apply the same audit to `test.sh`'s crash-fallback JSON
  literals, which are easy to miss because they are plain `printf` strings.

- 2026-09-03 | task rework / AGENT-VISIBLE REFERENCE SNAPSHOTS TURN RESEARCH
  INTO TEMPLATE FILLING | A single agent generated a hard-coded portfolio
  without visiting a source because frozen source text in the runtime inputs
  revealed the answer substrate. Keep immutable public fallbacks in
  `tests/verifier_inputs/` only, require direct route retrieval receipts and
  saved captures for the agent, and test an empty/default-shaped fixture so
  absent records cannot earn credit through true-by-default branches.

- 2026-09-08 | multi decomp / STRUCTURAL CSVS WITH UNGROUNDED QUOTES SCORE ~0.3
  EVEN WHEN FILES LOOK COMPLETE | MA can pass static schema checks while live
  grounding zeros every evidence row when body quotes are paired with generic
  metadata claims and context sentences are invented. Separate discovery from
  staged fetch from evidence assembly; force context quote banks first; require
  local/live substring proofs, >=12-word body quotes inside Gutenberg START/END
  markers, and claim/quote token overlap in every research and validator seat;
  keep the orchestrator dispatch-only; split plan vs audit ownership.

- 2026-09-08 | pre-run decomposition audit / UNDECLARED CHILD FAN-OUT BREAKS
  ESTIMATED-AGENT CONSISTENCY | A compact manager plan can describe dozens of
  child workers while declaring only the managers, making `dag_width` plausible
  but leaving `estimated_sub_agents` irreconcilable with the YAML node count.
  Declare every planned worker as a sub-task, keep its unit scope disjoint, and
  compute width, depth, and estimated agents directly from the resulting DAG.

- 2026-09-08 | verifier regression / WINDOWS TEMP PATHS REQUIRE CANONICAL
  COMPARISON | A Harbor-staging regression loaded every trusted fallback but
  failed because one `Path` was resolved and the expected temporary path was
  compared lexically. Resolve both sides before asserting trusted-root identity;
  report the physical resolved path in missing-input errors.

- 2026-09-08 | rubric self-audit / INTERNAL CONSISTENCY IS NOT A CONTENT CHECK
  BY ITSELF | Distinct prose, cross-file equality, recomputed self-reported
  metrics, and visible IDs can all be fabricated coherently. When such checks
  occupy a content bucket, bind each credited unit to a case-local quotation
  and immutable public-source round trip, then reserve semantic judges for
  causal adequacy, clustering, intervention quality, and prose claims.

- 2026-09-08 | QG / HIDDEN NUMERIC GATES AND SHAPE-ONLY LEDGERS FAIL QD-03/10 |
  An undeclared SVG byte floor is a hidden spec; unique-ID CSV headers and
  schema mills (placeholder identity, empty causes, letterhead quotes, all
  wave-1 NONE predecessors, ID-stuffed briefs) pass if content checks never
  bind catalog dates/URLs, source-text identity, nonempty cells, clustered
  campaigns, occupied waves, or coordinate heatmaps. Disclose every graded
  product constraint in instruction/rules, make the manifest describe the
  actual function, and do not treat an empty execution_logs tree as a
  shippable fairness/gap proof (QD-07.10 hard-stops without orchestrator
  sessions).

- 2026-09-08 | live verifier / NESTED JSON RECOVERY SELECTED AN ITEM INSTEAD
  OF ITS ENVELOPE | Scanning from every `{` and returning the last decodable
  dictionary selects the final nested rubric item from `{"items":[...]}`.
  Recover the last schema-bearing outer object, validate its complete ID set,
  and regression-test fenced responses with nested item dictionaries before a
  paid run.

- 2026-09-09 | adversarial fixture / EVIDENCE BINDING MUST FIRST PROVE THE
  EVIDENCE IS REAL | A shape-complete hollow submission earned action-binding
  and claim-traceability credit by making generic actions overlap invented
  quote text and by listing portfolio IDs without any   claim records. Require
  exact immutable-source grounding before action credit, score every required
  claim slot explicitly, and keep a schema-rich hollow fixture below the weak
  score band before authorizing live runs.

- 2026-09-09 | draft QG / HIDDEN DIVERSITY + SILENT CHECK ZEROS + WEAK SUSTAIN + UNGROUNDED JUDGE EVIDENCE | Draft REJECT for undisclosed roster diversity thresholds, instruction prohibitions with no verifier assertion, run_bucket exceptions still reported as all-checks-completed, sustain overlap at one keyword, and judge evidence accepted without source overlap. Disclose every graded diversity floor in instruction/rules and match the manifest to code; enforce already-exists/invention/citation prohibitions; escalate check exceptions into INFRA/status warnings; require >=2 term overlap for all action types; code-side ground judge evidence against trusted excerpts. Empty execution_logs remain a hard ship-blocker and must never be fabricated.

- 2026-09-09 | frozen-source verifier / NORMALIZE BOTH SIDES BEFORE LOCATING
  QUOTES OR PAGES | PDF text extracts may contain compatibility glyphs and
  U+0002 page-break artifacts. Normalizing only submitted quotes causes valid
  source spans to fail or shifts recommendation boundaries against the raw
  string. Use one canonical representation for source searching, cue location,
  and page-marker lookup, and regression-test at least one extract carrying
  each artifact.

- 2026-09-09 | MA trajectory audit / LOGICAL MANAGER LABELS DO NOT GUARANTEE
  A NESTED SPAWN TREE | A decomposition can name managers yet realize a flat
  root fan-out when managers only write briefs and leaf ownership is implicit;
  general reducers may also add undeclared children. Declare exclusive parent
  ownership in both manager and leaf descriptions, give each manager its exact
  child IDs and sequencing contract, prohibit delegation in direct-execution
  stages, and audit raw session `parent_id` links plus declared-versus-observed
  task counts before accepting the run.

- 2026-09-09 | final QG / ESTIMATED_SUB_AGENTS MUST EQUAL DECOMP COUNT NOT
  REALIZED SESSIONS | Setting estimated_sub_agents to observed spawn count
  (including nested helpers) fails when decomposition.yaml has fewer top-level
  sub_tasks. Keep estimated_sub_agents == len(sub_tasks); put realized width/
  depth in dag_width/dag_depth/why_multi_agent after the run; soften the
  directive to allow nested helpers under a declared manager without inventing
  new top-level IDs.

- 2026-09-09 | final QG / RH KEYWORD OVERLAP AND EIGHT-WORD SPLICE ARE GAMEABLE
  | Bare token-overlap action binding and bare eight-word quote presence in
  wrapper prose can pass identical filler actions and dangling quote splices.
  Require stricter term overlap, ban cross-alert repeated action n-grams /
  known filler clauses, require analytical leftover terms outside the quote
  span, and normalize spelled-out numbers before invention/already-exists
  regexes.

- 2026-09-10 | frozen-source build / HASH THE BYTES AFTER PLATFORM NEWLINE
  TRANSLATION | Hashing an in-memory UTF-8 string before `Path.write_text` on
  Windows made every legitimate frozen text fail its verifier hash because
  on-disk newlines differed. Write the file first, hash `read_bytes()`, copy
  that exact file into verifier inputs, and run a 100% manifest integrity
  regression before packaging.

- 2026-09-10 | local QG / A COMPLETE HIDDEN RELATION GRAPH IS AN ORACLE, NOT
  A PARTIAL CHECK | Deriving a full pairwise answer set from a real public
  tracker still fails self-sufficiency when the derived set is grader-only,
  and source-valid quotes do not prove that they support the claimed edge.
  Retain only a small mixed positive/negative spot oracle, make every rubric
  item Boolean, and bind edge claims and semantic judges to compact immutable
  source context. Also enforce every public word bound and output-root
  prohibition, and keep infrastructure preflight explicit but outside the
  task-quality reward path.

- 2026-09-10 | draft review / ENFORCE PROHIBITIONS AND EVIDENCE PER ROW |
  Natural-language prohibitions such as route-family-only joins, cycle
  reporting, uncertainty explanations, and later-outcome paraphrases need
  explicit deterministic or semantic coverage. Never validate evidence as a
  pooled union across a deliverable: require each row to cite its own relevant
  source and regression-test the generic-boilerplate shortcut directly.

- 2026-09-11 | planned MA / ONE MISSING PACKAGE MUST NOT HALT THE DAG, AND
  MANAGERS MUST NOT PARAPHRASE CHILD PROMPTS | If a reducer or manager
  BLOCKED the whole portfolio because one canonical file was missing, later
  stages never wrote ledgers and the run collapsed. Require PARTIAL CONTINUE:
  COMPLETE when any owned package exists, always emit full-row ledgers with
  fail-closed stubs only for absent IDs, and BLOCKED only at zero coverage.
  Also paste each child's decomposition `description` verbatim (appendix or
  yaml.safe_load by id); a short invented manager prompt drops schema and
  path contracts even when research succeeded.

- 2026-09-11 | planned MA / PATCH KNOWN ASSEMBLY DEFECTS BEFORE THE CLOUD RUN,
  BUT DO NOT CHASE THE HELD-OUT CEILING | If prior runs already failed on
  schema aliases, string packets, blank official URLs, missing board markers,
  NVD 1015, or narrative overwrite, put those contracts in the compact
  decomposition before spending another multi run. Do not rewrite the shared
  instruction, retune the verifier, or chase held-out cells that SA also
  scores 0; those spend a second SA run without opening the gap. Keep YAML
  compact so root/managers can still paste child prompts.

- 2026-09-11 | verifier / CSV BOOLEAN SPELLINGS ARE PARSER, NOT RUBRIC |
  Python/Excel dumps of True/False in a decision CSV are the same flags as
  true/false. Rejecting them as schema-invalid also zeros every later
  `== "true"` content comparison, so the swarm looks like it asserted false
  on every case. Canonicalize only those two tokens (not yes/no/1/0). Role
  labels may match case-insensitively as a lookup key, but empty URLs and
  non-boolean field_located must still fail. Do not loosen stub receipts to
  manufacture a gap.

- 2026-09-11 | verifier / PARSER-ONLY VERIFY-ONLY DID NOT OPEN THE GAP; REVERT |
  A CSV True/False and case-insensitive receipt-role parse did not produce a
  shippable SA/MA pair on cloud verify-only. Restore the verifier to the
  contract that scored the frozen SA and multi_noplan trees rather than
  leaving a drifted parser in place. Fix packaging in decomposition next.

- 2026-09-11 | planned MA / RECEIPT REDUCER MUST COPY CAPTURES, NOT EMIT A STUB FILE |
  If PO1/source spans are high but receipts are 36 identical FETCH_FAILED
  rows with empty URLs and lowercase roles, the research happened and the
  reducer threw it away. Bind the receipt seat to copy handoff URLs and
  7-60 word capture signatures, uppercase CISA/NVD/REMEDIATION, JSON boolean
  field_located, and GATE: do not COMPLETE when all signatures match or all
  URLs are empty. Also bind decision CSV lowercase true/false and PNG tEXt
  keys. Do not loosen the verifier to accept the stub.

- 2026-09-11 | freeze / REGISTER PDF LINKS MAY NEVER SAY DP |
  A GOV.UK register row can point at the only programme PDF with link text
  that never contains "programme" or "dp" (sailaway, disconnection, etc.).
  Classify leftover PDFs as the DP when that role is required and missing,
  instead of shipping an empty documents object.

- 2026-09-11 | verifier / EMPTY-FIXTURE CONTENT CHECKS NEED A ROW COUNT |
  A reward-hacking loop over OSPAR or casefile rows returns True on an
  empty submission. Require the roster-sized row count before scanning
  weights, dates, or labels so a do-nothing fixture stays at zero.

- 2026-09-11 | freeze / OSPAR.ORG DOCUMENT FETCH CAN HANG |
  `ospar.org/documents?v=` may never return under requests. Capture the
  public consolidated Decision text once, record the official URL and
  retrieval date, and freeze that UTF-8 extract for grading. Do not
  fabricate OSPAR definitions.

- 2026-09-11 | local QG / EMPTY execution_logs FAILS QD-07 CHECK 10 |
  An empty `execution_logs/` folder still FAIL QD-07 check 10 (missing
  `raw_trajectory/orchestrator_ses_*.json`). Do not spend a hosted Draft
  Review until single, multi, and multi_noplan Harbor trees are merged in.

- 2026-09-11 | local QG / RUBRIC FILE MUST CONTAIN QD-07 |
  If `Quality_dimensions_phase_2.md` has two `# QD-06:` headers and no
  `# QD-07:`, restore QD-07 from a sibling copy before the local gate.
  Re-sync `LocalQualityGate_ReviewerPrompt_Phase2.md` check counts to the
  live rubric (QD-02=6, QD-03=11, QD-04=13, QD-07=14).

- 2026-09-11 | local QG / DISCLOSE SCORED CLOSED SETS, NEVER HIDE NUMERIC GATES |
  If verify.py scores a 6-word note, a quote word-band, or a close-out
  package subset, state those as task requirements in campaign_rules.md
  and instruction.md. Do not leave Jaccard numbers in the instruction
  (reverse leak); do not leave the requirement unstated (forward gap).

- 2026-09-11 | local QG / CHECK CRASHES ARE INFRASTRUCTURE, NOT CONTENT ZERO |
  A NameError or other unexpected exception inside a registered check must
  write verifier_status.json infrastructure_error. Converting it to score
  0.0 with status completed is a silent fail-closed content zero.

- 2026-09-11 | local QG / DECOMP SCOPE ONLY; NO HELD-OUT ID CLUSTERS |
  Sub-task text may name exclusive ID thirds, not a held-out shared-CA
  sample. Quote word-bands belong in instruction/rules, not only in
  decomposition. Strip quote-repair, legal-screen, and sequencing how-to.

- 2026-09-11 | local QG / QUOTE ROUND-TRIP NEEDS ABOUTNESS |
  Substring membership of any distinctive PDF span is not a commitment
  quote. Require held-out posture tokens that are real extract substrings,
  reject letterhead/location-only quotes, and require CA quote_ok whenever
  a CA exists.

- 2026-09-11 | local QG / HLP IS DELIVERABLES ONLY |
  high_level_prompt.md fails if it tells the agent to fetch sources or
  consult a rulebook. Restate the eight files and constraints; keep
  process in instruction.md.

- 2026-09-11 | local QG / BIND EVIDENCE TO THE PROGRAMME, NOT THE INSTRUMENT PREAMBLE |
  An OSPAR Decision URL named in the instruction is a lazy evidence_source
  if quote_ok accepts any span containing "installation". Bind
  evidence_source to that row's own DP/CA/close-out official_url; allow
  the Decision URL only for a unique definitional quote. Match
  committed_solution_class to quote tokens, require exact shared-URL ID
  sets, reject unknown where the frozen extract states a weight or
  placement year, drop a bare "install" date trigger, and match host
  oracle edges in the declared satellite-to-host direction only.
  Unenforced "quote the disagreement" sentences should be deleted rather
  than left as fake prohibitions. LLM per_id shards of 10–11 IDs fail
  full-coverage; require every rostered ID in each judge theme.

- 2026-09-11 | draft QG / AHT MUST MATCH THE 200K+ TOKEN BAND |
  input_token_estimate above 200K requires human_solving_hours_estimate in
  the 80-200h band. Count frozen-source words, convert honestly, and make
  the justification add to that total. A 54h AHT on a ~1.6M-word corpus
  fails QD-01.18 even when the rest of the instruction is clean.

- 2026-09-11 | draft QG / OPTIONS TABLES ARE NOT CLASS COMMITMENTS |
  Substring class matching still passes if an options list names both
  full removal and leave in situ. Require the quote to hit the declared
  class and no other exclusive class family. Pair that with a numeric
  Annex-1 weight check, token-proximity false-consent detection that still
  allows "not in hand", and phrase-level host regexes instead of lone
  words such as export.

- 2026-09-15 | verifier / HARBOR DROPS LOGS UNDER /logs/agent AND BOOLEAN 32/32 WIPES A NEAR-COMPLETE PACK |
  Harbor may write trajectory.json, opencode.txt, and raw_trajectory/ beside
  agent deliverables; extra-file checks must ignore those names. Exact
  frozen-extract quotes fail live pdftotext punctuation; grade alphanumeric
  token spans while keeping URL binding and the word band. "Not yet in hand"
  is the same draft-consent fact as "not in hand". A 32/32 Boolean wipe on
  one overlong summary or one comma-separated order line invents a zero;
  score unit means so a near-complete multi pack can still clear 0.7.

- 2026-09-15 | SA / A FETCH LOOP PLUS KEYWORD QUOTES IS A SCRIPTABLE BACKBONE |
  A single agent that writes generate_pack.py over the roster, slices
  18-120 word windows around "full removal" / "leave in situ", copies
  register_status, and templates 50-word summaries will bank schema,
  host-regex, and fluent-judge credit. Downloading PDFs is allowed;
  emitting the graded pack from a for-loop is not. Grade committed
  solution aboutness, exclusive-class quotes, exact shared-index schema,
  and OSPAR evidence that is not letterhead/TOC. Do not let unit-mean
  judges pass contents-list spans. Host edges need more than a tie-back
  regex if that regex is the whole oracle.

- 2026-09-15 | verifier / UNIT-MEAN JUDGES WILL PASS TOC QUOTES UNLESS THE DETERMINISTIC BOARD FAILS THEM |
  Schema-valid 18-120 word contents-list or document-control spans can
  round-trip into frozen extracts and bank static plus fluent-judge credit.
  Reject dotted leaders, document-control sheets, options tables, and host
  snips under the 18-word band in the quote checks, and overlay those fails
  onto per_id so a fluent judge cannot wash them out.

- 2026-09-15 | verifier / ALL-OUT-OF-SCOPE BOARDS BANK DECOY RECALL UNLESS ANCHORS BIND |
  A format-only ledger that tags every row not_in_scope correctly classifies
  every held-out decoy and can clear 0.35+ before substance. Multiply decoy
  recall by recall on a few must-include in-scope anchors, and multiply
  in-scope recall by out-of-scope recall inside the scope oracle, so skipping
  the roster or tagging the majority class cannot bank the anti-gaming bucket.

- 2026-09-15 | packaging / HARBOR MULTI ZIPS CAN OMIT OPENCODE.TXT AND TRAJECTORY.JSON |
  S-02 requires those two names under each trial `agent/` and exactly one
  `tests/*.py` named `verify.py`. A finished mascloud zip may keep
  `opencode-internal.log` plus `raw_trajectory/` and still omit the tee file
  and ATIF write. Recover `opencode.txt` / ATIF-v1.6 `trajectory.json` from
  the orchestrator session export using Harbor's event mapping; do not invent
  a narrative. Keep trainer regression scripts out of delivered `tests/`.

- 2026-09-15 | local QG / QUOTE SKIP-EMPTY, ANY-TOKEN DRIFT, AND PNG-ONLY CHARTS ARE HIGH EXPLOITS |
  A content quote check that `continue`s blank cells, a mismatch check that
  accepts any closed drift token, and chart scoring that only tests PNG
  magic will FAIL QD-04/10 even with a real corpus. Score every roster row
  in the quote denominator, reject the first-N HTML-token prefix, require
  Item-local needles, grade each followup against held-out gold not set
  membership, and join chart sidecar counts to the ledger. HLP must stay
  deliverable-only. Empty `execution_logs/` cannot close QD-05/07/08/09;
  do not fabricate Harbor trees to pass those checks.

- 2026-09-15 | local QG / HEADING HARVEST, SELF-JOIN CHARTS, WORD FLOORS, AND K<1 PRODUCTS RE-FAIL THE PACKAGE |
  A 12-word Item heading, a CSV that echoes the agent's own heatmap, a 1x1 PNG, and 220/400-word padding will CONFIRM QD-10 HIGH exploits. Require the quote text itself to contain the conclusion phrase (or 4.01/Exhibit 16/2.02 for OOS), freeze chart gold from held-out scope/probes, parse PNG IHDR size, and score notes by held-out decoy accessions not word count. Intra-group `depends_on` fails QD-06.8 — put sequential clerks in distinct `parallel_group`s. Manifest probe IDs must include every collapse/issue branch the code claims to run. Judge memos in the PO bucket must receive filing excerpts in the system role. Use additive unit means only; uniqueness/anchor/overlay factors averaged, never multiplied by K<1. Empty logs still cannot close QD-07.10 / QD-08.24 / QD-09.

- 2026-09-16 | rubric / PER-CVE MEANS LET ONE BULK CSAF FILE DOMINATE |
  Averaging content checks across every CVE lets a 300+ third-party-component dump set ~80% of PO/RH even when the other advisories are unread. Average per advisory, keep mechanical completeness of bulk files on a separate register, and require distinctive-subset prose only. Shared document-level ICS recommended-practice notes are not evidence. Product-tree vendor/product joins are real concordance work when CVE IDs do not collide.

