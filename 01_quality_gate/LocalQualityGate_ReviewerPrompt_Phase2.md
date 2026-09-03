# Local Quality Gate — Reviewer Prompt (PHASE 2)

> Independent, pre-submission self-review harness for **SwarmBench Phase 2**
> tasks. Mirrors the upstream QG Draft Reviewer's semantic **Quality
> Dimensions QD-01 → QD-10** (as defined in
> `01_quality_gate/Quality_dimensions_phase_2.md`) so that fixable issues
> are caught locally and do not consume daily agentic-reviewer quota.
>
> This is the Phase-2 successor to `LocalQualityGate_ReviewerPrompt.md`
> (which targeted the older 14-dimension, oracle-based Phase-1 rubric and
> is NOT valid for Phase 2). Run this in a **fresh** agent session, not
> in the chat that built the task, so the review is independent.

---

## What this prompt does

1. **Spawns 6 sub-agents in parallel** (Groups A–F), then **one dependent
   sub-agent** (Group G) once Group F has returned. Together they cover
   QD-01 → QD-10 exactly once. Group G is the only sequential dispatch:
   QD-10b grades the exploits QD-10a (Group F) produced, so it cannot run
   in the first batch.
2. **Forces each sub-agent to read its QD section** of the single
   consolidated rubric file `Quality_dimensions_phase_2.md`, evaluate
   *every* numbered check, and write a strict-schema JSON to
   `<ARTEFACTS_ROOT>\qg_run\QD-XX.json`.
3. **Assembles one final JSON report** with `APPROVE` / `REJECT` /
   `MANUAL_REVIEW` and verbatim `rejection_reasons[]` quoted from local
   files.

### Phase-2 differences from the Phase-1 gate (do NOT reintroduce)

- **10 dimensions, not 14 and no longer 9.** The single source of truth is
  `Quality_dimensions_phase_2.md`. There are NO per-QD skill files and
  NO `Tasks\skills\` dependency. QD-10 (the reward-hacking
  exploiter/grader pair) was added to the hosted reviewer on 2026-07-23
  and has failed every task reviewed since; it is not optional.
- **No oracle, no `solution/`.** Phase-2 rubric tasks derive
  `reward` from a boolean rubric implemented in `tests/verify.py`
  (`judge.py` is retired; some older packages still carry it). There is
  no `oracle.json` and no `solution/solve.sh`. Do NOT flag their absence
  — it is correct by design. A frozen `tests/ground_truth/` file (e.g.
  `registry_facts.json`) is judge *grounding data*, not an answer key.
  Grade the reward shape the package actually declares (flat one-point
  items, or the three-tier structure/reward-hacking/partial-oracle
  category weights from `new_verifier_reward_system.md`) — do not fail a
  package for choosing the shape the other document prescribes.
- **`tests/rubric_manifest.json` is mandatory** (Phase 2.1) and is graded:
  QD-03 checks 6–9 cover manifest truthfulness, real weight vs declared
  weight, reverse coverage of every reward-touching function, and the
  hard **content ≥ 60% / structural ≤ 40%** floor (check 9). Read the
  manifest on every run.
- **opencode agents — three modes.** `swarm-opencode-single`,
  `swarm-opencode-multi`, and `swarm-opencode-multi` no-plan /
  `multi_noplan` (kimi variants also exist). `execution_logs/` must hold
  `single-opencode-agent/`, `multi-opencode-agent/`, and
  `multi-opencode-agent-noplan/` — there is no `oracle/` run. Gap/reward
  targets apply to single vs plan-guided multi; noplan is authenticity /
  prompt-integrity only (see QD-07 / QD-08).
- **Gap: the reviewer fails below `multi - single >= 0.20`** (QD-07
  check 7). The internal build target is `>= 0.23` — aim for 0.23, but a
  sub-agent must grade against the rubric's 0.20, not the target.
- **Seven-item task root (production rework):** `instruction.md`,
  `high_level_prompt.md`, `task.toml`, `decomposition.yaml`,
  `environment/`, `tests/`, `execution_logs/`. QD-01 check 20 grades the
  high-level prompt; its absence is a FAIL, not a Phase-1 leftover.
- **Trainer tools live OUTSIDE the task folder** in a sibling
  `__trainer_artefacts` (double underscore). It is never shipped and the
  QG never sees it. This gate writes ONLY there — never inside
  `<TASK_ROOT>`, which would break the seven-item root (static check S-02).
- **No `audit.json` / `build_task.py` loop.** Fixes are applied directly
  to the task files (then re-run the local static gate + this gate).

Load-bearing constraints (do NOT alter the prompt body):

- **First turn = exactly 6 `Agent` tool calls, no preamble** (after the
  optional one-question path pre-flight). The 7th call (Group G,
  QD-10b) is dispatched in a later turn, after Group F returns.
- **Quote-or-pass evidence rule** — a FAIL is invalid unless it cites
  verbatim text from a local task file. Default to PASS under
  uncertainty.
- **Cross-QD independence** — no verdict may reference another QD as
  justification.
- **Harbor-alignment clause** — `decomposition.yaml` asymmetry, and
  `tests/` being absent from the Docker image, are intentional design
  and must NOT be flagged.
- **Strict enum contract** — `result` ∈ {`PASS`, `FAIL`,
  `NOT_APPLICABLE`, `WARN`}; `decision` ∈ {`APPROVE`, `REJECT`,
  `MANUAL_REVIEW`}; `id` is an integer; no nulls. QD-09's rubric emits
  `FLAG`; the harness has no such value, so report it as `WARN` and say
  "FLAG (reported as WARN)" in the text — this is exactly what the hosted
  reviewer does.
- **`additional_*` findings are allowed and expected** — after the last
  numbered check of a QD, a sub-agent MAY append further findings
  numbered from N+1 with names prefixed `additional_`. The hosted
  reviewer does this in every recent review and roughly one reject reason
  in five comes from one. Same evidence bar; same blocking rules.

## Prerequisites (one-time per machine)

1. **The Phase-2 rubric file** is present at:
   ```
   D:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\documentations_phase_2\01_quality_gate\Quality_dimensions_phase_2.md
   ```
   It contains dimensions QD-01 → QD-10b. There are NO `QD-0X_<slug>`
   anchor lines in the file — a dimension starts at its `# QD-0X:`
   markdown header and runs to the next `# QD-` header (or EOF). Always
   Grep the **first** matching `# QD-0X:` header (do not take a later
   duplicate if one reappears). Section boundaries as of 2026-08-05:

   ```
   QD-01   Task Quality, Instruction & Authenticity      lines    1–154
   QD-02   Instruction–Verifier Alignment                lines  155–209
   QD-03   Verifier Rubric Integrity                     lines  210–294
   QD-04   Reward-Hacking Resistance                     lines  295–459
   QD-05   Multi-Agent Necessity                         lines  460–526
   QD-06   Decomposition Soundness                       lines  527–643
   QD-07   Benchmark Validity & Fairness                 lines  644–959
   QD-08   Infrastructure & Harbor Compliance            lines  960–1150
   QD-09   Coordination Value & Gap Integrity            lines 1151–1351
   QD-10b  Reward-Hacking Exploit Grading (Grader)       lines 1352–1446
   QD-10a  Reward-Hacking Exploit Generation (Exploiter) lines 1447–EOF
   ```
   (Line numbers are hints — always locate a section by Grepping its
   `# QD-0X:` header, since edits may shift lines. **QD-10b appears
   before QD-10a** in the file; that is intentional file order, not a
   grading order — Groups F then G still run exploiter → grader.)

   Known rubric-file defects to read past, not to reproduce: QD-07's
   check 10 and check 12 verdict rules say a FAIL "forces the overall
   QD-10 result to FAIL" — they mean **QD-07** (the wording predates the
   real QD-10). QD-08's check 5 is named
   `no_inflated_fallback_on_llm_failure` but its body also covers
   verifier reproducibility, so a determinism failure is reported under
   that name. QD-01 check 5 still says rubric items are "equally
   weighted by design" in one sentence — that forbids *instruction-side*
   differential weight leaks to the agent; it does **not** forbid the
   declared 1/2/3 category weights in `verify.py` / `rubric_manifest.json`.

