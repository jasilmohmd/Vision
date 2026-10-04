# Firmware status (Session B)

## Current: F1 bench firmware ready for team testing - 2026-10-04

User explicitly directed implementing all four bench sketches now, while other
F0 checks are ongoing. This authorizes preparation, not a claim of F0/F1
hardware acceptance. Prior snapshots below are historical.

- Actual firmware implemented: bench/servo_sweep, neopixel_test, mic_level,
  ir_test. All four compiled; simultaneous-servo variant compiled too.
- verify_bench.ps1 -IncludeServoStress completed exit0 using CLI1.5.1,
  core3.3.11, ESP32Servo3.2.1, NeoPixel1.15.5. Servo builds emitted upstream
  MCPWM deprecation/unused-variable warnings; no compile errors.
- Servo: GPIO1 pan / GPIO2 tilt, 50Hz, 30..150 degree sweep, 1deg/40ms,
  sequential by default, BOTH_TOGETHER switch, centres and waits for r repeat.
- NeoPixel: GPIO7, brightness40, GRB default, all eight colour/flash states.
- Mic: INMP441 SCK4/WS5/SD6, 16kHz/32-bit left mono, 800-sample RMS/peak
  windows, SHIFT14 and clipping; no raw audio saved.
- IR: GPIO1, raw+debounced state and hold time. IR_ACTIVE_LOW=1 is provisional
  until real sensor test; optional part may be omitted.
- All sketches Serial115200, boot/reset and error logs, no network/secrets.
- TEAM_TESTING.md has setup, compile/upload commands, wiring, observations,
  troubleshooting and return report. verify_bench.ps1 never uploads.
- No physical test or flash by this agent. F1 real-part gate pending; wait for
  team results and F1 DONE before F2. F2/F3 camera/voice sketches are placeholders.
- Board: user-confirmed N16R8 dual-port with OV3660; camera signal map from user
  image matches core S3-EYE entry. PWDN/RESET remain unverified before F2.
- Network addresses remain unselected; live reachability checks follow F2/F3.
  HARDWARE_PLAN.md still absent.
- Existing HEAD: 5194c5ed39c02b2bcc91bfaef899492f5788838c.
  Intended testing commit: fw phase 1: add bench sketches for hardware testing.
  Implementation/context changes local and uncommitted; no push here.

Exact next action: user commits/pushes the actual bench sketches and handoff;
hardware team follows TEAM_TESTING.md and returns Gate F1 results/F1 DONE.

---

Earlier entries below are historical.

Updated: 2026-10-04. Current phase: F0; board facts / F0 DONE pending.

- Portable Arduino CLI 1.5.1 downloaded from Arduino's official release;
  SHA256 matched the release checksum. Local path: .toolchain/arduino-cli.exe.
- Existing ESP32 core 3.3.11 reused. Installed local ESP32Servo 3.2.1 and
  Adafruit NeoPixel 1.15.5 under .toolchain/user/libraries.
- Scaffold, firmware-local ignore rules, secret example and pin-free probe ready.
- Generic compile profiles: esp32:esp32:esp32s3:PSRAM=opi and
  esp32:esp32:esp32c3:CDCOnBoot=cdc. S3 OPI is a compile probe setting only,
  not a confirmed board fact. Actual camera FQBN/PSRAM mode awaits board model.
- Both generic compile probes passed (exit 0): S3 266499 bytes flash / 22388
  bytes RAM; C3 295710 bytes flash / 14476 bytes RAM. Upstream ESP32Servo
  unused-variable and S3 legacy MCPWM deprecation warnings were emitted.
  No hardware test or flash performed.
- All board pins and network addresses remain unconfirmed. Set passwords only
  in local ignored secrets.h files. No credentials requested for context/chat.
- HARDWARE_PLAN.md absent. Obtain it before relying on wiring phase references.
- F1-F5 not started. Existing camera/voice sketches remain legacy placeholders.
- User explicitly allowed shared root context updates for Session B.
- Current HEAD: 993e3d5f51fb7ea9d6a8a9212a5e485a3c93151e.
- User committed and pushed preparation for the separate testing team:
  fw phase 0: prepare toolchain and scaffold for team testing.
  Live origin/main verified at the same hash. This preparation commit does not
  complete F0 board acceptance or authorize F1. F0 DONE still pending.
- git diff --check passed; secret/build/media ignore rules verified. Pre-existing
  software changes were preserved. This post-push handoff update is uncommitted.

Run the compile-only checks from the repo root:

```powershell
./firmware/tools/verify_toolchain.ps1
```

No flashable hardware sketch exists yet. After F0 DONE, F1 bench sketches will
be compiled, then flashed only when the user identifies a connected board and
explicitly authorizes the upload. Serial for those sketches will be 115200 baud.

Next action: obtain the exact Gate F0 board facts
and F0 DONE. Do not start bench implementation before that phrase.

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

## Local C3 bench test started - 2026-10-04

User explicitly connected a C3 SuperMini and requested testing here. User says
options1+2 are connected (NeoPixel and INMP441). Test order: pixel then mic.
COM18 enumerated as USB Serial Device VID303A/PID1001; Bluetooth ports excluded.
Read-only esptool --chip esp32c3 --port COM18 chip-id did not identify the chip:
first unavailable-port error, then ClearCommError/PermissionError device-command
error. No firmware upload yet; no physical tests passed. Device presence varied
between scans. Asked user to hold BOOT while unplugging/replugging, release BOOT,
close Serial Monitor and reply ready. Await that physical state before retrying.
Next action: rescan, confirm C3 chip with esptool, upload NeoPixel bench firmware
on the confirmed port under user's start-test authorization, observe Serial and
obtain actual colour/pattern confirmation; then flash mic_level and check RMS.
No S3 test, F1 DONE or phase advancement; context update remains uncommitted.

