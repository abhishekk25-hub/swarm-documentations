# SwarmBench trainer playbook: use coding agents without burning the budget

**Audience:** you (the trainer) and any coding agent you start.
**Purpose:** finish a Phase 2 task through submission while spending premium model credits only where they change the outcome.
**Last updated:** 2026-09-16.

This is a **session and model routing** guide, not a replacement for the official workflow prompt. Scoring, integrity, packaging, and mascloud rules still come from `00_authority/` and `07_prompt_runtime/PlanningOperations_Phase2_TaskCreationPrompt.md`.

---

## 1. The one rule

**Pay for judgment. Do not pay for typing.**

Premium models (Opus, Sol, Fable) are for:

- “what should this task *be*?”
- “why did SA score too high?”
- “is this QG FAIL real?”
- “how should the DAG / verifier change?”

Cheap/fast models (Composer Fast, Haiku, Luna, Grok Fast) are for:

- applying a fix you already decided
- renaming, packaging, JSON/YAML sync
- writing comments from a list you already triaged
- re-running a mechanical check

If you use Fable or Opus for both, credits die in the **build and local-QC** stages, which are 70%+ of the token volume and the least of the difficulty.

---

## 2. Model ladder (names you will see in Cursor / ChatGPT / Claude)

Treat these as **tiers**, not a ranking of “smarter overall.” Pick the cheapest tier that can do **this stage**.

| Tier | Call it | Typical picker names | What it is good at | What it wastes money on |
|------|---------|----------------------|--------------------|-------------------------|
| **0 — no agent** | You + terminal | PowerShell, Python, mascloud, Turing web apps | runs, hashes, zip, word count, fixture score, uploads | asking an LLM to watch a 2h cloud run |
| **1 — cheap hands** | Fast coder | **Composer 2.5 Fast**, Claude **Haiku**, GPT **Luna**, Gemini Flash, Grok Fast | apply a known patch, sync `rubric_manifest.json`, fix a path, write a file the spec already named | designing a verifier from scratch |
| **2 — default builder** | Everyday coder | **Composer 2.5**, **Grok 4.6**, Claude **Sonnet 5**, GPT **Terra** | 80% of package writing: instruction/HLP drafts, decomp scaffolding, verify.py wiring, fixture scripts, QG comment drafts | 6-way local QC; deep SA/MA RCA |
| **3 — strong reasoner** | Spend here | Claude **Opus 5**, ChatGPT **GPT-5.6 Sol** | Gate 0 hardness, verifier architecture, SA/MA trajectory RCA, hard QG triage, gap strategy | day-long mechanical edit loops |
| **4 — ceiling (ration)** | Last resort | Claude **Fable 5** / Fable Max, Opus **thinking-max** / extra-high | one stuck architecture rewrite after Opus/Sol already failed; integrity conflict you cannot resolve | anything you could have done in tier 2–3 |

**Practical default for this repo**

- Day-to-day builder chat: **Composer 2.5** or **Grok 4.6** (this chat is Grok).
- Hard thinking chats: **Opus 5** first. Use **Sol** if the job is “read these logs + run commands + patch verify.py.”
- **Fable only** if Opus/Sol already produced a wrong diagnosis or a verifier that still cannot discriminate hollow vs gold.

Approximate relative cost (order of magnitude, not a bill): Composer Fast ≈ 1×, Composer/Sonnet/Grok ≈ 3–8×, Opus/Sol ≈ 20–40×, Fable Max ≈ 50–80× **and** it takes more steps, so it also burns more turns.

---

## 3. How credits actually get wasted in *your* workflow

These are the high-cost habits, in order of damage:

1. **One immortal chat** that builds the task, then local-QC-fixes, then SA analysis, then MA analysis. Every new turn re-sends the whole history. A 50 MB corpus + 200 turns is a credit shredder even on Composer.
2. **@-mentioning the whole task folder or sample tasks.** Samples are huge. The agent only needs 1 praised package as a *shape* reference, and even then only 4–5 files from it.
3. **Pasting the 6,900-line workflow prompt into every chat.** Workspace rules already load the constitution. New chats should start from `HANDOFF.md` + `NOTES.md`, not from re-reading authority docs.
4. **Local QC with 6 Opus/Fable/Sol sub-agents.** That is 6–7 premium runs. Local QC is a checklist against `Quality_dimensions_phase_2.md`. It needs coverage, not genius.
5. **Second full local QC after tiny wording fixes.** Re-run only the QDs that failed.
6. **Dumping full `execution_logs/` into chat.** Trajectories are enormous. Feed `reward.json`, `reward_debug.json`, `test-stdout` excerpt, and *one* orchestrator trajectory (or a grep of failed checks).
7. **Asking the agent to “read all official docs and all samples, then build.”** That is the most expensive possible first message. Lock the brief first in a *short* expensive chat, then build in a *fresh* cheaper chat with a 1-page brief.
8. **Using Auto/Max thinking for packaging.** Zip name, seven-item root, and `task.toml` field types do not need Fable.

