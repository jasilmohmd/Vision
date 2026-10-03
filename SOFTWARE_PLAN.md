# Hands-Free Photography Rig — Software Build Plan (for a coding agent)

> Save this file in the repo root. For Claude Code, reference it from `CLAUDE.md`; for Codex, from `AGENTS.md`
> (e.g. "Follow SOFTWARE_PLAN.md phase by phase").

---

## 0. Instructions for the coding agent (read first)

1. **Work strictly phase by phase, in order.** Do not start a phase until the previous phase's acceptance checks pass.
2. **Hardware gates (🛑) are hard stops.** When you reach one:
   - Summarise what is finished and what was tested.
   - Print the gate's checklist for the user, word for word.
   - **Stop and wait.** Do not continue, do not "assume it's done", do not work ahead on later phases.
   - Resume only when the user replies with the gate's resume phrase (e.g. `GATE A DONE`).
   - If the user reports a failed check, use the gate's troubleshooting list before moving on.
3. **Use mocks until the real hardware exists.** Every hardware-facing component has a mock so the whole app runs on a laptop.
4. **Keep `STATUS.md` updated** after every phase: phase, date/time, what works, what's pending, known issues.
5. **Commit after every phase** with a message like `phase 3: control core + mocks`.
6. **Never guess IPs or ports.** If one is unknown, ask the user.
7. **Never install PyTorch / ultralytics on the Uno Q.** Export models on the laptop; run them on the Uno Q with `onnxruntime` / OpenCV.
8. Prefer small, testable modules. Every module gets a quick test or a runnable demo script.
9. **Firmware is not yours.** A parallel session builds it from `FIRMWARE_PLAN.md`. Never edit `firmware/`. If the interface contract (§2) needs a change, stop and ask the user, since the firmware depends on it.

---

## 1. What we're building

A voice-controlled, wheelchair-mounted camera for a user who can only move their head and speak.

- **Camera head** — ESP32-S3 camera board + 2 servos (pan/tilt). Streams video, moves on command, captures full-res photos.
- **Voice unit** — ESP32-C3 SuperMini + INMP441 MEMS mic + 1 NeoPixel (+ optional IR sensor). Streams mic audio, shows status colours.
- **Brain** — Arduino Uno Q (Linux side, Python). Speech recognition (Vosk), detection (YOLO ONNX + YuNet), tracking (OpenCV tracker), control loop, photo storage, gallery web page.
- **Network** — all three boards on the user's phone hotspot with fixed IPs. No internet required at runtime.

Core user flow: *"Camera, track person"* → camera follows the person → *"Camera, shoot"* → photo saved → visible in phone gallery.

---

## 2. Interface contract (do not change without telling the user)

### Camera head (ESP32-S3)
| Endpoint | Method | Response | Notes |
| --- | --- | --- | --- |
| `http://<S3_IP>:81/stream` | GET | MJPEG multipart stream, 320×240 | Separate server on port 81 (like the `CameraWebServer` example) |
| `http://<S3_IP>/move?pan=<deg>&tilt=<deg>` | GET | JSON `{"pan":int,"tilt":int}` | Absolute angles; firmware clamps to limits |
| `http://<S3_IP>/capture` | GET | `image/jpeg`, full resolution | Firmware keeps a copy in memory until `/ack` |
| `http://<S3_IP>/ack` | GET | JSON `{"ok":true}` | Frees the held photo |
| `http://<S3_IP>/status` | GET | JSON `{"pan","tilt","uptime_s","held_photo":bool,"rssi"}` | Health check |

### Voice unit (ESP32-C3)
| Direction | Transport | Payload |
| --- | --- | --- |
| C3 → Uno Q `:5005` | UDP | Raw PCM, signed 16-bit little-endian, mono, 16 kHz, 512 samples (1024 bytes) per packet |
| Uno Q → C3 `:5006` | UDP | ASCII light state: `ready`, `heard`, `tracking`, `nosubject`, `saved`, `error`, `reconnect`, `sleep` |
| C3 → Uno Q `:5007` | UDP | ASCII `shoot` (optional IR head-tilt trigger) |

