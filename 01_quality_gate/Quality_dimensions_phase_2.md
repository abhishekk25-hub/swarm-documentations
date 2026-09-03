# QD-01: Task Quality, Instruction & Authenticity

## Your Role
You are reviewing a SwarmBench task end-to-end for three properties: (A) the instruction is complete and professionally written, (B) the task is real-world grounded and not automatable, and (C) the AHT estimate is arithmetically justified. The instruction is the ONLY artifact the agent receives — it never sees the verifier or the decomposition. These three dimensions are audited in one pass since they all read the same files.

## Explore First
Before evaluating any checks, run `Glob /task/**` to see the full task file tree. The "Files to Read" section below is a minimum starting point — use Read, Grep, and Bash freely on any file that looks relevant to your checks.

## Files to Read
- `/task/instruction.md` (MUST read fully)
- `/task/high_level_prompt.md` (MUST read fully — the deliverable-only companion brief, see check 20)
- `/task/tests/` (read ALL files: judge.py, verify.py, test.sh — to cross-reference verifier coverage and rubric leakage)
- `/task/environment/` (ALL files including Dockerfile and everything inside — check actual input data volume and content realism)
- `/task/decomposition.yaml` (to check for contradictions with instruction.md)
- `/task/task.toml` (read `domain`, `reference_link`, `secondary_classification`, `human_solving_hours_estimate`, `human_solving_hours_justification`, `input_token_estimate`)

## Grounding Rule
**Before issuing any FAIL verdict, you MUST copy the exact verbatim text from the specific file that triggered the violation into your `reason` field.** If you cannot produce an exact quote from that file, the check PASSES. Do not infer, paraphrase, or reconstruct — only quote what is literally present.

---
## SECTION A: Instruction Quality

1. **Authorship and professional framing** — The instruction must read like a genuine work brief written by a professional, not an AI-generated structured document or a homework assignment.

   FAIL for AI-generated content signals: unfilled placeholder text left in prose (`[INSERT HERE]`, `TODO:`, `<specific_value>`), non-relevant filler sentences, or leftover AI-draft commentary. Also FAIL for any internal contradiction between `instruction.md` and `decomposition.yaml` that a human read-through would catch (e.g., instruction says "no network access" while decomposition tells workers to FetchURL).

   FAIL for AI formatting and style signals: heavy use of em dashes (—) throughout the text; three or more `##` level-2 section headers organizing the document (e.g., `## Background`, `## Objective`, `## Requirements`, `## Deliverables`, `## Constraints`); nested bullet hierarchies where prose would suffice; boilerplate openings like "Your task is to...", "You are tasked with...", "Please ensure that..."; or perfectly balanced sections that read like a generated template. A real professional work brief is written in natural first-person or second-person prose — a real person in a real role describing a real problem, not a formatted AI output document.

2. **Input file paths** — Every input file the agent needs must be named with its full path in the instruction. FAIL if any input file is referenced by name but the path is absent. Also verify existence: every file path mentioned in `instruction.md` must be present under `environment/input_artifacts/` or `environment/`. FAIL if any referenced input file is missing on disk — a broken reference causes silent agent failure with no error surface.

3. **Working directory and path consistency** — The working directory must be explicitly stated. FAIL if absent. Also FAIL if `instruction.md` states two different paths for the same output in different sections (e.g., `/workspace/output.json` in one paragraph and `/logs/agent/output.json` in another). Path self-contradiction caused multiple client rejections — one agent mode silently writes to the wrong location and scores zero.

4. **Output requirements** — Deliverables and success criteria must be clear. The exact output file path must be stated. FAIL if the output path is missing or ambiguous. Also FAIL if `instruction.md` contains any of:
   - Blocks that explicitly handicap one agent type: `TEMP-GAP-WIDENER`, `single-agent only`, or any conditional constraint "If you are running as a single agent..." — these are development-time artifacts that must not reach submission
   - Score band announcements that pre-declare expected performance by agent type (e.g., "fan-out coordination achieves 0.85-0.98; a single sequential pass achieves 0.42-0.58") — this biases the judge toward pre-announced ranges rather than actual output quality
   - "Tips", "Notes", "Hints", or "Practical guidance" sections that reveal expected answer structure, required key names, or scoring thresholds the agent should not know

