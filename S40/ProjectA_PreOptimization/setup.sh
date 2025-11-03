#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

python -m venv "$VENV_DIR"

if [[ "${VIRTUAL_ENV:-}" != "" ]]; then
  deactivate || true
fi

if [[ "${OS:-}" == "Windows_NT" ]] || [[ "${OSTYPE:-}" == msys* ]] || [[ "${OSTYPE:-}" == cygwin* ]]; then
  # shellcheck disable=SC1090
  source "$VENV_DIR/Scripts/activate"
else
  # shellcheck disable=SC1091
  source "$VENV_DIR/bin/activate"
fi

pip install --upgrade pip
pip install -r "$SCRIPT_DIR/requirements.txt"
