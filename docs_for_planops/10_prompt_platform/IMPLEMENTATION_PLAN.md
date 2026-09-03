# Prompt Platform Implementation Plan  
**(Grounded in the reorganized `documentations_phase_2` tree)**

**Status:** Design + folder reorganization done; **module extraction / builder not implemented yet.**  
**Companion catalog:** [`../README.md`](../README.md)  
**Architecture name:** Constitution + Compiled Playbook + Staged Library (CCP+SL)

**Update 2026-08-05:** Binding docs in `00_authority/`:
- `Verifier & Rubric Manifest Standards (Effective Immediately).txt` → M1
  constitution/platform scoring (hybrid verifier_type, honest manifest, S-08).
- `Production Rework Requirements.txt` → M1 constitution + packaging:
  content ≥**60%** / structural ≤**40%** (SUPERSEDES the Standards' original
  ≥40% floor for this wave), `high_level_prompt.md`, three log modes
  (`single`/`multi`/`multi_noplan`), multiplicative content-quality signal,
  ≥20pp SA–planned-multi gap. Weights/gates allowed **if** the manifest
  tells the truth and content share meets the Production Rework floor.

---

## 0. What changed in the library (prerequisite)

`PHASE_2/documentations_phase_2/` was reorganized from a flat dump into numbered roles:

```text
00_authority/          ← Trainer Guidelines v1.1 (wins)
01_quality_gate/       ← QD + local QG prompt
02_onboarding/         ← calls / KT
03_design_guides/      ← rubric, pipeline, mistakes, reward conflict note
04_domains/            ← PO + KR packs (sources)
05_feedback/           ← ingestion (batches, team_updates)
06_incidents_and_lessons/
07_prompt_runtime/     ← current monolith (temporary)
08_samples/            ← exemplars
09_qg_reviews/
10_prompt_platform/    ← this plan
_archive/              ← duplicates / outdated / ephemeral
```

Cursor rules were updated to the new paths. The monolith’s internal absolute paths still point at old locations — fixing those is **Milestone M2**, not blocking reading via this README.

---

## 1. Target architecture (recap)

```text
Sources (this folder’s modules, once split)
    → Prompt Builder (deterministic; no RAG)
    → COMPILED_PROMPT.md + STAGE_INDEX.md + MANIFEST.json
    → Task Creation Agent
```

| Layer | Sourced primarily from | Inline? |
|------:|------------------------|---------|
| 0 Constitution | Guidelines + integrity/scoring hard rules already in monolith | Always |
| 1 Platform | Monolith gates/phases + `03_design_guides` distillates + packaging from guidelines | Always |
| 1b Capabilities | `llm_judge` ← team_updates/judge lessons; `browsing` ← onboarding/samples | By flag |
| 2 Domain | `04_domains/<name>/` | Exactly one |
| 3 Active lessons | Distilled from `05_feedback`, `06_*`, `09_qg_reviews`, monolith LESSONS LOG | Bounded always |
| 4 Library | Full files in `00`–`03`, `08` | Stage-index only |

**Do not** RAG-select whether Integrity / Guidelines / client rejection rules load.

---

## 2. Source → module mapping (concrete)

### Layer 0 — Constitution (extract into `10_prompt_platform/sources/constitution/`)

| Module id | Extract from |
|-----------|----------------|
| `const.acceptance_criteria` | Monolith “TWO ACCEPTANCE CRITERIA” |
| `const.integrity_mandate` | Monolith INTEGRITY MANDATE |
| `const.scoring_constitution` | Monolith SCORING INTEGRITY + Guidelines § reward / package contract summary |
| `const.authority_pointer` | Always cite `00_authority/…Guidelines (2).txt` as winner |
| `const.never_omit_checklist` | Machine list of required module ids |

### Layer 1 — Platform (`sources/platform/`)

| Module id | Extract / distill from |
|-----------|----------------------|
| `plat.phase21_package_contract` | Guidelines + monolith P21 block |
| `plat.baseline_b1_b6` | Monolith + 2026-06-25 onboarding |
| `plat.client_categories` | Monolith + All Hands / presentation brief |
| `plat.autonomy_and_escalation` | Monolith |
| `plat.claim_spec_flow` | Monolith CLAIM-TIME TASK SPEC |
| `plat.gates_and_phases` | Monolith Gates 0–4, Phases 0–6 (**strip PO-only wording**) |
| `plat.difficulty_and_gap_targets` | Monolith + `rubric_scale_presentation` |
| `plat.scoring_implementation` | Monolith PHASE 2 verifier section + Guidelines |
| `plat.scoring_conflict_note` | Explicit: flat vs `new_verifier_reward_system.md` — **ask owner** |
| `plat.packaging_s01_s07` | Guidelines §6 |
| `plat.client_rejection_current` | Distill `rework-common-mistakes` + Batch-12/14 + MAS client feedback 2026-07-17 + monolith A–F |
| `plat.qd_index` | Pointer to `01_quality_gate/Quality_dimensions_phase_2.md` |
| `plat.working_conventions` | Monolith working style + PowerShell |

