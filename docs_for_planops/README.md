# Phase 2 Documentation Catalog

Reorganized 2026-08-05. This folder is the **source of truth library** for SwarmBench Phase 2 task creation. The runtime agent kickoff still lives in `07_prompt_runtime/` until the prompt platform ships; this README defines what each document is for and how the prompt system should use it.

**Prompt-platform plan:** [`10_prompt_platform/IMPLEMENTATION_PLAN.md`](10_prompt_platform/IMPLEMENTATION_PLAN.md)

---

## Folder map (read in this order when unsure)

| Dir | Role in prompt system | Always inline? |
|-----|----------------------|----------------|
| `00_authority/` | Official spec — **wins on any conflict** | Summary in constitution; full doc stage-loaded |
| `01_quality_gate/` | QD rubric + local pre-submit reviewer | Summary inline; full QD stage @ Phase 4 |
| `02_onboarding/` | Calls / KT that define Phase 2 intent | Stage @ Gate 0 (selective) |
| `03_design_guides/` | Rubric craft, pipeline, common mistakes | Stage @ Gate 3 / pre-submit |
| `04_domains/` | Domain packs (PO, KR, …) | Exactly one domain pack inline |
| `05_feedback/` | Client/batch/team feedback **ingestion** | Distill → ACTIVE lessons / platform; never dump raw |
| `06_incidents_and_lessons/` | Concrete failure RCAs | Distill → ACTIVE lessons |
| `07_prompt_runtime/` | Current monolithic kickoff prompt | Temporary until platform cutover |
| `08_samples/` | Exemplars (study, do not copy blindly) | Library / stage @ Gate 1–2 |
| `09_qg_reviews/` | Per-task QG reports | Maintainer distill only |
| `10_prompt_platform/` | Architecture + implementation plan | Maintainer |
| `_archive/` | Duplicates, Phase-1-era, ephemeral kickstarts | Never runtime |

---

## Document-by-document guide

### `00_authority/` — highest priority

| Document | About | Freshness | Prompt use |
|----------|-------|-----------|------------|
| `[Harbor] … Trainer Guidelines (2).txt` | **Phase 2.1 Trainer Guidelines v1.1 (2026-07-20)** — package contract, verify.py, rubric_manifest, S-01..S-07, CR rules, delivery | **CURRENT authority** (file dated 2026-08-03; replaces older `(1).txt` naming) | Layer 0/1 source for package/delivery. Stage-load full text when reconciling claim vs platform. |
| `Verifier & Rubric Manifest Standards (Effective Immediately).txt` | **Binding** Batch-12/14 verifier law: `hybrid` type, reward.json breakdown, content share (original ≥40%), held-out checks, manifest↔verify.py fidelity, same verifier SA/MA, hollow-fixture discrimination; QG **S-08** + QD-03 checks 7–8 auto-reject | **Effective immediately** | Distill into `const.scoring_*` / `plat.scoring_implementation`. STAGE MUST-read at Gate 3. Supersedes older “weights forbidden / always executable” wording where they conflict. Briefed in All-Hands 2026-08-04 (`02_onboarding/…`). |
| `Production Rework Requirements.txt` | **Production rework wave**: pause new authoring; Completed→Rework; force-reinstall mascloud for `multi_noplan`; three log packages (`single`/`multi`/`multi_noplan`); required `high_level_prompt.md` (~250 words); structural ≤**40%** / content ≥**60%**; multiplicative content-quality signal; ≥20pp SA–planned-multi gap; static checker + LLM QG report on resubmit | **Effective now** | Always distill into constitution + `plat.client_rejection_current` + packaging. STAGE MUST-read before any rework/resubmit. **SUPERSEDES** Verifier Standards content≥40% floor with the stricter ≥60%/≤40% share for this wave. Extends S-02 root with `high_level_prompt.md`. Full checklist: monolith P21-13. |

