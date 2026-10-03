# Project scope and architecture

## Phase 3 runtime map - 2026-10-04T01:38:42+05:30

app/main.py now runs devices/workers; --check-config validates without devices.
Default audioUDP; --mock selects localhost camera/light hosts, same wire contract.
app/state.py owns commands/photo jobs; control/controller.py angle math;
vision/stream.py latest MJPEG; storage.py numbered photos/atomic index;
gallery/server.py and templates gallery. io/ has camera/light/speaker clients.
tools/mock_camera.py shifts a320x240 crop inside full webcam frame; held JPEG
capture persists until ACK. tools/mock_voice_unit.py sends raw16kHz mono s16le
1024-byte packets and prints5006 light states/flash restore. README has commands.
One app writer per photos_dir. Hardware/firmware owned separately by Session B.

---

Earlier entries below are historical snapshots; this current software update
takes precedence. Session B records are preserved.

## Firmware Session B scaffold - 2026-10-04

firmware/AGENTS.md scopes Session B to FIRMWARE_PLAN.md; firmware/STATUS.md and
firmware/context/HANDOFF.md track its independent gates. User allows shared
context updates. firmware/secrets.example.h contains zero-address placeholders;
firmware/.gitignore excludes secrets, toolchain, builds and check media.
firmware/toolchain_probe/ and tools/verify_toolchain.ps1 prove compilation only,
without pin maps, network or uploads. Bench/check implementations await F1-F3.

Updated: 2026-10-04T01:17:16+05:30 (Asia/Calcutta).

## Purpose

Hands-free, wheelchair-mounted photography for a user who can move their head
and speak. Core flow: "Camera, track person" -> follows person -> "Camera,
shoot" -> saved photo -> phone gallery. Preserve the full planned scope unless
user explicitly approves a cut.

## Components

- Camera head: ESP32-S3 camera + pan/tilt servos, MJPEG stream, absolute moves,
  full-resolution capture held until acknowledgement.
- Voice unit: ESP32-C3 SuperMini + INMP441, NeoPixel, optional IR trigger.
- Brain: Arduino Uno Q Linux/Python; recognition, detection, tracking, control,
  photo storage, gallery. Use mocks on the laptop until hardware exists.
- Network: phone hotspot, fixed IPs to be confirmed; no runtime internet.

## Contracts to preserve

Camera HTTP: stream on :81/stream (320x240 MJPEG); HTTP :80 /move?pan=...&tilt=...
returns clamped angles (firmware specifies target angles while slewing); /capture returns held JPEG; /ack frees it; /status
returns pan, tilt, uptime_s, held_photo and rssi. See source plan for exact JSON.

Voice UDP: C3 -> Uno Q :5005 raw signed little-endian 16-bit mono PCM, 16 kHz,
512 samples/1024 bytes per packet. Uno Q -> C3 :5006 ASCII light states.
Optional C3 -> Uno Q :5007 ASCII shoot. Gallery :8080.

Light states: ready, heard, tracking, nosubject, saved, error, reconnect, sleep.
Colour/flash timing is defined in the plan; do not alter it silently.
Wake word: camera. Commands: track person/face/dog/cat, stop tracking, left,
right, up, down, a bit left/right/up/down, centre, shoot, burst, timer, sleep, wake.

## Config defaults

IPs are examples, not confirmed hardware addresses: S3 192.168.43.101,
C3 .102, Uno Q .103. Detection every 5 frames; dead_zone .08; gain_deg 12;
max_step_deg 4; pan 10..170; tilt 40..140; both invert flags false;
Vosk confidence .7; centre timeout 1.5 seconds; photos_dir photos.
Relative photo paths resolve beside the selected YAML file. See ../config.yaml
for authoritative current values and ../app/config.py for typed validation.

## Implemented file map

- app/config.py: frozen Config dataclass, YAML loading, validation and path resolution.
- app/main.py: CLI flags/config validation only (Phase 0 runtime scaffold).
- app/vision/detector.py: YOLOv8/11 raw ONNX inference, letterboxing, class filter,
  NMS, clipped source-image boxes. Detection tuple: (class, confidence, x, y, w, h).
- app/vision/face.py: YuNet FaceDetectorYN, same tuple shape.
- app/vision/tracker.py: CSRT preferred/KCF fallback, detect every N frames or
  after failure, nearest prior box centre; initially choose highest confidence.
  Returns (box_or_None, offset_or_None), dx/dy in [-1, 1], right/down positive.
  Missing detection clears active tracking; prior box remains for association.
- tools/export_onnx.py: laptop-only static YOLOv8n FP32 320 export, opset 17.
- tools/download_models.py and .sh: official YuNet and small English Vosk download.
- tools/demo_vision.py: preview/console offsets, headless or frame-limited mode.
- tools/bench_vision.py: detector-only and detector+tracker FPS, cached frames,
  optional JSON report. tools/vision_common.py shares source/CLI/pipeline setup.
