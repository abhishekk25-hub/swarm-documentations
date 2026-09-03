#!/bin/bash
set -euo pipefail
mkdir -p /logs/verifier

pip install --quiet openpyxl==3.1.5 requests==2.32.3 >/dev/null 2>&1 || true

set +e
python3 /tests/judge.py 2>&1 | tee /logs/verifier/test-output.log
set -e

[ -f /logs/verifier/reward.txt ] || echo 0 > /logs/verifier/reward.txt

exit 0
