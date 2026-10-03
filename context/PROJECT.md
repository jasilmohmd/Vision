# Project scope and architecture

Updated: 2026-10-04T00:14:29+05:30 (Asia/Calcutta).

## Purpose

Hands-free, wheelchair-mounted photography for a user who can move their head
and speak. Core flow: "Camera, track person" -> follows person -> "Camera,
shoot" -> saved photo -> phone gallery. Preserve the full planned scope unless
user explicitly approves a cut.

## Components

- Camera head: ESP32-S3 camera + pan/tilt servos, MJPEG stream, absolute moves,
  full-resolution capture held until acknowledgement.
- Voice unit: ESP32-C3 SuperMini + INMP441, NeoPixel, optional IR trigger.
- Brain: Arduino Uno Q Linux/Python; recognition, detection, tracking, control,
  photo storage, gallery. Use mocks on the laptop until hardware exists.
- Network: phone hotspot, fixed IPs to be confirmed; no runtime internet.

## Contracts to preserve

Camera HTTP: stream on :81/stream (320x240 MJPEG); HTTP :80 /move?pan=...&tilt=...
returns applied angles; /capture returns held JPEG; /ack frees it; /status
returns pan, tilt, uptime_s, held_photo and rssi. See source plan for exact JSON.

Voice UDP: C3 -> Uno Q :5005 raw signed little-endian 16-bit mono PCM, 16 kHz,
512 samples/1024 bytes per packet. Uno Q -> C3 :5006 ASCII light states.
Optional C3 -> Uno Q :5007 ASCII shoot. Gallery :8080.

Light states: ready, heard, tracking, nosubject, saved, error, reconnect, sleep.
Colour/flash timing is defined in the plan; do not alter it silently.
Wake word: camera. Commands: track person/face/dog/cat, stop tracking, left,
right, up, down, a bit left/right/up/down, centre, shoot, burst, timer, sleep, wake.

## Config defaults

IPs are examples, not confirmed hardware addresses: S3 192.168.43.101,
C3 .102, Uno Q .103. Detection every 5 frames; dead_zone .08; gain_deg 12;
max_step_deg 4; pan 10..170; tilt 40..140; both invert flags false;
Vosk confidence .7; centre timeout 1.5 seconds; photos_dir photos.
Relative photo paths resolve beside the selected YAML file. See ../config.yaml
for authoritative current values and ../app/config.py for typed validation.

## Implemented file map

- app/config.py: frozen Config dataclass, YAML loading, validation and path resolution.
- app/main.py: CLI flags/config validation only (Phase 0 runtime scaffold).
- app/vision/detector.py: YOLOv8/11 raw ONNX inference, letterboxing, class filter,
  NMS, clipped source-image boxes. Detection tuple: (class, confidence, x, y, w, h).
- app/vision/face.py: YuNet FaceDetectorYN, same tuple shape.
- app/vision/tracker.py: CSRT preferred/KCF fallback, detect every N frames or
  after failure, nearest prior box centre; initially choose highest confidence.
  Returns (box_or_None, offset_or_None), dx/dy in [-1, 1], right/down positive.
  Missing detection clears active tracking; prior box remains for association.
- tools/export_onnx.py: laptop-only static YOLOv8n FP32 320 export, opset 17.
- tools/download_models.py and .sh: official YuNet and small English Vosk download.
- tools/demo_vision.py: preview/console offsets, headless or frame-limited mode.
- tools/bench_vision.py: detector-only and detector+tracker FPS, cached frames,
  optional JSON report. tools/vision_common.py shares source/CLI/pipeline setup.
- tests/test_config.py, tests/test_vision.py: current automated coverage.
- requirements-laptop.txt: runtime + pytest; requirements-export.txt: laptop
  Ultralytics/ONNX export; requirements-unoq.txt: headless runtime only.

## Future-phase placeholders

app/vision/stream.py; app/voice/*; app/control/controller.py; app/io/*;
app/state.py; app/storage.py; app/gallery/server.py and templates/index.html;
tools/mock_camera.py, mock_voice_unit.py, check_camera.py, check_voice_unit.py;
firmware/*/*.ino; deploy/install_unoq.sh and photo-rig.service.
These are scaffold files, not functioning implementations.

## Local-only artifacts

models/yolov8n.pt, yolov8n.onnx, face_detection_yunet_2023mar.onnx,
vosk-model-small-en-us-0.15/, validation-bus.jpg and benchmark-webcam.json.
Models, generated media, environments and secrets must stay out of commits.
