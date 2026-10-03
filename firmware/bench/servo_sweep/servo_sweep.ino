#include <Arduino.h>
#include <ESP32Servo.h>
#include <esp_system.h>

#ifndef BOTH_TOGETHER
#define BOTH_TOGETHER 0
#endif
#ifndef SAFE_MIN
#define SAFE_MIN 30
#endif
#ifndef SAFE_MAX
#define SAFE_MAX 150
#endif
static_assert(SAFE_MIN >= 0 && SAFE_MIN < 90 && SAFE_MAX > 90 && SAFE_MAX <= 180,
              "Safe limits must surround 90 degrees");
static_assert(BOTH_TOGETHER == 0 || BOTH_TOGETHER == 1, "Use 0 or 1");
constexpr int PAN_PIN = 1;
constexpr int TILT_PIN = 2;
constexpr uint32_t STEP_MS = 40;
Servo pan, tilt;
int panAngle = 90, tiltAngle = 90;

void moveSlowly(int panTarget, int tiltTarget) {
  while (panAngle != panTarget || tiltAngle != tiltTarget) {
    if (panAngle != panTarget) panAngle += panAngle < panTarget ? 1 : -1;
    if (tiltAngle != tiltTarget) tiltAngle += tiltAngle < tiltTarget ? 1 : -1;
    pan.write(panAngle);
    tilt.write(tiltAngle);
    Serial.printf("pan=%d tilt=%d\n", panAngle, tiltAngle);
    delay(STEP_MS);
  }
}

void runSweep() {
  Serial.printf("START sweep BOTH_TOGETHER=%d limits=%d..%d\n", BOTH_TOGETHER, SAFE_MIN, SAFE_MAX);
  if (BOTH_TOGETHER) {
    moveSlowly(SAFE_MIN, SAFE_MIN);
    moveSlowly(SAFE_MAX, SAFE_MAX);
    moveSlowly(90, 90);
  } else {
    Serial.println("PAN only; tilt held at 90");
    moveSlowly(SAFE_MIN, 90);
    moveSlowly(SAFE_MAX, 90);
    moveSlowly(90, 90);
    delay(1000);
    Serial.println("TILT only; pan held at 90");
    moveSlowly(90, SAFE_MIN);
    moveSlowly(90, SAFE_MAX);
    moveSlowly(90, 90);
  }
  Serial.println("DONE centred 90/90; send r to repeat. Check smoothness and supply voltage.");
}

void setup() {
  Serial.begin(115200);
  delay(1500);
  Serial.printf("servo_sweep boot reset_reason=%d\n", static_cast<int>(esp_reset_reason()));
  Serial.println("Wi-Fi disabled; IP none (bench). Pan GPIO1, tilt GPIO2, 50Hz.");
  Serial.println("Starting in 5s. Clear bracket; shared ground and capacitors required.");
  delay(5000);
  pan.setPeriodHertz(50);
  tilt.setPeriodHertz(50);
  pan.attach(PAN_PIN, 500, 2400);
  tilt.attach(TILT_PIN, 500, 2400);
  if (!pan.attached() || !tilt.attached()) {
    Serial.println("ERROR servo PWM attachment failed");
    while (true) delay(1000);
  }
  // Physical boot position is unknown; initial centring may move the bracket.
  pan.write(90);
  tilt.write(90);
  delay(1500);
  runSweep();
}

void loop() {
  if (Serial.available() && Serial.read() == 'r') runSweep();
  delay(10);
}
