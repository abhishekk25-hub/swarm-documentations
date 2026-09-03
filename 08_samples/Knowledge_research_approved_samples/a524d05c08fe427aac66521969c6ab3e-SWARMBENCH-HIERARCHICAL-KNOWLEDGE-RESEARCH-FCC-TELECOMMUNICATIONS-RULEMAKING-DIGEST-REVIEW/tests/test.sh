#!/bin/bash
set -e

cd /tests

pip3 install --break-system-packages requests==2.31.0 2>/dev/null || pip3 install requests==2.31.0 2>/dev/null || true

mkdir -p /logs/verifier /logs/agent

echo "=== Running Phase 2.1 grader (single entry point: tests/verify.py) ==="
python3 verify.py 2>&1

echo "=== Verifying reward contract exists ==="
if [ ! -f /logs/verifier/reward.txt ]; then
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "total_static_check_score": 0.0, "total_reward_hacking_check_score": 0.0, "total_partial_oracle_check_score": 0.0}' > /logs/verifier/reward.json
    echo "FALLBACK: reward.txt missing after verify.py, wrote 0.0"
fi
cat /logs/verifier/reward.txt
