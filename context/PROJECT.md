# Project scope and architecture

## Experimental BLE selection - 2026-10-04

Optional C3 BLE microphone/light transport implemented in the preceding trial;
UDP remains default and selectable by verified same-partition reflash helper.
App --mic ble requires explicit verified --ble-address. Optional Bleak3.0.2 on
Uno Q; deferred import keeps UDP users independent. Four-chunk startup cushion,
bounded PCM buffer, indexed notifications and padding/gap metrics are included.
SOFTWARE_PLAN section 2 remains unchanged. Current Session A instructions forbid
further firmware edits; Session B owns follow-up. Details and limits are in
[BLE_TRANSPORT.md](BLE_TRANSPORT.md). Current C3 is BLE; latest strict probe fails
only the 101ms notification-gap limit despite no loss or padding. S3 still times
out; physical NeoPixel colors and full voice/camera acceptance are pending.

## New-network runtime and ownership exceptions - 2026-10-04

User explicitly allowed Session A network-only firmware updates/uploads and
Wi-Fi diagnostics/connection fixes for this migration. Other firmware ownership
and pin/contract boundaries remain in force. S3 now reports disconnect reasons;
its ineffective transmit-power experiment was removed. Current board addresses
UnoQ172.20.10.2, C3172.20.10.4, S3172.20.10.5 (DHCP, reverify after restart).
Hotspot association capacity prevented all three boards plus laptop joining;
user moved laptop back to previous network. Three boards share new hotspot;
laptop live view uses USBADB forwarding8080 at http://localhost:8080/live.
All processing runs on Uno Q. No service activation or stability acceptance;
measured camera/audio gaps and current app freshness warnings still persist.

---

## Complete-project publication preparation - 2026-10-04

User explicitly requested update contexts then commit and push EVERYTHING.
This authorizes publication of all existing software,deployment,firmware,CAD,
editor and context changes; no new firmware implementation or future phases.
Existing HEAD before this commit:bf898850ed1fe0a0fc68a9f5c0e6a6a948f1087b
Intended commit message:feat: publish live tracking, C3 firmware and enclosure models
Do not invent the resulting commit hash;Git log is authoritative after publish.

Scope:read-only live annotated /live + /live/frame.jpg using UnoQ's existing
tracking snapshot,gallery link;new gallery tests;Phase5 network diagnostic and
quote-safe runner/current-IP deployment docs;user board config;existing C3
voice_unit and Wi-Fi diagnostic/checker/docs/context;ESP32C3/S3 editor setup;
enclosure OpenSCAD,9 STL exports,previews and validation;durable issue handoffs.
Root context records below preserve separate firmware/CAD histories. Root current
handoff supersedes older firmware notes claiming no receiver tests had yet run.
No credentials,private media,model/toolchain archives or ignored runtime logs.

Fresh commit checks:129 pytest tests pass (7.56s);bash syntax for Phase5 runner
passes;normal Git diff --check passes. C3 production sketch compiled999841bytes
program/37976globals;Wi-Fi diagnostic953875program/36152globals,exit0 for both,
no hardware upload. All9 existing STL meshes pass standard-library validation.
No credential scan matches;both ignored secrets.h and private WAV/JPEG confirmed
excluded. HEAD/origin main synchronized before commit. Source tests/compilation
are not physical hardware acceptance;no phase/gate declared complete.

Latest live run is STOPPED:app log ends^C,result exit0,no app process found via
USB;owned serial reader26616 absent. User said everything powered from laptop.
Current known IPs S3 10.153.76.67,UnoQ 10.153.76.45,C3 10.153.76.243;reverify DHCP
before future run. Full application runs on UnoQ;live URLhttp://10.153.76.45:8080/live.
Manual run has no timer;Ctrl+C stops it. Runtime-local launch scripts are ignored,
not part of reproducible firmware fix;README documents normal runtime command.

Confirmed blockers:repeated S3brownouts after servo motion (power topology and
under-load voltage need hardwareteam);C3 USB logging suspected to stall audio
when serial reader closed (open31.41packets/s vsclosed2.265s gap). See
HARDWARE_POWER_ISSUE.md and FIRMWARE_AUDIO_ISSUE.md. Original five-second C3
checker failed42.4% rate shortfall. All8 light states were sent but physical
colour/clear-WAV confirmation not received. Live direction/track/shoot accepted,
photosIMG_0001/0002 saved in actual logs;phone-new-photo/fullmotion smoothness
unconfirmed. Spoken camera stop tracking accepted at least once after initial
recognition complaints. Network14.45FPS is NOT CPU benchmark;UnoQ benchmark
still unrun. Full mock/hardware acceptance remains pending despite publication.

