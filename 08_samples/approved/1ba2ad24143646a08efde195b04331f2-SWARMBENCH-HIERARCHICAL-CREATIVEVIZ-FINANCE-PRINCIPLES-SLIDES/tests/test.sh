#!/bin/bash
set -euo pipefail
mkdir -p /logs/verifier /logs/agent

fail_closed() {
  status=$?
  if [ ! -f /logs/verifier/reward.json ]; then
    printf '{"reward": 0.0}\n' > /logs/verifier/reward.json
    printf 'Verifier failed before judge.py wrote a reward. Exit status: %s\n' "$status" > /logs/verifier/judge_justification.txt
  fi
  exit "$status"
}
trap fail_closed EXIT

python3 -m pip install --no-cache-dir openai==1.109.1 python-pptx==1.0.2 >/logs/verifier/pip-install.log 2>&1 || true

python3 /tests/judge.py \
  --agent-output /logs/agent/output.pptx \
  --pdf /input_artifacts/Principles_Finance.pdf \
  --reward-out /logs/verifier/reward.json

trap - EXIT