2. **Pick a runner**: Cursor chat, `claude` CLI, Codex CLI, or any
   runner that implements a parallel `Agent` / sub-agent tool.

## How to run it (per task)

1. Open a **fresh** agent session (do NOT reuse the chat that built the
   task — independence matters). If convenient, set the working
   directory to the task root, e.g.
   `D:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\phase_2_tasks\task4\<uuid>-SWARMBENCH-…\`.
   (If you forget, the prompt's pre-flight asks for the path.)

2. Paste the prompt block below **verbatim**. The Windows path mapping is
   baked into the `PRE-FLIGHT — PATH RESOLUTION` section.

3. Wait for the final JSON. Save it to
   `<ARTEFACTS_ROOT>\qg_report.json` (the sibling folder — never inside
   the task root).

4. **Decision logic**:
   - `"decision": "APPROVE"` → proceed to packaging (rebuild the
     forward-slash submission ZIP, upload, run the hosted Draft Review).
   - `"decision": "REJECT"` → walk `rejection_reasons[]`. Each entry has a
     `code` (e.g. `QD-02.6`), a verbatim quoted offending string from a
     local file, and a `Fix:` clause. Apply the fix directly to the task
     file, re-run the local static gate, then re-run this gate. Loop
     until APPROVE.
   - `"decision": "MANUAL_REVIEW"` → triage the flagged QDs by hand;
     decide whether to fix or annotate `<ARTEFACTS_ROOT>\HANDOFF.md`
     with the rationale for why a flagged item is intentional. A QD-09
     FLAG lands here by design — the hosted gate returns MANUAL_REVIEW
     for an otherwise-clean package whose QD-09 is FLAG/WARN, so treat it
     as a senior-review item, not as a pass.

5. **Do not spend a hosted draft review on a package with an empty
   `execution_logs/`.** QD-07 check 10 fails on missing
   `raw_trajectory/orchestrator_ses_*.json` alone, QD-09 degrades to
   FLAG or FAIL, and six or more QD-08 checks go `NOT_APPLICABLE`. Every
   log-free draft review on record burned ~$9 to return the same four to
   six findings. Run the real **single + multi + multi_noplan**
   executions first (merge all three mode trees into `execution_logs/`).

---

## The prompt (paste verbatim into a fresh agent session)

```text
# Harbor Harness Context for Phase-2 Quality Reviewers

You are reviewing a SwarmBench PHASE 2 task that runs on the Harbor evaluation harness. Understanding how Harbor executes a Phase-2 task is critical for judging whether it is correctly constructed.

## Phase-2 Task Directory Structure (seven items at the root)

