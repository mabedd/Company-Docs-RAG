#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

pick_python() {
  for candidate in python3.13 python3.12 python3.11 python3; do
    if command -v "$candidate" >/dev/null 2>&1; then
      version="$("$candidate" -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')"
      major="${version%%.*}"
      minor="${version#*.}"
      if [ "$major" -gt 3 ] || { [ "$major" -eq 3 ] && [ "$minor" -ge 11 ]; }; then
        echo "$candidate"
        return 0
      fi
    fi
  done
  return 1
}

if [ ! -d .venv ]; then
  python_bin="$(pick_python)" || {
    echo "Python 3.11+ is required. Install it, then rerun ./run.sh"
    exit 1
  }
  echo "Creating virtualenv with $python_bin..."
  "$python_bin" -m venv .venv
  .venv/bin/pip install -r requirements.txt
fi

source .venv/bin/activate
exec uvicorn app.main:create_app --factory --reload --host 0.0.0.0 --port 8000 "$@"
