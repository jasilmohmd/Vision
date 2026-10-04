// Experimental, build-selected BLE transport. UDP remains the default build.
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLE2902.h>
#include <freertos/semphr.h>

constexpr char BLE_SERVICE[] = "9b930001-8a97-4ed0-9f08-42d26e75baf1";
constexpr char BLE_AUDIO[] = "9b930002-8a97-4ed0-9f08-42d26e75baf1";
constexpr char BLE_LIGHT[] = "9b930003-8a97-4ed0-9f08-42d26e75baf1";
BLEServer *bleServer;
BLECharacteristic *bleAudio;
BLE2902 *bleSubscription;
volatile bool bleConnected = false;
volatile bool bleRestartAdvertising = false;
QueueHandle_t bleLightQueue;
bool bleSendAccepted = false;
BLECharacteristicCallbacks::Status bleSendStatus;
uint32_t bleSendErrors = 0, bleLastSendCode = 0;

class VoiceAudioCallbacks : public BLECharacteristicCallbacks {
  void onStatus(BLECharacteristic *, Status status, uint32_t code) override {
    // Called synchronously by notify(); acceptance means queued, not peer ACK.
    bleSendStatus = status; bleSendAccepted = status == SUCCESS_NOTIFY;
    if (!bleSendAccepted) { ++bleSendErrors; bleLastSendCode = code; }
  }
};

class VoiceBleCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer *) override { bleConnected = true; }
#if defined(CONFIG_BLUEDROID_ENABLED)
  void onConnect(BLEServer *server, esp_ble_gatts_cb_param_t *param) override {
    server->updateConnParams(param->connect.remote_bda, 6, 12, 0, 200);
  }
#elif defined(CONFIG_NIMBLE_ENABLED)
  void onConnect(BLEServer *server, ble_gap_conn_desc *desc) override {
    server->updateConnParams(desc->conn_handle, 6, 12, 0, 200);
  }
#endif
  void onDisconnect(BLEServer *) override {
    bleConnected = false; bleRestartAdvertising = true;
  }
};
class VoiceLightCallbacks : public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic *characteristic) override {
    const String name = characteristic->getValue();
    if (name.length() < 1 || name.length() > 16 || memchr(name.c_str(), 0, name.length())) return;
    Light light;
    if (parseLight(name.c_str(), light)) xQueueSend(bleLightQueue, &light, 0);
  }
};
void bleAudioTask(void *) {
  int32_t raw[SAMPLE_COUNT]; uint8_t pcm[SAMPLE_COUNT * 2], packet[244];
  size_t collected = 0; uint32_t sampleIndex = 0, attempts = 0, report = millis();
  while (true) {
    const size_t bytes = microphone.readBytes(reinterpret_cast<char *>(raw + collected),
                                             (SAMPLE_COUNT - collected) * sizeof(int32_t));
    if (!bytes || bytes % sizeof(int32_t)) {
      collected = 0; vTaskDelay(pdMS_TO_TICKS(10)); continue;
    }
    collected += bytes / sizeof(int32_t);
    if (collected < SAMPLE_COUNT) continue;
    collected = 0; const uint32_t firstSample = sampleIndex; sampleIndex += SAMPLE_COUNT;
    if (!bleConnected || !bleSubscription->getNotifications()) continue;
    const uint16_t mtu = bleServer->getPeerMTU(bleServer->getConnId());
    // Do not burst 64 tiny notifications while the MTU exchange is pending.
    // Drain microphone during negotiation; start only at the trial's required MTU.
    if (mtu < 247) continue;
    const size_t capacity = min(static_cast<size_t>(240), static_cast<size_t>(mtu - 7)) & ~size_t(1);
    for (size_t i = 0; i < SAMPLE_COUNT; ++i) {
      const int32_t value = constrain(raw[i] >> SHIFT, -32768, 32767);
      const uint16_t bits = static_cast<uint16_t>(static_cast<int16_t>(value));
      pcm[2*i] = bits & 0xff; pcm[2*i+1] = bits >> 8;
    }
    for (size_t offset = 0; offset < sizeof(pcm) && bleConnected; offset += capacity) {
      const size_t length = min(capacity, sizeof(pcm) - offset);
      const uint32_t index = firstSample + offset / 2;
      for (unsigned b = 0; b < 4; ++b) packet[b] = index >> (8*b);
      memcpy(packet + 4, pcm + offset, length);
      bleAudio->setValue(packet, length + 4);
      const uint32_t retryStarted = millis();
      do {
        bleSendAccepted = false; bleAudio->notify(); ++attempts;
        if (bleSendAccepted || bleSendStatus != BLECharacteristicCallbacks::ERROR_GATT) break;
        vTaskDelay(max(static_cast<TickType_t>(1), pdMS_TO_TICKS(2)));
      } while (bleConnected && millis() - retryStarted < 8);
      // Let the BLE task drain its queue; notification attempts are not ACKs.
      vTaskDelay(1);
    }
    if (millis() - report >= 10000) {
      logMessage("BLE audio attempts=%lu MTU=%u heap=%u errors=%lu last_code=%lu\n", static_cast<unsigned long>(attempts), mtu, ESP.getFreeHeap(), static_cast<unsigned long>(bleSendErrors), static_cast<unsigned long>(bleLastSendCode));
      report = millis();
    }
  }
}
void startBleTransport() {
  bleLightQueue = xQueueCreate(8, sizeof(Light));
  if (!bleLightQueue) fatal("BLE light queue allocation failed");
  BLEDevice::init("Vision-C3-Voice"); BLEDevice::setMTU(247);
  bleServer = BLEDevice::createServer(); bleServer->setCallbacks(new VoiceBleCallbacks());
  BLEService *service = bleServer->createService(BLE_SERVICE);
  bleAudio = service->createCharacteristic(BLE_AUDIO, BLECharacteristic::PROPERTY_NOTIFY);
  bleAudio->setCallbacks(new VoiceAudioCallbacks());
  bleSubscription = new BLE2902(); bleAudio->addDescriptor(bleSubscription);
  BLECharacteristic *light = service->createCharacteristic(BLE_LIGHT,
    BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_WRITE_NR);
  light->setCallbacks(new VoiceLightCallbacks()); service->start();
  BLEAdvertising *advertising = BLEDevice::getAdvertising();
  advertising->addServiceUUID(BLE_SERVICE); advertising->setScanResponse(true);
  advertising->setMinPreferred(6); advertising->setMaxPreferred(12);
  BLEDevice::startAdvertising();
  if (xTaskCreate(bleAudioTask, "ble_audio", 6144, nullptr, 2, nullptr) != pdPASS)
    fatal("BLE audio task allocation failed");
  logMessage("BLE ready address=%s; UDP disabled in this build\n", BLEDevice::getAddress().toString().c_str());
}
void pollBleTransport() {
  if (bleRestartAdvertising) { bleRestartAdvertising = false; BLEDevice::startAdvertising(); }
  Light light;
  for (unsigned i = 0; i < 8 && xQueueReceive(bleLightQueue, &light, 0) == pdTRUE; ++i) acceptLight(light);
  updateLight(bleConnected); pollLogs(); delay(5);
}