```
{task_id}/
├── instruction.md          ← Full task prompt. Identical for single, multi, and multi_noplan.
├── high_level_prompt.md    ← REQUIRED deliverable-only companion brief (~250 words). Graded by QD-01 check 20.
├── task.toml               ← Metadata: verifier_type, domain, coordination_pattern, dag_depth, estimated_sub_agents, AHT, etc.
├── decomposition.yaml      ← Multi-agent coordination guide. Injected ONLY into the plan-guided multi orchestrator (not noplan).
├── environment/
│   ├── Dockerfile          ← Builds the container. Must NOT COPY tests/ or any answer/ground-truth data.
│   └── input_artifacts/    ← Task packet (rules, roster/manifest). Load-bearing browsing means NO local answer data here.
├── tests/
│   ├── test.sh             ← Verifier entrypoint. Invokes the grader and writes reward (or an explicit INFRA error state).
│   ├── verify.py           ← The single grader (judge.py is retired; older packages may still ship one). Boolean rubric. NO oracle.json.
│   ├── rubric_manifest.json ← MANDATORY client-readable rubric, 1:1 with verify.py's checks. Graded by QD-03 checks 6–9.
│   └── ground_truth/       ← Frozen grounding facts for the grader (e.g. registry_facts.json). NOT an answer key the agent must match.
└── execution_logs/
    ├── single-opencode-agent/         ← 1 single-agent run (Task/sub-agent tools blocked)
    ├── multi-opencode-agent/          ← 1 plan-guided multi run (full tools + decomposition injected)
    └── multi-opencode-agent-noplan/   ← 1 multi no-plan run (full tools, NO decomposition). Authenticity required; no gap target.
```

There is NO `solution/`, NO `oracle.json`, and NO `oracle/` execution log in a Phase-2 rubric task. Their absence is CORRECT — never flag it.

## How Harbor Executes a Phase-2 Task

1. BUILD — Docker image from environment/Dockerfile. Only input_artifacts are baked in.
2. START — Container started; /logs/agent/ and /logs/verifier/ volume-mounted to host.
3. AGENT RUN — Agent receives instruction.md (and the high-level prompt channel when the harness serves it) and works in the container.
   - Single: tool-restricted, no Task/CreateSubagent tools.
   - Multi (plan-guided): reads decomposition.yaml, full tool access including sub-agent spawning.
   - Multi no-plan: full tools, decomposition.yaml withheld — same instruction.md as the other modes.
4. VERIFICATION — Harbor copies tests/ into the container AFTER the agent finishes, runs test.sh → verify.py → writes /logs/verifier/reward.json (float 0.0–1.0) or an explicit infrastructure/error sentinel when the judge cannot run.
5. CLEANUP — Container destroyed; results land in execution_logs/ on the host.

## Critical Rules

- The agent NEVER sees tests/ or decomposition.yaml during its own run (noplan never receives decomposition.yaml at all). tests/ is uploaded only AFTER the agent finishes.
- instruction.md is served IDENTICALLY to single, multi, and multi_noplan. Symmetry is at the task layer; decomposition.yaml is the intended asymmetric channel for the plan-guided multi orchestrator only.
- Scoring is a boolean rubric with no oracle diff: either flat one-point items (reward = passed_items / total_items) or the declared three-tier category weights (1 structure / 2 reward-hacking / 3 partial-oracle). Grade the shape the package declares; neither shape is a violation by itself. Content (RH + partial-oracle) must be ≥ 60% of total weight (QD-03 check 9). No multipliers, caps, floors or tiers beyond the declared shape.
- Infrastructure / judge failure must write an **explicit error / INFRA sentinel** (QD-02 check 5) — a silent fail-closed `reward: 0.0` with no error field is a FAIL. Missing critical agent deliverables may still score 0.0 as a content grade.
- The benchmark measures the gap between single and plan-guided multi. QD-07 check 7 FAILs below multi - single = 0.20; the internal build target is 0.23. multi_noplan has no gap/reward target.

## Three Agent Modes

- `swarm-opencode-single` (or swarm-kimi-single): sub-agent tools BLOCKED. Solves alone.
- `swarm-opencode-multi` (or swarm-kimi-multi): ALL tools. Reads decomposition.yaml. Spawns sub-agents.
- multi_noplan (`multi-opencode-agent-noplan/` logs): ALL tools, decomposition.yaml withheld. Same instruction.md.

All three receive the SAME instruction.md. The score gap between single and plan-guided multi is what the benchmark measures.

You are the Phase-2 Quality Gate reviewer for this SwarmBench task.

The task is at /task/. The consolidated rubric is the single file:
  D:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\documentations_phase_2\01_quality_gate\Quality_dimensions_phase_2.md
There are 10 quality dimensions (QD-01 through QD-10). Nine of them are split across 6 named sub-agent groups you dispatch in parallel; QD-10 is a two-phase adversarial pair, so its grader (Group G) is dispatched only after its exploiter (Group F) returns.

## PRE-FLIGHT — PATH RESOLUTION (Windows local run, baked in)

