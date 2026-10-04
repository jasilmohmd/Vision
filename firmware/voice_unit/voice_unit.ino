#include <Arduino.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <ESP_I2S.h>
#include <Adafruit_NeoPixel.h>
#include <esp_system.h>
#include <esp_wifi.h>
#if __has_include("secrets.h")
#include "secrets.h"
#else
#include "../secrets.example.h"
#endif
#ifndef WIFI_USE_DHCP
#define WIFI_USE_DHCP 0
#endif
#ifndef SHIFT
#define SHIFT 14
#endif
static_assert(SHIFT >= 0 && SHIFT <= 31, "SHIFT must be 0..31");
// Optional IR is deliberately omitted from this prototype.
constexpr size_t SAMPLE_COUNT = 512;
constexpr uint16_t AUDIO_PORT = 5005, LIGHT_PORT = 5006;
I2SClass microphone;
Adafruit_NeoPixel pixel(1, 7, NEO_GRB + NEO_KHZ800);
WiFiUDP lightSocket;
enum class Light { Ready, Heard, Tracking, NoSubject, Saved, Error, Reconnect, Sleep };
Light steady = Light::Ready, transient = Light::Ready;
bool transientActive = false;
uint32_t transientStarted = 0, steadyStarted = 0, rendered = UINT32_MAX;

