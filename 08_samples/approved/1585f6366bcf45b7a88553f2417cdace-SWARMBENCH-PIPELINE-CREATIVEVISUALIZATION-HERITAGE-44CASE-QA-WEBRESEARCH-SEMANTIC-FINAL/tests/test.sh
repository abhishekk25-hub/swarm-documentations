#!/bin/bash
set -uo pipefail
mkdir -p /logs/verifier /logs/agent
python3 /tests/verify.py --agent-root /logs/agent --input-root /input_artifacts --reference-root /tests/reference_sources --config /tests/rubric_config.json --reward-out /logs/verifier/reward.txt 2>&1 | tee /logs/verifier/test-output.log
[ -f /logs/verifier/reward.txt ] || echo 0 > /logs/verifier/reward.txt
