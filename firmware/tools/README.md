# Hardware checks

verify_toolchain.ps1 compiles the F0 probe; verify_bench.ps1 compiles all four
F1 bench sketches with optional simultaneous-servo variant. Neither uploads.
See ../TEAM_TESTING.md for manual upload commands and physical acceptance.

Phase F2: check_camera.py --ip <S3_IP> exercises status, a small servo pattern,
QVGA MJPEG, higher-resolution capture, retained-photo retry, ack and stream
recovery. Requires requests. JPEGs default to ignored ../.build/camera_checks/.
The checker also moves pan/tilt through85..95degrees during active streaming,
prints each move latency, requires acknowledgements below2s, and checks
commanded slew plus fresh video frames. These are software readbacks; the user
must still verify actual direction, smoothness and return to neutral.
Target/command readback cannot measure physical servo position; observe motion.
Do not run simultaneously with the app: the stream server serves one viewer.

check_voice_unit.py remains a Phase F3 task.

Phase F3: check_voice_unit.py --ip <C3_IP> runs on the configured audio receiver.
It records5s of UDP5005 PCM to ignored .build/voice_checks/check.wav, checks1024
byte packet sizes and observed rate/RMS/peak, then sends all8 light states.
User readiness is required before the microphone/colour checks. It cannot
measure exact packet loss because the contract PCM datagrams have no sequence
numbers; estimated rate shortfall is reported explicitly. IR remains omitted.
