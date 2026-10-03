# Hands-Free Photography Rig — Firmware Build Plan (Session B, for a coding agent)

> Run this in a **separate coding-agent session** from the app (Session A, `SOFTWARE_PLAN.md`), on the same repo.
> The **hardware team** drives this session. It stays in step with `HARDWARE_PLAN.md`: each gate here lines up with a
> hardware phase, so code is ready the moment the wiring is.
>
> For Claude Code, reference this file from a `firmware/CLAUDE.md`; for Codex, from `firmware/AGENTS.md`
> (e.g. "Follow ../FIRMWARE_PLAN.md phase by phase").

---

## 0. Instructions for the coding agent (read first)

1. **You only edit files inside `firmware/`.** Session A owns `app/`, `tools/`, `deploy/`, `config.yaml`. Never touch them.
2. **The interface contract in `SOFTWARE_PLAN.md` §2 is the source of truth** (endpoints, ports, payloads, light states).
   If anything in it must change, **stop and ask the user**; Session A depends on it.
3. **Work phase by phase.** Write code and make it compile before each gate, so it's ready when the hardware is.
4. **Hardware gates (🛑) are hard stops.** At each one:
   - Summarise what's ready and how to flash it.
   - Print the gate checklist word for word.
   - **Stop and wait** for the resume phrase (e.g. `F2 DONE`). Don't assume, don't work ahead.
   - If the user reports a failure, work through the gate's troubleshooting list first.
5. **Flash only with the user's confirmation**, and only to a board the user says is plugged in.
6. **Never guess pin maps.** Use the board model and pins the user confirms at Gate F0.
7. Keep `firmware/STATUS.md` updated after each phase; commit after each phase (`fw phase 2: camera_head`).
8. Every sketch prints clear Serial logs (boot reason, Wi-Fi state, IP, errors) at 115200 baud.

---

## 1. Fixed facts for this build

| Item | Value |
| --- | --- |
| Toolchain | Arduino-ESP32 core 3.x, via `arduino-cli` (or the Arduino IDE) |
| Libraries | `ESP32Servo`, `Adafruit NeoPixel` (camera support is in the core) |
| Camera head board | ESP32-S3 camera board (exact model confirmed at Gate F0), **PSRAM enabled** |
| Servo pins | **GPIO 1 = pan, GPIO 2 = tilt** (confirmed at Gate F0) |
| Servo power | From the S3's own 5V pin, with C2 + C1 (470 µF each) on the rail |
| Voice unit board | ESP32-C3 SuperMini, **USB CDC On Boot enabled** for Serial |
| Mic (INMP441, I2S) | SCK GPIO 4, WS GPIO 5, SD GPIO 6, L/R → GND (left channel) |
| NeoPixel (WS2812, 1 px) | DIN GPIO 7 via 330 Ω |
| IR sensor (optional) | OUT GPIO 1 |
| Network | Phone hotspot, static IPs, credentials in `secrets.h` |

---

## 2. Folder layout (Session B owns all of it)

```
firmware/
├── STATUS.md
├── secrets.example.h          # WIFI_SSID, WIFI_PASS, S3_IP, C3_IP, UNOQ_IP, GATEWAY, SUBNET
├── bench/
│   ├── servo_sweep/servo_sweep.ino
│   ├── neopixel_test/neopixel_test.ino
│   ├── mic_level/mic_level.ino
│   └── ir_test/ir_test.ino
├── camera_head/
│   ├── camera_head.ino
│   ├── camera_pins.h          # copied from the core's CameraWebServer example
│   └── secrets.h              # gitignored
├── voice_unit/
│   ├── voice_unit.ino
│   └── secrets.h              # gitignored
└── tools/                     # laptop-side Python checks (requests, numpy only)
    ├── check_camera.py
    └── check_voice_unit.py
```

`secrets.h` files are gitignored. The `.example` file shows the format.

---

## 3. Timeline against the hardware build

| Firmware phase | Ready by (from start) | Lines up with |
| --- | --- | --- |
| F0 Toolchain + board info | ~0.5 h | H0 |
| F1 Bench sketches | ~1 h | H1.1 servo test, H2.2–2.4 parts tests |
| F2 `camera_head.ino` + `check_camera.py` | ~3 h | H1 done → Gate A |
| F3 `voice_unit.ino` + `check_voice_unit.py` | ~5 h | H2 done → Gate B |
| F4 Battery diagnostics | ~6 h | H3 → Gate C |
| F5 Hand-off to Session A | with Gates A, B | Session A Phases 6–7 |

---

## 4. Phases

### Phase F0 — Toolchain and board facts 💻

