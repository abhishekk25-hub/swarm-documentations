#!/bin/bash
set -euo pipefail

agent_dir="${AGENT_DIR:-/logs/agent}"
input_dir="${INPUT_DIR:-/input_artifacts}"
verifier_dir="${VERIFIER_DIR:-/logs/verifier}"
reward_json="$verifier_dir/reward.json"
mkdir -p "$agent_dir" "$verifier_dir"

set +e
python3 /tests/verify.py \
  --agent-dir "$agent_dir" \
  --input-dir "$input_dir" \
  --out-dir "$verifier_dir" \
  2>&1 | tee "$verifier_dir/test-output.log"
rc=${PIPESTATUS[0]}
set -e

reward_valid=false
if [ -f "$reward_json" ]; then
  if python3 - "$reward_json" <<'PY'
import json, math, sys
try:
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    keys = (
        "reward",
        "total_static_check_score",
        "total_reward_hacking_check_score",
        "total_partial_oracle_check_score",
    )
    values = [data[key] for key in keys]
    valid = all(isinstance(v, (int, float)) and not isinstance(v, bool)
                and math.isfinite(v) and 0.0 <= v <= 1.0 for v in values)
    expected = (values[1] + 2 * values[2] + 3 * values[3]) / 6
    if not valid or abs(values[0] - expected) > 0.001:
        raise ValueError("invalid reward fields or weighted formula")
except Exception as exc:
    print(f"invalid reward.json: {exc}", file=sys.stderr)
    sys.exit(1)
PY
  then
    reward_valid=true
  fi
fi

if [ "$reward_valid" != true ]; then
  printf '{\n  "reward": 0.0,\n  "total_static_check_score": 0.0,\n  "total_reward_hacking_check_score": 0.0,\n  "total_partial_oracle_check_score": 0.0\n}\n' > "$reward_json"
  printf '{"status":"verifier_error","reward_is_graded":false,"exit_code":%s,"error":"verify.py did not produce a valid four-field reward.json"}\n' "$rc" > "$verifier_dir/verifier_status.json"
  printf 'VERIFIER_ERROR\nverify.py exited %s without a valid reward.json; fallback zeros indicate infrastructure failure, not a graded submission.\n' "$rc" > "$agent_dir/judge_justification.txt"
  printf 'VERIFIER_ERROR: invalid or missing reward.json; fallback zeros emitted\n' >&2
fi

exit "$rc"