### NeoPixel colour map (implemented in C3 firmware)
| State | Colour |
| --- | --- |
| `ready` | soft green, steady |
| `heard` | blue flash (300 ms), then previous state |
| `tracking` | cyan, steady |
| `nosubject` | amber, slow blink |
| `saved` | white flash (300 ms), then previous state |
| `error` | red, two blinks, then previous state |
| `reconnect` | purple, slow blink |
| `sleep` | off / very dim |

### Voice commands (wake word "camera")
`track person`, `track face`, `track dog`, `track cat`, `stop tracking`, `left`, `right`, `up`, `down`, `a bit left`, `a bit right`, `a bit up`, `a bit down`, `centre`, `shoot`, `burst`, `timer`, `sleep`, `wake`.

---

## 3. Repo layout

```
photo-rig/
├── SOFTWARE_PLAN.md
├── STATUS.md
├── config.yaml                 # IPs, ports, thresholds, servo limits
├── requirements-laptop.txt     # opencv-python, onnxruntime, vosk, sounddevice, flask, pyyaml, requests, numpy, ultralytics (export only)
├── requirements-unoq.txt       # opencv-python-headless, onnxruntime, vosk, flask, pyyaml, requests, numpy
├── app/
│   ├── main.py                 # entry point: python -m app.main [--mock] [--mic laptop|udp]
│   ├── config.py
│   ├── state.py                # state machine
│   ├── vision/
│   │   ├── stream.py           # MJPEG reader thread, latest-frame buffer, auto-reconnect
│   │   ├── detector.py         # YOLO ONNX via onnxruntime (COCO classes)
│   │   ├── face.py             # YuNet via cv2.FaceDetectorYN
│   │   └── tracker.py          # CSRT/KCF wrapper + re-detect policy
│   ├── control/
│   │   └── controller.py       # offset -> pan/tilt steps (dead zone, gain, clamps)
│   ├── voice/
│   │   ├── audio_source.py     # UdpAudioSource, LaptopMicSource (same interface)
│   │   ├── recognizer.py       # Vosk fixed-grammar recogniser + confidence filter
│   │   └── commands.py         # grammar list + phrase -> Command parsing
│   ├── io/
│   │   ├── camera_client.py    # /move, /capture, /ack, /status with timeouts + retries
│   │   ├── light_client.py     # UDP light states to C3
│   │   └── speaker.py          # optional TTS (Piper/eSpeak); no-op if no speaker
│   ├── storage.py              # photos/IMG_0001.jpg numbering, metadata json
│   └── gallery/
│       ├── server.py           # Flask gallery on :8080
│       └── templates/index.html
├── tools/
│   ├── export_onnx.py          # laptop only: YOLOv8n -> ONNX (imgsz 320)
│   ├── download_models.sh      # YuNet ONNX + Vosk small EN model
│   ├── mock_camera.py          # laptop webcam served with the S3 contract (+ simulated pan/tilt crop)
│   ├── mock_voice_unit.py      # laptop mic -> UDP 5005; prints light states from 5006
│   └── bench_vision.py         # FPS of detector/tracker on current machine
├── firmware/                   # owned by Session B (FIRMWARE_PLAN.md); do not edit
│   ├── camera_head/  voice_unit/  bench/
│   └── tools/check_camera.py, check_voice_unit.py
├── deploy/
│   ├── install_unoq.sh
│   └── photo-rig.service       # systemd unit
└── tests/
```

---

## 4. Phases

Legend: 💻 = laptop only · 🧠 = Uno Q · 🔌 = needs real hardware · 🛑 = hard stop for the user

---

### Phase 0 — Scaffold, config, contract 💻

**Tasks**
- Create the repo layout above, `STATUS.md`, `config.yaml`, both requirements files.
- `config.yaml` keys (with sensible defaults): `s3_ip`, `c3_ip`, `unoq_ip`, ports from the contract, `detect_every_n_frames: 5`, `dead_zone: 0.08`, `gain_deg: 12`, `max_step_deg: 4`, `pan_min/max: 10/170`, `tilt_min/max: 40/140`, `invert_pan`, `invert_tilt`, `vosk_conf_threshold: 0.7`, `centre_timeout_s: 1.5`, `photos_dir`.
- `app/config.py` loads it into a typed object; `--config` flag to override.

**Acceptance**
- `python -m app.main --help` runs. `pytest` runs (even with zero tests).

---

