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
- Existing HEAD: 891274f580ad6d7e6b5abc87b7c5abdf2cd317d1.
- No commit while F0 acceptance pending. Intended message after acceptance:
  fw phase 0: toolchain and firmware scaffold.
- git diff --check passed; secret/build/media ignore rules verified. Pre-existing
  software changes were preserved; no paths were staged.

Run the compile-only checks from the repo root:

```powershell
./firmware/tools/verify_toolchain.ps1
```

No flashable hardware sketch exists yet. After F0 DONE, F1 bench sketches will
be compiled, then flashed only when the user identifies a connected board and
explicitly authorizes the upload. Serial for those sketches will be 115200 baud.

Next action: obtain the exact Gate F0 board facts
and F0 DONE. Do not start bench implementation before that phrase.
