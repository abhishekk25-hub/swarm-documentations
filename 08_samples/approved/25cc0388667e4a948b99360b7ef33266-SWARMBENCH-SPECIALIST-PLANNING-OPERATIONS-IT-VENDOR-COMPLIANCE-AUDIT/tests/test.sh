#!/bin/bash
set -uo pipefail
mkdir -p /logs/verifier /logs/agent

pip install --no-cache-dir openai==1.82.0 openpyxl 2>/dev/null

python3 /tests/judge.py 2>&1 | tee /logs/verifier/test-output.log

[ -f /logs/verifier/reward.json ] || echo '{"reward": 0.0}' > /logs/verifier/reward.json
