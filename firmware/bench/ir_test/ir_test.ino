#include <Arduino.h>
#include <esp_system.h>

#ifndef IR_ACTIVE_LOW
#define IR_ACTIVE_LOW 1
#endif
static_assert(IR_ACTIVE_LOW == 0 || IR_ACTIVE_LOW == 1, "Use 0 or 1");
constexpr int IR_PIN = 1;
constexpr uint32_t DEBOUNCE_MS = 20;
int lastRaw, stableRaw;
uint32_t changedAt, heldFrom;
bool held;

bool active(int value) { return value == (IR_ACTIVE_LOW ? LOW : HIGH); }
void setup() {
  Serial.begin(115200);
  delay(1500);
  Serial.printf("ir_test boot reset_reason=%d\n", static_cast<int>(esp_reset_reason()));
  Serial.println("Wi-Fi disabled; IP none (bench). OUT GPIO1, VCC=3V3, GND shared.");
  Serial.printf("IR_ACTIVE_LOW=%d is provisional: compare raw levels with cheek near/far.\n", IR_ACTIVE_LOW);
  pinMode(IR_PIN, INPUT); // Sensor must drive its OUT pin; no assumed pull-up.
  lastRaw = stableRaw = digitalRead(IR_PIN);
  changedAt = heldFrom = millis();
  held = active(stableRaw);
  Serial.printf("initial raw=%d active=%d\n", stableRaw, held);
}
void loop() {
  const uint32_t now = millis();
  const int raw = digitalRead(IR_PIN);
  if (raw != lastRaw) { lastRaw = raw; changedAt = now; }
  if (raw != stableRaw && now - changedAt >= DEBOUNCE_MS) {
    stableRaw = raw;
    const bool isActive = active(raw);
    if (isActive) {
      heldFrom = now;
      Serial.printf("raw=%d active=1 hold started\n", raw);
    } else {
      Serial.printf("raw=%d active=0 held_ms=%lu\n", raw, static_cast<unsigned long>(held ? now - heldFrom : 0));
    }
    held = isActive;
  }
  delay(2);
}
