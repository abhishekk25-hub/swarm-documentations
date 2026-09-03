#!/bin/bash
set -euo pipefail
mkdir -p /logs/verifier /logs/agent

# Fail closed: if judge.py dies before writing a reward, record a zero reward
# and a justification instead of crashing the verifier with no score.
fail_closed() {
  status=$?
  if [ ! -f /logs/verifier/reward.json ]; then
    printf '{"reward": 0.0, "error": "verifier_crashed"}\n' > /logs/verifier/reward.json
    printf 'Verifier failed before judge.py wrote a reward. Exit status: %s\n' "$status" \
      > /logs/verifier/judge_justification.txt
  fi
  exit "$status"
}
trap fail_closed EXIT

python3 -m pip install --no-cache-dir openai==1.109.1 pillow==10.4.0 \
  >/logs/verifier/pip-install.log 2>&1 || true

python3 /tests/judge.py \
  --agent-dir /logs/agent \
  --brief /input_artifacts/diagnostic_brief.md \
  --reward-out /logs/verifier/reward.json \
  2>&1 | tee /logs/verifier/test-stdout.txt

trap - EXIT
