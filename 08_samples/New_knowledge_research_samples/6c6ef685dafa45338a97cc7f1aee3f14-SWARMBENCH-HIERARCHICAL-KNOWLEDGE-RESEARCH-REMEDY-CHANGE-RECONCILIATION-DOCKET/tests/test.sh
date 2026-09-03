#!/bin/bash
set -uo pipefail
mkdir -p /logs/verifier

python3 -m pip install --no-cache-dir requests==2.32.3 \
    >/logs/verifier/pip-install.log 2>&1

python3 /tests/verify.py 2>&1 | tee /logs/verifier/test-output.log
VERIFY_EXIT=${PIPESTATUS[0]}

if [ ! -f /logs/verifier/reward.json ]; then
    echo "INFRASTRUCTURE_ERROR verify.py exited $VERIFY_EXIT without writing reward.json" \
        | tee -a /logs/verifier/test-output.log
    echo '{"reward": 0.0, "total_static_check_score": 0.0, "total_reward_hacking_check_score": 0.0, "total_partial_oracle_check_score": 0.0}' \
        > /logs/verifier/reward.json
fi
