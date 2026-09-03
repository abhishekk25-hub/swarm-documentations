#!/bin/bash
set -uo pipefail

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
  > "$verifier_dir/test-output.log" 2>&1
rc=$?
cat "$verifier_dir/test-output.log"

python3 -c 'import json,math,sys
keys=("reward","total_static_check_score","total_reward_hacking_check_score","total_partial_oracle_check_score")
d=json.load(open(sys.argv[1],encoding="utf-8"))
v=[d[k] for k in keys]
ok=all(isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x) and 0.0<=x<=1.0 for x in v)
if not ok or abs(v[0]-(v[1]+v[2]+v[3])/3)>0.001: raise SystemExit("invalid reward fields or formula")
' "$reward_json"
reward_valid=$?
set -e

if [ ! -f "$reward_json" ] || [ "$reward_valid" -ne 0 ]; then
  printf '{\n  "reward": 0.0,\n  "total_static_check_score": 0.0,\n  "total_reward_hacking_check_score": 0.0,\n  "total_partial_oracle_check_score": 0.0\n}\n' > "$reward_json"
  printf '{"status":"verifier_error","reward_is_graded":false,"exit_code":%s}\n' "$rc" > "$verifier_dir/verifier_status.json"
  printf 'VERIFIER_ERROR: verify.py exited %s without a valid reward.json\n' "$rc" >&2
fi

exit "$rc"
