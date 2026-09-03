#!/bin/bash
set -euo pipefail
python -m pip install --no-cache-dir requests==2.32.5
python /tests/verify.py
python /tests/judge.py
