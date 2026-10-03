# Verification and runnable commands

Updated: 2026-10-04T00:14:29+05:30 (Asia/Calcutta).

## Latest executed checks (2026-10-04)

- pytest: 23 passed (15 Phase 0/config tests, 8 vision tests).
- CLI help: app.main, tools.demo_vision, tools.export_onnx, tools.download_models passed.
- YOLO export: static input (1,3,320,320), output (1,84,2100), opset 17; succeeded.
- Real inference on official Ultralytics bus sample: 3 people, YuNet 2 faces.
- Headless webcam: 10 person frames and 3 face frames, boxes/offsets printed.
- pip check: no broken requirements.
- git diff --check: passed after Phase 1 changes.

Automated tests cover config defaults/overrides and invalid values; RGB
letterboxing, inverse coords, class filter/NMS, clipping, offset direction and
bounds; detection interval, nearest-box identity, failure/reacquisition,
real CSRT/KCF on a textured frame, fallback and missing-model setup errors.
They do not prove tracking smoothness while a person moves.

## Benchmark (2026-10-04)

Laptop CPU, webcam source 0, person target, CSRT, 320x240, detection interval 5.
100 cached frames; acquisition/model load excluded; detector warmed up:

- Detector-only 68.39 FPS; detector+tracker 19.13 FPS.
- Detected 100/100; tracked 100/100.
- Local JSON: ../models/benchmark-webcam.json (ignored).
- Earlier 30-frame run: 66.52/38.04 FPS, detected 4/30, tracked 7/30; do not
  use its higher tracking FPS as the normal present-subject benchmark.

## Current-session docs verification

- Context file inventory, relative Markdown links and git diff --check verified.
- No application tests rerun for this documentation-only change. Last 23-test
  result above remains the latest application evidence.

## Resume commands (PowerShell from repo root)

```powershell
git status --short
git log -3 --oneline
.\.venv\Scripts\python.exe -m app.main --help
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m tools.demo_vision --target person
.\.venv\Scripts\python.exe -m tools.bench_vision --frames 100 --output models/benchmark-webcam.json
```

For another camera use --source 1; for a recording use --source path/to/video.mp4.
Demo --target face|dog|cat selects the subject; --tracker KCF changes tracker.
Use --headless --frames 100 for finite console-only output. Q/Escape closes GUI.

## Fresh clone setup

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install pyyaml pytest "opencv-contrib-python>=4.10,<5" onnxruntime numpy
.\.venv\Scripts\python.exe -m tools.download_models
python -m venv .venv-export
.\.venv-export\Scripts\python.exe -m pip install -r requirements-export.txt
.\.venv-export\Scripts\python.exe -m tools.export_onnx
```

The full laptop requirements include later-phase runtime libraries; the command
above installs what Phase 1 currently needs. Do not install requirements-export
into Uno Q or combine base/contrib OpenCV distributions in the runtime venv.
Future Uno Q installation is Phase 5; do not perform it during laptop phases.

## Phase 1 visual acceptance - passed (2026-10-04)

Visible person preview launched at user request, with up to 1800 frames.
Tracked boxes and changing offsets appeared in numerical logs, with no errors
at inspection. After moving left/right and closer/farther in the preview, user
reported: "Yes?tracking is smooth and offsets change". Human acceptance passed.
Numeric logs remain in ignored logs/; no camera images were saved for this check.

No application code changed since the 23-test pass. Documentation/context
updates were checked with git diff --check before the Phase 1 commit.
No remaining Phase 1 acceptance checks. Phase 2 has not started.
