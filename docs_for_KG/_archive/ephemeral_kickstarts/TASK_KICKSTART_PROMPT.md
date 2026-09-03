# Reusable Phase 2 Task-Creation Kickstart Prompt

The task idea is MY OWN. I (the user) come up with an original idea for every
task. Do NOT pick, claim, or copy an idea from the `MAS2 Initial 50 Tasks
Tracker - llm_generated_prompts (1).csv`, and do NOT run a picker over it. The
sheet is a METHODOLOGY / PATTERN reference ONLY: study a few rows to learn HOW
the team leads generally design tasks -- how they build a multi-node DAG, how
they set DAG depth and width, how they stage a multi-stage workflow, and how
they scale/expand the corpus -- then apply that method to a UNIQUE idea of my
own. Every task must be distinct (a per-task similarity check runs): my idea
must not be the same as another idea and the task must not be similar to
another task. Prefer the planning-operations domain (this file and the
idea-design docs are written for it); move to another domain only if my idea
genuinely cannot become a strong planning-operations task.

How to reuse this file:

1. Fill in the `OWN ORIGINAL TASK IDEA` block below with MY own idea for the
   new task (a domain, persona, one-line objective, or a fuller scenario). Do
   NOT copy an idea from the sheet. If you do not have my idea yet, ask me for
   one before copying anything into an agent chat.
2. Leave everything else as-is (the enhancement principles, hard rules,
   creativity gate, and deliverables are generic and reusable across ideas).
3. Copy everything inside the fenced block into a fresh agent chat.

---

