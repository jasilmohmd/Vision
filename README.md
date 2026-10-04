ï»¿# Hands-free photography rig

Follow SOFTWARE_PLAN.md for the interface contract and phase requirements.
Read [context/README.md](context/README.md), [context/HANDOFF.md](context/HANDOFF.md)
and STATUS.md before resuming work. Update context before every commit, as
required by AGENTS.md. Future-phase files are labeled placeholders.

## Phase 0 setup (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install pyyaml pytest
.\.venv\Scripts\python.exe -m app.main --help
.\.venv\Scripts\python.exe -m app.main --config config.yaml --check-config
.\.venv\Scripts\python.exe -m pytest
```

Only PyYAML and pytest are needed for Phase 0. The requirements files list
later laptop and Uno Q dependencies. Ultralytics is laptop-only for export;
never install it or PyTorch on the Uno Q.

Use --check-config to validate configuration without starting devices. Phase 3
adds --mock, --mic laptop|udp (default udp), --preview and --seconds.
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


## Phase 2 voice (PowerShell)

```powershell
.\.venv\Scripts\python.exe -m pip install vosk sounddevice
.\.venv\Scripts\python.exe -m tools.demo_voice --list-devices
.\.venv\Scripts\python.exe -m tools.demo_voice --list-commands
.\.venv\Scripts\python.exe -m tools.demo_voice --mic laptop --device 3
```

Device 3 was this laptop's AMD microphone array during development; the default
input was a virtual Elgato line. Check device IDs on each machine and choose the
actual microphone; this does not change the system default. Ctrl+C stops the demo.
Use --seconds 30 for a finite run. Events are printed as JSON: heard, command
(with a typed action/target/direction/small-step flag), or low_confidence.
The standalone Phase 2 demo prints events only. The Phase 3 app applies commands.

Vosk uses all 19 exact "camera <command>" phrases plus [unk]. A final command
requires the leading wake word and confidence at or above config.vosk_conf_threshold
for every word, including "camera". Empty/[unk] results are ignored; other rejected
non-empty results emit low_confidence. Partial "camera" emits heard once per utterance.

Keep quiet for the two-second startup microphone sample, then wait for Ready.
Speech is separated after about 0.7 seconds of quiet, retaining a short lead-in
so the wake word is not cut off. Say one complete command at a time and pause
for its response. Commands still require the full wake phrase and word
confidence threshold. Closing the app discards unfinished speech rather than
turning it into a command. Loud startup samples are bounded; actual headset,
quiet speech and background-chatter reliability still need live checks.

Run the guided acceptance check from 0.5-1 m away:

```powershell
.\.venv\Scripts\python.exe -m tools.demo_voice --device 3 --checklist --report logs/phase2-voice-check.json
```

Say each prompted phrase, pause for its command event and repeat if rejected.
After all 19 commands, talk normally for the prompted 20-second background test,
without saying command phrases. It should produce no command events. The summary
records coverage and false commands, not raw audio or chatter transcripts. A
passing summary still needs confirmation that the distance and chatter conditions
were actually exercised. No recording is saved. Ctrl+C produces an incomplete
summary if you stop early. --background-seconds can adjust the test duration.

UDP mode is also runnable without real hardware:

```powershell
.\.venv\Scripts\python.exe -m tools.demo_voice --mic udp --seconds 30
```

It binds config.audio_port (5005 by default) on 0.0.0.0. Each datagram must contain
512 mono s16le samples (1024 bytes) at 16 kHz. A bounded arrival-order queue buffers
jitter, drops old backlog and inserts 32 ms silence chunks for missing playout slots.
The raw contract has no sequence numbers/timestamps, so it cannot reconstruct packet
reordering or exact losses. Before any valid packet, read_chunk returns empty on
short timeouts. Closing the source releases its receiver thread/socket.

API references: [Vosk microphone example](https://github.com/alphacep/vosk-api/blob/master/python/example/test_microphone.py),
[Vosk recognizer API](https://github.com/alphacep/vosk-api/blob/master/python/vosk/__init__.py),
[sounddevice raw streams](https://python-sounddevice.readthedocs.io/en/latest/api/raw-streams.html).


For no-response diagnosis, demo_voice --levels prints input RMS/peak once per
second and the selected input name. Verify --list-devices after connecting a
headset; IDs can change. Nonzero changing levels show capture activity, not
successful recognition. Headset tests are diagnostic and do not by themselves
replace the planned laptop-microphone acceptance at 0.5-1 m.


## Phase 3 mock rig (three PowerShell terminals)

Install laptop dependencies with `.\.venv\Scripts\python.exe -m pip install -r requirements-laptop.txt`.
Models must already exist locally (see Phase 1/2 setup above). From the repository
root, run one command in each terminal. Start the camera mock first and wait
for "Mock camera ready" before starting the app (webcam startup can take a while):

```powershell
.\.venv\Scripts\python.exe -m tools.mock_camera
.\.venv\Scripts\python.exe -m tools.mock_voice_unit --device 4
.\.venv\Scripts\python.exe -m app.main --mock --preview
```

Device 4 is the verified boAt headset on this laptop; check `tools.demo_voice
--list-devices` before using another computer. The voice mock sends live 16 kHz
mono s16le audio in 1024-byte UDP packets, and prints light states/colours. The
app uses UDP audio by default; `--mic laptop --device N` bypasses the voice mock
for diagnosis. It does not change the system microphone setting.

Wait for "Ready", say **camera track person**, then move left/right. The camera
mock shifts its 320x240 crop inside the full webcam image; the preview shows the
box, offsets and pan/tilt. A narrow crop may require standing farther back or
moving into its initial centre. Say **camera shoot**, check the `saved` white
flash in the voice console, and open http://localhost:8080. Tap the newest photo
to open its full resolution. The gallery refreshes when a new photo is saved.
Press Q in the preview, then Ctrl+C in both mock terminals.

Manual direction/small-step/centre commands work while idle or tracking. Stop
tracking returns to idle; sleep ignores commands until camera wake. Burst saves
three photos about 400 ms apart after centering; timer flashes blue three times
then shoots. Missing subjects produce nosubject after two seconds. Movement is
limited to ten requests per second and configured angle limits. Captures wait
for centering or the configured timeout, save before ACK, and retain camera
photos if saving fails. A failed ACK is retried before another capture.

`photos/` (including index metadata), model files and diagnostic logs are Git
ignored. Runtime needs write access to photos_dir. Only one app instance may
write the same photo directory. Optional `speaker_enabled: true` uses eSpeak NG
or eSpeak when installed; disabled/missing synthesis is a no-op.

For headless diagnostics, camera `--synthetic` or `--image path.jpg` avoids the
webcam; voice `--silence` avoids microphone access; all three support --seconds.
The mock HTTP/UDP ports match the shared contract exactly. `--mock` only changes
camera/light destination addresses to localhost; real board/network integration
waits for the plan's hardware gates. Firmware is owned by separate Session B.
