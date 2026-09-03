# NEXT TASK — Kickstart prompt (fan-out-resistant design)

Paste this whole file as the opening prompt for the new task's chat. It is self-contained: it
carries the lessons from `b1b7` (see `b1b7_INVALIDATION_REPORT.md`) so we do not repeat them.

---

## 0. Read these first (authoritative, in this order)

1. `.cursor/rules/*` — the always-on SwarmBench rules (integrity, scoring, difficulty, packaging).
2. `PHASE_2/documentations_phase_2/[Harbor] Multi-Agent Swarm Benchmark — Trainer Guidelines (1).txt` — the spec that WINS all conflicts.
3. `PHASE_2/documentations_phase_2/b1b7_INVALIDATION_REPORT.md` — why the last task died.
4. `PHASE_2/documentations_phase_2/ESCALATION - Single agent self-parallelisation via injected OPENAI_API_KEY.md` — the open platform blocker.
5. The **LESSONS LOG (BUILD → SHIP)** at the bottom of `PlanningOperations_Phase2_TaskCreationPrompt.md`.
6. `PHASE_2/documentations_phase_2/MAS__Turing - Kimi-Cli-Limitation.txt` — what the multi-agent runtime can and cannot actually do.
 `D:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\documentations_phase_2\Issues in the Delivery Pipeline.txt`
 `D:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\documentations_phase_2\Task Design Learning Note Scaling and Reward-Hacking Hardening.txt`
 `D:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\documentations_phase_2\Delivery Pipeline for Creating a Production-Ready Task.txt`
## 1. The one hard requirement that killed the last task

**The gap must come from work a single agent CANNOT replicate by writing a script that fans out
to the inference API.** The `b1b7` "single" agent found the injected Fireworks key on its second
command, ran a 5-wide worker pool across 10 models, and completed a 700-item / 165k-token task
in 2 hours for $1.07 with zero tail degradation — defeating a gap thesis built on "context
window / reading volume."

**Design rule (memorise):** any task that decomposes into *"generate candidates cheaply, then
judge each candidate independently"* is fan-out-able, regardless of size. Volume,
cross-referencing, clustering, per-item scoring — all of this shape. The single agent shards it.