```text
You are creating a new SwarmBench PHASE 2 task end to end, PREFERRING the
planning-operations domain (fall back to another official domain only if the
seed cannot become a strong planning-operations task -- see the domain note
below). Work in the repo at d:\Abisheik\Projects\swarmbench\Tasks. Follow the
gated discipline exactly. Do not skip or compress any phase.

===========================================================================
STEP 0 - READ THESE FIRST (they are authoritative; if they conflict, the
official guidelines and the delivery-manager video win over my summary)
===========================================================================
1. d:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\documentations_phase_2\PlanningOperations_Phase2_TaskCreationPrompt.md
   (the full Phase 2 task-creation spec and all gates - the idea is MY OWN,
   original idea, never picked from the sheet; Gate 0 explains how to grow my
   idea into a unique task under one of the sub-classes)
2. d:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\documentations_phase_2\Quality_dimensions_phase_2.md
   (the 9 QD reviewer dimensions the QG grades against - build the task to pass these)
3. d:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\documentations_phase_2\Thinking in Planning-Operations — Ideas for Designing Real Tasks.txt
   (the idea-design guide: find the "many decisions x many constraints" shape
   inside MY seed; name the concrete single-agent failure it forces)
4. d:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\documentations_phase_2\LLM_gennerated_tasks_guidelines_video_transcript.md
   (the KT video: creativity lives in the coordination pattern / decomposition,
   not in model-intelligence puzzles; persona is a creativity lever; read any
   seed as a real-world operator and BUILD ON TOP of it - never paste it in)
5. Optionally skim a few rows of
   d:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\documentations_phase_2\MAS2 Initial 50 Tasks Tracker - llm_generated_prompts (1).csv
   (parse with python + the csv module, the rows are large) ONLY to LEARN the
   leads' design method -- how a query maps to a multi-node DAG, how they set
   DAG depth/width, how they stage a multi-stage workflow, and how the columns
   (query, real_sources_or_entities, expected_outputs, why_multi_agent,
   expected_single_agent_failure, hardness_strategy, grader_rationale,
   verification_shape, novelty_rationale) hang together. Do NOT pick, claim,
   or copy any row as the idea; the idea is MY OWN.
6. Reference an already-approved planning-operations task for folder shape and
   file conventions (do NOT copy its content or scenario):
   d:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\phase_2_tasks\task2\75c7756ea0454443bf455633d850e81d-SWARMBENCH-HIERARCHICAL-PLANNING-OPERATIONS-DRUG-SHORTAGE-BRIEFING
   and the approved samples under
   d:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\documentations_phase_2\approved_sample_tasks

===========================================================================
OWN ORIGINAL TASK IDEA - my own idea, build on top of it
===========================================================================
The idea comes from ME and is my OWN, original idea. Do NOT pick, claim, or
copy an idea from the tracker CSV (the sheet is a methodology reference only,
for learning how the leads shape DAG depth/width + multi-stage design). Read
my idea as a real-world user first: understand the persona, the keywords, and
the end goal, then BUILD ON TOP of it. Do NOT paste my idea verbatim into
instruction.md.

My idea (from me - fill this in before pasting into the agent chat):
- Persona / operator: <who does this on a Tuesday, and in what role>
- Domain / sub-vertical: <the industry or area>
- Objective / scenario: <the real-world work request, in my words>
- Any sources / entities I already have in mind (optional): <URLs, portals,
  APIs, registries, public PDFs, real named entities - verify, do not trust>
- Chosen sub-class(es) if I specified (optional): <one or more of Browsing /
  Long Writing / Multi-Modal / Long Horizon>

If this is blank or thin, ask me to supply/expand my own idea before Gate 0
rather than inventing a domain or pulling one from the sheet. Then, per the
spec's Gate 0 "HOW TO SHAPE MY OWN IDEA" guidance, develop 2-3 concrete
framings on top of my idea and pick the strongest (clearest natural
single-agent failure, most-real browsable sources, complex hierarchical
decomposition, cleanest boolean rubric). Confirm it is UNIQUE - not the same
as another idea and not similar to another task (a per-task similarity check
runs). Keep it in planning-operations unless it genuinely cannot be realized
there, in which case move to another official domain (reasoning-math /
code-swe / data-analysis / knowledge-research) and record why.

===========================================================================
REQUIRED ENHANCEMENTS (generic principles - apply so the single agent breaks
through COORDINATION and CONTEXT LOAD, not through raw intelligence)
===========================================================================
- Scale up until one agent cannot hold it: many similar-but-non-identical
  decisions/units (aim for a count where context degrades - often 40-70+),
  each honoring a different subset of a dense constraint corpus.
- Multi-source / multi-jurisdiction constraint surface: force reconciliation
  ACROSS rule sets / documents / sources, not within a single clause, so
  cross-unit consistency is genuinely hard.
- Several decision or "tactic" families, each with cases that must be handled
  distinctly (and, where it fits, seeded control cases that must NOT be
  mishandled after the plan is applied).
- Extra input artifacts for genuine long-horizon browsing: pinned fixtures,
  the constraint/rule documents, supporting datasets, and any real-world
  context the operator would actually consult.
- Diverse deliverable (NOT a default spreadsheet): a written report/dossier
  (docx or md), a numbered rulebook/plan, a deck/charts, or another real
  artifact the operator would hand over. Diversify format across tasks.
  Seeded/expected cases are RUBRIC checks, never an oracle.json.
- Embedded organizational rules (the single-agent breakers, stated inside
  instruction.md): the format/evidence/consistency rules that a context-
  overloaded single agent will drop - e.g. every asserted fact cites its
  exact source clause/URL, no two decisions may contradict, missing info must
  be flagged, a fixed citation format is used throughout.
- Complex hierarchical / specialist-routed decomposition, depth >= 2 (aim
  higher), distinct roles differentiated by RESPONSIBILITY, not sharded by
  count: lead/orchestrator -> domain specialists (each owning one area end to
  end) -> reviewer/reconciler -> reducer -> separate writer/producer roles.
  No map-reduce, no flat fan-out of identical workers.

Name in writing WHY the single agent naturally fails for MY specific idea
(constraints fade past ~decision 10; late decisions go generic; cross-unit
reasoning collapses), and how the multi-agent decomposition recovers it.

===========================================================================
HARD PHASE 2 RULES (from the spec + the video) - enforce all of them
===========================================================================
- The two acceptance criteria: (1) the single-vs-multi gap is REAL, arising
  from genuine scale/breadth/coordination, never from a scoring trick, hidden
  restriction, engineered timeout, or hallucinating judge; (2) the task is
  creative and real-world, not a Phase 1 reskin or a synthetic exercise.
- The idea is MY OWN, original idea. Do not pick, claim, or copy an idea from
  the tracker CSV (study it only to learn the leads' design method). It must be
  UNIQUE - not the same as another idea and not similar to another task (a
  per-task similarity check runs). Land it under at least one of the four
  sub-classes. Prefer planning-operations; fall back to another official domain
  only if my idea cannot become a strong planning-ops task.
- NO ORACLE. Grade with a boolean RUBRIC of 15-25 checklist items, each worth
  exactly one point, reward = items_passed / total_items, clamped to [0,1]. No
  weightage, no tiers, no multipliers. Do not ship a solution/ folder or load
  an oracle.json in the verifier.
- Load-bearing browsing / external retrieval through real public sources.
  Pin/archive volatile sources only where a live fetch is genuinely unreliable.
- Hierarchical / specialist-routed decomposition only. No map-reduce, no flat
  fan-out of identical workers.
- Diverse real deliverable artifacts, not JSON, and specifically not a default
  spreadsheet.
- instruction.md must read like a real human operator handing off the job:
  first person, conversational, no Markdown # / ## headings, no bulleted spec
  sheet. Embed the rules and constraints in prose.
- Do NOT use em dashes or en dashes anywhere (so the task does not read as
  LLM-generated). Use plain hyphens or rewrite the sentence.
- Coordination complexity is the goal, not model-intelligence puzzles. The
  decomposition.yaml should be genuinely complex.

===========================================================================
CREATIVITY GATE - CHECK BEFORE BUILDING FILES
===========================================================================
Per the delivery-manager video, the crafted creative idea must be claimed in
the sheet and approved by the QA lead BEFORE task-file creation. Ask me whether
the QA lead has already approved the creativity for this idea.
- If NOT yet approved: help me finalize the crafted idea write-up for the sheet
  (built on my seed) and STOP. Do not create task files yet.
- If approved: proceed to full task creation below.

===========================================================================
DELIVERABLES TO PRODUCE (once creativity is approved)
===========================================================================
Scaffold a new task folder under
d:\Abisheik\Projects\swarmbench\Tasks\PHASE_2\phase_2_tasks\ with a fresh
hex-id + SWARMBENCH-<COORDINATION>-<DOMAIN>-... name (e.g.
SWARMBENCH-HIERARCHICAL-PLANNING-OPERATIONS-... for the default domain; use
the actual chosen domain in the slug if a fallback was approved), containing:
- instruction.md (human first-person prompt, embedded rules, no headings, no
  em/en dashes)
- task.toml (metadata, human_solving_hours_estimate, why_multi_agent, timeout,
  dag_width, sub-agent count consistent with the decomposition)
- decomposition.yaml (hierarchical structure, depth >= 2, distinct roles)
- tests/judge.py (15-25 boolean rubric + CitationGrader-style source-grounding
  checks; deterministic anti-templating where relevant; no oracle)
- the __trainer_artefacts folder with static_checks.py, selfcheck_judge.py
  (build GOOD and PARTIAL fixtures that make the rubric discriminate), and
  RUN_COMMANDS.md
- any pinned source fixtures needed for reliable runs

Then validate: run static_checks and selfcheck_judge until green and until the
GOOD fixture clearly outscores the PARTIAL fixture. Watch for full
scriptability (if one script can loop and pass, the gap will collapse - the
embedded per-case judgment and cross-source reconciliation must be genuinely
non-scriptable) and for agent timeouts (keep the load coordinatable; use
incremental writes; recommend a fresh --job-name per run so Harbor does not
resume a failed trial).

Start by reading the sources in STEP 0, then confirm MY own idea in the
OWN ORIGINAL TASK IDEA block (ask me for it if blank; do not pick or copy an
idea from the sheet) and the creativity-gate status with me before creating
any files.
```
