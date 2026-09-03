#!/bin/bash
set -uo pipefail
mkdir -p /logs/verifier
pip install --quiet --no-cache-dir requests==2.32.3 >/dev/null 2>&1 || true
python3 /tests/verify.py 2>&1 | tee /logs/verifier/test-output.log
if [ ! -f /logs/verifier/reward.txt ]; then
  echo 0 > /logs/verifier/reward.txt
  [ -f /logs/verifier/verify_status.json ] || printf '%s\n' '{"status": "infra_error", "reason": "verify.py did not produce reward.txt; the fallback 0 is an infrastructure failure, not a graded zero-quality submission."}' > /logs/verifier/verify_status.json
fi
