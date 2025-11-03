#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/logs/log_original.txt"
METRICS_FILE="$SCRIPT_DIR/logs/metrics_original.json"
PERF_FILE="$SCRIPT_DIR/performance/time_original.txt"

rm -f "$LOG_FILE" "$METRICS_FILE" "$PERF_FILE"

"$SCRIPT_DIR/setup.sh"

if [[ "${OS:-}" == "Windows_NT" ]] || [[ "${OSTYPE:-}" == msys* ]] || [[ "${OSTYPE:-}" == cygwin* ]]; then
  # shellcheck disable=SC1090
  source "$SCRIPT_DIR/.venv/Scripts/activate"
else
  # shellcheck disable=SC1091
  source "$SCRIPT_DIR/.venv/bin/activate"
fi

python -m tests.test_original \
  --log-file "$LOG_FILE" \
  --metrics-file "$METRICS_FILE" \
  --perf-file "$PERF_FILE"