> Note: Cursor rules previously pointed at `Trainer Guidelines (1).txt`. That filename is gone; `(2).txt` is the live v1.1 copy in this tree. Phase-1 `…-V3.txt` remains superseded (see workspace `_archive`).
>
> Precedence among authority docs: Trainer Guidelines for package/delivery contract; **Verifier & Rubric Manifest Standards** for scoring/manifest/QG reject rules; **Production Rework** wins on content share (≥60%), `high_level_prompt.md`, and three-mode logs for this wave. If other details conflict, escalate — do not silently pick.
> The All-Hands meeting that walked trainers through the Verifier Standards is filed under `02_onboarding/` (not authority — the written announcement wins; notes add operational nuance).

---

### `01_quality_gate/`

| Document | About | Freshness | Prompt use |
|----------|-------|-----------|------------|
| `Quality_dimensions_phase_2.md` | Binding Phase 2 QD checklist (QD-01…; includes QD-10 reward-hacking pair) | Current for Phase 2 | Stage MUST-read before Phase 4 / local QG. Summarize only in compiled prompt. |
| `LocalQualityGate_ReviewerPrompt_Phase2.md` | Parallel sub-agent local QG harness mirroring hosted reviewer | Current (2026-07-31) | **Not** part of task-creation compile by default. Separate session prompt for pre-submit self-review. |

---

### `02_onboarding/` — intent & history (stage-load selectively)

| Document | About | Freshness | Prompt use |
|----------|-------|-----------|------------|
| `MAS2 - Onboarding call - 2026_06_25 …` | Initial Phase 2 requirements baseline | Foundational | Gate 0 education; already absorbed into monolith — prefer guidelines + platform modules over re-reading every time |
| `Onboarding for MAS 2.0 - 2026_07_20 …` | Phase 2.1 onboarding (three-dimension verifier, partial oracle, eval calibration) | **Important** | Stage when building/changing verifiers; feed `plat.phase21_*` |
| `MAS_2.0_Trainer_Onboarding_Expanded.*` | Expanded notes of 2026-07-20 call | Duplicate of notes in nicer form | Prefer `.txt`; PDF optional |
| `All_Hands_Meta_Multi_Agent_Swarm - 2026_07_01 …` | All-hands on meta / swarm design | Useful | Stage for decomposition creativity; distill durable rules into platform |
| `All -Hands - Verifier & Rubric Manifest Standards [MANDATORY] - 2026_08_04 …` | All-hands briefing for Batch-12/14 Verifier Standards (hybrid TOML, reward.json, content share, held-out vs copy-from-input, manifest fidelity, identical SA/MA verifier, print→test-stdout, hollow fixtures, simple scoring) | **Important companion** to `00_authority/Verifier & Rubric Manifest Standards…` | STAGE @ Gate 3 with the authority announcement. Notes ≠ authority (announcement wins). Meeting taught content ≥40%; Production Rework later raises floor to ≥60% for the rework wave. Distill print-logging + simple-scoring + classification rules into platform. |
| `MAS - All Hands Call.txt` | Early (May) four client shapes (WildSearch etc.) | **Partially outdated** vs Phase 2 hierarchical mandate | Historical context only; do not override Phase 2 pattern ban on map-reduce/fan-out |
| `MAS__Turing - Kimi-Cli-Limitation.txt` | Why OpenCode, not Kimi-CLI | Still true | Short platform note / stage once |
| `LLM_gennerated_tasks_guidelines_video_transcript.md` | Creativity / persona / build-on-seed KT | Still useful | Domain + Gate 0; methodology not idea bank |
| `phase2_meeting_presentation_brief.ipynb` | Phase 2 standards deck (classes, instruction style) | Useful | Stage @ Gate 1 |

PDF twins of `.txt` notes are **binary duplicates** — keep one text canonical; PDFs are human reading copies.

---

### `03_design_guides/` — how to design & grade

