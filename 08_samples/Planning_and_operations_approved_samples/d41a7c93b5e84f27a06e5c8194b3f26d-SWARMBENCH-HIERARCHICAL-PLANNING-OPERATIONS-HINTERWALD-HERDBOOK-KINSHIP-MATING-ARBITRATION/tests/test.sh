#!/bin/bash
# Executable verifier entrypoint. Scoring is fully deterministic: no API key, no network
# access and no LLM call is required or used. Every expectation about the pedigree is
# recomputed inside tests/verify.py on the standard library; the only frozen input is
# tests/health_standing.json, the standing reconciled from the prose herd health
# correspondence, which sits beside this file and is never copied into the agent image.
#
# This file must keep LF line endings. Under CRLF, bash reads the shebang as /bin/bash\r
# and appends \r to every path it builds, so the reward file never lands where the
# harness looks for it.
set -uo pipefail

agent_dir="${AGENT_DIR:-/logs/agent}"
input_dir="${INPUT_DIR:-/input_artifacts}"
verifier_dir="${VERIFIER_DIR:-/logs/verifier}"
tests_dir="${TESTS_DIR:-/tests}"
reward_json="$verifier_dir/reward.json"
mkdir -p "$agent_dir" "$verifier_dir"

set +e
# Redirect rather than pipe, so $? is the verifier's own status in any POSIX shell.
python3 /tests/verify.py \
  --agent-dir "$agent_dir" \
  --input-dir "$input_dir" \
  --out-dir "$verifier_dir" \
  --tests-dir "$tests_dir" \
  > "$verifier_dir/test-output.log" 2>&1
rc=$?
cat "$verifier_dir/test-output.log"

# Re-validate the reward contract independently of verify.py.
python3 -c 'import json,math,sys
keys=("reward","total_static_check_score","total_reward_hacking_check_score","total_partial_oracle_check_score")
data=json.load(open(sys.argv[1],encoding="utf-8"))
v=[data[k] for k in keys]
ok=all(isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x) and 0.0<=x<=1.0 for x in v)
if not ok or abs(v[0]-(v[1]+2*v[2]+3*v[3])/6)>0.001: raise SystemExit("invalid reward fields or weighted formula")
' "$reward_json"
reward_valid=$?
set -e

if [ ! -f "$reward_json" ] || [ "$reward_valid" -ne 0 ]; then
  printf '{\n  "reward": 0.0,\n  "total_static_check_score": 0.0,\n  "total_reward_hacking_check_score": 0.0,\n  "total_partial_oracle_check_score": 0.0\n}\n' > "$reward_json"
  printf '{"status":"verifier_error","reward_is_graded":false,"exit_code":%s,"error":"verify.py did not produce a valid four-field reward.json"}\n' "$rc" > "$verifier_dir/verifier_status.json"
  printf 'VERIFIER_ERROR: verify.py exited %s without a valid reward.json; fallback zeros indicate infrastructure failure, not a graded submission.\n' "$rc" >&2
fi

exit "$rc"