Next resume:read this handoff and issue docs;resolve S3power and nonblocking C3
logging through hardwareteam/SessionB;verify gates,then full real-component
tracking/photo/physicallights/phone-gallery and actualCPUbenchmark. Do not
restart automatically or implement later phases merely because commit pushed.
Update context before every future commit;preserve other sessions' work.

---

## Live annotated browser view deployed and verified - 2026-10-04

User requested visible live camera/tracking and reported no response to spoken
stop tracking. Correct exact phrase remains "camera stop tracking". Existing
logs had no accepted stop command; no voice threshold/gain change or speech fix
claimed. Existing state test covers transition to IDLE when command accepted.
User then requested restart with live visual; implemented requested view only.

Added /live browser page and /live/frame.jpg to existing Uno Q gallery8080.
Uses read-only callback from the existing control/display snapshot,without
opening another S3 stream or running detection on laptop. JPEG includes green
box,mode,pan/tilt,dx/dy,search/stopped/reconnect indication. Page polls one request
at a time every250ms,backs off when hidden,retries unavailable camera. Routes
return404 without provider,503 while no frame,no-store caching. Gallery root
links live view. No browser control/movement route added.
Files:app/main.py,app/gallery/server.py,templates/index.html,templates/live.html;
new tests/test_live_gallery.py. Full129 tests pass (7.49s),remote py_compile passed.

Prior manual-stop app/monitor had already ended (no Python receiver or owned
reader present); cause not established. Preserved prior app log, deployed only
runtime source/templates over verified USB ADB,then restarted no-time-limit app
and serial workaround. New monitor PID22888,COM18/C3+COM19/S3. Same stop marker
and Ctrl+C console cleanup;no app/monitor timeout. No firmware changes.
Actual remote Ready05:40:53.796,accepted track person05:40:57.713. Live page200,
JPEG200,image/jpeg,decoded320x240. Visually inspected actual frame:greenperson
box,TRACKING,pan43/tilt93,dx-0.04/dy-0.12. Opened user's browser to
http://10.153.76.45:8080/live. Also accessible on phone same network.
Image/private evidence ignored logs/vision-live-preview-{check.jpg,result.json}.

Next: user says camera stop tracking,pause;watch IDLE and box disappear. If no
recognition,response remains voice issue; don't claim it fixed from visual UI.
Original user physical full-test/phone-new-photo confirmation,CPU benchmark and
standalone USB-logging fix remain pending. App continues until user Ctrl+C in
Vision - RUNNING until Ctrl+C. ExistingHEADbf89885;no commit/push. Context updated
before ending and must be refreshed before every future commit. Preserve separate
firmware/CAD/editor work and shared records.

---

## Current update: C3 microphone selected - 2026-10-04

User explicitly requested INMP441 on ESP32-C3 Super Mini; do not use Bluetooth
headset or laptop microphone. This supersedes earlier boAt preference.
Laptop voice mock has exited with PortAudio channel error; it is not supplying
audio. Firmware handoff confirms production C3 10.153.76.243 sends 16kHz mono
s16le, 512 samples/1024 bytes to Uno Q 10.153.76.45:5005. No firmware edits.
Opening ignored logs/check-c3-mic-console.ps1: password entered only locally,
strict verified host key; uploads diagnostic shell, refuses concurrent app,
then existing tools.demo_voice --mic udp --levels --seconds 180 on Uno Q.
This check recognizes commands only; no camera requests, photos or light commands.
Receiver delivery, speech clarity and acceptance remain pending actual output.
Next: authenticate in C3 console; wait for Listening, say camera track person,
pause, then camera shoot. Review levels/events. Keep camera on laptop mock for
Phase5; do not switch to real S3 or declare firmware gates complete.

Remote source refresh/preflight subsequently succeeded (older failure notes
below are historical): all three models, CSRT/KCF,16 checksums passed.
User's 60s UnoQ-to-laptop read-only stream diagnostic passed:875frames,
60.569s,14.45 received FPS,max chunk gap1.011s,errors[],ok=true,SSH exit0.
PowerShell NativeCommandError on normal SSH connection-close text was cosmetic.
Received FPS is network delivery, not CPU inference benchmark.
Quote-safe deploy/run_phase5.sh and read-only check_mock_network.py added;
latest local full suite126 passed, bash syntax passed. Phase5 full flow,
phone gallery and UnoQ CPU benchmark still pending; no commit/push this update.
Laptop camera mock PID11448 remains active (no automatic expiry); stop owned
mock after acceptance or user stop. Firmware/CAD/editor work preserved.
Context must be refreshed before every commit. Current known HEAD bf89885;
no intended commit yet while acceptance pending.

---

## Updated network and Phase5 restart - 2026-10-04T10:04:50+05:30

