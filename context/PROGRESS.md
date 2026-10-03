# Progress ledger

## Verified push and next steps - 2026-10-04T02:53:49+05:30

User pushed Phase3 team-testing implementation commit5194c5e. Verified exact
local/live-origin hash5194c5ed39c02b2bcc91bfaef899492f5788838c. Software is shared
with team; this does not complete live acceptance. Await team results, then
close Phase3 if successful. Phase4 belongs to B; Gate0 precedes Phase5.
No software/code changes, new test runs, staging, commits or pushes in this turn.
Only post-push context refreshed; firmware work preserved.

---

Previous entries are historical snapshots.

## Team-testing handoff - 2026-10-04T02:07:20+05:30

Phase3 software implementation ready to share;98 automated tests pass. User
requests pushing for hardware team checks and clarifies there is no local LED.
Record mock printed-light acceptance separately from physical NeoPixel testing.
Live spoken end-to-end acceptance still unconfirmed; Phase3 not complete.
User-authorized testing commit may precede live acceptance. Intended message:
phase 3: add control core, mocks, and gallery for team testing. Existing HEAD:7307751; no new commit/push performed here.
Added TEAM_TESTING.md with setup, exact laptop mock flow, report checklist and
hardware ownership/gates. Physical testing exclusively hardware team/Session B.
No firmware changes, no later phases implemented.

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

## Software Phase 3 - 2026-10-04T01:38:42+05:30

Implemented camera HTTP client (2s timeout,2 retries), UDP lights/steady-state
memory, optional TTS, 10Hz proportional controller with dead zone/inversion/angle
limits, IDLE/TRACKING/SHOOTING/TIMER/SLEEP state machine, asynchronous cancellable
photo jobs, centering timeout, burst3/timer3, missing-subject light after2s,
save-before-ACK and pending-ACK recovery, numbered JPEGs/atomic metadata index,
Flask gallery8080 newest-first, MJPEG latest-frame/reconnect worker, threaded app,
webcam crop mock (control80,stream81) and mic/light UDP mock (5005/5006).
98 tests pass and actual-model headless app smoke passed. Live voice/visible crop
follow/shoot/gallery/light acceptance PENDING. No Phase 3 completion or commit yet.
Phase 2 actual commit7307751. Firmware untouched; Phase4 skipped, Gate0 later.

---

Earlier entries below are historical snapshots; this current software update
takes precedence. Session B records are preserved.

## Firmware Session B - 2026-10-04

User requested FIRMWARE_PLAN.md work and approved shared context updates.
F0: portable Arduino CLI 1.5.1 checksum verified, existing ESP32 core 3.3.11
reused, ESP32Servo 3.2.1 and Adafruit NeoPixel 1.15.5 installed locally.
Firmware scaffold, ignore rules, placeholder secrets and compile-only probe
created. Generic S3 and C3 compilation passed with upstream library warnings.
Exact camera board/profile, pins, IPs/ports and F0 DONE remain pending.
F0 is not complete; no F1 work, upload, commit or push. Software progress below
is preserved. No app tests rerun for firmware scaffolding.

Updated: 2026-10-04T01:17:16+05:30 (Asia/Calcutta).

| Phase | State | Remaining acceptance |
| --- | --- | --- |
| 0 Scaffold/config/contract | Complete; de1dfad | None |
| 1 Laptop vision | Complete; 891274f | None |
| 2 Laptop voice | Complete for accepted temporary headset setup; ready to commit | Final INMP441 check belongs to later integration |
| 3 Control/mocks/gallery | Not started | All planned checks |
| 4 Firmware | Skipped by Session A; owned by Session B | Independent F0-F5 checks; no firmware evidence yet |
| 5 Uno Q with mocks | Not started | Gate 0 first; all checks |
| 6 Real camera | Not started | Gate A first; all checks |
| 7 Real voice | Not started | Gate B first; all checks |
| 8 Robustness/autostart | Not started | Gate C first; all checks |
| 9 Demo/final checks | Not started | All checks; final rehearsal gate |

## Hardware stops