| Document | About | Freshness | Prompt use |
|----------|-------|-----------|------------|
| `rubric_scale_presentation.pdf` (+ `.txt`) | **Primary rubric craft doc** — correctness not presence; scale; gap levers | **Must-use @ Gate 3** | Stage MUST-read before verifier; lessons → `plat.difficulty_*` / scoring implementation |
| `rework-common-mistakes.pdf` (+ `.txt`) | Pre-submit mistake checklist (2026-07-28) | **Current / high value** | Distill into `plat.client_rejection_current` + ACTIVE lessons; stage @ Phase 5 |
| `Delivery Pipeline for Creating a Production-Ready Task.txt` | End-to-end pipeline (ideation → debug) | Current process | Stage for trainers; procedure already in gates/phases |
| `new_verifier_reward_system.md` | Management weighted 1/2/3 scheme after five-task zero-gap RCA | Partially aligned; use with Production Rework ≥60% content floor | Read with `00_authority/Verifier & Rubric Manifest Standards…` + `Production Rework Requirements.txt`; category 1/2/3 is one way to hit content ≥60% — still declare weights honestly in the manifest |
| `Task Design & Grader Construction.md` | Client praise patterns (floor-killers, content share) | Superseded-in-part by authority announcements (share now QG-hard; Production Rework raises floor to 60%) | Prefer authority docs for enforceable rules; keep this for praised-task examples |
| `Task Design Learning Note Scaling and Reward-Hacking Hardening.txt` | Worked pattern: scale units + RH hardening | Reusable method | Library / domain-agnostic design note; stage optional |
| `MAS2 Initial 50 Tasks Tracker …csv` | LLM-generated idea patterns | Methodology only | **Never** claim ideas from it; study DAG/scale columns only |
| `verifier_templates/WANDB_Qwen_Vision_Verifier_Template/` | **Team starter** for W&B LLM-judge HTTP calls (vision + text evidence, JSON responses, retries, infra vs quality failure). Default model `Qwen/Qwen3.6-35B-A3B` (smoke-tested). **Do not send `temperature`.** | **Current (2026-08)** | STAGE @ Gate 3 / Phase 2 when any check needs LLM (esp. charts/images). Copy the *call pattern* into `tests/verify.py`; do **not** ship as the whole grader — still add deterministic static/RH/PO + Production Rework reward.json. Prefer `hybrid` when mixed. See `.cursor/rules/swarmbench-judge-provider.mdc`. |

---

### `04_domains/`

| Document | About | Freshness | Prompt use |
|----------|-------|-----------|------------|
| `planning_operations/Thinking in Planning-Operations — …txt` | PO gap engine: many decisions × many constraints | Domain theory (still valid) | **PO domain pack** core |
| `knowledge_research/Knowledge_Research Domain Guide…txt` | Corpus → questions → oracle workflow | **Phase-1 shaped** (oracle, fan-out) | **KR domain pack source** — must be rewritten to Phase 2 (no oracle; hierarchical/specialist-routing) before inline use |

---

### `05_feedback/` — ingestion only

| Document | About | Freshness | Prompt use |
|----------|-------|-----------|------------|
| `batches/MAS_Client_Feedback_Document_2026-07-17.txt` | Consolidated client feedback (Batch-era) | Prefer this over June copy | Ingest → ACTIVE / platform; do not inline whole file |
| `batches/__TuringInternal__Batch-12…` / `Batch-14…` | Internal batch feedback (Aug 2026) | **Latest batch signal** | Same — distill blockers first |
| `Feedbacks.txt` | Stub for human rework notes | Empty template | Keep as append target; not compile input until filled |
| `LLM_Review_Issues.txt` | LLM QG issue log (mostly Phase-1 static checks) | **Mostly outdated** for Phase 2 scoring | Mine for still-true packaging lessons; archive rest |
| `team_updates/verifier_changes/` | reward.json / test.sh / verify.py examples | Operational | Capability `llm_judge` / packaging examples — library |

Archived: older `MAS Client Feedback Document` (2026-06-15) → `_archive/duplicates/`.

---

### `06_incidents_and_lessons/`