### Layer 1b — Capabilities

| Module | When | Source |
|--------|------|--------|
| `plat.cap.browsing` | browsing / internet | Monolith browsing lessons + samples `text_url` patterns |
| `plat.cap.llm_judge` | qualitative prose checks | Monolith judge wiring + `05_feedback/team_updates/verifier_changes` |
| `plat.cap.long_horizon` / `long_writing` / `multimodal` | categories | Monolith client categories |

### Layer 2 — Domain packs

| Pack | Source files | Work required |
|------|--------------|---------------|
| `domain.planning_operations` | `04_domains/planning_operations/Thinking in Planning-Operations…` + PO Gate 0/1 text from monolith | Extract as-is (strong) |
| `domain.knowledge_research` | `04_domains/knowledge_research/Knowledge_Research…` | **Rewrite** for Phase 2: drop oracle/fan-out; keep corpus≫context + buried claims; align with sample `08_samples/phase_2_1/…USGS…` |

Future: `code_swe`, `data_analysis`, `reasoning_math` — skeleton only until owned.

### Layer 3 — Lessons

| Artifact | Source |
|----------|--------|
| `lessons/LOG.md` | Start from monolith LESSONS LOG; append new; stop appending inside monolith after cutover |
| `lessons/ACTIVE.md` | Distill blockers from: `05_feedback/batches/*` (Batch-12/14 first), `rework-common-mistakes`, `06_incidents_*`, QG distillate from `09_qg_reviews` |

Severity: `blocker` | `high` | `normal` + `review_by` + `applies_to`.

### Layer 4 — STAGE_INDEX targets (do not inline)

| Stage hook | Path |
|------------|------|
| `authority_on_conflict` | `00_authority/…Guidelines (2).txt` |
| `gate0_onboarding_p21` | `02_onboarding/Onboarding for MAS 2.0 - 2026_07_20…` |
| `gate1_classes` | `02_onboarding/phase2_meeting_presentation_brief.ipynb` |
| `gate3_rubric` | `03_design_guides/rubric_scale_presentation.pdf` |
| `phase4_qd` | `01_quality_gate/Quality_dimensions_phase_2.md` |
| `presubmit_mistakes` | `03_design_guides/rework-common-mistakes.txt` |
| `pipeline` | `03_design_guides/Delivery Pipeline…` |
| `exemplars_p21` | `08_samples/phase_2_1/` |
| `exemplars_praised` | `08_samples/praised/` + `03_design_guides/Task Design & Grader Construction.md` |

**Not in STAGE_INDEX for every run:** full `05_feedback` dumps, full QG folder, tracker CSV body, May All Hands as binding law.

---

## 3. Builder (v1 — keep simple)

### Inputs
- `domain` (from claim / task.toml enum)
- `capabilities[]` (derived from claim: browsing, long_horizon, long_writing, multimodal, llm_judge)
- `release` (default `current`)
- `strict=true` for production seeds

### Outputs (per task compile)
```text
_trainer_artefacts/prompt_platform/
  COMPILED_PROMPT.md
  STAGE_INDEX.md
  MANIFEST.json
```

### Selection
1. All constitution + platform base  
2. Capability modules matching flags  
3. Exactly one domain pack  
4. ACTIVE lessons filtered by domain/caps under budget (**never drop blockers**)  
5. Apply `SUPERSEDES.yaml`  
6. Fail closed on conflict / missing never-omit ids  

### SUPERSEDES (seed entries to create in M1)

| Old claim | New claim | Notes |
|-----------|-----------|-------|
| Phase-1 oracle / solution | Phase 2.1 partial-oracle sample | Guidelines |
| Fail-closed LLM → reward 0.0 as content | Infra error / invalid run (monolith D update) | Confirm owner |
| MA target 0.70–0.90 | Phase 2.1 “MA also challenged” | Guidelines 2026-07-20 |
| Map-reduce / fan-out as Phase 2 pattern | Hierarchical / specialist-routing only | Onboarding + guidelines |
| Flat vs 1/2/3 weights | **Unresolved — compile must surface ASK** | Do not auto-pick |

---

## 4. Compilation order

1. Banner (release, domain, caps, manifest hash)  
2. Precedence notice (Guidelines > Constitution > Platform > Domain > Lessons)  
3. Constitution  
4. Platform base  
5. Capability modules  
6. Domain pack  
7. ACTIVE lessons  
8. STAGE_INDEX summary  

Validate: constitutional coverage, one domain, blockers fit budget, `llm_judge` ⇒ judge module present.

---

## 5. Migration milestones (incremental)