## C3 NeoPixel test progress - 2026-10-04

User requested local testing and confirmed NeoPixel+INMP441 wired. After user
BOOT/replug step, esptool identified ESP32-C3 AZ rev1.1, embedded4MB flash,
USB Serial/JTAG on COM18. NeoPixel bench upload exit0 with all flash hashes
verified. User asked about power: use laptop USB, LiPo disconnected; pixel5V,
mic3V3, shared ground. After RESET with BOOT released, Serial confirms sketch
boot and all contract state labels through sleep. User confirms pixel cycles.
Specific colour/order acceptance still awaiting user's full-map confirmation.
Boot reasons observed:1 then11; ROM reports USB_UART_CHIP_RESET, not brownout.
One serial read was interrupted during RESET and succeeded after reopening.
No microphone test yet. No S3 servo or optional IR test; F1 gate not complete.
Next action: obtain full NeoPixel colour/pattern result, then upload mic_level
under existing local-test authorization and compare quiet/speech RMS+peak.
No commit/push or phase advancement here.

## Local C3 results: NeoPixel passed, mic baseline obtained - 2026-10-04

User explicitly confirms all NeoPixel colours/patterns match. GRB brightness40
accepted for this pixel. Serial also confirmed the complete cycle.
Uploaded mic_level to confirmed C3 COM18, exit0 with flash hash verification.
USB laptop power retained; LiPo disconnected. Current board firmware is mic_level,
replacing NeoPixel test (pixel no longer cycles; no production Wi-Fi firmware).
Ten-second requested quiet baseline:201 windows, averageRMS361.0557,
minRMS47.3, maxRMS2316.2, maxPeak4732, zero clipped windows. SHIFT14, left16kHz.
Physical quiet conditions not independently verified; these are observed numeric
levels, not calibrated sound pressure or speech recognition acceptance. No raw
recording saved. Asked user for readiness to speak continuously near mic for10s.
Next action: capture speech RMS/peak, compare to baseline and adjust SHIFT only
if clipping occurs; obtain human confirmation. Servo/IR remain untested; F1 not
complete, no phase advancement or commit/push.

## C3 microphone comparison: acceptance not passed - 2026-10-04

NeoPixel all-colour/pattern acceptance passed by explicit user confirmation;
GRB brightness40 preserved. C3 COM18 currently runs mic_level, USB powered.
First requested10s speech sample:201 windows, meanRMS295.2403, maxRMS2005,
maxPeak4202, zero clipping; earlier quiet sample meanRMS361.0557. Not a clear rise.
Repeated45s capture with quiet first10s, explicit speak-now cue, continuous speech
requested until stop. Baseline200 windows meanRMS317.3785, maxRMS1715.8,
maxPeak2529. Speech16..40s:480 windows, meanRMS341.6658, maxRMS3562.4,
maxPeak4921, zero clipping. Mean rose only about7.7%; mic hardware acceptance
NOT passed. No I2S error observed; steady numeric windows arriving. SHIFT14/left
retained; changing gain does not address uncertain physical pickup.
Asked user to verify VDD3V3/GND/SCK4/WS5/SD6/LR-GND and confirm speaking close to
actual INMP441 sound hole throughout capture. Await answer before more tests.
Next action: apply F1 troubleshooting (pin/LR/channel checks), correct reported
wiring/test-condition issue, then repeat controlled speech versus silence.
Do not claim a microphone pass or F1 DONE. No raw audio saved, no new commit/push.
S3 servo and optional IR untested; camera/voice integration not started.

## Ten-second mic retest - 2026-10-04

User confirms wiring correct and requested another test limited to10s.
COM18 mic_level numeric speech window:201 measurements, meanRMS385.4960,
maxRMS2626.2, maxPeak2795, zero clipped windows. Compared with previous quiet
mean317.3785/maxPeak2529, no clear speech pickup established. User speech cue
sent when monitor's initial10s setup window yielded; actual alignment of speech
with measured window is not independently confirmed. Do not claim speech pass.
SHIFT14/left retained, no raw audio recorded or firmware change. Current C3
still mic_level; NeoPixel colour check previously passed. USB power, no LiPo.
Next action: controlled near-mic clap/tap stimulus or left/right-slot diagnostic
per F1 troubleshooting, with explicit timing. Await user steering. No F1 DONE,
commit/push or later-phase implementation.

## Synchronized clap diagnostic - 2026-10-04

User accepted10s clap test. Opened COM18 first, armed until explicit local
start signal, then requested five loud claps over10s.200 windows, meanRMS475.0025,
maxRMS2552.1, maxPeak26632;15 windows exceeded peak10000;zero clipping.
This is a clear transient response (~10.5x prior quiet peak2529), supporting
working sound pickup with left channel/SHIFT14. Speech acceptance still pending;
clap response is not speech recognition or F1 complete evidence.
Requested readiness for one final synchronized10s speech test at approximately
5cm from mic, with explicit speak-now cue. User can stop instead. No raw audio
saved. Current C3 COM18 remains mic_level; pixel previously passed.
Next action: if ready, measure synchronized speech and compare to quiet levels;
if stop, preserve pending acceptance and stop diagnostics. No commit/push here.

## Local C3 bench results: NeoPixel and mic passed - 2026-10-04

