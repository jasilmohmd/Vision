# Verification and runnable commands

## Verified push and next steps - 2026-10-04T02:53:49+05:30

git log/rev-parse and git ls-remote origin refs/heads/main confirm pushed software
commit5194c5ed39c02b2bcc91bfaef899492f5788838c. No implementation changes since
98 passing tests and headless real-model mock smoke; no unnecessary test rerun.
Team live acceptance remains pending. Gate0 network/SSH/actual IP checks are not
verified in this software session. Firmware latest status read only; its F0 DONE
remains pending and physical results are not inferred from board wiring docs.
No hardware test or deployment executed.

---

Previous entries are historical snapshots.

## Team handoff evidence - 2026-10-04T02:07:20+05:30

Latest automated result:98 passed. Real-model headless HTTP/UDP app smoke exit0.
No software/dependency changes since those checks; only docs/context refreshed.
Latest diff whitespace check to run before handoff. Live demo logs are not a pass:
heard/error light flashes, no verified track/shoot/gallery sequence, camera stream
unavailable after bounded mock timeout. User clarifies physical hardware checks
are for team; no local NeoPixel required to observe mock's printed states.
Team should run context/TEAM_TESTING.md, return spoken tracking/shoot/gallery and
printed saved results. Physical INMP441/C3/NeoPixel/servo checks remain separately
pending per appropriate firmware/software hardware gates. Do not claim any real
hardware result from laptop mocks. No raw media or secrets in tracked handoff.

---

Prior entries below are historical; this update controls the current handoff.

## Live Phase 3 demo launched - 2026-10-04 01:40 +05:30

The actual webcam mock is serving :80/:81. boAt headset device4 sends UDP audio,
and the app runs --mock --preview with actual models. Gallery8080 returned HTTP200;
initial indexed photo count0. Visible headset/light console and OpenCV preview
are open. Each process has a10-minute bound; Q exits app, Ctrl+C exits mocks.
Ignored logs/phase3-live-processes.json records spawned PIDs; voice/app/camera
logs are in logs/phase3-live-*.log. No raw audio recording.
First app launch preceded webcam readiness and exited; restarted successfully
once camera /status worked. README now requires waiting for Mock camera ready.
User acceptance question pending: camera track person -> visible crop follows ->
camera shoot -> photo appears in gallery -> saved white-flash message. No passing
human observation claimed yet. Next action: review response and live logs; fix
failures if any, then refresh all context before committing. Do not advance gates.

## Latest software verification - 2026-10-04T01:38:42+05:30

- python -m pytest -q: 98 passed in6.42s (70 regression +28 Phase3).
- pip check: no broken requirements. Flask3.1.3 installed, already in requirements.
- git diff --check: passed; rerun before commit.
- app.main/tools.mock_camera/tools.mock_voice_unit --help: all passed.
- Synthetic HTTP camera + UDP silence mock + actual ONNX/YuNet/Vosk app
  --mock --seconds5: exit0. Ignored logs/phase3-smoke-app.log and mock-0/1.log.
- Tests cover controller math/rate/limits, storage restart/gaps/corruption/failed
  index writes, state missing-subject/sleep/cancel/timer/burst, save-before-ACK,
  ACK recovery, real HTTP/MJPEG/UDP, gallery newest-first/full image, and integrated
  parsed command -> crop move -> capture -> photo/gallery -> saved UDP light.
- Parsed command injection is automated integration, NOT spoken live acceptance.
- Remaining: user says camera track person, moves, camera shoot; verify crop
  follows, gallery8080 holds full photo, voice mock prints saved white flash.
- Headset boAt device4 available now; default Elgato virtual input. IDs can change.
  No original built-in mic/distance or INMP441 validation claimed. No raw audio or
  private media in context/Git; runtime photos/models/logs ignored.

---

Earlier entries below are historical snapshots; this current software update
takes precedence. Session B records are preserved.

## Firmware Session B verification - 2026-10-04

- Arduino CLI 1.5.1 official archive SHA256 matched its release checksum.
- Existing ESP32 core 3.3.11 and board option metadata inspected locally.
- Local ESP32Servo 3.2.1 / Adafruit NeoPixel 1.15.5 installed and listed.
- ./firmware/tools/verify_toolchain.ps1 runs pin-free compilation only.
  Generic S3 PSRAM=opi passed: 266499 bytes flash, 22388 bytes RAM.
  Generic C3 CDCOnBoot=cdc passed: 295710 bytes flash, 14476 bytes RAM.
  Verification script completed with exit 0.
