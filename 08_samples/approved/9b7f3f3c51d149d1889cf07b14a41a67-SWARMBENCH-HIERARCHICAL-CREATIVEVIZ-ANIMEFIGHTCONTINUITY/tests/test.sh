#!/bin/bash
set -uo pipefail
mkdir -p /logs/verifier /logs/agent

# Verifier-only dependencies (not baked into the agent image): tesseract for HUD/callout OCR,
# pytesseract + openai for the OCR and the multimodal LLM-judge slice. judge.py fails open on
# any of these, so a failed install degrades gracefully rather than crashing the verifier.
apt-get update >/dev/null 2>&1 && apt-get install -y --no-install-recommends tesseract-ocr >/dev/null 2>&1 || true
pip install --quiet pytesseract==0.3.13 openai==1.109.1 >/dev/null 2>&1 || true

python3 /tests/judge.py --agent-output /logs/agent/output.json \
  --gold-clusters /tests/gold_clusters.json --gold-fight /tests/gold_fight.json 2>&1 | tee /logs/verifier/judge-output.log || true
[ -f /logs/verifier/reward.txt ] || echo 0 > /logs/verifier/reward.txt
cat /logs/verifier/reward.txt
