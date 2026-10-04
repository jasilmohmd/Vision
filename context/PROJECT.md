# Project scope and architecture

## CAD artifact map - 2026-10-04

enclosure/vision_enclosures.scad is a standalone parametric model for seven
enclosure designs, with nine individual part selections plus layout and assembly
previews. enclosure/README.md explains usage, measurements and prototype limits.
enclosure/check_meshes.py validates ASCII exports; enclosure/validation/ contains
nine STL prototypes, render logs, preview PNGs and the mesh report. No dependency
on the app or firmware, and no phase acceptance is changed by these artifacts.

---

## Verified Uno Q runtime - 2026-10-04T05:19:45+05:30

Installed into /home/arduino/Vision on Linux aarch64, Python3.13.5. Headless
contrib4.14.0/ORT1.30.0/NumPy2.5.3; no torch/Ultralytics in that runtime.
Mock endpoints both laptop192.168.29.58; app/gallery on UnoQ192.168.29.199:8080.
16 model checksums matched; all models/CSRT/KCF load and photos directory writable.
No service enabled, no firmware dependency used. Live/benchmark checks pending.

## Phase 5 deployment map - 2026-10-04T04:37:24+05:30

Deploy scripts are functional: package_unoq.py emits explicit source/model tarballs
and mock config; copy_to_unoq.ps1 performs interactive SSH/scp/extract/install;
install_unoq.sh handles Linux apt/venv/requirements and tools.check_runtime verifies
loaded models, checksums, trackers/storage and versions. deploy/README.md has exact
network, install, mock/phone-gallery and benchmark commands. photo-rig.service
remains untouched Phase8 placeholder. Root config preserved; generated config,
archives/reports are ignored logs/. Tests/test_deployment.py covers transfer safety.
Source/models land in user ~/Vision, preserving photos and normal config.yaml.
Camera mock --bind exposes exact same contract on selected laptop LAN address.
UDP light/audio protocol and firmware ownership unchanged. Main optional --tracker
supports KCF for Phase5 tuning; default CSRT unchanged. No board pin changes.

---

Earlier records are historical; this software update takes precedence.

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

## Prototype scope: IR deferred to future TODO - 2026-10-04

User explicitly requests putting IR into future-feature TODO and skipping it in
this prototype. Added firmware/TODO.md. Optional C3 GPIO1 head/cheek shoot trigger
is deferred; future prototype voice firmware must default USE_IR=0. Retain
compiled ir_test for future validation, with hardware polarity/placement untested.
Current prototype uses voice-triggered shooting. No shared contract change.
Required F1 real-part checks passed: NeoPixel colours/patterns user-confirmed,
mic synchronized speech response ~5x quiet with no clipping, servo smoothness/
neutral return user-confirmed with minimum rail5.05V. IR explicitly omitted;
it is no longer an outstanding prototype acceptance item. F1 DONE not received.
User's earlier wait pauses further physical operations; this is documentation
maintenance only, not authorization to start F2. No motion/upload/test rerun.
Current S3 COM19 retains both-servo bench, C3 COM18 retains mic_level.
Existing HEAD08fabad4fff50b1d9172bef0119a24e9fb70b8cb. No commit/push performed;
intended docs message if requested: fw docs: record bench results and defer IR.
Next action when user resumes: obtain F1 DONE, refresh context before commit,
then start F2 only under user direction. Preserve Session A records and scope.

## Firmware F2 bench addressing and scope - 2026-10-04
User acknowledged F1 DONE and explicitly approved DHCP for first S3 camera
check; production static IPs remain to be chosen after connectivity. Credentials
are locally configured in ignored firmware/camera_head/secrets.h, never recorded
here. Camera GPIO signal mapping is supplied-image/core matched; unlabeled
PWDN/RESET=-1 remain hardware-init acceptance. Servo boot centre assumes F1
aligned neutral, without physical position feedback. IR stays future TODO.
Uno Q installation belongs to another active session; do not operate it here.

## Camera bench integration decisions - 2026-10-04
DHCP benchS3IP192.168.29.231 observed; productionstaticIP still deferred. Camera
map/OV3660/PSRAM init physically verified; user-confirmed pan/tilt motion passed
under camera firmware. Chunked JPEG transfer and video pause during photo send
preserve JPEG/endpoint contract. Diagnostics distinguish targets from position.
Use laptop app with real S3 and selected boAt microphone for F2 diagnostic;
C3 remains bench, lights local-only, no Uno Q work. Temporary config/wrapper and
private images remain ignored under firmware/.build. Voice shoot check awaits
user readiness and timely explicit Speak now cue. F2 reliability is not complete.

## Current F2 implementation addition - 2026-10-04
firmware/camera_head now has a dedicated20ms servo task with separate mutex,
10fps stream pacing, capture freeze and additive commanded-movement timing
status fields. firmware/tools/check_camera.py checks responsiveness under
streaming and prints PWM settle timing. No endpoint or confirmed pin changes.
New source compiled; new flash/physical acceptance deferred at user request.

