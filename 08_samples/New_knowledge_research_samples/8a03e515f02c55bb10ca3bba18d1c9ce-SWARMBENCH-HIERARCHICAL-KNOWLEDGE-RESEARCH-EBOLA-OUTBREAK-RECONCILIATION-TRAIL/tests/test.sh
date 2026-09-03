#!/bin/bash
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[TEST.SH] installing verifier-only dependencies"
python3 -m pip install --no-cache-dir --quiet requests==2.32.3 || \
  echo "[TEST.SH] WARNING: pip install failed; judge-backed checks will report an infrastructure failure" >&2

echo "[TEST.SH] starting verifier (tests/verify.py)"
python3 "$SCRIPT_DIR/verify.py"
status=$?

VERIFIER_DIR="${VERIFIER_DIR:-/logs/verifier}"
REWARD_JSON="$VERIFIER_DIR/reward.json"

if [ "$status" -ne 0 ]; then
  echo "[TEST.SH] verify.py exited non-zero ($status) -- this means the verifier itself crashed" \
       "before it could write reward.json, not that the task scored zero." >&2
fi

if [ ! -f "$REWARD_JSON" ]; then
  echo "[TEST.SH] $REWARD_JSON is missing -- verify.py crashed before writing it." \
       "Writing a zero-valued fallback so Harbor/Quality Gate always finds a valid reward.json." >&2
  mkdir -p "$VERIFIER_DIR"
  cat > "$REWARD_JSON" <<EOF
{
  "reward": 0.0,
  "total_static_check_score": 0.0,
  "total_reward_hacking_check_score": 0.0,
  "total_partial_oracle_check_score": 0.0,
  "infra_failure": true,
  "infra_failure_detail": {"reason": "verify.py crashed with exit status $status before writing reward.json"}
}
EOF
  echo "0.0" > "$VERIFIER_DIR/reward.txt"
  cat > "$VERIFIER_DIR/judge_justification.txt" <<EOF
VERIFIER INFRASTRUCTURE FAILURE

verify.py exited with status $status and did not write reward.json.
This is a verifier crash, not a scored zero -- the submission was never
actually evaluated. See the test runner's stderr/stdout log for the
Python traceback that caused this.
EOF
  status=1
fi

JUSTIFICATION="$VERIFIER_DIR/judge_justification.txt"
if [ -f "$JUSTIFICATION" ]; then
  echo "[TEST.SH] ---- judge_justification.txt (per-criterion score breakdown and reasoning) ----"
  cat "$JUSTIFICATION"
  echo "[TEST.SH] ---- end judge_justification.txt ----"
fi

echo "[TEST.SH] verifier finished with exit code $status"
exit "$status"
