# Verification and runnable commands

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