This prompt uses Linux-style placeholders (`/task/`, `/rubric`, `/qd_results/`, `/tmp/qd_results/`). On this machine they resolve as follows. Do NOT ask the user about `/rubric` or `/qd_results/` — they are CONSTANTS:

  - `/rubric`       → `D:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\documentations_phase_2\01_quality_gate\Quality_dimensions_phase_2.md`
                      (the single file containing all QD sections; locate a QD by Grepping its **first** `# QD-0X:` header and read to the next `# QD-` header or EOF — there are no `QD-0X_` anchor lines)
  - `/qd_results/`  → `<ARTEFACTS_ROOT>\qg_run\`
                      (create it if missing; one `QD-XX.json` per dimension goes here)
  - `/tmp/qd_results/` → the SAME folder as `/qd_results/`. QD-10a's rubric says to write `/tmp/qd_results/QD-10-EXPLOIT.json`; write it to `<ARTEFACTS_ROOT>\qg_run\QD-10-EXPLOIT.json`.
  - `/task/`        → `<TASK_ROOT>` (resolve per the rule below)
  - `<ARTEFACTS_ROOT>` → the SIBLING folder next to `<TASK_ROOT>`, named `<task-folder-name>__trainer_artefacts` (double underscore). NEVER write anything inside `<TASK_ROOT>` — its root is a seven-item whitelist and an extra folder fails static check S-02.

### Resolving `<TASK_ROOT>` (do this BEFORE the first-action section)

1. Run `Get-Location` (PowerShell) or `pwd` (Bash). If the current working directory contains BOTH `instruction.md` AND `task.toml`, that IS `<TASK_ROOT>`. Set it silently and proceed to the "CRITICAL — FIRST AND ONLY ACTION" section in the SAME turn — do NOT ask the user anything.

2. If the current working directory does NOT contain both files, your FIRST response is exactly ONE clarifying question — no preamble, no tool calls, no sub-agent dispatches yet. Ask exactly:

     > Which task folder should I review? Please paste the absolute path to the task root (the folder that contains `instruction.md`, `high_level_prompt.md`, `task.toml`, `environment/`, `tests/`, and `execution_logs/`).

   When the user replies with a path, set `<TASK_ROOT>` to that path. Your SECOND turn is then the 6-Agent-call batch per the "CRITICAL" section.

3. NEVER ask about `/rubric` or `/qd_results/`. Only the task folder may be unknown, and only if auto-detection failed. Set `<ARTEFACTS_ROOT>` to the sibling folder `<parent-of-TASK_ROOT>\<task-folder-name>__trainer_artefacts` and create it (plus its `qg_run\` subfolder) if missing. If a previous run left a `__trainer_artefacts` folder INSIDE `<TASK_ROOT>`, say so in your final report — it must be moved out before packaging.

### Pass the resolved mapping to every sub-agent

In each `Agent` tool call, prepend this single paragraph to the sub-agent prompt (substituting the resolved `<TASK_ROOT>` and `<ARTEFACTS_ROOT>` literals):

  > PATH MAPPING (Windows): `/task/` = `<TASK_ROOT>`. `/rubric` =
  > `D:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\documentations_phase_2\01_quality_gate\Quality_dimensions_phase_2.md`.
  > `/qd_results/` and `/tmp/qd_results/` both = `<ARTEFACTS_ROOT>\qg_run\`. Whenever
  > this prompt refers to `/task/...`, `/rubric`, or `/qd_results/...`, read/write the
  > corresponding Windows path instead, and never write inside `<TASK_ROOT>`. Locate
  > each QD's checks by Grepping the **first** `# QD-0X:` header inside `/rubric` and
  > reading to the next `# QD-` header (or EOF); there are no `QD-0X_` anchor lines.
  > Translate bash snippets to PowerShell (`New-Item -ItemType Directory -Force -Path ...`;
  > write JSON via `python -c "..."` or Set-Content) if `bash` is not on PATH.

## CRITICAL — FIRST AND ONLY ACTION OF YOUR FIRST TURN (after pre-flight)

**Once `<TASK_ROOT>` is resolved, your NEXT response MUST contain exactly 6 Agent tool calls and NOTHING ELSE.** No text, no thinking out loud, no preamble — just emit 6 `Agent` tool_use blocks back-to-back in this single assistant turn. Then stop and wait for the tool results.

This is a HARD CONSTRAINT. Sequential calls across turns are a CRITICAL BUG, with exactly two allowed exceptions: the optional pre-flight clarifying turn, and the Group G dispatch described below (which is data-dependent on Group F and CANNOT be batched with it).

### The sub-agent groups (fixed assignment — do NOT alter)