| ID | Work | Done when |
|----|------|-----------|
| **M0** | Folder reorg + README catalog | **DONE (2026-08-05)** |
| **M1** | Create `10_prompt_platform/sources/` stubs + `registry.yaml` + `SUPERSEDES.yaml` listing known conflicts; **no kickoff change** | Registry reviewed by owner (esp. flat vs weighted) |
| **M2** | Extract constitution + platform text from monolith into sources; builder emits compile for **diff-only**; fix monolith REFERENCE paths to new tree | Diff normative sections ≈ monolith |
| **M3** | Extract `domain.planning_operations`; first PO task may optionally seed from compile | One PO task built with compile seed |
| **M4** | Split LESSONS LOG → `lessons/LOG.md` + `ACTIVE.md`; ingest Batch-12/14 + rework-common-mistakes into ACTIVE | ACTIVE non-empty; Standing Duty updates ACTIVE |
| **M5** | Cutover: kickoff = compile; freeze monolith to `_archive/legacy_monolith/` | New tasks no longer paste monolith |
| **M6** | Phase-2 KR domain pack + compile(domain=knowledge-research) | Second domain without copying platform |
| **M7** | Optional: generate `.cursor/rules` from platform sources | Single source of truth |

**Non-goals until M5:** RAG, auto-LLM promotion of lessons, rewriting all samples.

---

## 6. Proposed on-disk layout for the platform (to create in M1+)

```text
10_prompt_platform/
  IMPLEMENTATION_PLAN.md          ← this file
  README.md                       ← how to compile (later)
  registry.yaml                   ← module index
  SUPERSEDES.yaml
  releases/
    CURRENT
  sources/
    constitution/
    platform/
    platform/capabilities/
    domains/
      planning_operations/
      knowledge_research/
    lessons/
      LOG.md
      ACTIVE.md
  builder/                        ← code later (not yet)
  fixtures/                       ← expected manifest checks
```

Library documents stay in `00_`–`09_`; platform **sources** are extracted *copies/distillates*, not moves of the authority PDF/TXT (authority files remain canonical in `00_`–`03_`).

---

## 7. How each folder feeds the prompt (operating model)

| Folder | Human action | Builder action |
|--------|--------------|----------------|
| `00_authority` | Update only when client ships new guidelines | Stage + constitution pointer |
| `01_quality_gate` | Update when QD changes | Stage @ Phase 4; local QG is separate prompt |
| `02_onboarding` | Rarely; historical | Stage selective; distill durable → platform |
| `03_design_guides` | Add new decks when team publishes | Distill → platform / ACTIVE; stage full deck |
| `04_domains` | Edit domain theory | Inline matching pack |
| `05_feedback` | Drop new batch files here | **Ingest ritual** → ACTIVE/platform within 48h of directive |
| `06_incidents` | Add RCA | Ingest → ACTIVE |
| `07_prompt_runtime` | Freeze after M5 | Until then: sole kickoff |
| `08_samples` | Add praised packages | STAGE exemplars only |
| `09_qg_reviews` | Drop reports | Periodic distill |
| `_archive` | No edits for runtime | Ignored by builder |

---

## 8. Future expansion

- **New domain:** add `04_domains/<x>/` guide + `sources/domains/<x>/` pack; register enum; no platform copy.  
- **New capability:** extend closed enum + one `plat.cap.*` + claim derivation.  
- **New client batch:** land in `05_feedback/batches/` → ACTIVE blockers → promote to `plat.client_rejection_current` → release bump.  
- **Versioned releases:** pin `release` in task `_trainer_artefacts` alongside judge model pin for gap validity.

---

## 9. Risks specific to *this* library

| Risk | Mitigation |
|------|------------|
| Monolith still cites old paths | M2 path rewrite; README cheat sheet already published |
| Flat vs weighted scoring docs both “current” | M1 owner decision recorded in SUPERSEDES; builder surfaces ask |
| KR guide ports Phase-1 oracle into Phase 2 | M6 rewrite gate; refuse compile if pack mentions `oracle.json` as agent deliverable |
| Feedback dumps re-inlined “to be safe” | Hard rule: `05_feedback` never in selection set; only ACTIVE |
| Sample folders huge / overlapping | Prefer `phase_2_1` + `praised`; document in STAGE_INDEX |
| Cursor rules vs sources drift | M7 generate rules from platform |

---

## 10. Immediate next actions (when you say “implement”)

1. **Owner decision:** flat 1-pt vs category 1/2/3 (or hybrid policy).  
2. **M1:** create `sources/` stubs + `registry.yaml` + `SUPERSEDES.yaml` under `10_prompt_platform/`.  
3. **Ingest pass:** write first `lessons/ACTIVE.md` from Batch-12/14 + rework-common-mistakes + SA self-parallelisation escalation.  
4. **M2:** extract constitution/platform from monolith; path-fix REFERENCE MATERIAL.  

Do **not** start builder code until M1 registry + scoring conflict decision exist.

---

## Success criteria

1. Critical rules cannot be omitted without compile failure.  
2. PO and KR share one platform; only domain packs differ.  
3. Adding a batch feedback file does not enlarge the runtime prompt until distilled.  
4. Guidelines `(2).txt` remains the conflict authority.  
5. Folder stays navigable (this tree) as the long-term library behind the Prompt OS.
