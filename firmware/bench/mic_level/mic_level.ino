#include <Arduino.h>
#include <ESP_I2S.h>
#include <esp_system.h>
#include <math.h>

#ifndef SHIFT
#define SHIFT 14
#endif
#ifndef MIC_SLOT
#define MIC_SLOT I2S_STD_SLOT_LEFT
#endif
static_assert(SHIFT >= 0 && SHIFT <= 31, "SHIFT must be 0..31");
I2SClass microphone;
constexpr size_t SAMPLE_COUNT = 800; // 50ms at 16kHz, 32-bit mono slots.
int32_t samples[SAMPLE_COUNT];
uint32_t lastErrorLog = 0;

void setup() {
  Serial.begin(115200);
  delay(1500);
  Serial.printf("mic_level boot reset_reason=%d\n", static_cast<int>(esp_reset_reason()));
  Serial.printf("Wi-Fi disabled; IP none (bench). SCK4 WS5 SD6, 16000Hz, SHIFT=%d\n", SHIFT);
  Serial.println("INMP441 VDD=3V3, L/R=GND; CSV columns rms,peak in int16 units.");
  microphone.setPins(4, 5, -1, 6);
  if (!microphone.begin(I2S_MODE_STD, 16000, I2S_DATA_BIT_WIDTH_32BIT,
                        I2S_SLOT_MODE_MONO, MIC_SLOT)) {
    Serial.printf("ERROR I2S init failed code=%d\n", microphone.lastError());
    while (true) delay(1000);
  }
}
void loop() {
  const size_t bytes = microphone.readBytes(reinterpret_cast<char *>(samples), sizeof(samples));
  if (bytes == 0 || bytes % sizeof(int32_t) != 0) {
    if (millis() - lastErrorLog >= 1000) {
      Serial.printf("ERROR I2S read bytes=%u code=%d\n", static_cast<unsigned>(bytes), microphone.lastError());
      lastErrorLog = millis();
    }
    delay(10);
    return;
  }
  const size_t count = bytes / sizeof(int32_t);
  double sumSquares = 0;
  int32_t peak = 0;
  for (size_t i = 0; i < count; ++i) {
    int32_t value = samples[i] >> SHIFT;
    if (value > 32767) value = 32767;
    if (value < -32768) value = -32768;
    const int32_t magnitude = value < 0 ? -value : value;
    if (magnitude > peak) peak = magnitude;
    sumSquares += static_cast<double>(value) * value;
  }
  Serial.printf("%.1f,%ld\n", sqrt(sumSquares / count), static_cast<long>(peak));
}
