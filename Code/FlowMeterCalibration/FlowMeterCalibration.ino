/*
  YF-DN80 flow meter multi-trial calibration tool
  Board: Adafruit Feather M0
  Sensor signal: YF-DN80 yellow wire -> level shifter -> Feather D11

  Calibration method:
    1. Enter the number of calibration trials in Serial Monitor.
    2. For each trial, put the outlet into a measuring container.
    3. Send "s" to start counting pulses.
    4. Run a measured amount of water through the sensor.
    5. Send "e" to end that trial.
    6. Send "v <liters>" with the measured water volume.

  The final recommended calibration uses all trials together:
    combined_pulses_per_liter = sum(total_pulses) / sum(measured_liters)
    K_FACTOR_HZ_PER_L_MIN = combined_pulses_per_liter / 60

  This is a weighted calibration, so larger-volume trials naturally count more.
  The K factor matches the logger formula:
    Frequency (Hz) = K_FACTOR_HZ_PER_L_MIN * Flow rate (L/min)
*/

const uint8_t FLOW_PIN = 11;
const uint8_t MAX_TRIALS = 20;

// Keep this equal to the current datasheet/default value in the logger.
const float CURRENT_K_FACTOR_HZ_PER_L_MIN = 0.5;

// Print live pulse totals at this interval while a calibration run is active.
const uint32_t LIVE_PRINT_INTERVAL_MS = 1000;

volatile uint32_t pulseCount = 0;

bool trialCountConfigured = false;
bool runActive = false;
bool runComplete = false;

uint8_t targetTrialCount = 0;
uint8_t completedTrialCount = 0;

uint32_t runStartMs = 0;
uint32_t runEndMs = 0;
uint32_t lastLivePrintMs = 0;
uint32_t completedRunPulses = 0;

uint32_t trialPulses[MAX_TRIALS];
float trialLiters[MAX_TRIALS];
float trialSeconds[MAX_TRIALS];
float trialKFactor[MAX_TRIALS];

void countPulse() {
  pulseCount++;
}

void setup() {
  Serial.begin(115200);

  while (!Serial && millis() < 5000) {
    delay(10);
  }

  pinMode(FLOW_PIN, INPUT_PULLUP);

  attachInterrupt(
    digitalPinToInterrupt(FLOW_PIN),
    countPulse,
    FALLING
  );

  printIntro();
}

void loop() {
  handleSerialInput();
  printLiveStatus();
}

void handleSerialInput() {
  if (!Serial.available()) {
    return;
  }

  String command = Serial.readStringUntil('\n');
  command.trim();

  if (command.length() == 0) {
    return;
  }

  if (!trialCountConfigured) {
    configureTrialCount(command);
    return;
  }

  char action = tolower(command.charAt(0));

  if (action == 's') {
    startRun();
  } else if (action == 'e') {
    endRun();
  } else if (action == 'v') {
    float measuredLiters = parseVolumeLiters(command);
    recordCompletedRun(measuredLiters);
  } else if (action == 'p') {
    printFinalSummary();
  } else if (action == 'r') {
    resetAll();
  } else if (action == 'h') {
    printHelp();
  } else {
    Serial.println("Unknown command. Send h for help.");
  }
}

void configureTrialCount(const String &command) {
  int requestedTrialCount = command.toInt();

  if (requestedTrialCount < 1 || requestedTrialCount > MAX_TRIALS) {
    Serial.print("Enter a trial count from 1 to ");
    Serial.print(MAX_TRIALS);
    Serial.println(".");
    Serial.println("Example: 5");
    return;
  }

  clearStoredTrials();

  targetTrialCount = requestedTrialCount;
  trialCountConfigured = true;

  Serial.println();
  Serial.print("Configured trial count: ");
  Serial.println(targetTrialCount);
  printNextTrialPrompt();
}

void startRun() {
  if (!trialCountConfigured) {
    Serial.println("Enter the number of trials first.");
    return;
  }

  if (completedTrialCount >= targetTrialCount) {
    Serial.println("All trials are complete. Send p to print the final summary or r to restart.");
    return;
  }

  if (runActive) {
    Serial.println("A run is already active. Send e to end it.");
    return;
  }

  if (runComplete) {
    Serial.println("This run is waiting for volume. Send v <liters> before starting the next run.");
    return;
  }

  noInterrupts();
  pulseCount = 0;
  interrupts();

  runActive = true;
  runComplete = false;
  completedRunPulses = 0;
  runStartMs = millis();
  runEndMs = runStartMs;
  lastLivePrintMs = runStartMs;

  Serial.println();
  Serial.print("Trial ");
  Serial.print(completedTrialCount + 1);
  Serial.print(" of ");
  Serial.print(targetTrialCount);
  Serial.println(" started.");
  Serial.println("Run water through the sensor, then send e to end this trial.");
}

