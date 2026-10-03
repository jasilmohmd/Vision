# Phase 3 software: team testing handoff

Software is implemented and automated tests pass (98). Live spoken end-to-end
acceptance is unconfirmed. Sharing this version is for testing; Phase3 is not
marked complete and hardware gates remain in force. Physical hardware is tested
by the hardware team/Session B, not on the development laptop.

## Setup on a laptop

Pull main after the user pushes the software commit. From the repository root,
follow README Phase1/2 model setup and install requirements-laptop.txt. Local
.venv, models, photos and logs are ignored and are NOT included in the push.
ONNX YOLO export needs the separate requirements-export.txt environment; runtime
needs models/yolov8n.onnx, models/face_detection_yunet_2023mar.onnx and the Vosk
small English model. Do not install export dependencies on Uno Q.

Run `.\.venv\Scripts\python.exe -m pytest -q` and expect98 passing tests.
Use `.\.venv\Scripts\python.exe -m tools.demo_voice --list-devices` to select an
actual microphone. Device4 was the developer's boAt headset; choose the team's
own device ID rather than assuming4.

## Laptop mock acceptance (no physical NeoPixel required)

Run these in three terminals from the repository root:

```powershell
.\.venv\Scripts\python.exe -m tools.mock_camera
.\.venv\Scripts\python.exe -m tools.mock_voice_unit --device <MIC_ID>
.\.venv\Scripts\python.exe -m app.main --mock --preview
```

Wait for "Mock camera ready" before starting the app; webcam opening may take
several seconds. Wait for app "Ready". Say camera track person, move left/right,
then camera shoot. Check that crop/box follows, offsets/angles change, a newest
photo appears at http://localhost:8080, opening it shows full resolution, and
voice mock prints Light: saved (white flash). This last item is a software print,
not a requirement for a LED on the laptop. PressQ and Ctrl+C in mocks to stop.
Test camera burst (3 photos), camera timer (3 blue-flash prints then photo),
manual moves/centre, stop tracking, and sleep/wake as additional functional checks.

Return which checks passed, OS/mic device name, any traceback, and whether the
photo appeared. Avoid sharing private photos/audio or credentials in context.

## Real boards and gates

Session B/hardware team follows FIRMWARE_PLAN.md for physical INMP441/C3 audio,
NeoPixel, camera, servos and firmware checks. No firmware change is part of this
software commit. SOFTWARE_PLAN.md Gate0 must be explicitly satisfied before
Phase5 UnoQ deployment; real S3/C3 integration belongs to later gates/phases.
Current config IPs are examples, not confirmed addresses. Never guess pins or
replace IPs using an unverified interface address. Wire contract remains HTTP
control80/stream81, UDP audio5005/lights5006 and gallery8080.
