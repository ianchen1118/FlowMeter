#include <SPI.h>
#include <SD.h>
#include <Wire.h>
#include <RTClib.h>

RTC_DS3231 rtc;

// ============================================================
// PIN SETTINGS
// ============================================================

const uint8_t FLOW_PIN = 11;
const uint8_t SD_CS_PIN = 4;

// ============================================================
// FLOW-METER TUNING VARIABLES
// Change these later after calibration.
// ============================================================

// YF-DN80 datasheet default:
// Frequency (Hz) = K_FACTOR_HZ_PER_L_MIN * Flow rate (L/min)
// Default: F = 0.5 * Q
float K_FACTOR_HZ_PER_L_MIN = 0.5;

// Optional correction after calibration.
// Leave these at the default values for now.
float CALIBRATION_SCALE = 1.0;
float FLOW_OFFSET_L_MIN = 0.0;

// Ignore tiny readings caused by electrical noise.
// Leave at zero during initial testing.
float MIN_VALID_FLOW_L_MIN = 0.0;

// ============================================================
// LOGGER SETTINGS
// ============================================================

// Save one row every 10 seconds.
const uint32_t SAMPLE_INTERVAL_MS = 10000;

// RTC setting:
// Normally leave this false.
// Set true, upload once to set RTC to compile time,
// then change back to false and upload again.
const bool FORCE_SET_RTC_TO_COMPILE_TIME = 0;

// ============================================================
// GLOBAL VARIABLES
// ============================================================

volatile uint32_t pulseCount = 0;

uint32_t lastSampleTime = 0;
uint32_t sampleCount = 0;
float totalVolumeLiters = 0.0;

// 8.3-compatible SD path:
// /YYYYMMDD/HHMMSS.CSV
// Example: /20260609/153245.CSV
char logFilePath[24];

// ============================================================
// INTERRUPT
// ============================================================

void countPulse() {
  pulseCount++;
}

// ============================================================
// SETUP
// ============================================================

void setup() {
  Serial.begin(115200);

  while (!Serial && millis() < 5000) {
    delay(10);
  }

  Serial.println();
  Serial.println("Starting YF-DN80 + DS3231 + SD logger...");

  // ----------------------------
  // Flow meter setup
  // ----------------------------
  pinMode(FLOW_PIN, INPUT_PULLUP);

  attachInterrupt(
    digitalPinToInterrupt(FLOW_PIN),
    countPulse,
    FALLING
  );

  // ----------------------------
  // RTC setup
  // ----------------------------
  Wire.begin();


  if (!rtc.begin()) {
    Serial.println("ERROR: RTC not found. Check VCC, GND, SDA, and SCL.");
    stopProgram();
  }

  ensureRtcRunsOnBattery();

  bool rtcLostPower = rtc.lostPower();

  Serial.print("RTC lost power flag: ");
  Serial.println(rtcLostPower ? "YES" : "NO");

  if (FORCE_SET_RTC_TO_COMPILE_TIME) {
    Serial.println("FORCE_SET_RTC_TO_COMPILE_TIME is enabled.");
    Serial.println("Setting RTC to code compile time.");
    rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
  } 
  else if (rtcLostPower) {
    Serial.println("WARNING: RTC lost backup power.");
    Serial.println("Setting RTC to code compile time.");
    rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
  } 
  else {
    Serial.println("RTC retained its previous time.");
  }

  DateTime startupTime = rtc.now();

  Serial.print("RTC startup time: ");
  printTimestampToSerial(startupTime);
  Serial.println();

  // ----------------------------
  // SD card setup
  // ----------------------------
  Serial.println("Initializing SD card...");

  if (!SD.begin(SD_CS_PIN)) {
    Serial.println("ERROR: SD card initialization failed.");
    stopProgram();
  }

  Serial.println("SD card initialized.");

  // Create a new CSV file for this power-on session.
  DateTime sessionStart = rtc.now();

  if (!createNewSessionFile(sessionStart)) {
    Serial.println("ERROR: Could not create a new session CSV file.");
    stopProgram();
  }

  lastSampleTime = millis();

  Serial.print("Logger ready. Writing to: ");
  Serial.println(logFilePath);

  Serial.println(
    "timestamp | session_elapsed_s | sample_number | pulses | "
    "frequency_hz | flow_l_min | total_volume_l"
  );
}

// ============================================================
// MAIN LOOP
// ============================================================

void loop() {
  uint32_t currentTime = millis();
  uint32_t elapsedTimeMs = currentTime - lastSampleTime;

  if (elapsedTimeMs >= SAMPLE_INTERVAL_MS) {
    lastSampleTime = currentTime;

    // Copy and reset pulse count safely.
    noInterrupts();
    uint32_t pulses = pulseCount;
    pulseCount = 0;
    interrupts();

    float elapsedSeconds = elapsedTimeMs / 1000.0;
    float frequencyHz = pulses / elapsedSeconds;

    // Datasheet method:
    // F = K * Q  ->  Q = F / K
    float flowLMin = frequencyHz / K_FACTOR_HZ_PER_L_MIN;

    // Reserved for later calibration.
    flowLMin = flowLMin * CALIBRATION_SCALE + FLOW_OFFSET_L_MIN;

    if (flowLMin < MIN_VALID_FLOW_L_MIN) {
      flowLMin = 0.0;
    }

    // L/min * seconds / 60 = liters accumulated during this sample.
    float sampleVolumeLiters = flowLMin * elapsedSeconds / 60.0;
    totalVolumeLiters += sampleVolumeLiters;

    sampleCount++;

    DateTime now = rtc.now();
    uint32_t sessionElapsedSeconds = millis() / 1000;

    if (!appendCsvRow(
          now,
          sessionElapsedSeconds,
          sampleCount,
          pulses,
          frequencyHz,
          flowLMin,
          totalVolumeLiters
        )) {
      Serial.println("ERROR: Could not append data to the CSV file.");
      return;
    }

    printSerialRow(
      now,
      sessionElapsedSeconds,
      sampleCount,
      pulses,
      frequencyHz,
      flowLMin,
      totalVolumeLiters
    );
  }
}