void endRun() {
  if (!runActive) {
    Serial.println("No active run. Send s to start.");
    return;
  }

  runEndMs = millis();

  noInterrupts();
  completedRunPulses = pulseCount;
  interrupts();

  runActive = false;
  runComplete = true;

  Serial.println();
  Serial.println("Trial ended.");
  printRunSummary();
  Serial.println("Now send v <liters>, for example: v 18.92");
}

void recordCompletedRun(float measuredLiters) {
  if (!runComplete) {
    Serial.println("No completed run is waiting for volume. Send s to start and e to end first.");
    return;
  }

  if (completedRunPulses == 0) {
    Serial.println("No pulses were recorded. Check wiring, pin, and interrupt setup.");
    runComplete = false;
    return;
  }

  if (measuredLiters <= 0.0) {
    Serial.println("Invalid volume. Send a positive value, for example: v 18.92");
    return;
  }

  uint8_t trialIndex = completedTrialCount;
  float elapsedSeconds = getCompletedRunElapsedSeconds();
  float pulsesPerLiter = completedRunPulses / measuredLiters;

  trialPulses[trialIndex] = completedRunPulses;
  trialLiters[trialIndex] = measuredLiters;
  trialSeconds[trialIndex] = elapsedSeconds;
  trialKFactor[trialIndex] = pulsesPerLiter / 60.0;

  completedTrialCount++;
  runComplete = false;

  printSingleTrialResult(trialIndex);

  if (completedTrialCount >= targetTrialCount) {
    printFinalSummary();
  } else {
    printNextTrialPrompt();
  }
}

float parseVolumeLiters(const String &command) {
  int separatorIndex = command.indexOf(' ');

  if (separatorIndex < 0) {
    return 0.0;
  }

  String valueText = command.substring(separatorIndex + 1);
  valueText.trim();

  return valueText.toFloat();
}

void resetAll() {
  noInterrupts();
  pulseCount = 0;
  interrupts();

  clearStoredTrials();

  trialCountConfigured = false;
  targetTrialCount = 0;

  Serial.println();
  Serial.println("Calibration state reset.");
  printTrialCountPrompt();
}

void clearStoredTrials() {
  runActive = false;
  runComplete = false;
  completedTrialCount = 0;
  completedRunPulses = 0;
  runStartMs = 0;
  runEndMs = 0;
  lastLivePrintMs = 0;

  for (uint8_t i = 0; i < MAX_TRIALS; i++) {
    trialPulses[i] = 0;
    trialLiters[i] = 0.0;
    trialSeconds[i] = 0.0;
    trialKFactor[i] = 0.0;
  }
}

void printLiveStatus() {
  if (!runActive) {
    return;
  }

  uint32_t currentMs = millis();

  if (currentMs - lastLivePrintMs < LIVE_PRINT_INTERVAL_MS) {
    return;
  }

  lastLivePrintMs = currentMs;

  noInterrupts();
  uint32_t pulses = pulseCount;
  interrupts();

  float elapsedSeconds = (currentMs - runStartMs) / 1000.0;

  Serial.print("Running | trial=");
  Serial.print(completedTrialCount + 1);
  Serial.print("/");
  Serial.print(targetTrialCount);
  Serial.print(" | elapsed_s=");
  Serial.print(elapsedSeconds, 1);
  Serial.print(" | pulses=");
  Serial.println(pulses);
}

void printRunSummary() {
  Serial.print("Total pulses: ");
  Serial.println(completedRunPulses);

  Serial.print("Elapsed time (s): ");
  Serial.println(getCompletedRunElapsedSeconds(), 3);
}

void printSingleTrialResult(uint8_t trialIndex) {
  float pulsesPerLiter = trialPulses[trialIndex] / trialLiters[trialIndex];
  float litersPerPulse = trialLiters[trialIndex] / trialPulses[trialIndex];
  float averageFlowLMin = trialLiters[trialIndex] / trialSeconds[trialIndex] * 60.0;

  Serial.println();
  Serial.print("Trial ");
  Serial.print(trialIndex + 1);
  Serial.println(" recorded");
  Serial.println("----------------");

  Serial.print("Measured volume (L): ");
  Serial.println(trialLiters[trialIndex], 4);

  Serial.print("Total pulses: ");
  Serial.println(trialPulses[trialIndex]);

  Serial.print("Elapsed time (s): ");
  Serial.println(trialSeconds[trialIndex], 3);

  Serial.print("Average flow (L/min): ");
  Serial.println(averageFlowLMin, 3);

  Serial.print("Pulses per liter: ");
  Serial.println(pulsesPerLiter, 4);

  Serial.print("Liters per pulse: ");
  Serial.println(litersPerPulse, 8);

  Serial.print("Trial K_FACTOR_HZ_PER_L_MIN: ");
  Serial.println(trialKFactor[trialIndex], 6);
}

