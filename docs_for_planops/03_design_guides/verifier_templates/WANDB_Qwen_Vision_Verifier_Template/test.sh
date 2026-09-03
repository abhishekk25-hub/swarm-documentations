#!/bin/bash
set -euo pipefail

pip3 install --break-system-packages requests==2.31.0 2>/dev/null || pip3 install requests==2.31.0
mkdir -p /logs/verifier
python3 /tests/verify.py --config /tests/judge_config.json