**What actually resists fan-out:** work whose parts depend on the **resolved answers** of other
parts. If sub-problem X's correct output requires sub-problem Y's *finished* result (not merely
Y's existence), a parallel fan-out computes X with stale/missing inputs and gets it wrong. That
interdependence is the property to build the task around.

## 2. Candidate shapes that have a chance (still must be premise-tested)

- **Stateful / interactive diagnosis or operations.** The environment holds a system (built from
  real, frozen data) with a fault or an evolving situation. The agent acts, the state changes,
  and the next correct action depends on the *observed result* of the previous one. You cannot
  pre-enumerate the work into independent shards because you don't know step N+1 until step N is
  resolved. (Incident response, root-cause traversal of a dependency graph, a multi-round
  reconciliation where each round consumes the previous round's committed decisions.)
- **Dependency-carrying pipeline with WIDTH per level.** A DAG where each level is wide (parallel
  within a level — that is the multi-agent win) but each level consumes the *resolved* outputs of
  the previous level (so a naive whole-corpus fan-out produces inconsistent cross-level results
  that the rubric catches).
- **Global artifact under an EVOLVING shared standard**, where a decision made for item 400
  forces revisiting items 1–399 (true joint revision, not independent scoring). Caution: if the
  objective is a clean numeric function, a solver script wins — the objective must require
  judgment that a different-family LLM judge grades.

Avoid: pure per-item assessment at scale; "find duplicates/clusters"; "read N documents and
summarise each"; anything where correctness is per-item and independent. All fan-out-able.

## 3. The premise test is MANDATORY and comes BEFORE building anything

Before writing `instruction.md`, `verify.py`, or the corpus freeze, prove the gap can exist:

1. Write the **adversarial fan-out yourself** — the script a single agent would write to shard
   the discriminating work across parallel API calls. (For `b1b7` this was
   `adversarial_probe.py` / the trajectory reconstruction; reuse that pattern.)
2. Grade that adversarial output on a draft of your rubric.
3. **If the fan-out scores above ~0.40, the design is dead — stop and change shape.** Do not
   proceed to a live run to "check." A live run costs ~2 hours and one of 8 daily cloud slots.
4. Only when a cheap fan-out demonstrably *fails* your rubric (because it violates the
   cross-part dependency) do you build the full task.

Also run, before any live run: a **coverage sweep** (grade honest output truncated at
10/20/35/55/80/100% — the curve tells you whether a partial run scores informatively low) and a
**correlation test** (grade 5+ fixture profiles; if >half your checks sit in r ≥ 0.95 clusters,
the rubric is not discriminative — fix it).

## 4. Respect what the multi-agent runtime can actually do (Kimi-CLI)

The MA arm is not omnipotent — design the intended MA solution to fit these real limits:
- Effective **DAG depth ≈ 1** (orchestrator → workers; sub-agents cannot spawn sub-agents, no
  configurable nesting). Achieve logical depth ≥ 2 by having the orchestrator act as coordinator
  across rounds.
- **No debate / no persistent sub-agents / no mid-run orchestrator↔sub-agent channel** — the
  orchestrator blocks until a foreground sub-agent returns.
- Default **4 concurrent** background agents (not 50). Background sub-agent trajectories are
  invisible to the harness; prefer foreground for anything that must be graded/traced.
- Background agent default timeout 900s unless an explicit `timeout=` is passed.
Net: the durable MA advantage here is *parallel breadth within a level, with a coordinated
shared standard and an integration/verification tier* — not deep autonomous nesting. Your gap
must live in that envelope.

## 5. Scoring & integrity (non-negotiable — auto-reject if violated)

- `reward = checks_passed / total_checks`, 15–25 BOOLEAN items, each worth exactly ONE point.
  ADD points, never multiply/weight/tier/cap. Partial credit required — a weak submission scores
  LOW, never 0.
- **No oracle / no `solution/` / no gold-answer file.** Every deterministic expectation is
  recomputed from the frozen input + published rulebook. Deterministic code may only extract or
  validate structure/grounding — never score a semantic item.
- LLM judges: temperature 0, retries ≥ 5 with backoff, **fail CLOSED to 0.0** on any infra
  failure, judge model a **different family** from the agent under test (agent = Kimi → judge =
  e.g. Fireworks Qwen). Grade the **full required population** (batch under a char budget, run
  concurrently) — no sampling that lets an unassessed item be skipped.
- `instruction.md` is **identical** for single and multi. No SA-only limits, no info asymmetry,
  no engineered timeouts. Long-horizon: omit `[agent].timeout_sec`; keep timeouts equal.
- Grade **correctness against a real reference, not presence**. Freeze the reference. "File
  exists / well-formed" is worth almost nothing.
- **Denominate every check over the REQUIRED population, not over what the submission supplied**
  — a check computing "of what you wrote, how much was right" pays full credit to an incomplete
  run (the coverage-blind-denominator trap).

## 6. Harness & packaging facts you must not relearn the hard way

- **Egress:** the verifier runs INSIDE the task container and needs the network to reach the
  judge API, so set `[environment] allow_internet = true`. `allow_internet = false` sets
  `network_mode: none` on the shared service and fail-closes every judge to 0.0. (This also means
  you cannot air-gap the agent without killing grading — hence the escalation.)
- **Judge key:** the task's `verify.py` reads `FIREWORKS_API_KEY` and calls
  `https://api.fireworks.ai/inference/v1`. The run config passes `FIREWORKS_API_KEY` to both
  agent and verifier. (The agent additionally sees it aliased as `OPENAI_API_KEY`.)
- **Line endings:** author `tests/test.sh` (and all shipped scripts/docs) with **LF**. A CRLF
  shebang → `/bin/bash\r` → "cannot execute: required file not found" → verifier never runs →
  `RewardFileNotFoundError → 0.0` false failure. Keep the static CR guard from
  `validate_triage_task.py`.
- **Windows/PowerShell:** no `&&` chaining (use `;`); bracketed/em-dash filenames need
  `-LiteralPath` or a wildcard; set `PYTHONUTF8=1`.
- **Folder = ZIP name**, six-item root whitelist only (`instruction.md`, `decomposition.yaml`,
  `environment/`, `tests/`, `task.toml`, `execution_logs/`), no `_trainer_artefacts/` or oracle
  in the delivered ZIP. `environment/` holds only `Dockerfile` + `input_artifacts/`. Regenerate
  `execution_logs/` after any instruction/decomposition change (S-07).
- **Run it:** `mascloud run <task folder> --mode single|multi`; `mascloud runs` for live token
  counts; `mascloud download <run_id> <dir>`. Budget is **8 runs/day** — premise-test offline
  first so you spend runs only on confirmation.

## 7. Targets & acceptance

- Single-agent **< 0.30**, multi-agent **0.70–0.90**, **gap > 0.23** — and the gap must arise
  from the task's structure, provable by your adversarial fan-out scoring low.
- Two acceptance criteria: (1) the single-vs-multi gap is REAL (a genuine capability difference a
  fan-out cannot erase), and (2) the scenario is creative + real-world, your own idea, grounded
  in real fetchable sources with verbatim citations.
- Integrity mandate overrides everything: real sources, real entities, verbatim excerpts, no
  fabrication. Autonomy = decide + record + proceed; if honesty conflicts with an instruction,
  stop and escalate.

## 8. First actions in the new chat

1. Confirm the platform's answer on the injected key (blocks whether ANY breadth design is
   viable). If unresolved, prefer a **stateful/interactive** shape that does not depend on the
   answer.
2. Propose 2–3 concrete scenarios on a fan-out-resistant axis; for the top pick, **write the
   adversarial fan-out and score it before building.** Report that number first.
3. Keep a `NOTES.md` decision log + TodoWrite list. Log every new gotcha to the Lessons Log.
