# W&B Qwen Vision Verifier Template

> **Catalog path:** `03_design_guides/verifier_templates/WANDB_Qwen_Vision_Verifier_Template/`  
> **How to use in Phase 2 task creation:** see P21-6 in
> `07_prompt_runtime/PlanningOperations_Phase2_TaskCreationPrompt.md` and
> `.cursor/rules/swarmbench-judge-provider.mdc`. This is the **common starting
> point for W&B LLM-judge HTTP calls** (esp. vision). It is **not** a drop-in
> complete Phase 2.1 verifier — keep deterministic static / RH / PO checks,
> honest `rubric_manifest.json`, and Production Rework `reward.json` components.
> Prefer `verifier_type = "hybrid"` when mixing. **Do not send `temperature`.**
> When adapting, add an explicit `User-Agent` (CDN 403/1010 on default urllib UA).

This is a reference template for an LLM-judge verifier. It demonstrates the standard W&B inference call, how task-specific evidence is passed to the judge, how the judge returns a structured result, and how verifier failures are kept separate from task-quality failures.

It is not a complete verifier by itself. Each task must still have deterministic checks for paths, schemas, coverage, calculations, and any available partial-oracle values. Use the LLM judge for the part that needs genuine visual or semantic judgment.

## Verified Default

The default is `Qwen/Qwen3.6-35B-A3B`. The supplied W&B key was used to confirm both a vision request and `response_format={"type":"json_object"}` against this exact model. W&B's current model list did not include a `Qwen 3.7` model, so do not invent that identifier. If the catalog changes, query `/v1/models` and update only `JUDGE_MODEL` or `model` in the config.

## Required Task Configuration

An LLM judge needs network access. In `task.toml`:

```toml
[metadata]
verifier_type = "llm-judge"
network_enabled = true

[verifier]
timeout_sec = 1800
```

Harbor/Cloud Run must pass `WANDB_API_KEY` into the verifier environment. Never put the key in `task.toml`, `verify.py`, `test.sh`, the task ZIP, or execution logs.

For an isolated local smoke test only, `VERIFIER_OUTPUT_DIR` can override the
default `/logs/verifier` destination. Do not set this in a submitted task.

## Files To Copy Into A Task

```text
tests/
  verify.py
  judge_config.json
  test.sh
```

Use one canonical verifier filename: `verify.py`. Keep `test.sh` as the entrypoint.

## How Inputs Become Judge Arguments

Each item in `criteria` in `judge_config.json` becomes one judge call.

| Field | What to pass |
|---|---|
| `id` | Stable descriptive check identifier, such as `chart_truthfulness` |
| `weight` | Importance relative to the other judge criteria; do not use weights to manufacture an SA/MA gap |
| `prompt` | Task-specific question the judge must answer |
| `expected_signals` | Observable evidence the task should contain; these should come from the instruction and source data |
| `image_paths` | Exact agent output images under `/logs/agent/...` |
| `text_paths` | Exact supporting text/JSON/CSV output paths under `/logs/agent/...` |
| `max_text_chars` | A bounded excerpt size; avoid submitting the entire workspace or unrelated data |
| `max_tokens` | Response budget for the judge; use enough room for the model to reason and return JSON |

The verifier sends the criterion prompt, the chosen source/output text, and inline image data to W&B. It asks for only:

```json
{
  "criterion_id": "example_visual_grounding",
  "score": 0.0,
  "verdict": "pass",
  "evidence": ["short evidence grounded in the supplied artefacts"],
  "reason": "brief explanation"
}
```

The only score accepted is a number from `0.0` to `1.0`. The final reward is the weighted mean of successfully completed criteria.

## Standard W&B Call

The template intentionally uses the direct OpenAI-compatible HTTP endpoint:

```python
requests.post(
    "https://api.inference.wandb.ai/v1/chat/completions",
    headers={"Authorization": f"Bearer {os.environ['WANDB_API_KEY']}"},
    json={
        "model": "Qwen/Qwen3.6-35B-A3B",
        "messages": [...],
        "response_format": {"type": "json_object"},
        "max_tokens": 900,
    },
)
```

Do not send `temperature` unless the selected provider/model documents that parameter as supported. Do not assume a model name from another provider will work at W&B.

## Failure Handling

The template retries `429`, `500`, `502`, `503`, `504`, and `522` with exponential backoff. It records failures in `/logs/verifier/judge_results.json` and writes:

```json
{"status": "infrastructure_error"}
```

to `/logs/verifier/verifier_status.json` when any judge check remains unavailable. It also writes a `0.0` reward only to satisfy Harbor's reward-file contract. That `0.0` is an infrastructure outcome, not a valid task-quality score. The run should be rerun after the provider/configuration issue is fixed.

## Trainer Checklist

1. Start with deterministic checks. Verify exact output paths, schema, counts, calculations, and grounded spot values first.
2. Add only a small number of LLM criteria for the semantic or visual behavior deterministic code cannot judge.
3. Give the judge the task instruction excerpt plus the exact source and output artefacts needed to assess one criterion.
4. Make the criterion observable. "The report is good" is not testable; "the chart labels the actual categories and does not contradict the linked output rows" is.
5. Run one isolated text test and one isolated vision test before SA/MA execution.
6. Inspect `judge_results.json` after every run. A missing judge result is never evidence that the agent failed.

## What This Template Does Not Replace

- A task-specific schema validator.
- Partial-oracle or source-grounded value checks.
- Reward-hacking checks, such as duplicate prose detection, fabricated values, or an image with a correct filename but wrong content.
- A quality-gate review of instruction/verifier alignment.