### Phase 1 — Vision on the laptop 💻

**Tasks**
- `tools/export_onnx.py`: export YOLOv8n (or YOLO11n) to ONNX at `imgsz=320`. Store in `models/`.
- `tools/download_models.sh`: fetch the YuNet face ONNX from the OpenCV model zoo and the Vosk small English model into `models/`.
- `vision/detector.py`: onnxruntime inference, letterbox preprocessing, NMS, returns `[(class_name, conf, x, y, w, h)]`. Filter to the requested class.
- `vision/face.py`: `cv2.FaceDetectorYN` wrapper with the same output shape.
- `vision/tracker.py`: on a new detection, init CSRT (fallback KCF); update every frame; re-run detection every `detect_every_n_frames` or when the tracker fails; pick the detection closest to the last box.
- Output per frame: target box or `None`, plus normalised offset `(dx, dy)` in `[-1, 1]` from frame centre.
- Demo script: laptop webcam window with box + offset overlay.

**Acceptance**
- Person tracked smoothly on the laptop webcam; offset printed; `tools/bench_vision.py` reports FPS for detector-only and detector+tracker.

**Licence note:** Ultralytics weights are AGPL-3.0. Fine for a hackathon; flag it in `STATUS.md`.

---

### Phase 2 — Voice on the laptop 💻

**Tasks**
- `voice/audio_source.py`: common interface `read_chunk() -> bytes` (s16le, 16 kHz, mono).
  - `LaptopMicSource` via `sounddevice`.
  - `UdpAudioSource` binding `0.0.0.0:5005`, with a small jitter buffer; tolerate lost packets.
- `voice/commands.py`: grammar list = every `"camera <command>"` phrase + `"[unk]"`; `parse(text) -> Command | None`.
- `voice/recognizer.py`: Vosk `KaldiRecognizer(model, 16000, grammar_json)`, `SetWords(True)`. On a final result: accept only if text starts with `camera` and every word's `conf >= threshold`; otherwise report `low_confidence` (only if non-empty and not `[unk]`).
- Emit events on a queue: `heard` (as soon as a partial contains "camera"), `command(cmd)`, `low_confidence`.
- Demo script: speak into the laptop mic, print events.

**Acceptance**
- Every command recognised from 0.5–1 m on the laptop mic; background chatter produces no commands.

---

### Phase 3 — Control core, mocks, gallery 💻 (full end-to-end simulation)

**Tasks**
- `io/camera_client.py`: `move(pan, tilt)`, `capture() -> bytes`, `ack()`, `status()`; timeouts (2 s), 2 retries, raises `CameraOffline`.
- `io/light_client.py`: `send(state)` over UDP; remembers the "steady" state so flashes return to it.
- `io/speaker.py`: optional TTS; if no audio device or disabled in config, no-op.
- `control/controller.py`: keeps current `pan/tilt`; given `(dx, dy)`: inside dead zone → no move; else step = clamp(gain × offset, ±max_step); apply invert flags; clamp to limits; call `move`. Rate-limit moves (max ~10/s).
- `state.py` state machine: `SLEEP`, `IDLE`, `TRACKING(target_class)`, `SHOOTING`, `TIMER`. Manual commands (`left`, `a bit up`, `centre`) work in IDLE and TRACKING. `stop tracking` → IDLE.
- Shooting: wait until centred or `centre_timeout_s`, `capture`, save via `storage.py`, `ack`, light `saved` (+ TTS "Photo N saved" if speaker). `burst` = 3 captures ~400 ms apart. `timer` = 3 blue blinks then shoot.
- No subject for > 2 s while tracking → light `nosubject`.
- `storage.py`: sequential filenames, `photos/index.json` with timestamp + command.
- `gallery/server.py`: Flask on `:8080`, newest-first grid, tap to open full image.
- `tools/mock_camera.py`: serves the full S3 contract from the laptop webcam. Simulate pan/tilt by cropping a 320×240 window out of the full frame and shifting it with the angles, so the control loop visibly works.
- `tools/mock_voice_unit.py`: laptop mic → UDP 5005; listens on 5006 and prints light states (colour names).
- `app/main.py`: threads for frame grabbing, audio/recognition, control loop (~10 Hz), gallery server. `--mock` points clients at localhost mocks.

