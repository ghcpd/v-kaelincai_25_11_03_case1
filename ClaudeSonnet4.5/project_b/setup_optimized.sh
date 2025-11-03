#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$PROJECT_DIR"
python -m venv .venv
if [[ -d ".venv/Scripts" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi
python -m pip install --upgrade pip
python -m pip install --no-cache-dir -r requirements_optimized.txt
