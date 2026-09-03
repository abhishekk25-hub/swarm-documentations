#!/bin/bash
set -u

mkdir -p /logs/verifier

python3 /tests/verify.py
STATUS=$?

if [ ! -s /logs/verifier/reward.json ]; then
  cat > /logs/verifier/reward.json <<'JSON'
{"reward": 0.0, "total_static_check_score": 0.0, "total_reward_hacking_check_score": 0.0, "total_partial_oracle_check_score": 0.0, "infrastructure_failure": true, "error": "verify.py did not produce reward.json"}
JSON
fi

if [ ! -s /logs/verifier/reward.txt ]; then
  echo "0.0" > /logs/verifier/reward.txt
fi

exit $STATUS