User supplied updated board addresses: S3 camera10.153.76.67, UnoQ10.153.76.45,
C310.153.76.243. Laptop Wi-Fi currently10.153.76.189, gateway10.153.76.224.
These supersede old192.168.29.* addresses and example192.168.43.* board addresses.
UnoQ new TCP22 reachable, oldUnoQ192.168.29.199 timed out. Board IPs are user-supplied;
no real S3/C3 endpoint or hardware acceptance performed by Session A.

Updated root config.yaml with real user board addresses (ports unchanged). Phase5
must still use generated config.phase5.yaml: s3_ip and c3_ip BOTH10.153.76.189
(laptop mocks), unoq_ip10.153.76.45, photos relative. No real-board integration
started or firmware edits. Updated copy helper's default UnoQ and deploy runbook.
Both config checks pass;21 config/deployment tests pass. Latest HEADbf89885
contains Phase5 prep; later-current voice code includes64994af bounded-silence fix.

Previous bounded mocks/app expired; no old Python/SSH sessions found before restart.
Headset boAt MME ID is now5 (ID4 now AMD array); confirmed inventory and selected5.
New camera/headset mocks launched on currentLAN for30min. Camera/status verified
ready; voice mock announces audio->10.153.76.45:5005 and listens10.153.76.189:5006.
Interactive new-network source-copy/live console opened. User supplies SSH passwords
there. Reuses previous trusted UnoQ host key via temporary HostKeyAlias192.168.29.199,
StrictHostKeyChecking=yes; new-address handshake passes key check but BatchMode
cannot authenticate without password. No trust disabled or credentials stored.

Current package includes runtime source/new mock config/latest voice fix, excludes
firmware/CAD/private media/secrets. Only source archive is recopied; installed models
and photos remain. Remote check-only verifies16 model hashes, then starts app for10min.
This source update and new-network app readiness are pending user authentication;
do not claim remote refresh complete before log evidence. Ignored scripts/logs:
logs/phase5-new-network-{app,voice,camera}*, processes JSON. Source archive39712 bytes.
Next: user completes login/copy, app Ready, spoken track person/shoot, saved print,
phone gallery http://10.153.76.45:8080 and crop http://10.153.76.189:81/stream.
Then stop app and benchmark on UnoQ against new laptop stream; old benchmark URLs
must not be used. Phase5 live/benchmark acceptance remains pending. No commit/push.
Preserve separate CAD and Session B records/work; context updated before any commit.

---

Prior network addresses are historical; preserve separate CAD/firmware entries.

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

firmware/voice_unit/voice_unit.ino now implements the C3 I2S/UDP audio and timed
NeoPixel contract. firmware/tools/check_voice_unit.py is the standalone5s audio/
light checker; private WAVs default to ignored firmware/.build. Current C3
production build999581/37976 flashed, but no Wi-Fi IP yet (WPA3 auth expiry).
Compile/boot is not real voice integration acceptance. Secrets remain ignored.

## C3 connection setting - 2026-10-04
User authorized the targeted Wi-Fi diagnostic/restoration. Keep production C3
TX cap8.5dBm after start and before connect: WPA2 default-power diagnostic failed,
reduced-power queued diagnostic obtained DHCP10.153.76.243, and restored voice
firmware was reachable at that IP with matching C3 MAC. Root hardware cause is
not proven; do not generalize to all C3 boards/WPA3. DHCP addresses may change.
F3 audio/colour/receiver/voice acceptance still pending; no contract changes.

## Final IntelliSense repair and commit preparation - 2026-10-04
User confirms the C/C++1696 include error is gone after final editor changes and
explicitly requests context update, commit and push. Clearance is user-observed;
no agent GUI verification claimed. Initial mapping/response-file configuration
was insufficient. Final helper expands GCC response files and -iprefix /
-iwithprefixbefore into explicit SDK include paths/defines/architecture flags,
normalizes compiler entries to existing .exe files and writes the generated
compile database atomically. Profiles use explicit fallback paths; SDK paths
are portable LOCALAPPDATA placeholders rather than developer-specific values.
Resolved include paths remain identical after portability cleanup. Temporary
C_Cpp Debug logging removed; normal error reporting stays enabled.
Validation: refresher maps3 sketches; each original source exists, appears once
in its arguments, compiler exists, no @response args remain in editor database.
C3 and S3 IPAddress header syntax-only checks both pass with final explicit
fallback settings. Windows rejected direct long probe command lines; probes
were rerun via ignored response files and both returned exit0. JSON and git
diff --check pass. User-observed editor clearance completes this editor fix,
not pending F2/F3/Phase5 hardware or software integration acceptance.
Current existing HEAD c78803fb4a18e66b569a1ebbdf2a662225390e55, already origin/main,
contains prior firmware/live tracking/enclosure publication from another commit.
Only final .vscode fix/docs and this shared context maintenance are in the next
commit; no firmware source, app, enclosure, credentials, media or build outputs
changed by this commit preparation. Intended message:
fix editor: resolve firmware header include diagnostics
Exact next action: commit explicit reviewed editor/context paths, push origin
main, verify remote HEAD. Then resume pending C3 receiver/mic/light checks when
user is ready; no acceptance or future phase is inferred from editor success.


