#!/bin/bash
set -uo pipefail
mkdir -p /logs/verifier
if ! python3 -m pip install --disable-pip-version-check --no-cache-dir requests==2.32.3 pypdf==5.9.0 cryptography==41.0.7 openpyxl==3.1.5; then
  echo "VERIFIER_INFRASTRUCTURE_ERROR: failed to install pinned verifier dependencies"
  echo '{"reward": 0, "total_static_check_score": 0, "total_reward_hacking_check_score": 0, "total_partial_oracle_check_score": 0}' > /logs/verifier/reward.json
  exit 1
fi
python3 /tests/verify.py 2>&1 | tee /logs/verifier/test-output.log
[ -f /logs/verifier/reward.json ] || echo '{"reward": 0, "total_static_check_score": 0, "total_reward_hacking_check_score": 0, "total_partial_oracle_check_score": 0}' > /logs/verifier/reward.json
