#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_A="$ROOT/ProjectA_PreOptimization"
PROJECT_B="$ROOT/ProjectB_PostOptimization"

pushd "$PROJECT_A" >/dev/null
./run_tests.sh
popd >/dev/null

pushd "$PROJECT_B" >/dev/null
./run_tests.sh
popd >/dev/null

python "$ROOT/report_tools/generate_report.py" \
  --project-a-metrics "$PROJECT_A/logs/metrics_original.json" \
  --project-b-metrics "$PROJECT_B/logs/metrics_optimized.json" \
  --project-a-perf "$PROJECT_A/performance/time_original.txt" \
  --project-b-perf "$PROJECT_B/performance/time_optimized.txt" \
  --output "$ROOT/compare_report.md"

echo "Comparison report written to $ROOT/compare_report.md"