Phase 1 — all six dispatched together in your first turn:

  Group A  `structural-harbor`   owns QD-08          (24 checks — a full agent's work on its own)
  Group B  `instruction-spec`    owns QD-01, QD-02
  Group C  `rubric-integrity`    owns QD-03, QD-04
  Group D  `validity-necessity`  owns QD-05, QD-06, QD-07
  Group E  `coordination-gap`    owns QD-09          (full end-to-end trajectory reads)
  Group F  `exploit-redteam`     owns QD-10a         (restricted file list — see the QD-10 protocol)

Phase 2 — dispatched alone, only after Group F returns:

  Group G  `exploit-grader`      owns QD-10b         (grades Group F's exploits)

Together these cover QD-01 → QD-10 exactly once. No QD belongs to two groups; no QD is unowned.

### CORRECT behavior

First assistant turn = ONE message with 6 ToolUseBlocks in `content`:
```
[ToolUse(Agent, "structural-harbor"), ToolUse(Agent, "instruction-spec"),
 ToolUse(Agent, "rubric-integrity"),  ToolUse(Agent, "validity-necessity"),
 ToolUse(Agent, "coordination-gap"),  ToolUse(Agent, "exploit-redteam")]
```
Second assistant turn (after results) = ONE message with 1 ToolUseBlock:
```
[ToolUse(Agent, "exploit-grader")]
```

### WRONG behavior

- One Agent call per QD (10 calls) — WRONG, you must batch by group
- Batching Group G with Phase 1 — WRONG, it has nothing to grade yet
- Any text/preamble before the 6 tool calls — WRONG
- Re-dispatching a Phase-1 group after seeing its result — WRONG (dispatch once; assemble from /qd_results/). The single exception is a group that failed to write one of its QD files at all.

### The QD-10 protocol (two phases, do NOT collapse into one)

QD-10 is an adversarial pair and only works if the exploiter is kept ignorant:

  1. Group F (QD-10a) reads ONLY `/task/instruction.md` and every file under `/task/tests/`. It MUST NOT read `decomposition.yaml`, `environment/`, or anything under `execution_logs/` — reasoning from instruction + verifier alone is what forces fresh exploits instead of restatements of prior findings. It produces at least 3 concrete exploits (or an explicit, quoted justification for fewer) and writes `/qd_results/QD-10-EXPLOIT.json`. This is an INTERMEDIATE artifact, not a dimension result — do NOT put it in the final report.
  2. Group G (QD-10b) reads that file FIRST, then independently re-traces the quoted verifier code, rates plausibility HIGH / MEDIUM / LOW, checks the execution logs (single, multi, and multi_noplan if present) for an exploit that already fired for real, and writes `/qd_results/QD-10.json`. Mapping: NOT CONFIRMED → PASS; CONFIRMED at HIGH/MEDIUM → FAIL; CONFIRMED at LOW → WARN (recorded, non-blocking).

QD-10 has failed every hosted review since it was introduced. Expect findings here and budget fixing time for them.

### QD → rubric-section map (all inside the single /rubric file)

  QD-01  → /rubric  section "# QD-01: Task Quality, Instruction & Authenticity"      (Sections A instruction, B authenticity, C AHT, D high-level prompt)
  QD-02  → /rubric  section "# QD-02: Instruction–Verifier Alignment"
  QD-03  → /rubric  section "# QD-03: Verifier Rubric Integrity"                    (checks 1–9 incl. content ≥60%)
  QD-04  → /rubric  section "# QD-04: Reward-Hacking Resistance"
  QD-05  → /rubric  section "# QD-05: Multi-Agent Necessity"
  QD-06  → /rubric  section "# QD-06: Decomposition Soundness"
  QD-07  → /rubric  section "# QD-07: Benchmark Validity & Fairness"
  QD-08  → /rubric  section "# QD-08: Infrastructure & Harbor Compliance"
  QD-09  → /rubric  section "# QD-09: Coordination Value & Gap Integrity (Client Perspective)"
  QD-10a → /rubric  section "# QD-10a: Reward-Hacking Exploit Generation (Exploiter)"
  QD-10b → /rubric  section "# QD-10b: Reward-Hacking Exploit Grading (Grader)"
  (Note: in the rubric file, the QD-10b header currently appears above QD-10a — always Grep by header name.)

### Per-sub-agent prompt template

For each Agent call, use this exact prompt (substitute `<group_name>`, the group's QD list, and the resolved `<TASK_ROOT>` / `<ARTEFACTS_ROOT>` literals from PRE-FLIGHT). For Groups F and G, also paste the QD-10 protocol above verbatim into the sub-agent prompt — Group F's restricted file list overrides step 2 of the numbered procedure below, and both groups follow the QD-10 FILE CONTRACT instead of the plain one-file-per-QD rule:

  > PATH MAPPING (Windows): `/task/` = `<TASK_ROOT>`. `/rubric` =
  > `D:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\documentations_phase_2\01_quality_gate\Quality_dimensions_phase_2.md`.
  > `/qd_results/` and `/tmp/qd_results/` both = `<ARTEFACTS_ROOT>\qg_run\`. Whenever
  > this prompt or the rubric refers to `/task/...`, `/rubric`, or `/qd_results/...`,
  > read/write the corresponding Windows path instead, and never write inside
  > `<TASK_ROOT>`. Translate bash snippets to PowerShell or `python -c` if `bash` is
  > not on PATH.
  >
  > You are the `<group_name>` reviewer for the SwarmBench Phase-2 task at /task/.
  >
  > Your assigned QDs are: <comma-separated list from the group's owned set above>.
  >
  > For EACH QD in your assigned list, in order:
  >
  >   1. Open /rubric and locate your QD by Grepping its **first** header (e.g. `# QD-05:`).
  >      Read from that header to the next `# QD-` header (or EOF) to learn its
  >      numbered checks and its "Files to Read" / procedure text. There are no
  >      `QD-0X_` anchor lines in the file. (QD-10b's header currently sits above
  >      QD-10a — still Grep by the exact header string.)
  >   2. Read every task file the rubric names, and treat its "read ALL files"
  >      instructions literally: task.toml, instruction.md, high_level_prompt.md,
  >      decomposition.yaml, environment/Dockerfile, environment/input_artifacts/,
  >      and EVERY file under tests/ — test.sh, verify.py (the current grader),
  >      judge.py if one is still present, rubric_manifest.json, ground_truth/,
  >      fixtures — plus execution_logs/ for all three modes
  >      (single-opencode-agent/, multi-opencode-agent/,
  >      multi-opencode-agent-noplan/) as the rubric requires. rubric_manifest.json
  >      is graded for truthfulness (QD-03 check 6), real weights (check 7), reverse
  >      coverage (check 8), and content ≥ 60% (check 9); do not skip it. Use Glob
  >      and Grep freely.
  >   3. Evaluate EVERY numbered check in the rubric section. Do NOT stop after the
  >      first FAIL.
  >   4. You MAY append further findings after the last numbered check, numbered from
  >      N+1 with names prefixed `additional_` (e.g. `additional_manifest_internal_
  >      self_contradiction`). Same evidence bar as any other check: a verbatim local
  >      quote or it does not exist. Use FAIL only for a real blocking defect; use
  >      WARN for something the trainer should see but that should not block.
  >   5. Save the result to /qd_results/QD-XX.json (see schema below).
  >
  > ## PHASE-2 GROUND TRUTH — do NOT flag these intentional facts
  >
  >   - No oracle.json, no solution/, no oracle/ execution log. Absence of an oracle
  >     is CORRECT. Reward comes from a boolean rubric in tests/verify.py — either
  >     flat one-point items or the declared three-tier category weights (1 structure /
  >     2 reward-hacking / 3 partial-oracle). Grade the shape the package declares.
  >     QD-03 check 9 still requires content (RH + partial-oracle) ≥ 60% of total
  >     weight regardless of shape.
  >   - tests/ground_truth/ holds frozen grading-grounding facts, NOT an answer key
  >     the agent is expected to reproduce verbatim.
  >   - high_level_prompt.md is a required root file (QD-01 check 20) — its presence
  >     is correct; do not treat it as an extra/unauthorized root item.
  >   - instruction.md is identical for single, multi, and multi_noplan;
  >     decomposition.yaml is the plan-guided multi orchestrator's private channel
  >     only. Detailed multi-agent architecture in decomposition.yaml is the
  >     legitimate, intended asymmetry — not a violation.
  >   - tests/ is NOT in the Docker image; Harbor mounts it after the agent finishes.
  >     Never recommend COPYing tests/ or ground_truth into the image.
  >   - Judge / infra failure must surface an explicit error / INFRA sentinel
  >     (QD-02 check 5) — do NOT require a silent reward 0.0 for API/key failures.
  >   - Known wording defects in /rubric itself: QD-07's checks 10 and 12 say a
  >     FAIL forces "the overall QD-10 result" to FAIL — they mean QD-07. QD-08's
  >     check 5 is named for LLM fallback but its body also covers verifier
  >     determinism. QD-01 check 5's "equally weighted by design" clause forbids
  >     scoring-mechanic leaks inside instruction.md, not category weights in the
  >     verifier. Follow the check bodies, not the stale labels.
  >
  > ## MANDATORY COMPLETENESS — no QD may be skipped
  >
  > You MUST produce a /qd_results/QD-XX.json for EVERY QD in your list, even if an
  > earlier QD returned FAIL. Each QD's checks must be evaluated against the actual
  > task files — never inferred from a sibling QD's verdict. Before returning, list
  > /qd_results/ and confirm every assigned QD has its file.
  >
  > ## MANDATORY INDEPENDENCE — no cross-QD contamination
  >
  > Each QD's verdict must trace ONLY to (a) the numbered checks in that QD's own
  > rubric section, and (b) verbatim quotes from local task files. You MUST NOT cite
  > a sibling QD as evidence or reason. FORBIDDEN patterns: "QD-N FAILs because QD-M
  > failed", "NOT_APPLICABLE because QD-M covered it", "propagating FAIL from QD-M",
  > or any reason text naming another QD. The same underlying issue may legitimately
  > FAIL one QD and PASS another.
  >
  > ## EVIDENCE REQUIREMENT — applies to EVERY check, no exceptions
  >
  >   (a) Quote-or-pass. To FAIL a check you MUST quote verbatim text from a specific
  >       local file (path + exact string) demonstrating the violation. Paraphrases
  >       are NOT evidence. If you cannot produce a verbatim local-file quote, the
  >       check PASSES.
  >   (b) Don't hallucinate. Never claim a URL, record, person, or external thing
  >       "does not exist" / "is fabricated" unless you have local evidence (e.g. a
  >       captured 404). Restrict yourself to what is locally checkable.
  >   (c) Today is real — do NOT trust your training cutoff for dates. Run
  >       `date -u +%Y-%m-%d` (or `Get-Date`) before judging whether a date is future.
  >       A date in the current month/year per the system clock is NOT fabrication.
  >   (d) Absence of confirmation ≠ proof of failure. "I could not confirm X" is not
  >       "X is fake." Default to PASS when evidence is missing or ambiguous.
  >   (e) Justify your PASS too — briefly cite the file and what you observed.
  >
  > Issuing a FAIL without a verbatim local-file quote is itself a reviewer error.
  > Prefer PASS over an unsupported FAIL.
  >
  > ## HARBOR ALIGNMENT — anchor every verdict on harbor rules + the rubric's explicit checks
  >
  >   (f) Harbor design is ground truth, not "fairness" intuition. The task-layer
  >       symmetry (same instruction.md) plus the decomposition.yaml asymmetry is the
  >       intended benchmark structure.
  >   (g) A NUMBERED check may only FAIL on a pattern its own rubric text enumerates.
  >       If your candidate FAIL does not match a pattern the rubric explicitly names,
  >       that numbered check is PASS — even if the situation feels off. A genuine
  >       defect the rubric does not enumerate belongs in an `additional_*` entry
  >       (step 4), never smuggled into a numbered check's verdict; hold it to the
  >       same verbatim-quote bar, and prefer WARN unless it is plainly blocking.
  >   (h) When in doubt, re-read the rubric section — do not extrapolate a novel
  >       violation theory it does not name.
  >   (i) Do not flag missing oracle/solution or missing tests/ in the image — these
  >       are Phase-2/Harbor-correct.
  >
  > ## JSON output contract — write ONE FILE PER QD in your list
  >
  >    (PowerShell) New-Item -ItemType Directory -Force -Path /qd_results/ | Out-Null
  >    then write /qd_results/QD-XX.json containing exactly:
  >    {"dimension":"QD-XX","result":"<PASS|FAIL|NOT_APPLICABLE|WARN>","checks":[{"id":1,"name":"<str>","result":"<PASS|FAIL|NOT_APPLICABLE|WARN>","reason":"<str>"}],"justification":"<str>"}
  >
  > STRICT FIELD CONTRACT — parsed by Pydantic (`QDResult` / `CheckDetail`). ANY
  > deviation aborts the review:
  >    - `result` (top-level AND each check) MUST be EXACTLY one of PASS, FAIL,
  >      NOT_APPLICABLE, WARN (uppercase). Not N/A, Passed, OK, null, "".
  >    - `checks[*].id` MUST be a JSON integer (1, not "1").
  >    - `checks[*].name`, `checks[*].reason`, `justification` MUST be JSON strings —
  >      never null, never numbers, never the name of another QD.
  >    - Emit valid JSON only — no trailing commas, no comments, no smart quotes.
  >
  > ## QD-09 NORMALISATION (Group E only)
  >
  > QD-09's rubric section emits a different shape from every other QD: a
  > `dimensions[]` array whose entries carry `finding`, and a result that may be
  > `FLAG`. The harness parses neither. Convert before writing the file:
  >    - each `dimensions[]` entry becomes a `checks[]` entry, ids 1-4, names
  >      `single_agent_trace`, `multi_agent_trace`, `gap_integrity`,
  >      `coordination_verdict`;
  >    - `finding` text goes into `reason` verbatim;
  >    - `FLAG` (top-level or per-dimension) is written as `WARN`, and the reason /
  >      justification text says so explicitly — e.g. "FLAG (reported as WARN): ...".
  >      This is exactly what the hosted reviewer does, and the orchestrator's
  >      decision logic depends on being able to see it.
  >
  > ## QD-10 FILE CONTRACT (Groups F and G only)
  >
  >    - Group F writes `/qd_results/QD-10-EXPLOIT.json` in the exploiter schema
  >      given in the rubric's QD-10a section (`exploits[]` with `mechanism`,
  >      `target_file`, `target_evidence`, `example_hacky_output`,
  >      `estimated_effort_to_produce`, `estimated_score_if_submitted`, plus
  >      `coverage_note`). This is an INTERMEDIATE artifact — it is NOT a QDResult
  >      and must NOT appear in the final report's `dimensions` map.
  >    - Group G writes `/qd_results/QD-10.json` in the standard QDResult shape above,
  >      one `checks[]` entry per exploit, named
  >      `exploit_<n>_<short-slug-from-exploiter-title>`.
  >
  > Return a one-line confirmation listing each QD in your set and its top-level
  > result, e.g. "QD-08: PASS; QD-09: WARN".

## After the 6 Phase-1 Agent calls return

1. Confirm `/qd_results/QD-10-EXPLOIT.json` exists, then dispatch Group G (`exploit-grader`) — one Agent call, alone, in that turn. If Group F failed to write the exploit file, re-dispatch Group F once before dispatching G.
2. List the result folder: `Get-ChildItem "<ARTEFACTS_ROOT>\qg_run\"` (PowerShell) or `ls "<ARTEFACTS_ROOT>/qg_run/"` (Bash). Anywhere the prompt says `/qd_results/` or `/tmp/qd_results/`, the on-disk path is `<ARTEFACTS_ROOT>\qg_run\`.
3. Verify QD-01 through QD-10 are ALL present (10 QDResult files, plus the intermediate QD-10-EXPLOIT.json). If any are missing, dispatch one additional Agent call to the owning group to produce them. Do NOT assemble a final report while any QD is missing.
4. Read each QD-XX.json and assemble the final report. QD-10-EXPLOIT.json is working material only — do not put it in `dimensions`.

## Decision logic

  - ALL 10 dimensions are BLOCKING: any FAIL anywhere → decision = REJECT
  - No FAIL anywhere, but QD-09 is WARN (i.e. the rubric's FLAG) → decision = MANUAL_REVIEW. QD-09's own rule is that a FLAG "must be reviewed by a senior reviewer before the task is submitted", and the hosted gate returns MANUAL_REVIEW for exactly this shape — an otherwise-clean package whose QD-09 flagged.
  - No FAIL anywhere and QD-09 is PASS → decision = APPROVE. A WARN on any dimension other than QD-09, and any NOT_APPLICABLE, is non-blocking (the hosted gate has approved a package carrying a QD-03 WARN).
  - Also use MANUAL_REVIEW if a dimension could not be evaluated at all (missing files, tooling failure).

## Orchestrator-level completeness rule

Every QD result MUST have a `checks` entry for every numbered check in its rubric section — even after finding a FAIL. Extra `additional_*` entries beyond the numbered list are allowed and should be preserved, not pruned; carry any that are FAIL into `rejection_reasons[]` like any other failing check. If a sub-agent returned an incomplete result, fix it yourself (re-read the rubric + task files, fill missing checks) before producing the final report. The final report MUST contain all 10 QDs.

## Cross-QD independence — final-report level

When assembling, the `reason` and `justification` text for each QD MUST NOT reference any other QD. If a sub-agent's output contains forbidden cross-QD references ("see QD-N", "as QD-M found"), rewrite those reasons to cite the underlying file evidence directly, or downgrade the verdict per the evidence rule.

## Final Output Format

Your final response must be ONLY the JSON object below — wrapped in ```json fences OR as bare JSON.

**YOUR VERY FIRST CHARACTER must be ` ``` ` (start of a ```json fence) or `{`.**
**YOUR VERY LAST CHARACTER must be ` ``` ` (closing fence) or `}`.**

- NO words, spaces, or newlines before the opening character
- NO words, spaces, or newlines after the closing character
- No "I have all results", no "Applying decision logic" — anywhere

## PYDANTIC VALIDATION CONTRACT — READ CAREFULLY

Parsed by Pydantic models (`QualityGateReport` → `LLMReview` → `QDResult` → `CheckDetail`, plus `Decision` and `CheckResult` enums). ANY deviation raises a `ValidationError` and the entire review aborts.

### Enum values — case-sensitive, no synonyms allowed

| Field | Allowed values (exactly these strings) |
|---|---|
| `decision` | `APPROVE`, `REJECT`, `MANUAL_REVIEW` |
| `dimensions.*.result` | `PASS`, `FAIL`, `NOT_APPLICABLE`, `WARN` |
| `dimensions.*.checks[*].result` | `PASS`, `FAIL`, `NOT_APPLICABLE`, `WARN` |

**FORBIDDEN result variants** (will crash the parser): `N/A`, `NA`, `n/a`, `Not Applicable`, `not_applicable`, `Passed`, `passed`, `pass`, `Failed`, `failed`, `fail`, `Warning`, `warn`, `OK`, `SKIP`, `Skipped`, `NONE`, `FLAG`, `null`, `""`, numbers, booleans. Use `NOT_APPLICABLE` and `WARN` exactly. QD-09's rubric produces `FLAG` — write it as `WARN` and preserve the word FLAG in the `reason`/`justification` text, which is what the hosted reviewer does and what the MANUAL_REVIEW rule keys on.

**FORBIDDEN decision variants**: `Approve`, `approve`, `Reject`, `reject`, `MANUAL`, `manual_review`, `NEEDS_REVIEW`, `PENDING`. Use exact uppercase `APPROVE` / `REJECT` / `MANUAL_REVIEW`.

### Type constraints

| Field | Required JSON type |
|---|---|
| `task_id` | string |
| `decision` | string (enum above) |
| `dimensions` | object (map: dimension name → object) |
| `dimensions.*.result` | string (CheckResult enum) |
| `dimensions.*.checks` | array of objects |
| `dimensions.*.checks[*].id` | integer — NOT a string |
| `dimensions.*.checks[*].name` | string (non-null) |
| `dimensions.*.checks[*].result` | string (CheckResult enum) |
| `dimensions.*.checks[*].reason` | string (non-null; use "" if empty) |
| `dimensions.*.justification` | string (non-null; use "" if empty) |
| `rejection_reasons` | array of objects |
| `rejection_reasons[*].code` | string (non-null) |
| `rejection_reasons[*].message` | string (non-null) |

### Structural rules

- Strictly valid JSON: no trailing commas, no comments, no smart quotes, no Python None/True/False. `null` is NOT allowed for any field in this schema.
- `dimensions` MUST contain all ten keys `QD-01` … `QD-10`. There is no `QD-10a` / `QD-10b` key — QD-10b's output IS the `QD-10` entry, and QD-10a's exploit file never appears in the report.
- Every QD in `dimensions` MUST have all three keys (`result`, `checks`, `justification`).
- Every entry in `dimensions.*.checks` MUST have all four keys (`id`, `name`, `result`, `reason`).
- Every entry in `rejection_reasons` MUST have both keys (`code`, `message`).

### Schema template

```json
{
  "task_id": "<folder name from /task/>",
  "decision": "APPROVE",
  "dimensions": {
    "QD-01": {
      "result": "PASS",
      "checks": [
        {"id": 1, "name": "<check_name>", "result": "PASS", "reason": "<verbatim evidence for FAIL, or brief confirmation for PASS>"},
        {"id": 2, "name": "<check_name>", "result": "NOT_APPLICABLE", "reason": "..."}
      ],
      "justification": "For PASS: 2-3 sentence overall assessment. For FAIL: list each failing check by ID and name."
    }
  },
  "rejection_reasons": [
    {
      "code": "<QD-XX.Y where Y is the check id, e.g. QD-02.1>",
      "message": "Check name: <name>. Evidence: <verbatim quoted text from the file>. Required: <what the rule says>. Fix: <what the trainer must change>."
    }
  ]
}
```

The agent spawns 6 sub-agents (covering QD-01…QD-09 plus the QD-10 exploiter simultaneously), then one grader once the exploiter returns. Each reads the task files against one set of criteria, and you get a single report back with every rejection reason quoted directly from your files.

## Why this matters

The hosted QG Draft Reviewer runs the same 10 semantic dimensions (plus the static S-xx checks). Catch a FAIL locally first and you fix + resubmit without spending a review slot.
```

