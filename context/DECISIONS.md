# Decisions and constraints

Updated: 2026-10-04T00:14:29+05:30 (Asia/Calcutta).

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

Do not guess exact S3 board camera pin maps. At Gate 0 obtain board model and
confirm pan GPIO1/tilt GPIO2 (or user replacements), C3 mic GPIO4/5/6,
NeoPixel GPIO7, optional IR GPIO1, hotspot setup and Uno Q IP.
Firmware pin comments are plans, not confirmations. No board-specific pin map
or hardware resume phrase has been supplied.

## Runtime and security boundaries

Never install PyTorch or Ultralytics on Uno Q. Firmware hotspot credentials
belong in ignored secrets.h, with a non-secret example when Phase 4 arrives.
Do not put credentials or recordings/photos in context records. No hardware
flashing, deployment, or remote publish has occurred as part of Phase 1.
