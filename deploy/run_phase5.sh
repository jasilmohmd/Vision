#!/usr/bin/env bash
# Keep quoted commands on Linux; Windows launcher passes only this script path.
set -euo pipefail
PHASE5_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd -- "$PHASE5_ROOT"
PHASE5_MODE="${1:-live}"
case "$PHASE5_MODE" in
  network)
    printf 'Checking laptop mock network for60s; no capture/movement commands.\n'
    exec .venv/bin/python -m deploy.check_mock_network --seconds 60
    ;;
  live|benchmark) ;;
  *) printf 'Usage: bash deploy/run_phase5.sh [network|live|benchmark]\n' >&2; exit 2 ;;
esac
PHASE5_PGREP_STATUS=0
pgrep -f '[p]ython.*-m app\.main' >/dev/null || PHASE5_PGREP_STATUS=$?
case "$PHASE5_PGREP_STATUS" in
  0) printf 'Stop the existing app before this run.\n' >&2; exit 2 ;;
  1) ;;
  *) printf 'Process check failed; refusing to run concurrently.\n' >&2; exit 2 ;;
esac
if [[ "$PHASE5_MODE" == benchmark ]]; then
  PHASE5_STREAM="$(.venv/bin/python -c 'from app.config import load_config; c=load_config("config.phase5.yaml"); print(f"http://{c.s3_ip}:{c.camera_stream_port}/stream")')"
  exec .venv/bin/python -m tools.bench_vision --config config.phase5.yaml --source "$PHASE5_STREAM" --target person --frames 100 --output logs/phase5-benchmark.json
fi
exec .venv/bin/python -m app.main --config config.phase5.yaml --mic udp --seconds 600