**Acceptance (all on one laptop)**
- Run `mock_camera.py`, `mock_voice_unit.py`, `python -m app.main --mock`.
- Say *"Camera, track person"* → crop window follows you → *"Camera, shoot"* → photo in gallery at `http://localhost:8080` → light prints `saved`.
- Unit tests for `commands.parse`, `controller` step maths, `storage` numbering.

---

### Phase 4 — Firmware (handled by Session B, skip) 🚫

Firmware is built in a **separate session** that follows `FIRMWARE_PLAN.md`, driven by the hardware team, in parallel with you.
- **Do not create or edit anything in `firmware/`.**
- Make sure `tools/mock_camera.py` and `tools/mock_voice_unit.py` follow the contract in §2 exactly; that's what lets your app switch to the real boards at Gates A and B with only an IP change.
- The hardware checks you'll use later are `firmware/tools/check_camera.py` and `firmware/tools/check_voice_unit.py`, written by Session B. You may run them; don't edit them.

---

## 🛑 GATE 0 — Uno Q and network ready

**Stop here. Print this checklist to the user and wait for `GATE 0 DONE`:**

- [ ] Phone hotspot is set up (name + password noted).
- [ ] Arduino Uno Q is booted, joined to the hotspot, and reachable over SSH from the laptop.
- [ ] Tell me the Uno Q's IP address (or confirm the fixed IP plan).
- [ ] Tell me the static IPs planned for the S3 and C3 (the firmware session sets them on the boards).

**Troubleshooting:** Uno Q not booting → use a USB-C cable and supply rated 5V 3A. Can't find its IP → check the hotspot's connected-devices list.

---

### Phase 5 — Deploy to the Uno Q (against laptop mocks) 🧠

