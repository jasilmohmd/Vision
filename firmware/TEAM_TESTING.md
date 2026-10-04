# F1 bench firmware: hardware team handoff

Prototype scope update (2026-10-04): user deferred optional IR to TODO.md.
IR physical testing is skipped for this version. Servo, NeoPixel and microphone
checks are required. The exact original gate below is preserved for reference;
its optional IR item is omitted under this user direction.

These are actual standalone firmware sketches. Test each part before camera/
voice integration. All Serial output uses 115200 baud. Boot logs show numeric
ESP reset reason; Wi-Fi is intentionally disabled and there is no bench IP.
No camera_head/voice_unit runtime firmware is implemented yet.

## Toolchain and compilation

Install Arduino CLI on PATH (or pass -Cli /path/to/arduino-cli.exe to the script).
From the repository root:

```powershell
arduino-cli core update-index --additional-urls https://espressif.github.io/arduino-esp32/package_esp32_index.json
arduino-cli core install esp32:esp32@3.3.11 --additional-urls https://espressif.github.io/arduino-esp32/package_esp32_index.json
arduino-cli lib install ESP32Servo@3.2.1 "Adafruit NeoPixel@1.15.5"
./firmware/tools/verify_bench.ps1 -IncludeServoStress
arduino-cli board list
```

S3: ESP32S3 Dev Module, 16MB flash, OPI PSRAM for N16R8. Default S3 Serial
is UART: use the board's USB-to-UART connector. If using its native USB/OTG
connector, compile with `-S3Fqbn 'esp32:esp32:esp32s3:PSRAM=opi,FlashSize=16M,CDCOnBoot=cdc'`.
C3 SuperMini: ESP32C3 Dev Module with USB CDC On Boot enabled.
The script prefers the local portable CLI/libraries when present, otherwise
uses your installed CLI/libraries. Toolchains/builds are not shipped in Git.

## Upload and Serial

Identify the correct board and replace COM_S3 / COM_C3 with its actual port.
Run these manually only when that board is plugged in and the hardware lead
authorizes flashing. Nothing here automatically uploads.

```powershell
# S3 UART connector, normal one-servo-at-a-time sweep:
arduino-cli upload --fqbn esp32:esp32:esp32s3:PSRAM=opi,FlashSize=16M --port COM_S3 --input-dir ./firmware/.build/servo_sweep ./firmware/bench/servo_sweep
arduino-cli monitor --port COM_S3 --config baudrate=115200

# C3: choose ONE sketch, then repeat for each remaining part:
arduino-cli upload --fqbn esp32:esp32:esp32c3:CDCOnBoot=cdc --port COM_C3 --input-dir ./firmware/.build/neopixel_test ./firmware/bench/neopixel_test
arduino-cli monitor --port COM_C3 --config baudrate=115200
```

For microphone or IR, replace both neopixel_test path components with mic_level
or ir_test. Close the monitor before uploading another sketch. For native USB
S3 use the same CDC-enabled FQBN used when compiling. Arduino IDE is also fine:
open the matching .ino, select the options above, upload, and use Serial Monitor
or Serial Plotter at 115200. If C3 upload fails, hold BOOT while plugging in.

## Tests and reports

### 1. Servos (S3)

- Pan signal GPIO1; tilt GPIO2. S3 5V/GND feeds the rails, both servo power leads
  connect to those rails, shared ground. C2 and C1 are 470uF, correct polarity,
  at the S3 feed and servo headers. Follow the hardware team's wiring plan.
- Clear the bracket before powering up. Initial centre command may move an
  unknown physical position. Sketch waits 5 seconds after its startup logs,
  attaches both servos, centres them, then moves 1 degree every 40ms.
- Pan sweeps 30..150..90 while tilt holds90, then tilt sweeps while pan holds90.
  Mechanical clearance must support those angles; lower SAFE_MIN/MAX if needed.
- It stops centred; send lowercase r (any newline setting) to repeat.
- After separate motion succeeds, flash .build/servo_sweep_both using the same
  sketch/upload command to exercise BOTH_TOGETHER=1. Both move in that variant.
- Report: each servo smooth? Centre correct? Minimum S3 5V reading while BOTH
  move (target above approximately 4.6V), any jitter/reset and boot reset reason.
- Resets: check cable/capacitor polarity and revert to separate motion. Jitter:
  verify shared ground and breadboard rail continuity, then try another servo.

### 2. NeoPixel (C3)

