#include <Arduino.h>
#include <WiFi.h>
#include <ESP32Servo.h>
#include <esp_camera.h>
#include <esp_http_server.h>
#include <esp_heap_caps.h>
#include <esp_system.h>
#include <errno.h>
#include <lwip/sockets.h>
#include "camera_pins.h"
#if __has_include("secrets.h")
#include "secrets.h"
#else
#include "../secrets.example.h"
#endif
#ifndef WIFI_USE_DHCP
#define WIFI_USE_DHCP 0
#endif
#define PAN_MIN 10
#define PAN_MAX 170
#define TILT_MIN 40
#define TILT_MAX 140
constexpr uint32_t SERVO_INTERVAL_MS = 20;
constexpr int SLEW_DEG = 2;
constexpr uint32_t STREAM_INTERVAL_MS = 100;  // At most 10 fps; leave airtime for control.
Servo panServo, tiltServo;
SemaphoreHandle_t cameraMutex, servoMutex;
volatile bool capturePending = false;
volatile bool photoSending = false;
int targetPan = 90, targetTilt = 90, actualPan = 90, actualTilt = 90;
uint32_t moveReceivedMs = 0, moveSettledMs = 0;
bool moveInProgress = false;
uint8_t *heldPhoto = nullptr;
size_t heldLength = 0;
framesize_t captureSize = FRAMESIZE_QXGA;
httpd_handle_t controlServer = nullptr, streamServer = nullptr;

