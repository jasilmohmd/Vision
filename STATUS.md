# Project status

- Phase 0: complete and committed (de1dfad).
- Phase 1: complete; automated checks, webcam benchmark and visual acceptance passed.
- Updated: 2026-10-04T00:14:29+05:30 (Asia/Calcutta).

## What works

- YOLOv8n exported on the laptop to models/yolov8n.onnx: static FP32 input
  (1, 3, 320, 320), raw output (1, 84, 2100), opset 17, no embedded NMS.
- ONNX Runtime detector with RGB letterboxing, class filtering, NMS and
  inverse-coordinate mapping/clipping. No PyTorch runtime imports.
- YuNet FaceDetectorYN with matching detection tuples.
- CSRT tracking with KCF fallback, per-frame updates, configured detection
  interval, immediate re-detection after failure and nearest-box association.
- Per-frame target box or None, with normalised dx/dy (positive right/down).
- Webcam/video demo with overlay, printed offsets and headless option.
- Detector-only and detector+tracker benchmark with optional JSON report.
- Cross-platform model downloader and shell wrapper. YuNet and Vosk small
  English models downloaded locally. Models are ignored by Git.
- Runtime uses opencv-contrib-python (headless contrib for Uno Q) so CSRT/KCF
  are available. Export dependencies are separate in requirements-export.txt
  to prevent simultaneous installation of conflicting cv2 distributions.

## Verification

- Python 3.13.5, OpenCV contrib 4.14.0, ONNX Runtime 1.30.0, NumPy 2.5.3.
- python -m pytest: 23 passed (15 config/CLI tests plus 8 vision tests).
- Vision tests cover letterboxing, inverse box mapping, class filtering/NMS,
  clipping, offset signs/bounds, detection cadence, identity association,
  failure recovery, real CSRT/KCF initialization, fallback and missing models.
- YOLO export succeeded; official bus sample yielded 3 people with YOLO and
  2 faces with YuNet. Both real models loaded and ran successfully.
- Webcam headless smoke: person tracking over 10 frames, face tracking over
  3 frames; boxes and offsets printed.
- Main, demo, export and download CLI help checks passed.
- pip check: no broken requirements. git diff --check: passed.

## Laptop webcam benchmark

Source 0, person, CSRT, 320x240, detect_every_n_frames=5; CPU processing only,
excluding camera acquisition and model load (same cached frames for both runs):

- Frames: 100.
- Detector-only: 68.39 FPS.
- Detector+tracker: 19.13 FPS.
- Detected frames: 100/100.
- Tracked frames: 100/100.
- Local report: models/benchmark-webcam.json (Git ignored).

## Pending and known issues

- Visible person demo passed on 2026-10-04. User confirmed smooth tracking
  and changing offsets. Numerical logs showed tracking without errors. Command:
  .\.venv\Scripts\python.exe -m tools.demo_vision --target person
- Phase 1 acceptance is complete. Context updated before preparing commit:
  phase 1: laptop vision and tracking. Resolve the resulting hash from git log.
- Phase 2 and later have not started. Their files remain placeholders.
- Camera board pin maps and actual network addresses remain unconfirmed.
- Normal sandbox command runner still fails during setup; verification and
  file changes ran through approved escalated commands.

## Licence

Ultralytics YOLOv8 weights are AGPL-3.0, as flagged in SOFTWARE_PLAN.md.
Ultralytics/PyTorch were used on this laptop only for export. The deployed
vision code uses ONNX Runtime/OpenCV; never install export dependencies on Uno Q.

## Durable session handoff

- context/README.md indexes the handoff, project scope, decisions, progress and
  verification records. Read context/HANDOFF.md first in a new session.
- User requires context updates BEFORE EVERY commit; AGENTS.md records this
  mandatory rule, including documentation-only commits.
- Context files and guidance are included with the prepared Phase 1 commit.
- No remaining Phase 1 acceptance blockers; Phase 2 has not started.
