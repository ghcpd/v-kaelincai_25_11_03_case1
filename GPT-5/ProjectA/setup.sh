#!/usr/bin/env bash
set -euo pipefail
python -m venv .venv || exit 1
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "[ProjectA] Environment setup complete."