User confirmed correct microphone wiring and readiness for synchronized10s
speech approximately5cm from INMP441. Monitor armed before explicit start signal.
Measured201 windows, meanRMS1648.8781, maxRMS12900.2, maxPeak14937,
6 windows above peak10000, zero clipped windows. Mean is about5.2x prior quiet
317.3785; peak about5.9x quiet2529. Clear speech-associated level increase now
observed: F1 mic response check passed. Earlier weak speech windows were not
accepted; synchronized retest resolves that remaining local mic check.
Keep left channel, SHIFT14, SCK4/WS5/SD6/LR-GND. No gain/firmware code adjustment
needed. This confirms bench level response, not recorded voice quality, Vosk
recognition or UDP stability (later F3/software integration).
NeoPixel passed via explicit user all-colours/patterns confirmation: GPIO7,
GRB order, brightness40. Actual C3 ESP32-C3 AZ rev1.1/4MB flash, COM18.
Current uploaded sketch mic_level; pixel cycle replaced by microphone firmware.
Both uploads exit0/hash verified. USB laptop power; LiPo disconnected. All finite
Serial capture processes finished and COM18 closed. No raw audio saved.
S3 servo gate still untested; optional IR not tested/omission not yet confirmed.
F1 hardware phase not complete; no F1 DONE, F2/F3 implementation, commit/push here.
Next action: connect/authorize S3 servo bench test and record smoothness/rail
voltage; optional IR test or explicit omission; then obtain F1 DONE before F2.

## Local S3 sequential servo test - 2026-10-04

User connected S3 camera board with two capacitors/two servos, confirmed USB
connection, panGPIO1/tiltGPIO2, S3-fed5V/commonGND, capacitor polarity and
30..150degree bracket clearance; explicitly authorized sweep.
COM19 CH343 USB-UART identified ESP32-S3 rev0.2 with embedded8MB PSRAM.
Flashed sequential servo_sweep profile PSRAM=opi,FlashSize=16M on COM19;
upload exit0, all flash hashes verified.35s finite Serial monitor captured
312 angle updates (opened after sweep began), PAN/TILT phases and DONE centred
90/90. Last angle pan90/tilt90. No error/reset lines during captured portion;
initial boot logs were not captured. Serial port closed when finite monitor ended.
Requested physical smoothness/centering/no jitter/binding/reset confirmation
and whether multimeter is available before both-servo stress test. Await answer.
No voltage reading yet; servo hardware/power acceptance remains pending.
C3 NeoPixel and mic bench checks already passed. Optional IR not tested/omitted
not confirmed. F1 gate incomplete; no F1 DONE, commit/push or F2 implementation.
Next action: if separate sweeps physically passed, flash BOTH_TOGETHER variant,
observe motion/Serial and measure minimum5V rail (target above~4.6V); otherwise
use F1 troubleshooting before further motion.

## S3 sequential repeat - 2026-10-04

User requested test again. Sent r to existing sequential servo_sweep on COM19;
no reflashing. Captured START BOTH_TOGETHER=0, PAN-only then TILT-only, all480
angle updates, DONE centred90/90. Process exit0, no error/reset lines observed,
port closed. Physical smoothness/centering still awaiting user confirmation;
no 5V reading or both-servo stress test yet. F1 hardware acceptance pending.
Next action: obtain physical result, then both-servo test and voltage reading.
No new commit/push or phase advancement.

## Servo horn alignment pending - 2026-10-04

User reports both servos returned to their starting positions after sequential
sweep and says servo arms still need alignment. This confirms observed return,
not yet mechanical neutral alignment, physical smoothness or voltage acceptance.
Existing sequential sketch completed and commands90/90; no repeat sent here.
Advised disconnect USB power before removing/reseating horns, fit bracket neutral
against commanded90-degree reference, then reconnect for repeat testing.
Do not trigger motion while user adjusts horns. Current S3 COM19 retains
servo_sweep; both-servo stress and minimum5V rail measurement remain pending.
Next action: await user alignment/readiness, repeat sequential test as needed,
then both-servo test/voltage. C3 pixel/mic passed; optional IR unresolved.
No F1 DONE, phase advancement, new firmware change, commit or push.

## Servo alignment completed; reconnect pending - 2026-10-04

User reports alignment done. Attempted present-device scan: no USB serial device
currently present (all USB Ports scan empty), so no motion or upload performed.
Asked user to reconnect S3 via same UART USB connector and reply connected.
Warned existing sequential sketch auto-sweeps after startup; keep bracket clear.
Asked whether multimeter is available to measure minimum5V rail during both-servo
motion; answer pending. Do not infer voltage or power acceptance.
Next action: after explicit reconnect, identify S3/COM, upload existing compiled
BOTH_TOGETHER variant, observe Serial and obtain smoothness/centering and actual
minimum rail voltage. Alignment reported done; physical full acceptance pending.
C3 NeoPixel/mic previously passed. IR omission/test unresolved. No F1 DONE,
commit/push or later-phase work.

## Voltage measurement setup - 2026-10-04

User confirms multimeter ready and will measure during both-servo test.
Actual voltage still unmeasured. S3 USB reconnect reply remains pending; no
upload/motion performed since alignment. Next action: confirm S3 connected,
run BOTH_TOGETHER test, obtain lowest5V rail value and physical motion result.

## S3 both-servo test executed - 2026-10-04

User reports horn alignment done, confirms multimeter ready, then explicitly
confirms S3 reconnected. Verified same S3/COM19 CH343, rev0.2/embedded8MB PSRAM.
Uploaded compiled servo_sweep_both on COM19 (BOTH_TOGETHER=1), exit0/all flash
hashes verified. Initial run observed29 trailing updates/DONE90/90. Requested
repeat for complete trace and measurement: START BOTH_TOGETHER=1, all240
simultaneous updates, DONE centred90/90, exit0. No reset/error lines in repeat.
User asked to report lowest5V/GND rail reading during movement (target>~4.6V)
and confirm physical smoothness/neutral/no jitter/binding/reset. Results pending;
do not equate commanded angles/Serial success with actual power/motion acceptance.
Also asked whether optional IR is omitted or wired for testing; answer pending.
Current S3 firmware is both-servo bench (auto-sweep on next powerup, r repeats).
COM19 monitor closed. C3 current retained mic_level; NeoPixel/mic checks passed.
F1 real-part gate not complete until remaining results; no F1 DONE, F2 work,
commit or push. Next action: review actual voltage/motion+IR choice, fix F1
issues if any, then obtain F1 DONE before camera firmware.