**Tasks**
- Install `arduino-cli`, the `esp32` core (3.x), and the `ESP32Servo` and `Adafruit NeoPixel` libraries.
- Find the correct FQBNs for the S3 and C3 boards; note the board options needed (PSRAM for the S3, USB CDC On Boot for the C3).
- Create the folder layout, `secrets.example.h`, `.gitignore` entries, `STATUS.md`.
- Compile an empty sketch for both targets to prove the toolchain works.

## 🛑 GATE F0 — Board facts

**Print this and wait for `F0 DONE`:**
- [ ] Exact **ESP32-S3 camera board model** (printed on the board).
- [ ] Confirm **GPIO 1 (pan) and GPIO 2 (tilt)** are free on that board, or give replacements.
- [ ] Hotspot name and password; the static IPs you want for the S3, C3 and Uno Q (or let me propose them).
- [ ] Which laptop USB port each board will be plugged into for flashing.

---

### Phase F1 — Bench test sketches 💻

Small, single-purpose sketches the hardware team uses to test each part on its own. Each prints what it's doing on Serial.

- **`servo_sweep`** (S3): attach GPIO 1 and GPIO 2; sweep one servo at a time, slowly, between safe limits (e.g. 30°–150°), then centre both at 90°. Serial prints the angle. A `#define BOTH_TOGETHER 0/1` lets the team test the worst case.
- **`neopixel_test`** (C3): cycle the full contract colour map on GPIO 7 with names printed on Serial; brightness capped at about 40/255. `#define COLOR_ORDER NEO_GRB` (switchable to RGB).
- **`mic_level`** (C3): read the INMP441 over I2S (16 kHz, 32-bit slots, left channel), compute RMS and peak every ~50 ms, print as `rms,peak` for the Serial Plotter. A `#define SHIFT` controls the 32→16-bit scaling.
- **`ir_test`** (C3): print the IR sensor state on change and how long it was held. Note whether the module is active-low.

**Acceptance:** all four compile.

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

---

### Phase F2 — `camera_head.ino` 💻 (then 🔌 at Gate F2)

Base it on the core's **CameraWebServer** example (two `esp_http_server` instances: control on :80, stream on :81), stripped down to the contract.

**Camera**
- Pin map from `camera_pins.h` for the model confirmed at F0 (e.g. the ESP32-S3-EYE or XIAO ESP32S3 entries). If no entry matches, stop and ask.
- JPEG, frame buffers in PSRAM, 2 buffers, grab-latest mode. Stream at **QVGA (320×240)**, quality ~12.
- Refuse to boot into the main loop without PSRAM; print a clear error.

**Endpoints (exactly as in the contract)**
- `GET :81/stream` — MJPEG multipart.
- `GET /move?pan=&tilt=` — clamp to `PAN_MIN/MAX`, `TILT_MIN/MAX` (`#define`s matching `config.yaml`: 10–170 and 40–140); set the **target** angles; reply `{"pan","tilt"}` with the clamped targets.
- `GET /capture` — take a mutex that pauses the stream and freezes servo motion; switch to the highest frame size that captures reliably on this sensor; discard 1–2 frames after the switch; copy the JPEG into a PSRAM buffer; switch back to QVGA; release the mutex; return the JPEG. Keep the buffer.
- `GET /ack` — free the held buffer; `{"ok":true}`.
- `GET /status` — `{"pan","tilt","uptime_s","held_photo","rssi","free_heap","free_psram","reset_reason"}`.

**Servos (they share the S3's power, so be gentle)**
- `ESP32Servo` on GPIO 1/2, 50 Hz, pulse range set for MG90S.
- **Slew limiting:** a loop task moves the actual angle toward the target by at most ~2° every ~20 ms. This caps current spikes.
- No motion while `/capture` holds the mutex.
- Centre (90°/90°) on boot, slowly.

**Network**
- Static IP from `secrets.h`; `WiFi.setSleep(false)` for streaming latency.
- Reconnect loop that never gives up; Serial log on every state change.

**`tools/check_camera.py`** (laptop): `--ip`; checks `/status`; runs a small pan/tilt pattern and reads back targets; grabs one stream frame to `stream.jpg`; `/capture` to `capture.jpg` with its resolution and time; `/ack`; prints PASS/FAIL per step and timings.

**Acceptance:** compiles; `check_camera.py` runs (it will fail to connect until hardware is ready, with a clear message).

## 🛑 GATE F2 — Camera head on real hardware (= Gate A in the other plans)

**Print this and wait for `F2 DONE`:**
- [ ] Camera head wired exactly as in `HARDWARE_PLAN.md` H1.3 (S3 5V/GND → rails, C2 at the feed, C1 at the servos, pan GPIO 1, tilt GPIO 2).
- [ ] Bracket assembled, camera attached, free to move.
- [ ] S3 plugged into this laptop. Say go, and I'll flash `camera_head.ino`.
- [ ] Laptop joined to the hotspot.

**After you reply I'll flash, watch Serial for the IP, run `check_camera.py`, and report every step.** Open `http://<S3_IP>:81/stream` on a phone to see video.

**Troubleshooting**
| Symptom | Fix |
| --- | --- |
| Camera init failed | PSRAM option off, wrong `camera_pins.h` model, loose ribbon |
| Reboots on `/move` | Lower slew rate; cable/capacitor checks from F1 |
| Reboots on `/capture` | Lower the capture frame size one step |
| Stream freezes after capture | Mutex not released or frame size not restored |
| `reset_reason` shows brownout | Power problem, not code: cable, capacitors, or servos on the bank's second port |

---

### Phase F3 — `voice_unit.ino` 💻 (then 🔌 at Gate F3)

**Audio**
- I2S via the core's `ESP_I2S` library (check the core's examples for exact call signatures): standard mode, **16 kHz, 32-bit slots, mono, left channel**, pins from §1.
- Convert each 32-bit sample to int16 with `>> SHIFT` (default 14, value from F1 testing) and clip.
- Send packets of **512 samples (1024 bytes)** to `UNOQ_IP:5005` over UDP. `WiFi.setSleep(false)`.

