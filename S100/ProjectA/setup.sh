#!/usr/bin/env bash
set -euo pipefail
python -m venv .venv
if [[ "$(uname -s)" == MSYS* || "$(uname -s)" == MINGW* ]]; then
  source .venv/Scripts/activate
else
  source .venv/bin/activate
fi
pip install --upgrade pip
pip install -r requirements.txt