void printFinalSummary() {
  if (!trialCountConfigured || completedTrialCount == 0) {
    Serial.println("No recorded trials yet.");
    return;
  }

  uint32_t totalPulses = 0;
  float totalLiters = 0.0;
  float totalSeconds = 0.0;
  float simpleKSum = 0.0;

  for (uint8_t i = 0; i < completedTrialCount; i++) {
    totalPulses += trialPulses[i];
    totalLiters += trialLiters[i];
    totalSeconds += trialSeconds[i];
    simpleKSum += trialKFactor[i];
  }

  float combinedPulsesPerLiter = totalPulses / totalLiters;
  float combinedKFactor = combinedPulsesPerLiter / 60.0;
  float simpleAverageKFactor = simpleKSum / completedTrialCount;
  float suggestedCalibrationScale = CURRENT_K_FACTOR_HZ_PER_L_MIN / combinedKFactor;
  float averageFlowLMin = totalLiters / totalSeconds * 60.0;

  Serial.println();
  Serial.println("Final multi-trial calibration");
  Serial.println("=============================");

  Serial.print("Completed trials: ");
  Serial.print(completedTrialCount);
  Serial.print(" of ");
  Serial.println(targetTrialCount);

  Serial.print("Total measured volume (L): ");
  Serial.println(totalLiters, 4);

  Serial.print("Total pulses: ");
  Serial.println(totalPulses);

  Serial.print("Total elapsed time (s): ");
  Serial.println(totalSeconds, 3);

  Serial.print("Combined average flow (L/min): ");
  Serial.println(averageFlowLMin, 3);

  Serial.print("Combined pulses per liter: ");
  Serial.println(combinedPulsesPerLiter, 4);

  Serial.println();
  Serial.println("Trial comparison vs combined K:");

  for (uint8_t i = 0; i < completedTrialCount; i++) {
    float differencePercent = (trialKFactor[i] - combinedKFactor) / combinedKFactor * 100.0;

    Serial.print("  Trial ");
    Serial.print(i + 1);
    Serial.print(": K=");
    Serial.print(trialKFactor[i], 6);
    Serial.print(" | diff_pct=");
    Serial.println(differencePercent, 2);
  }

  Serial.println();
  Serial.println("Use this recommended value in the logger:");
  Serial.print("K_FACTOR_HZ_PER_L_MIN = ");
  Serial.print(combinedKFactor, 6);
  Serial.println(";");

  Serial.println();
  Serial.println("For comparison only:");
  Serial.print("Simple average K_FACTOR_HZ_PER_L_MIN = ");
  Serial.print(simpleAverageKFactor, 6);
  Serial.println(";");

  Serial.print("CALIBRATION_SCALE = ");
  Serial.print(suggestedCalibrationScale, 6);
  Serial.println(";  // only if you keep the current K factor");

  Serial.println();
  Serial.println("Best option: update K_FACTOR_HZ_PER_L_MIN and keep CALIBRATION_SCALE = 1.0.");
  Serial.println("Send r to restart with a new trial count, or p to print this summary again.");
}

float getCompletedRunElapsedSeconds() {
  uint32_t elapsedMs = runEndMs - runStartMs;

  if (elapsedMs == 0) {
    return 0.001;
  }

  return elapsedMs / 1000.0;
}

void printIntro() {
  Serial.println();
  Serial.println("YF-DN80 flow meter multi-trial calibration tool");
  Serial.println("FLOW_PIN = 11");
  printHelp();
  printTrialCountPrompt();
}

void printTrialCountPrompt() {
  Serial.print("Enter number of trials, 1 to ");
  Serial.print(MAX_TRIALS);
  Serial.println(".");
  Serial.println("Example: 5");
}

void printNextTrialPrompt() {
  Serial.println();
  Serial.print("Ready for trial ");
  Serial.print(completedTrialCount + 1);
  Serial.print(" of ");
  Serial.print(targetTrialCount);
  Serial.println(".");
  Serial.println("Send s to start.");
}

void printHelp() {
  Serial.println();
  Serial.println("Workflow:");
  Serial.println("  1) Enter trial count first, for example: 5");
  Serial.println("  2) For each trial: send s, run water, send e, then send v <liters>");
  Serial.println("  3) After the final trial, use the combined K factor printed by the tool");
  Serial.println();
  Serial.println("Commands after trial count is configured:");
  Serial.println("  s            start the current trial");
  Serial.println("  e            end the current trial");
  Serial.println("  v <liters>   record measured volume for the completed trial");
  Serial.println("  p            print final summary again");
  Serial.println("  r            reset all trials and choose a new trial count");
  Serial.println("  h            show this help");
  Serial.println();
  Serial.println("Example trial sequence:");
  Serial.println("  5");
  Serial.println("  s");
  Serial.println("  e");
  Serial.println("  v 18.92");
}
