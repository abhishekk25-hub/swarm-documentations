#!/bin/bash
set -uo pipefail
mkdir -p /logs/verifier
python3 /tests/verify.py 2>&1 | tee /logs/verifier/test-output.log
rc=${PIPESTATUS[0]}

reward_json=/logs/verifier/reward.json
reward_valid=false
if [ -f "$reward_json" ]; then
  if python3 - "$reward_json" <<'PY'
import json, math, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
keys = ("reward", "total_static_check_score",
        "total_reward_hacking_check_score", "total_partial_oracle_check_score")
values = [data[k] for k in keys]
for v in values:
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or not 0.0 <= v <= 1.0:
        raise SystemExit(f"reward.json field out of range: {v}")
expected = (values[1] + 2 * values[2] + 3 * values[3]) / 6
if abs(values[0] - expected) > 0.001:
    raise SystemExit(f"reward {values[0]} does not match the 1:2:3 bucket formula {expected}")
PY
  then
    reward_valid=true
  fi
fi

if [ "$reward_valid" != true ]; then
  printf '{\n  "reward": 0.0,\n  "total_static_check_score": 0.0,\n  "total_reward_hacking_check_score": 0.0,\n  "total_partial_oracle_check_score": 0.0\n}\n' \
    > "$reward_json"
  printf '{"status": "verifier_error", "reward_is_graded": false, "exit_code": %s, "error": "verify.py did not produce a valid four-field reward.json"}\n' "$rc" \
    > /logs/verifier/verifier_status.json
  echo "VERIFIER_ERROR: verify.py exited ${rc} without a valid reward.json; the zeros below are an infrastructure failure, not a graded result" \
    | tee -a /logs/verifier/test-output.log >&2
  echo 0 > /logs/verifier/reward.txt
fi
