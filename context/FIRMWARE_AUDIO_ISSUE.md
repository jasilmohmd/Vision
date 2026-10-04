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


## C3 logging repair flashed - 2026-10-04
User explicitly requested “flash c3”. Arduino discovery found COM18 ESP USB;
esptool identified ESP32-C3 AZrev1.1,4MB,MAC44:b1:76:17:f5:7c before writing.
Uploaded the previously compiled999975-byte repair using esp32:esp32:esp32c3:
CDCOnBoot=cdc. Upload exited0, written hashes verified, hard reset completed.
Startup confirmed mic4/5/6,pixel7,SHIFT14,IR omitted,TX8.5dBm,DHCP IP
10.153.76.243,RSSI -50dBm,audio destination10.153.76.45:5005,light listener5006.
Brief serial checks showed packets_sent98/167/192 but send_errors118/362/650:
send failures are increasing, so delivery is NOT established and this is NOT
F3 acceptance. No receiver, speech/LED observation or >=40s closed-monitor
delivery test was run. Root cause of send errors is unverified; confirm Uno Q
destination availability/network path when user resumes hardware testing.
Serial readers closed after checks; S3/Uno Q not flashed or controlled and
service not enabled. Hardware remains deferred except this requested upload.
Ignored logs:firmware/.build/voice-unit-nonblocking-upload.log and startup.log
(full startup filename:voice-unit-nonblocking-startup.log).
Existing HEAD d64f754f219d4b983a32bd87f740309fc2920e41 is published on origin/main.
No new commit/push requested for this flash. Exact next action: diagnose C3 UDP
send failures with the verified destination available, then closed-monitor
sustained delivery and speech/light checks; measure S3 power-bank feed under
servo load before combined physical acceptance. Preserve pending gates.

## Later outage evidence - 2026-10-04
Latest Session B repair is compiled but not flashed. Following freeform test
missing-audio warning, stopped-app receiver got38validpackets/20.351s (1.87/s),
14.374s gap,zero malformed/receive/checksum/buffererrors. Both ESP32 USB ports
currently absent;sender Serial counters unavailable. User says boards stayed
powered. Do not attribute all this deficit to old logging without new evidence.
Flash/retest remains Session B owned;no Session A firmware changes.

## Camera and microphone repair investigation - 2026-10-04

User authorized fixing delivery issues. Vision remains stopped; no movement,
capture, light command, firmware modification, flash or service activation.
Session A ownership remains in force. Latest Session B handoff confirms the C3
queued-logging repair WAS FLASHED successfully on COM18. Earlier Session A
notes saying unflashed are superseded. User confirms hotspot close and awake,
battery saver off. Uno Q remains 10.153.76.45, S3 .67, C3 .243; MACs verified
through Uno Q neighbours. ADB serial 662499217; C3 COM18 is present again.

Actual stopped-app measurements after repair:
- C3 serial-closed 20.081s: 601 valid packets, 29.93/s, max gap 1.070s,
  zero malformed/other-source/kernel receive or checksum errors.
- S3 stream-only 21.095s: 87 frames, 4.12 received FPS, max chunk gap .937s,
  status latency .534s, RSSI -39, uptime 788s. No HTTP errors. Diagnostic ok
  means delivery occurred, not stable tracking or physical acceptance.
- C3 active receiver + serial open 40.057s: 1036 valid packets, 25.86/s,
  max gap 1.420s, zero malformed or kernel receive errors. Sender counters
  increased from sent15353/errors6147 to sent16076/errors6363 across three
  10-second reports, then sent16389/errors6363 on the next report. Send failures
  persist with an active destination; not simply a missing receiver or old
  blocking producer logging. Their exact stage/errno remains unknown.
- Uno Q ping averages: C3 380ms (max1072), S3 373ms (max829), hotspot130ms.
  Laptop also sees C3 delays up to1119ms and one timeout in five probes.
  Strong RSSI does not establish a responsive path. Network/firmware attribution
  still unresolved; no power problem inferred solely from these measurements.

Temporary Wi-Fi comparison launched in a local console; sudo authentication
is pending. No power setting changed yet. Baseline 633/20.011s =31.63/s,
max gap .620s, zero receive errors. It will test power saving off and restore
original ON through an EXIT trap; no permanent profile edits. First attempt
failed due to CRLF in an ignored script; corrected LF and restarted. Existing
result JSON from first attempt is stale while new test waits. No secrets saved.

Evidence is metadata under ignored logs/: c3-repair-receiver.json,
c3-repair-sender.log, repair-camera-baseline.json, unoq-wifi-repair-console.log.
Software freshness race fix from preceding turn remains deployed; 136 tests
passed then, not rerun here because production source is unchanged this turn.
Current HEAD d64f754f219d4b983a32bd87f740309fc2920e41. No commit/push requested.
Acceptance and benchmark remain pending. Next: complete authenticated network
comparison, evaluate measured effects, and report any remaining sender firmware
fault to user for Session B. Do not increase freshness/buffer limits to hide gaps.