// ============================================================
// SESSION FILE CREATION
// ============================================================

bool createNewSessionFile(const DateTime &sessionStart) {
  char dateFolder[10];

  snprintf(
    dateFolder,
    sizeof(dateFolder),
    "/%04d%02d%02d",
    sessionStart.year(),
    sessionStart.month(),
    sessionStart.day()
  );

  if (!SD.exists(dateFolder)) {
    if (!SD.mkdir(dateFolder)) {
      Serial.println("ERROR: Could not create date folder.");
      return false;
    }
  }

  snprintf(
    logFilePath,
    sizeof(logFilePath),
    "%s/%02d%02d%02d.CSV",
    dateFolder,
    sessionStart.hour(),
    sessionStart.minute(),
    sessionStart.second()
  );

  if (SD.exists(logFilePath)) {
    Serial.println("ERROR: A session file with the same timestamp already exists.");
    return false;
  }

  File file = SD.open(logFilePath, FILE_WRITE);

  if (!file) {
    return false;
  }

  // Store session information and CSV header.
  file.print("# session_start=");
  printTimestampToFile(file, sessionStart);
  file.println();

  file.println(
    "timestamp,session_elapsed_seconds,sample_number,pulses,"
    "frequency_hz,flow_rate_l_min,total_volume_l"
  );

  // Close immediately so the file exists safely on the card.
  file.close();

  return true;
}
// ============================================================
// CSV WRITING
// ============================================================

bool appendCsvRow(
  const DateTime &now,
  uint32_t sessionElapsedSeconds,
  uint32_t currentSampleCount,
  uint32_t pulses,
  float frequencyHz,
  float flowLMin,
  float totalLiters
) {
  File file = SD.open(logFilePath, FILE_WRITE);

  if (!file) {
    return false;
  }

  printTimestampToFile(file, now);
  file.print(",");
  file.print(sessionElapsedSeconds);
  file.print(",");
  file.print(currentSampleCount);
  file.print(",");
  file.print(pulses);
  file.print(",");
  file.print(frequencyHz, 3);
  file.print(",");
  file.print(flowLMin, 3);
  file.print(",");
  file.println(totalLiters, 4);

  // Close after every row.
  // This preserves the latest successfully written row if power is removed.
  file.close();

  return true;
}

// ============================================================
// SERIAL OUTPUT
// ============================================================

void printSerialRow(
  const DateTime &now,
  uint32_t sessionElapsedSeconds,
  uint32_t currentSampleCount,
  uint32_t pulses,
  float frequencyHz,
  float flowLMin,
  float totalLiters
) {
  printTimestampToSerial(now);
  Serial.print(" | ");
  Serial.print(sessionElapsedSeconds);
  Serial.print(" | ");
  Serial.print(currentSampleCount);
  Serial.print(" | ");
  Serial.print(pulses);
  Serial.print(" | ");
  Serial.print(frequencyHz, 3);
  Serial.print(" | ");
  Serial.print(flowLMin, 3);
  Serial.print(" | ");
  Serial.println(totalLiters, 4);
}

// ============================================================
// TIMESTAMP HELPERS
// ============================================================

void printTimestampToFile(File &file, const DateTime &now) {
  file.print(now.year());
  file.print("-");
  printTwoDigitsToFile(file, now.month());
  file.print("-");
  printTwoDigitsToFile(file, now.day());
  file.print(" ");
  printTwoDigitsToFile(file, now.hour());
  file.print(":");
  printTwoDigitsToFile(file, now.minute());
  file.print(":");
  printTwoDigitsToFile(file, now.second());
}

void printTimestampToSerial(const DateTime &now) {
  Serial.print(now.year());
  Serial.print("-");
  printTwoDigitsToSerial(now.month());
  Serial.print("-");
  printTwoDigitsToSerial(now.day());
  Serial.print(" ");
  printTwoDigitsToSerial(now.hour());
  Serial.print(":");
  printTwoDigitsToSerial(now.minute());
  Serial.print(":");
  printTwoDigitsToSerial(now.second());
}

void printTwoDigitsToFile(File &file, int value) {
  if (value < 10) {
    file.print("0");
  }

  file.print(value);
}

void printTwoDigitsToSerial(int value) {
  if (value < 10) {
    Serial.print("0");
  }

  Serial.print(value);
}

// ============================================================
// STOP HELPER
// ============================================================

void stopProgram() {
  while (true) {
    delay(1000);
  }
}

void ensureRtcRunsOnBattery() {
  Wire.beginTransmission(0x68);
  Wire.write(0x0E); // DS3231 control register
  Wire.endTransmission();

  Wire.requestFrom(0x68, 1);

  if (Wire.available()) {
    uint8_t controlRegister = Wire.read();

    // Clear EOSC bit 7:
    // 0 = oscillator continues running on VBAT
    controlRegister &= ~(1 << 7);

    Wire.beginTransmission(0x68);
    Wire.write(0x0E);
    Wire.write(controlRegister);
    Wire.endTransmission();
  }
}