## S3 servo/power acceptance passed - 2026-10-04

User reports minimum5V rail measurement5.05V during both-servo movement and
answers yes to smooth simultaneous motion, neutral return, no jitter/binding/
resets. Physical result user-observed; full240-update Serial repeat independently
captured without error/reset.5.05V exceeds plan's approximately4.6V target.
Servo motion and supply check passed with aligned horns, USB laptop power and
two capacitors. Current S3 COM19 remains BOTH_TOGETHER=1 bench firmware.
C3 pixel and mic bench checks previously passed. Optional IR test/omission reply
still pending; F1 DONE not received. Do not advance to F2 before gate resume.
Next action: obtain IR result or explicit omission, then F1 DONE; refresh required
context/status before any testing-result commit. No new commit/push here.

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

## Firmware F2 prepared; awaiting hardware flash confirmation - 2026-10-04

Session B current state (supersedes prior paused/F1-pending entries): user
acknowledged F1 DONE, requested the S3 camera test with existing software,
approved DHCP for the first camera check, and confirmed local Wi-Fi secrets
configured. IR remains deferred to firmware/TODO.md, omitted from prototype.
User clarified Uno Q setup belongs to another session; do not operate on Uno Q.

Implemented firmware/camera_head/camera_head.ino and camera_pins.h: PSRAM JPEG
QVGA stream on81, control on80 (/move,/status,/capture,/ack), bounded servo slew,
capture mutex, retained JPEG/retry until ack, QVGA restoration, reconnect logs.
GPIO1 pan/GPIO2 tilt; camera signal map from supplied board diagram matches
installed core ESP32S3_EYE map. PWDN/RESET=-1 from matching core entry still
requires successful physical camera init. OV3660 PID and PSRAM checked at boot.
F1 aligned horns start90/90; boot centres without sweep, no measured physical
position feedback. Static production configuration retained; DHCP is bench-only.
Added firmware/tools/check_camera.py and camera README. Checker uses85..95degree
pattern, status targets, JPEG dimensions, open-stream capture, retained retry,
ack, same connection survival and fresh QVGA stream. Photos are ignored/private.

Actual checks: camera compile exit0, ArduinoESP32core3.3.11/OPIPSRAM/16MBflash,
983621bytes program,56640bytes globals; upstream ESP32Servo warnings only.
Checker --help passed. JPEG dimension/split-frame/truncation smoke checks passed
on rerun after correcting PowerShell command quoting. Disconnected127.0.0.2
returned expected clear FAIL and exit1. Git ignores secrets.h and test JPEGs.
No S3 camera upload or live endpoint/image/motion test yet; no camera IP known.
Reliable full-resolution size, camera init, stream recovery, physical motion,
Wi-Fi reconnect and existing-app integration remain unverified. F2 not complete.
Current S3 COM19 retains BOTH_TOGETHER=1 servo bench (auto-sweep on powerup),
C3 retains mic_level; recheck ports before flashing. F3+ not started.

Existing HEAD08fabad4fff50b1d9172bef0119a24e9fb70b8cb; no commit/push performed.
Intended commit message after F2 acceptance: fw phase 2: camera_head.
Preserved concurrent software files and records; do not stage unrelated edits.
Exact next action: obtain Gate F2 hardware/flash confirmation (F2 DONE/go),
recheck S3 COM19 identity, upload compiled camera_head, watch Serial115200 for
sensor/PSRAM/IP, run firmware/tools/check_camera.py against actual DHCP IP,
report each result and obtain physical image/motion observations. Then use the
existing software with a firmware-owned temporary config only if camera checks
pass. Preserve Uno Q ownership in other session. Refresh handoff before ending.

## Firmware F2 live testing and unresolved physical motion - 2026-10-04

Current Session B state supersedes F2-prepared/awaiting-flash entries. User
confirmed F2 DONE/go; verified S3 COM19/MAC28:84:85:a1:85:ec and flashed actual
camera firmware (all flash hashes verified). Boot confirms8MBPSRAM and
OV3660PID0x3660, validating supplied signal map/PWDNRESET-1 camera operation.
Observed DHCP S3 IP192.168.29.231; laptop192.168.29.58. Static IP still deferred.

Implemented/fixed15s control send timeout,5s stream send timeout, peer-disconnect
probe/forced session close, Serial stream diagnostics, bounded4KB chunked JPEG
send, and video pause during still transfer (servo mutex released for transfer).
Checker continuously consumes video during capture as existing app does.
One earlier complete endpoint run passed: status,85..95degree targets, QVGA,
QXGA2048x1536 capture260238bytes3.33s, identical retry3.05s, ack, same-connection
recovery0.15s, fresh stream0.27s. Later weak-link repeat measured-77..-79dBm,
QVGA17.27s, capture271522bytes88.21s, identical retry64.45s, ack passed; same
connection failed read timeout. Initial3s send truncations were fixed, but
repeated app/disconnect tests remained intermittent. Do not claim robust video.
User cannot move board closer/clear antenna now. Wi-Fi reconnect observed with
unchanged IP; at times takes~55s. No brownout/reset observed within test intervals.

