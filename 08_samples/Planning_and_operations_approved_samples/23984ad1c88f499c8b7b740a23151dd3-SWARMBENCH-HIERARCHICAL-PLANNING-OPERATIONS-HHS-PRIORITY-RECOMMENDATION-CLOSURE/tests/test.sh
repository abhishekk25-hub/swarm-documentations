#!/bin/bash
set -euo pipefail

mkdir -p /logs/verifier

write_fallback() {
  python3 - <<'PY'
import json
from pathlib import Path

out = Path("/logs/verifier")
out.mkdir(parents=True, exist_ok=True)
if not (out / "reward.json").exists():
    (out / "reward.json").write_text(json.dumps({
        "reward": 0.0,
        "total_static_check_score": 0.0,
        "total_reward_hacking_check_score": 0.0,
        "total_partial_oracle_check_score": 0.0
    }, indent=2) + "\n", encoding="utf-8")
    (out / "reward.txt").write_text("0.000000\n", encoding="utf-8")
    (out / "judge_justification.txt").write_text(
        "INFRASTRUCTURE CRASH -- not a scored zero.\n\n"
        "tests/verify.py exited before writing reward.json. The zero-valued file is only a crash fallback.\n",
        encoding="utf-8"
    )
PY
}

trap 'write_fallback' ERR EXIT
pip3 install --quiet --break-system-packages requests==2.31.0 2>/dev/null || pip3 install --quiet requests==2.31.0
python3 /tests/verify.py
status=$?
trap - ERR EXIT
write_fallback
exit "$status"