- GPIO7 -> 330 ohm -> DIN; VCC5V and shared GND. One external pixel, not the
  board's onboard RGB LED. Brightness capped40/255. COLOR_ORDER defaults NEO_GRB.
- Repeating sequence logs every state: ready green; heard blue300ms then green;
  tracking cyan; nosubject amber slow blink; saved white300ms then green;
  error red twice then green; reconnect purple slow blink; sleep off.
- Report each colour/pattern. If red/green swap, change COLOR_ORDER to NEO_RGB
  at the top of the sketch, recompile and reflash, then report the working order.
  These simple bench delays are deliberate; F3 production timers will be nonblocking.

### 3. Microphone (C3)

- INMP441 VDD3V3, GND, SCK4, WS5, SD6, L/R tiedGND; wires short (under20cm).
- 16kHz, 32-bit mono slots, left channel; 800 samples per ~50ms window.
  SHIFT14 converts to signed16-bit with saturation. Output rms,peak is in int16
  units, not calibrated sound pressure. Open Serial Plotter after startup text.
- Speak then remain quiet. Report silence/speech RMS and peak; speech should
  clearly rise. Persistent peak32767/32768 suggests clipping: increase SHIFT,
  rebuild, and report the resulting value. This sketch saves no audio.
- Flat/zero: verify wiring/LR ground. Temporarily change MIC_SLOT to
  I2S_STD_SLOT_RIGHT only to diagnose a channel mismatch; report it rather than
  silently changing the intended left-channel wiring. I2S errors log their code.

### 4. IR (C3, optional)

- Sensor VCC3V3/GND, OUT GPIO1. It must drive OUT; no internal pull assumed.
- Logs initial raw level, debounced changes, active state and hold time on release.
  IR_ACTIVE_LOW=1 is provisional; verify near/far raw levels before accepting it.
- Report raw level far/near, active polarity, and held_ms for a roughly1s hold.
  Change IR_ACTIVE_LOW to0 only if actual module output requires it. If IR is
  omitted, mark skipped/optional; this does not block the required three parts.

## Return this summary

```text
Board/connector/COM ports:
Compile results (four sketches + BOTH_TOGETHER):
Servo pan/tilt smooth; minimum both-moving 5V; resets/jitter:
NeoPixel colours/patterns; working COLOR_ORDER:
Mic silence/speech RMS+peak; working SHIFT; channel:
IR near/far raw levels; polarity; hold time (or omitted):
Remaining F0 setup facts / camera PWDN+RESET documentation:
Failures and Serial logs:
F1 DONE (only when real-part checks pass)
```

Live Wi-Fi/IP checks follow F2/F3 firmware, not these bench programs.
HARDWARE_PLAN.md is absent from this checkout: the hardware team should supply
it before relying on the plan's named wiring phases. No firmware gate is passed
just because these sketches compile; hardware observation is still required.

## 🛑 GATE F1 — Bench tests on real parts

**Print this and wait for `F1 DONE`** (the hardware team can answer in pieces as parts are wired):
- [ ] **Servo sweep:** S3 5V/GND on the breadboard rails with C2 and C1 fitted, pan servo on GPIO 1, tilt on GPIO 2. Tell me when it's plugged in, and I'll flash `servo_sweep`. Does each servo sweep smoothly? What does the S3's 5V pin read while both move (target: above about 4.6V)?
- [ ] **NeoPixel:** DIN → 330 Ω → GPIO 7, 5V, GND. Flash `neopixel_test`. Do the colours match their names? (If red and green are swapped, I'll switch the colour order.)
- [ ] **Mic:** INMP441 wired per §1, L/R to GND, short wires. Flash `mic_level`. Does the plotter jump when you talk and stay near flat in silence?
- [ ] **IR (optional):** flash `ir_test`. Does it trigger when your cheek comes within a few cm?

**Troubleshooting**
| Symptom | Fix |
| --- | --- |
| S3 resets during sweep | Shorter/thicker USB cable; check capacitor polarity; test `BOTH_TOGETHER 0` |
| Servo jitters at rest | Shared ground; split breadboard rail; try a different servo |
| Mic flat / zeros | L/R floating, SCK/WS/SD swapped, wrong slot (try right channel to confirm) |
| Mic clipping | Increase `SHIFT` |
| C3 won't flash | Hold BOOT while plugging in, then upload |
| No Serial on C3 | Enable USB CDC On Boot |