- ESP32Servo emits upstream unused-variable and S3 legacy MCPWM warnings.
- Hardware-specific profile/PSRAM/pins, uploads and all real-part tests unrun.
  Generic compilation does not verify the actual camera board or PSRAM hardware.
- Initial --user-dir install attempt failed (unsupported CLI flag); corrected
  with ARDUINO_DIRECTORIES_USER. Normal shell helper failed; escalated runner works.
- Software tests not rerun; software evidence below is separately attributed.
- git diff --check passed; git check-ignore confirmed both secrets.h paths,
  portable CLI, build output and check.wav are excluded. Git status reviewed;
  pre-existing software changes remain uncommitted and were not staged.

Updated: 2026-10-04T01:17:16+05:30 (Asia/Calcutta).

## Phase 1 executed checks (2026-10-04)

- pytest: 23 passed (15 Phase 0/config tests, 8 vision tests).
- CLI help: app.main, tools.demo_vision, tools.export_onnx, tools.download_models passed.
- YOLO export: static input (1,3,320,320), output (1,84,2100), opset 17; succeeded.
- Real inference on official Ultralytics bus sample: 3 people, YuNet 2 faces.
- Headless webcam: 10 person frames and 3 face frames, boxes/offsets printed.
- pip check: no broken requirements.
- git diff --check: passed after Phase 1 changes.

Automated tests cover config defaults/overrides and invalid values; RGB
letterboxing, inverse coords, class filter/NMS, clipping, offset direction and
bounds; detection interval, nearest-box identity, failure/reacquisition,
real CSRT/KCF on a textured frame, fallback and missing-model setup errors.
They do not prove tracking smoothness while a person moves.

## Benchmark (2026-10-04)

Laptop CPU, webcam source 0, person target, CSRT, 320x240, detection interval 5.
100 cached frames; acquisition/model load excluded; detector warmed up:

- Detector-only 68.39 FPS; detector+tracker 19.13 FPS.
- Detected 100/100; tracked 100/100.
- Local JSON: ../models/benchmark-webcam.json (ignored).
- Earlier 30-frame run: 66.52/38.04 FPS, detected 4/30, tracked 7/30; do not
  use its higher tracking FPS as the normal present-subject benchmark.

## Phase 1 context verification

- Context file inventory, relative Markdown links and git diff --check verified.
- No application tests rerun for this documentation-only change. Last 23-test
  result above remains the latest application evidence.

## Resume commands (PowerShell from repo root)

```powershell
git status --short
git log -3 --oneline
.\.venv\Scripts\python.exe -m app.main --help
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m tools.demo_vision --target person
.\.venv\Scripts\python.exe -m tools.bench_vision --frames 100 --output models/benchmark-webcam.json
```

For another camera use --source 1; for a recording use --source path/to/video.mp4.
Demo --target face|dog|cat selects the subject; --tracker KCF changes tracker.
Use --headless --frames 100 for finite console-only output. Q/Escape closes GUI.

