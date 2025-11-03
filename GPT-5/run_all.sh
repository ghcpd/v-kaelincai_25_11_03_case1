#!/usr/bin/env bash
set -euo pipefail
ROOT="$(dirname "$0")"
pushd "$ROOT" >/dev/null
bash ProjectA/run_tests.sh
bash ProjectB/run_tests.sh
python generate_comparison.py
echo "All test suites executed. See compare_report.md"
popd >/dev/null