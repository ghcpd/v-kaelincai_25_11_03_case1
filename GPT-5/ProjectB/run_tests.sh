#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -d .venv ]; then
  bash setup_optimized.sh
fi
source .venv/bin/activate
python tests/test_optimized.py > logs/run_output.txt 2>&1 || true
echo "[ProjectB] Tests executed. See logs/log_optimized.txt and performance/summary.json"