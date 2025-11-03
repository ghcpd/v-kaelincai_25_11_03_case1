#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

echo "========================================"
echo "Running All Tests and Generating Report"
echo "========================================"
echo ""

echo "=== Project A (Initial Implementation) ==="
pushd "$ROOT_DIR/project_a" > /dev/null
./run_tests.sh || echo "Warning: Project A tests encountered issues, continuing..."
popd > /dev/null
echo ""

echo "=== Project B (Optimized Implementation) ==="
pushd "$ROOT_DIR/project_b" > /dev/null
./run_tests.sh || echo "Warning: Project B tests encountered issues, continuing..."
popd > /dev/null
echo ""

echo "=== Generating Comparison Report ==="
python "$ROOT_DIR/generate_compare_report.py"

echo ""
echo "========================================"
echo "Comparison report generated successfully!"
echo "Location: $ROOT_DIR/compare_report.md"
echo "========================================"
