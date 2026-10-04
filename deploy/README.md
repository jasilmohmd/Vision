# Phase 5: Uno Q against laptop mocks

This phase deploys the Linux software and models and measures Uno Q performance.
No S3/C3 addresses, firmware flashing or systemd service are required. Physical
integration begins only at later gates. Service/autostart work belongs to Phase8.

## Known network and login

User supplied Uno Q LAN IP192.168.29.199 and confirmed SSH/hotspot readiness.
Laptop Wi-Fi IP192.168.29.58 was observed locally when preparing this phase.
Recheck both after changing networks. User confirmed SSH username arduino; no password is stored in scripts or context. The laptop and Uno Q must be mutually reachable,
not merely have access to the same hotspot; disable hotspot client isolation if
it prevents this. Keep host-key verification enabled.

## Copy and install from PowerShell

From the repository root:

```powershell
.\deploy\copy_to_unoq.ps1 -User arduino -UnoqIp 192.168.29.199 -LaptopIp 192.168.29.58
```

This packages runtime source and the three required models, copies two archives
via scp to ~/Vision, then runs the installer over SSH. SSH/sudo prompts are entered
in your own terminal, never in chat. Existing photos and normal config.yaml are
preserved. Generated config.phase5.yaml intentionally points both mock endpoints
at the laptop IP; do not use it as a real-board config. Archives/source/model
checksums and generated local config are in ignored logs/. Firmware, photos,
export .pt weights, virtual environments and secrets are excluded from transfer.

`-SkipInstall` only copies/extracts. On the Uno Q, install/check separately:

```bash
cd ~/Vision
bash deploy/install_unoq.sh
# Already prepared OS packages: add --skip-apt
# Recheck existing runtime without installs:
bash deploy/install_unoq.sh --check-only
```

Installer creates project .venv, installs headless contrib/ORT/Vosk/Flask etc.,
verifies models and writable storage, and writes logs/phase5-preflight.json.
It installs missing Debian python3/venv/pip/libgomp/libatomic packages if needed.
No export dependencies on Uno Q. Missing binary wheels stop installation rather
than build OpenCV/ORT from source. Record architecture/Python and the exact error
if this happens. Setup downloads packages; runtime model inference works offline.
Use a different -RemoteDirectory if ~/Vision is used by another deployment.

## Run laptop mocks

On the laptop, in separate terminals, select your actual microphone device ID:

```powershell
.\.venv\Scripts\python.exe -m tools.mock_camera --bind 192.168.29.58
.\.venv\Scripts\python.exe -m tools.mock_voice_unit --host 192.168.29.199 --bind 192.168.29.58 --device 4
```

Device4 was the boAt headset on this laptop; confirm with demo_voice --list-devices.
Wait for camera ready before running the Uno Q app. Allow this project Python
through Windows Firewall for the shared network if prompted. Required traffic:
Uno Q -> laptop TCP80/81 and UDP5006; laptop -> Uno Q UDP5005; phone -> Uno Q TCP8080.
The default camera mock binds localhost, so --bind is essential for LAN testing.
Stop the laptop app; the app now runs only on Uno Q and laptop only runs mocks.

## Run app on Uno Q and accept from phone

```bash
cd ~/Vision
.venv/bin/python -m app.main --config config.phase5.yaml --mic udp
```

Do NOT add --mock here: localhost would mean the Uno Q, not the laptop. Do NOT
add --preview to the headless runtime. Say camera track person and move inside
the laptop webcam view; view http://192.168.29.58:81/stream from a laptop browser
to observe the crop. Say camera shoot and confirm saved in the mock light console.
From a phone on the same network, open http://192.168.29.199:8080 and confirm the
newest photo opens at full resolution. Stop the app with Ctrl+C before benchmarking.
No physical NeoPixel is needed for the mock's printed light message.

## Benchmark on Uno Q

With laptop camera mock still running and a person visible in its crop:

```bash
cd ~/Vision
.venv/bin/python -m tools.bench_vision --config config.phase5.yaml --source http://192.168.29.58:81/stream --target person --frames 100 --output logs/phase5-benchmark.json
```

Record detected/tracked frames and detector-only/detector+tracker FPS, architecture
and Python/library versions from preflight. This benchmark excludes acquisition
and preloads frames; it is CPU processing FPS, not end-to-end network throughput.
Do not treat a no-subject run as a representative tracking benchmark.
If tracking is slow, benchmark --tracker KCF and start app --tracker KCF, or raise
detect_every_n_frames in config.phase5.yaml and measure again. Changing static
ONNX input size requires a fresh laptop export; never install export tools on Uno Q.

Return preflight, benchmark numbers, phone-gallery and voice/tracking/photo results.
Update STATUS/context with actual results before committing. Phase5 remains
incomplete until these checks pass. Stop at SOFTWARE_PLAN GateA afterward.

References: [Arduino Debian/SSH guide](https://docs.arduino.cc/tutorials/uno-q/debian-guide/),
[ONNX Runtime Python platforms](https://onnxruntime.ai/docs/get-started/with-python.html).

## Current prepared USB test deployment (2026-10-04)
The current DHCP observations are Uno Q10.153.76.45 and laptop10.153.76.189.
Recheck these before testing; the earlier addresses above are historical examples.
User installed ADB separately and confirmed USB device serial662499217. The
latest source was copied over USB into /home/arduino/Vision-phase5-20261004,
with its own models/config/photos and the existing ~/Vision runtime venv.
Original ~/Vision is retained. Runtime/model preflight passed; live acceptance
and benchmark are deferred until the user is ready. App Lab is not required
for this direct Linux Python workflow.

When ready, start the camera/voice mocks on the laptop using the current IPs
and confirmed headset device. From the user's Platform Tools directory:

```powershell
.\adb.exe -s 662499217 shell -t "cd /home/arduino/Vision-phase5-20261004 && .venv/bin/python -m app.main --config config.phase5.yaml --mic udp"
```

Keep this terminal open. Once a photo is saved, the phone gallery is
http://10.153.76.45:8080 on the same network. After stopping the app, keep the
laptop camera mock running and benchmark:

```powershell
.\adb.exe -s 662499217 shell -t "cd /home/arduino/Vision-phase5-20261004 && .venv/bin/python -m tools.bench_vision --config config.phase5.yaml --source http://10.153.76.189:81/stream --target person --frames 100 --output logs/phase5-benchmark.json"
```

Do not report Phase5 passed from preflight alone. SSH also listens on port22,
but the new IP's host key has not yet been enrolled in the laptop's SSH client;
use the trusted USB connection to verify it rather than disabling verification.
