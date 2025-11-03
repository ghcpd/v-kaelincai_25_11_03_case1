#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$PROJECT_DIR"
./setup_optimized.sh
if [[ -d ".venv/Scripts" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi
mkdir -p logs performance
: > logs/log_optimized.txt
: > performance/time_optimized.txt
PYTHONPATH="$PROJECT_DIR/src" pytest --disable-warnings --maxfail=1 -q | tee logs/log_optimized.txt
python -m src.profile_runner >> performance/time_optimized.txt
