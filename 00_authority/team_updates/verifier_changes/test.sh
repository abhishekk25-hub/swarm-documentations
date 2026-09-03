#!/bin/bash
set -uo pipefail
mkdir -p /logs/verifier
python3 /tests/verify.py 2>&1 | tee /logs/verifier/test-output.log
[ -f /logs/verifier/reward.json ] || echo '{"reward": 0, "total_static_check_score": 0, "total_reward_hacking_check_score": 0, "total_partial_oracle_check_score": 0}' > /logs/verifier/reward.json