## New-network uploads completed; S3 connection blocker - 2026-10-04

User explicitly authorized this Session A to compile/upload EXISTING sketches
and update network addresses only, overriding the normal Session B boundary
for this narrow task. No sketch implementation changed. Verified chips/MACs
before writing: C3 COM18 ESP32-C3 AZrev1.1/44:b1:76:17:f5:7c; S3 COM19
ESP32-S3 rev0.2/28:84:85:a1:85:ec. User-edited secrets initially did not match
laptop SSID exactly. Corrected SSID in both ignored headers to the observed
network, preserved user passwords, set C3 UNOQ_IP172.20.10.2. Both passwords
compared equal without printing values. DHCP1 retained; no guessed static IPs.

Both final builds succeeded: C3 999979 program/37976 globals; S3 984997/56656.
Both final uploads exited0, flash hashes verified and boards reset. Pins,
servo/camera/microphone conversion/light behavior/shared contract unchanged.
Source diff confirms neither sketch edited. Secret headers still Git-ignored.
One earlier successful upload had the nonmatching SSID; final uploads replace it.

Uno Q now on new iPhone network, DHCP172.20.10.2/28, gateway172.20.10.1;
laptop172.20.10.3. Uno Q fell back to old network once during uploads; manually
reactivated verified new profile and rechecked it remains new. Do not assume
future reconnections keep this DHCP destination; verify before later uploads.
C3 joined172.20.10.4; MAC confirmed by neighbour and serial boot. LightUDP5006
ready, audio destination172.20.10.2:5005. Ping averaged24ms in3 probes, but
sustained serial-CLOSED receiver40.132s got only388 packets (9.67/s), max gap
9.517s, zero malformed/other-peer/kernel receive errors. New network has NOT
resolved audio delivery. Source sender/network causal attribution still pending.

S3 has NOT joined; no confirmed new IP. Serial repeated Wi-Fi state changes
and E wifi:Set status to INIT after upload and after one authorized restart.
Camera/PSRAM/OV3660 initialization succeeds; latest boot reset_reason1 is
explicit tool reset, not a new inferred spontaneous brownout. No fresh BOD
message captured. User says iPhone Maximize Compatibility already enabled;
scan reports hotspot2437MHz. Password equality alone does not identify fault.
No extra connection behavior change authorized under network-only exception.
Asynchronous question asks user to authorize Wi-Fi diagnostics/connection fixes
here or hand remaining firmware issue back to Session B. Await decision.

Root config.yaml and ignored full-system config have UnoQ172.20.10.2 and
C3172.20.10.4. S3 field still OLD10.153.76.67; NOT ready for full runtime.
Launch console URL updated172.20.10.2:8080/live; app remains STOPPED, no full
new-network run or camera comparison claimed. Local config validation passed;
prior136 software tests not rerun for configuration/build-only changes.
Ignored logs hold build/upload/serial and new-network-c3-delivery.json metadata;
no speech WAV/media or credentials included in handoff. Serial readers closed.

No commit/push or service activation. Existing HEADd64f754. All physical
acceptance/CPUbenchmark pending. Exact next action: resolve Wi-Fi diagnostic
ownership, diagnose S3 association and C3 gaps, verify S3 IP by MAC/status,
finish runtime config/deployment, then run requested unrestricted live test.
Respect user no guided voice sequence and no time limit. Update context before
any future commit; preserve both sessions' records.


## New-network real-component run active; lag persists - 2026-10-04

User requested migration, all IP updates and another unrestricted real run.
User explicitly authorized two Session A exceptions: network-only secret/settings
build/upload, then Wi-Fi diagnostics/connection fixes. This does not authorize
unrelated firmware features/pins/contract edits or future phases. Corrected both
ignored SSIDs to verified laptop network, preserved user-entered passwords,
set C3 UNOQ_IP172.20.10.2, retained DHCP. Secrets remain ignored, not printed.
Verified chip/MAC/ports before upload. C3 final compile999979/37976 bytes,
S3 final compile986161/56664; final uploads exit0 with verified flash hashes.

