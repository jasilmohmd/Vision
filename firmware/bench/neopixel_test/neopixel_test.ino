#include <Arduino.h>
#include <Adafruit_NeoPixel.h>
#include <esp_system.h>

#ifndef COLOR_ORDER
#define COLOR_ORDER NEO_GRB
#endif
Adafruit_NeoPixel pixel(1, 7, COLOR_ORDER + NEO_KHZ800);
uint32_t green, blue, cyan, amber, white, red, purple;

void show(uint32_t colour) { pixel.setPixelColor(0, colour); pixel.show(); }
void flash(uint32_t colour, uint32_t duration = 300) {
  show(colour);
  delay(duration);
  show(green); // Previous steady state for this bench sequence is ready.
}
void setup() {
  Serial.begin(115200);
  delay(1500);
  Serial.printf("neopixel_test boot reset_reason=%d\n", static_cast<int>(esp_reset_reason()));
  Serial.printf("Wi-Fi disabled; IP none (bench). DIN GPIO7, brightness40, order=%u\n", COLOR_ORDER);
  pixel.begin();
  pixel.setBrightness(40);
  green = pixel.Color(0, 180, 0);
  blue = pixel.Color(0, 0, 255);
  cyan = pixel.Color(0, 255, 255);
  amber = pixel.Color(255, 100, 0);
  white = pixel.Color(255, 255, 255);
  red = pixel.Color(255, 0, 0);
  purple = pixel.Color(150, 0, 255);
  show(0);
}
void loop() {
  Serial.println("ready: soft green steady"); show(green); delay(2000);
  Serial.println("heard: blue 300ms then ready"); flash(blue); delay(1700);
  Serial.println("tracking: cyan steady"); show(cyan); delay(2000);
  Serial.println("nosubject: amber slow blink");
  for (int i = 0; i < 3; ++i) { show(amber); delay(500); show(0); delay(500); }
  show(green);
  Serial.println("ready: previous steady state for transient tests"); delay(1000);
  Serial.println("saved: white 300ms then ready"); flash(white); delay(1700);
  Serial.println("error: red twice then ready");
  for (int i = 0; i < 2; ++i) { show(red); delay(150); show(0); delay(150); }
  show(green); delay(1500);
  Serial.println("reconnect: purple slow blink");
  for (int i = 0; i < 3; ++i) { show(purple); delay(500); show(0); delay(500); }
  Serial.println("sleep: off"); show(0); delay(2000);
}
