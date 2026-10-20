#!/bin/sh
# One environment for everyone: Python 3.13 venv OUTSIDE the repository (the model's python runs this interpreter
# under sandbox-exec, which denies reads inside the repo), pinned packages from requirements.txt.
#   sh scripts/setup_env.sh            then run everything with  ~/.poppy/venv/bin/python ...
set -e
VENV="$HOME/.poppy/venv"
PY="${PYTHON:-python3.13}"
command -v "$PY" >/dev/null 2>&1 || { echo "python3.13 not found; install Python 3.13 (brew install python@3.13) or set PYTHON=/path/to/python3.13"; exit 1; }
"$PY" -c 'import sys; assert sys.version_info[:2] == (3, 13), sys.version' || { echo "need Python 3.13.x"; exit 1; }
if [ ! -x "$VENV/bin/python" ]; then "$PY" -m venv "$VENV"; echo "created $VENV"; fi
"$VENV/bin/python" -m pip install --quiet --upgrade pip
"$VENV/bin/python" -m pip install --quiet -r "$(dirname "$0")/../requirements.txt"
echo "ready: $VENV  ($("$VENV/bin/python" --version))"
echo "next:  $VENV/bin/python scripts/check_env.py"
