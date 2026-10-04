# Experimental switchable C3 transport

User requested a BLE trial while retaining Wi-Fi/UDP selection on 2026-10-04.
This authorizes the narrow C3 transport prototype/build/upload in this session;
other firmware ownership and hardware gates remain with Session B. This document
is the trial specification, not a replacement for SOFTWARE_PLAN.md section2.
The existing UDP contract and default mode remain unchanged. Camera stays Wi-Fi.

## Selecting modes

Close the app/audio probes and serial readers before changing board mode. From
project root PowerShell, tools/switch_voice_transport.ps1 -Transport ble or udp
verifies identified C3 COM18/MAC44:b1:76:17:f5:7c, compiles and flashes selected
mode. Same normal partition scheme; this trial switches by reflash, not live.
VOICE_TRANSPORT_BLE defaults0; BLE mode uses compiler.cpp.extra_flags define1.
Builds are isolated firmware/.build/voice_unit_ble and voice_unit_udp.

Uno Q: optional requirements-ble.txt (Bleak3.0.2). App --mic udp remains default;
--mic ble requires --ble-address from actual C3 serial output/verified scan.
One BLE connection supplies both INMP441 audio and NeoPixel light writes. The
laptop/Bluetooth headset is not the audio source. All processing stays Uno Q.

Do not launch existing full-system config on router until S3 and C3 addresses
are verified/updated: it still has old hotspot addresses. BLE avoids C3 IP
routing but camera must have current S3 IP. Current Uno Q192.168.1.99 and last
verified S3192.168.1.122; C3 router DHCP still unknown.

## Trial GATT framing

Name Vision-C3-Voice; service9b930001-8a97-4ed0-9f08-42d26e75baf1.
Audio notify9b930002-8a97-4ed0-9f08-42d26e75baf1: uint32 little-endian
first-sample index followed by even PCM payload (s16le16kHzmono). Up to240PCM
bytes plus4index, limited by actual peer MTU. MTU247 requested. Gap/duplicate/
wrap detection occurs on Uno Q; reconnect drops old audio, bounded buffer avoids
backlog. Firmware drains microphone while disconnected, never replays old audio.

Light write9b930003-8a97-4ed0-9f08-42d26e75baf1: existing ASCII states.
Callback validates and queues requests; existing loop renders pixels/flash logic.
No IR; pins4/5/6 and pixel7, SHIFT14 preserved. UDP firmware code remains present
and default; BLE build skips Wi-Fi initialization. Trial GATT is unpaired and
requires later product/security/contract review before adoption.

## Acceptance probe

Uno Q from /home/arduino/Vision:
.venv/bin/python -m tools.check_voice_transport --transport ble --address <verified-address> --seconds 30 --lights --report logs/ble-voice-check.json
UDP selectable with --transport udp
and a verified --config. Probe does not move/capture or save private audio.
BLE delivery gate: >=14400 actual samples/s, no missing/malformed samples and
max notification gap<100ms, no buffer drops or inserted playout padding. This is a trial threshold, not full voice acceptance.
Light writes only count as requests; physical colour confirmation required.
Full Vosk commands, camera flow and standalone stability still need acceptance.

## Results and current state

BLE build784555 bytes program/26472 globals; UDP1000105/37976. Both compile
and upload hashes verified. Actual BLE address44:B1:76:17:F5:7E scanned by Uno Q
atRSSI-52. BLE -> UDP -> BLE switching verified using the helper; currentBLE.
UDP boot confirmed existing destination192.168.1.99 and ports5005/5006, but
Wi-Fi authentication still fails. Switching preserves availability, not a claim
that the existing Wi-Fi fault is repaired. Current Session A ownership instruction
forbids further firmware changes; hand off firmware work to Session B.

Initial BLE30s failed (1752missing/maxgap126ms). MTU247 gating/short connection
interval40s failed (1728missing). Bounded retry of rejected notification enqueue
then delivered640272samples/40.015s with0missing/maxgap66ms. This passed the older
gate before consumer padding was measured. Serial-closed follow-up40.021s had
0missing/maxgap67ms but272samples padding: strictfail. Four-chunk startup buffer
(128ms vs96ms) then eliminated consumer underflow in final40.019s:
640480samples,16004.26/s,0missing/invalid/outoforder/bufferdrops/padding,
maxgap101ms. Unchanged strict <100ms notification timing gate FAILED narrowly.
Final report logs/ble-voice-buffered-check.json; no saved private audio.

Full local suite142 passed in9.73s; focused BLE6 passed in0.30s. Includes sequence
wrap/gaps, malformed watchdog, reconnect flush, bounded gaps/close wakeup,
partial audio preservation/padding metrics and reconnect during paced read.
Uno Q optional wheels Bleak3.0.2/dbus-fast5.2.0 installed offline overADB after
PyPI DNS/network failure. Firmware uses core3.3.11 NimBLE; callback handling
supports the installed stack. Normal partition unchanged; no pins/SHIFT changes.

Previously requested light writes are not physical acceptance: user did not watch
NeoPixel. All colors unverified. Concurrent S3 probe returned0frames withstatus/
stream timeout (logs/ble-concurrent-camera-check.json). Full Vision app stopped.
No full Vosk command, camera flow, standalone stability or phase completion.
Next: Session B timing/camera investigation, repeat strictBLE probe, physically
confirm colors, then integration with verified config. User subsequently authorized commit/push; see newest HANDOFF publication entry.