class CameraLock {
 public:
  bool acquired;
  explicit CameraLock(uint32_t ms) : acquired(xSemaphoreTake(cameraMutex, pdMS_TO_TICKS(ms)) == pdTRUE) {}
  ~CameraLock() { release(); }
  void release() { if (acquired) { xSemaphoreGive(cameraMutex); acquired = false; } }
};
class ServoLock {
 public:
  bool acquired;
  explicit ServoLock(uint32_t ms) : acquired(xSemaphoreTake(servoMutex, pdMS_TO_TICKS(ms)) == pdTRUE) {}
  ~ServoLock() { release(); }
  void release() { if (acquired) { xSemaphoreGive(servoMutex); acquired = false; } }
};
void fatal(const char *message) {
  Serial.printf("FATAL %s; stopped. Correct configuration and reset.\n", message);
  while (true) delay(1000);
}
esp_err_t errorReply(httpd_req_t *req, const char *status, const char *message) {
  char text[180];
  snprintf(text, sizeof(text), "{\"error\":\"%s\"}", message);
  httpd_resp_set_status(req, status);
  httpd_resp_set_type(req, "application/json");
  return httpd_resp_send(req, text, HTTPD_RESP_USE_STRLEN);
}
esp_err_t jsonReply(httpd_req_t *req, const char *text) {
  httpd_resp_set_type(req, "application/json");
  httpd_resp_set_hdr(req, "Cache-Control", "no-store");
  return httpd_resp_send(req, text, HTTPD_RESP_USE_STRLEN);
}
bool parseAngle(const char *query, const char *key, int low, int high, int &result) {
  char value[24];
  if (httpd_query_key_value(query, key, value, sizeof(value)) != ESP_OK) return false;
  char *end;
  errno = 0;
  const long angle = strtol(value, &end, 10);
  if (errno || end == value || *end) return false;
  result = angle < low ? low : angle > high ? high : static_cast<int>(angle);
  return true;
}
esp_err_t moveHandler(httpd_req_t *req) {
  const uint32_t received = millis();
  char query[96];
  int pan, tilt;
  if (httpd_req_get_url_query_str(req, query, sizeof(query)) != ESP_OK ||
      !parseAngle(query, "pan", PAN_MIN, PAN_MAX, pan) ||
      !parseAngle(query, "tilt", TILT_MIN, TILT_MAX, tilt))
    return errorReply(req, "400 Bad Request", "pan and tilt must be integers");
  // A stalled camera frame must not delay a manual target or servo PWM update.
  ServoLock lock(100);
  if (!lock.acquired) return errorReply(req, "503 Service Unavailable", "servos busy");
  targetPan = pan; targetTilt = tilt;
  moveReceivedMs = received;
  moveInProgress = actualPan != targetPan || actualTilt != targetTilt;
  moveSettledMs = moveInProgress ? 0 : received;
  char text[64];
  snprintf(text, sizeof(text), "{\"pan\":%d,\"tilt\":%d}", targetPan, targetTilt);
  lock.release();
  Serial.printf("move accepted pan=%d tilt=%d received_ms=%lu handler_ms=%lu\n", pan, tilt,
    static_cast<unsigned long>(received), static_cast<unsigned long>(millis() - received));
  return jsonReply(req, text);
}
esp_err_t statusHandler(httpd_req_t *req) {
  CameraLock lock(2000);
  if (!lock.acquired) return errorReply(req, "503 Service Unavailable", "camera busy");
  ServoLock servoLock(100);
  if (!servoLock.acquired) return errorReply(req, "503 Service Unavailable", "servos busy");
  char text[448];
  snprintf(text, sizeof(text),
    "{\"pan\":%d,\"tilt\":%d,\"actual_pan\":%d,\"actual_tilt\":%d,"
    "\"move_received_ms\":%lu,\"move_settled_ms\":%lu,\"move_in_progress\":%s,"
    "\"uptime_s\":%lu,\"held_photo\":%s,\"rssi\":%d,\"free_heap\":%u,"
    "\"free_psram\":%u,\"reset_reason\":%d}",
    targetPan, targetTilt, actualPan, actualTilt,
    static_cast<unsigned long>(moveReceivedMs), static_cast<unsigned long>(moveSettledMs),
    moveInProgress ? "true" : "false", static_cast<unsigned long>(millis() / 1000),
    heldPhoto ? "true" : "false", WiFi.RSSI(), static_cast<unsigned>(ESP.getFreeHeap()),
    static_cast<unsigned>(ESP.getFreePsram()), static_cast<int>(esp_reset_reason()));
  servoLock.release();
  lock.release();
  return jsonReply(req, text);
}
esp_err_t ackHandler(httpd_req_t *req) {
  CameraLock lock(2000);
  if (!lock.acquired) return errorReply(req, "503 Service Unavailable", "camera busy");
  if (heldPhoto) { free(heldPhoto); heldPhoto = nullptr; heldLength = 0; }
  lock.release();
  return jsonReply(req, "{\"ok\":true}");
}
void discardFrames(unsigned count) {
  for (unsigned i = 0; i < count; ++i) {
    camera_fb_t *frame = esp_camera_fb_get();
    if (frame) esp_camera_fb_return(frame);
  }
}
esp_err_t captureHandler(httpd_req_t *req) {
  const uint32_t started = millis();
  capturePending = true;
  // Wait for any in-progress servo write before changing camera resolution.
  // The loop rechecks capturePending while holding the same servo mutex.
  {
    ServoLock servoLock(100);
    if (!servoLock.acquired) {
      capturePending = false;
      return errorReply(req, "503 Service Unavailable", "servos busy");
    }
  }
  CameraLock lock(5000);
  if (!lock.acquired) {
    capturePending = false;
    return errorReply(req, "503 Service Unavailable", "camera busy");
  }
  // Retried /capture returns the retained image until /ack.
  if (!heldPhoto) {
    sensor_t *sensor = esp_camera_sensor_get();
    bool captured = false;
    const framesize_t sizes[] = {captureSize, FRAMESIZE_UXGA, FRAMESIZE_SXGA, FRAMESIZE_XGA};
    for (framesize_t size : sizes) {
      if (sensor->set_framesize(sensor, size) != 0) continue;
      delay(100);
      discardFrames(2);
      camera_fb_t *frame = esp_camera_fb_get();
      if (frame && frame->format == PIXFORMAT_JPEG && frame->len > 4 &&
          frame->buf[0] == 0xff && frame->buf[1] == 0xd8) {
        uint8_t *copy = static_cast<uint8_t *>(heap_caps_malloc(frame->len, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));
        if (copy) {
          memcpy(copy, frame->buf, frame->len);
          heldPhoto = copy; heldLength = frame->len; captureSize = size; captured = true;
          Serial.printf("capture %ux%u bytes=%u time_ms=%lu\n", frame->width, frame->height,
            static_cast<unsigned>(frame->len), static_cast<unsigned long>(millis() - started));
        } else Serial.println("ERROR capture PSRAM allocation failed");
      }
      if (frame) esp_camera_fb_return(frame);
      if (captured) break;
      Serial.printf("ERROR capture failed at size=%d; trying lower\n", static_cast<int>(size));
    }
    const int restored = sensor->set_framesize(sensor, FRAMESIZE_QVGA);
    if (restored == 0) discardFrames(2);
    else Serial.println("ERROR restoring QVGA stream");
    if (!captured || restored != 0) {
      if (heldPhoto) { free(heldPhoto); heldPhoto = nullptr; heldLength = 0; }
      capturePending = false;
      return errorReply(req, "503 Service Unavailable", "capture failed; inspect Serial");
    }
  }
  const uint8_t *photo = heldPhoto;
  const size_t length = heldLength;
  capturePending = false;
  lock.release();
  // Single control server task serializes /ack after this response finishes.
  httpd_resp_set_type(req, "image/jpeg");
  httpd_resp_set_hdr(req, "Cache-Control", "no-store");
  // Give still-photo traffic the radio while keeping the servo mutex released.
  // Bounded chunks avoid a single large blocking send from PSRAM.
  photoSending = true;
  esp_err_t sent = ESP_OK;
  for (size_t offset = 0; offset < length && sent == ESP_OK; offset += 4096) {
    const size_t chunk = min(static_cast<size_t>(4096), length - offset);
    sent = httpd_resp_send_chunk(req, reinterpret_cast<const char *>(photo + offset), chunk);
    delay(1);
  }
  if (sent == ESP_OK) sent = httpd_resp_send_chunk(req, nullptr, 0);
  photoSending = false;
  Serial.printf("capture send bytes=%u result=0x%x total_ms=%lu\n", static_cast<unsigned>(length),
    sent, static_cast<unsigned long>(millis() - started));
  return sent;
}
esp_err_t streamHandler(httpd_req_t *req) {
  httpd_resp_set_type(req, "multipart/x-mixed-replace;boundary=frame");
  httpd_resp_set_hdr(req, "Cache-Control", "no-store");
  uint8_t *copy = nullptr;
  size_t capacity = 0;
  esp_err_t result = ESP_OK;
  const int socket = httpd_req_to_sockfd(req);
  Serial.printf("stream open socket=%d\n", socket);
  uint32_t streamFrames = 0, lastStreamLog = millis();
  while (WiFi.status() == WL_CONNECTED) {
    const uint32_t frameCycleStarted = millis();
    // A viewer may close its receive side while queued video is still writable.
    // Detect FIN promptly so the single stream task can accept the next viewer.
    char pending;
    const int peek = recv(socket, &pending, 1, MSG_PEEK | MSG_DONTWAIT);
    if (peek == 0 || (peek < 0 && errno != EAGAIN && errno != EWOULDBLOCK)) break;
    if (capturePending || photoSending) { delay(5); continue; }
    size_t length = 0;
    {
      CameraLock lock(2000);
      if (!lock.acquired) { result = ESP_FAIL; break; }
      if (capturePending) continue;
      const uint32_t frameStarted = millis();
      camera_fb_t *frame = esp_camera_fb_get();
      if (millis() - frameStarted > 1000) Serial.printf("stream frame wait_ms=%lu\n", static_cast<unsigned long>(millis() - frameStarted));
      if (!frame || frame->format != PIXFORMAT_JPEG) {
        if (frame) esp_camera_fb_return(frame);
        Serial.println("ERROR stream frame unavailable"); result = ESP_FAIL; break;
      }
      if (frame->len > capacity) {
        uint8_t *grown = static_cast<uint8_t *>(heap_caps_realloc(copy, frame->len, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));
        if (!grown) {
          esp_camera_fb_return(frame); Serial.println("ERROR stream PSRAM allocation failed");
          result = ESP_ERR_NO_MEM; break;
        }
        copy = grown; capacity = frame->len;
      }
      length = frame->len;
      memcpy(copy, frame->buf, length);
      esp_camera_fb_return(frame);
    }
    // Network sends use a private copy, never holding camera/servo mutex.
    char header[100];
    const int headerLength = snprintf(header, sizeof(header),
      "\r\n--frame\r\nContent-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n", static_cast<unsigned>(length));
    result = httpd_resp_send_chunk(req, header, headerLength);
    if (result == ESP_OK) result = httpd_resp_send_chunk(req, reinterpret_cast<const char *>(copy), length);
    if (result != ESP_OK) break;
    ++streamFrames;
    if (millis() - lastStreamLog >= 10000) {
      Serial.printf("stream socket=%d frames=%lu RSSI=%d\n", socket, static_cast<unsigned long>(streamFrames), WiFi.RSSI());
      lastStreamLog = millis();
    }
    const uint32_t elapsed = millis() - frameCycleStarted;
    delay(elapsed < STREAM_INTERVAL_MS ? STREAM_INTERVAL_MS - elapsed : 1);
  }
  free(copy);
  Serial.printf("stream close socket=%d frames=%lu result=0x%x\n", socket, static_cast<unsigned long>(streamFrames), result);
  // Force HTTPD to close this streaming session rather than retaining it as an
  // idle keep-alive connection after a half-close.
  return result == ESP_OK ? ESP_FAIL : result;
}
bool addRoute(httpd_handle_t server, const char *path, esp_err_t (*handler)(httpd_req_t *)) {
  httpd_uri_t route = {};
  route.uri = path; route.method = HTTP_GET; route.handler = handler;
  return httpd_register_uri_handler(server, &route) == ESP_OK;
}
void startServers() {
  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  config.server_port = 80; config.stack_size = 12288;
  config.lru_purge_enable = true; config.recv_wait_timeout = 3; config.send_wait_timeout = 15;
  if (httpd_start(&controlServer, &config) != ESP_OK ||
      !addRoute(controlServer, "/move", moveHandler) || !addRoute(controlServer, "/status", statusHandler) ||
      !addRoute(controlServer, "/capture", captureHandler) || !addRoute(controlServer, "/ack", ackHandler))
    fatal("control HTTP server failed");
  config.server_port = 81; config.ctrl_port += 1; config.stack_size = 8192;
  config.send_wait_timeout = 5;
  if (httpd_start(&streamServer, &config) != ESP_OK || !addRoute(streamServer, "/stream", streamHandler))
    fatal("stream HTTP server failed");
  Serial.printf("HTTP ready: http://%s/status stream=http://%s:81/stream\n",
    WiFi.localIP().toString().c_str(), WiFi.localIP().toString().c_str());
}
void servoTask(void *) {
  while (true) {
    {
      ServoLock lock(1);
      if (lock.acquired && !capturePending) {
        const int panStep = constrain(targetPan - actualPan, -SLEW_DEG, SLEW_DEG);
        const int tiltStep = constrain(targetTilt - actualTilt, -SLEW_DEG, SLEW_DEG);
        if (panStep) { actualPan += panStep; panServo.write(actualPan); }
        if (tiltStep) { actualTilt += tiltStep; tiltServo.write(actualTilt); }
        if (moveInProgress && actualPan == targetPan && actualTilt == targetTilt) {
          moveSettledMs = millis();
          moveInProgress = false;
        }
      }
    }
    // Never catch up missed periods with a burst of servo writes.
    vTaskDelay(pdMS_TO_TICKS(SERVO_INTERVAL_MS));
  }
}
void setup() {
  Serial.begin(115200); delay(1500);
  Serial.printf("camera_head boot reset_reason=%d\n", static_cast<int>(esp_reset_reason()));
  if (!psramFound()) fatal("PSRAM missing; enable OPI PSRAM for N16R8");
  Serial.printf("PSRAM bytes=%u free=%u\n", static_cast<unsigned>(ESP.getPsramSize()), static_cast<unsigned>(ESP.getFreePsram()));
  cameraMutex = xSemaphoreCreateMutex();
  servoMutex = xSemaphoreCreateMutex();
  if (!cameraMutex || !servoMutex) fatal("mutex allocation failed");
  camera_config_t config = {};
  config.ledc_channel = LEDC_CHANNEL_7; config.ledc_timer = LEDC_TIMER_3;
  config.pin_d0 = Y2_GPIO_NUM; config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM; config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM; config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM; config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM; config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM; config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM; config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM; config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000; config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_QXGA; config.jpeg_quality = 12;
  config.fb_count = 2; config.fb_location = CAMERA_FB_IN_PSRAM; config.grab_mode = CAMERA_GRAB_LATEST;
  const esp_err_t result = esp_camera_init(&config);
  if (result != ESP_OK) {
    Serial.printf("ERROR camera init=0x%x; check ribbon and documented pins\n", result);
    fatal("camera initialization failed");
  }
  sensor_t *sensor = esp_camera_sensor_get();
  Serial.printf("Camera sensor PID=0x%x\n", sensor->id.PID);
  if (sensor->id.PID != OV3660_PID) fatal("sensor differs from user-confirmed OV3660");
  if (sensor->set_framesize(sensor, FRAMESIZE_QVGA) != 0) fatal("QVGA configuration failed");
  panServo.setPeriodHertz(50); tiltServo.setPeriodHertz(50);
  panServo.attach(1, 500, 2400); tiltServo.attach(2, 500, 2400);
  if (!panServo.attached() || !tiltServo.attached()) fatal("servo attachment failed");
  // F1 horns were aligned at 90/90. No measured physical position is available.
  panServo.write(90); tiltServo.write(90);
  if (xTaskCreate(servoTask, "servo_slew", 3072, nullptr, 2, nullptr) != pdPASS)
    fatal("servo task allocation failed");
  Serial.println("Servo centre90/90; slew2deg/20ms; no automatic sweep.");
  if (!strcmp(WIFI_SSID, "REPLACE_LOCALLY") || !strcmp(WIFI_PASS, "REPLACE_LOCALLY"))
    fatal("configure ignored secrets.h Wi-Fi credentials");
  WiFi.persistent(false); WiFi.mode(WIFI_STA); WiFi.setSleep(false); WiFi.setAutoReconnect(true);
#if !WIFI_USE_DHCP
  if (S3_IP == IPAddress(0, 0, 0, 0) || !WiFi.config(S3_IP, GATEWAY, SUBNET)) fatal("confirmed static IPv4 settings required");
#endif
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.printf("Wi-Fi starting; addressing=%s\n", WIFI_USE_DHCP ? "DHCP bench" : "static");
}
void loop() {
  static uint32_t lastRetry = 0;
  static int lastWifi = -1;
  const uint32_t now = millis();
  const int wifi = WiFi.status();
  if (wifi != lastWifi) {
    Serial.printf("Wi-Fi state=%d\n", wifi); lastWifi = wifi;
    if (wifi == WL_CONNECTED) Serial.printf("Wi-Fi connected IP=%s RSSI=%d\n", WiFi.localIP().toString().c_str(), WiFi.RSSI());
  }
  if (wifi == WL_CONNECTED && !controlServer) startServers();
  if (wifi != WL_CONNECTED && now - lastRetry >= 10000) {
    lastRetry = now; Serial.println("Wi-Fi reconnect attempt"); WiFi.reconnect();
  }
  delay(2);
}
