# Firmware status (Session B)

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
