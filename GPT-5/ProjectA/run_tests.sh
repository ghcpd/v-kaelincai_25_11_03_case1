#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -d .venv ]; then
  bash setup.sh
fi
source .venv/bin/activate
python tests/test_original.py > logs/run_output.txt 2>&1 || true
echo "[ProjectA] Tests executed. See logs/log_original.txt and performance/summary.json"