- tests/test_config.py, tests/test_vision.py: current automated coverage.
- requirements-laptop.txt: runtime + pytest; requirements-export.txt: laptop
  Ultralytics/ONNX export; requirements-unoq.txt: headless runtime only.

## Future-phase placeholders

app/vision/stream.py; app/control/controller.py; app/io/*;
app/state.py; app/storage.py; app/gallery/server.py and templates/index.html;
tools/mock_camera.py, mock_voice_unit.py; deploy/install_unoq.sh and photo-rig.service.
Firmware sketches/check tools are owned independently by Session B. Legacy root
tools/check_camera.py and check_voice_unit.py remain unused scaffold placeholders.
These are scaffold files, not functioning implementations.

## Local-only artifacts

models/yolov8n.pt, yolov8n.onnx, face_detection_yunet_2023mar.onnx,
vosk-model-small-en-us-0.15/, validation-bus.jpg and benchmark-webcam.json.
Models, generated media, environments and secrets must stay out of commits.

## Phase 2 file map

- app/voice/commands.py: frozen Command dataclass, 19 supported phrases, grammar,
  parse(text) -> Command or None. Wake word and whole phrase must match.
- app/voice/audio_source.py: AudioSource interface/context manager,
  LaptopMicSource via sounddevice RawInputStream and UdpAudioSource on :5005.
  Both return s16le/16 kHz/mono chunks; UDP contract is exactly 1024 bytes.
- app/voice/recognizer.py: VoiceRecognizer processes PCM and puts VoiceEvent
  objects on a Queue (heard/command/low_confidence). Configured threshold gates
  every final word; flush handles residual speech; run supports a future worker.
- tools/demo_voice.py: standalone voice CLI and guided live acceptance check.
- tests/test_voice.py: 47 parser, recognizer, audio and UDP cases at last run.
- No state machine, light client, control or app orchestration in Phase 2.

## Ownership after the updated software plan

Session A: app/, root tools/, deploy/, config.yaml and software context/docs.
Session B: all firmware/, following FIRMWARE_PLAN.md F0-F5. Software Phase 4
is skipped. Canonical hardware checks: firmware/tools/check_camera.py and
firmware/tools/check_voice_unit.py (A may run, never edit). Shared contract in
SOFTWARE_PLAN.md section 2 remains authoritative. Unknown IPs must be confirmed.
Gate 0 is network readiness; board pin/model confirmation is Session B Gate F0.
See PLAN_REVIEW.md for missing hardware plan and other cross-session findings.

## Confirmed final voice path / current test setup

Final hardware remains INMP441 MEMS -> ESP32-C3 SuperMini -> Wi-Fi UDP 5005 ->
Uno Q UdpAudioSource/Vosk. 16 kHz mono s16le, 512 samples/1024 bytes per packet.
Firmware B owns I2S conversion/transmission; software A owns reception and
recognition. Current headset is a temporary accepted Phase 2 test input, not
final hardware. Its passed checklist does not replace firmware F3/Phase 7 checks.

## Firmware Session B: F1 implemented for team testing - 2026-10-04

User explicitly requested actual F1 test firmware now while remaining F0 checks
continue; do not keep the software team waiting for sketches that do not exist.
All four implemented: servo_sweep, neopixel_test, mic_level, ir_test, plus
verify_bench.ps1 and firmware/TEAM_TESTING.md with setup/uploads/exact GateF1.
Compile command: ./firmware/tools/verify_bench.ps1 -IncludeServoStress; exit0.
CLI1.5.1/core3.3.11/ESP32Servo3.2.1/NeoPixel1.15.5. Build sizes flash/RAM bytes:
servo299058/22724; pixel298986/14532; mic330354/17796; IR296890/14500;
both-servo298958/22724. Servo dependency emitted upstream MCPWM/unused-variable
warnings. No compile error. No board upload, physical observation or new app tests.
S3 profile esp32:esp32:esp32s3:PSRAM=opi,FlashSize=16M (UART connector default);
C3 esp32:esp32:esp32c3:CDCOnBoot=cdc. F1 bench programs use no Wi-Fi or secrets.
Confirmed servo panGPIO1/tiltGPIO2; I2S4/5/6, SHIFT14, left; pixel7 GRB brightness40;
IR1 active-low remains provisional pending real sensor test. No camera/voice runtime
firmware yet. User image camera map correspondence recorded; PWDN/RESET unresolved.
F0 other setup checks still ongoing; F1 real-part acceptance pending. No phase
completion or F2 advancement claimed. HARDWARE_PLAN.md absent; live IP verification
follows Wi-Fi firmware. Preserve Session A software scope/results separately.
Existing HEAD:5194c5ed39c02b2bcc91bfaef899492f5788838c. Intended testing commit:
fw phase 1: add bench sketches for hardware testing. No staging/commit/push here.
Next action: user commits/pushes actual bench firmware/context; team flashes on
identified boards and returns Gate F1 observations/F1 DONE. Fix failures within F1.