Existing software test uses ignored firmware/.build/config-s3-camera.yaml with
real S3, boAt headset device4/16kHz, local-only light destination (C3 still bench),
private photos under firmware/.build/s3_app_photos. Root config/app not edited.
User's initial live-video/commands-worked reply was explicitly withdrawn as a
mistake; do not cite it as acceptance. Repeat diagnostic wrapper confirmed a
rendered S3 frame and recognized camera centre/up/track person; camera move ACKs
observed (e.g90/86 then tracking updates). Numerous2s stream timeouts/reconnects.
No voice shoot command/saved app-gallery photo observed; cue came near end of
90s window. User requests explicit Speak now cue; provide only after live frame
and selected microphone are active. Microphone preference is boAt headset.
Direct existing CameraClient(default2s read timeout) then successfully captured
and decoded2048x1536 JPEG324956bytes in6.94s, acked, held_photofalse. Private
JPEG stored only in ignored build; this is API capture, not voice/gallery pass.
A temporary helper initially failed by assuming MjpegStream.start returns self;
corrected helper then saw real stream timeouts. Do not claim helper integration
passed. Temporary wrappers/check scripts stay ignored, not deployment artifacts.

User reports servos not moving; clarified live-stream URL only displays video,
laptop app sends movement. Requested direct observed test: pan90->70->110->90,
tilt90->75->105->90. All targets/commanded-angle readbacks succeeded; full trace
exit0 and centre90/90, uptime533..555/reset_reason1. Physical reply pending.
Compiled GPIO pulse-readback diagnostic (input buffer enabled without changing
PWM routing, sampled GPIO1/2; Serial p) successfully:984629bytes program,
56640bytes globals. NOT flashed yet; current flashed firmware is preceding
chunked-photo/stream-diagnostic build984197bytes. PWM library uses MCPWM onS3,
camera clock uses separateLEDC. Neither confirms external signal/power until
physical or pulse check. Do not label physical motion passed from HTTP readback.

F2 remains IN PROGRESS: physical servo observation, stable video/reopen at
adequate signal, latest full checker run and voice-shoot/gallery confirmation
pending. F3+ not started, C3 mic_level retained, IR future TODO. No Uno Q actions;
user explicitly reserves it for another session. Existing HEAD remains
08fabad4fff50b1d9172bef0119a24e9fb70b8cb; no commit/push. Intended message after
acceptance: fw phase 2: camera_head. Preserve concurrent software changes.
Exact next action: get observed direct servo result; if no movement, flash
compiled pulse-readback build to verified COM19, measure GPIO1/2 PWM and inspect
actual servo power/sharedground/signals (without guessing pin replacements).
Then resolve real camera/app stability and repeat a focused voice-shoot test
with timely cue. Refresh required context before ending/any eventual commit.

## Latest Session B handoff: servos confirmed; voice test waiting - 2026-10-04

User observed the direct camera-firmware test and explicitly reports BOTH
servos moved smoothly and centred. This supersedes the earlier physical-motion
failure/pending entry: pan70..110 and tilt75..105 physical acceptance passed.
No pin/PWM change was required. Removed the extra unflashed GPIO pulse probe;
current source/build matches the tested chunked-photo firmware. Final compile
exit0:984197bytes program,56640bytes globals. No additional upload after this
source restoration; flashed S3 remains camera_head with diagnostic stream logs,
15s control/5s stream send timeout and4KB chunked JPEG/video pause during send.

Confirmed: S3DHCP192.168.29.231,8MBPSRAM,OV3660PID0x3660, QVGA video seen by
existing software frame-ready marker, movement/voice centre/up/track person
acknowledged, direct camera module2048x1536 JPEG324956bytes decoded/save6.94s,
/ack completed and held_photofalse. Prior full endpoint run passed on stronger
signal. Subsequent weak Wi-Fi repeat and app runs have stream read/connect
timeouts; live reliability is pending. Do not claim an entirely stable run.
User's earlier live-video/commands-success reply was withdrawn as a mistake.
No voice shoot/gallery-save pass: shoot cue came late in prior90s test; no shoot
command/saved gallery photo observed. API photo capture is separately passed.

User selected boAt headset(device4,16kHzmono confirmed), requires Speak now cue
only once actual S3 preview frame and microphone are active. Asked focused45s
voice-photo check; user replies NOT READY YET. Hold further physical/voice tests
until ready. All preview/check/Serial processes used here ended; no runtime left
running by this session. Boards retain camera_head(S3) and mic_level(C3).
Temporary45s wrapper and config are ignored under firmware/.build, outgoing
lights local-only; C3 voice/LEDintegration is not implemented or claimed tested.
No Uno Q operations; another session owns its setup. IR remains future TODO.

F2 remains IN PROGRESS; do not startF3, commit/tag as accepted, or push here.
Exact next action when user is ready: start ignored firmware/.build/run_s3_preview.py
with repo PYTHONPATH using boAt device4, wait S3_PREVIEW_FRAME_READY marker,
immediately cue Speak now: camera shoot; allow full45s, verify app saved JPEG
and metadata/gallery plus S3ack/heldfalse and stream recovery. If weak Wi-Fi
persists, record failure and resolve actual link before finalF2 acceptance.
Final full checker/reconnect/reopen reliability and physical image quality
confirmation remain pending. Refresh context/status before any eventual commit.
Verified existing HEAD: 08fabad4fff50b1d9172bef0119a24e9fb70b8cb. No commit/push performed.
Intended message after acceptance: fw phase 2: camera_head.

## F2 focused voice-photo result; timeout diagnostic ready - 2026-10-04
User resumed with ready. Started45s S3/boAt headset test, confirmed actual
S3_PREVIEW_FRAME_READY before explicit Speak now cue. Recognizer logged
camera shoot at05:27:57.260; automatic photo job failed at05:28:23.752 because
existing CameraClient capture exhausted3 attempts with2s read timeout.
No automatic gallery JPEG was saved during that run; stream timeouts observed.
Runtime ended; do not mark voice-to-gallery test passed.

