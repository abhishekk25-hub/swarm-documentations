#!/bin/bash
set -uo pipefail
mkdir -p /logs/verifier

FROZEN=/logs/verifier/frozen
rm -rf "$FROZEN"; mkdir -p "$FROZEN/findings"
cp -a /logs/agent/findings/*.json "$FROZEN/findings"/ 2>/dev/null || true
cp -a /logs/agent/limb_matrix.csv "$FROZEN"/ 2>/dev/null || true
cp -a /logs/agent/state_profile.csv "$FROZEN"/ 2>/dev/null || true
cp -a /logs/agent/limb_brief.md "$FROZEN"/ 2>/dev/null || true
export VERIFY_FINDINGS_DIR="$FROZEN/findings"
export VERIFY_MATRIX_PATH="$FROZEN/limb_matrix.csv"
export VERIFY_PROFILE_PATH="$FROZEN/state_profile.csv"
export VERIFY_BRIEF_PATH="$FROZEN/limb_brief.md"
export VERIFY_PARTIAL_ORACLE_PATH=/tests/partial_oracle.json
echo "Froze $(ls -1 "$FROZEN"/findings/*.json 2>/dev/null | wc -l) findings files, $(ls -1 "$FROZEN"/limb_matrix.csv 2>/dev/null | wc -l) limb matrix, $(ls -1 "$FROZEN"/state_profile.csv 2>/dev/null | wc -l) state profile and $(ls -1 "$FROZEN"/limb_brief.md 2>/dev/null | wc -l) brief at verifier start." \
  | tee /logs/verifier/freeze.log

pip install --quiet --no-cache-dir requests==2.32.3 >/dev/null 2>&1 || true

python3 /tests/verify.py 2>&1 | tee /logs/verifier/test-output.log

if [ ! -f /logs/verifier/reward.json ]; then
  printf '%s\n' '{"reward": 0.0, "total_static_check_score": 0.0, "total_reward_hacking_check_score": 0.0, "total_partial_oracle_check_score": 0.0}' > /logs/verifier/reward.json
  [ -f /logs/verifier/reward.txt ] || echo 0.0000 > /logs/verifier/reward.txt
  [ -f /logs/verifier/verify_status.json ] || printf '%s\n' '{"status": "infra_error", "reason": "verify.py did not produce reward.json; the all-zero fallback is an infrastructure failure, not a graded zero-quality submission."}' > /logs/verifier/verify_status.json
fi

exit 0
