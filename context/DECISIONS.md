# Decisions and constraints

## Enclosure prototype choices - 2026-10-04

User explicitly requested OpenSCAD code and supplied external enclosure prompts
as reference material. Deliver one self-contained .scad with a selector for all
parts, without implementing software/firmware phases. Typical dimensions remain
assumptions. Mechanical corrections include a deeper camera rear bay, larger
horn mounts/yoke, clearance for servo head projection, a taller/wider pan bearing
ring and an offset vertical clamp. Lens hood is optional/off for flat printing;
labels are engraved. Pod is enlarged. README discloses these deviations, support
requirements, longer screws and unverified hardware fit. Network/pin/protocol
contracts and all existing phase gates are unchanged. No commit authorized here.

---

## Phase 5 choices - 2026-10-04T04:37:24+05:30

User done/next-phase instruction authorizes progression from accepted Phase3 and
revised Gate0; S3/C3 addresses deferred until later real-board gates. Use user
UnoQ192.168.29.199 and verified laptop192.168.29.58; SSH username arduino provided.
No guessed board IP/pins. Separate generated config.phase5.yaml points both mock
clients at laptop; normal config.yaml/examples preserved. App on UnoQ omits --mock
because localhost means UnoQ. Camera bind stays127.0.0.1 by default, explicit LAN
--bind for Phase5; voice destination/bind flags were already supported.
Runtime/models copied explicitly with manifest verification, not whole workspace.
No PyTorch/Ultralytics or multiple cv2 packages in the UnoQ venv. Laptop export
packages allowed locally. Binary OpenCV/ORT/NumPy installs avoid compiling heavy
runtime packages on board. KCF remains opt-in only after measured CSRT benchmark.
Keep host-key verification; passwords entered only into user SSH/sudo terminal.
No auto-login/key setup/service enablement/firmware implementation in Phase5.

---

Earlier records are historical; this software update takes precedence.

## User network/gate clarification - 2026-10-04T03:57:11+05:30

User confirms hotspot setup and UnoQ hotspot/SSH reachability are done, and
says the UnoQ IP was already supplied. Previously supplied external LAN IPv4:
192.168.29.199 (alongside internal bridge/IPv6 addresses). Retain it for upcoming
SSH verification; do not ask user to repeat the address or claim an agent SSH test.
User explicitly defers S3/C3 static IPs until the firmware plan is finished.
That deferral overrides Gate0 item4 for laptop-mock deployment: Phase5 only needs
UnoQ and laptop mock connectivity. Require real board IPs before their respective
integration gates; no guessed firmware IP/pin changes. No config changes here.
Phase3 live acceptance is still awaiting team results. No Phase5 implementation
or deployment started in this clarification turn. No formal GATE 0 DONE received;
do not demand S3/C3 addresses now. Next software work after Phase3 acceptance is
Phase5 UnoQ deployment against laptop mocks while firmware proceeds separately.

---

Earlier gate descriptions are superseded by this user clarification.

## User-authorized team handoff - 2026-10-04T02:07:20+05:30

User states laptop has no NeoPixel and physical hardware testing belongs to team.
Do not ask for a physical laptop LED check. Phase3 mock checks printed UDP states.
User wants remote software handoff for testing now; preserve live acceptance as
pending and allow testing commit before that check. This is an explicit exception
to holding the commit until live acceptance, not permission to mark complete or
advance hardware gates. Session A supplies software; Session B owns firmware.

---

Prior entries below are historical; this update controls the current handoff.

## Phase 3 decisions - 2026-10-04T01:38:42+05:30

Use UDP audio by default to exercise the final hardware interface. --mic laptop
is diagnostic. --mock changes hosts only; shared ports/PCM/HTTP remain unchanged.
Photo jobs run separately while centering so tracking/audio continue; moves pause
for capture. Burst centers once then captures3 with400ms spacing. Timer gives3
one-second-spaced blue flashes before shooting. Save succeeds before ACK; failed
ACK is retried before another capture to avoid duplicating held images.
Single app writer per photo directory, preserve orphan/restart numbering and refuse
corrupt metadata. speaker_enabled defaults false; eSpeak NG/eSpeak optional,
missing/disabled synthesis no-op. No firmware/pin/IP decisions made here.

---

Earlier entries below are historical snapshots; this current software update
takes precedence. Session B records are preserved.

## Firmware Session B authorization - 2026-10-04