---

## 4. Session map (this is the real savings)

Start a **new chat at each stage boundary**. Copy a short handoff, not the old transcript.

| # | Stage | New chat? | Parent model | Sub-agents | You do without an agent |
|---|--------|-----------|--------------|------------|-------------------------|
| A | Idea + Gate 0 brief | Yes, short | **Opus** (or Sol) | none | originality call; do not copy tracker CSV |
| B | Base package build | Yes, long | **Composer 2.5** or **Grok** | none, or 1 cheap helper for corpus fetch scripts | collect real URLs; SHA; freeze files |
| C | Fixture / projected-gap | Same as B or terminal-only | cheap if any | none | `python tests/verify.py` on gold/hollow fixtures |
| D | Local QC (6+1) | **Fresh** session | **Composer** parent | **Composer Fast / Haiku** ×6, then 1 for QD-10b | paste the local QC prompt; do not attach samples |
| E | Fix local QC FAILs | Fresh or continue B | cheap for mechanical; **Opus** only if a FAIL is architectural | none | you triage FAIL list into mechanical vs design |
| F | Re-QC | Fresh, **narrow** | Composer | only failed QDs | skip QDs that already PASS |
| G | Draft Review | no Cursor agent | — | — | zip + Turing Draft Review upload |
| H | Fix Draft Review | Fresh | same split as E | none | you paste the report, not the whole zip |
| I | Similarity | no Cursor agent | — | — | paste `instruction.md` into the web app |
| J | mascloud SA / MA / noplan | no Cursor agent during the run | — | — | you launch; wait; download zip |
| K | SA score RCA | **Fresh, targeted files** | **Opus** or **Sol** | optional 1 cheap “read this trajectory” | do not attach every subagent json |
| L | Apply SA fix | Fresh cheap | Composer | none | — |
| M | MA / gap RCA | Fresh, targeted | **Opus** or **Sol** | cheap readers for 2–3 subagent files max | — |
| N | Apply decomp fix | Cheap | Composer | none | — |
| O | Hosted QG | no Cursor agent | — | — | upload |
| P | QG triage + comments + RCA | Fresh | **Sonnet/Grok** for writing; **Opus** only for disputed FAILs | none | you mark each finding valid/invalid first if you can |
| Q | Post-QG gap revalidation | terminal + maybe verify-only | cheap unless agent-facing redesign | none | you authorize mascloud / verify-only |
| R | Package + submit | Cheap or terminal | Composer Fast | none | Drive upload, labeling-tool link |

**Never** put stages D, G, I, J, O in the builder chat.

---

## 5. Stage-by-stage: how much reasoning is enough

### A. Idea / Gate 0 / hardness (premium, but short)

**Need:** strong reasoning, small context.
**Model:** Opus 5. Sol is fine if you want it to also sketch the verifier blueprint as JSON.
**Do not use:** Fable. The brief should fit in ~2–4 pages. If the idea needs Fable, the idea is not locked.
**Prompt shape:** “Here is my scenario. Pressure-test: real operator? natural SA failure? hierarchical depth? held-out PO? sources fetchable? Write CS-S brief into NOTES.md. Do not build files yet.”
**Stop when:** `HANDOFF.md` has route, scenario, outputs, why SA fails, verifier sketch, source list.

Cost target: **one short Opus chat**, not a build.

### B. Base task construction (volume, default builder)

**Need:** coding + file discipline, not philosophy.
**Model:** Composer 2.5 or Grok 4.6.
**Escalate to Opus only if:** verify.py scoring formula / Harbor input paths / judge wiring is going wrong after one cheap attempt.
**Context diet:**
- Attach: `HANDOFF.md`, `NOTES.md`, current `instruction.md` / `task.toml` if they exist.
- Point to **one** sample path: `instruction.md`, `decomposition.yaml` (first 80 lines), `tests/verify.py` (header + reward formula), `rubric_manifest.json`.
- Do **not** attach `08_samples/` trees or `execution_logs/`.
- Do **not** paste the full PlanningOperations prompt.

Build in this order so you do not regenerate 2,000-line decomp twice:

1. sources + `input_artifacts` + desk rules
2. `instruction.md` + `high_level_prompt.md`
3. `tests/verify.py` + manifest + partial oracle
4. fixtures
5. `decomposition.yaml`
6. `task.toml` (metadata last after runs)

