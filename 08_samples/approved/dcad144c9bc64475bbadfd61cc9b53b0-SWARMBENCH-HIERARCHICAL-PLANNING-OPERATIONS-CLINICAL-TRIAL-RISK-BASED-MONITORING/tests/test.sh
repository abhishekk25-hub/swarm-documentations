#!/bin/bash
set -uo pipefail
mkdir -p /logs/verifier /logs/agent

# Fail closed: if anything below errors out, leave a 0.0 reward behind so a
# broken run can never silently score as a pass.
fail_closed() {
  if [ ! -s /logs/verifier/reward.txt ]; then
    echo "0.0" > /logs/verifier/reward.txt
  fi
}
trap fail_closed EXIT

# The verifier only needs openpyxl. Install if missing (pinned), quietly.
python3 -c "import openpyxl" 2>/dev/null || pip install --quiet openpyxl==3.1.5

python3 /tests/verify.py 2>&1 | tee /logs/verifier/test-output.log

exit 0
