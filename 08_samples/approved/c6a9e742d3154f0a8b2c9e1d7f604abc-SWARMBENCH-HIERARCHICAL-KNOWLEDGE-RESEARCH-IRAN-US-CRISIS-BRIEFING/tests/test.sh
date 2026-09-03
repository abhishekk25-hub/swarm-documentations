#!/bin/bash
set -euo pipefail

mkdir -p /logs/verifier

python /tests/judge.py > /logs/verifier/judge_output.json

python - <<'PY'
import json
from pathlib import Path

judge_path = Path("/logs/verifier/judge_output.json")
reward_path = Path("/logs/verifier/reward.json")

try:
    data = json.loads(judge_path.read_text(encoding="utf-8"))
    reward = float(data.get("judge_score", 0.0))
except Exception:
    reward = 0.0

reward_path.write_text(json.dumps({"reward": reward}, indent=2), encoding="utf-8")
PY
