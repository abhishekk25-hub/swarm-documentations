#!/bin/bash
set -uo pipefail
mkdir -p /logs/verifier /logs/agent

fail_closed() {
  status=$?
  if [ ! -f /logs/verifier/reward.json ]; then
    printf '{"reward": 0.0}\n' > /logs/verifier/reward.json
    printf '0.0\n' > /logs/verifier/reward.txt
    printf 'Verifier crashed before writing reward. Exit status: %s\n' "$status" \
      > /logs/verifier/judge_justification.txt
  fi
  exit "$status"
}
trap fail_closed EXIT

# Belt-and-suspenders: image already installs these, but ensure they are present.
pip install --quiet --no-cache-dir python-docx==1.1.2 openai==1.109.1 2>/logs/verifier/pip-install.log || true

python3 /tests/judge.py 2>&1 | tee /logs/verifier/judge-output.log

[ -f /logs/verifier/reward.txt ] || echo 0 > /logs/verifier/reward.txt
trap - EXIT