## Fresh clone setup

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install pyyaml pytest "opencv-contrib-python>=4.10,<5" onnxruntime numpy
.\.venv\Scripts\python.exe -m tools.download_models
python -m venv .venv-export
.\.venv-export\Scripts\python.exe -m pip install -r requirements-export.txt
.\.venv-export\Scripts\python.exe -m tools.export_onnx
```

The full laptop requirements include later-phase runtime libraries; the command
above installs what Phase 1 currently needs. Do not install requirements-export
into Uno Q or combine base/contrib OpenCV distributions in the runtime venv.
Future Uno Q installation is Phase 5; do not perform it during laptop phases.

## Phase 1 visual acceptance - passed (2026-10-04)

Visible person preview launched at user request, with up to 1800 frames.
Tracked boxes and changing offsets appeared in numerical logs, with no errors
at inspection. After moving left/right and closer/farther in the preview, user
reported: "Yes?tracking is smooth and offsets change". Human acceptance passed.
Numeric logs remain in ignored logs/; no camera images were saved for this check.

No application code changed since the 23-test pass. Documentation/context
updates were checked with git diff --check before the Phase 1 commit.
No remaining Phase 1 acceptance checks. Phase 1 commit: 891274f.
Phase 2 was subsequently started; see its current verification below.

## Phase 2 verification (2026-10-04)

- Full pytest: 70 passed (15 config + 8 vision + 47 voice).
- Voice tests: all 19 phrases, exact wake word/whole phrase rejection, typed
  parsing; heard dedup/reset; threshold boundary, missing/mismatched word
  evidence, low/NaN/out-of-range confidence; flush/worker; mic format/cleanup;
  real UDP loopback validation, bounded buffer/drop, underrun silence,
  recovery, initial timeout and close waking a waiting reader.
- Vosk 0.3.45 and sounddevice 0.5.6 installed; pip check clean.
- Real Vosk small EN model loaded and every grammar word is present, including
  centre. 3.2 seconds synthetic silence produced no events.
- AMD device 3: 32 real microphone chunks, 1024 bytes each at 16 kHz mono,
  zero overflows. Audio kept only in memory; no recording saved.
- Finite laptop demo (2 seconds) and UDP idle demo (1 second) succeeded.
- demo_voice --help and --list-commands succeeded.
- These smoke checks do not prove recognition of live commands/background speech.

### Outstanding live acceptance

```powershell
.\.venv\Scripts\python.exe -m tools.demo_voice --device 3 --checklist --report logs/phase2-voice-check.json
```

Stand 0.5-1 m away, speak each of 19 phrases with pauses, then talk normally
without command phrases during the 20-second chatter segment. No background
command events. Check report and obtain user confirmation of distance and chatter.
Do not mark Phase 2 complete or commit before this acceptance passes.
For a different device ID, run demo_voice --list-devices first.

### Phase 2 final checks and user status

- Full regression rerun after guided demo changes: 70 passed.
- Finite guided-checklist smoke (0.1 seconds) correctly reported checks_passed
  false with all 19 commands missing; summary JSON verified programmatically.
- git diff --check and relative Markdown links passed.
- User explicitly reported not running the real guided acceptance check yet.
  That smoke summary is not live acceptance and must never be used as a pass.

## Updated-plan review verification (2026-10-04)

- Reviewed software diff against HEAD 891274f and the complete firmware plan.
- Programmatically compared software section 2 with HEAD: contract unchanged.
- HARDWARE_PLAN.md absent; firmware/ contains only the initial two sketch placeholders
  at inspection. No firmware completion/status/gate evidence was supplied.
- Documentation/relative links and diff whitespace checked; firmware file hashes
  unchanged across this documentation update.
- No application tests rerun for this documentation-only review. Latest actual
  application result remains 70 passed; live Phase 2 acceptance still pending.
- No hardware/toolchain/flashing checks executed in this session.

## Live microphone check launched (2026-10-04)

User authorized the check. Opened a visible console running demo_voice with
AMD mic device 3, --checklist --seconds 600 and summary-only report at
logs/phase2-live-voice-check.json. Await all 19 commands, 20-second real chatter
with zero command events, and user confirmation of 0.5-1 m distance. No raw
audio saved. No Phase 2 commit or Phase 3 work until acceptance passes.

## Live voice check retry (2026-10-04)

User reported the first console did not run properly and requested a restart;
no specific error/phrase supplied yet. Closed only the identified first voice
workers/console to release the mic. Launched a new visible console titled
Vision - Phase 2 live voice check (console PID 24896 at launch), with clear
instructions and unbuffered output. Verified voice worker is running; Vosk
startup diagnostics show model/grammar loading, no failure at inspection.
Current result: logs/phase2-live-voice-retry.json. Startup diagnostics:
logs/phase2-voice-retry-startup.log. Launcher: logs/launch-voice-check.ps1.
All are ignored local test artifacts. This retry supersedes the previous
live-check console; wait for its report plus distance/chatter confirmation.
No acceptance pass, phase commit or Phase 3 work has been recorded.

## Microphone selection diagnosis (2026-10-04)

User reported no recognition and said headphones were in use. Verified the
running checklist used device 3 (AMD laptop array), not the headphones. Newly
available headset: boAt Rockerz 255 Pro+, device 4 (MME); 16 kHz mono int16
format check passed. Vosk model/grammar startup showed no error. Stopped only
the owned laptop-mic workers/console and switched the diagnostic to device 4.
The earlier timeout/incomplete runs have not passed acceptance.

Added demo --levels (normalised RMS/peak once per second) and explicit input
device display. Full regression after change: 70 passed. No threshold change.
Headset diagnostic console PID 25368 at launch, --device 4 --levels --checklist,
600-second limit. Summary logs/phase2-headset-diagnostic.json; startup diagnostics
logs/phase2-headset-startup.log. Both ignored; no raw audio saved. Await user
report of input levels and heard/command events. This supersedes previous active
laptop check consoles; verify process IDs before any cleanup.

Headset diagnosis does not satisfy the specified laptop microphone check from
0.5-1 m. After fixing input/recognition, return to verified laptop-mic acceptance
or obtain an explicit user-approved acceptance change. No Phase 2 commit or
Phase 3 advancement; no firmware edits.

## Headset live check result (2026-10-04)

User reported all checks passed. Verified logs/phase2-headset-diagnostic.json:
19/19 supported commands, zero missing commands, 20.09 seconds background test,
zero background command events, confidence threshold 0.7, device 4 boAt headset,
checks_passed true. No raw audio recorded. Latest full regression remains 70 passed.

The headset result is passing evidence for that setup. Original built-in laptop
microphone at 0.5-1 m remains unverified. Asked the user to choose accepting the
headset setup as Phase 2 acceptance or running the original mic/distance check.
Await that answer before phase completion/commit. No Phase 3 work. Firmware B
has its own new files; none edited or staged in this task. Earlier active-run
entries above are historical and superseded by this completed headset result.

## Accepted Phase 2 result / limitations (2026-10-04)

User accepted the temporary headset test workflow after clarification of the
final INMP441/C3/UDP integration and asked for commit commands. Headset checks:
19/19 phrases; 20.09 seconds background; 0 command events; threshold 0.7.
Latest regression: 70 passed after input display/levels change. No application
code changed afterward, so tests were not repeated for this context-only update.

Built-in laptop mic at 0.5-1 m was not verified. Record this accepted temporary
setup deviation explicitly. Final MEMS audio clarity, real-mic command recognition,
confidence tuning and light states still need firmware F3/software Phase 7 checks.
No claim of final hardware acceptance. git diff --check passed before handing
the software commit commands to the user. No firmware code or tests changed.

## Firmware Session B push verification - 2026-10-04

User reported committing and pushing firmware preparation for a different
team to test. Verified HEAD, origin/main and live git ls-remote main all equal
993e3d5f51fb7ea9d6a8a9212a5e485a3c93151e.
Message: fw phase 0: prepare toolchain and scaffold for team testing.
F0 board facts and F0 DONE remain pending; no flashing or F1 work authorized.
User previously explicitly allowed shared context updates for B. Preserve
Session A's separately updated software records above. Firmware is now tracked,
not untracked; earlier Session A ownership descriptions remain historical.
Next firmware action: await testing team's exact S3 model, free pan/tilt pins,
confirmed network plan and flashing ports, with F0 DONE. HARDWARE_PLAN.md absent.
These post-push handoff updates remain local/uncommitted; no additional commit
or push performed by the agent. Existing software changes remain untouched.

## Network report - 2026-10-04

User supplied Arduino interface addresses:
172.20.0.1, 172.17.0.1, 172.18.0.1, 172.19.0.1, 192.168.29.199,
2405:201:f025:d03c:f99c:335:258b:cfa0.
Recorded as candidate Uno Q addresses, not a confirmed shared-network UNOQ_IP.
Interface names, shared hotspot subnet/gateway and S3/C3 reachability are unknown.
Do not select an address from this list or change secrets/config until confirmed.
User says other checks are ongoing and will confirm once done. F0 DONE has not
been received. F0 board facts remain pending; no F1 work or flashing performed.
Next action: await board facts and confirmation of the Uno Q IPv4 address that
S3/C3 can reach on their shared network, plus the remaining F0 checks/F0 DONE.
Existing verified HEAD/remote: 993e3d5f51fb7ea9d6a8a9212a5e485a3c93151e.
This network/handoff update is local and uncommitted; no new commit/push.

## Board facts update - 2026-10-04

User identifies the camera board as ESP32 S3 CAM DEVKIT N16R8 DUAL PORT WITH
2MP CAMERA and reports servos connected to GPIO 1/2. Preserve planned mapping
pan=GPIO 1, tilt=GPIO 2; wiring report is not a completed servo/power test.
Exact-name seller listing found: Tomson Electronics SKU SEN-29083, 16MB flash,
8MB PSRAM, UART+OTG USB, RHYX M21-45 2MP camera:
https://www.tomsonelectronics.com/products/esp32-s3-cam-devkit-n16r8-dual-port-with-2mp-camera
No board-specific camera GPIO map established from that listing. Do not assume
ESP32S3_EYE or another core camera profile merely from the N16R8 module label.
Obtain seller schematic/pin map or matching board documentation before F2.
Network clarification: user notes live S3/C3 reachability can only be checked
once Wi-Fi firmware is flashed. Defer live connectivity verification to F2/F3;
static network values can be configured beforehand once the subnet is known.
Other F0 checks are ongoing per user. F0 DONE not received; F1 not started.
Next action: await remaining F0 toolchain/board facts and F0 DONE; obtain actual
camera pin map before camera implementation. No flash, commit or push here.

## Confirmed wiring and sensor - 2026-10-04

User explicitly confirms pan=GPIO 1, tilt=GPIO 2, and camera sensor=OV3660
on the ESP32 S3 CAM DEVKIT N16R8 dual-port board. OV3660 supersedes the earlier
2MP/RHYX seller description for this user's installed sensor. Sensor model
confirmation does not establish camera bus/control GPIO wiring; actual board
camera pin map remains pending before F2. Do not assume a core camera profile.
F0 DONE not received; other F0 checks remain pending. No F1 implementation,
flashing, new compile check, commit or push in this update.
Next action: await remaining F0 confirmation and F0 DONE, then implement F1.
Live S3/C3 network verification remains deferred until Wi-Fi firmware flashing.

## Camera pinout evidence - 2026-10-04

User supplied an ESP32-S3-CAM N16R8 pinout diagram. Read directly from it:
SIOD=4, SIOC=5, XCLK=15, VSYNC=6, HREF=7, PCLK=13;
D0/Y2=11, D1/Y3=9, D2/Y4=8, D3/Y5=10, D4/Y6=12, D5/Y7=18,
D6/Y8=17, D7/Y9=16. All 14 labelled camera signals exactly match the installed
Arduino ESP32 core 3.3.11 CameraWebServer CAMERA_MODEL_ESP32S3_EYE entry.
This is pin-map correspondence, not identification as a physical S3-EYE board.
Diagram does not label camera PWDN/RESET. Core entry uses -1/-1; those two
connections remain unverified and must not be represented as image-confirmed.
GPIO 1 and 2 have no camera assignment in this diagram; retain user-confirmed
pan=1 and tilt=2. Camera sensor remains user-confirmed OV3660.
No camera implementation, physical test or flashing performed. F0 DONE still
pending. Next action: await remaining F0 confirmation/resume phrase, then F1.
At F2 use this documented map, resolve PWDN/RESET via board documentation or
team confirmation, and verify camera initialization on hardware. No commit/push.

## Firmware documentation commit preparation - 2026-10-04

User requested commands to commit/push the documented board facts for team
review. Existing HEAD: 73077515675bfa622279da0254a7ae7ca674f8ad.
Intended message: fw docs: record board wiring and camera pinout for team review.
This is a documentation handoff, not new executable firmware or F0 completion.
F0 DONE and remaining checks pending; F1 sketches not implemented. Camera
PWDN/RESET still unverified. Live connectivity deferred to Wi-Fi flashing.
Git diff --check passed. No new compile/hardware tests run for these records.
Shared context currently contains app team's concurrent Phase 3 records:
selectively stage only Session B updates there and preserve app implementation.
Next action: user reviews/stages firmware documentation and corresponding shared
context updates, commits/pushes; then await remaining F0 checks and F0 DONE.
No staging, commit or push performed by this agent for this preparation.

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