**Tasks**
- `deploy/install_unoq.sh`: apt packages if needed, venv, `pip install -r requirements-unoq.txt`, copy `models/` (ONNX, YuNet, Vosk) from the laptop via `scp`.
- Run the app on the Uno Q while `mock_camera.py` and `mock_voice_unit.py` run on the laptop (point `config.yaml` at the laptop's IP).
- Run `tools/bench_vision.py` on the Uno Q. If too slow: lower input size, raise `detect_every_n_frames`, prefer KCF over CSRT.

**Acceptance**
- Full mock flow works with the app running on the Uno Q; gallery reachable from the phone at `http://<UNOQ_IP>:8080`.
- Benchmark numbers recorded in `STATUS.md`.

---

## 🛑 GATE A — Camera head wired

**Stop here. Print this checklist and wait for `GATE A DONE`:**

- [ ] S3 **5V** pin → breadboard + rail, S3 **GND** → − rail (rails continuous end to end).
- [ ] **C2 470 µF** next to the S3 feed and **C1 470 µF** next to the servo headers, stripe on the − rail.
- [ ] Pan servo signal on **GPIO 1**, tilt on **GPIO 2**; red to +, brown to −.
- [ ] S3 powered from power bank A, one port, with a short thick USB cable (or the laptop while flashing).
- [ ] S3 5V pin stays above about 4.6V while both servos move.
- [ ] Servos mounted on the pan-tilt bracket, camera attached, bracket free to move.
- [ ] The firmware session has flashed `camera_head.ino` and its Gate F2 passed. Tell me the S3's IP.

**After you reply, I will run `firmware/tools/check_camera.py --ip <S3_IP>` and report every endpoint.**

**Troubleshooting:** S3 resets when servos move → shorter/thicker USB cable, check capacitor polarity, reduce `max_step_deg`; last resort, feed the servo rail from the bank's second port (keep the shared ground). Servos twitch → shared ground missing. No stream → PSRAM not enabled in board settings or wrong pin map.

---

### Phase 6 — Real camera integration 🧠🔌

**Tasks**
- Run `firmware/tools/check_camera.py` against the real S3 (already flashed by Session B). Report any firmware bugs to the user for Session B; don't fix them here.
- Point the app at the real S3. Tune `invert_pan/tilt`, `dead_zone`, `gain_deg`, `max_step_deg` until tracking is smooth with no oscillation.
- Verify `/capture` + `/ack` and the stream recovering after `/capture`.
- Keep using `mock_voice_unit.py` for voice.

**Acceptance**
- The real camera follows a person walking across the room; *"Camera, shoot"* (laptop mic via mock) saves a real photo to the gallery.

---

## 🛑 GATE B — Voice unit wired

**Stop here. Print this checklist and wait for `GATE B DONE`:**

- [ ] INMP441 → C3: VDD 3V3, GND, SCK GPIO 4, WS GPIO 5, SD GPIO 6, **L/R to GND**. Wires under ~20 cm.
- [ ] NeoPixel: DIN → 330 Ω → GPIO 7, VCC → 5V, GND → GND.
- [ ] (Optional) IR sensor: VCC 3V3, GND, OUT GPIO 1.
- [ ] C3 powered by USB (for now) or LiPo → TP4056 OUT+/OUT− → C3 5V/GND (100–470 µF capacitor only if it resets).
- [ ] The firmware session has flashed `voice_unit.ino`, its Gate F3 passed, and `UNOQ_IP` in the C3's `secrets.h` now points at the Uno Q. Tell me the C3's IP.

**After you reply, I will stop the app briefly and run `firmware/tools/check_voice_unit.py` on the Uno Q: it records 5 s of your voice to `check.wav` and cycles every light colour. Listen to the WAV and confirm it sounds clear.**

**Troubleshooting:** silence → L/R pin floating or wrong I2S pins. Loud hiss/clipping → adjust the bit shift/gain in firmware. NeoPixel dark → check 5V and data direction (DIN, not DOUT).

---

### Phase 7 — Real voice integration 🧠🔌

**Tasks**
- Run `firmware/tools/check_voice_unit.py` on the Uno Q (C3 already flashed by Session B).
- Switch the app to `UdpAudioSource` from the real C3. Retune `vosk_conf_threshold` with the real mic position (5–15 cm from the mouth).
- Verify the full light-state flow on the real NeoPixel.
- Optional: IR `shoot` on `:5007`.

**Acceptance**
- Real end-to-end: *"Camera, track person"* → follows → *"Camera, shoot"* → photo in gallery, with correct colours at every step, no laptop in the loop except SSH.

---

## 🛑 GATE C — Battery power and assembly

**Stop here. Print this checklist and wait for `GATE C DONE`:**

- [ ] Camera head on power bank A, one port: S3 via USB, servos from the S3's 5V pin.
- [ ] Uno Q on power bank B via a USB-C to USB-C cable rated 3A (bank must do 5V 3A / 15W).
- [ ] Voice unit on its LiPo + TP4056.
- [ ] Breadboard joints secured (hot glue/tape), mic and NeoPixel placed where they'd sit on the chair.
- [ ] Everything ran for 15 minutes on battery without resets (or tell me what reset).

---

### Phase 8 — Robustness and auto-start 🧠

**Tasks**
- `deploy/photo-rig.service`: systemd unit, `Restart=always`, starts after network; app sends `ready` light when up (and "Camera ready" TTS if speaker).
- Camera offline → light `reconnect`, retry with backoff, resume tracking automatically.
- Voice unit silent for > 5 s → log warning, keep running.
- Structured logging to `logs/`, rotate daily.
- `sleep` / `wake` commands; in SLEEP only `camera wake` is accepted.
- Optional: TTS replies via Piper or eSpeak if a speaker is attached.

**Acceptance**
- Power-cycle all three boards in any order: within ~60 s the rig shows `ready` and works with no one touching a laptop.

---

### Phase 9 — Demo mode and final checks 🧠

**Tasks**
- `--demo` flag: louder logging to console, larger confidence margin, gallery shows the latest photo full-screen on a phone.
- `tools/demo_checklist.md`: battery levels, hotspot on, IPs reachable, gallery open on the phone, backup video ready.
- Record a backup video of a full successful run.

**Acceptance**
- Three full demo runs in a row succeed, including one in a noisy spot.

---

## 🛑 FINAL GATE — Rehearsal

**Stop and ask the user to run the 2-minute demo script three times and report any failures.** Fix only what failed; no new features.

---

## 5. If time runs short (cut in this order)

1. IR backup trigger
2. `burst` and `timer`
3. Gallery page → just save photos to a folder
4. `track face`, `track dog`, `track cat` → keep only `track person`

The core loop — voice → tracking → photo — must survive every cut.
