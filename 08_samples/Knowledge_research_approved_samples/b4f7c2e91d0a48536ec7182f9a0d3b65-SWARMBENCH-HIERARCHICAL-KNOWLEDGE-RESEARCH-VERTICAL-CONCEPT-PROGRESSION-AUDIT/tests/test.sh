#!/bin/bash
set -uo pipefail
mkdir -p /logs/verifier

FROZEN=/logs/verifier/frozen
rm -rf "$FROZEN"
mkdir -p "$FROZEN/units" "$FROZEN/concepts"
cp -a /logs/agent/units/. "$FROZEN/units"/ 2>/dev/null || true
cp -a /logs/agent/concepts/. "$FROZEN/concepts"/ 2>/dev/null || true
cp -a /logs/agent/progression_index.json "$FROZEN"/ 2>/dev/null || true
cp -a /logs/agent/articulation_report.md "$FROZEN"/ 2>/dev/null || true
export VERIFY_SHEETS_DIR="$FROZEN/units"
export VERIFY_CONCEPTS_DIR="$FROZEN/concepts"
export VERIFY_INDEX_PATH="$FROZEN/progression_index.json"
export VERIFY_REPORT_PATH="$FROZEN/articulation_report.md"
export VERIFY_PARTIAL_ORACLE_PATH=/tests/partial_oracle.json
echo "Froze $(ls -1 "$FROZEN"/units/*.json 2>/dev/null | wc -l) unit sheets, $(ls -1 "$FROZEN"/concepts/*.json 2>/dev/null | wc -l) concept dossiers, $(ls -1 "$FROZEN"/progression_index.json 2>/dev/null | wc -l) progression index and $(ls -1 "$FROZEN"/articulation_report.md 2>/dev/null | wc -l) articulation report at verifier start." \
  | tee /logs/verifier/freeze.log

pip install --quiet --no-cache-dir requests==2.32.3 >/dev/null 2>&1 || true

python3 /tests/verify.py 2>&1 | tee /logs/verifier/test-output.log

if [ ! -f /logs/verifier/reward.json ]; then
  printf '%s\n' '{"reward": 0.0, "total_static_check_score": 0.0, "total_reward_hacking_check_score": 0.0, "total_partial_oracle_check_score": 0.0}' > /logs/verifier/reward.json
  [ -f /logs/verifier/reward.txt ] || echo 0.0000 > /logs/verifier/reward.txt
  [ -f /logs/verifier/verify_status.json ] || printf '%s\n' '{"status": "infra_error", "reason": "verify.py did not produce reward.json; the all-zero fallback is an infrastructure failure, not a graded zero-quality submission."}' > /logs/verifier/verify_status.json
fi

exit 0
