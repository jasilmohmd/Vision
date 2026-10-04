# C3 voice unit (F3)

User-confirmed C3 SuperMini wiring: INMP441 SCK GPIO4, WS GPIO5, SD GPIO6,
VDD3V3, common GND, L/R grounded. External NeoPixel DIN GPIO7, GRB, brightness40.
F1 microphone conversion uses SHIFT14. Optional IR is omitted in this prototype.

Copy ../secrets.example.h to ignored secrets.h and enter Wi-Fi credentials
locally. UNOQ_IP is the audio receiver's confirmed address, not the C3 address.
Use the laptop destination for the standalone bench checker; use the Uno Q
destination for integration. Initial addressing may use WIFI_USE_DHCP=1 to read
the C3 address from Serial. Static production addressing requires confirmed
C3_IP/GATEWAY/SUBNET; never invent those values. No credentials belong in Git.

The audio task reads mono left-channel I2S at16kHz/32bits, clips after SHIFT,
and sends exactly512 signed16bit little-endian samples per UDP5005 datagram.
It drains audio while offline and does not replay a disconnected backlog.
The main loop independently receives UDP5006 light states, using timers rather
than blocking flash/blink delays. heard/saved last300ms; error gives two150ms
red flashes with150ms gaps, then the previous steady state. Wi-Fi down overrides
the display with blinking purple. Unknown/malformed light messages are ignored.
Automatic reconnect remains enabled; manual retries wait45s for an in-progress WPA3 handshake. Serial prints disconnect reason, IP, reset reason, packet send counts,
send errors and signal level. Successful UDP send is not receiver acknowledgement.

From repository root, with the portable toolchain and installed libraries:

```powershell
& ./firmware/.toolchain/arduino-cli.exe compile --fqbn 'esp32:esp32:esp32c3:CDCOnBoot=cdc' --libraries ./firmware/.toolchain/user/libraries --build-path ./firmware/.build/voice_unit ./firmware/voice_unit
# Upload only after explicit user authorization and verifying the C3 port.
& ./firmware/.toolchain/arduino-cli.exe upload --fqbn 'esp32:esp32:esp32c3:CDCOnBoot=cdc' --port COM18 --input-dir ./firmware/.build/voice_unit ./firmware/voice_unit
```

Read Serial115200 for the DHCP address. PortCOM18 is the observed C3 connection,
not a guaranteed permanent port. If USB upload fails, use the already-tested
BOOT/reconnect procedure and retry only after the user confirms readiness.

Run firmware/tools/check_voice_unit.py on the configured audio receiver:

```powershell
./.venv/Scripts/python.exe firmware/tools/check_voice_unit.py --ip <C3_IP>
```

Stop other UDP5005 receivers first. This intentionally records five seconds of
microphone audio locally into ignored firmware/.build/voice_checks/check.wav
and cycles all light states. Get the user's readiness before recording/colour
checks. Raw packets have no sequence header, so packet loss is only estimated
from expected rate, never exactly measured. Listen to the WAV and observe the
physical colours before claiming acceptance. Compilation/boot alone does not
establish microphone quality, colour accuracy or end-to-end voice recognition.

Earlier build2026-10-04: compiled and flashed999581 program bytes/37976 globals,
verified C3 COM18/ESP32-C3 AZrev1.1. Explicit SAE-both negotiation is enabled.
Wi-Fi authentication still expires on the tested WPA3 hotspot; no C3 DHCP IP
confirmed yet. Packet, microphone quality and physical light checks are pending.
Try the existing hotspot in2.4GHz/WPA2-Personal with its unchanged current
password before additional firmware changes; this is a diagnostic next step,
not a claim that the ESP32-C3 lacks WPA3 support. Confirm actual network details
before changing destinations or declaring acceptance.

For C3 headers, select C/C++: Select a Configuration -> ESP32-C3 SuperMini in
VS Code/Cursor, then reload the editor window. The workspace provides separate
S3 and C3 compiler/SDK paths and associates .h/.ino with C++; pragma once itself
is valid and the full C3 sketch compiled successfully. Keep headers' board
configuration matched to the current sketch. Editor paths are validated locally;
visual diagnostic clearance still requires checking the editor.

## Latest Wi-Fi troubleshooting

The default-power Wi-Fi-only sketch detected the WPA2 hotspot at-47dBm but
failed to connect. The diagnostic capped transmit power at8.5dBm (ESP-IDF34)
and confirmed DHCP10.153.76.243, gateway10.153.76.224, RSSI around-43dBm.
Production now applies the same cap after starting STA, before connecting.
It compiled999841 program bytes/37976 globals and uploaded with verified hashes.
After restoration,10.153.76.243 answered two pings and its neighbour entry matched
C3 MAC44:b1:76:17:f5:7c. Serial showed packet-send counts240/553/866; five initial
send errors did not increase in those subsequent reports. This establishes
connection and sender activity, not receipt or microphone quality.
This is an observed working setting for this board/network, not proof of an
antenna/power fault or a universal fix. Production connectivity and F3 audio/
light acceptance must be checked separately. Diagnostic source is preserved
under ../bench/wifi_diagnostic; credentials remain ignored.
