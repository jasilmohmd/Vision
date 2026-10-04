# C3 audio delivery: suspected blocking USB status logging

Session A diagnosis, 2026-10-04. Firmware implementation remains Session B owned.

Observed production firmware: `voice_unit/voice_unit.ino` prints packet counters
with `Serial.printf` from `audioTask()` every10s (around line116). Build is
ESP32-C3 with CDCOnBoot=cdc, installed Arduino ESP32core3.3.11.

Controlled observations with current board/IPs and unchanged firmware:
- Hotspot awake/nearby, serial closed:533packets/20.02s,26.62/s,maxgap2.374s.
- Simultaneous serial reader open and receiver40s:1258packets/40.056s,
  31.41/s,maxgap0.555s. C3 counters at10.042/20.040/30.088/40.091s were
  79816/80129/80442/80755 (313between reports),send_errors7026 unchanged.
- Close serial reader and repeat:576packets/20.024s,28.77/s,maxgap2.265s.
- No malformed packets or kernel UDP receive-buffer/checksum errors in these runs.
- UnoQ power-save off earlier did not resolve the2s pauses; original ON restored.

Installed `cores/esp32/HWCDC.cpp` has tx_timeout_ms=100 and
max_consec_timeouts=20; write() comments describe host backpressure even with
USB physically connected. Logging from the producer task plus matching pause
lengths and open/closed comparison strongly support USB logging as cause.
This is an inference, not a completed firmware fix. Exact packet loss cannot be
reconstructed because contract packets have no sequence numbers.

Session B action: make status/debug output nonblocking so audio never waits for
USB host consumption. Review all Serial calls (audio error/counters, loop/light/
disconnect reporting); choose correct APIs for this exact core and keep the
16kHz/512sample/rawPCM contract unchanged. Do not suppress acceptance failures,
raise jitter buffering to hide them or change gain without microphone evidence.
Compile, then obtain upload authorization as required by firmware workflow.

Acceptance after fix: repeat >=40s reception with USB attached but serial reader
closed, then with C3 USB power only/no data if practical; record rate/gaps/kernel
errors. Run original5s voice-unit checker and actual WAV clarity/NeoPixel tests,
then real UnoQ voice directions/tracking/shoot/phone gallery. Temporary open-
monitor testing is diagnostic only; standalone robustness remains unpassed.

Evidence (private ignored logs): c3-hotspot-awake.json,c3-udp-serial-open.json,
c3-udp-serial-closed.json,c3-synchronized-sender.log and associated console logs.
No firmware file edited/reflashed by Session A during this diagnosis.

## Fresh receiver-side reproduction - 2026-10-04
User requested testing after e0d66c4. Unchanged canonical5second checker on Uno Q
passed format/rate threshold:166packets,0malformed,RMS151.4,peak1443. Private WAV
played; user clarity and light observation pending. With serial monitor closed,
new40.033second metadata-only sample received1072packets/26.78persecond,
0malformed,max gap2.513seconds,12gaps over250ms. No payloads saved for long check.
This reproduces the pauses; no logging fix/flash or fresh serial-open comparison
performed. Firmware B action and standalone closed-monitor acceptance above
remain pending. See ignored logs/c3_f3_test/delivery-serial-closed.json.


## Repair prepared, not yet hardware-verified — 2026-10-04
voice_unit now queues logs with zero-wait enqueue and drains only in main loop
when USB has space; CDC timeout0. Compile passed999975 program/37976 globals.
Not flashed under user's hardware deferral. The previous2.513s gap remains the
last sustained physical evidence. Next: flash with confirmed board connection,
then repeat >=40s delivery with serial CLOSED before claiming resolution.
