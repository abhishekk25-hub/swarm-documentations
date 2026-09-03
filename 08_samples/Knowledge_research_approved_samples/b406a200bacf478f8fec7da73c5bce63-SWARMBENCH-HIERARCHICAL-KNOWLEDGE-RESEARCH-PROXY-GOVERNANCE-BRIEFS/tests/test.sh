#!/bin/bash
set -uo pipefail
mkdir -p /logs/verifier

# Same as language-memory-models survey: install requests at grade time so the
# LLM judge is not blocked by Cloudflare 1010 on Python-urllib's User-Agent.
python3 -m pip install --no-cache-dir requests==2.32.3 >/logs/verifier/pip-install.log 2>&1 || true

FROZEN=/logs/verifier/briefs_frozen
rm -rf "$FROZEN" 2>/dev/null || true
mkdir -p "$FROZEN"
if [ -d /logs/agent/briefs ]; then
  cp -a /logs/agent/briefs/*.md "$FROZEN"/ 2>/dev/null || true
fi
export VERIFY_FROZEN_DIR="$FROZEN"
echo "Froze $(ls -1 "$FROZEN"/*.md 2>/dev/null | wc -l | tr -d ' ') briefs at verifier start for scoring." \
  | tee /logs/verifier/freeze.log

python3 /tests/verify.py 2>&1 | tee /logs/verifier/test-output.log
[ -f /logs/verifier/reward.json ] || echo '{"reward": 0, "total_static_check_score": 0, "total_reward_hacking_check_score": 0, "total_partial_oracle_check_score": 0}' > /logs/verifier/reward.json