Afterward status confirmed retained held_phototrue, uptime1279/reset_reason1,
RSSI-51. Recovered the SAME held image using existing CameraClient with
(timeout connect3/read20,retries0), decoded2048x1536/362008bytes in12.54s,
saved through existing PhotoStore asIMG_0001.jpg with recovered-command label
under ignored firmware/.build/s3_app_photos, then /ack and held_photofalse.
This is recovered original voice shot, NOT a successful automatic save run.
Existing Flask gallery test client passed page/index/API and exact JPEG route
response for that real image; no synthetic photo record created. Private image
and metadata stay ignored; none stored in shared context.

Prepared capture-only timeout diagnostic in ignored firmware/.build/run_s3_preview.py:
hold existing clientRLock, temporarily setcapture timeout(connect3/read20),
restore normal move/status timeout afterward. No app/config/roottools/deploy
source changed by firmware session. New45s voice retry awaits user readiness;
prompt offered Ready repeat or Pause here. Give Speak now immediately after
actual first preview frame and boAt microphone are active, then verify Saved
log/JPEG+metadata,/ack heldfalse and gallery. Do not treat extended diagnostic
as stock software compatibility. Firmware unchanged since tested984197byte
build; S3IP192.168.29.231, C3 stillmic_level, IRfutureTODO, no Uno Q work.
F2 remains IN PROGRESS: stock capture timeout compatibility, stable stream,
latest endpoint acceptance and image quality confirmation pending. NoF3,
commit/push/tag. Preserve other software session records and work.

## Latest F2 gallery viewing state - 2026-10-04
User reports localhost8080 unavailable. Cause: timed45s app shuts down its
embedded gallery at exit; prior Flask test-client pass did not leave an HTTP
server running. Started standalone existing GalleryServer(localhost127.0.0.1,
port8080) via ignored firmware/.build/run_s3_gallery.py, pointed at same real
S3testphotos. Unified exec session92886 intentionally remains RUNNING so user
can inspect actual recoveredIMG_0001.jpg. Verified real HTTP200 gallery page,
/api/photos entry and JPEG route362008bytes, valid SOI/EOI. User links provided:
http://localhost:8080 and /photos/IMG_0001.jpg. Keep gallery running until user
finishes/requests stop; do not mistake it for camera app or Uno Q service.
Next timed preview config now usesgallery8081 to avoid port collision; both
serve same ignored test-photo directory. Persistent8080 refresh shows any new
saved photo. No root app/config/deploy edits, no commit/push. Firmware unchanged.
45s capture-timeout20diagnostic prepared but NOT STARTED: user's response was
about gallery, not readiness to repeat voice test. Exact next action: let user
inspect recovered image; when explicitly ready, repeat boAt voice shoot test,
cue immediately after actual frame-ready marker, verify automatic saving/ACK
and refresh persistent gallery. Stock2s timeout compatibility/stable stream
remain pending; F2 not complete, noF3. Update handoff before any session ending.

## Latest F2 repeat: waiting for exclusive S3 stream viewer - 2026-10-04
User replied ready to longer capture-timeout diagnostic. Started prepared
boAt preview on8081; S3 statusuptime1609,heldfalse,RSSI-52 and mic/app ready,
but repeated stream read timeouts; NO frame-ready marker and NO Speak now cue.
Timed run ended (exec81340); no new voice/automatic-photo pass.
Serial12s probe without reset showed stream socket54 frames3817->3989,
RSSI-52..-54. After own preview ended, laptop Get-NetTCPConnection found no
remote192.168.29.231:81 connection. Evidence suggests another device/viewer
occupies the single-viewer stream server; peer identity not verified. Asked user
to close other S3 stream viewer; reply pending. Do not operate on Uno Q or kill
other session processes. No S3 reset/upload performed in this repeat.

Ignored diagnostic wrapper now measures45s from first rendered S3 frame, not
from app startup; no-frame watchdog exits after30s, preventing cue at end of
an already-expired window. Capture-only timeout(connect3/read20) retained;
software-owned app source unchanged. Persistent local gallery8080/session92886
remains intentionally running with recoveredIMG_0001.jpg. Next preview8081
shares same ignored photos. Exact next action: after other viewer is closed,
start wrapper, wait actual frame-ready marker, immediately cue camera shoot,
verify automatic save/ACK/gallery/stream. If no known viewer, diagnose actual
peer before guessing/altering other sessions. F2 pending; noF3/commit/push.

## Latest F2 build after voice movement report - 2026-10-04
This entry supersedes the earlier viewer-blocked and pending-photo snapshots.
Other stream viewer was closed by user. Real voice camera shoot saved
IMG_0002.jpg (355681 bytes, 5.94s) and IMG_0003.jpg (334604 bytes, 3.68s),
both decoded2048x1536 with automatic ACK. User says photos look good. These
voice runs used a diagnostic capture-only20s read timeout, not a source change
to the software app. A separate stock CameraClient2s capture/ACK/stream recovery
check passed (4.34s total capture); it does not establish prolonged reliability.
The full previous-build camera checker passed: status0.22s, small servo
pattern2.98s, QVGA0.41s, capture355624bytes2048x1536 in9.24s, identical retry
8.42s, ACK0.63s, same-stream recovery1.29s, fresh-stream1.29s. Actual log is
ignored firmware/.build/camera-final-check.log; those results predate this build.

Five-minute boAt voice command test (ignored s3-command-test.log) recognised
right90->94->98->102, left102->98->94->90->86 and up tilt90->86. HTTP ACKs
confirm targets only. User subsequently reported delayed responses and that
up did not work physically. Therefore voice movement acceptance is FAILED/
PENDING despite ACKs; do not claim all directions passed. Preview also had
intermittent read/connect timeouts. User accidentally cancelled the attempted
restart, then explicitly requested resume building and rerun tests afterward.
No second preview log/process was observed; no additional speech cue issued.
Previous direct pan70..110/tilt75..105 test had passed physical smooth motion,
but it does not override this latest voice-command failure.