S3 initially could not join. Added bounded disconnect reason/count reporting
(13 source lines; callback only updates counters, main reports at most2s).
Temporary S3 TX8.5dBm cap did NOT solve association; removed and flashed final
build with original transmit power. No other sketch behavior/pins/capture/audio
conversion/lights changed. New reporting revealed reason5 (ASSOC_TOOMANY,
access point unable to handle associated clients). Controlled test disconnected
ONLY Uno Q Wi-Fi while USB remained: S3 immediately joined172.20.10.5, whereas
Uno Q then failed rejoin. User says only laptop/UnoQ/C3 were connected. This
supports hotspot capacity in this observed setup, not a universal iPhone limit.
User moved laptop back to Jasil after Windows location policy blocked CLI switch.
Uno Q then rejoined successfully; all three board MACs reachable on new network.

Current verified board IPs: Uno Q172.20.10.2/28, C3172.20.10.4, S3172.20.10.5;
gateway172.20.10.1. Root config.yaml AND remote root/full-system config updated.
Laptop is on previous network and does not occupy new-hotspot slot. USBADB
662499217 forward tcp8080 -> UnoQ tcp8080 provides http://localhost:8080/live.
Application computation still entirely Uno Q; USB/laptop only console/live view.
Direct gallery on new network http://172.20.10.2:8080 (phone access unconfirmed).
ADB forwarding must be recreated after disconnect/device restart; no auto-start.

New-network delivery checks, serial monitors CLOSED, no capture/move/light:
Initial C3-only40.132s:388 valid packets,9.67/s,maxgap9.517s; not repaired.
After three boards could join, concurrent40s C3 + camera: C3993/40.010s,
24.82/s vs31.25expected,maxgap.639s,0malformed/kernel receive errors. Camera
20frames over13.065s,1.53receivedFPS,maxchunkgap1.197s,status1.106s; requested40s
ended early with2s readtimeout. Diagnostic okfalse. Changing network has NOT
eliminated delivery issues; these are network measurements, not CPU benchmark.
No claim of exact loss, smooth motion, WAV clarity, colours or full acceptance.

Requested app launched successfully, actual PID14195, UDP5005 owned by app,
--mic udp --seconds0 and real full-system config. USB /live and /live/frame.jpg
HTTP200; browser opened localhost live URL. Startup/calibration and camera sync
completed; repeated freshness warnings still observed. Accepted camera up at
08:04:15(board log clock); physical action not yet confirmed. No guided commands,
voice injection or automatic tracking; user chooses commands. Run continues
until user stops, no expiry or service activation. All diagnostics/readers ended.

Ignored logs retain final builds/uploads, serial association evidence, new-
network-camera-delivery.json and new-network-c3-delivery.json. Configuration
validation passed locally and on Uno Q. Prior136 software-test result unchanged;
not rerun for this firmware/network-only work. No commit/push requested. Existing
HEADd64f754; firmware/STATUS/context records updated under explicit exception.
Pending: user live feedback, residual stream/audio diagnosis, power under load,
full19-command/features/phone gallery acceptance, CPUbenchmark and standalone
acceptance. Next: observe freeform results or stop exact owned app on request;
never label network migration a stability pass. Refresh context before any commit.

## Wi-Fi transport follow-up - 2026-10-04

User explicitly authorized Session A network-only compilation/upload and Wi-Fi
connection diagnostics/fixes. Latest changes: C3 bounded transient UDP retries,
S3 TCP_NODELAY and stream timing. Both compiled/flashed with verified hashes.
C3 1000357/37976 bytes; S3 986425/56664. No pins/acquisition/PCM contract change.
Final concurrent sample: C3 27.83 packets/s with 0.867s max gap, no malformed or
kernel UDP errors; S3 2.91FPS, 1.166s max chunk gap, frame wait1ms versus network
send wait1009/1626ms. Delivery remains unstable; no F2/F3 or software acceptance.
Uno Q172.20.10.2, C3.4, S3.5; laptop on Jasil using USB localhost:8080/live.
Runtime stopped, all bounded diagnostics ended; no automatic restart or commit.
Next controlled access-point comparison requires verified new network settings;
do not assume changing hotspot alone fixes board RF/power/transport behavior.
Root HANDOFF/TESTING records contain exact evidence and outstanding acceptance.

## TinkerSpace router migration pending - 2026-10-04

User selected TinkerSpace; Uno Q verified192.168.1.99 and S3192.168.1.122,
WPA2 2.4GHz. Both ignored credentials updated, C3 audio destination192.168.1.99.
C3 still fails association; its DHCP address unknown. C3 default TX power and
manual45s reconnect comparison compiled1000105/37976/flashed verified; S3
986425/56664/flashed verified. No physical/PCM/capture contract change.
S3 HTTP probes failed with0frames; no concurrent audio probe/full run possible.
Runtime stopped; root/runtime config still old hotspot values, DO NOT launch.
Root HANDOFF/TESTING has exact diagnostics and next steps for Session B/router
association investigation, verified config completion and metadata retest.
No commit/push or gate completion; all bounded diagnostics/readers ended.
