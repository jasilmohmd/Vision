#include <Arduino.h>
#include <WiFi.h>
#include <esp_system.h>
#include <esp_wifi.h>
#include <freertos/queue.h>
#include "secrets.h" // Ignored local copy; never print credentials.

uint32_t attemptStarted = 0;
bool reportedTimeout = false;
struct EventRecord { int id; uint8_t reason; uint32_t ip; };
QueueHandle_t events;

void setup() {
  Serial.begin(115200);
  delay(1500);
  Serial.printf("wifi_diagnostic boot reset_reason=%d; no audio or GPIO tasks\n",
                static_cast<int>(esp_reset_reason()));
  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);
  WiFi.setAutoReconnect(false); // One attempt; avoid overlapping retries.
  Serial.printf("station MAC=%s\n", WiFi.macAddress().c_str());
  events = xQueueCreate(8, sizeof(EventRecord));
  if (!events) { Serial.println("Event queue allocation failed"); return; }
  WiFi.onEvent([](WiFiEvent_t event, WiFiEventInfo_t info) {
    EventRecord record{static_cast<int>(event), 0, 0};
    if (event == ARDUINO_EVENT_WIFI_STA_DISCONNECTED)
      record.reason = info.wifi_sta_disconnected.reason;
    else if (event == ARDUINO_EVENT_WIFI_STA_GOT_IP)
      record.ip = info.got_ip.ip_info.ip.addr;
    xQueueSend(events, &record, 0); // Keep Serial and network reads out of callbacks.
  });
  const int count = WiFi.scanNetworks();
  Serial.printf("scan result=%d\n", count);
  int matches = 0;
  for (int i = 0; i < count; ++i) {
    if (WiFi.SSID(i) != WIFI_SSID) continue;
    ++matches;
    Serial.printf("target AP channel=%d RSSI=%d auth=%d BSSID=%s\n",
                  WiFi.channel(i), WiFi.RSSI(i), static_cast<int>(WiFi.encryptionType(i)),
                  WiFi.BSSIDstr(i).c_str());
  }
  Serial.printf("target matches=%d\n", matches);
  WiFi.scanDelete();
  // Controlled comparison with the default-power baseline; not a proven fix.
  const esp_err_t powerResult = esp_wifi_set_max_tx_power(34); // 8.5 dBm.
  int8_t actualPower = 0;
  const esp_err_t readPowerResult = esp_wifi_get_max_tx_power(&actualPower);
  Serial.printf("TX power set_result=%d read_result=%d quarter_dBm=%d\n",
                static_cast<int>(powerResult), static_cast<int>(readPowerResult), actualPower);
  const wl_status_t result = WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.printf("begin status=%d; DHCP; auto/manual reconnect disabled\n", static_cast<int>(result));
  attemptStarted = millis();
}

void loop() {
  static int previous = -1;
  static uint32_t lastReport = 0;
  EventRecord record;
  for (unsigned i = 0; events && i < 8 && xQueueReceive(events, &record, 0) == pdTRUE; ++i) {
    Serial.printf("event=%d reason=%u\n", record.id, record.reason);
    if (record.id == ARDUINO_EVENT_WIFI_STA_GOT_IP)
      Serial.printf("GOT_IP=%s\n", IPAddress(record.ip).toString().c_str());
  }
  const int state = WiFi.status();
  if (state != previous) {
    Serial.printf("state=%d uptime_ms=%lu heap=%u\n", state,
                  static_cast<unsigned long>(millis()), static_cast<unsigned>(ESP.getFreeHeap()));
    previous = state;
  }
  if (state == WL_CONNECTED && millis() - lastReport >= 5000) {
    Serial.printf("CONNECTED IP=%s gateway=%s RSSI=%d\n",
                  WiFi.localIP().toString().c_str(), WiFi.gatewayIP().toString().c_str(), WiFi.RSSI());
    lastReport = millis();
  }
  if (!reportedTimeout && state != WL_CONNECTED && millis() - attemptStarted >= 30000) {
    reportedTimeout = true;
    Serial.println("No connection after30s; diagnostic remains idle until RESET");
    WiFi.disconnect(false, false);
  }
  delay(100);
}
