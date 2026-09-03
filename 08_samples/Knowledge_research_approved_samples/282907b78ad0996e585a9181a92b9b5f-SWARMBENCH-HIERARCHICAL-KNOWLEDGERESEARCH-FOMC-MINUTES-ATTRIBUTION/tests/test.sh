#!/bin/bash
set -uo pipefail

mkdir -p /logs/verifier

python3 /tests/verify.py
status=$?

if [ ! -s /logs/verifier/reward.json ]; then
  echo "verifier produced no reward.json" >&2
  cat > /logs/verifier/reward.json <<'JSON'
{
 "reward": 0.0,
 "total_static_check_score": 0.0,
 "total_reward_hacking_check_score": 0.0,
 "total_partial_oracle_check_score": 0.0,
 "content_score": 0.0,
 "structural_score": 0.0,
 "infrastructure_failure": true,
 "error": "verify.py did not write reward.json",
 "checks": []
}
JSON
fi

if [ ! -s /logs/verifier/reward.txt ]; then
  echo "verifier produced no reward file" >&2
  echo "0.000000" > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
exit $status
