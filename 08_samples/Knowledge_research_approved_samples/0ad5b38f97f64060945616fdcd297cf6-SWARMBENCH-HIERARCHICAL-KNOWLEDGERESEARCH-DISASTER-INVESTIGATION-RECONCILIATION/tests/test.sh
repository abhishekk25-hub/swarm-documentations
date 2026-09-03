#!/bin/bash
set -uo pipefail

mkdir -p /logs/verifier
rm -f /logs/verifier/reward.txt /logs/verifier/reward.json

python3 /tests/verify.py
STATUS=$?

if [ ! -s /logs/verifier/reward.json ]; then
  cat > /logs/verifier/reward.json <<'JSON'
{
  "reward": 0.0,
  "total_static_check_score": 0.0,
  "total_reward_hacking_check_score": 0.0,
  "total_partial_oracle_check_score": 0.0
}
JSON
fi

if [ ! -s /logs/verifier/details.json ]; then
  cat > /logs/verifier/details.json <<'JSON'
{
  "content_score": 0.0,
  "structural_score": 0.0,
  "infrastructure_failure": true,
  "error": "verify.py did not produce reward.json"
}
JSON
fi

if [ ! -s /logs/verifier/reward.txt ]; then
  printf '0.000000\n' > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt

exit $STATUS