F2 source now separates servoMutex from cameraMutex: /move and the20ms slew
loop no longer wait for stream frame acquisition. CapturePending still freezes
servo writes during capture, with a servo-lock barrier before acquisition.
MJPEG is capped at10fps to leave radio airtime for control. No pin-map, angle
sign or endpoint-contract change; inversion must not be guessed from missing
motion. Checker now exercises85..95 pan/tilt under an active consumed stream,
requires each move ACK below2s, checks commanded slew and fresh video.

Offline validation of NEW build: Arduino CLI compile exit0, core3.3.11,
ESP32Servo3.2.1, S3 OPI PSRAM/16MB;984561 program bytes,56648 global bytes.
Checker py_compile and --help passed; git diff --check passed (line-ending
warnings only). This build is NOT FLASHED and new checker hardware steps are
UNRUN. S3 retains earlier984197-byte camera build; C3 retains mic bench sketch.
No app/, root config/tools/deploy edits by this session; concurrent software
work preserved. No Uno Q operation, no F3 implementation, no commit/push/tag.
Persistent local gallery localhost8080 intentionally retained for viewing real
S3 test photos; private photos/config/secrets remain ignored, not in context.
Existing HEAD08fabad4fff50b1d9172bef0119a24e9fb70b8cb. No commit requested;
possible later message: fw phase 2: isolate servo control from camera streaming.
Exact next action: recheck connected S3 USB-UART port and unchanged clear
mechanics, flash this compiled F2 build when user resumes hardware testing,
run updated checker exclusively, then cue a short voice direction/centre/fine
movement test and collect physical observation. F2 remains IN PROGRESS until
that retest passes; stay within F2 and do not advance to F3 yet.

## Latest F2 flash and weak-link retest; user paused for hotspot - 2026-10-04
User said go ahead, authorizing the compiled984561-byte F2 update flash/retest.
Upload COM19 exit0 with all written-data hashes verified; identified ESP32-S3
rev0.2 embedded8MB PSRAM, MAC28:84:85:a1:85:ec. New firmware is now FLASHED.
No Uno Q or C3 operation. The checker against192.168.29.231 passed status
(2.15s), small85..95 pattern/readback (23.49s) and QVGA stream (6.70s), then
FAILED servo responsiveness during active streaming: first pan85/tilt90 ACK
3.40s exceeded2s requirement. Checker exited1 and restored90/90. Capture,
retry, ACK and stream recovery were NOT REACHED on this build; previous-build
passes do not substitute. Log firmware/.build/camera-responsive-check.log
is ignored. RSSI initially-78dBm, then-75dBm; no reset seen (reset_reason1,
uptime monotonic). Three idle/no-stream status reads measured0.24/0.16/0.07s;
actual commanded pan/tilt90/90, held_photo=false. Streaming load contributes
to latency; precise network cause and physical up response remain unverified.
Two attempted Python serial reads failed offline (quoting syntax, missing
pyserial) before opening the port; corrected native .NET8s serial read opened
COM19 without DTR/RTS reset and produced no lines. HTTP diagnostics supplied
actual state; do not claim observed boot Serial from this retest.

User now says they will use their hotspot instead and explicitly said wait.
Hardware testing PAUSED at user request; no headset preview/speech cue started.
User was instructed to configure new WIFI_SSID/WIFI_PASS only in ignored
firmware/camera_head/secrets.h, laptop on same hotspot, password out of chat.
Exact next action: wait for user readiness/configuration, rebuild with local
hotspot settings, flash authorised connected S3 and obtain new DHCP IP from
Serial (never assume192.168.29.231 on new network); run updated checker with
single stream viewer, then short cued voice movement test with physical
observations. F2 IN PROGRESS; no F3/commit/push/tag. Persistent localhost8080
gallery intentionally retained. Shared software-session work preserved.
Existing HEAD08fabad4fff50b1d9172bef0119a24e9fb70b8cb; no commit requested.

## Latest F2 hotspot acceptance and cued voice retest - 2026-10-04
User replied ready after switching hotspot/configuring ignored secrets. Rebuild
exit0 (984577 program bytes,56648 globals), upload COM19 exit0 with verified
written hashes. Serial confirmed OV3660 PID0x3660, DHCP IP10.153.76.67,
RSSI-37dBm and HTTP ready. Laptop hotspot IPv4 is10.153.76.189,
gateway10.153.76.224. Never reuse the old192.168.29.231 IP on this network.

Updated checker exit0 against10.153.76.67: status0.39s, small85..95 pattern
3.85s, QVGA0.30s, servo responsiveness while streaming4.32s total. Each move
ACK took0.43/0.27/0.38/0.19/0.14s, all below2s, commanded slew settled and
fresh video continued. QXGA2048x1536 capture214614bytes4.37s, identical held
retry3.66s, ACK0.24s, same-stream recovery0.43s, fresh stream0.91s. No reset
or held image at initial status, RSSI-36dBm. Full log ignored
firmware/.build/camera-hotspot-check.log. These are actual NEW flashed-build
passes; physical direction and long-running stability are separate checks.

Started boAt headset device4 preview on verified hotspot IP using ignored
local wrapper/config only; no app-source edits. Unified exec session75805,
log firmware/.build/s3-hotspot-voice-test.log. Actual live-frame ready marker
observed, then signal armed120s voice window and explicit Speak now cue given:
up three times/centre, down three/centre, left three/centre, right three/centre,
with2s pauses. Normal moves4degrees; centre90/90. Physical confirmation
requested and pending; prior failed-up observation is not yet superseded.
Persistent gallery localhost8080 retained; timed preview gallery8081.
F2 remains IN PROGRESS pending cued voice observations; no F3/Uno Q work,
no commit/push/tag. Existing HEAD08fabad4fff50b1d9172bef0119a24e9fb70b8cb.
Exact next action: inspect live COMMAND_RESULT/ACK log, collect user physical
results, stop/centre preview after test and update handoff with actual outcome.

