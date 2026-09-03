#!/bin/bash
# Hybrid verifier: judge.py does static + LLM checks and writes /logs/verifier/reward.txt.
set -uo pipefail
mkdir -p /logs/verifier /logs/agent

python3 /tests/judge.py \
  --agent-output /logs/agent/output.json \
  --oracle /tests/oracle.json 2>&1 | tee /logs/verifier/judge-output.log || true

[ -f /logs/verifier/reward.txt ] || echo 0 > /logs/verifier/reward.txt
cat /logs/verifier/reward.txt
