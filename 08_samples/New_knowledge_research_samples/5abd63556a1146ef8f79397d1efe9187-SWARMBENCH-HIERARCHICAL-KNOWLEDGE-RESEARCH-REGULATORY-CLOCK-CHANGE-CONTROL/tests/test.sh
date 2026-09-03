#!/bin/bash
set -u

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERIFIER_OUTPUT_DIR="${VERIFIER_OUTPUT_DIR:-/logs/verifier}"
export VERIFIER_OUTPUT_DIR
mkdir -p "$VERIFIER_OUTPUT_DIR"

python3 -m pip install --quiet --disable-pip-version-check --no-cache-dir requests==2.32.3 \
  > "$VERIFIER_OUTPUT_DIR/pip-install.log" 2>&1 || {
    printf '%s\n' 'Verifier dependency installation failed.' > "$VERIFIER_OUTPUT_DIR/verifier_error.txt"
  }

python3 "$HERE/verify.py" 2>&1 | tee "$VERIFIER_OUTPUT_DIR/test-stdout.txt"
STATUS=${PIPESTATUS[0]}

if [ ! -f "$VERIFIER_OUTPUT_DIR/reward.json" ]; then
  printf '%s\n' \
    '{"reward":0.0,"total_static_check_score":0.0,"total_reward_hacking_check_score":0.0,"total_partial_oracle_check_score":0.0}' \
    > "$VERIFIER_OUTPUT_DIR/reward.json"
  printf '%s\n' '0.0' > "$VERIFIER_OUTPUT_DIR/reward.txt"
  printf '%s\n' \
    'invalid_evaluation: verify.py crashed before producing the required four-field reward.json' \
    > "$VERIFIER_OUTPUT_DIR/judge_justification.txt"
  printf '%s\n' \
    '{"status":"infrastructure_error","invalid_evaluation":true,"error":"verify.py crashed before producing reward.json"}' \
    > "$VERIFIER_OUTPUT_DIR/verifier_status.json"
  STATUS=1
fi

echo "reward=$(cat "$VERIFIER_OUTPUT_DIR/reward.txt")"
exit "$STATUS"