## Runtime robustness modules — 2026-10-04
app/runtime.py owns rotating JSON logging, camera recovery and audio watchdog;
main.py integrates these with the existing state machine/tracker. UDP source
exposes last valid packet time; LightClient masks normal states during reconnect.
deploy/photo-rig.service is prepared but inactive; tools/prototype_acceptance.md
is the deferred combined hardware checklist. C3 logging repair is compile-only.
Shared ports/payloads unchanged. Hardware acceptance and boot-order gate pending.


## Confirmed supply description correction - 2026-10-04
User reports power bank -> S3 USB -> S3 5V/GND -> both servos. The initial
PD-charger description was corrected. Servos share S3 ground and USB power path.
Current voltage stability/brownout recurrence is untested; cause unresolved.
No new hardware check or wiring change. Measure under camera/both-servo load
when testing resumes; do not infer a defective power bank from old reset logs.

## Wi-Fi transport follow-up - 2026-10-04

User explicitly authorized Session A network-only compilation/upload and Wi-Fi
connection diagnostics/fixes. Latest changes: C3 bounded transient UDP retries,
S3 TCP_NODELAY and stream timing. Both compiled/flashed with verified hashes.
C3 1000357/37976 bytes; S3 986425/56664. No pins/acquisition/PCM contract change.
Final concurrent sample: C3 27.83 packets/s with 0.867s max gap, no malformed or
kernel UDP errors; S3 2.91FPS, 1.166s max chunk gap, frame wait1ms versus network
send wait1009/1626ms. Delivery remains unstable; no F2/F3 or software acceptance.
Uno Q172.20.10.2, C3.4, S3.5; laptop on Jasil using USB localhost:8080/live.
Runtime stopped, all bounded diagnostics ended; no automatic restart or commit.
Next controlled access-point comparison requires verified new network settings;
do not assume changing hotspot alone fixes board RF/power/transport behavior.
Root HANDOFF/TESTING records contain exact evidence and outstanding acceptance.

## TinkerSpace router migration pending - 2026-10-04

User selected TinkerSpace; Uno Q verified192.168.1.99 and S3192.168.1.122,
WPA2 2.4GHz. Both ignored credentials updated, C3 audio destination192.168.1.99.
C3 still fails association; its DHCP address unknown. C3 default TX power and
manual45s reconnect comparison compiled1000105/37976/flashed verified; S3
986425/56664/flashed verified. No physical/PCM/capture contract change.
S3 HTTP probes failed with0frames; no concurrent audio probe/full run possible.
Runtime stopped; root/runtime config still old hotspot values, DO NOT launch.
Root HANDOFF/TESTING has exact diagnostics and next steps for Session B/router
association investigation, verified config completion and metadata retest.
No commit/push or gate completion; all bounded diagnostics/readers ended.

## Router isolation performed; no successful fix yet - 2026-10-04

User requested find/fix. Read FIRMWARE_NETWORK_ISSUE.md for exact tests/results.
C3 fails in Wi-Fi-only sketches without microphone/NeoPixel software activity;
sees router-62/-64dBm but cannot authenticate, even targeted BSSID/channel and
lower transmit power. Its temporary access point reports started but is absent
from fresh Uno Q scans. This narrows investigation to radio/driver/calibration,
RF/power or AP behavior; no board defect or root cause conclusively established.
S3 b/g and Uno Q powersaveOFF comparisons failed; both experiments reverted.
User says hotspots off and alternate power/cable ready; post-report probes still
fail. Do not claim independently verified physical supply changes.
Temporary C3 diagnostics restored to production1000105/37976; S3 production
986425/56664 restored. Uploads0/hashesverified. Uno Q router profile restored,
actualpowersaveON/default0, temporary NM profile/helper removed. All bounded
readers/probes ended. Vision STOPPED; old runtime config must not launch on
router until unknown C3 DHCP address is verified and all configs updated.
User spare-C3 availability question pending. Next: identified spare-board radio
comparison if available, otherwise Session B driver/PHY and hardware/RF/AP logs.
No erase/NVS reset, guessed pins, future-phase work, commit or push. Existing
HEADd64f754f219d4b983a32bd87f740309fc2920e41. Prior136 software tests unchanged;
full stability/commands/gallery/benchmark and F2/F3 acceptance still pending.
Update context before every commit and when ending; preserve Session B ownership.
