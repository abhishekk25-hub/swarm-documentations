#!/bin/bash
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERIFIER_OUTPUT_DIR="${VERIFIER_OUTPUT_DIR:-/logs/verifier}"
mkdir -p "$VERIFIER_OUTPUT_DIR"
cd "$HERE"

pip install --quiet openai==1.51.0 httpx==0.27.2 requests==2.32.3 pypdf==4.3.1 \
  > "$VERIFIER_OUTPUT_DIR/pip-install.log" 2>&1 \
  || echo "verifier dependency install failed; verify.py may still run with available packages" \
    > "$VERIFIER_OUTPUT_DIR/verifier_error.txt"

python "$HERE/verify.py" 2>&1 | tee -a "$VERIFIER_OUTPUT_DIR/test-output.log" "$VERIFIER_OUTPUT_DIR/test-stdout.txt"
STATUS=${PIPESTATUS[0]}

if [ "$STATUS" -ne 0 ]; then
  echo "verify.py exited with code $STATUS (verifier/infra error, not a genuine zero)" \
    >> "$VERIFIER_OUTPUT_DIR/verifier_error.txt"
fi

if [ ! -f "$VERIFIER_OUTPUT_DIR/reward.txt" ]; then
  echo "verify.py did not produce reward.txt (verifier/infra error)" \
    >> "$VERIFIER_OUTPUT_DIR/verifier_error.txt"
  echo 0.0 > "$VERIFIER_OUTPUT_DIR/reward.txt"
fi

if [ ! -f "$VERIFIER_OUTPUT_DIR/reward.json" ]; then
  echo '{"reward": null, "invalid_evaluation": true, "error": "verify.py did not write reward.json"}' \
    > "$VERIFIER_OUTPUT_DIR/reward.json"
fi

echo "reward=$(cat "$VERIFIER_OUTPUT_DIR/reward.txt")"
exit $STATUS
