#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT=$(cd "$(dirname "$0")" && pwd)
export PYTHONPATH="$PROJECT_ROOT"
if [[ -d "$PROJECT_ROOT/.venv" ]]; then
  if [[ "$(uname -s)" == MSYS* || "$(uname -s)" == MINGW* ]]; then
    source "$PROJECT_ROOT/.venv/Scripts/activate"
  else
    source "$PROJECT_ROOT/.venv/bin/activate"
  fi
fi
python -m pytest "$PROJECT_ROOT/tests" --maxfail=1 --disable-warnings -q
