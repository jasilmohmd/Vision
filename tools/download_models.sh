#!/usr/bin/env bash
# Run from any directory; Python handles downloads on Windows and Linux.
set -euo pipefail
cd "$(dirname "$0")/.."
"${PYTHON:-python3}" -m tools.download_models "$@"
