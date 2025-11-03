#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

pushd "$ROOT_DIR/project_a" > /dev/null
./run_tests.sh
popd > /dev/null

pushd "$ROOT_DIR/project_b" > /dev/null
./run_tests.sh
popd > /dev/null

python "$ROOT_DIR/generate_compare_report.py"

echo "Comparison report generated at $ROOT_DIR/compare_report.md"
