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