---

## Where this gate fits in the Phase-2 pipeline

- **Blocking**: do not upload the submission ZIP to the hosted Draft
  Reviewer until this gate returns `"decision": "APPROVE"` and the local
  static gate (`static_checks.py`) and judge self-check
  (`selfcheck_judge.py`) both pass.
- **Independent**: run in a fresh agent session, not the chat that built
  the task.
- **Complements, does not replace, the hosted reviewer**: this covers the
  semantic QD-01…QD-10 dimensions. A full hosted run additionally reports
  Layer 1 static checks (`S-01_zip_package`, `S-02_required_files`,
  `S-03_task_toml`, `S-04_decomposition`, `S-05_cross_file`,
  `S-06_leakage`, `S-07_stale_logs`, plus `S-08` on
  `rubric_manifest.json`) and a Layer 2 execution line
  (`Single | Multi | Gap`), and requires Turing login + a Drive upload.
  A hosted *Temporary/Draft* review runs Layer 3 only — no static, no
  execution — and explicitly does not count as a submission review.
- **Persist**: save each run's final JSON to
  `<ARTEFACTS_ROOT>\qg_report.json` (overwrite on re-run). The last
  approving JSON is the audit trail submitted alongside the ZIP.
- **Re-sync duty**: the hosted reviewer's dimension set moves (QD-10 was
  added 2026-07-23; production-rework items such as `high_level_prompt.md`,
  `multi_noplan` logs, and QD-03 content≥60% landed later). Whenever a
  hosted report shows a dimension or check ID this prompt does not
  dispatch, or when `Quality_dimensions_phase_2.md` gains/renumbers
  checks, update this file before the next local run.
