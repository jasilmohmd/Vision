#!/usr/bin/env bash
# Phase 5: Linux runtime only. No firmware, export dependencies or systemd setup.
set -euo pipefail
PHASE5_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
PHASE5_CONFIG="$PHASE5_ROOT/config.phase5.yaml"
PHASE5_SKIP_APT=0
PHASE5_CHECK_ONLY=0
usage() {
  cat <<'HELP'
Usage: bash deploy/install_unoq.sh [--config PATH] [--skip-apt] [--check-only]
Run on Uno Q Linux after copying source and models. Creates local .venv, installs
requirements-unoq.txt, verifies model checksums and loads all three models.
--skip-apt   Skip OS packages when already prepared.
--check-only  Validate existing venv/config/models without installing anything.
Does not flash firmware or create/enable a systemd service.
HELP
}
while (($#)); do
  case "$1" in
    --config) (($# >= 2)) || { usage; exit 2; }; PHASE5_CONFIG="$2"; shift 2 ;;
    --skip-apt) PHASE5_SKIP_APT=1; shift ;;
    --check-only) PHASE5_CHECK_ONLY=1; shift ;;
    --help|-h) usage; exit 0 ;;
    *) printf 'Unknown option: %s\n' "$1" >&2; usage; exit 2 ;;
  esac
done
[[ "$(uname -s)" == Linux ]] || { printf 'Run this installer on Uno Q Linux.\n' >&2; exit 1; }
[[ -f "$PHASE5_CONFIG" ]] || { printf 'Missing config: %s\n' "$PHASE5_CONFIG" >&2; exit 1; }
cd -- "$PHASE5_ROOT"
if (( ! PHASE5_CHECK_ONLY )); then
  if (( ! PHASE5_SKIP_APT )); then
    command -v apt-get >/dev/null || { printf 'Expected Debian apt-get; use --skip-apt if dependencies are prepared.\n' >&2; exit 1; }
    PHASE5_MISSING=()
    for PHASE5_PACKAGE in python3 python3-venv python3-pip libgomp1 libatomic1; do
      [[ "$(dpkg-query -W -f='${Status}' "$PHASE5_PACKAGE" 2>/dev/null || true)" == 'install ok installed' ]] || PHASE5_MISSING+=("$PHASE5_PACKAGE")
    done
    if ((${#PHASE5_MISSING[@]})); then
      PHASE5_SUDO=()
      if (( EUID != 0 )); then PHASE5_SUDO=(sudo); fi
      "${PHASE5_SUDO[@]}" apt-get update
      "${PHASE5_SUDO[@]}" apt-get install -y "${PHASE5_MISSING[@]}"
    fi
  fi
  python3 -m venv "$PHASE5_ROOT/.venv"
  "$PHASE5_ROOT/.venv/bin/python" -m pip install --upgrade pip
  "$PHASE5_ROOT/.venv/bin/python" -m pip install --prefer-binary --only-binary=opencv-contrib-python-headless,onnxruntime,numpy -r requirements-unoq.txt
  "$PHASE5_ROOT/.venv/bin/python" -m pip check
fi
[[ -x "$PHASE5_ROOT/.venv/bin/python" ]] || { printf 'Missing Linux runtime venv. Run installer without --check-only.\n' >&2; exit 1; }
PHASE5_VERIFY=()
if [[ -f deploy/phase5-model-manifest.json ]]; then PHASE5_VERIFY=(--manifest deploy/phase5-model-manifest.json); fi
"$PHASE5_ROOT/.venv/bin/python" -m tools.check_runtime --require-linux --config "$PHASE5_CONFIG" "${PHASE5_VERIFY[@]}" --report logs/phase5-preflight.json
printf 'Runtime ready. Start laptop mocks, then run from %s:\n' "$PHASE5_ROOT"
printf '.venv/bin/python -m app.main --config %q --mic udp\n' "$PHASE5_CONFIG"