## Voice path addition - 2026-10-04
app/voice/endpoint.py now owns bounded monoPCM speech segmentation; recognizer
uses it before unchanged command/confidence parsing. app/main.py and standalone
voice demo calibrate input before Ready. tests/test_voice_endpoint.py covers
endpointing and shutdown regressions. No network/interface-contract changes,
no dependencies added, no firmware responsibility moved to Session A.

## Voice commit boundary - 2026-10-04
Prepared voice-only commit includes endpoint module, recognizer and demo,
calibration integration hunk, regression tests and voice docs plus required
shared context/status. Deployment/tracker and all firmware implementation
remain separate pending work. Normal app directions physically validated;
full integration/video acceptance still pending.

## Firmware commit preparation under user override - 2026-10-04
User explicitly said overide after the Session A firmware ownership restriction
was explained. This authorizes preparing the pending firmware commit and its
context here; it does not authorize future-phase implementation or Uno Q work.
Existing HEAD64994afafbb4265f00685a32b6cc66c15b8809f4, voice fix, equals fetched
origin/main. Intended message: fw phase 2: implement S3 camera head and servo control.
Scope: camera_head.ino/camera_pins.h/README, tools/check_camera.py/tools README,
secrets.example.h DHCP toggle, TODO optional IR deferral, TEAM_TESTING/AGENTS,
firmware STATUS/context handoff and mandatory shared root context/status.
Preserve unrelated software/deployment/enclosure changes. Do not include ignored
secrets, toolchain, builds, private photos or logs. Shared contract unchanged.
Reviewed implementation has OV3660/OPI PSRAM initialization; panGPIO1/tiltGPIO2;
HTTP80 control and81 QVGA MJPEG at10fps; retained higher-resolution capture until
ack; separate camera/servo mutexes and dedicated bounded2degree/20ms slew task;
commanded-movement diagnostics and exclusive-viewer endpoint checker.
Corrected stale camera pin comment to reflect earlier OV3660PID0x3660 boot.
Prior final compile/upload logs inspected:984997 program bytes,56656 globals,
upload written-data hash verified. Prior boot and software live tests provide
hardware evidence: user confirmed all four directions and smooth centre with
boAt after separate voice fix. These are historical observations, not new tests.
Checker py_compile and --help rerun successfully now; ignored credentials/build/
toolchain exclusion verified with git check-ignore. Compile-only recheck started;
its final result will be recorded separately. No flash or physical test here.
F2 remains IN PROGRESS: intermittent MJPEG timeouts, final-build full checker/
capture-ack-stream recovery, prolonged stability and remaining integration tests
are pending. C3 production voice firmware/F3 remains deferred. Phase5 Uno Q
mock-flow/gallery/benchmark and software GateA/Phase6 not advanced.
No agent commit/push. Next action: complete compile-only verification, review
explicit staged firmware/context diff, then user commits and pushes this scope.

Phase5 preparation now has isolated Uno Q test path
/home/arduino/Vision-phase5-20261004, copying models from existing deployment and
reusing its venv without reinstalling. Runtime checks passed; user deferred live
mock acceptance. Current DHCP Uno Q10.153.76.45/laptop10.153.76.189; recheck before
future tests. Original ~/Vision remains separate.

## Phase5 preparation and editor-fix commit - 2026-10-04
User explicitly requests commit and push. Existing HEAD verified
3176b5374386035afae7eb9d81eb5c6bf1379fe8.
Intended message: phase 5: prepare Uno Q deployment and runtime checks.
Commit includes deploy installer/transfer/packaging/readme/init, runtime preflight,
LAN bind option for mock camera, tracker selection in app, deployment tests,
README/.gitattributes, ESP32-S3 editor configuration and firmware editor docs,
plus shared root and firmware context/status records. Enclosure files are
unrelated untracked work and excluded; firmware implementation is already pushed.
Ignored credentials/models/photos/builds/logs are excluded. User's firmware
ownership override and direct editor-fix request cover the firmware doc records;
no sketch/pin/contract change in this commit.
Verification rerun for this commit:full pytest121 passed in6.70s, exit0;
PowerShell copy script parsed with zero errors; both editor JSON files parsed;
Uno Q isolated deployment bash -n installer and installer --check-only passed,
exit0. Runtime validated all3 models/16 checksums, CSRT/KCF, writable photos,
Linux/aarch64/Python3.13.5, OpenCV4.14/ORT1.30/NumPy2.5.3. No pip/apt install,
service restart, camera/mic opening or physical test in this commit work.
Earlier S3 editor repair compile passed984997 program bytes/56656 globals;
editor diagnostic clearance remains user-observed/pending, not agent visual QA.
User chose Prepare it; I'll test later. Live mock track-person/shoot, phone
Uno Q gallery and recorded benchmark remain unrun. Phase5/GateA/Phase6/F2/F3
are not declared complete. C3 production voice firmware remains deferred.
Current verified Uno Q10.153.76.45 and laptop10.153.76.189, USB662499217.
Prepared path/home/arduino/Vision-phase5-20261004; original~/Vision preserved.
Updated deploy README with current USB-based run/benchmark instructions and
historical-address clarification. No host-key verification bypass.
Exact next action after publishing: wait for user's readiness, recheck DHCP
addresses/headset ID, then run Phase5 mock flow/phone gallery/benchmark and
record actual acceptance. Do not advance gates or auto-start live tests.
