#!/usr/bin/env bash
set -euo pipefail
python -m venv .venv || exit 1
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements_optimized.txt
echo "[ProjectB] Environment setup complete."