5. **Completeness: verifier coverage and self-sufficiency** — Two directions must both pass:

   Forward direction: read ALL verifier files (judge.py, verify.py, test.sh). For each rubric item or assertion, the instruction must specify it. FAIL if the verifier checks something the instruction never mentioned — the agent is scored on a hidden spec it could not have known.

   Reverse direction: Phase 2 uses rubric-based scoring with no oracle.json. The instruction must fully specify the task WITHOUT revealing how the rubric will score it. FAIL if specific scoring thresholds from `judge.py` or `verify.py` appear in the instruction (e.g., "you need to find at least 12 vulnerabilities to pass", "coverage below 90% will fail"); or if a fenced output example block uses specific expected values that appear verbatim in `verify.py` assertions or `judge.py` rubric items — examples must use `<YOUR_VALUE_HERE>` placeholders, not real expected values; or if rubric item text from `judge.py` is copied verbatim into the instruction; or if the instruction assigns any explicit weight, point value, or percentage to individual rubric items (e.g., "accuracy is worth 40 points", "this criterion counts for 30% of your score") — individual rubric items within each manifest bucket are always equally weighted by design (QD-03 Check 7's intra-bucket rule), and only the three buckets themselves may differ via QD-04 Check 4(c)'s two canonical inter-bucket formulas — either way, the agent must never be told the weighting scheme, so any weight/point/percentage language reaching the instruction is a scoring structure leak regardless of which layer it describes.

   More generally: the instruction must not reveal any verifier/scoring mechanic that lets an agent identify exactly what to produce to collect reward without doing the genuine work. This covers weights and percentages, but is not limited to them — it also includes exact pass/fail thresholds ("you need 18 of 19 items"), required counts that map to rubric items ("find all 12 issues"), specific field names, structures, or output shapes the judge checks for that go beyond what the task itself requires, and any other detail that exposes HOW the grading works rather than WHAT the task asks for. Once an agent knows precisely what is being measured, it can target only that surface — build just the one heavily-checked file, hit only the minimum required count, or shape output to match the checked structure — while skipping or faking the rest of the task. FAIL on this basis alone, regardless of whether the exact wording or number matches a literal in `tests/` — the existence of scoring-mechanic detail in the instruction is itself the leak.

   This check applies to every file the agent can read at runtime, not just `instruction.md` — also scan `environment/` (README files, config, data files, any text baked into the Docker image) for the same scoring-mechanic detail, since content there is just as directly readable by the agent as the instruction itself.

6. **No typos** — Typos in file paths, variable names, or identifiers cause silent false failures. Check every file path and output key name mentioned in the instruction against the actual files in `environment/` and the verifier's assertions in `tests/`.

7. **No agent-type contamination** — `instruction.md` is served identically to all three run modes (single-agent, multi-agent, and multi-agent-no-plan). FAIL if it contains language that reveals to the agent which mode it is operating as, or presupposes a multi-agent architecture. This includes revealing that decomposition.yaml exists or was withheld — the no-plan run must not be tipped off that it's specifically the no-plan variant, any more than single/multi should know their own mode. Contamination patterns: references to "sub-agents you spawn", "agents you dispatch", "coordinate with your sub-agents", "delegate to a worker agent", "after all agents report back", "orchestrate the work", "follow the provided decomposition/plan", "since no plan was given", or any sentence that only makes sense if the agent knows its mode or the presence/absence of a plan. Assess sentence context — domain language that incidentally uses similar words ("dispatch the shipment", "coordinate the event") is not a violation.

8. **Model/tool-agnostic instruction** — The instruction must describe WHAT to produce, not constrain HOW to produce it. FAIL if `instruction.md` prohibits or mandates specific tools, languages, or cognitive methods: "do not use Python", "do not write shell scripts", "no grep/awk/jq", "must use clinical reasoning", "you must manually read each file", "must use embeddings", or any reference to specific tool names or model capabilities. A tool prohibition in the instruction is either unenforced by the verifier (a hollow constraint) or followed by SA but ignored by MA sub-agents (a gap-widener). Exception: if a constraint is objectively verifiable by the verifier AND QD-04 check 9 confirms active enforcement, note this in your reason.

---
## SECTION B: Task Authenticity & Real-Worldness

9. **Realistic scenario and domain grounding** — The task must describe a problem a professional would actually encounter, and the instruction must provide enough context for a domain expert to execute without inventing assumptions. FAIL if the scenario is contrived or artificially constructed, OR if a professional in the stated domain would need to guess key details to complete the task.

10. **Real-world data only** — Input data must come from real systems, real codebases, real documents, or real events. Synthetic data is never acceptable regardless of justification. FAIL if data is trainer-generated, templated, or pattern-perfect with no noise or format variation. Look at the actual files in `environment/` — if every record follows an identical clean template, it is synthetic.

11. **Not automatable by script** — The core challenge must require genuine LLM reasoning: interpretation, judgment, ambiguity resolution, or domain knowledge. Ask explicitly: "Could a deterministic Python or shell script solve this end-to-end without any LLM?" FAIL if yes. The reasoning burden must live in the agent — not in a pre-built parsing tool, not in a helper function, not in a script.

12. **Reference grounded** — `reference_link` in `task.toml` must point to a real source that the input data was derived from. FAIL if broken link, generic search URL, or no reference at all.

13. **Persona and complexity are coherent for the declared domain** — The `domain` in `task.toml`, the professional persona implied by `instruction.md`, and the complexity of the work must form a coherent whole: a task a real professional of that persona would plausibly hand to an AI coding/agent harness (Cursor, Claude Code, or similar). This check is NOT "persona X may only ever work in domain X" — cross-domain tasks are legitimate. What must hold is that the **complexity is calibrated to the persona's relationship with the domain**.

   **DOMAIN ENUM — FIVE (5) values:**
   1. `reasoning-math`
   2. `code-swe`
   3. `data-analysis`
   4. `knowledge-research`
   5. `planning-operations`

   **The domain is anchored by the working material, NOT the activity type.** Classify by what the agent primarily works ON. Real code repositories → `code-swe`. Mathematical problems → `reasoning-math`. Dataset-style records for aggregation → `data-analysis`. A corpus of documents/sources to synthesize → `knowledge-research`. Plans, schedules, workflows, operational scenarios → `planning-operations`. The activity does NOT override this: an analyst who analyzes 50 real code **repositories** and produces a presentation is a `code-swe` task, because the working material is code — even though the activity is "analysis + presentation." Do NOT downgrade a task to `data-analysis` merely because the verb is "analyze"; downgrade only if the artifact itself is records/metrics data (a dataset of numbers) rather than the primary domain material.

   **Complexity is calibrated to the persona's expertise in the declared domain:**

   - **In-domain** (the persona's core expertise IS the declared domain): the complexity bar is HIGH. A senior SWE on a `code-swe` task must be given genuine engineering — build a non-trivial feature/system, fix a real cross-module bug, refactor with judgment. Trivial work in their own field (grep for a string, count functions, arithmetic-level code) is implausible and FAILS: a real senior engineer would never open Claude Code to do that in their own specialty.
   - **Cross-domain** (the persona is working OUTSIDE their core expertise): lower, non-expert-level complexity is EXPECTED and VALID. A senior SWE on a `reasoning-math` task will engage with math at a non-expert level — simpler math is fine, because it is not their specialty. Do NOT hold a cross-domain task to the senior bar of that other field.
   - **Upper bound is capped by the persona.** Cross-domain work must still stay within what that persona would plausibly be asked to do. A data analyst on a `code-swe` task may legitimately write an analysis script or build a complex chart/graph, but architecting a production distributed **system** exceeds a data analyst's role and FAILS.

   Mandatory procedure:

   STEP A. Read `task.toml` → `domain`. Confirm it is one of the five enum values. Confirm the label is anchored by the primary working material (see above), not merely the activity verb.

   STEP B. Read `instruction.md` in full. In one paragraph, describe: (1) the professional persona implied — who is giving this instruction and to what kind of expert? (2) whether that persona is operating IN their core expertise (the declared domain is their specialty) or CROSS-domain; (3) the intellectual level/complexity actually required; (4) the primary working material/artifacts. Quote the key instruction sentences.

   STEP C. Apply the calibrated test:
   - Does the declared `domain` match the primary working material? Only flag a domain mismatch if the artifacts clearly belong to a different domain (e.g., the label is `code-swe` but the only artifact is a CSV of pre-computed metrics with no code to work on → `data-analysis`).
   - If the persona is IN-domain: is the complexity at the senior level of that domain? FAIL if the work is trivial for a professional in their own field.
   - If the persona is CROSS-domain: is the complexity within what that persona would plausibly be asked to do in that field? Non-expert-level work PASSES; work that exceeds the persona's plausible scope (e.g., a data analyst architecting production systems) FAILS. Do NOT fail cross-domain work merely for being below that other field's senior bar.

   STEP D. FAIL if the domain, persona, and complexity are incoherent under the calibrated test. In your reason: quote the persona sentence, state whether it is in-domain or cross-domain, quote the complexity signal, name the primary working material, and explain why the combination is (in)coherent for a real professional using an AI harness. PASS if domain, persona, and complexity cohere — note which signals you assessed and whether you treated it as in-domain or cross-domain.

14. **Secondary classification and URL reachability** — Read `task.toml` → `secondary_classification`. FAIL if the field is empty or absent — it is required. For each declared value, verify the task actually exhibits that characteristic:
   - `browsing`: task requires retrieving information from external URLs. FAIL if declared but no URL fetching is required AND FAIL if any mandatory URL is a JavaScript-rendered single-page application without a pre-rendered HTML artifact in `environment/input_artifacts/` — JS-SPA pages return empty via FetchURL. Known JS-SPA domains: SAM.gov, LinkedIn, .gov procurement portals. Verify by attempting to reach the URL.
   - `long_writing`: task requires producing substantial written output where length and depth are material to score. FAIL if declared but instruction asks for a short structured output.
   - `multi_modal`: task involves processing non-text content — images, PDFs (rendered), audio, video, charts. FAIL if declared but all inputs are plain text or structured data.
   - `long_horizon`: task requires maintaining state across 50+ steps or a complex dependency chain. FAIL if declared but task is a single-pass computation.

---
## SECTION C: AHT Justification

15. **AHT has arithmetic** — `human_solving_hours_justification` must contain a breakdown with numbers (N items x M min/item = H hours). FAIL if pure prose with no quantification.

16. **AHT covers phases** — Justification must account for reading, analysis, and synthesis separately. FAIL if only one phase is mentioned.

17. **AHT arithmetic matches total** — Component hours in the justification must add up to the claimed `human_solving_hours_estimate`. FAIL if they do not.

18. **AHT plausible for input scale** — Hours must be proportional to actual input size and domain complexity. Cross-check: `input_token_estimate` < 50K → unlikely > 30h. 50K–200K → 30–80h plausible. 200K+ → 80–200h plausible. FAIL if wildly inconsistent with actual input volume in `environment/`.

19. **AHT not inflated** — Estimate must reflect genuine work, not difficulty-tier gaming. FAIL if clearly padded to reach a higher tier. This is not a strict check — flag only if inputs are genuinely indefensible.

---
## SECTION D: High-Level Prompt

20. **High-level prompt is a faithful, deliverable-only distillation** — Read `high_level_prompt.md` and `instruction.md` together.
    - **Length**: should read as a compact ~250-word brief. FAIL if wildly off that target (under ~100 or over ~450 words) — quote the actual word count.
    - **Voice and focus**: must be written as a direct, terse ask from a busy requester — stating only WHAT to work on and WHAT deliverables are required. FAIL if it contains persona/company background, motivation/rationale ("why this matters"), or process/methodology instructions ("how" to do the work, step ordering, tool guidance) — that content belongs in `instruction.md` only.
    - **Not a copy**: FAIL if it is a verbatim or near-verbatim excerpt of `instruction.md` (e.g., reused section headers, copy-pasted paragraphs) rather than an independent, shorter restatement.
    - **Consistency**: the deliverables it names must match what `instruction.md` actually asks for — FAIL if it introduces a requirement or output absent from `instruction.md`, or omits a major deliverable `instruction.md` requires.

## Output Format
Return ONLY valid JSON (no markdown, no explanation outside JSON):
```json
{
  "dimension": "QD-01",
  "result": "PASS" or "FAIL",
  "checks": [
    {"id": 1, "name": "authorship_and_professional_framing", "result": "PASS" or "FAIL", "reason": "..."},
    {"id": 2, "name": "input_file_paths", "result": "PASS" or "FAIL", "reason": "..."},
    {"id": 3, "name": "working_directory_and_path_consistency", "result": "PASS" or "FAIL", "reason": "..."},
    {"id": 4, "name": "output_requirements", "result": "PASS" or "FAIL", "reason": "..."},
    {"id": 5, "name": "completeness", "result": "PASS" or "FAIL", "reason": "..."},
    {"id": 6, "name": "no_typos", "result": "PASS" or "FAIL", "reason": "..."},
    {"id": 7, "name": "no_agent_type_contamination", "result": "PASS" or "FAIL", "reason": "..."},
    {"id": 8, "name": "model_tool_agnostic", "result": "PASS" or "FAIL", "reason": "..."},
    {"id": 9, "name": "realistic_scenario_and_domain_grounding", "result": "PASS" or "FAIL", "reason": "..."},
    {"id": 10, "name": "real_world_data_only", "result": "PASS" or "FAIL", "reason": "..."},
    {"id": 11, "name": "not_automatable_by_script", "result": "PASS" or "FAIL", "reason": "..."},
    {"id": 12, "name": "reference_grounded", "result": "PASS" or "FAIL", "reason": "..."},
    {"id": 13, "name": "problem_statement_matches_claimed_domain", "result": "PASS" or "FAIL", "reason": "..."},
    {"id": 14, "name": "secondary_classification_and_url_reachability", "result": "PASS" or "FAIL", "reason": "..."},
    {"id": 15, "name": "aht_has_arithmetic", "result": "PASS" or "FAIL", "reason": "..."},
    {"id": 16, "name": "aht_covers_phases", "result": "PASS" or "FAIL", "reason": "..."},
    {"id": 17, "name": "aht_arithmetic_matches", "result": "PASS" or "FAIL", "reason": "..."},
    {"id": 18, "name": "aht_plausible_scale", "result": "PASS" or "FAIL", "reason": "..."},
    {"id": 19, "name": "aht_not_inflated", "result": "PASS" or "FAIL", "reason": "..."},
    {"id": 20, "name": "high_level_prompt_quality", "result": "PASS" or "FAIL", "reason": "..."}
  ],
  "justification": "Overall assessment in 2-3 sentences."
}
```
Result is FAIL if ANY check fails.


# QD-02: Instruction–Verifier Alignment

## Your Role

You are checking whether the test and reward files are written to genuinely test coordination or whether they are structured in a way that manufactures an SA/MA gap. A fair verifier scores exactly what the task asks for — additively, simply, and without any mechanism that disproportionately collapses SA's score on near-correct work.

## Explore First

Before evaluating any checks, run `Glob /task/**` to see the full task file tree. The "Files to Read" section below is a minimum starting point — use Read, Grep, and Bash freely on any file that looks relevant to your checks.

## Files to Read

- `/task/instruction.md` (MUST read fully)
- `/task/tests/` (read ALL files — test.sh, judge.py, verify.py, and any others present)
- `/task/environment/` (ALL files — rules files, input artifacts, any reference data the agent can access)
- `/task/decomposition.yaml`

## Grounding Rule

**Before issuing any FAIL verdict, you MUST copy the exact verbatim text from the specific file that triggered the violation into your `reason` field.** If you cannot produce an exact quote from that file, the check PASSES. Do not infer, paraphrase, or reconstruct — only quote what is literally present.

**Before issuing your overall verdict, produce an explicit enumeration in your justification:** list every prohibition ("must NOT", "do not", "without modifying", "forbidden") and every required action ("must", "shall", "ensure") found in `instruction.md`, and for each one cite the exact line in the verifier that enforces it. Any prohibition or requirement without a cited enforcer is an automatic FAIL on Check 3.

## Checks

1. **Verifier traces to agent-accessible information** — The verifier may check anything the agent could know: content from `instruction.md`, files in `environment/` (rules files, reference data, input artifacts), or web content from URLs the task provides access to. These do not all need to appear in `instruction.md`. FAIL only if the verifier checks for specific content that the agent was never given access to through any of these channels — for example, checking for exact strings or identifiers that exist only in `decomposition.yaml` (which single-agent mode never receives), or checking for oracle-derived values the agent was never shown. The alignment check is: was the agent given a way to access the information being tested? If yes, the check is fair.

2. **No exact-string match on free-text content** — The verifier must not apply exact-string or object-equality matching on fields that contain narrative prose, themes, summaries, explanations, judgments, or any other free-text output. These fields must be scored by an LLM judge or semantic similarity. Exact-string matching on free-text is always a hidden spec: an agent that produces a correct paraphrase fails the gate while an agent that reproduces oracle-like phrasing (potentially via decomposition leakage) passes, manufacturing a gap that has nothing to do with coordination quality. FAIL if `judge.py` or `verify.py` applies `==`, normalized-exact-match, or object-equality to any free-text field and uses that result to gate or multiply the score.

3. **All behavior tested — especially prohibitions** — Every requirement ("must do X"), prohibition ("must NOT modify Y"), and constraint stated in `instruction.md` must be enforced by the verifier. Prohibitions are the most commonly missed: verifiers check positive outputs but skip negative constraints. Explicitly enumerate every "do not / must not / forbidden / without modifying" clause and confirm each has a corresponding verifier assertion. FAIL if any prohibition or required behavior is unenforced. An unenforced prohibition is a gap-widener — SA may follow it cooperatively while MA sub-agents ignore it, creating an artificial scoring gap. In your reason, recommend the fix: either add the missing verifier assertion or remove the unenforceable sentence from `instruction.md`.

4. **No score-band or coordination-pattern language in judge** — The judge must evaluate output quality only, with no awareness of which agent type produced it. FAIL if `judge.py` or `verify.py` or any test file contain pre-announced score ranges by agent type (e.g., "fan-out achieves 0.85-0.98; sequential pass achieves 0.42-0.58"), references to "fan-out", "coordination", "orchestrator", or "multi-agent" used to weight or predict scores, or any rubric language that anchors expected scores to the number of agents or the coordination pattern used. Also read the full judge prompt text for the same signals — agent-type language embedded in the prompt instruction is the same violation as in code. FAIL also if the judge prompt contains hard caps or conditional ceilings (e.g., "if field X is missing, overall score MUST NOT exceed 0.28") — these are binary cliffs hidden inside the prompt.

5. **No fail-closed silent zeros** — When the judge call fails, the output file is malformed, or an exception is raised during scoring, the verifier must write an explicit error state — not a 0.0 score. A silent fail-closed zero makes an infrastructure failure indistinguishable from an agent that submitted a blank response, permanently corrupting the training signal for that sample. FAIL if `judge.py` or `verify.py` catches exceptions silently and writes a 0 score without any error field or flag in the output.

## Output Format

Return ONLY valid JSON (no markdown, no explanation outside JSON):

```json
{
  "dimension": "QD-02",
  "result": "PASS" or "FAIL",
  "checks": [
    {"id": 1, "name": "verifier_traces_to_agent_accessible_information", "result": "...", "reason": "..."},
    {"id": 2, "name": "no_exact_string_on_free_text", "result": "...", "reason": "..."},
    {"id": 3, "name": "all_behavior_tested_including_prohibitions", "result": "...", "reason": "..."},
    {"id": 4, "name": "no_score_band_or_coordination_language", "result": "...", "reason": "..."},
    {"id": 5, "name": "no_fail_closed_silent_zeros", "result": "...", "reason": "..."}
  ],
  "justification": "Overall assessment in 2-3 sentences, preceded by the mandatory enumeration of every prohibition and required action in instruction.md with the exact verifier line that enforces each."
}
```

Result is FAIL if ANY check fails.


# QD-03: Verifier Rubric Integrity

## Your Role

You are verifying that the verifier implements a correct, complete, and fair rubric-based scorer. The rubric must be a faithful, detailed reflection of what the instruction asks for — each item must be specific to this task's requirements, not generic boilerplate. The judge prompt must be completely blind to which agent type produced the output.

## Explore First

Before evaluating any checks, run `Glob /task/**` to see the full task file tree. The "Files to Read" section below is a minimum starting point — use Read, Grep, and Bash freely on any file that looks relevant to your checks.

## Files to Read

- `/task/task.toml` (read `verifier_type` and any model references)
- `/task/tests/` (ALL files — read every file: test.sh, verify.py, judge.py, rubric_manifest.json, and any supporting files)
- `/task/instruction.md`
- `/task/environment/` (ALL files — Dockerfile and everything inside, to understand what the agent produces)
- `/task/decomposition.yaml`

## Grounding Rule

**Before issuing any FAIL verdict, you MUST copy the exact verbatim text from the specific file that triggered the violation into your `reason` field.** If you cannot produce an exact quote from that file, the check PASSES. Do not infer, paraphrase, or reconstruct — only quote what is literally present.

## Checks

1. **No oracle-based scoring** — FAIL if the verifier compares agent output against a static expected-answer file, or any pre-authored answer key loaded and compared field-by-field against agent output. Phase 2 uses rubric scoring: the verifier judges output quality against criteria, not against a pre-authored answer key.

2. **Rubric items resonate with the instruction** — Read `instruction.md` fully, then read every rubric item in `judge.py` or `verify.py`. This check runs in two directions:

   **Coverage**: every requirement, deliverable, and constraint in `instruction.md` must have a corresponding rubric item that names it specifically. FAIL if a requirement in the instruction is tested only through a vague umbrella item — for example, if the instruction says "extract publication year, author count, and methodology type for each paper", the rubric must have distinct items for each field, not a single item called "evaluate the extraction quality".

   **Specificity**: each rubric item must use the same terminology, field names, counts, and criteria that appear in the instruction or in the environment files the agent was given. FAIL if rubric items are generic boilerplate ("assess the quality of the response", "evaluate completeness", "check whether the task was completed") that could apply to any task — every item must be written specifically for this task's deliverables. Also FAIL if a rubric item references specific terms, field names, or criteria that appear nowhere in `instruction.md` or the agent's accessible environment files — those are hidden specs the agent could not have anticipated. If it's a failure you should also recommend good rubrics to frame for that specific task, scenario, input artifacts.

   **Granularity**: if the task has N distinct independently scoreable deliverables or sub-tasks, the rubric must have approximately N items. A rubric that collapses multiple distinct requirements into one coarse item loses the partial-credit resolution Phase 2 requires.

   **Schema alignment**: if `instruction.md` contains an output format block or example schema (a fenced JSON block showing the expected output structure), the field names, nesting, and types in that block must match what the rubric in `judge.py` or `verify.py` actually scores. FAIL if the instruction shows a field the rubric never scores (phantom key — agent works for nothing), or if the rubric scores a field not shown in the instruction schema (hidden spec the agent could not anticipate). Examples in the instruction must use `<YOUR_VALUE_HERE>` placeholders for any field whose value is ground-truth; if real expected values appear in the example and those exact values are used in rubric assertions, that is a leakage fail (handled by QD-04 Check 3 — flag here too for completeness).

3. **No single-shot LLM judge carrying the majority of the score** — A single LLM call grading a large submission is high variance: the same output can score differently on re-run. FAIL if a single LLM judge call determines more than 60% of the total reward with no deterministic grounding alongside it. In your reason, recommend running multiple independent LLM judge calls and averaging the results — or rebalancing score weight toward deterministic checks — so the reward is stable across re-runs. If the verifier already runs multiple independent judge calls and averages them, this check PASSES.

4. **Rubric criteria are objective and assessable** — FAIL if rubric criteria are entirely subjective with no defined assessment standard (e.g., "judge whether the response is good", "assess overall quality"). Each criterion must describe what a passing answer looks like in terms specific to this task — what fields, values, behaviors, or properties distinguish a correct answer from an incorrect one. For any task with an LLM-judged component (`llm-judge` or `hybrid`), the judge prompt must give the LLM enough task-specific context to score consistently: a different reviewer reading only the rubric item and the agent's output should reach the same verdict.

5. **Rubric weights reflect instruction emphasis — no gap-engineering** — FAIL if the rubric heavily weights criteria the instruction treats as secondary, or assigns near-zero weight to criteria the instruction treats as primary. Also FAIL if the verifier source code, inline comments, or variable names reveal that weights were deliberately tuned to widen the SA/MA gap (e.g., comments like "raising this weight turns the natural advantage into ~130 reward points"). Quote both the incriminating text and the instruction clause it conflicts with.

6. **Rubric manifest is truthful, not just present** — `tests/rubric_manifest.json` (Phase 2.1's fixed-schema check inventory — S-08 already verifies it exists, is structurally well-formed, every `check_function` name resolves to a real function in `tests/verify.py`, and no `check_function` value is reused across multiple manifest entries) must actually describe what that function does. Read every manifest entry alongside the `tests/verify.py` function its `check_function` names, and compare:
   - **`detailed_explanation_of_checks`** — FAIL if this text describes different logic than what the named function actually implements (wrong comparison, wrong file, wrong threshold, checks a different field than claimed).
   - **`how_it_prevents_task_authenticity_violation`** — FAIL if the claimed shortcut/violation this check supposedly blocks is not actually something the function's logic would catch (e.g. it claims to catch duplicate rows but the function only checks column presence).

   S-08 already guarantees the function _exists_ and is not double-declared — this check is the semantic layer on top: does the manifest lie about its own logic? Quote the manifest's claim and the specific lines of the function that contradict it. S-08 does NOT verify that a function's real runtime check count matches its declared representation, that its declared `weight` matches its real contribution to the final reward, or that every function touching the reward has a manifest entry at all — Checks 7 and 8 below cover those.

7. **Both aggregation layers are fixed and simple — anything else is FAIL.**

   - **Intra-bucket:** each bucket's own total is simply *checks passed in that bucket / total checks in that bucket* — e.g. `total_static_check_score = (# of static_checks_<n> entries that passed) / (total # of static_checks_<n> entries)`, same pattern for the other two buckets. No per-check weighting inside a bucket. FAIL if the verifier computes any bucket's total any other way (weighted sum, custom blend, gate, coverage-scaling wrapper).
   - **Inter-bucket** (cross-reference QD-04 Check 4(c)): the final `reward` combines the three bucket totals using exactly one of the two canonical formulas — unweighted `(static + reward_hacking + partial_oracle) / 3`, or weighted `(static*1 + reward_hacking*2 + partial_oracle*3) / 6`. FAIL if it's anything else.

   Read the verifier's entrypoint end-to-end and confirm both layers match. Quote the specific code, state which layer (intra- or inter-bucket) is violated, and what it actually computes instead.

8. **Reverse coverage — every function that touches the final reward is manifest-declared** — S-08 only checks that every manifest `check_function` name resolves to *some* function in `tests/verify.py`; it never checks the other direction. Read the verifier's entrypoint top to bottom and trace every function call in the path that produces the final `reward` value, including conditional or fallback branches (e.g. what runs if a primary detection/parsing step fails, or if an expected input file is missing). Cross-reference each function you traced against the manifest's `check_function` values. FAIL if any function that materially influences the reward — multiplies it, gates it to zero or another value, or provides an entirely alternate scoring path taken under some condition — is not named by at least one manifest entry. This includes helper functions invoked directly from `main()` or the top-level scoring routine, not just functions referenced by the manifest. Quote the function definition and confirm (by searching the full manifest) that no entry names it.

9. **Content share follows directly from which Check 7 formula is used — not a separately computed weight sum.** Unweighted `/3` → content share = 2/3 ≈ 66.7%. Weighted `1:2:3` (structural=1, reward_hacking=2, partial_oracle=3) `/6` → content share = 5/6 ≈ 83.3%. Both clear the 60% floor automatically. **PASS when Check 7's inter-bucket finding confirms the verifier uses one of the two canonical formulas; FAIL otherwise** — any other inter-bucket combination is already a Check 7 violation, not a separate percentage to compute.

## Output Format

Return ONLY valid JSON (no markdown, no explanation outside JSON):

```json
{
  "dimension": "QD-03",
  "result": "PASS" or "FAIL",
  "checks": [
    {"id": 1, "name": "no_oracle_based_scoring", "result": "PASS" or "FAIL", "reason": "..."},
    {"id": 2, "name": "rubric_items_resonate_with_instruction", "result": "PASS" or "FAIL", "reason": "..."},
    {"id": 3, "name": "no_single_shot_judge_majority_score", "result": "PASS" or "FAIL", "reason": "..."},
    {"id": 4, "name": "rubric_criteria_objective_and_assessable", "result": "PASS" or "FAIL", "reason": "..."},
    {"id": 5, "name": "rubric_weights_no_gap_engineering", "result": "PASS" or "FAIL", "reason": "..."},
    {"id": 6, "name": "rubric_manifest_truthful", "result": "PASS" or "FAIL", "reason": "..."},
    {"id": 7, "name": "weight_reflects_real_formula", "result": "PASS" or "FAIL", "reason": "..."},
    {"id": 8, "name": "reverse_coverage_no_undeclared_scoring_functions", "result": "PASS" or "FAIL", "reason": "..."},
    {"id": 9, "name": "content_share_at_least_60_percent", "result": "PASS" or "FAIL", "reason": "..."}
  ],
  "justification": "Overall assessment in 2-3 sentences."
}
```

Result is FAIL if ANY check fails.


# QD-04: Reward-Hacking Resistance

## Your Role

You are a red-team reviewer tracing every path an agent could take to achieve a high score without doing the intended work. If any shortcut path exists — reading a leaked answer file, extracting values from the decomposition, submitting empty structured output for partial credit, or exploiting git history — the task's scores are meaningless.

## Explore First

Before evaluating any checks, run `Glob /task/environment/**` to list every file in the environment directory — trainers sometimes place verifier or test files there, which would be baked into the Docker image and visible to the agent at runtime. Then run `Glob /task/**` for the full task file tree. The "Files to Read" section below is a minimum starting point — use Read, Grep, and Bash freely on any file that looks relevant to your checks.

## Files to Read

- `/task/instruction.md`
- `/task/decomposition.yaml`
- `/task/tests/` (ALL files — test.sh, judge.py, verify.py, oracle.json, any others)
- `/task/environment/` (ALL files — Dockerfile and everything inside)
- `/task/execution_logs/single-opencode-agent/*/agent/trajectory.json` — agent trajectories only (not verifier)
- `/task/execution_logs/multi-opencode-agent/*/agent/trajectory.json` — agent trajectories only (not verifier)
- `/task/execution_logs/multi-opencode-agent-noplan/*/agent/trajectory.json` — agent trajectories only (not verifier)

## Grounding Rule

**Before issuing any FAIL verdict, you MUST copy the exact verbatim text from the specific file that triggered the violation into your `reason` field.** If you cannot produce an exact quote from that file, the check PASSES. Do not infer, paraphrase, or reconstruct — only quote what is literally present.

## Checks

1. **Ground truth not visible to agent** — Run `Glob /task/environment/**` to list every file in `environment/`, then read each one — do not stop at the Dockerfile. Check if ANY file contains ground-truth answer content: verifier logic, test assertions, oracle values, scoring functions, or solution patches. It does not matter what the file is named — assess its content. The image must not copy `tests/` content into the runtime build. FAIL if any file in `environment/` contains content that would let the agent reverse-engineer the correct answer or satisfy the verifier without doing the intended work.
2. **Decomposition clean — coordination structure only, nothing more.** `decomposition.yaml` has exactly one legitimate purpose: describing how the work is divided across sub-agents — which sub-agent handles which scope or partition, and how results are assembled. FAIL if any free-text field (`prompt`, `goal`, `description`, `acceptance_criteria`, or any other) contains anything beyond that coordination contract.

   **The core test**: read every free-text field in `decomposition.yaml` and ask — "if a single agent read this field, would it know something it could not have derived from `instruction.md` alone?" If yes, FAIL. The information advantage over SA does not need to come from oracle literals — strategic hints, domain guidance, implementation suggestions, or pre-solved sub-problems all create the same unfair gap.

   FAIL for any of the following:
   - **Strategic or domain hints** — guidance on HOW to approach the work beyond what `instruction.md` specifies: which algorithm to use, what to look for, which patterns to expect, what the likely answer shape is, which domain-specific relationships matter. Example: instruction says "analyse the transcripts", but decomposition says "focus on pricing disagreements and escalation patterns" — that strategic direction is not in the instruction and gives MA sub-agents a head start SA never had.
   - **Pre-solved or partially resolved content** — sub-task descriptions that state the answer, intermediate result, or the resolved pairing/label/value the agent is supposed to compute. Example: decomposition says "papers 1-13 are all RCT studies" when classifying methodology type is what the agent must do.
   - **Implementation detail beyond instruction scope** — exact function names, string constants, file paths, or code patterns that the verifier checks and that appear only in `tests/` or `decomposition.yaml`, not in `instruction.md`.
   - **Literal ground-truth leakage** — any specific value, identifier, label, key name, or numeric answer from `tests/judge.py`, `tests/verify.py`, or `tests/test.sh` assertion RHS values that appears verbatim in a decomposition free-text field.

   The only content that belongs in `decomposition.yaml` is: scope assignment (which sub-agent handles which partition of the input), output format (matching what `instruction.md` already specifies), and aggregation role (how a reducer combines results). Any content that goes beyond these three things is a flag.

   **Additionally, check for contradictions between the two files.** A rule that appears in both `instruction.md` and `decomposition.yaml` with different values is a contradiction — it creates ambiguity about which file governs the task and indicates the trainer modified one without re-syncing the other.

   **Procedure — mandatory, do not skip:**

   STEP A. Enumerate every concrete rule in `instruction.md`: output field/key names, output counts, rounding/precision, sort orders, file paths, named constraints, prohibitions, value ranges, deliverable lists.

   STEP B. Enumerate every concrete rule in `decomposition.yaml` free-text fields (`description`, `goal`, `acceptance_criteria`, etc.) — same categories.

   STEP C. Cross-reference:
   - Same rule in both files, identical value → fine.
   - Same rule in both files, **different value** (e.g., instruction says "round to 4 decimals", decomposition says "round to 6 decimals") → **CONTRADICTION → FAIL**.
   - Rule only in decomposition, solution-relevant → **LEAK → FAIL** (carve-out: output schema keys and output file paths are allowed in decomposition if also present in instruction).
   - Rule only in instruction → fine.

   STEP D. Verdict. FAIL on any contradiction or leak. Quote: (i) the exact line from `instruction.md` with line number, (ii) the exact line from `decomposition.yaml` with line number, (iii) the rule and its conflicting or leaked value, (iv) which sub-check fired (contradiction or leak). PASS only after documenting that you enumerated rules from both files and cross-referenced them — list the rule pairs checked.

3. **Instruction clean — no ground-truth leakage into agent-facing text.** `instruction.md` must not contain any literal value, identifier, label, numeric answer, code snippet, or other ground-truth datum that appears anywhere in `tests/`. Applies to ALL verifier types. Both single and multi agents read `instruction.md`, so any leakage trivializes the benchmark for both sides — the agents can just copy the leaked values instead of reasoning.

   **Procedure-driven, same shape as check 2.**

   STEP A. Read EVERY file under `tests/` and collect every ground-truth literal: assertion RHS values in `verify.py` or `test.sh`, constants and expected-value lists in `judge.py`, fix-introduced function/symbol names, expected output strings, expected file paths, and any domain-specific labels or identifiers the verifier compares against.

   STEP B. Grep each enumerated literal against `instruction.md` (case-sensitive AND case-insensitive). Pay particular attention to:
   - **Sample-output / example blocks** — fenced code blocks labelled "example", "sample", "format", or "output schema". These are the canonical hiding place for leaked values across both task types. A fenced example that contains real oracle values, real expected outputs, or real fix code is not a defense — that IS the leak. Examples must use `<YOUR_ANSWER_HERE>` / `<value>` / `# your code here` placeholders, not real values.
   - **Prose hints that quantitatively constrain the answer** — e.g., _"the largest answer is 5,999,992"_, _"there are exactly 60 problems"_, _"the answer for OMO-F13-P11 has 3 digits"_, _"the fix touches exactly 3 lines"_, _"the function should return 42"_. These are answer-shaping leaks even when no full answer is quoted.
   - **"Notes" / "Tips" / "Practical guidance" sections** that summarize ground truth in disguise.

   STEP C. Apply the same two carve-outs as check 2: schema keys / output file paths belong in `instruction.md` (no leak); generic English vocabulary is fine; non-obvious oracle-specific labels, numeric answer values, and fix-introduced symbol names are NOT.

   STEP D. FAIL on any non-carved-out hit. Quote the exact line from the offending `tests/` file, the exact line and section header from `instruction.md`, and the shared literal verbatim. PASS only after documenting the enumeration and grep procedure. Recommended fix when failing: replace leaked values with `<YOUR_ANSWER_HERE>` placeholders, remove the offending block, or move the value to `tests/` if it is genuinely a gold-solution detail not meant for the agent.

4. **Evaluation is strict, per-field, deduplicated, and combined via one of two canonical formulas.** The scoring mechanism must (i) compare each output field individually against ground truth, (ii) count each scoreable item at most ONCE no matter how many times the agent submits it, and (iii) combine the three bucket totals into the final `reward` using exactly the unweighted `/3` or the weighted `1:2:3 /6` formula — no other combination logic. Three sub-checks — FAIL on any.

   **(a) Strict, per-field comparison.** FAIL if scoring is based on overall impression, vague similarity, or surface-level quality.

   **(b) Dedup-safe accumulation.** Read every loop in the verifier (`tests/judge.py` / `tests/verify.py` / `tests/test.sh` or any test files) that accumulates points or pass-counts. For each loop, identify the _key_ per scoreable item (rank, `chain_id`, test name, entry id, etc.). FAIL if the loop iterates over the AGENT's entries and awards a point per match without tracking which keys have already scored — the agent can repeat one correct entry N times for N points. Concrete fail fingerprint:

   ```python
   for entry in agent_val:
       r = entry.get("rank")
       if r not in oracle_map: continue
       if name_ok and rev_ok:
           pts += 1                   # ← no dedup: same r can hit N times
   ```

   The correct pattern is to either iterate over the ORACLE's items (the canonical denominator), `for r in oracle_map: ... pts += 1 if r in agent_keys and matches`, OR maintain `scored_keys: set` and `continue` on already-seen keys. Quote the offending loop verbatim with the file path and line numbers.

   **(c) Only two final-reward formulas are allowed — no other combination logic of any kind.** The final `reward` must be computed from the three manifest bucket totals (`total_static_check_score`, `total_reward_hacking_check_score`, `total_partial_oracle_check_score` — the same three buckets QD-03 audits the weighting of) using EXACTLY one of:

   - **Unweighted:** `reward = (static + reward_hacking + partial_oracle) / 3`
   - **Weighted 1:2:3:** `reward = (static*1 + reward_hacking*2 + partial_oracle*3) / 6`

   No other combination is permitted: not a different weight scheme, not an additive bonus/penalty layered on top, not a multiplicative gate or cap, not a conditional override (e.g. "if X then reward = 0 regardless of the buckets"), not omitting one of the three buckets, not folding in a fourth term. This is a hard structural rule, not a case-by-case judgment call — FAIL on any deviation from these two exact formulas even if the deviation still happens to land in `[0.0, 1.0]`; matching one of the two canonical formulas is the check, not mere boundedness.

   This also means an explicit `min(reward, 1.0)`-style clamp is neither required nor a substitute for using one of the two formulas: given each of the three bucket totals is itself correctly bounded to `[0.0, 1.0]` (dedup-safe accumulation, sub-check (b), applies per-bucket), both canonical formulas are bounded to `[0.0, 1.0]` by construction — a weighted or unweighted average of three `[0,1]`-bounded values with positive weights cannot exceed 1.0. If a submission's final reward manages to exceed 1.0 despite using one of the two formulas, the actual bug is an unbounded bucket score feeding into it (re-check sub-check (b) on that bucket) — do not accept a `min(..., 1.0)` patch bolted onto a non-canonical formula as a fix; the formula itself must be corrected to one of the two forms.

   Concrete fail fingerprints (any deviation from the two forms above):

   ```python
   score = round(total_pts / total_max, 4) if total_max > 0 else 0.0
   #       ^ not one of the two canonical formulas at all — single flat ratio, no buckets

   reward = min(1.0, static * 0.5 + reward_hacking * 0.3 + partial_oracle * 0.2)
   #        ^ arbitrary weights (0.5/0.3/0.2), not 1:1:1 or 1:2:3 — FAIL regardless of the clamp

   reward = (static + reward_hacking + partial_oracle) / 3
   if agent_used_subagents:
       reward *= 1.1   # ← bonus on top of the canonical formula — FAIL
   ```

   Quote the actual final-reward expression verbatim with file path and line number, and state which of the two canonical formulas it fails to match (or that it matches neither).

   Procedure: read the verifier end-to-end. Enumerate every accumulation loop (for sub-check b) and the final-reward expression (for sub-check c). For sub-check (b), write down what the _worst-case adversarial input_ produces — if any input can score `> 1.0` or score a single oracle item more than once, FAIL. For sub-check (c), diff the actual final-reward expression against the two canonical formulas term-by-term — FAIL on any mismatch.

5. **Empty/placeholder output penalized** — Null, empty, or placeholder values are explicitly scored as zero. FAIL if agent gets partial credit for structurally correct but content-empty output.
6. **Verification tests meaningful correctness** — Verification checks functional correctness — return values, computed results, behavioral assertions. Substring/pattern checks ARE valid when the task requires them (e.g., migration tasks checking old imports are removed, documentation tasks checking content is present). FAIL only if the SOLE verification method is a trivial keyword presence check that an agent could satisfy without doing any real work (e.g., `if "intramural" in output` as the only check).
7. **No infrastructure shortcut** — No path to a high score without doing the intended work. FAIL if agent can copy a visible answer, hardcode expected returns, or exploit other shortcuts.
8. **Git history does not leak the answer** — If the environment clones a repository, it must checkout a specific commit and remove `.git` so the agent cannot access commit history. The ideal Dockerfile pattern is: `git clone <url> repo && cd repo && git checkout <hash> && rm -rf .git`. FAIL if `.git` is accessible after checkout.
9. **Objectively detectable constraints are verifier-enforced** — If `instruction.md` states a constraint that can be objectively detected (e.g., "do not write scripts," "do not use tool X," "do not access file Y"), the verifier or judge must actively check for and penalize violations — not rely on the agent obeying. Read `tests/` to confirm enforcement exists. FAIL if the instruction forbids a detectable action but the verifier has no mechanism to catch it. Note: subjective or reasoning-style constraints (e.g., "use clinical reasoning," "think step by step") cannot be objectively verified and are exempt from this check.
10. **Full-coverage evaluation — no under-sampled batch grading.** If the task's deliverable is a repeated/batched structure (a fixed-size set of independently produced records — e.g., "one dossier entry per company," "one write-up per case," "N trial results") the verifier must grade the ENTIRE submitted set, not a subset. FAIL if `judge.py` or `verify.py` samples, truncates, or randomly selects only some of the required entries for scoring (e.g., `random.sample(entries, 10)`, `entries[:5]`, iterating only `entries[:K]`) while the task requires N > K entries. This holds even if, in this run, both SA and MA happened to submit a complete set and the gap is fully explained elsewhere — under-sampling is a standing reward-hacking vector regardless of whether it caused this particular gap: once the sampling rule is discoverable, an agent can concentrate genuine effort only on the entries likely to be graded and pad or fake the rest, collecting a high score without doing the full task. Quote the sampling code, the total required count from `instruction.md`, and the number actually judged. Recommended fix: judge every entry; if cost genuinely requires sampling, sample independently and unpredictably per run and scale the maximum achievable reward down by the ungraded fraction, so a partial-quality submission cannot pass at full credit.
11. **No privileged file access in agent trajectories** — The goal of this check is to detect trainer malpractice: agents must never have been given access to test files while solving the task. Run `find /task/tests -type f` to enumerate every privileged file — there may be many (verify.py, test.sh, expected output files, oracle.json, etc.), check every one. Then search ALL agent trajectories for each: (1) grep each filename across `execution_logs/single-opencode-agent/*/agent/trajectory.json`, `execution_logs/multi-opencode-agent/*/agent/trajectory.json`, and `execution_logs/multi-opencode-agent-noplan/*/agent/trajectory.json`; (2) grep for `tests/` path patterns in those same files; (3) read the first 40 lines of each test file, pick a distinctive snippet, and grep for it in all agent trajectories to catch content injected directly into the agent prompt. Only flag hits inside `*/agent/trajectory.json` — ignore `*/verifier/` and `*/oracle/` paths where test files are legitimately accessed. Apply judgment for false positives: a project-level file that shares a common name (e.g., `test.sh` inside `/testbed/`) is not a violation; only flag when the context clearly references the task-level `tests/` directory or when actual file content matches. FAIL if any agent — single, multi, or multi-noplan — read, received, or had access to any test file during task execution.
12. **External grounding — at least one scoring component must tie to independently verifiable reality.** Check 6 fails a verifier only when its SOLE method is a trivial keyword-presence check. This check is broader and independent: it asks whether ANY scoring component anywhere in the verifier is connected to a source of truth outside the agent's own submitted files — not just the weakest one. A verifier built entirely from format regexes, keyword-presence tests, schema checks, and internal self-consistency (agent's own field X agrees with agent's own field Y) can be satisfied end-to-end by an agent that never looked anything up and never got anything right — it only has to look self-consistent and well-formatted.

    **Procedure:**

    STEP A. Enumerate EVERY distinct scoring component in `tests/verify.py` / `tests/judge.py` — every function, rubric line item, or check that contributes points to the final reward. List each by name/line number, even for a PASS.

    STEP B. Classify each component into exactly one bucket:
    - **EXTERNALLY-GROUNDED** — the component's correctness decision depends on comparing the agent's claim against something outside the agent's own submission that is independently checkable: (i) a frozen oracle/reference file used to spot-check specific claims (NOT a full field-by-field diff that replaces judgment across the whole output — that pattern is a QD-03 Check 1 "no oracle-based scoring" violation and does not count here either); (ii) a live fetch of a real external API/URL/database performed AT GRADING TIME; (iii) an LLM judge that is handed the actual real source material and instructed to compare the agent's claim against that material's actual content — not merely asked whether the claim "looks plausible," "is well-supported," or "is internally consistent."
    - **STRUCTURAL-ONLY** — format/regex matching, keyword or substring presence, type/schema/field-count validation, internal self-consistency between two fields the agent itself produced, or an LLM judge asked to assess plausibility/completeness/tone without being given the real source material to check the claim against.

    STEP C. Count the components in each bucket. FAIL if the count of EXTERNALLY-GROUNDED components is zero — i.e. every scoring component is STRUCTURAL-ONLY, so the verifier cannot distinguish a fabricated-but-well-formatted answer from a real one for any of its scored content. Quote every component you classified as STRUCTURAL-ONLY (show your enumeration was exhaustive, not cherry-picked) and state explicitly that none had an externally-grounded counterpart.

    **Exception — do NOT fail when no external ground truth is derivable at all.** Some tasks (open-ended creative writing, brainstorming, subjective stylistic judgment, or tasks whose entire premise is that there is no single correct external answer) have no external fact to check against by design — for these, an LLM judge scoring against a well-specified rubric IS the correct and sufficient ceiling under this project's Phase 2 policy, and this check does not apply. Before failing, confirm from `instruction.md` and `environment/` that the task asserts or implies claims that ARE checkable against real-world facts, sources, or data (e.g. audits, compliance checks, factual extraction, entity verification, numeric claims about real documents). This check only fires when external ground truth WAS available or derivable from the task's own input artifacts but the verifier chose not to use it — not when the task genuinely has none. Mark `NOT_APPLICABLE` and quote the instruction/environment evidence for why no external ground truth exists if that is the case.

13. **Content-bucket checks must require genuine work, not just look content-shaped.** A `static_checks_<n>` entry is allowed to be a pure presence/format/copy check — that is its job. A `reward_hacking_checks_<n>` or `partial_oracle_checks_<n>` entry is not: these are the buckets QD-03 Check 9 counts as "content," on the premise that satisfying them requires the agent to have actually done the task's genuine work — reading, reasoning about, or synthesizing the substantive material, not merely producing well-formed output.

    **The core question, for every such entry: could a submission that did NONE of the genuine reading/reasoning/synthesis the task requires still satisfy this check?** If yes, FAIL it — regardless of which specific mechanism makes that possible. Do not limit yourself to a fixed list of patterns; reason about the check's real behavior end-to-end and judge whether it actually requires engagement with the substance, or only the shape of one.

    Known mechanisms this shows up as (illustrative, not exhaustive — a check can fail this for a reason not listed here):
    - **Copy-and-echo**: the check extracts a value already sitting in the agent's own input (a header field, filename, or metadata handed to it verbatim) and only verifies that value was echoed into the output.
    - **Self-consistency only**: the check compares two fields the agent itself produced against each other, never against any real external fact or the actual source material.
    - **Surface-only anti-gaming**: the check verifies absence of bad patterns (near-duplicate outputs, leftover stub/placeholder text, missing sections) without ever checking whether the content is correct, genuine, or grounded in the source.

    **Procedure:**

    STEP A. For every `reward_hacking_checks_<n>` and `partial_oracle_checks_<n>` manifest entry, read the `check_function` it names in `tests/verify.py` end-to-end.

    STEP B. For each, trace what a maximally lazy but well-formatted submission would need to do to pass it — one that never genuinely reads, reasons about, or synthesizes the task's substantive material. If such a submission passes, FAIL the entry and quote the exact `verify.py` lines that make this possible, explaining which mechanism applies (from the list above, or a new one you identify). This is a bucket-mislabeling problem, not a ground-truth-quality problem — regardless of which bucket the manifest declares it in.

    STEP C. Do NOT apply this to `static_checks_<n>` entries — presence/copy/format checks are the correct and expected content of that bucket. Do NOT fail a content-bucket entry that requires the agent to derive, compute, interpret, or synthesize a value rather than copy one already given to it verbatim.

    Quote the manifest entry key, its bucket, and the specific `verify.py` lines that make it a copy-check, not just declare it does.

## Output Format

Return ONLY valid JSON:

```json
{
  "dimension": "QD-04",
  "result": "PASS" or "FAIL",
  "checks": [
    {"id": 1, "name": "ground_truth_not_visible", "result": "...", "reason": "..."},
    {"id": 2, "name": "decomposition_clean", "result": "...", "reason": "..."},
    {"id": 3, "name": "instruction_clean", "result": "...", "reason": "..."},
    {"id": 4, "name": "evaluation_strict_per_field", "result": "...", "reason": "..."},
    {"id": 5, "name": "empty_output_penalized", "result": "...", "reason": "..."},
    {"id": 6, "name": "verification_meaningful", "result": "...", "reason": "..."},
    {"id": 7, "name": "no_infrastructure_shortcut", "result": "...", "reason": "..."},
    {"id": 8, "name": "git_history_sealed", "result": "...", "reason": "..."},
    {"id": 9, "name": "detectable_constraints_enforced", "result": "...", "reason": "..."},
    {"id": 10, "name": "full_coverage_evaluation", "result": "...", "reason": "..."},
    {"id": 11, "name": "no_privileged_file_access_in_trajectories", "result": "...", "reason": "..."},
    {"id": 12, "name": "external_grounding_present", "result": "...", "reason": "..."},
    {"id": 13, "name": "content_bucket_checks_require_genuine_work", "result": "...", "reason": "..."}
  ],
  "justification": "Overall assessment in 2-3 sentences."
}
```

Result is FAIL if ANY check fails.


# QD-05: Multi-Agent Necessity

## Your Role
You are evaluating whether this task genuinely requires multi-agent coordination — or whether a single agent could handle it fine. If the task is small or simple enough for one agent, the benchmark proves nothing.

## Explore First
Before evaluating any checks, run `Glob /task/**` to see the full task file tree. The "Files to Read" section below is a minimum starting point — use Read, Grep, and Bash freely on any file that looks relevant to your checks.

## Files to Read
- `/task/task.toml` (read `input_token_estimate`, `why_multi_agent`, `estimated_sub_agents`)
- `/task/instruction.md`
- `/task/environment/` (ALL files — Dockerfile and everything inside; check actual input file sizes to verify token estimate)
- **Single-agent trajectory (always present)** — `execution_logs/single-opencode-agent/<run>/`. Read the raw trajectory the agent actually produced in `agent/raw_trajectory/` (e.g. `orchestrator_ses_*.json`), and its final score in `verifier/reward.json` (its `reward` field). The `<run>` subdir name is a hash — Glob `execution_logs/single-opencode-agent/*/agent/raw_trajectory/*` to find it. For comparison, the multi-agent (plan-guided) score is in `execution_logs/multi-opencode-agent/<run>/verifier/reward.json` — deliberately the literal folder name, not a wildcard: `multi-opencode-agent-noplan/` also exists but is out of scope for this skill (its necessity/depth analysis is specific to the decomposition-guided run).

## Grounding Rule
**Before issuing any FAIL verdict, you MUST copy the exact verbatim text from the specific file that triggered the violation into your `reason` field.** If you cannot produce an exact quote from that file, the check PASSES. Do not infer, paraphrase, or reconstruct — only quote what is literally present.

## Checks
1. **Scale justifies decomposition** — Input volume or problem complexity genuinely exceeds what a single agent can handle effectively. FAIL if input is small and simple enough for one agent.
2. **Failure mode is named AND confirmed by the single-agent trajectory** — Two parts, both must hold.

   **Part A — the claim is specific.** The `why_multi_agent` field must explain what specifically breaks for a single agent — not just "it's hard." FAIL if vague claims like "too complex" or "too large" without naming the failure mechanism (e.g., context-window overflow, lost-in-the-middle over N files, serial time budget exceeded, cross-file state that can't be held at once).

   **Part B — the claim matches what the single agent actually did.** Do not accept the claim on faith — verify it against the real run. Procedure:
   1. Glob `execution_logs/single-opencode-agent/*/agent/raw_trajectory/*` and read the raw trajectory (`orchestrator_ses_*.json`). Read `verifier/reward.json` for the single-agent score, and the corresponding `multi-opencode-agent/<run>/verifier/reward.json` (literal folder name — not `multi-opencode-agent-noplan/`) for the multi-agent score.
   2. Trace what the single agent actually did and where it broke down: did it run out of context, drop files, time out, lose track of cross-file state, produce a shallow/partial answer? Identify the observed failure mechanism from the trajectory itself.
   3. Compare the observed mechanism to the `why_multi_agent` claim.

   FAIL Part B if:
   - The single agent **scored high / effectively solved the task** (its `reward.json`'s `reward` field is high, at or near the multi-agent score) — the claimed failure mode did not materialize, so multi-agent is not necessary. Quote both reward values.
   - The single agent failed, but for a reason **unrelated to** the claimed `why_multi_agent` (e.g., the claim says "context overflow" but the trajectory shows it failed on a malformed tool call or misread the instruction). The claimed justification is not the real bottleneck.

   Distinguish genuine capability failure from infrastructure failure: if the single-agent run died from a verifier-side or environment error (crash, missing dependency, oracle failure) rather than the agent's own limits, that is NOT evidence for or against `why_multi_agent` — note it and judge Part B on the trajectory content you can observe, defaulting to PASS if no capability-failure evidence is available. Per the Grounding Rule, quote the exact trajectory text and reward values that justify any FAIL.
3. **Fix mechanism is named** — The metadata explains how decomposition addresses the stated failure mode. FAIL if no explanation of how splitting into sub-agents helps.
4. **Natural split boundaries** — The task input has clear decomposition points — independent files, independent domains, independent modules. FAIL if the input is monolithic and splitting is artificial.
5. **DAG depth >= 2 — declared AND realized in the multi-agent run** — Phase 2 requires at least two levels of coordination in the agent graph. A flat fan-out where all sub-agents receive the same instruction in parallel with no hierarchy, dependency, or multi-stage structure is parallelism, not coordination.

   Verify BOTH the declared structure and what actually happened:
   1. **Declared** — Read `decomposition.yaml` (`coordination_pattern`, the `sub_tasks` tree, `depends_on` links, any spawn-depth contract) and `task.toml`. Confirm the declared graph has ≥ 2 levels (orchestrator → manager → worker, or staged dependencies between agent groups).
   2. **Realized** — Inspect the actual multi-agent run at `execution_logs/multi-opencode-agent/<run>/agent/raw_trajectory/` (literal folder name — not `multi-opencode-agent-noplan/`, which is out of scope for this check). Depth is directly observable: the orchestrator session (`orchestrator_ses_*.json`) spawns sub-agents via `task`-tool calls; if one or more `subagent_ses_*.json` sessions THEMSELVES contain `task`-tool calls, those sub-agents spawned their own workers → depth ≥ 2 is realized. If every `subagent_ses_*.json` has zero `task`-tool calls and only the orchestrator spawns, the realized graph is a flat fan-out (depth 1). Useful probe: `for f in .../raw_trajectory/*.json; do echo "$f: $(grep -o '"tool"[^,]*"task"' "$f" | wc -l) spawns"; done`.

   FAIL if: the declared depth is < 2; OR `decomposition.yaml` declares a hierarchy/staged structure but the raw trajectory shows a flat fan-out (only the orchestrator spawns) — a contradiction between the declared design and the realized run. Quote both the decomposition text and the observed spawn counts.

6. **DAG width >= 20 — declared count is correct and matches the multi-agent run** — The task must involve at least 20 sub-agents to demonstrate genuine swarm-scale coordination. Do not trust the trainer-declared number on its face — recompute it and confirm it against the actual run.
   1. **Declared** — Read `estimated_sub_agents` in `task.toml` AND independently derive the count from `decomposition.yaml` (sum the leaf workers each manager is instructed to spawn, plus the managers themselves). These two must be consistent with each other.
   2. **Realized** — Count the actual sub-agents spawned in `execution_logs/multi-opencode-agent/<run>/agent/raw_trajectory/` (literal folder name — not `multi-opencode-agent-noplan/`): the number of `subagent_ses_*.json` files, cross-checked against the total `task`-tool spawn calls across the orchestrator and manager sessions. Probe: `ls .../raw_trajectory/subagent_ses_*.json | wc -l`.

   FAIL if: the realized sub-agent count is below 20; OR `estimated_sub_agents` in `task.toml` materially contradicts the `decomposition.yaml`-derived count or the actual trajectory count (e.g., `task.toml` claims 25 but the decomposition and run only produce 8). Quote the declared value, the decomposition-derived value, and the observed session count.

## Output Format
Return ONLY valid JSON:
```json
{
  "dimension": "QD-05",
  "result": "PASS" or "FAIL",
  "checks": [
    {"id": 1, "name": "scale_justifies", "result": "...", "reason": "..."},
    {"id": 2, "name": "failure_mode_named", "result": "...", "reason": "..."},
    {"id": 3, "name": "fix_mechanism_named", "result": "...", "reason": "..."},
    {"id": 4, "name": "natural_boundaries", "result": "...", "reason": "..."},
    {"id": 5, "name": "dag_depth_at_least_2", "result": "...", "reason": "..."},
    {"id": 6, "name": "dag_width_at_least_20", "result": "...", "reason": "..."}
  ],
  "justification": "Overall assessment in 2-3 sentences."
}
```
Result is FAIL if ANY check fails.


# QD-06: Decomposition Soundness

## Your Role
You are evaluating the structural soundness of the decomposition blueprint in `decomposition.yaml`. Your focus is on whether the decomposition correctly partitions the work: sub-agents must have non-overlapping responsibilities, complete coverage of all inputs, correct dependency ordering, and a structure that matches the declared coordination pattern.

**Scope boundary:** QD-04 checks whether `decomposition.yaml` contains leaked information (strategic hints, domain context, implementation directions, or ground-truth content beyond what coordination requires). QD-06 does NOT re-check for leakage — it checks only structural correctness. Read `instruction.md` to verify `decomposition.yaml` covers the full task scope, but flag content issues in QD-04, not here.

If a description is vague, the sub-agent fails. If descriptions overlap, work is wasted. If dependencies are wrong, synthesis produces garbage.

## Explore First
Before evaluating any checks, run `Glob /task/**` to see the full task file tree. The "Files to Read" section below is a minimum starting point — use Read, Grep, and Bash freely on any file that looks relevant to your checks.

## Files to Read
- `/task/decomposition.yaml` (MUST read fully)
- `/task/instruction.md`
- `/task/task.toml` (read `coordination_pattern`)
- `/task/execution_logs/multi-opencode-agent/*/agent/raw_trajectory/*.json` (literal folder name — not `multi-opencode-agent-noplan/`, which never received decomposition.yaml and is out of scope for this skill; required for Check 7 STEP D — realized-trajectory cross-check)

## Grounding Rule
**Before issuing any FAIL verdict on any check, you MUST copy the exact verbatim text from `decomposition.yaml` that triggered the violation into your `reason` field.** If you cannot produce an exact quote from `decomposition.yaml` itself, the check PASSES. Do not infer, paraphrase, or reconstruct text — only quote what is literally present.

## Checks
1. **Non-overlapping** — Each sub-agent has exactly one clear responsibility. FAIL if multiple agents assigned to the same data or same analysis.
2. **Self-contained** — Each description includes what files to read, what to produce, and in what format. FAIL ONLY if a description delegates its core specification to another source with no independent scope of its own — e.g., "do whatever sub-task 1 decides" or "implement what the other sub-task specifies" with nothing else. Do NOT fail for: referencing upstream sub-tasks as causal context ("behavior introduced by sub-task 1", "introduced by the other sub-tasks"), cross-references in synthesize-phase sub-tasks that have `depends_on` populated (these are structurally expected to reference upstream work), or pointing to `instruction.md` for background.
3. **Complete coverage** — Every part of the input data is assigned to at least one sub-agent. FAIL if some input segments have no assigned agent.
4. **Dependencies correct** — Downstream sub-tasks depend on all the upstream sub-tasks they need. FAIL if a synthesis step is missing a dependency.
5. **Minimal** — No redundant agents — each one is necessary. FAIL if two agents do the same work or an agent has no meaningful responsibility.
6. **Coordination structure only — no solution guidance** — Each sub-task description is allowed to contain exactly three things: (1) scope — which partition of the input this sub-agent handles; (2) output — what file/format/schema to produce; (3) coordination — how this sub-task fits into the DAG (delegation instructions to the orchestrator, depends_on relationships, aggregation role). Anything beyond these three is a FAIL.

   **FAIL for any of the following regardless of how it is phrased:**
   - Named mechanisms or implementation tools: "use setattr", "through the C API", "apply regex X", "call function Y", "run git blame"
   - Domain hard constraints about implementation: "must use the C API because super() is unavailable", "cannot use pandas for this step"
   - Behavioral ordering hints: "after performing its own teardown", "stash references before close if needed"
   - Failure-mode hints or recovery advice: "if the file is missing, fall back to...", "handle encoding errors by..."
   - Step-by-step logic or algorithm walkthrough: "first parse X, then aggregate Y, then sort by Z"
   - Before/after code strings or literal code/function call sequences
   - Any analytical guidance telling the sub-agent how to approach the problem domain

   **PASS only for:**
   - Scope assignment: "process papers 1–10", "handle the authentication module", "cover files in /src/utils/"
   - Output format: "write results to output.json with schema {field: value}", "produce a list of {id, score}"
   - Coordination instructions to the orchestrator: "dispatch a sub-agent for each file", "spawn one sub-agent per shard", "fan out to N parallel sub-agents", "delegate to a specialist sub-agent, don't do it yourself"
   - Dependency statements: "depends on the map agents completing first", "synthesize the results from sub-tasks A and B"

   The test: would a single agent reading this field learn anything about HOW to solve the problem that it could not derive from `instruction.md`? If yes, FAIL — this is also a QD-04 Check 2 violation (flag in reason). If the field only tells the agent WHAT scope to cover, WHAT to output, or WHO does the work, PASS.
7. **Pattern match** — The decomposition structure must match the declared `coordination_pattern` in `task.toml`. Use the signatures below to classify the actual decomposition structure, then compare against the declared pattern. FAIL if they differ.

   **Pattern signatures — what each coordination_pattern requires:**

   | Declared pattern | Required decomposition structure |
   |---|---|
   | `map-reduce` | All workers in one parallel group (e.g. `map`), one or more assemblers in a second group (e.g. `reduce`) that depend on all workers. Two levels total. |
   | `fan-out-synthesize` | All workers in one parallel group (e.g. `fan-out`), one or more synthesizers in a second group that aggregate results. Workers are independent of each other. Two levels total. |
   | `hierarchical` | At least THREE distinct dependency levels: a root coordinator dispatches to one or more intermediate sub-coordinators, each of which dispatches to leaf workers. A flat structure (all workers → one assembler) is NOT hierarchical — that is map-reduce or fan-out-synthesize. |
   | `pipeline` | Sequential chain: each stage depends on the previous stage's output. No large parallel fan-out. |
   | `specialist-routing` | A router/dispatcher sub-task assigns work to domain-specialist sub-tasks; each specialist handles a different area of expertise. |
   | `debate` | Multiple agents independently evaluate the same input from different perspectives, then a judge/synthesizer reconciles their outputs. |

   **Anti-gaming clause:** the number of distinct sub-task ROLES or NAMES is irrelevant — what matters is the number of distinct DEPENDENCY LEVELS, counted strictly by hops between a leaf worker and the final output node. Four independently-named specialists that ALL feed directly into one integrator is TWO levels, no matter how sophisticated or specialized their descriptions sound. An "intermediate" node only counts as a genuine third level if it (a) does NOT depend on every leaf worker directly (it must aggregate a real SUBSET, not all of them), and (b) performs actual synthesis on its inputs rather than forwarding them unchanged. FAIL if an intermediate node is a decorative pass-through inserted only to manufacture a fake third level.

   **Procedure — mandatory, do not skip:**
   STEP A. List EVERY sub-task with its `id`, `parallel_group`, and `depends_on` verbatim in your reason, even for a PASS. From this list, compute Level 0 = sub-tasks with no `depends_on`, Level 1 = sub-tasks depending only on Level 0, Level 2 = depending on Level 1, etc. State the maximum level number found.
   STEP B. Classify the actual structure using the table above AND the anti-gaming clause — a node that satisfies (a) or (b) above does not count toward the level total.
   STEP C. Compare to the declared `coordination_pattern` from `task.toml`. FAIL if they do not match — quote the full `parallel_group`/`depends_on` list and the declared pattern in your reason.

   STEP D. **Cross-check against the realized multi-agent trajectory — do not accept decomposition.yaml's own structure as proof of what actually happened at runtime.** Steps A–C establish whether `decomposition.yaml`'s OWN dependency/parallel_group structure matches the declared `coordination_pattern` on paper. That is necessary but not sufficient: an LLM orchestrator reads `decomposition.yaml` as guidance, not as an executable script, and can dispatch sub-agents differently than the plan specifies. Perform this second, independent check on every available multi-agent run:

   1. Glob `execution_logs/multi-opencode-agent/*/agent/raw_trajectory/*.json` (literal folder name — not `multi-opencode-agent-noplan/`) and read every session file: the `orchestrator_ses_*.json` (root) and all `subagent_ses_*.json`. Each session JSON carries its own `id` and a `parent_id` pointing to the session that spawned it.
   2. Reconstruct the realized spawn tree from `id`/`parent_id`: the orchestrator is the root; a sub-agent whose `parent_id` is another sub-agent's `id` (not the orchestrator's) is a nested, level-2+ agent — a real hierarchy. If every sub-agent's `parent_id` is the orchestrator, the realized graph is a single-level fan-out, no matter how many sub-agents there are. Corroborate with `task`-tool spawn calls per session (a session that made `task` calls is a spawner; a session with zero `task` calls is a leaf worker).
   3. Compute the realized level count using the same level-counting definition as STEP A (hops from a leaf worker to the final output node), applied to the id/parent_id tree instead of decomposition.yaml's depends_on graph.
   4. Compare the realized level count and shape against BOTH: (a) the level count computed from `decomposition.yaml` in STEP A, and (b) the declared `coordination_pattern` from `task.toml`, using the same pattern-signature table as STEP B.

   FAIL if either comparison diverges:
   - **Divergence from decomposition.yaml** — the realized spawn tree has a different level count or shape than STEP A computed from `decomposition.yaml` itself (e.g. decomposition.yaml specifies a manager layer, but every sub-agent's `parent_id` in the actual run is the orchestrator directly — the declared manager layer was never dispatched). This means the orchestrator deviated from the gold decomposition at runtime.
   - **Divergence from the declared coordination_pattern** — the realized tree, independently of decomposition.yaml, does not match the pattern-signature table (e.g. `coordination_pattern = hierarchical` but every sub-agent's `parent_id` is the orchestrator — a flat fan-out was realized) — even if decomposition.yaml's own structure, on paper, would have satisfied the hierarchical signature.

   Quote: the full list of session `id`/`parent_id` pairs with file names, the computed realized level count, the STEP A decomposition-derived level count, and the declared `coordination_pattern`. If both match, PASS and state so explicitly, quoting the id/parent_id evidence that establishes the match — do not PASS this step on the strength of STEP A/B/C alone.

   **If multiple multi-agent runs exist**, check each; FAIL if the majority of runs diverge, and note any single-run outlier separately rather than letting one anomalous run drive the verdict — multi-agent dispatch has run-to-run variance, and this step is checking systemic pattern mismatch, not one bad roll.

   **If no multi-agent execution logs / raw_trajectory exist yet** (task package under review pre-execution), mark this STEP D sub-result `NOT_APPLICABLE`, state that no trajectory was available, and let STEP A–C's paper-based verdict stand as the check's result — do not FAIL for missing logs.

   **Note on scope overlap:** this procedure deliberately mirrors QD-05 Checks 5–6 and QD-07 Check 5, which perform the same id/parent_id spawn-tree reconstruction for different purposes (QD-05: depth/width sufficiency; QD-07: fairness/pattern-fidelity of SA-vs-MA comparison). This step's angle is distinct: it asks whether the REALIZED run matches THIS TASK's specific `decomposition.yaml` blueprint and declared pattern, as a decomposition-soundness question. Do not skip this step by reasoning that another QD already read the trajectory — your verdict must independently quote the id/parent_id evidence per the Grounding Rule.

   Common false claim to flag: decomposition has workers all in `parallel_group: map` and one assembler in `parallel_group: reduce` (two flat levels) but `task.toml` declares `hierarchical`. That is map-reduce, not hierarchical — this holds even if there are 4+ distinctly-named workers, and even if a pass-through node sits between them and the assembler.
8. **Parallel-group consistency** — A sub-task in `parallel_group: X` cannot list any `depends_on` entry that resolves (directly or transitively) to another sub-task that is also in `parallel_group: X`. Tasks in the same parallel group run concurrently by definition, so they cannot have dependency relationships among themselves. Walk every sub-task: collect its `depends_on` list, follow the dependency chain, and FAIL if any node in that chain shares its `parallel_group`. The contradiction is logical, not stylistic — `depends_on` says "I wait for these to finish" while same-group `parallel_group` says "I run alongside these". Both cannot be true.

   Example violation to recognize:
   ```yaml
   - id: documentation
     depends_on:
       - lookups-and-key-transforms       # also parallel_group: fan-out
       - backend-features-and-sqlite      # also parallel_group: fan-out
     parallel_group: fan-out
   ```
   `documentation` cannot belong to `parallel_group: fan-out` while waiting on other `fan-out` tasks to finish. Either move `documentation` to a later group (e.g. `synthesize`) or remove the same-group dependencies.

## Output Format
Return ONLY valid JSON:
```json
{
  "dimension": "QD-06",
  "result": "PASS" or "FAIL",
  "checks": [
    {"id": 1, "name": "non_overlapping", "result": "...", "reason": "..."},
    {"id": 2, "name": "self_contained", "result": "...", "reason": "..."},
    {"id": 3, "name": "complete_coverage", "result": "...", "reason": "..."},
    {"id": 4, "name": "dependencies_correct", "result": "...", "reason": "..."},
    {"id": 5, "name": "minimal", "result": "...", "reason": "..."},
    {"id": 6, "name": "what_not_how", "result": "...", "reason": "..."},
    {"id": 7, "name": "pattern_match", "result": "...", "reason": "..."},
    {"id": 8, "name": "parallel_group_consistency", "result": "...", "reason": "..."}
  ],
  "justification": "Overall assessment in 2-3 sentences."
}
```
Result is FAIL if ANY check fails.


# QD-07: Benchmark Validity & Fairness

## Your Role

You are checking whether the single-agent vs multi-agent comparison is fair. If the multi-agent gets unfair advantages — domain knowledge the single agent doesn't have, or a decomposition that essentially solves the problem — the benchmark number is misleading.

## Explore First

Before evaluating any checks, run `Glob /task/**` to see the full task file tree. The "Files to Read" section below is a minimum starting point — use Read, Grep, and Bash freely on any file that looks relevant to your checks.

## Files to Read

- `/task/decomposition.yaml`
- `/task/instruction.md`
- `/task/task.toml` (read `coordination_pattern` and `verifier_type`)
- `/task/environment/` (ALL files — Dockerfile and everything inside; check for helper scripts in input artifacts)
- `/task/execution_logs/multi-opencode-agent/` (literal folder name — not `multi-opencode-agent-noplan/`, which is out of scope for this skill's plan-guided fairness checks) — the multi-agent **raw** trajectory (`<run>/agent/raw_trajectory/`, containing `orchestrator_ses_*.json` + `subagent_ses_*.json`). Required for check 5; also used by checks 7, 10, 14.
- `/task/tests/` (read ALL files for check 9)

## Grounding Rule

**Before issuing any FAIL verdict on any check, you MUST copy the exact verbatim text from the file being evaluated that triggered the violation into your `reason` field.** If you cannot produce an exact quote from that specific file, the check PASSES. Do not infer, paraphrase, or reconstruct text — only quote what is literally present.

## Hard-Stop Checks (Check 10)

Check 10 is a **hard stop** — it is evaluated before all other checks and **immediately terminates evaluation with overall FAIL** if any violation is found. Do not proceed to checks 1–9 if Check 10 fails. The reason is simple: if SA was handicapped at runtime, every score, gap, and reward value in this task is invalid. There is nothing to evaluate.

## Checks

1. **Same role-neutral instruction, no mode-dependent scoring promises.** All three run modes (single, multi, multi-noplan) receive the identical task instruction. `instruction.md` must describe ONLY what to compute, what inputs to use, and what schema to produce — never how the work will be organized AND never how the score will be adjusted based on the agent's process. Two failure modes to check:

   **(a) Orchestration-language leak.** FAIL if `instruction.md` contains multi-agent-only execution language such as assigning work to "each agent", referring to "map agents", "sub-agents", "shards", "your module assignment", or saying that "a synthesizer agent will run after all agents finish". These orchestration details belong in `decomposition.yaml`, not in the shared `instruction.md`. Example violations: _"Each agent in this task is assigned one SciPy module"_, _"A synthesizer agent will run after all 16 map agents finish"_.

   **(b) Mode-dependent scoring-rubric leak.** FAIL if `instruction.md` describes scoring rubric details that are keyed on the agent's PROCESS rather than its OUTPUT — bonuses or penalties for sub-agent coordination, trajectory marker presence, delegation counts, map/reduce structure, orchestration evidence, or any other process-shape signal. The agent's process is invisible to the grading; only output quality against the oracle is graded. Example violations: _"You will receive +40 points for evidence of sub-agent coordination in your trajectory"_, _"-45 if the trajectory does not contain map-reduce markers"_, _"Orchestration patterns will be rewarded"_, _"Score bonus awarded for delegating to specialist agents"_. This pairs with QD-14 Check 1, which forbids the verifier from APPLYING such mode-dependent adjustments — the instruction must not PROMISE them either. The principle is symmetric: process is invisible on both the input side (instruction) and the output side (verifier).

2. **Same timeout** — Both configurations have the same `agent.timeout_sec`. FAIL if asymmetric timeouts.
3. **Coordination-driven gap** — Multi-agent advantage comes from coordination quality — context splitting, specialist reasoning, structured synthesis. FAIL if gap is only from parallelism (same work faster, not better). **Exception: if the single-agent fails due to timeout while the multi-agent completes within the same timeout, a parallelism-driven gap is acceptable — decomposing context across sub-agents to fit within the timeout budget is a valid coordination mechanism, not mere speed. Do not fail this check when the timeout scenario in check 7 applies.**
4. **No custom tooling advantage** — Input artifacts are data for the agent to process, not scripts that do the processing. FAIL if executable scripts in input artifacts perform substantive analysis.
5. **Multi-agent trajectory follows the declared coordination pattern — reconstructed from the raw trajectory** — Do not accept the declared pattern on faith. Open the multi-agent **raw** trajectory and reconstruct what the orchestrator actually did, then confirm it matches the declared `coordination_pattern`.

   **Procedure — MANDATORY:**

   STEP A. Read the declared `coordination_pattern` from `task.toml` and the intended structure in `decomposition.yaml`.

   STEP B. Glob `execution_logs/multi-opencode-agent/*/agent/raw_trajectory/` (literal folder name — not `multi-opencode-agent-noplan/`) and read every session file: the `orchestrator_ses_*.json` (root) and all `subagent_ses_*.json`. Each session JSON carries its own `id` and a `parent_id` pointing to the session that spawned it — this is the ground truth of the coordination graph.

   STEP C. Reconstruct the actual spawn tree from `id`/`parent_id`:
   - The orchestrator is the root (its `id` equals the `orchestrator_ses_*` file's id and appears as the `parent_id` of the top-level sub-agents).
   - A sub-agent whose `parent_id` is another **sub-agent's** `id` is a nested (level-2+) agent → a real hierarchy. If every sub-agent's `parent_id` is the orchestrator, the graph is a single-level fan-out.
   - Corroborate with `task`-tool spawn calls per session: a session that made `task` calls is a spawner (orchestrator or manager); a session with zero is a leaf worker. Probe: `for f in .../raw_trajectory/*.json; do python3 -c "import json,sys;d=json.load(open(sys.argv[1]));print(d['id'],d.get('parent_id'))" "$f"; done`.

   STEP D. Confirm the reconstructed tree matches the exact `coordination_pattern` string the trainer declared in `task.toml` — whatever that value is. The realized spawn structure (the `id`/`parent_id` graph plus per-session spawn counts) must be consistent with the declared pattern's plain meaning. For example, a declared `hierarchical` pattern requires multi-level parent chains (some workers' `parent_id` is a manager sub-agent, not the orchestrator), whereas a flat structure where every sub-agent's `parent_id` is the orchestrator is a fan-out — a mismatch. The check is not about which pattern is "best"; it is strictly whether the actual multi-agent coordination matches what the trainer claimed.

   **Verdict — state it explicitly in `reason`, citing the reconstructed tree (parent_id linkages + per-session spawn counts):** FAIL if the orchestrator solved the task monolithically (no or negligible sub-agent spawns), if it ignored the decomposition, or if the realized graph is a different pattern than declared (e.g., `coordination_pattern = hierarchical` but every sub-agent's `parent_id` is the orchestrator — a flat fan-out, not a hierarchy). PASS only if the realized spawn tree demonstrably matches the declared pattern. Per the Grounding Rule, quote the declared `coordination_pattern` and the actual `id`/`parent_id` values that establish the realized structure.

6. **Partial credit supported — HARD FAIL on any cap or multiplier in the reward formula** — The verifier must award fractional scores strictly proportional to how much of the task was completed. The reward must flow continuously from agent output quality to final score with no caps, no multipliers, and no tiers applied after scoring. Documentation in `instruction.md` does not make a cap or multiplier valid — it must be removed entirely.

   **HARD FAIL immediately if the verifier contains ANY of the following patterns — no exceptions, no threshold, no override:**
   - **Any multiplicative factor on a partial score** — e.g. `reward = K × (passed/total)` for any K < 1.0, `final *= 0.5`, `score = 0.5 * base_reward`. A multiplier on a partial score compresses the range of achievable scores and creates a cliff between partial and perfect work. It does not matter whether K is 0.5, 0.3, or 0.0 — any constant scaling of a partial score is a cap by another name.
   - **Any hard cap at any stage of scoring** — e.g. `cap = min(cap, X)`, `reward = min(reward, X)`, `score = min(score, X)` applied after any scoring has begun, regardless of whether the score is normalized to [0,1] or expressed as a raw point total (e.g. `score = min(score, 60.0)` out of 100 is identical in effect to `score = min(score, 0.6)` out of 1.0). A cap sets a ceiling that partial work cannot exceed regardless of quality, at any stage of the pipeline — before normalization, after normalization, or during intermediate accumulation. Hard FAIL for any cap, including X = 0.85, X = 0.70, X = 0.60, X = 0.55, X = 0.30, X = 0.14.
   - **Any binary-zero gate** — e.g. `if condition: final *= 0.0`, `if not passes: reward = 0.0`. Collapses any partial score to zero.
   - **Any two-tier formula** — e.g. `if all_pass: reward = 1.0 else: reward = K × proportion`. Creates an unreachable dead zone [K, 1.0). A 99% completion scores identically to a 50% completion — both hit the same ceiling K.
   - **Any heuristic cap formula that can reach 0.0** — e.g. `cap = max(0.0, 1.0 - n × 0.09)` where cap hits 0.0 at n ≥ 12. Designed to be graduated but functionally binary at the boundary.
   - **Any reward assignment to a fixed constant** — e.g. `reward = 0.0` or `reward = 0.14` triggered by any threshold on a continuous metric, regardless of whether the threshold is disclosed.
   - **Catch-all: any `min(score, X)` or `min(reward, X)` expression anywhere in the verifier** — regardless of the value of X, the name of the variable, the stage of scoring, or whether the cap is conditional. The presence of `min(` applied to a score or reward variable is a HARD FAIL. Scan the entire verifier file for `min(` and flag every instance where the argument could constrain a score below what the agent earned. Do not allow a conditional cap to pass because the condition "rarely fires" — the code path exists and will distort scores.

   **The only valid reward formula is one where the score moves continuously and proportionally with task completion quality — no floor, no ceiling below 1.0, no multiplier, no tier, no cap at any stage.**

   **For each verifier type:**
   - **Executable verifier**: Read `tests/verify.py` or `tests/test.sh` or any tests/ related files end-to-end. Every scored dimension must contribute fractionally. FAIL if any final multiplier or assignment can reduce a non-zero weighted sum to 0.0. FAIL if any individual check is worth more than 50% of the total score and is evaluated as binary pass/fail.
   - **LLM judge verifier**: Read the judge prompt — it must explicitly instruct the judge to award a score between 0.0 and 1.0 based on how many sub-tasks or requirements were met, with each scoreable criterion listed. FAIL if the judge prompt asks only for a binary verdict or contains no instruction about partial scoring.

   **The instruction.md exception does NOT apply**: a trainer cannot make a binary gate valid by documenting it in `instruction.md`. The gate must be removed or replaced with a graduated penalty (e.g., linearly scaling the multiplier between 0.5 and 1.0 rather than between 0.0 and 1.0). If you see a threshold like "≥7/8 entries required" that fires a `× 0.0` multiplier, that is a HARD FAIL regardless of whether the threshold appears in the instruction.

7. **Meaningful performance gap — absolute, not waived by timeout.** Read the execution logs for both single-agent and multi-agent configurations. **The multi-agent reward must be at least 18% higher than the single-agent reward. This requirement is ABSOLUTE — it applies whether or not the single agent timed out.** A timeout is not proof of difficulty if the single agent already produced a high-reward output before the timer expired (Issue 3.14: _"single agent timed out but received reward 1.0"_ is logically incoherent — single solved the task; the timeout is irrelevant). The combination of `AgentTimeoutError` and `reward >= 0.9` on the single-agent side means the task is NOT multi-agent-requiring; single just happened to finish the work before the timer fired. FAIL if `multi.mean_reward - single.mean_reward < 0.18`, regardless of single's exception status.

   You MUST quote the actual reward values from the execution logs in your reason — both `single.mean_reward` and `multi.mean_reward` verbatim, plus the computed gap. If a timeout was present on the single agent, also quote the recorded reward — that combination needs to be visible in your reasoning, not hidden behind the timeout. Also verify the timeout values from check 2 are identical between single and multi — a gap produced by giving multi-agent a longer timeout is forgery and fails this check. If you cannot find execution log evidence at all, this check PASSES — do not infer or estimate.

8. **Verifier type matches implementation** — Read `verifier_type` from `/task/task.toml`. Then read every file in `/task/tests/` to determine what scoring mechanism is actually implemented. Apply the following rules:

   **If `verifier_type = "llm-judge"`:**
   - The scoring decision for the agent's output must be made by an LLM. Look for evidence of an LLM API call in any test file — for example, a model completion call, an LLM client being instantiated, or an API key being read from the environment and passed to a model call.
   - FAIL if the actual scoring logic is fully deterministic — i.e., if correctness is determined purely by JSON field comparison, regex matching, numeric tolerance checks, or string normalization with no LLM involved. Such a verifier cannot handle the full space of valid agent responses and will silently penalize correct answers that differ in phrasing, format, or structure from the oracle.
   - FAIL if an LLM is invoked only for formatting or post-processing (e.g., parsing the agent's output into JSON) while the correctness decision itself is still made deterministically. The LLM must be the judge of correctness, not a preprocessor.
   - **HARD FAIL if the judge script contains any of the following deterministic score-suppression mechanisms that can fire regardless of LLM output:** (a) a pre-gate function (`pregate`, `pre_gate`, `structural_gate`, or any block that assigns `reward = 0.0` and returns before LLM scoring runs); (b) score caps (`cap = min(cap, X)` or `reward = min(reward, X)` where X ≤ 0.55) applied by the script after or before the LLM; (c) additive penalty deductions applied by the script that in aggregate can reduce the score to 0.0 regardless of LLM score. These patterns mean the script is doing the real scoring and the LLM is window-dressing — the task is effectively `executable` not `llm-judge`. A legitimate `llm-judge` verifier lets the LLM score freely against the oracle and instruction rules; the script only handles I/O (reading the agent output, writing the reward file). Any script logic that modifies the score is a de-facto executable verifier and must be rejected.

   **If `verifier_type = "executable"`:**
   - The scoring logic must be fully deterministic — no LLM API calls, no model client instantiation, no API keys. FAIL if any test file makes a model call to determine correctness.

   **If `verifier_type = "hybrid"`:**
   - The scoring logic must show evidence of BOTH a real LLM API call that materially contributes to the correctness decision AND a deterministic/structural scoring component (regex, schema check, numeric tolerance, etc.).
   - FAIL if either side is entirely absent from `tests/verify.py` — that means the task is actually a plain `llm-judge` or plain `executable` verifier mislabeled as `hybrid`.

   **Additionally — output type vs verifier type alignment:**
   - If the task's expected outputs are open-ended, interpretive, or admit multiple valid forms (e.g., analytical reports, natural-language explanations, ranked lists with justifications, structured summaries where content matters more than exact values), the verifier MUST be `llm-judge` or `hybrid`. FAIL if `verifier_type = "executable"` for such a task — deterministic code and regex matching cannot cover the full range of correct responses and will produce invalid scores.
   - If the task's expected outputs are fully deterministic (e.g., exact numeric values, fixed-schema JSON, specific file modifications, pass/fail unit tests), `executable` is the correct type and an LLM judge introduces unnecessary variance. This is not a FAIL condition but note it in your reason if the declared type is `llm-judge` for a fully deterministic task.
   - `hybrid` is appropriate when the task has both a fully-deterministic sub-part (exact values/schema) and an open-ended sub-part (narrative/synthesis) that genuinely needs LLM judgment. Not a FAIL condition either way — informational only.

   You MUST quote the `verifier_type` value from `task.toml` and cite the specific file(s) in `tests/` — or their absence — that support your verdict.

9. **No gap-distorting verifier floors, cliffs, or binary gates** — Read `tests/judge.py` (or `tests/verify.py`) end-to-end. Search for score-modifying patterns: `max(score,`, `min(score,`, `score *=`, and explicit assignments like `score = 0.0` or `reward = 0.0`. For each one found, determine whether the triggering condition is **asymmetric** — i.e., a well-structured multi-agent output would satisfy (or fail) it more often than a single-agent output simply because of how multi-agent outputs are produced.

   Common asymmetric patterns to flag:
   - **Floor triggered by aggregate count** — e.g., `if verified_excerpts >= 30: score = max(score, 0.55)`. Multi-agent outputs fan out across sub-agents and naturally accumulate more excerpt-level hits, pushing the count above the floor threshold even when LLM judge quality is low. Single-agent outputs rarely reach the threshold. The floor then manufactures a gap that does not reflect true quality.
   - **Completeness gate unlocked by structural shape** — e.g., `if complete_report_shape(output): score = max(score, 0.5)`. The multi-agent orchestrator synthesizes a complete report schema by construction; a single agent may produce a partial schema under time or context pressure. The structural completeness is an artifact of the coordination pattern, not a quality signal.
   - **Binary multiplier on a field a single agent more often omits** — e.g., `if not has_summary_section: score *= 0`. Multi-agent synthesis stages reliably produce a summary section; single agents may omit it. The multiplier collapses single-agent scores disproportionately.
   - **Cliff compressing multi-agent scores** — e.g., `if precheck_failures: score = min(score, 0.65)`. If precheck failures are more likely when an agent produces MORE content (e.g., a long multi-agent output triggers a regex that a terse single-agent output does not), the cliff deflates multi-agent scores artificially.

   **Verdict rules:**
   - FAIL if any floor, cliff, or binary gate **exists in the verifier code** such that a well-structured multi-agent output would trigger it more often than a single-agent output — **regardless of whether it fired in the recorded run**. The presence of the asymmetric pattern in the code is the violation, not whether it happened to be triggered in the execution logs. A trainer cannot fix this by making the threshold harder to reach (e.g., switching from lenient to strict excerpt matching so that the floor is rarely triggered) — the code must be removed or made symmetric.
   - PASS if every floor/cliff/gate mechanism applies identically to both agent types, OR if the modifier protects against a degenerate edge case that applies equally to both (e.g., `score = max(0.0, score)` to prevent negatives — this is always symmetric).
   - **Band-aid mitigations do not pass.** If you see TWO excerpt-matching functions (one strict, one lenient) where strict is used for the floor count and lenient for prechecks, this is a sign the trainer tried to make the floor harder to trigger rather than removing it. Still FAIL — the floor code is still present.

   You MUST quote the exact line(s) from `tests/judge.py` (or `tests/verify.py`) in the `reason` field before issuing a FAIL. If no such patterns are present, state that explicitly and PASS.

10. **SA runtime prompt matches instruction.md exactly — no injected handicaps.**

Check 1 audits `instruction.md` on disk for mode-dependent language. This check goes one level deeper: it verifies that the instruction SA _actually received at runtime_ (recorded in `raw_trajectory/orchestrator_ses_*.json`) is identical to the current `instruction.md` — no extra content inserted, no content removed.

**Why this matters:** A trainer can write a clean `instruction.md`, inject a handicap block into the runtime prompt at execution time (e.g. via a harness config or a pre-run script), run SA, then delete the block from `instruction.md` before delivery. The static file looks fine; only the runtime logs expose the fraud.

**Procedure — MANDATORY, do not skip:**

STEP A. Read `instruction.md` and record its first non-empty line as `ANCHOR`.

STEP B. Open `execution_logs/single-opencode-agent/*/agent/raw_trajectory/orchestrator_ses_*.json` (all SA runs). Read `messages[0]["parts"][0]["data"]["text"]` from each file — this is the harness prompt that contains `instruction.md`. Because the field is stored as a JSON-encoded string, internal double-quotes appear as `\"` (escaped). Unescape `\"` → `"` before comparing.

STEP C. In the unescaped text, find `ANCHOR`. Extract everything from `ANCHOR` to end-of-string as `SA_INSTRUCTION_SLICE`. If the string `## Gold Decomposition Guide` appears in the slice, truncate at that point (it should not be in SA runs, but be defensive).

STEP D. Normalize both `SA_INSTRUCTION_SLICE` and `instruction.md` by replacing `\r\n` → `\n`, stripping leading/trailing whitespace.

STEP E. **Hard FAIL if `SA_INSTRUCTION_SLICE != instruction.md` (after normalization).** Quote the first ~200 characters of divergence in `reason`. Do not attempt to characterize whether the difference is "minor" — any difference is a FAIL.

STEP F. **Additionally, scan the full unescaped text for gap-widener fingerprints regardless of the above result.** Hard FAIL if any of the following strings appear (case-insensitive) or any order sentence or keywords patterns fall under the below mentioned one:

- `TEMP-GAP-WIDENER`
- `GAP-WIDENER`
- `remove before submission`
- `remove before llm review`
- `MANDATORY EXECUTION CONSTRAINTS`
- `NO SCRIPTING` (when followed by constraint language, not task-content references)
- `MANUAL ACCUMULATION`
- `intentional differentiator`
- `k=4` or `k = 4` (reward-exponent gap wideners)

Quote the exact matched string and surrounding context (~100 chars) in `reason`.

STEP G. Open `execution_logs/multi-opencode-agent/*/agent/raw_trajectory/orchestrator_ses_*.json` (all MA runs). Extract and unescape `messages[0]["parts"][0]["data"]["text"]`. Verify `instruction.md` appears verbatim as a substring. FAIL if not found (MA was run with a different instruction). This is the same as Check 1 / S-07 but applied to the runtime logs explicitly.

STEP H. Open `execution_logs/multi-opencode-agent-noplan/*/agent/raw_trajectory/orchestrator_ses_*.json` (all noplan runs). Extract and unescape `messages[0]["parts"][0]["data"]["text"]`. Verify `instruction.md` appears verbatim as a substring — same check as STEP G. Confirms noplan received the identical instruction.md; only the decomposition guide is withheld, nothing else about the prompt changed. This check applies regardless of noplan's reward/completion outcome — it is about prompt integrity, not performance.

**Verdict rules — no exceptions, no partial credit, no WARN:**

- FAIL if SA slice ≠ instruction.md (Step E) — any divergence, however small
- FAIL if any gap-widener fingerprint found in SA prompt (Step F)
- FAIL if instruction.md not found verbatim in MA prompt (Step G)
- FAIL if instruction.md not found verbatim in noplan prompt (Step H)
- FAIL if `raw_trajectory/orchestrator_ses_*.json` is missing for any run — unverifiable logs are treated as a violation
- PASS only if Steps E, F, G, and H are all clean across every run
- **A FAIL on Check 10 forces the overall QD-10 result to FAIL regardless of all other checks. The overall result field MUST be "FAIL" if Check 10 is "FAIL".**

11. **Structural/schema compliance penalties must not be capable of zeroing out genuine task-intent quality.**

Every task has a **primary intent** — the thing it is actually trying to measure: extraction accuracy, code correctness, answer quality, synthesis coherence. Structural penalties (exact-format field copying, flag combinations, key schema compliance, type enforcement, count rules) are secondary — they enforce output hygiene, not task quality. A verifier that lets structural penalties alone cancel out a high task-intent score is grading format compliance as if it were the task goal. This check applies to every task, regardless of domain or verifier type.

**Procedure:**

STEP A. Identify the task's **primary intent score component** from the rubric in `tests/judge.py` or the judge prompt. This is the component that directly measures whether the agent produced correct output (e.g., extraction accuracy, test pass rate, answer correctness, synthesis quality). Record its **maximum possible contribution** as `I_max` (the fraction of 1.0 that this component can earn at full credit).

STEP B. Enumerate every **structural/compliance penalty** in the verifier — any deduction that fires based on format or schema rule violations rather than wrong content. Examples: per-field exact-match penalties, per-missing-key deductions, per-type-mismatch penalties, per-flag-combination violations, per-count-mismatch deductions. For each, record:

- `rate`: the per-violation deduction amount
- `max_violations`: the maximum number of violations possible given the task's stated output schema (e.g., if the task has 50 questions, max q-field violations = 50; if 10 papers, max page violations = 10)
- `max_contribution = rate × max_violations`

STEP C. Sum all structural penalty max contributions → `P_max_structural`. Separately record any uncapped hallucination penalty as `P_hallucination = penalty_per_instance × (number of quotable fields in the schema)`.

STEP D. Apply verdict logic:

- **FAIL if `P_max_structural >= I_max`** — structural penalties alone can cancel out every point earned for correct answers. The verifier is rewarding schema compliance, not task performance.
- **FAIL if any single structural penalty category contributes `max_contribution >= I_max`** — one compliance axis alone can erase full credit for correct content.
- **FAIL if `P_hallucination` (uncapped, no per-agent ceiling) `>= I_max`** — the hallucination deduction alone can zero out full extraction credit regardless of accuracy.
- **FAIL if `P_max_structural + P_hallucination > 1.0`** — penalties can exceed the entire possible score, making it impossible for any agent to score above 0.0 under worst-case structural conditions regardless of answer quality.
- PASS if all structural penalty categories are individually bounded well below `I_max`, and combined `P_max_structural < 0.5 × I_max`.

STEP E. If any FAIL triggered: quote the exact penalty instruction lines, state `P_max_structural`, state `I_max`, and note whether SA scored 0.0 in execution logs despite a non-trivial extraction base. If no structural penalties exist beyond standard numeric tolerance checks (e.g., ±5% for floats), state that explicitly and PASS.

**This check is task-domain-neutral.** It applies equally to extraction tasks, code tasks, synthesis tasks, audit tasks, and any other task type. Any verifier where schema compliance penalties dominate content quality signals fails this check.

12. **Oracle comparison values must be derivable from instruction.md alone — no hidden weights or undisclosed formulas.**

When the verifier scores by comparing agent output numerically against a static oracle file (e.g., `oracle.json`, `gold.json`, `expected_output.json`) using tolerance-based matching (`close()`, `abs(a - b) <= tol`, etc.), those oracle values must be fully reproducible by an agent reading only `instruction.md` and the disclosed input artifacts. If the oracle was generated using a weighting scheme, calibration formula, or multi-factor aggregation method that `instruction.md` does not describe, agents are penalized for failing to guess a formula they were never given. This is **undisclosed oracle dependency** — a **hard FAIL**.

**Why this matters:** When oracle values require an undisclosed formula, neither SA nor MA can derive them correctly. The score gap between the two modes then reflects which mode's ad-hoc guess was closer to the trainer's private formula — not which coordination pattern produced better reasoning. The gap is random luck, not benchmark signal.

**Procedure — MANDATORY for any task where a static oracle file is present in `tests/`:**

STEP A. Check whether a static oracle file exists in `tests/` (common names: `oracle.json`, `gold.json`, `ground_truth.json`, `expected_output.json`, or any `.json` file loaded by the verifier as a reference answer). If no static oracle file exists — the oracle is generated dynamically at run time from the same input artifacts the agent reads, using only the methodology in `instruction.md` — this check **PASSES**. Skip remaining steps.

STEP B. Read the oracle file. Identify every numeric field that the verifier compares against agent output using tolerance-based or exact matching (look for `close()`, `abs(a - b) <= tol`, `==`, or equivalent). Record the field names and example values (e.g., `probability: 0.7231`, `risk_score: 0.8412`).

STEP C. Read `instruction.md` in full. Identify every constraint it places on HOW the agent must compute its numeric outputs — formulas, weights, normalization rules, aggregation functions, scoring methodology. A valid instruction specifies the methodology precisely enough that a careful reader could reproduce the oracle values (e.g., "compute risk score as the equally-weighted average of z-scored signals across all four sources").

STEP D. For each numeric oracle field identified in Step B, ask: **can an agent, following only the methodology described in `instruction.md` and reading only the disclosed input artifacts, deterministically reproduce this value?** Apply the following verdict rules:

**HARD FAIL** if any of the following:

- `instruction.md` says "use all four sources" or equivalent but does not specify the relative weights or aggregation formula, yet the oracle contains specific probability or score values derived from a trainer-chosen weighting scheme (e.g., `climate × 0.08 + population × 0.32 + ...`). Agents cannot reverse-engineer weights from oracle values they are not shown.
- The oracle contains entity-level numeric outputs derived from a non-trivial formula (normalization + weighted sum + calibration step) and `instruction.md` describes the output schema but not the computation.
- The verifier applies a tolerance-based cap or penalty based on deviation from oracle values (e.g., `if avg_error > threshold: cap = min(cap, X)`) and the threshold was calibrated to the oracle formula rather than disclosed in `instruction.md`.

**PASS** if any of the following:

- Oracle values are direct extractions from the input data — no formula is required because the value appears verbatim in the input CSV or JSON.
- `instruction.md` specifies the exact formula, weights, and/or algorithm sufficient to reproduce the oracle values from the input artifacts.
- The oracle contains only categorical, qualitative, or ordering values (e.g., entity names, rank order) where no undisclosed numeric formula is needed.

STEP E. If HARD FAIL: quote (i) the specific oracle field(s) whose values cannot be derived, (ii) the exact text from `instruction.md` that was supposed to specify the methodology but does not (or its absence), and (iii) the verifier lines that compare against those oracle values. Estimate the score impact: what fraction of the verifier's point budget depends on matching undisclosed-formula oracle values?

**Verdict rules — no exceptions, no partial credit, no WARN:**

- HARD FAIL if any oracle numeric field is undisclosed-formula-dependent (Step D FAIL conditions).
- PASS only after confirming every tolerance-matched oracle field is derivable from `instruction.md` alone.
- **A FAIL on Check 12 forces the overall QD-10 result to FAIL regardless of all other check results.**

13. **LLM judge must not truncate agent output before scoring — when judge weight ≥ 50%.**

When a task uses an embedded LLM judge as the dominant scoring component (weight ≥ 50%), the verifier must pass the agent's complete output to the judge. Truncating the submission before the judge sees it means the judge scores a partial view — sections that fall outside the truncation window are silently penalised as absent regardless of quality.

**Why this matters asymmetrically:** Single-agent outputs are often denser (all content in a flat monolithic response). Multi-agent outputs are naturally longer (orchestrator synthesis across sub-agent results produces more tokens). A character or token cutoff penalises SA disproportionately when key scored sections fall in the second half of a long SA response but within the first half of a verbose MA synthesis. This matches the Bayway Refinery rejection pattern: SA's 62 KB output was truncated to 12 KB before the judge, key sections fell outside the window, SA scored 29% despite high static recall while MA's verbose output filled the window and scored 88%.

**Procedure:**

STEP A. Read `task.toml` `verifier_type`. If `executable` with no LLM API call in `tests/`, PASS immediately — no judge to truncate. For `hybrid`, do NOT auto-pass — apply the same procedure as `llm-judge` below, since a hybrid verifier also has an LLM-judged component that can be truncated.

STEP B. Read `tests/judge.py` (or equivalent judge script) end-to-end. Search for any truncation or slicing of the agent's raw output before it is passed to the LLM:

- String slice: `agent_output[:N]`, `text[:12000]`, `output[:max_chars]`
- Length-based branch: `if len(text) > N: text = text[:N]`
- Token-level truncation: `tokens[:N]` followed by detokenisation
- Helper calls: `truncate(output, limit)`, `clip_text(output, N)`, or any wrapping function that reduces the string length

STEP C. If truncation exists, determine the LLM judge's weight in the final reward formula (the fraction of `reward.json` that comes from the judge's score).

STEP D. Determine whether a complete agent response for this task plausibly exceeds the truncation limit. Read `instruction.md` to understand the output deliverable: if the task asks for a multi-section report, a long analysis, or content over many input documents, a `[:12000]` character limit can easily cut off the last third of a valid response.

**HARD FAIL if ALL three conditions hold:**

- Truncation code exists in the judge script (Step B)
- LLM judge weight ≥ 50% in the final reward formula (Step C)
- The truncation limit is short enough that sections of a complete agent response could fall outside it given the task's stated output scope (Step D)

**PASS if:** No truncation exists, OR the LLM judge weight is < 50% and a deterministic component independently covers the truncated content, OR the truncation limit demonstrably exceeds any plausible complete agent response for this task.

Quote the exact truncation line (with file path and line number) and the judge weight derivation in `reason` before issuing FAIL.

14. **SA reward=0.0 from FileNotFoundError must not coexist with SA having produced correct output.**

A verifier that records `reward=0.0` because it cannot find the agent's output file — when the agent actually wrote the file — is reporting an infrastructure failure as a task failure. This produces a fake gap: SA is scored as if it produced nothing, while MA (whose output may be structured differently and found by the verifier) gets a real quality score.

Two variants exist:

- **Pattern 6a (wrong expected path):** The verifier looks for output at a path the agent was not told to write to, or there is a prefix mismatch between instruction.md and tests/. The agent wrote a file; the verifier looked in the wrong place.
- **Pattern 6b (volume isolation):** SA wrote to the correct path — confirmed by a subsequent `ls` or read-back in the agent's trajectory — but the Docker volume mount failed and the verifier container could not see the file.

**Procedure:**

STEP A. Read `execution_logs/single-opencode-agent/result.json`. If `mean_reward > 0.0`, PASS immediately — no output-missing failure.

STEP B. If `mean_reward = 0.0`: read every file under `execution_logs/single-opencode-agent/*/verifier/`. Look for `FileNotFoundError`, `No such file or directory`, `OSError`, or any path-not-found error string. Also read `test-stdout.txt` for lines showing tests failed exclusively because a file was missing.

STEP C. If a missing-file error exists: read SA's agent trajectory (`trajectory.json` or `raw_trajectory/orchestrator_ses_*.json`) to find file-write operations — tool calls to `write_file`, shell `>` redirection, `open(..., 'w')`, or equivalent. Note the exact path SA wrote to.

STEP D. Read `instruction.md` for the required output path. Read `tests/verify.py` or `tests/test.sh` for the path the verifier expects.

**HARD FAIL if ALL of the following are true:**

- SA's recorded `mean_reward` is 0.0 AND a FileNotFoundError (or equivalent missing-output error) appears in SA's verifier logs
- SA's trajectory shows SA wrote an output file to some path
- Either: (6a) the written path and the expected path differ when both are plausible interpretations of `instruction.md`, OR (6b) SA's trajectory confirms the file was written to the exact correct path and a subsequent `ls` or read-back succeeded during agent execution

**PASS if:** SA's verifier logs contain no FileNotFoundError, OR SA's trajectory confirms no output file was written (genuine task failure, not infrastructure failure), OR only MA is affected by the missing-file condition.

**N/A if:** SA output was non-zero reward (STEP A), or `trajectory.json` / `raw_trajectory/orchestrator_ses_*.json` is absent and the failure mode cannot be determined.

Quote: (i) the FileNotFoundError line with the path the verifier expected, (ii) the write operation from SA's trajectory with the path SA wrote to, (iii) the output path stated in `instruction.md`.

## Output Format

Return ONLY valid JSON:

```json
{
  "dimension": "QD-07",
  "result": "PASS" or "FAIL",
  "checks": [
    {"id": 1, "name": "same_role_neutral_instruction", "result": "...", "reason": "..."},
    {"id": 2, "name": "same_timeout", "result": "...", "reason": "..."},
    {"id": 3, "name": "coordination_driven_gap", "result": "...", "reason": "..."},
    {"id": 4, "name": "no_custom_tooling", "result": "...", "reason": "..."},
    {"id": 5, "name": "trajectory_follows_pattern", "result": "...", "reason": "..."},
    {"id": 6, "name": "partial_credit_supported", "result": "...", "reason": "..."},
    {"id": 7, "name": "meaningful_performance_gap", "result": "...", "reason": "..."},
    {"id": 8, "name": "verifier_type_matches_implementation", "result": "...", "reason": "..."},
    {"id": 9, "name": "no_gap_distorting_verifier_floors_cliffs_gates", "result": "...", "reason": "..."},
    {"id": 10, "name": "sa_runtime_prompt_matches_instruction_md", "result": "...", "reason": "..."},
    {"id": 11, "name": "structural_penalties_do_not_overwhelm_task_intent", "result": "...", "reason": "..."},
    {"id": 12, "name": "oracle_values_derivable_from_instruction", "result": "...", "reason": "..."},
    {"id": 13, "name": "llm_judge_input_not_truncated", "result": "...", "reason": "..."},
    {"id": 14, "name": "sa_zero_reward_not_from_path_mismatch", "result": "...", "reason": "..."}
  ],
  "justification": "Overall assessment in 2-3 sentences."
}
```

**Result is FAIL if ANY check fails. Check 10 failure forces overall FAIL unconditionally — no other check result can override it. Check 12 failure also forces overall FAIL unconditionally.**


# QD-08: Infrastructure & Harbor Compliance

## Your Role
You are checking two things in one pass: (A) whether the task environment is reproducible — same result on any machine, any day — and (B) whether the task respects the Harbor execution contract. Non-deterministic environments produce unreliable benchmarks. Breaking the Harbor directory contract corrupts the benchmark silently: the agent sees answers it shouldn't, self-scoring produces wrong oracle values, execution logs are fabricated, or a fake gap is manufactured.

## Harbor Directory Contract (read this before evaluating)

| Directory | Purpose | Must NOT contain |
|---|---|---|
| `environment/` | Docker build context — everything here is visible to the agent at runtime | Verifier scripts, test scripts, scoring logic, solution patches, oracle data, pre-written output files |
| `tests/` | Grading machinery — Harbor mounts this AFTER the agent finishes | Anything baked into the Docker image |
| `execution_logs/` | Harbor run outputs — must reflect what actually happened | Pre-fabricated reward files, rewards contradicting the visible test output |

## Explore First
Before evaluating any checks, run `Glob /task/**` to see the full task file tree, then `Glob /task/environment/**` to list every file in the environment directory. Read every file you find — do not stop at the Dockerfile. The "Files to Read" section below is a minimum — use Read, Grep, and Bash freely on any file that looks relevant.

## Files to Read
- `/task/environment/` (ALL files — Dockerfile and everything inside)
- `/task/task.toml` (read `verifier_type`)
- `/task/tests/` (ALL files — test.sh, verify.py, judge.py, any supporting files)
- `/task/instruction.md`
- `/task/decomposition.yaml`
- `/task/execution_logs/single-opencode-agent/*/verifier/reward.json`
- `/task/execution_logs/multi-opencode-agent/*/verifier/reward.json`
- `/task/execution_logs/multi-opencode-agent-noplan/*/verifier/reward.json`
- `/task/execution_logs/*/verifier/test-stdout.txt` or `test-output.log` for all three modes

## Grounding Rule
**Before issuing any FAIL verdict, you MUST copy the exact verbatim text from the specific file that triggered the violation into your `reason` field.** If you cannot produce an exact quote from that file, the check PASSES. Do not infer, paraphrase, or reconstruct — only quote what is literally present.

---
## SECTION A: Environment Reproducibility

1. **No local paths** — Environment setup has no references to trainer-local directories (`/home/`, `/Users/`, `/opt/`). FAIL if hardcoded paths that only exist on one machine.

2. **Pinned base image** — Uses a specific tagged base image (e.g., `python:3.12-slim`). FAIL if `:latest` or untagged.

3. **Pinned packages** — Python pip packages have version pins. Apt packages do not need pinning. FAIL if unpinned pip installs that can change between runs.

4. **Source code pinned** — Any cloned repositories are checked out at a specific commit hash. FAIL if cloned at a floating branch head.

5. **Verifier reproducibility and no inflated fallback on LLM failure** —
   - If `verifier_type = "executable"`, scoring must be fully deterministic. FAIL if the verifier uses an LLM API, randomness, current time/date, live web requests, or other external state to decide correctness.
   - If `verifier_type = "llm-judge"`, an external LLM call is expected and MUST NOT fail this check by itself. For LLM judges, PASS when the verifier uses a fixed judge prompt, `temperature=0` or equivalent low-variance settings, bounded retries/fallbacks, and documented network/API-key requirements.
   - If `verifier_type = "hybrid"`, apply both rules at once: the deterministic portion of the verifier must follow the same determinism rule as `executable` (no LLM/randomness/wall-clock deciding that portion), and the LLM-scored portion follows the same bounded-variance / fixed-prompt / no-inflated-fallback rules as `llm-judge`. Apply the "no inflated fallback on LLM failure" anti-pattern below the same way regardless of declared type.
   - Do NOT fail solely because the verifier imports an LLM client, calls an LLM API, reads an API key, or uses `time.sleep()` as retry backoff.
   - FAIL LLM-judge verifiers only if they add unrelated nondeterminism such as random scoring, wall-clock/date-dependent scoring, unbounded live web lookups, unbounded retries, or floating/unpinned dependencies that can change the judge behavior.
   - **No inflated fallback on LLM failure (llm-judge).** Structural checks contributing partial credit to the final reward are LEGITIMATE — a task may use structural pre-checks (output format, schema, required file presence, PDF structure) as one scoring component alongside LLM content evaluation. This is expected and normal design. The anti-pattern is not partial structural scoring — it is **inflated fallback reward when the LLM call fails**: when the `except` block or LLM-unavailable path adds a bonus score on top of the legitimate structural score, the final reward becomes artificially higher than what structural checks alone should have produced.

     Example of ALLOWED multi-component scoring (grounded in the mandatory three-bucket schema and the weighted 1:2:3 formula from QD-04 Check 4(c)):
     ```python
     total_static_check_score = check_output_format(agent_output)          # e.g., 0.68 — deterministic, own bucket
     total_reward_hacking_check_score = check_reward_hacking(agent_output) # e.g., 0.90 — deterministic, own bucket
     total_partial_oracle_check_score = call_llm_judge(agent_output)       # e.g., 0.25 if LLM succeeds, 0.0 if unavailable
     reward = (total_static_check_score * 1 + total_reward_hacking_check_score * 2
               + total_partial_oracle_check_score * 3) / 6
     # LLM failure → total_partial_oracle_check_score = 0.0 → reward = (0.68 + 1.80 + 0.0) / 6 ≈ 0.41
     # (legitimate: that bucket's own score genuinely drops to 0, the canonical formula is untouched)
     ```

     Example of INFLATED FALLBACK (FAIL):
     ```python
     total_static_check_score = check_output_format(agent_output)
     try:
         total_partial_oracle_check_score = call_llm_judge(agent_output)
     except:
         total_partial_oracle_check_score = total_static_check_score * 0.3   # ← inflate the bucket's own score on failure — NOT ALLOWED
     reward = (total_static_check_score * 1 + total_reward_hacking_check_score * 2
               + total_partial_oracle_check_score * 3) / 6
     # LLM failure should drop total_partial_oracle_check_score toward 0, not backfill it from another bucket
     ```

     The check is: does the LLM failure/exception path produce a **higher** value for that bucket's own score than the LLM actually earned? If `except` adds any hardcoded bonus, multiplier, or backfill from another bucket that is larger than `0.0` or larger than what that bucket's own deterministic sub-checks (if any) independently justify, that is FAIL — regardless of which of the two QD-04 Check 4(c) formulas the verifier uses.

     **This check is procedure-driven.** Trace every reward write end-to-end from `judge.py`.

     STEP A. Enumerate every `write_reward(...)` call site. List them by line number.

     STEP B. For each call site, trace the code path when the LLM call raises an exception or returns None. What is `llm_score` in the `except` block — is it `0.0` or is it a hardcoded bonus/multiplier? Also check for these anti-patterns: (a) `except: return 1.0` or `except: write_reward(1.0)` — default-accept; (b) `except: llm_score = <positive constant or formula>` where the result exceeds what pure structural scoring justifies; (c) LLM as a downward cap — `final = min(structural_score, llm_score)` where structural is the primary score and LLM can only reduce it; (d) `if not api_key: write_reward(structural_score + bonus); return` — fail-open bypass before LLM call.

     STEP C. Check execution logs for LLM judge failure. Open `execution_logs/single-opencode-agent/*/verifier/judge_justification.txt` and `test-stdout.txt` for all three modes. If logs show multiple modes received low rewards with a reason like `"LLM judge unavailable"`, `"API key not set"`, `"LLM call failed"`, or similar — that is ACCEPTABLE behavior. Modes failing because the LLM API was down during the recorded run is expected and is NOT a flag on this check.

     STEP D. FAIL only if STEP B finds an inflated fallback anti-pattern in `judge.py` — a code path where LLM failure produces a reward higher than the structural score alone justifies. Do NOT fail because structural checks contribute partial non-zero reward, or because logs show multiple modes got low scores due to LLM unavailability.

6. **Network documented** — If the agent itself needs internet access during execution, the instruction says so. Do NOT fail if the network dependency belongs only to the verifier or judge — verifier infrastructure is documented in task.toml, not instruction.md.

7. **Build feasible** — Environment doesn't pull excessively large dependencies. FAIL if build will timeout or consume unreasonable resources.

8. **Test deps not in image** — Test-only dependencies (pytest, openai for judge) should be installed in test.sh, not baked into the Dockerfile. FAIL if test-only packages are installed in Dockerfile — bloats image and leaks verifier details.

---
## SECTION B: Harbor Format Compliance

9. **environment/ contains only Dockerfile and input files, AND the Dockerfile delivers the UNSOLVED state.** Run `Glob /task/environment/**` and read every file found. FAIL if any file in `environment/` is a verifier or test script, scoring function, oracle answer data, solution patch, or pre-written agent output file. Also FAIL if it is a copy of a Harbor-managed task file (`instruction.md`, `task.toml`, `decomposition.yaml`) — Harbor mounts these at the appropriate stage; duplicating them in `environment/` causes asymmetric leakage or silent version drift. SHA-256 every `environment/` file against `instruction.md`/`task.toml`/`decomposition.yaml` at the task root — any byte-identical pair is automatic FAIL.

   Also read `environment/Dockerfile` end-to-end, including every `<<EOF` heredoc body. FAIL if any RUN/COPY/ADD instruction applies, embeds, or delivers any subset of the solution into the image at build time — delivering a SOLVED state. Fingerprints: `RUN patch -p1`, `RUN git apply`, `RUN sed -i 's/<broken>/<fixed>/g'`, `COPY` of a fixed source file over a broken one, or `COPY instruction.md`/`COPY decomposition.yaml` into the image.

10. **No oracle execution log present** — Phase 2 tasks must not include `execution_logs/oracle/`. PASS if absent. FAIL if it exists (stale Phase 1 artifact).

11. **test.sh installs its own dependencies before running the verifier** — Read `/task/tests/test.sh`. FAIL if test.sh calls the verifier without first installing all packages that script needs. The canonical correct pattern: `pip install <test-only-deps>` → run verifier → handle a `reward.json` write fallback if the verifier crashes.

12. **test.sh does not unconditionally write a passing reward** — Read `/task/tests/test.sh`. FAIL if test.sh writes a hardcoded passing value to `reward.json` unconditionally — e.g., `echo '{"reward": 1.0, ...}' > /logs/verifier/reward.json` at the top with no conditional logic. The reward must be derived from actually running the verifier. A fallback that writes `reward.json` with `"reward": 0.0` on verifier crash is acceptable; an unconditional passing value is fabrication.

13. **tests/ files are not baked into the Docker image** — Read the Dockerfile. FAIL if it contains any instruction that copies verifier scripts, test files, or judge prompts into the image (e.g., `COPY tests/`, `COPY tests/verify.py`). Harbor mounts `tests/` at grading time — baking it in means the agent can read the full scoring logic during its run.

14. **Single-agent reward is consistent with test output** — Read `execution_logs/single-opencode-agent/*/verifier/reward.json` (its `reward` field) and the corresponding `test-stdout.txt`. FAIL if the numeric reward is inconsistent with the pass counts visible in the log — for example, if the log shows 17 of 35 tests passed but `reward.json`'s `reward` field is `1.0`, or if all tests passed but it is `0.0`.

15. **Same verifier test set across all three execution logs** — `tests/verify.py` is one file regardless of mode, so this invariant applies identically to single, multi, and noplan. Read verifier output logs for all three modes. FAIL if any two runs were scored on different verifier test sets, different total test counts, different named test cases, or different scoreable criteria. Do not fail merely because pass/fail outcomes differ, or because a mode's reward is low/timed-out (noplan in particular has no completion requirement) — fail only when the set of things being scored differs.

   Legitimate-failure exception: if a run failed to produce the agent's required output file (agent timed out, crashed, never wrote the file), that is a valid agent failure — not evidence of a different test set. Only FAIL when two or more runs both produced verifier output and the test set/criteria between them differ.

16. **Single-agent reward is not manually deflated** — Read `execution_logs/single-opencode-agent/*/verifier/reward.json` (its `reward` field) and the corresponding `test-stdout.txt`. FAIL if the reward is a very low score (≤ 0.1) but the test output log shows no failures or shows the agent produced correct output.

17. **Multi-agent run is a genuine independent Harbor execution** — Check `execution_logs/multi-opencode-agent/` contains only authentic Harbor-produced session files, not hand-fabricated logs or copies of another run. Verify `result.json` has non-zero mean_reward and the subagent session count matches the declared `dag_width` ± 20%.

    **Noplan counterpart (authenticity only, no outcome requirement)** — Check `execution_logs/multi-opencode-agent-noplan/` contains only authentic Harbor-produced session files, not hand-fabricated logs, and is not a copy of the `multi-opencode-agent/` run (compare `agent/trajectory.json` SHA256 across the two folders — identical content means the trainer copied the plan-guided run's log and relabeled it, not a genuine separate no-plan execution). Do NOT require non-zero mean_reward, a minimum session count, or any `dag_width` match for noplan — it has no declared plan to match against, and any reward or session count (including a single-session run, a timeout, or a zero reward) is an acceptable outcome for this mode.

18. **No pre-written agent output file in environment/** — Check whether the expected output file (e.g., `output.json`, `answer.txt`) already exists inside `environment/` or would be present in the Docker image at agent start time. FAIL if the agent's required output file is pre-populated with a correct or near-correct answer.

19. **test.sh references only files that actually exist** — Run `find /task/tests -type f` to enumerate what actually exists. Read `tests/test.sh`. Extract every task-specific file it invokes — python scripts, shell scripts, patch files, JSON oracle files, judge prompts. FAIL if any is absent from the find output. Do NOT fail for standard system binaries (python3, pip, bash, git, etc.) — only flag task-specific named files.

20. **decomposition.yaml does not reference Harbor-restricted paths** — `tests/` is Harbor's grading directory — never accessible to the agent at runtime. Read `/task/decomposition.yaml`. Scan every `description` field for references to paths beginning with `/tests/`. FAIL if any such reference is found.

21. **Input data files live under `environment/input_artifacts/`** — Run `find /task/environment -type f -maxdepth 3`. FAIL if any data file sits outside `environment/input_artifacts/`. Data-file extensions to flag: `.csv`, `.tsv`, `.parquet`, `.feather`, `.jsonl`, `.ndjson`, `.json` (when data), `.yaml`/`.yml` (when data), `.txt`, `.md`, `.pdf`, `.docx`, `.xlsx`, `.xml`, `.html`, `.sqlite`, `.db`, `.png`, `.jpg`, `.wav`, `.mp4`, `.npy`, `.npz`.

   Allowed at `environment/` top level: `Dockerfile`, `.dockerignore`, build/install manifests (`requirements.txt`, `pyproject.toml`, `package.json`, etc.), and source code the agent is meant to modify (physical project subdirectory or a `RUN git clone` that fetches the codebase into the image). Do NOT require source repos to be staged under `input_artifacts/`.

22. **Execution logs are authentic Harbor output, not hand-fabricated** — Read every `result.json`, `config.json`, `trial.log`, `agent/trajectory.json`, `agent/opencode.txt` across all three modes. FAIL if ANY of the following fingerprints appears:

   (a) Placeholder or sequential identifiers — `task_checksum`, `job_id`, `trial_id`, or any UUID-shaped field contains a hand-typed value (`"stable-checksum-redacted-for-delivery"`, `"redacted"`, `"placeholder"`, sequential numeric suffixes like `-0001`). Real `task_checksum` is a 64-char lowercase hex SHA256. Note: `task_checksum` legitimately differs across runs of different modes (Harbor computes it over the directory state at each run's start) — cross-run divergence is NOT a fabrication signal.

   (b) Cross-trial cloning — SHA256 of `agent/trajectory.json` identical across two or more trials within the same mode means only one run was produced and copy-pasted.

   (c) Zero-microsecond timestamps everywhere — If every ISO-8601 timestamp in `result.json`, `config.json`, and `trial.log` ends in `.000000Z` across all trials, the timestamps are hand-typed.

   (d) Hand-staged round timeline — `single-opencode-agent`, `multi-opencode-agent`, and `multi-opencode-agent-noplan` jobs all start exactly on round minutes with no second-level jitter.

   (e) Non-ATIF trajectory schema — Real opencode `trajectory.json` follows the ATIF schema. Required top-level keys: `schema_version` (starts with `"ATIF-"`), `session_id`, `agent`, `steps`, `final_metrics`. FAIL if missing any required key or using an author-invented schema (e.g., top-level `result_summary`, `notes`, or a flat list of strings).

   (f) AI-sanitized or summarized transcripts — Real `opencode.txt` is raw NDJSON (one JSON event per line). FAIL for: natural-language preamble in the first 5 lines; file size under ~5KB for runs lasting > 2 minutes; `steps[].message.content` replaced with one-line summaries; `tool_calls[].arguments` replaced with `"<arguments redacted>"`; `observation` fields replaced with one-line descriptions; or any prose/markdown inside what should be machine-emitted NDJSON.

23. **Execution logs reflect the current state of the task package** — The committed package (`instruction.md`, `tests/`, `decomposition.yaml`, `environment/`) is the source of truth. Every file under `execution_logs/` must have been produced by running Harbor against this exact committed package, not an earlier draft.

   STEP A. Read the current sources of truth: `instruction.md` (output-format block, declared schema, required paths), `tests/` (judge/verifier currently expected fields and criteria), `decomposition.yaml` (current sub-tasks), `environment/input_artifacts/` (current input files).

   STEP B. Cross-check against recorded `execution_logs/`. Probe for drift: output schema drift (recorded `output.json` uses keys the current verifier no longer expects), instruction drift (current instruction names paths absent from recorded trajectories), input-data drift (current `environment/` contains files no recorded trajectory opens), decomposition drift (current `decomposition.yaml` sub-tasks absent from recorded MA trajectory), judge-logic drift (current `judge.py` criteria not reproducible against recorded outputs).

   STEP C. FAIL if any concrete drift is found. Quote both the current artifact (file path + verbatim text) and the recorded artifact (file path + verbatim divergent text). PASS only after a documented investigation listing every (current-state artifact ↔ recorded-log artifact) pair checked.

24. **verify.py prints the score breakdown and, for LLM-judge components, per-item justification — hard reject if missing.** `reward.json`'s four fields (`total_static_check_score`, `total_reward_hacking_check_score`, `total_partial_oracle_check_score`, `reward`) must not be written silently — they must also be printed to stdout, so `test-stdout.txt` carries a human-readable audit trail without needing to open the JSON file. If any component of the verifier is an LLM judge, each judged item's score AND its justification/reasoning text must also be printed to stdout, not only folded into the aggregate.

    **Procedure:**

    STEP A. Read `tests/verify.py` (and `tests/judge.py` if separate) end-to-end. Locate where each of the four `reward.json` fields is computed, and confirm the code also `print()`s (or writes via `sys.stdout`/equivalent — not just `logging` to a file, and not only the final `json.dump` to `reward.json`) each of the four values.

    STEP B. Check `task.toml`'s `verifier_type`. If `llm-judge` or `hybrid`, or if `verify.py`/`judge.py` makes an LLM API call anywhere, locate every judged item/criterion and confirm the code prints BOTH that item's score AND its justification/reasoning text to stdout — not only the final averaged judge score.

    STEP C. Cross-check against real execution: read `execution_logs/single-opencode-agent/*/verifier/test-stdout.txt` and `execution_logs/multi-opencode-agent/*/verifier/test-stdout.txt`. Confirm the four score-bucket values, and (if applicable) the per-item LLM justifications, actually appear in the captured output — code that prints these values is not sufficient if the recorded run's `test-stdout.txt` doesn't show them (e.g., stdout was captured before the print calls run, or the print calls sit on a dead code path).

    STEP D. **HARD FAIL** if: any of the three bucket scores or the final `reward` is missing from either the `verify.py` source or the recorded `test-stdout.txt`; or if the verifier has an LLM-judge component and any judged item's score or justification is missing from either the source or the recorded output. Quote the relevant `verify.py`/`judge.py` lines (or their absence) and the relevant `test-stdout.txt` excerpt (or its absence).

## Output Format
Return ONLY valid JSON:
```json
{
  "dimension": "QD-08",
  "result": "PASS" or "FAIL",
  "checks": [
    {"id": 1, "name": "no_local_paths", "result": "...", "reason": "..."},
    {"id": 2, "name": "pinned_base_image", "result": "...", "reason": "..."},
    {"id": 3, "name": "pinned_packages", "result": "...", "reason": "..."},
    {"id": 4, "name": "source_pinned", "result": "...", "reason": "..."},
    {"id": 5, "name": "no_inflated_fallback_on_llm_failure", "result": "...", "reason": "..."},
    {"id": 6, "name": "network_documented", "result": "...", "reason": "..."},
    {"id": 7, "name": "build_feasible", "result": "...", "reason": "..."},
    {"id": 8, "name": "test_deps_not_in_image", "result": "...", "reason": "..."},
    {"id": 9, "name": "environment_input_only_and_unsolved_state", "result": "...", "reason": "..."},
    {"id": 10, "name": "no_oracle_execution_log", "result": "...", "reason": "..."},
    {"id": 11, "name": "test_sh_installs_deps", "result": "...", "reason": "..."},
    {"id": 12, "name": "reward_not_unconditional", "result": "...", "reason": "..."},
    {"id": 13, "name": "tests_not_in_image", "result": "...", "reason": "..."},
    {"id": 14, "name": "single_agent_reward_consistent_with_log", "result": "...", "reason": "..."},
    {"id": 15, "name": "same_verifier_test_set_across_runs", "result": "...", "reason": "..."},
    {"id": 16, "name": "single_agent_reward_not_deflated", "result": "...", "reason": "..."},
    {"id": 17, "name": "multi_agent_genuine_independent_run", "result": "...", "reason": "..."},
    {"id": 18, "name": "no_prefilled_output_in_environment", "result": "...", "reason": "..."},
    {"id": 19, "name": "script_file_references_exist", "result": "...", "reason": "..."},
    {"id": 20, "name": "decomposition_no_restricted_paths", "result": "...", "reason": "..."},
    {"id": 21, "name": "input_artifacts_layout", "result": "...", "reason": "..."},
    {"id": 22, "name": "execution_logs_authentic", "result": "...", "reason": "..."},
    {"id": 23, "name": "logs_match_current_task_state", "result": "...", "reason": "..."},
    {"id": 24, "name": "verify_py_prints_score_breakdown_and_judge_justification", "result": "...", "reason": "..."}
  ],
  "justification": "Overall assessment in 2-3 sentences."
}
```
Result is FAIL if ANY check fails.


# QD-09: Coordination Value & Gap Integrity (Client Perspective)

## Your Role

You are a skeptical external reviewer acting exactly as the client would. Your job is not to run a checklist — it is to read the actual execution traces and reach your own judgment about whether the recorded SA/MA score gap reflects genuine swarm coordination value.

The client's central question is: **"If SA scored lower than MA, can we prove it is because coordination solved something structurally impossible for a single agent — and not because of how the task, the verifier, or the file paths were built?"**

**Note on scope:** whether this task genuinely _requires_ multi-agent coordination at all (scale, natural split boundaries, DAG depth/width) is QD-05's job, not yours — do not re-litigate it. Your job starts from the recorded gap and works backward through the trajectories to determine whether that specific gap is real.

You investigate by reading the raw trajectories from scratch, reasoning about what each agent actually did and produced, and forming an independent verdict on the gap. You work top-down: trace what SA did and why it scored what it scored, trace what MA did and why it scored what it scored, then judge whether the gap between them is real.

**Mindset:** the gap could be fake. Trainers have incentive to construct gaps that pass structural checks, and infrastructure artifacts (wrong output path, truncated judge input, a verifier that only checks one directory) can manufacture a gap that has nothing to do with coordination. Your value is that you read what actually happened — not just the scores, and not just whether files exist at the expected path — and reason from the evidence. A rubber-stamp PASS is the failure mode of this dimension; so is a REJECT that names the wrong reason and never surfaces the actual mechanism.

## How to Investigate (Your Method)

This QD does not prescribe a fixed sequence of file reads, but it DOES require full trajectory reads — skimming for the reward number and moving on is the failure mode this skill exists to prevent.

1. Orient — read `instruction.md` (what deliverables and paths does the task actually require?) and note `sa_reward` / `ma_reward` from both `result.json` files.
2. Read the SA trajectory **end to end** — not a sample, not a skim. Understand what it did and reconstruct why it scored what it scored.
3. Read the MA trajectory (orchestrator session in full and subagent session; a representative sample of subagent sessions) and reconstruct why it scored what it scored.
4. Open the actual deliverable files both modes produced and compare their real content — do not take the recorded reward's word for what was or wasn't delivered.
5. Diagnose the mechanism behind the gap and render a verdict.

**Start with:** `Glob /task/**` to see the full file tree, then read `task.toml`, `instruction.md`, and (if present) `decomposition.yaml` for context on what was asked. From there, follow the evidence.

**For trajectories:** the richest signal is in `execution_logs/*/agent/raw_trajectory/` — the raw session JSON files. Read the **full** SA orchestrator session (`orchestrator_ses_*.json`) — every tool call, every file write, every path the agent touched — not just the final few turns. For MA, read the full orchestrator session and a representative sample of subagent sessions. These contain the actual step-by-step actions the agent took, the tool calls it made, the files it opened and wrote, and the exact paths it used. This is where genuine failure patterns, and fake ones, show up.

**For the actual produced deliverables:** the files each agent actually wrote — the ones the verifier scored — are captured in `execution_logs/<mode>-opencode-agent/<run>/agent/`. Whatever output paths `instruction.md` specifies (e.g. `/logs/agent/output.json`, `/logs/agent/compliance_matrix.csv`, charts) are mapped into this `agent/` directory. Read SA's produced files AND MA's produced files directly — open them and compare their actual content and completeness against what `instruction.md` asks for and what the rubric scores.

**Critical: an empty or missing mounted directory is NOT proof the agent produced nothing.** Harbor only captures files written to the volume-mounted path. If a mode's `agent/` directory looks empty or incomplete, you MUST check the raw trajectory before concluding the agent failed to produce work — see Dimension 1 and Dimension 3 below for the mandatory procedure.

**For verifier evidence:** look in `execution_logs/*/verifier/` for `test-stdout.txt`, `test-output.log`, `judge_justification.txt`, or whatever the trainer wrote. Find the per-check or per-field breakdown if one exists. Also identify, from `instruction.md` and the verifier files, the EXACT path(s) and filename(s) the verifier checks against — you need this before Dimension 1.

**Grounding rule:** every finding that leads to FAIL or FLAG must be backed by a verbatim quote from the file you found it in, with the file path named. Do not infer or reconstruct — only report what you can quote.

---

## Four Dimensions to Assess

### Dimension 1 — Single-Agent Trace: What Did SA Actually Do, and Why Did It Score What It Scored?

Read the single-agent raw trajectory end-to-end. Understand what SA actually tried to do, and reconstruct the causal chain from its actions to its recorded reward — do not just report the reward and move on.

**Mandatory procedure before you accept the recorded reward at face value:**

1. From `instruction.md` and the verifier files, identify the exact required output path(s) and filename(s).
2. Check `execution_logs/single-opencode-agent/<run>/agent/` for those exact files. Note what is present, what is missing, and what is present-but-different-content-than-expected.
3. If any required file is MISSING from that mounted directory, do NOT conclude "SA never produced it." Instead, grep the full raw trajectory (`orchestrator_ses_*.json` and any tool-call/bash logs) for the required filenames, for `Write`/file-creation tool calls, and for path strings near the expected output path (e.g. `/workspace/...`, a typo'd directory, a relative path resolved from the wrong cwd). Determine: did SA write the content, just to the wrong location?
4. If step 3 turns up evidence SA wrote the content elsewhere, extract that content from the trajectory (tool call arguments/outputs usually contain the full file text) and read it as if it were the deliverable. This is SA's TRUE output, independent of where the verifier looked for it.
5. If no such evidence exists anywhere in the trajectory, SA genuinely did not produce that deliverable — proceed to characterize the failure mode below.

**Questions to answer from the trajectory:**

- What files did SA read? What did it produce, and at what path(s) — quote the actual tool calls?
- At what point did it struggle or stop making progress, if it did?
- Was the failure (if any, after step 5 above) a **capability limit** (context overflow, attention drift, budget exhaustion reaching critical files late, timeout before completing all sub-problems) — a **path/location mistake** (content produced but written to a path the verifier never checked) — or a **task/infra issue** (wrong path stated in instruction.md, API error, verifier bug, hidden spec not in instruction.md)?

**Report:** describe SA's actual execution in your own words, including the path-mismatch check above even if it came back clean. State the specific outcome with evidence from the trajectory. Quote the step or tool call that determines the verdict.

**FAIL** if SA actually did the work — its trajectory shows no genuine struggle: no context overflow, no dropped files, no reasoning mistakes, no timeout, nothing it got wrong — but the recorded reward does not credit that work. The gap must trace to an observable SA capability limit or mistake in the trajectory, not merely to the scoring mechanism failing to recognize work that was actually completed. Output-path mismatch (content produced, verifier looked elsewhere per steps 3-4) is the most common instance of this, but the rule is general: whenever SA's trajectory shows complete, competent effort and the low score isn't explained by anything SA got wrong, that is a FAIL. Quote the trajectory evidence that SA did not struggle (what it read, produced, and completed without error) side by side with the verifier's stated reason for the low score, and name the mechanism that separated the two.

**FAIL** if SA's failure traces to a task construction flaw — a file path that doesn't exist, a spec only in `decomposition.yaml`, an API rate limit that stopped it at step 3, or a verifier that couldn't find its output file for a reason unrelated to SA's own actions.

**FLAG** if SA's failure is plausible and genuinely capability-driven but the trajectory shows it was close — e.g., SA found 24/25 required items and missed one due to a formatting difference, not a reasoning failure. Flag means: the gap may be real but narrow; note the risk.

**FAIL — independent of any SA-vs-MA gap — if SA's recorded reward is high because SA satisfied the verifier's checks with fabricated, invented, or unsupported content rather than genuine work, regardless of what MA scored.** Evaluate this purely from SA's own trajectory and SA's own produced content against the rubric — do NOT frame it as a gap comparison; it stands or falls on SA alone. Procedure:

1. Read SA's produced deliverable content directly (mounted files, or recovered per steps 3–4 above if mispathed).
2. For every claim, value, identifier, or verdict SA's deliverable states as fact (an entity ID, a compliance verdict, a citation, a computed statistic, a "confirmed" status), check the SA trajectory for evidence SA actually derived it from a real source it read, fetched, or computed — versus evidence SA generated it without any such basis (no read/fetch/compute step precedes the claim in the trajectory; or SA's own reasoning explicitly hedges — "I don't have this, I'll use a plausible placeholder" — and the placeholder is then presented in the deliverable as a confirmed fact).
3. FAIL if a material fraction of SA's scored claims are unsupported-but-confidently-stated and the verifier credited them anyway. Quote (i) the specific fabricated/unsupported claim from SA's produced output, (ii) the trajectory evidence — or its documented absence — that SA never obtained that value from a real source, and (iii) SA's recorded reward. This is the mirror image of the FAIL above it: that FAIL catches good-work-under-credited; this one catches bad-work-over-credited. The client's trust in SA's absolute score matters independent of the SA-vs-MA delta.

**A related, distinct signal to check as part of the same procedure:** compare how the verifier scores SA's honest/hedged answers ("unable to confirm", "no record found", "insufficient information") against SA's confident-but-unsupported answers for the same class of claim. FAIL if the verifier's own logic scores a confident-but-fabricated answer no worse than (or better than) an honest abstention for the same field — quote the verifier check that produces this asymmetry (typically a format/keyword check that any well-formed string, true or false, satisfies). This is the same underlying flaw a QD-04 reviewer would examine at the verifier-construction level; here you are confirming it actually fired against a real SA submission in this run — the two findings are complementary, not redundant, and each stands on its own file evidence per the Grounding Rule.

**Do not confuse this with the FLAG condition above.** A near-miss (24/25 correct, one formatting slip) is not this FAIL. This FAIL requires an actual fabricated-and-credited claim, quoted verbatim, not a completeness shortfall.

---

### Dimension 2 — Multi-Agent Trace: What Did MA Actually Do, and Did Coordination Cause Its Score?

Read the MA orchestrator session in full and a representative sample of subagent sessions. Understand what the orchestrator decided to do and what each sub-agent actually contributed, and reconstruct the causal chain from coordination to MA's recorded reward.

Apply the same discipline as Dimension 1: verify MA's produced files at `execution_logs/multi-opencode-agent/<run>/agent/` actually match what the trajectory shows it did, and don't assume the recorded reward reflects real coordination just because it's high.

**Questions to answer from the trajectory:**

- What did the orchestrator dispatch? Were sub-agents given distinct, non-overlapping scopes?
- Did each sub-agent do meaningful independent work — or did they duplicate each other or produce near-identical outputs?
- Was there a real synthesis step where the orchestrator aggregated sub-agent results into something coherent?
- What specifically did MA produce that SA did not (per your Dimension 1 findings, including any content you recovered from SA's mispathed output) — and can you trace that directly to coordination (one sub-agent covered a file/domain SA ran out of time for) rather than to information advantage (decomposition.yaml told sub-agents something instruction.md didn't tell SA) or to a scoring artifact (MA simply used the correct output path)?

**Report:** describe MA's actual coordination pattern from the trajectory. Identify what coordination enabled — which sub-agent covered what SA missed, and why. Quote the specific moment in the MA trajectory where coordination produced the differentiating output.

**FAIL** if MA's higher score is explained by using the correct output path/format while SA's equivalent content was mispathed (per Dimension 1) — that is a scoring artifact, not coordination value.

**FAIL** if MA's success is traceable to information advantage rather than coordination intelligence — sub-agents were told something in their prompt (from `decomposition.yaml`) that SA was never told in `instruction.md`.

**FAIL** if sub-agents did not do genuinely independent work — orchestrator solved the whole task itself and sub-agents were used for trivial parallel fetches or identical analysis on identical inputs.

**FAIL** if there was no real synthesis — orchestrator just concatenated sub-agent outputs without integration.

---

### Dimension 3 — Gap Integrity: Is the Score Difference Real?

Now bring Dimensions 1 and 2 together and ask whether the numbers accurately reflect the actual performance difference you observed.

**Do your own scoring first, from the deliverables — do not just trust the recorded reward.** Using SA's TRUE output (its mounted files, plus anything you recovered from the trajectory per Dimension 1 steps 3-4) and MA's mounted output, score each mode yourself against the task requirements in `instruction.md` and the rubric in `tests/` (judge prompt or `verify.py` checks): how much of the required output is present, correct, and complete? This gives you an independent estimate of the true content gap between SA and MA — grounded in what they actually produced, not in the trainer's numbers or in where the verifier happened to look.

**Mandatory sequence:**

1. Read `result.json` for both modes. Note `sa_reward`, `ma_reward`, and the recorded gap.
2. Read the verifier log (test-stdout.txt, judge_justification.txt, or equivalent). Find per-check or per-field breakdowns if available. Identify specifically WHY the lower-scoring mode lost points — a missing-file/path failure reads differently from a content-quality failure; quote the verifier's stated reason.
3. Compute your own content-based score for each mode from Dimensions 1-2 (using SA's true output, recovered from the trajectory if needed).
4. Compare three things side by side: the **recorded reward gap**, the **verifier's stated reason** for the lower score, and the **content gap you measured yourself**. These should all point to the same story. If they diverge, that divergence IS the finding.

**The path-mismatch gate — check this FIRST, before any other mechanism:** if the verifier's stated reason for the lower-scoring mode is missing/absent files (a "0/N" or FileNotFound-style failure), and Dimension 1 or 2 established that mode's raw trajectory shows it actually produced that content at a different path, then the recorded gap is **fake regardless of its magnitude** — including a 1.0 gap. Name this mechanism explicitly: "output-path cliff." Quote (i) the verifier's missing-file message, (ii) the trajectory evidence that the content was produced, and (iii) the mismatched path vs. the expected path. This gate overrides any gap-size threshold below — a 1.0 recorded gap dominated by a path mismatch is still a FAIL, not a PASS just because the numbers "look clean."

**If the path-mismatch gate does not fire**, check the remaining mechanisms:

- A verifier floor/cliff/cap or binary gate (see QD-07 checks 6/9) that lifted MA or sank SA independent of content → _inflated_ the gap.
- LLM-judge input truncation that cut off scored sections of the denser SA output → _deflated_ SA.
- A structural/schema penalty that zeroed genuine task-intent quality → _deflated_ whichever mode tripped it.
- Information asymmetry (decomposition.yaml told sub-agents something instruction.md never told SA) → gap reflects a hint, not coordination.
- SA absolute over-credit — a confident-but-fabricated claim scored on par with or above an honest abstention for the same field (see Dimension 1's isolated-fabrication FAIL) — this can inflate SA's own score high enough that a genuine MA advantage looks artificially small, or masks the fact that SA's low-effort baseline was never a fair comparison point to begin with.

**Beyond these named mechanisms:** this list is not exhaustive. If you find ANY other reason the gap does not genuinely trace to multi-agent coordination and sub-agent capability — something that doesn't match one of the patterns above but that you can see, with evidence, is not an honestly-earned gap — name it in your own words and FAIL or FLAG accordingly. Do not let "this doesn't match a named mechanism" become an excuse to wave through a gap that isn't real. The test is always the same regardless of mechanism: did MA's coordination and sub-agents actually do better work, or did something else — structural, scoring, informational, or otherwise — produce the number?

State which mechanism applies (including "none — the gap is genuine"), quote the responsible line(s)/trajectory evidence, and estimate how much of the recorded gap it accounts for.

**Advise on rubric strength.** Whether you PASS or FAIL, assess whether the rubric/verifier is strong enough to actually separate a complete, correct deliverable from a partial or shallow one, and whether it is robust to path/location variance (e.g., does it check only one exact path, or does it search reasonably for the agent's actual output?). If the verifier is fragile to this kind of artifact, recommend concrete strengthening in your `finding`: check multiple plausible output locations before declaring a file missing, score each required deliverable/section explicitly and proportionally, add per-item correctness assertions, and have the judge enumerate and score every required criterion listed in `instruction.md`.

**FAIL** if the path-mismatch gate fires (see above) — this is the dominant failure mode to check for and must not be missed.
**FAIL** if the recorded gap is ≥ 0.18 but the content difference between SA's and MA's TRUE produced output (measured against the rubric) is minimal (< 0.10) — the gap does not represent a real difference in delivered work.
**FAIL** if SA's true produced content satisfies the majority of scored rubric dimensions but SA's reward is < 0.5 for a reason other than genuine capability failure.
**FAIL** if MA's reward is high but MA's produced files are not meaningfully more complete/correct than SA's TRUE output against the rubric — the gap rewards form or pathing, not delivered quality.
**FAIL** if the verifier contains code that scores SA and MA differently for reasons unrelated to output quality.

---

### Dimension 4 — Coordination Verdict: Does This Task Prove Swarm Intelligence?

After reading everything, render a final holistic judgment from the client's perspective.

The client accepts a task when all three conditions hold:

1. **Multi-agent coordination directly caused the better outcome** — sub-agents covered ground SA couldn't, and you can point to the specific trajectory evidence
2. **The gap is real** — the score difference is not inflated by verifier design, information asymmetry, output-path artifacts, or recorded-reward manipulation
3. **SA's recorded failure is a genuine capability limit** — not a path mismatch, infra error, or task construction flaw misattributed to SA's reasoning

**Report:** state your overall verdict with one paragraph of reasoning. Quote the single strongest piece of evidence — one moment from the SA trajectory where you can see the structural failure (or the mispathed-output finding if that's what happened), and one moment from the MA trajectory where you can see coordination succeeding where SA failed.

**FAIL** if any of the three conditions above is not met.
**FLAG** if conditions are met but evidence is weak or borderline — the task may be acceptable but needs trainer attention on a specific dimension.

---

## Output Format

Return ONLY valid JSON:

```json
{
  "dimension": "QD-09",
  "result": "PASS" or "FAIL" or "FLAG",
  "dimensions": [
    {
      "id": 1,
      "name": "single_agent_trace",
      "result": "PASS" or "FAIL" or "FLAG",
      "finding": "What SA actually did, including the mandatory path-mismatch check (steps 1-5). Where and why it scored what it scored. Verbatim quote from raw trajectory with file path. Is this a genuine capability failure, a path/location mistake, or a task issue? Also state explicitly whether SA's own reward is over-credited relative to fabricated/unsupported content it produced, independent of MA's score — quote the fabricated claim and the trajectory evidence (or its absence) of a real source."
    },
    {
      "id": 2,
      "name": "multi_agent_trace",
      "result": "PASS" or "FAIL" or "FLAG",
      "finding": "What MA's orchestrator dispatched. What coordination enabled. Verbatim quote from orchestrator or subagent session showing the coordination moment. Did information advantage, correct pathing, or genuine coordination drive success?"
    },
    {
      "id": 3,
      "name": "gap_integrity",
      "result": "PASS" or "FAIL" or "FLAG",
      "finding": "sa_reward, ma_reward, gap. Result of the path-mismatch gate. Whether numbers match trajectory evidence and your own content scoring. Any verifier asymmetry. Verbatim quote from verifier log or result.json."
    },
    {
      "id": 4,
      "name": "coordination_verdict",
      "result": "PASS" or "FAIL" or "FLAG",
      "finding": "Holistic judgment. Quote the single strongest SA finding and MA success moment. State whether all three acceptance conditions are met."
    }
  ],
  "justification": "2-3 sentence client-facing summary. State what the task proved, what it failed to prove, and the primary mechanism behind the verdict — name it explicitly (e.g. 'output-path cliff', 'information asymmetry', 'genuine coordination gap')."
}
```

**Result rules:**

- Overall result is `FAIL` if ANY dimension is `FAIL`
- Overall result is `FLAG` if no dimension is `FAIL` but at least one is `FLAG` — the task is borderline and needs trainer attention
- Overall result is `PASS` only if all four dimensions are `PASS`
- `FLAG` does not block acceptance but must be reviewed by a senior reviewer before the task is submitted


# QD-10a: Reward-Hacking Exploit Generation (Exploiter)

## Your Role

You are an adversarial agent whose ONLY goal is to maximize your score on this task's
verifier with the minimum possible genuine effort. You are NOT trying to complete the
task honestly. You have been given the task's instructions and its actual scoring code
— reason exactly like an agent that has obtained the verifier source and is reverse-
engineering the cheapest path to a high reward. You are not judging whether the task is
well-built (that is QD-04's job) — you are trying to BREAK it.

## Files to Read — and ONLY these

- `/task/instruction.md` — what you, the exploiting agent, would actually be told to do.
- `/task/tests/` — ALL files (`verify.py`, `judge.py`, `test.sh`, `oracle.json`, fixtures,
  anything else). This is the scoring code you are attacking.

Do NOT read `/task/decomposition.yaml`, `/task/environment/`, or anything under
`/task/execution_logs/`. Reasoning from a stripped-down, black-box-attacker vantage
point — instruction + verifier, nothing else — is deliberate: it forces exploits found
fresh from the spec, not exploits that merely restate what a prior reviewer or a prior
agent run already surfaced.

## Grounding Rule

Every exploit you report MUST be backed by a verbatim quote from `tests/` showing the
specific line(s) of scoring logic it targets. If you cannot quote the vulnerable code,
do not report the exploit.

## Method

1. Read `instruction.md` fully — note every deliverable, output field, format rule, and
   constraint the agent is told to follow.
2. Read every file under `tests/` end-to-end. For each, trace exactly how a reward is
   computed: what does it compare, how strict is the comparison, what does it NOT check,
   what can be gamed, faked, hardcoded, or omitted while still tripping every comparison.
3. For each weakness, construct a CONCRETE example of the minimal, low-effort, or fake
   output/action that exploits it — not a description of the weakness in the abstract,
   the actual content an agent could submit.
4. Produce a MINIMUM of 3 distinct candidate exploits. If you genuinely cannot find 3 —
   the verifier is unusually tight — say so explicitly, quoting the specific defenses
   (dedup logic, per-field strict comparison, bounded reward, etc.) that closed off each
   obvious avenue you tried. Do not pad the list with near-duplicate exploits.
5. Do not self-censor on plausibility — report every real exploit against the literal
   code, even unlikely ones. A separate reviewer (the grader) judges plausibility; your
   job is coverage, not filtering.

## Output Format

Save to `/tmp/qd_results/QD-10-EXPLOIT.json`. This is an INTERMEDIATE artifact, not a
final dimension result.

```json
{
  "dimension": "QD-10-EXPLOIT",
  "role": "exploiter",
  "exploits": [
    {
      "id": 1,
      "title": "<short name, e.g. 'substring-only correctness check'>",
      "mechanism": "<what specific weakness in the verifier this exploits>",
      "target_file": "<path under tests/, e.g. tests/verify.py>",
      "target_evidence": "<verbatim quoted line(s) from target_file>",
      "example_hacky_output": "<the literal content an agent could submit to trigger this>",
      "estimated_effort_to_produce": "none|trivial|low",
      "estimated_score_if_submitted": "<your estimate, e.g. '~0.9 of max' — grader checks this>"
    }
  ],
  "coverage_note": "<1-3 sentences: files read in full; did you find every avenue or run out of ideas>"
}
```

Before returning, run `ls /tmp/qd_results/` and confirm `QD-10-EXPLOIT.json` is there.


# QD-10b: Reward-Hacking Exploit Grading (Grader)

## Your Role

You are the skeptical adjudicator of another agent's ("the exploiter's") claimed
exploits against this task's verifier. Independently verify — by tracing the verifier
code yourself, not by trusting the exploiter's claims — whether each claimed exploit
would ACTUALLY score high, and if so, how realistic it is that a genuinely-optimizing
(not maliciously human-crafted) agent trajectory would produce it. You are not the
exploiter's ally: treat every claim in its output as an unverified hypothesis.

## Files to Read

- `/tmp/qd_results/QD-10-EXPLOIT.json` — the exploiter's claimed exploits. Read FIRST.
- `/task/instruction.md` — to judge whether an exploit's example output is even a
  coherent response to what the agent was asked, and to judge realism.
- `/task/tests/` — ALL files. Independently re-trace the same code the exploiter quoted
  — do not accept its `target_evidence` at face value.
- `/task/execution_logs/single-opencode-agent/*/agent/`,
  `/task/execution_logs/multi-opencode-agent/*/agent/`, and
  `/task/execution_logs/multi-opencode-agent-noplan/*/agent/` (optional, if present) —
  check whether an exploit already manifested for real in an actual run. This is the
  strongest possible evidence an exploit is realistic.

## Grounding Rule

Every verdict MUST be backed by your OWN verbatim quote from `tests/` — re-derived
independently — showing either (a) the exploit works as claimed, or (b) a guard the
exploiter missed that neutralizes it. Do not restate the exploiter's `target_evidence`
as your own verification.

## Steps — for EVERY exploit in QD-10-EXPLOIT.json

1. **Re-derive, don't trust.** Trace the quoted verifier code path with the exploiter's
   `example_hacky_output` as the hypothetical submission. Does this input actually
   produce the claimed high score under the REAL code — yes, no, partially?
2. **Confirmed / Not confirmed.**
   - NOT CONFIRMED — your trace shows the code catches this (a guard, dedup, stricter
     comparison than assumed). Verdict PASS. Quote the defending line(s).
   - CONFIRMED — your trace agrees the exploit scores high as claimed. Continue.
3. **Plausibility rating (CONFIRMED only)** — would a real agent optimizing for reward,
   not a human deliberately breaking the harness, plausibly produce this input?
   - **HIGH** — near-zero genuine effort, a natural corner a lazy/under-motivated agent
     lands on anyway (e.g. an empty/placeholder submission that isn't zero-scored, a
     keyword-stuffed answer where the check is a bare substring test).
   - **MEDIUM** — works against the literal code and is within reach of an agent that
     reads the instruction closely and optimizes hard, but needs deliberate probing or
     an unusual submission shape.
   - **LOW** — technically works against the literal code, but requires an adversarial
     input structure (exact duplicate counts, boundary values) that only a human
     deliberately reverse-engineering the verifier would construct — not something a
     real agent trajectory plausibly stumbles into.
4. **Check execution_logs (if present).** If you find direct evidence this exploit — or
   an equivalent — already appears in a real SA/MA trajectory or output, upgrade to
   HIGH regardless of step 3, and cite the trajectory quote.
5. **Suggested fix (CONFIRMED, any plausibility).** Write a concrete, specific new
   test-case/assertion (or instruction.md clarification) that closes this exact exploit
   — not "make the verifier stricter," the literal code change.

## Verdict Mapping (per exploit → one `checks[]` entry)

- NOT CONFIRMED → `result: "PASS"`, reason cites the defending code.
- CONFIRMED, HIGH or MEDIUM plausibility → `result: "FAIL"`, reason cites the confirming
  trace AND the suggested fix.
- CONFIRMED, LOW plausibility → `result: "WARN"`, reason cites the confirming trace,
  plausibility reasoning, AND the suggested fix (recorded, not blocking).
- If exploiter's `coverage_note` claims zero exploits or fewer than 3 with justification
  → add one extra entry `"exploiter_coverage"`: `PASS` if you independently agree the
  verifier is tight, `WARN` if you disagree and can point to something missed (one
  sentence pointing the trainer at the gap — do not invent a full new exploit here).

Dimension-level `result` is `FAIL` if ANY `checks[]` entry is `FAIL`. LOW-plausibility
(`WARN`) entries do NOT cause a dimension FAIL — visible to the trainer, non-blocking.

## Output Format

Save to `/tmp/qd_results/QD-10.json` — this IS the final dimension record for QD-10.

```json
{
  "dimension": "QD-10",
  "result": "PASS" or "FAIL",
  "checks": [
    {
      "id": 1,
      "name": "exploit_1_<short-slug-from-exploiter-title>",
      "result": "PASS" or "FAIL" or "WARN",
      "reason": "<independent trace verdict, plausibility rating/reasoning if applicable, suggested fix if CONFIRMED>"
    }
  ],
  "justification": "2-3 sentences. If FAIL: list confirmed-blocking exploit IDs and one-line fixes. If PASS with WARNs: note how many low-plausibility exploits were logged."
}
```

Before returning, run `ls /tmp/qd_results/` and confirm `QD-10.json` is there.
