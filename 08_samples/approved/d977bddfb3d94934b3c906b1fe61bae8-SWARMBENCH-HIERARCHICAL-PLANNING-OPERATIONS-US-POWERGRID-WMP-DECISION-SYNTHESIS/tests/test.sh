#!/bin/bash
set -uo pipefail
mkdir -p /logs/verifier /logs/agent

# The judge only needs the LLM client plus the parsers for the agent's
# deliverables (docx + pptx). python-docx/python-pptx are already in the image;
# openai is installed at runtime. A single transient PyPI/network blip during
# this install otherwise silently zeroes all 21 LLM quality checks, so retry a
# few times and confirm the import actually succeeds before scoring.
for attempt in 1 2 3 4 5; do
  if python3 -c "import openai" 2>/dev/null; then
    break
  fi
  pip install --no-cache-dir openai==1.82.0 python-docx==1.1.2 python-pptx==1.0.2
  sleep 4
done
python3 -c "import openai" 2>/dev/null \
  || echo "WARNING: openai still not importable after retries; LLM checks will not score" >&2

python3 /tests/judge.py 2>&1 | tee /logs/verifier/test-output.log

# Defensive default: a run must never be left without a reward file. Mark it as an
# explicit error state so an infrastructure failure is distinguishable from a genuine
# zero-reward agent submission.
[ -f /logs/verifier/reward.json ] || echo '{"reward": 0.0, "error": "verifier_no_reward_file"}' > /logs/verifier/reward.json
