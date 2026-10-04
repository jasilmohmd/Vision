# Wi-Fi transport diagnostic handoff - 2026-10-04

No root cause or successful fix established. Current symptoms occur below the
Vision app: C3 fails association and S3 HTTP/frame delivery stalls. Do not mark
software phases or firmware F2/F3 passed. Session A had explicit network-only
Wi-Fi diagnostic/build/upload exceptions; broader firmware remains Session B.

## Verified tests

- Uno Q active TinkerSpace WPA2,2462MHz,192.168.1.99; S3 earlier joined
  192.168.1.122/MAC28:84:85:a1:85:ec. C3 DHCP unknown; never inferred.
- C3 temporary Wi-Fi-only sketch (no I2S/NeoPixel software initialization):
  standard b/g/n20s and b/g30s both failed association, disconnectreason2.
- Second C3 isolation: scanner saw the exact router BSSID90:67:17:02:a6:67,
  channel11,RSSI-64/-62; targeted channel/BSSID connection at8.5dBm then5dBm,
  20s each, failed. No evidence that password is wrong: both ignored credentials
  matched locally stored active Uno Q profile, including unescaped comparison.
- C3 diagnostic softAP reported AP_READY192.168.4.1/channel1. Uno Q could not
  find Vision-C3-Diagnostic; directed rescan/full rescan still did not list it.
  This implicates radio/calibration/driver or RF/power path, not a confirmed
  board defect. Needs spare-board or driver/PHY comparison to distinguish causes.
- Uno Q powersaveOFF router test:0frames/4158bytes, maxgap3.871s,status1.886s,
  readtimeout; actualradioON/savedprofiledefault0 restored and verified.
- S3 b/g comparison:1frame/4.750s, status0.963s, streamreadtimeout. Reverted
  protocol experiment; original b/g/n production rebuilt986425/56664/flashed
  with verified hashes. No sensor/pins/servo/capture protocol changes.
- User says hotspots off, boards close/clear antennas, alternate cable/power
  ready. Post-report production C3 retry50s still no IP/three reason2 events;
 20s UDP metadata discovery returned no peers. Cannot independently verify
  physical wiring or power changes. S3 post-hotspot-off probe0frames/status and
  streamconnecttimeouts; later ping1/3 replies,551ms. No single cause proven.

## Restoration and next action

Both temporary C3 isolation/access-point sketches were removed from the board
by production upload1000105/37976. Production keeps prior SDK-default TX power,
manual45s reconnect and bounded audio-send retry; no new production C3 feature.
S3 protocol comparison reverted. Uno Q restored TinkerSpace, temporary diagnostic
NM profile deleted, credential-bearing remote test helper self-deleted.
All serial readers/probes ended; Vision stopped. Root/runtime config still old
hotspot addresses: do not launch until all verified board IPs are updated.
No commit/push. Existing HEADd64f754f219d4b983a32bd87f740309fc2920e41.

User asked find/fix. Asked whether spare C3 available; comparison pending. If
available, identify exact connected replacement port/MAC before any flash,
repeat Wi-Fi-only association/AP comparison, then restore production. If not,
Session B should compare driver/PHY calibration on this board and hardware team
check unloaded supply/RF; router administrator can check association/MAC-filter
logs. Do not erase flash/NVS or guess pins as an unapproved diagnostic shortcut.
Camera transport remains independently unresolved and needs retest afterward.
Prior136 software tests are last result; not rerun during network isolation.

## Metadata evidence (ignored logs; no private media)

c3-wifi-isolation-result.log; c3-wifi-isolation-power-result.log;
c3-wifi-ap-start.log; router-c3-new-power-check.log;
router-camera-powersave-off.json; router-camera-bg.json;
router-camera-hotspots-off.json; router-s3-restored-compile/upload logs;
router-c3-final-production-upload.log. Temporary diagnostic builds/uploads also
ignored. Official reason2 interpretation: authentication response timeout,
https://docs.espressif.com/projects/esp-idf/en/release-v5.4/esp32/api-guides/wifi.html
Search found older driver reports, not a verified matching3.3.11 fix; no SDK
upgrade/downgrade performed.

## BLE comparison - 2026-10-04

C3 BLE trial delivered loss-free PCM in final40s (0padding), while Wi-Fi still
fails authentication. This establishes useful BLE throughput on this board; it
does not prove the Wi-Fi root cause or complete full acceptance. Maximum101ms
notification gap exceeds strict100ms threshold. S3 concurrentprobe still0frames/
timeout. See BLE_TRANSPORT.md and latest HANDOFF. Furtherfirmware work belongsB.
