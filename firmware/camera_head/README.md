# S3 camera head (F2)

Board: user-confirmed ESP32-S3 CAM N16R8, OV3660. GPIO1 pan, GPIO2 tilt.
Camera signals match the supplied pinout and installed core ESP32S3_EYE entry;
PWDN/RESET are -1 in that entry and must be validated by camera initialization.
OPI PSRAM is required. F1 horns were aligned at 90/90; this sketch centres on
boot without an automatic sweep. There is no physical position feedback.

Copy ../secrets.example.h to secrets.h and configure Wi-Fi locally. Never commit
secrets.h. Production defaults to static addressing; user approved
WIFI_USE_DHCP=1 for the first bench check. All devices need the same 2.4 GHz
network without client isolation.

From repository root (portable toolchain used in this workspace):

```powershell
& ./firmware/.toolchain/arduino-cli.exe compile --fqbn 'esp32:esp32:esp32s3:PSRAM=opi,FlashSize=16M' --libraries ./firmware/.toolchain/user/libraries --build-path ./firmware/.build/camera_head ./firmware/camera_head
# Run upload only after Gate F2 confirmation; recheck the connected board/port.
& ./firmware/.toolchain/arduino-cli.exe upload --fqbn 'esp32:esp32:esp32s3:PSRAM=opi,FlashSize=16M' --port COM19 --input-dir ./firmware/.build/camera_head ./firmware/camera_head
& ./.venv/Scripts/python.exe firmware/tools/check_camera.py --ip <IP_FROM_SERIAL>
```

Serial115200 reports PSRAM, camera PID, IP, capture dimensions and errors.
HTTP control is port80; MJPEG is port81. Stream is QVGA320x240 JPEG quality12.
Video is capped at10fps to leave Wi-Fi airtime for control requests. Servo
targets and PWM updates have a separate mutex from camera frame acquisition;
a slow frame cannot hold the servo lock. Capture still freezes servo updates
while acquiring the photo. The checker also measures move latency and checks
commanded slew while an active stream is being consumed. Physical direction
and actual movement require observation; status angles are software commands.
Servo slew runs in a dedicated task, independently of Wi-Fi reconnect work in
the Arduino loop, with at most2degrees per20ms and no burst to catch up missed
periods. Status diagnostics move_received_ms, move_settled_ms and
move_in_progress measure command handling and completion of commanded PWM
updates, not physical servo position. Millisecond values wrap after49days.
Serial logs each accepted move with handler duration; speech recognition
latency on the laptop is outside this firmware's timing measurements.
Capture attempts QXGA2048x1536, then lower sizes if capture/allocation fails;
QXGA2048x1536 has decoded successfully in real bench and voice capture tests.
JPEG is retained until /ack; repeated /capture returns the same held image.
Capture freezes servo updates and excludes stream frame acquisition; stream
resumes at QVGA. Ordinary streaming uses a separate lock from servo control.
Video transmission also pauses while the JPEG is sent, leaving the servo mutex
released. Slow links can cause an app reader with a short timeout to reconnect.
Still responses use chunked HTTP transfer; JPEG content/type contract is unchanged.
Move targets clamp to pan10..170, tilt40..140, with2degrees/20ms slew.
The check uses only85..95degrees; it does not exercise mechanical end stops.

Only one stream viewer at a time. Close phone/browser/app stream before the
checker, and close the checker before starting the existing software app.
Live integration, Wi-Fi reconnect, prolonged operation and image quality are
hardware acceptance items; compilation alone does not establish them.

Observed DHCP bench IP: 192.168.29.231 (recheck Serial after reconnect).
After switching to the user's closer hotspot, Serial reported10.153.76.67
and RSSI-37dBm; laptop10.153.76.189. These are DHCP observations, not permanent
addresses. The checker passed streaming move ACKs in0.14..0.43s on that link.
OV3660 PID0x3660 and8MB PSRAM confirmed; QXGA2048x1536 capture decoded
successfully. Wi-Fi varied from roughly-50 to-79dBm; weak-link timeouts and
intermittent live video remain an acceptance issue. No static IP chosen yet.
User confirmed both servos physically move smoothly and centre in the direct
camera-firmware test (pan70..110, tilt75..105). HTTP readback remains commanded
angles, not a physical position sensor.

## Commit handoff - 2026-10-04
The final dedicated-servo-task build was previously flashed successfully.
Subsequent normal-software tests using the boAt headset produced up/down/left/
right movements and centre acknowledgements; the user confirmed all four
correct and smoothly centred. This is user-observed physical evidence, not
servo position feedback. Full F2 acceptance remains pending: intermittent
MJPEG timeouts, final-build capture/ack/stream recovery and longer stability
checks still need confirmation. C3 production voice firmware/F3 is deferred.
The software phrase-ending fix is a separate commit (64994af).