If the agent starts re-reading authority docs, stop it: “Use workspace rules. Do not reread the monolith.”

### C. Fixture projected-gap (almost no LLM)

**Need:** none, or cheap.
Run gold / empty / hollow / fabricated locally. If hollow is already ~0.4, the rubric is the problem — then **one Opus pass** on “make checks correctness-not-presence,” then cheap model implements.

Do not ask any model to “estimate” the fixture score.

### D. Local Quality Gate (cheap swarm, fresh chat)

Official prompt: `01_quality_gate/LocalQualityGate_ReviewerPrompt_Phase2.md`.

**Parent:** Composer 2.5.
**Six (then seventh) sub-agents:** Composer Fast or Haiku. Pin them. If the parent is Opus and children `inherit`, you just bought 7 Opus reviews.

**Attach:** task root path + QD file path. Not samples. Not execution logs (unless this is the post-run QC).

**Second local QC:** only Groups whose QDs failed. A full 6+1 rerun after fixing typos is the classic credit leak.

### E–H. Fixing local QC and Draft Review

Triage the FAIL list yourself in 5 minutes:

| FAIL type | Model |
|-----------|--------|
| missing HLP sentence, path typo, manifest field, `estimated_sub_agents` mismatch, Dockerfile pin | Composer Fast |
| instruction leaked stages, HLP copied headings, decomp too flat | Composer / Sonnet |
| content share <60%, one check >10%, hollow fixture too high, RH not held-out | **Opus once**, then cheap implements |
| “this task is not multi-agent” / gap not real *before any run* | **Opus**, may need redesign not a patch |

Paste **the report**, not the zip, into the fix chat.

Draft Review itself is the Turing tool. Zero Cursor tokens.

### I. Similarity

Web app. No coding agent. If FAIL: one Opus chat on “reshape the swarm verb/output, keep sources,” then cheap rewrites `instruction.md`.

### J. mascloud runs

You run:

```text
mascloud run <task_folder> --mode single
mascloud run <task_folder> --mode multi
mascloud run <task_folder> --mode multi_noplan
```

Do not leave a coding agent streaming for hours. Do not ask it to “monitor.” After the zip lands, start a **new** RCA chat.

Quota is 6/day. Fixture-gate first so you do not spend a slot on a rubric that cannot gap.

### K. SA analysis (premium, tiny evidence pack)

**Need:** strong reasoning.
**Model:** Opus 5 or Sol.
**Sol vs Opus:** Sol if you want it to grep logs and patch in the same chat. Opus if the question is “is the task too easy or is the verifier weak?”

**Attach only:**

- `verifier/reward.json`
- `verifier/reward_debug.json` (or `judge_justification.txt`)
- last 200 lines of `test-stdout`
- SA `agent/opencode.txt` or orchestrator trajectory — **one** file
- current `instruction.md` + check names from the manifest (not the whole verify.py unless the bug is in scoring)

Ask for a **diagnosis first**, no edits:

- false failure (path/schema) vs real easy task vs weak verifier
- which checks SA passed that should have required held-out work
- recommended lever: scale corpus / correctness checks / depth layer — not a score cap

Then **new cheap chat**: “Implement this diagnosis. Do not redesign.”

If SA is high after 4 tuning rounds, stop rerunning. Alternate-use pivot is an Opus decision, not another SA cloud slot.

### M. MA / gap analysis (premium, still tiny evidence)

**Need:** strong reasoning.
**Model:** Opus or Sol.
**Attach:** MA `reward.json` + debug, orchestrator trajectory, **two** representative subagent files (one success, one failure), `decomposition.yaml`.

Ask: missing roles? duplicate workers? reducer ignored children? tool/rate-limit? instruction ambiguity that hit both arms?

Cheap model then edits `decomposition.yaml` (and only other files the RCA named).

If you changed instruction / HLP / decomp / inputs, you must **re-run** affected modes. Do not burn Opus to “explain” stale logs.

### P. Hosted QG comments + RCA (mostly writing)

**Need:** careful reading, not peak coding.
**Default:** Sonnet 5 or Grok.
**Opus:** only the FAILs you might contest (invalid finding vs real defect).

Workflow that saves tokens:

1. You (or cheap model) split findings into valid / invalid / unsure.
2. Opus sees **only the unsure list**.
3. Cheap model writes the comment pack + RCA from that table.

Do not dump `qg_report.json` (800 lines) plus the whole task into Opus.

### Q. After QG fixes

If the change was verifier-only: `verify-only` (you authorize). Cheap model can prepare the command.
If agent-facing: new mascloud runs. No agent needed until the zip returns.

