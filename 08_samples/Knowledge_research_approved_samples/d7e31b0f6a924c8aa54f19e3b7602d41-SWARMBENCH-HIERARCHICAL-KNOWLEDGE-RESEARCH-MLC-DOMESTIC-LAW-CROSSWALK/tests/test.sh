#!/bin/bash
set -uo pipefail
mkdir -p /logs/verifier

pip install --no-cache-dir requests==2.32.3 pypdf==5.1.0 >/logs/verifier/test-deps-install.log 2>&1

FROZEN=/logs/verifier/frozen
rm -rf "$FROZEN"
mkdir -p "$FROZEN/shards"
cp -a /logs/agent/mlc_transposition_workbook.xlsx "$FROZEN/" 2>/dev/null || true
cp -a /logs/agent/article_lineage_graph.json "$FROZEN/" 2>/dev/null || true
cp -a /logs/agent/unresolved_research_queue.csv "$FROZEN/" 2>/dev/null || true
cp -a /logs/agent/source_coverage.csv "$FROZEN/" 2>/dev/null || true
cp -a /logs/agent/method_audit.json "$FROZEN/" 2>/dev/null || true
cp -a /logs/agent/comparative_legal_memorandum.md "$FROZEN/" 2>/dev/null || true
cp -a /logs/agent/comparative_legal_memorandum.pdf "$FROZEN/" 2>/dev/null || true
cp -a /logs/agent/shards/. "$FROZEN/shards"/ 2>/dev/null || true
export VERIFY_FROZEN_DIR="$FROZEN"
export VERIFY_INPUTS="${VERIFY_INPUTS:-/input_artifacts}"
export VERIFY_REWARD_PATH=/logs/verifier/reward.json
export VERIFY_STATUS_PATH=/logs/verifier/verify_status.json
export VERIFY_PARTIAL_ORACLE_PATH=/tests/partial_oracle.json
echo "Froze workbook, graph, queue, coverage, audit, memorandum and $(ls -1 "$FROZEN"/shards/*.json 2>/dev/null | wc -l) shard files at verifier start." \
  | tee /logs/verifier/freeze.log

python3 /tests/verify.py 2>&1 | tee /logs/verifier/test-output.log

if [ ! -f /logs/verifier/reward.json ]; then
  printf '%s\n' '{"reward": 0.0, "total_static_check_score": 0.0, "total_reward_hacking_check_score": 0.0, "total_partial_oracle_check_score": 0.0}' > /logs/verifier/reward.json
  [ -f /logs/verifier/verify_status.json ] || printf '%s\n' '{"status": "infra_error", "reason": "verify.py did not produce reward.json; the fallback all-zero reward.json is an infrastructure failure, not a graded zero-quality submission."}' > /logs/verifier/verify_status.json
fi

exit 0