| Document | About | Prompt use |
|----------|-------|------------|
| `ESCALATION - Single agent self-parallelisation…` | SA cheating via injected key / self-fan-out | ACTIVE lesson `blocker` → platform fairness rule |
| `b1b7_INVALIDATION_REPORT.md` | Run invalidation RCA | ACTIVE / process lesson |
| `PREMISE_TEST_FINDING_falcon_ad_review.md` | Premise-test killed fan-out-indistinguishable design | ACTIVE lesson: premise-test before build |
| `HANDOFF_NOTE_next_task_design.md` | Task-specific handoff | Ephemeral; do not put in global compile |

---

### `07_prompt_runtime/`

| Document | About | Prompt use |
|----------|-------|------------|
| `PlanningOperations_Phase2_TaskCreationPrompt.md` | **Current monolith** (~compiled everything) | Temporary single kickoff until CCP+SL builder ships |

---

### `08_samples/` — exemplars

| Subfolder | Use |
|-----------|-----|
| `phase_2_1/` | Newest Phase 2.1-shaped packages — prefer when studying structure |
| `approved/` | Broad approved set (mixed domains) — trajectory/distinctness study |
| `praised/` | Client-praised patterns (align with Task Design & Grader Construction) |
| `initial/` | Early demos (e.g. EMERGPROCUREMENT, text_url patterns) — provenance patterns |
| `updated_poc/` | Updated POC copies — overlap with initial; prefer `phase_2_1` + `praised` first |

Never copy instruction text; study packaging, decomposition depth, verifier substance.

---

### `09_qg_reviews/`

Raw per-task QG reports. **Maintainer distill** into ACTIVE lessons / QG distillate — do not compile wholesale.

---

### `_archive/` (do not use for new tasks)

| Path | Why archived |
|------|----------------|
| `duplicates/planning_ops_doc.txt` | Byte-identical to Thinking-in-PO |
| `duplicates/Issues in the Delivery Pipeline.txt` | Superset wrapper around Delivery Pipeline doc |
| `duplicates/MAS Client Feedback…2026-06-15` | Older than 2026-07-17 client feedback |
| `outdated_phase1_era/AgentSwarmBench - Common Issues Report.txt` | May / early era |
| `outdated_phase1_era/Untitled` | Orphan QD-01 skill fragment |
| `ephemeral_kickstarts/*` | One-off kickstarts / manifests superseded by claim-time flow |
| `macosx/` | Junk |

---

## Precedence (when documents disagree)

1. `00_authority` Trainer Guidelines v1.1  
2. Constitution / compiled platform modules (once built)  
3. `plat.client_rejection_current` distilled from `05_feedback` + `rework-common-mistakes`  
4. Domain pack  
5. Onboarding notes / learning notes  
6. Samples / QG raw reports  

**Scoring note (updated by Verifier & Rubric Manifest Standards):** content (RH+PO) must be ≥40% of total score; structural ≤60%; manifest must truthfully describe any non-uniform weights/gates; use `verifier_type = "hybrid"` when mixing deterministic + LLM checks. Older “flat weight:1 only / never weight” text in the monolith and Batch-16 notes is **superseded for distribution** where it conflicts — still no silent tricks, and the manifest must match `verify.py`. Category 1/2/3 (`new_verifier_reward_system.md`) remains a valid way to meet the 40% content floor if the manifest declares it.

---

## Old → new path cheat sheet

| Old (root) | New |
|------------|-----|
| `PlanningOperations_Phase2_TaskCreationPrompt.md` | `07_prompt_runtime/…` |
| `[Harbor] … Guidelines (2).txt` | `00_authority/…` |
| `Quality_dimensions_phase_2.md` | `01_quality_gate/…` |
| `rubric_scale_presentation.pdf` | `03_design_guides/…` |
| `new_verifier_reward_system.md` | `03_design_guides/…` |
| `Verifier & Rubric Manifest Standards (Effective Immediately).txt` | `00_authority/…` |
| `Thinking in Planning-Operations…` | `04_domains/planning_operations/…` |
| `Knowledge_Research Domain Guide…` | `04_domains/knowledge_research/…` |
| `client_feedback_docs/*` | `05_feedback/…` |
| `phase_2_1_sample_tasks/` | `08_samples/phase_2_1/` |
| `QG_reviews/` | `09_qg_reviews/raw_reports/` |