## Latest F2 S3-only code completed; hardware tests deferred - 2026-10-04
User reported Still delayed or inconsistent after the hotspot voice test, so
physical voice movement acceptance remains FAILED/PENDING. The normal up,
down,left,right and centre commands were recognised and acknowledged, but
that is not proof of prompt/correct physical response. Fine1degree adjustment
was not confirmed. Preview still logged intermittent2s stream-read timeouts.
Stopped preview75805; shell exit1 reflects redirected native Vosk stderr in
this PowerShell session, not a proven clean app exit. Direct centre ACK passed
and status confirmed target/commanded90/90, held_photo=false, uptime230,
RSSI-54, reset_reason1. Persistent gallery8080 retained. No further preview
or hardware tests are running from this session.

User explicitly instructed complete coding before further tests, and clarified
Finish only the S3 camera fixes first. This does NOT authorize C3/F3 work;
voice_unit remains placeholder. Hardware tests are deferred until user resumes.
No guessing about voice recognition latency or physical direction. Laptop
recognizer finalises phrases before dispatch and is software-session owned;
inspected only. No software source/config/deploy changes by this session.

Completed S3 code update: separate camera/servo mutexes and10fps video cap
retained; servo slew moved to dedicated FreeRTOS task (priority2,3072-byte
stack), at most2degrees every20ms, independent of Arduino Wi-Fi reconnect loop.
No burst catch-up if scheduling is delayed. Capture freeze and barrier retained.
Added /status diagnostic move_received_ms, move_settled_ms, move_in_progress
and Serial move handler timing. Values describe commanded PWM, not measured
physical position; uint32 millisecond wrap documented. Checker prints commanded
slew duration and requires no pending movement after settling. Ignored laptop
preview helper now records move-send time and request duration for next test.
These changes isolate a plausible scheduling cause and expose timing; they
DO NOT establish that speech/physical inconsistency is fixed.

Final NEW source compile exit0:984997 program bytes,56656 globals, core3.3.11,
ESP32Servo3.2.1, S3 OPI PSRAM/16MB. Checker and diagnostic helper py_compile
passed, checker --help passed, git diff --check passed (line-ending warnings
only). Final build log ignored firmware/.build/camera-task-final-compile.log.
This final dedicated-task build is NOT FLASHED and hardware tests UNRUN.
S3 still runs earlier hotspot984577-byte build, whose automated checker passed
but subsequent physical voice test failed. Full camera checker must be rerun
on the final build; don't transfer earlier acceptance to new code.

Existing HEAD08fabad4fff50b1d9172bef0119a24e9fb70b8cb. No commit requested,
no staging/commit/push/tag. Possible later message: fw phase 2: isolate servo
slew task and add movement timing diagnostics. Root/firmware context refreshed
under explicit user authorization; concurrent software-session work preserved.
Exact next action when user resumes testing: verify connected S3 COM19, flash
compiled final build (credentials remain ignored/local), read current DHCP IP,
run checker exclusively, then short cued headset test using timing diagnostics
and physical observation. No F3 advancement while F2 physical checks pending.

## Latest F2 final S3 build flashed - 2026-10-04
User explicitly requested go ahead and flash. Verified COM19 USB port, then
uploaded the final dedicated-servo-task build (984997 program bytes,56656
globals). Upload exit0, written-data hashes verified, same ESP32-S3rev0.2/
MAC28:84:85:a1:85:ec/embedded8MB PSRAM. Serial after upload confirmed
reset_reason1, PSRAM8388608bytes, OV3660PID0x3660, centre90/90 without sweep,
DHCP10.153.76.67, RSSI-39dBm, HTTP80/81 ready. Logs ignored under
firmware/.build/camera-task-upload.log and camera-task-serial.log.
Read-only /status verification passed with NEW movement timing fields,
target/commanded90/90, move_in_progress=false, uptime19s, held_photo=false,
RSSI-40, reset_reason1. This establishes flash/boot/HTTP readiness only.
No movement commands, camera checker or headset preview run in this turn.
Final-build streaming/capture/voice/physical checks remain UNRUN; previous
build's user report Still delayed or inconsistent remains unresolved.

S3 now runs final984997-byte build; C3/F3 remains deferred by user's explicit
S3-only scope. Persistent gallery8080 retained. No app/root config/tools/deploy
edits, no Uno Q operation, no commit/push/tag. Existing HEAD remains last
verified08fabad4fff50b1d9172bef0119a24e9fb70b8cb (no commit performed here).
Exact next action: when user resumes testing, run updated checker against
current Serial-confirmed10.153.76.67 with exclusive stream viewer, then short
cued voice test capturing request/PWM timing and user physical observations.
F2 IN PROGRESS; no acceptance claim from flashing alone; no F3 advancement.

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

### Final firmware commit verification - 2026-10-04
Compile-only recheck exited0:984997 program bytes,56656 globals, confirmed S3
OPI PSRAM/16MB profile. Ignored log firmware/.build/camera-commit-compile.log.
Checker syntax/help passed; staged whitespace check passed. Explicitly staged
all11 pending firmware files plus7 shared root context/status files (18 total).
Unrelated deployment/software/enclosure changes remain unstaged; ignored secrets,
builds/toolchain/photos/logs excluded. Existing HEAD64994af remains unchanged.
No flash, hardware retest, commit or push performed. F2 acceptance still pending.
User next action: review git diff --cached --stat, commit with intended message
fw phase 2: implement S3 camera head and servo control, then git push origin main.