User requested starting FIRMWARE_PLAN.md, selecting Session B for this task.
User explicitly answered "Allow shared context updates" to resolve firmware-only
ownership versus root before-commit maintenance. Session B may append root
context/ and STATUS.md while preserving software records. Software implementation
remains owned by A; stage only explicit B paths and its context changes.
Compile probes use generic chip profiles; actual S3 model/PSRAM/pins await F0.
Credentials are entered locally into ignored secrets.h; never put passwords in
chat/context. Confirm actual network addresses before using them.

Updated: 2026-10-04T01:17:16+05:30 (Asia/Calcutta).

## Mandatory user rules

- Work within the requested phase. No future-phase implementation ahead of time.
- Follow every hardware hard stop and wait for its exact resume phrase.
- Update context/ BEFORE EVERY commit, including documentation-only commits.
  This rule was explicitly requested on 2026-10-04 and is recorded in AGENTS.md.
- Keep durable handoff records current when ending a session without a commit.

## Implementation decisions

1. Phase 0: immutable typed dataclass for config; reject unknown keys, invalid
   types/ranges; resolve relative photos_dir beside selected YAML. CLI --config
   overrides the file; --mock/--mic advertise future runtime selections.
2. Phase 1: use YOLOv8n, static FP32 320x320 batch one, opset 17, no embedded
   NMS/simplification. Output (1,84,2100) decoded by ONNX Runtime code. Export
   happens only on laptop; runtime does not import Ultralytics/PyTorch.
3. Use OpenCV contrib >=4.10,<5 for CSRT/KCF instead of the original base OpenCV
   requirements. Use contrib headless on Uno Q. Change was communicated during
   Phase 1. Avoid installing multiple cv2 distributions in one environment.
4. Separate requirements-export.txt/.venv-export from laptop runtime because
   Ultralytics installs base OpenCV. The initial model was exported successfully
   before cleaning the runtime environment; the separate export venv is documented.
5. Python model downloader is the cross-platform implementation; the planned
   .sh entry point wraps it. Vosk is downloaded now per Phase 1 tasks, but no
   voice code is implemented until Phase 2.
6. Demo/benchmark process 320x240 frames. Benchmark preloads the same frames,
   warms detector first, excludes acquisition/model load, and reports target
   coverage so absent targets cannot inflate apparent tracking performance.
7. Highest-confidence initial target, nearest prior box-centre on re-detection.
   Immediate re-detection after tracker failure; missing detections clear target.
8. Phase acceptance includes human observation. Webcam smoke tests and FPS do
   not substitute for smooth visible person tracking.

## Licence

SOFTWARE_PLAN.md flags Ultralytics YOLO weights as AGPL-3.0. Preserve this note
in STATUS.md; using ONNX does not erase the model's licence obligations.

## Unresolved hardware choices

Do not guess board pin maps. Session B obtains board model and confirms pins
at firmware Gate F0. Session A obtains hotspot/Uno Q SSH and confirmed network
addresses at software Gate 0; it no longer implements pin maps or flashing.
Firmware pin comments are plans, not confirmations. No board-specific pin map
or hardware resume phrase has been supplied.

## Runtime and security boundaries

Never install PyTorch or Ultralytics on Uno Q. Firmware hotspot credentials
belong in ignored firmware secrets.h; Session B owns the non-secret example.
Do not put credentials or recordings/photos in context records. No hardware
flashing, deployment, or remote publish has occurred as part of Phase 1.

## Phase 2 decisions

- Immutable Command(action, target, direction, small) carries intent only;
  degrees and camera/control effects belong to Phase 3.
- Exact wake-word parser; no silent "center" alias or unsupported extra words.
- Fixed Vosk grammar: all 19 phrases plus [unk], SetWords(True), 16 kHz.
- Require complete matching word evidence and every confidence >= configured
  threshold (inclusive), finite and <=1. Missing evidence rejects the command.
- Partial camera word emits heard once per utterance; final/flush resets it.
  Empty/[unk] ignored; other rejected non-empty finals emit low_confidence.
- UDP has 3-packet startup jitter and 8-packet maximum by default, 32 ms playout,
  drops oldest backlog and fills underruns with silence. Arrival order only:
  no sequence numbers/timestamps exist in the specified raw PCM contract.
- Do not change system microphone defaults. Device selection belongs to demo CLI;
  AMD device 3 was verified here, while the default virtual line is unsuitable.
