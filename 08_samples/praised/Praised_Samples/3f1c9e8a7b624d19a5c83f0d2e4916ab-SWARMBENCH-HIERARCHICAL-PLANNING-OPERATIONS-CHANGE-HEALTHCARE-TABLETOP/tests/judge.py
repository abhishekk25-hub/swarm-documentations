#!/usr/bin/env python3
import json
import os
import re
from pathlib import Path

try:
    import requests
except Exception:
    requests = None


OUTPUT = Path("/logs/agent/output")
VERIFIER = Path("/logs/verifier")
INPUT = Path("/environment/input_artifacts")
JUDGE_MODEL = os.environ.get("JUDGE_MODEL", "accounts/fireworks/models/deepseek-v4-flash")
FIREWORKS_API_KEY = os.environ.get("FIREWORKS_API_KEY", "")
FIREWORKS_URL = "https://api.fireworks.ai/inference/v1/chat/completions"


LLM_CHECKS = [
    "Representative cited evidence actually supports the incident facts or pressure points used in injects.",
    "The timeline reflects the real Change Healthcare incident sequence and does not materially misorder key events.",
    "Injects are incident-specific and do not read like generic ransomware boilerplate.",
    "Role packets are appropriate to their roles and contain role-specific private context rather than repeated generic text.",
    "The facilitator guide can realistically run a 2-hour tabletop session.",
    "Observer scorecards evaluate decisions that actually appear in the injects and role packets.",
    "The after-action template is operationally useful and maps findings to owners, deadlines, and retesting.",
    "The incident map accurately represents roles, incident phases, systems/entities, dependencies, and decision points described elsewhere.",
    "The visual exhibit notes interpret source-derived charts, tables, figures, or visual layouts and connect them to concrete exercise design choices.",
    "The package avoids unsupported claims, invented facts, and citation drift.",
]


def read(path, limit=18000):
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
        return text[:limit]
    except Exception:
        return ""


def call_judge(prompt):
    if not requests or not FIREWORKS_API_KEY:
        return ""
    response = requests.post(
        FIREWORKS_URL,
        headers={"Authorization": f"Bearer {FIREWORKS_API_KEY}", "Content-Type": "application/json"},
        json={
            "model": JUDGE_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "max_tokens": 1800,
        },
        timeout=120,
    )
    if response.status_code != 200:
        return ""
    return response.json()["choices"][0]["message"]["content"]


def parse_pass_fail(text):
    results = []
    for idx in range(1, len(LLM_CHECKS) + 1):
        pat = re.compile(rf"CHECK\s*{idx}\s*:\s*(PASS|FAIL)", re.I)
        m = pat.search(text)
        if not m:
            return None
        results.append(m.group(1).upper() == "PASS")
    return results


def write_reward(reward, justification):
    reward = max(0.0, min(1.0, float(reward)))
    (VERIFIER / "reward.json").write_text(json.dumps({"reward": round(reward, 4)}, indent=2), encoding="utf-8")
    (VERIFIER / "judge_justification.txt").write_text(justification, encoding="utf-8")
    print(json.dumps({"reward": round(reward, 4)}, indent=2))


def main():
    VERIFIER.mkdir(parents=True, exist_ok=True)
    verify = {}
    try:
        verify = json.loads((VERIFIER / "verify_output.json").read_text(encoding="utf-8"))
    except Exception:
        pass
    deterministic = verify.get("checks", [])

    excerpts = {
        "executive_runbook.md": read(OUTPUT / "executive_runbook.md", 12000),
        "facilitator_guide.md": read(OUTPUT / "facilitator_guide.md", 16000),
        "injects_timeline.csv": read(OUTPUT / "injects_timeline.csv", 16000),
        "observer_scorecards.csv": read(OUTPUT / "observer_scorecards.csv", 12000),
        "evidence_register.csv": read(OUTPUT / "evidence_register.csv", 12000),
        "visual_exhibit_notes.csv": read(OUTPUT / "visual_exhibit_notes.csv", 12000),
        "incident_map.html": read(OUTPUT / "incident_map.html", 10000),
        "after_action_template.md": read(OUTPUT / "after_action_template.md", 10000),
    }
    role_dir = OUTPUT / "role_packets"
    for role in ["ciso.md", "legal.md", "communications.md", "executive_leadership.md", "it_operations.md", "vendor_management.md"]:
        excerpts[f"role_packets/{role}"] = read(role_dir / role, 6000)

    source_summary = read(INPUT / "sources.json", 10000)
    prompt = f"""
You are grading a cyber crisis tabletop exercise package. Evaluate only output quality and evidence use. Do not consider how the work was coordinated.

Return exactly one line per check using this format:
CHECK 1: PASS/FAIL - short reason
...
CHECK {len(LLM_CHECKS)}: PASS/FAIL - short reason

Checks:
{json.dumps({i + 1: c for i, c in enumerate(LLM_CHECKS)}, indent=2)}

Deterministic verifier summary:
{json.dumps(verify, indent=2)[:12000]}

Pinned source manifest excerpt:
{source_summary}

Agent output excerpts:
{json.dumps(excerpts, indent=2)[:55000]}
"""
    judge_text = call_judge(prompt)
    if not judge_text:
        write_reward(
            0.0,
            "Reward 0.0000: LLM judge unavailable or returned an empty response. "
            "Failing closed so deterministic structural checks cannot produce a non-zero reward without LLM validation.",
        )
        return
    llm_results = parse_pass_fail(judge_text)
    if llm_results is None:
        write_reward(
            0.0,
            "Reward 0.0000: LLM judge response could not be parsed into all required PASS/FAIL checks. "
            f"Failing closed.\n\nLLM judge output:\n{judge_text}",
        )
        return

    all_checks = []
    for item in deterministic:
        all_checks.append({"name": item.get("name", "deterministic"), "passed": bool(item.get("passed")), "kind": "deterministic", "reason": item.get("reason", "")})
    for idx, passed in enumerate(llm_results):
        all_checks.append({"name": LLM_CHECKS[idx], "passed": passed, "kind": "llm", "reason": ""})

    total = len(all_checks)
    passed = sum(1 for item in all_checks if item["passed"])
    reward = max(0.0, min(1.0, passed / total if total else 0.0))
    write_reward(
        reward,
        f"Reward {reward:.4f}: {passed}/{total} checks passed.\n\nLLM judge output:\n{judge_text}\n\nAll checks:\n{json.dumps(all_checks, indent=2)}",
    )


if __name__ == "__main__":
    main()