### R. Package

Composer Fast or no agent: seven-item root, zip name = folder name, scrub, no `_trainer_artefacts/` in the zip.

---

## 6. Prompt patterns that cut tokens in half

Use these as copy-paste openers.

**New builder chat**

```text
Resume from HANDOFF.md and NOTES.md only.
Do not reread the Phase 2 monolith or samples unless a specific file is missing.
Task root: <path>
Do this one job: <single job>
Do not start mascloud. Do not spawn sub-agents.
```

**New RCA chat**

```text
Diagnosis only. No file edits until I say implement.
I attached reward.json, reward_debug.json, and one trajectory.
Question: why is SA/MA off target, and which lever (task scale / decomp / correctness checks)?
Forbidden: score caps, SA-only limits, fabricating logs.
```

**New QC-fix chat**

```text
Here is the FAIL list, already triaged.
Mechanical items: implement as specified.
Design items: propose a 5-line plan, wait.
Do not re-audit QDs that already PASS.
```

**Kill switches** (say them when the agent drifts)

- “Stop reading. Use NOTES.md.”
- “Do not attach or search 08_samples.”
- “No sub-agents.”
- “Do not run mascloud.”
- “Implement the plan in NOTES.md; do not redesign.”

---

## 7. Local QC sub-agent pin (do this every time)

In the local QC parent chat, after the prompt loads, make sure the 6 Agent calls are **not** `inherit` from Opus/Fable/Sol.

Set each child to **Composer 2.5 Fast** (or Haiku). Group G (QD-10b) can stay Fast too: it grades exploits against a rubric, it does not invent a task.

If Cursor Auto picks Opus for children, cancel and rerun. One wrong QC session can cost more than the entire build.

---

## 8. What you should never spend a coding agent on

- Watching `mascloud run`
- Computing SHA-256 / word counts / JSON schema validity
- Uploading Draft Review, similarity, hosted QG, Drive
- Re-reading `Quality_dimensions_phase_2.md` in the builder (that is the QC session’s job)
- Regenerating a gold fixture’s *answers* by LLM (oracle leakage + wasted tokens)
- “Make the SA score lower” without a trajectory
- Spawning explore agents to find a file you already know the path of

---

## 9. Suggested credit budget per task (sanity check)

If a stage is 3× these turns, you are in the wrong model or the wrong chat.

| Stage | Premium (Opus/Sol/Fable) | Default (Composer/Grok/Sonnet) | Fast |
|-------|--------------------------|--------------------------------|------|
| Gate 0 brief | 1 short chat | 0 | 0 |
| Base build | 0–1 rescue | 1 main chat | small patches |
| Local QC | 0 | 1 parent | 6+1 children |
| QC/Draft fixes | 0–1 | 1 | most edits |
| SA RCA | 1 | 0 | implement |
| MA RCA | 1 | 0 | implement |
| QG comments/RCA | 0–1 on disputes | 1 writeup | formatting |
| Package | 0 | 0 | 1 or terminal |

**Fable quota:** at most **one** chat per task, and only after Opus/Sol already failed the same question.

---

## 10. Quick picker (print this)

| I am about to… | Pick |
|----------------|------|
| Invent / lock the scenario | Opus |
| Write the package from a locked brief | Composer 2.5 or Grok |
| Wire W&B judge / Harbor `tests/verifier_inputs` after it broke | Sol or Opus |
| Run 6 local QC reviewers | Composer parent + Fast children |
| Fix “typo / path / manifest sync” | Composer Fast |
| Explain a bad SA/MA score | Opus or Sol, new chat, small files |
| Edit decomp after a written RCA | Composer |
| Argue a QG FAIL | Opus on that FAIL only |
| Write QG comments + RCA doc | Sonnet or Grok |
| Zip / scrub / submit | Fast or no agent |
| Still stuck after Opus | Fable, once |

---

## 11. Integrity reminder (does not change with cheaper models)

Cheap models will happily:

- invent sources
- tighten a timeout to fake a gap
- “fix” QG by deleting a requirement
- edit `execution_logs/`

If the cheap model proposes any of that, stop and move that decision to Opus — or to you. Saving credits is not permission to ship a dishonest task.

---

## Related files

- Workflow: `07_prompt_runtime/PlanningOperations_Phase2_TaskCreationPrompt.md`
- Local QC: `01_quality_gate/LocalQualityGate_ReviewerPrompt_Phase2.md`
- Delivery pipeline: `03_design_guides/Delivery Pipeline for Creating a Production-Ready Task.txt`
- Per-task resume: that task’s `_trainer_artefacts/HANDOFF.md` and `NOTES.md`