- Guided checklist summary stores accepted command coverage and background
  false-command counts only; no audio or background speech transcript is saved.
  Distance and actual chatter still require human confirmation.

## 2026-10-04 - Updated ownership decision

User's updated SOFTWARE_PLAN.md overrides the older software firmware tasks.
Never create/edit/move/delete anything under firmware/ in Session A; skip Phase 4.
FIRMWARE_PLAN.md governs the separate hardware-driven Session B. Read it for
integration, but do not implement it here. Section 2 contract unchanged; stop and
ask user before a change needed by either session. No guessing unknown IPs/ports.
Use firmware/tools/ checks at Gates A/B after B has flashed and passed F2/F3.
Report firmware defects via the user for B. Preserve before-every-commit context
rule; do not silently resolve B's firmware-only/root-context conflict.

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

## Accepted temporary microphone setup (2026-10-04)

User accepted the passing headset test as the current Phase 2 setup after the
final hardware path was explained, then asked for commit commands. Do not demand
another temporary built-in microphone test before the software phase commit.
Do not claim the original built-in-mic/distance test or INMP441 passed. Real
INMP441/C3 sends the contract PCM over UDP to Uno Q; select --mic udp at Phase 7,
retune confidence if necessary and repeat real command/audio acceptance.

Session B's firmware/STATUS.md records explicit user authorization for shared
root context updates. That overrides firmware-only edit guidance for those
context maintenance files; firmware implementation remains exclusively B-owned.

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

## F2 responsiveness fix - 2026-10-04
User reported delayed voice movement and no physical up movement despite HTTP
ACK. Keep F2 open. Separate servo target/PWM locking from camera frame locking
and cap MJPEG at10fps; capture still freezes servo motion. New build compiles
but is not flashed/tested. Preserve GPIO1 pan/GPIO2 tilt, clamps and existing
angle signs. Diagnose physical directions during retest before changing any
invert setting. User requested build first, tests afterward; no F3 advancement.

## F2 S3-only coding scope and task isolation - 2026-10-04
User clarified S3 fixes only and hardware tests after coding is complete; C3
phase stays deferred. Use dedicated servo task with20ms minimum spacing and
capture freeze, independent camera lock and Wi-Fi loop. Timing diagnostics
report command/PWM stages only; do not imply mechanical feedback or prove
speech latency fixed. Final code compiles but is not flashed; latest physical
voice movement report is failed/pending despite automated checker passes.

## User replaced ownership instructions - 2026-10-04
This session now follows Session A ownership: never edit firmware/. Existing
S3 firmware can be exercised diagnostically at integration, with private logs/
config/test media under ignored root logs/. Firmware fixes are handed to user
for separate Session B. Hardware/physical acceptance remains evidence based;
latest voice up observation failed and direct repeat observation is pending.

## Speech diagnostic finding; no production change - 2026-10-04
User retains boAt mic. Silence-separated diagnostic with exact wake phrase and
confidence0.7 accepted both mic-only commands and physically moved S3 upward.
Temporary10degree step and measured baseline581.5 are test parameters only;
do not ship fixed thresholds or weaken grammar from this limited evidence.
Original app unchanged; production phrase separation and remaining live
acceptance pending. Loud live calibration was discarded before speaking cue.

## Production bounded phrase separation - 2026-10-04
User authorized implementing the successful diagnostic approach in software.
Use bounded startup calibration, short pre-roll and0.7s quiet/8s maximum
phrases; preserve exact wake word and confidence0.7. Stop discards unfinished
commands. No fixed headset581.5 baseline shipped. Normal4degree directions and
centre now user-confirmed with boAt; this is manual control acceptance only.
Use Space-started visible prompts in ignored bench helpers when user misses
chat-timed cues; no change to the normal app's product UI. Stream stalls remain.

## Scoped voice commit decision - 2026-10-04
User requests commit commands. Isolate voice hunks in mixed app/main.py and
README.md via prepared ignored logs/voice-commit.patch; preserve pending tracker/
deployment edits. Context history shared with Session B included as required.
Intended message fix voice: finalise commands on bounded silence; existing
HEAD08fabad4fff50b1d9172bef0119a24e9fb70b8cb. Agent did not stage actual index,
commit or push. Isolated code snapshot115 tests passed; mixed tree121 earlier.

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
