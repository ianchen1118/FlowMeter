#include <SPI.h>
#include <SD.h>

const uint8_t SD_CS_PIN = 4;
const uint32_t SAMPLE_INTERVAL_MS = 1000;
const uint16_t TOTAL_SAMPLES = 30;

uint32_t lastSampleTime = 0;
uint16_t sampleCount = 0;

void setup() {
  Serial.begin(115200);

  while (!Serial && millis() < 5000) {
    delay(10);
  }

  Serial.println("Initializing SD card...");

  if (!SD.begin(SD_CS_PIN)) {
    Serial.println("ERROR: SD card initialization failed.");
    while (true) {
      delay(1000);
    }
  }

  Serial.println("SD card initialized.");

  // Remove the old test file so every test starts clean.
  if (SD.exists("dummy.csv")) {
    SD.remove("dummy.csv");
  }

  File file = SD.open("dummy.csv", FILE_WRITE);

  if (!file) {
    Serial.println("ERROR: Could not create dummy.csv.");
    while (true) {
      delay(1000);
    }
  }

  file.println("elapsed_seconds,dummy_flow_rate_lpm");
  file.close();

  Serial.println("Created dummy.csv.");
  Serial.println("Collecting 30 seconds of dummy data...");

  lastSampleTime = millis();
}

void loop() {
  if (sampleCount >= TOTAL_SAMPLES) {
    Serial.println("Collection complete.");
    Serial.println("You may power off the board and remove the SD card.");

    while (true) {
      delay(1000);
    }
  }

  uint32_t currentTime = millis();

  if (currentTime - lastSampleTime >= SAMPLE_INTERVAL_MS) {
    lastSampleTime += SAMPLE_INTERVAL_MS;

    float dummyFlowRate = 10.0 + 0.5 * (sampleCount % 10);

    File file = SD.open("dummy.csv", FILE_WRITE);

    if (!file) {
      Serial.println("ERROR: Could not open dummy.csv.");
      return;
    }

    file.print(sampleCount + 1);
    file.print(",");
    file.println(dummyFlowRate, 2);

    file.close();

    Serial.print("Saved sample ");
    Serial.print(sampleCount + 1);
    Serial.print(": ");
    Serial.print(dummyFlowRate, 2);
    Serial.println(" L/min");

    sampleCount++;
  }
}