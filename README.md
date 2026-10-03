# Hands-free photography rig

Follow SOFTWARE_PLAN.md for the interface contract and phase requirements.
Read [context/README.md](context/README.md), [context/HANDOFF.md](context/HANDOFF.md)
and STATUS.md before resuming work. Update context before every commit, as
required by AGENTS.md. Future-phase files are labeled placeholders.

## Phase 0 setup (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install pyyaml pytest
.\.venv\Scripts\python.exe -m app.main --help
.\.venv\Scripts\python.exe -m app.main --config config.yaml
.\.venv\Scripts\python.exe -m pytest
```

Only PyYAML and pytest are needed for Phase 0. The requirements files list
later laptop and Uno Q dependencies. Ultralytics is laptop-only for export;
never install it or PyTorch on the Uno Q.

The CLI supports --config, --mock, and --mic laptop|udp. In Phase 0 it validates
configuration and exits. Hardware, mocks, voice, and gallery runtime are pending.
Relative photos_dir values resolve beside the selected YAML file. IP defaults
are examples awaiting confirmation at Gate 0. Ports follow the source contract.


## Phase 1 vision (PowerShell)

The laptop runtime uses **opencv-contrib-python** for CSRT/KCF, replacing the
base OpenCV package from the original scaffold. Uno Q requirements use its
headless contrib equivalent. Install one cv2 distribution per environment:
[OpenCV package guidance](https://pypi.org/project/opencv-contrib-python/).

```powershell
.\.venv\Scripts\python.exe -m pip install "opencv-contrib-python>=4.10,<5" onnxruntime numpy
.\.venv\Scripts\python.exe -m tools.download_models
```

YOLOv8n exports at 320 pixels with a static FP32 batch-one input and raw outputs
(no embedded NMS). Export dependencies live in a separate laptop environment
because Ultralytics depends on base OpenCV:

```powershell
python -m venv .venv-export
.\.venv-export\Scripts\python.exe -m pip install -r requirements-export.txt
.\.venv-export\Scripts\python.exe -m tools.export_onnx
```

The downloader fetches official YuNet and Vosk small English models. The shell
wrapper is `bash tools/download_models.sh` (set PYTHON to your venv Python on
Linux). Models and benchmark reports live in ignored models/; downloads need
internet, but runtime inference runs locally using ONNX Runtime and OpenCV.

```powershell
.\.venv\Scripts\python.exe -m tools.demo_vision --target person
.\.venv\Scripts\python.exe -m tools.bench_vision --frames 100 --output models/benchmark-webcam.json
.\.venv\Scripts\python.exe -m pytest
```

Move across the webcam view and confirm the box follows smoothly. The preview
shows the target and normalised dx/dy; the console prints the box and offset
per frame. Press Q or Escape to exit. Positive dx is right, positive dy is down,
and (0, 0) means centred; absent targets return (None, None).

Use --target face|dog|cat, --tracker KCF, --source 1 for another webcam, or
--source path/to/video.mp4. A video file is useful for repeatable benchmarks.
Demo --headless --frames 100 prints offsets without opening a window.
Benchmarks exclude acquisition time, preload the same 320x240 frames for both
runs, and report detected/tracked frame counts; a run without a target does not
measure normal tracking performance. CSRT is preferred with KCF fallback;
detection refreshes every configured N frames and immediately after a failure.
New boxes associate with the closest previous box centre; confidence chooses
the initial target. A missing detection clears the active target.

Ultralytics YOLOv8 weights are AGPL-3.0, as noted in SOFTWARE_PLAN.md.
Model/export references: [Ultralytics ONNX export](https://docs.ultralytics.com/modes/export),
[OpenCV YuNet](https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet),
[Vosk models](https://alphacephei.com/vosk/models),
and [FaceDetectorYN API](https://docs.opencv.org/4.x/df/d20/classcv_1_1FaceDetectorYN.html).
