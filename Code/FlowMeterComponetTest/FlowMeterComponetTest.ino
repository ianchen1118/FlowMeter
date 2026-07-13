/*
  YF-DN80 basic flow-rate test
  Board: Adafruit Feather M0
  Sensor signal: YF-DN80 yellow wire -> level shifter -> Feather D5

  Default datasheet relationship:
      Frequency (Hz) = 0.5 * Flow rate (L/min)
      Flow rate (L/min) = Frequency / 0.5
*/

const uint8_t FLOW_PIN = 5;

// ============================================================
// TUNING VARIABLES
// Change these later after calibration.
// ============================================================

// Datasheet default for YF-DN80:
// Frequency (Hz) = K_FACTOR * Flow rate (L/min)
float K_FACTOR_HZ_PER_L_MIN = 0.5;

// Optional correction after calibration.
// Leave these at default values for the first test.
float CALIBRATION_SCALE = 1.0;
float FLOW_OFFSET_L_MIN = 0.0;

// Measure and print once per second.
// You can increase this later if readings fluctuate too much.
unsigned long SAMPLE_INTERVAL_MS = 1000;

// Ignore tiny readings caused by electrical noise.
// Leave at 0.0 for the first test so that you can see everything.
float MIN_VALID_FLOW_L_MIN = 0.0;

// ============================================================

volatile unsigned long pulseCount = 0;
unsigned long lastSampleTime = 0;

void countPulse() {
  pulseCount++;
}

void setup() {
  Serial.begin(115200);

  // Wait briefly so the Serial Monitor can connect.
  delay(2000);

  pinMode(FLOW_PIN, INPUT_PULLUP);

  attachInterrupt(
    digitalPinToInterrupt(FLOW_PIN),
    countPulse,
    FALLING
  );

  lastSampleTime = millis();

  Serial.println("YF-DN80 flow meter test started.");
  Serial.println("Default formula: Flow (L/min) = Frequency (Hz) / 0.5");
  Serial.println();
  Serial.println("Pulses | Frequency_Hz | Flow_L_min");
}

void loop() {
  unsigned long currentTime = millis();
  unsigned long elapsedTime = currentTime - lastSampleTime;

  if (elapsedTime >= SAMPLE_INTERVAL_MS) {

    // Copy and reset the pulse count safely.
    noInterrupts();
    unsigned long pulses = pulseCount;
    pulseCount = 0;
    interrupts();

    lastSampleTime = currentTime;

    // Use the real elapsed time rather than assuming exactly 1 second.
    float elapsedSeconds = elapsedTime / 1000.0;

    // Frequency in pulses per second.
    float frequencyHz = pulses / elapsedSeconds;

    // Datasheet method:
    // F = K * Q  ->  Q = F / K
    float flowLMin = frequencyHz / K_FACTOR_HZ_PER_L_MIN;

    // Variables reserved for later calibration.
    flowLMin = flowLMin * CALIBRATION_SCALE + FLOW_OFFSET_L_MIN;

    if (flowLMin < MIN_VALID_FLOW_L_MIN) {
      flowLMin = 0.0;
    }

    Serial.print(pulses);
    Serial.print(" | ");
    Serial.print(frequencyHz, 2);
    Serial.print(" | ");
    Serial.println(flowLMin, 2);
  }
}