void show(uint32_t colour) {
  if (colour != rendered) { rendered = colour; pixel.setPixelColor(0, colour); pixel.show(); }
}
void fatal(const char *message) {
  Serial.printf("FATAL %s; correct configuration and reset\n", message);
  show(pixel.Color(255, 0, 0));
  while (true) delay(1000);
}
bool parseLight(const char *name, Light &result) {
  const char *names[] = {"ready", "heard", "tracking", "nosubject", "saved", "error", "reconnect", "sleep"};
  const Light values[] = {Light::Ready, Light::Heard, Light::Tracking, Light::NoSubject,
                         Light::Saved, Light::Error, Light::Reconnect, Light::Sleep};
  for (size_t i = 0; i < 8; ++i) {
    if (!strcmp(name, names[i])) { result = values[i]; return true; }
  }
  return false;
}
void acceptLight(Light state) {
  if (state == Light::Heard || state == Light::Saved || state == Light::Error) {
    transient = state; transientActive = true; transientStarted = millis();
  } else { steady = state; steadyStarted = millis(); transientActive = false; }
}
void updateLight(bool connected) {
  const uint32_t now = millis();
  if (!connected) { show((now / 500) % 2 ? 0 : pixel.Color(150, 0, 255)); return; }
  if (transientActive) {
    const uint32_t age = now - transientStarted;
    const uint32_t duration = transient == Light::Error ? 600 : 300;
    if (age < duration) {
      if (transient == Light::Error) show((age / 150) % 2 ? 0 : pixel.Color(255, 0, 0));
      else show(transient == Light::Heard ? pixel.Color(0, 0, 255) : pixel.Color(255, 255, 255));
      return;
    }
    transientActive = false;
  }
  const bool blink = ((now - steadyStarted) / 500) % 2 == 0;
  switch (steady) {
    case Light::Ready: show(pixel.Color(0, 180, 0)); break;
    case Light::Tracking: show(pixel.Color(0, 255, 255)); break;
    case Light::NoSubject: show(blink ? pixel.Color(255, 100, 0) : 0); break;
    case Light::Reconnect: show(blink ? pixel.Color(150, 0, 255) : 0); break;
    default: show(0); break;
  }
}
void audioTask(void *) {
  // This socket and its reconnect operations belong exclusively to this task.
  WiFiUDP audioSocket;
  int32_t raw[SAMPLE_COUNT];
  uint8_t pcm[SAMPLE_COUNT * 2];
  size_t collected = 0;
  bool socketReady = false;
  uint32_t sent = 0, failed = 0, lastReport = millis(), lastError = 0;
  while (true) {
    const size_t bytes = microphone.readBytes(reinterpret_cast<char *>(raw + collected),
                                             (SAMPLE_COUNT - collected) * sizeof(int32_t));
    if (!bytes || bytes % sizeof(int32_t)) {
      collected = 0;
      if (millis() - lastError >= 2000) {
        Serial.printf("ERROR I2S bytes=%u code=%d\n", static_cast<unsigned>(bytes), microphone.lastError());
        lastError = millis();
      }
      vTaskDelay(pdMS_TO_TICKS(10)); continue;
    }
    collected += bytes / sizeof(int32_t);
    if (collected < SAMPLE_COUNT) continue;
    collected = 0;
    if (WiFi.status() != WL_CONNECTED) {
      if (socketReady) audioSocket.stop();
      socketReady = false; continue; // Drain mic offline; never replay old audio.
    }
    if (!socketReady) socketReady = audioSocket.begin(0) != 0;
    for (size_t i = 0; i < SAMPLE_COUNT; ++i) {
      const int32_t value = constrain(raw[i] >> SHIFT, -32768, 32767);
      const uint16_t bits = static_cast<uint16_t>(static_cast<int16_t>(value));
      pcm[2 * i] = bits & 0xff; pcm[2 * i + 1] = bits >> 8;
    }
    bool ok = socketReady && audioSocket.beginPacket(UNOQ_IP, AUDIO_PORT) != 0;
    if (ok) {
      const size_t written = audioSocket.write(pcm, sizeof(pcm));
      const bool delivered = audioSocket.endPacket() != 0;
      ok = written == sizeof(pcm) && delivered;
    }
    if (ok) ++sent;
    else { ++failed; audioSocket.stop(); socketReady = false; }
    if (millis() - lastReport >= 10000) {
      Serial.printf("audio packets_sent=%lu send_errors=%lu RSSI=%d free_heap=%u\n",
                    static_cast<unsigned long>(sent), static_cast<unsigned long>(failed),
                    WiFi.RSSI(), static_cast<unsigned>(ESP.getFreeHeap()));
      lastReport = millis();
    }
  }
}
void setup() {
  Serial.begin(115200); delay(1500);
  pixel.begin(); pixel.setBrightness(40); show(0);
  Serial.printf("voice_unit boot reset_reason=%d; mic4/5/6 pixel7 SHIFT=%d IR omitted\n",
                static_cast<int>(esp_reset_reason()), SHIFT);
  if (!strcmp(WIFI_SSID, "REPLACE_LOCALLY") || !strcmp(WIFI_PASS, "REPLACE_LOCALLY"))
    fatal("configure ignored secrets.h locally");
  if (UNOQ_IP == IPAddress(0, 0, 0, 0)) fatal("confirmed audio destination required");
  microphone.setPins(4, 5, -1, 6);
  if (!microphone.begin(I2S_MODE_STD, 16000, I2S_DATA_BIT_WIDTH_32BIT,
                        I2S_SLOT_MODE_MONO, I2S_STD_SLOT_LEFT)) fatal("I2S init failed");
  WiFi.persistent(false); WiFi.mode(WIFI_STA); WiFi.setSleep(false); WiFi.setAutoReconnect(true);
  // This C3 connected with this cap in the isolated Wi-Fi diagnostic.
  // Keep it explicit; the board/network cause is not established by that test.
  if (esp_wifi_set_max_tx_power(34) != ESP_OK) fatal("Wi-Fi TX power configuration failed");
  Serial.println("Wi-Fi TX power cap=8.5dBm");
  WiFi.onEvent([](WiFiEvent_t event, WiFiEventInfo_t info) {
    Serial.printf("Wi-Fi disconnected reason=%u\n", info.wifi_sta_disconnected.reason);
  }, ARDUINO_EVENT_WIFI_STA_DISCONNECTED);
#if !WIFI_USE_DHCP
  if (C3_IP == IPAddress(0, 0, 0, 0) || !WiFi.config(C3_IP, GATEWAY, SUBNET))
    fatal("confirmed static C3 address required");
#endif
  // Configure before connecting so WPA3 can negotiate either supported SAE method.
  WiFi.begin(WIFI_SSID, WIFI_PASS, 0, nullptr, false);
  wifi_config_t station;
  if (esp_wifi_get_config(WIFI_IF_STA, &station) != ESP_OK) fatal("Wi-Fi config unavailable");
  station.sta.sae_pwe_h2e = WPA3_SAE_PWE_BOTH;
  if (esp_wifi_set_config(WIFI_IF_STA, &station) != ESP_OK || esp_wifi_connect() != ESP_OK)
    fatal("Wi-Fi start failed");
  if (xTaskCreate(audioTask, "audio_udp", 6144, nullptr, 2, nullptr) != pdPASS)
    fatal("audio task allocation failed");
  Serial.printf("Wi-Fi starting addressing=%s; audio destination=%s:%u; lights UDP%u\n",
                WIFI_USE_DHCP ? "DHCP bench" : "static", UNOQ_IP.toString().c_str(), AUDIO_PORT, LIGHT_PORT);
}
void loop() {
  static int previous = -1;
  static bool listening = false;
  static uint32_t lastRetry = 0;
  const int state = WiFi.status();
  const bool connected = state == WL_CONNECTED;
  if (state != previous) {
    Serial.printf("Wi-Fi state=%d\n", state); previous = state;
    if (connected) Serial.printf("Wi-Fi connected IP=%s RSSI=%d\n", WiFi.localIP().toString().c_str(), WiFi.RSSI());
  }
  if (connected) {
    if (!listening) {
      listening = lightSocket.begin(LIGHT_PORT) != 0;
      if (listening) Serial.printf("Light UDP%u ready\n", LIGHT_PORT);
    }
    for (unsigned i = 0; listening && i < 8; ++i) {
      const int length = lightSocket.parsePacket();
      if (!length) break;
      char name[17];
      const int received = lightSocket.read(reinterpret_cast<uint8_t *>(name), sizeof(name) - 1);
      lightSocket.flush();
      if (length > 16 || received != length || received < 0 || memchr(name, 0, received)) continue;
      name[received] = '\0';
      Light light;
      if (parseLight(name, light)) { acceptLight(light); Serial.printf("light %s\n", name); }
      else Serial.println("Ignored unknown light state");
    }
  } else {
    if (listening) lightSocket.stop();
    listening = false; transientActive = false;
    // Allow an in-progress WPA3 handshake to finish before a manual retry.
    if (millis() - lastRetry >= 45000) { lastRetry = millis(); WiFi.reconnect(); }
  }
  updateLight(connected); delay(5);
}