**Light**
- Listen on UDP **5006**; parse the contract states; drive the NeoPixel with **non-blocking** timers: steady states, `heard`/`saved` 300 ms flashes that return to the previous steady state, `error` two blinks, `nosubject`/`reconnect` slow blinks, `sleep` off/dim.
- Brightness cap ~40/255; colour order from F1.
- Show `reconnect` whenever Wi-Fi is down.

**IR (optional, `#define USE_IR 1`)**
- Active level from F1. Held ≥ 1 s → send `shoot` to `UNOQ_IP:5007`; then a 2 s lockout.

**Network**
- Static IP; reconnect loop; Serial logs.
- `UNOQ_IP` in `secrets.h`. **For bench testing, set it to the laptop's IP**; switch it to the Uno Q's IP for integration (Gate B).

**`tools/check_voice_unit.py`** (laptop): listens on UDP 5005 for 5 s → `check.wav` (16 kHz mono s16le); reports packet count, packet loss, RMS/peak; sends every light state to the C3 on 5006 one second apart, printing each name; listens on 5007 and reports any `shoot`.

**Acceptance:** compiles; `check_voice_unit.py` runs.

## 🛑 GATE F3 — Voice unit on real hardware (= Gate B in the other plans)

**Print this and wait for `F3 DONE`:**
- [ ] Voice unit wired per `HARDWARE_PLAN.md` H2 (mic, NeoPixel, optional IR), USB power for now.
- [ ] `secrets.h` `UNOQ_IP` set to this laptop's IP for the test.
- [ ] C3 plugged into this laptop. Say go, and I'll flash `voice_unit.ino`.

**After you reply I'll flash it, run `check_voice_unit.py`, and you'll watch every colour. Then play `check.wav` and confirm your voice is clear.** Finally, set `UNOQ_IP` back to the Uno Q and reflash.

**Troubleshooting**
| Symptom | Fix |
| --- | --- |
| No packets arrive | Wrong `UNOQ_IP`, laptop firewall blocking UDP 5005, different network |
| WAV silent | Same causes as F1 mic; check `SHIFT` |
| WAV choppy | Packet loss: move the hotspot closer; check `setSleep(false)` |
| Colours stick | Flash timers blocking; states not matching the contract strings |

---

### Phase F4 — Battery diagnostics 💻

Support the hardware team's 15-minute soak test on battery.

- Camera head: `/status` already reports `reset_reason`, uptime and free memory; also log the reset reason on boot to Serial.
- Voice unit: on boot, flash the NeoPixel once in a colour that signals the last reset reason (e.g. brownout = red then off) and log it.
- `tools/soak_monitor.py` (laptop, optional): polls the S3 `/status` every 5 s, counts UDP audio packets from the C3, and prints any uptime reset or audio gap with a timestamp.

## 🛑 GATE F4 — Soak test (= Gate C)

**Print this and wait for `F4 DONE`:**
- [ ] All units on battery per `HARDWARE_PLAN.md` H3.
- [ ] Run `soak_monitor.py` for 15 minutes while Session A runs tracking and voice.
- [ ] Report any resets and their `reset_reason`.

---

### Phase F5 — Hand-off to Session A

- Tag the firmware (`fw-v1`) and summarise in `firmware/STATUS.md`: board model, pins, IPs, capture resolution, `SHIFT`, colour order, known limits.
- Tell the user, in one message they can paste to Session A: the S3 and C3 IPs, the capture resolution, and that the real boards now satisfy the contract.
- From here, only fix firmware bugs Session A reports; no new features without the user's go-ahead.
