# C3 Wi-Fi diagnostic

Temporary F3 troubleshooting sketch. Uses DHCP and the same ignored local
credentials as voice_unit. It scans for that network, reports channel/RSSI/auth,
then makes one connection attempt using the Arduino core connection defaults. No microphone,
NeoPixel, audio UDP, or servo tasks run. Credentials are never printed.

Copy voice_unit/secrets.h locally into this folder (secrets.h is ignored).
Compile for esp32:esp32:esp32c3:CDCOnBoot=cdc and upload only to the confirmed C3
with user authorization. Observe Serial at115200. A failed attempt stops after
30seconds; RESET starts another. After diagnosis restore production voice_unit
with user authorization. A successful connection does not pass F3 acceptance.

After the initial default-power baseline failed despite detecting the hotspot,
the diagnostic caps transmit power at8.5dBm (ESP-IDF value34, quarter-dBm units)
and reports set/read results for comparison. This is an experiment, not a claim
that the board has a power or antenna fault.

Events are queued from the Wi-Fi callback and printed in loop; DHCP addresses
are also printed every5seconds while connected. The final diagnostic confirmed
10.153.76.243 on the current WPA2 hotspot. This DHCP address may change later.