No gates reached or acknowledged. After Phase 3 acceptance, skip software
Phase 4 and reach Gate 0 / GATE 0 DONE.
After Phase 5: Gate A / GATE A DONE. After Phase 6: Gate B / GATE B DONE.
After Phase 7: Gate C / GATE C DONE. After Phase 9: final rehearsal.
Print the exact checklist from SOFTWARE_PLAN.md when reaching a gate; never
paraphrase it from this index or work ahead past it.

## Work history

### 2026-10-03 - Phase 0

Created repository scaffold, config, requirements, CLI and 15 tests. Initial
sandbox/network errors blocked dependency installation; user installed PyYAML
and pytest. Approved escalated execution later allowed verification and commit.
CLI and tests passed. Commit de1dfad. User configured GitHub origin afterward.

### 2026-10-04 - Phase 1 implementation

Implemented detector, face wrapper, tracking, export/download tools, demo,
benchmark, tests and environment documentation. Downloaded/exported models.
23 tests passed. Headless webcam checks ran for person and face. The longer
100-frame webcam benchmark tracked a person in all frames. At that time, human smoothness
acceptance was pending; user said the demo was not run yet.
There was no Phase 1 commit or Phase 2 implementation at that point.

### 2026-10-04 - Durable context rule

User requested a context folder covering the project and a mandatory update
before every commit. Added README/index, HANDOFF, PROJECT, DECISIONS, PROGRESS
and TESTING documents; updated root AGENTS/README/STATUS. Documentation checks
are recorded in TESTING. At that point this work was uncommitted alongside Phase 1, with the phase
acceptance boundary in force. See the completion entry below for the final state.

## Phase 1 completion and commit

On 2026-10-04, after viewing the webcam preview and moving, user confirmed:
"Yes?tracking is smooth and offsets change". This passes the remaining visual
acceptance check. Previously recorded automated checks and benchmark passed.
Context and STATUS were updated before preparing the required Phase 1 commit:
`phase 1: laptop vision and tracking`. Resolve the real hash from git log after
creation. Phase 2 has not started. No remote push is included.

## 2026-10-04 - Phase 2 implementation

User started Phase 2 after Phase 1 commit 891274f. Implemented exact command
parser, laptop/UDP PCM audio sources, confidence-gated Vosk event recognizer,
voice demo and guided acceptance checklist. Installed Vosk/sounddevice locally.
70 tests passed; real model contains every grammar word; silence emitted no
events; laptop mic produced correctly sized PCM without overflows. Finite UDP
and laptop demos ran successfully. No raw audio saved. Live 19-command recognition
from 0.5-1 m plus background-chatter acceptance remains pending. No Phase 2 commit;
Phase 3 not started. Context updated while waiting for that evidence.

User subsequently confirmed the live checklist has not been run yet.
All 70 tests pass; incomplete-checklist reporting verified. No phase commit.

## 2026-10-04 - Updated plans / separate firmware session

Reviewed updated SOFTWARE_PLAN.md and FIRMWARE_PLAN.md at user request.
Section 2 contract unchanged. Session A no longer owns firmware Phase 4 or
flashing/check-tool implementation. Session B owns all firmware/ and independent
F0-F5 work. Revised Gates A/B depend on B's F2/F3 completion and actual IPs;
Gate 0 is network/Uno Q readiness. Recorded review findings in PLAN_REVIEW.md.
No implementation or firmware changes in this review. Phase 2 live acceptance
still pending; no Phase 3, commit or push. HARDWARE_PLAN.md absent.

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

## Phase 2 completion / user commit handoff (2026-10-04)

Following the passing headset report, explained the final INMP441/C3 UDP path
and later real-hardware acceptance. User accepted that workflow and requested
commit commands. Temporary headset recognition is accepted for Phase 2; the
unverified built-in mic/distance check is an acknowledged deviation, not a pass.
Context updated before handing over commands. Intended message:
phase 2: laptop voice and recognition. Existing HEAD 993e3d5 (B's firmware
preparation commit). No software commit/push by this session; Phase 3 not started.

Firmware preparation is now committed by B as 993e3d5. Earlier firmware entries
above are pre-commit snapshots; F0 board facts and F0 DONE still remain pending
per firmware/STATUS.md. User explicitly allowed shared context maintenance for B.

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
