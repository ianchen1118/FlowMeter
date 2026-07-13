#include <Wire.h>
#include <RTClib.h>

RTC_DS3231 rtc;

void setup() {
  Serial.begin(115200);
  delay(2000);

  Wire.begin();

  if (!rtc.begin()) {
    Serial.println("RTC not found. Check VCC, GND, SDA, and SCL.");
    while (1) {
      delay(10);
    }
  }

  rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));

  if (rtc.lostPower()) {
    Serial.println("RTC lost power. Setting time to compile time.");

    // Set RTC using the date and time when this code was compiled.
    rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
  }

  Serial.println("RTC test started.");
}

void loop() {
  DateTime now = rtc.now();

  Serial.print(now.year());
  Serial.print("-");
  printTwoDigits(now.month());
  Serial.print("-");
  printTwoDigits(now.day());
  Serial.print(" ");

  printTwoDigits(now.hour());
  Serial.print(":");
  printTwoDigits(now.minute());
  Serial.print(":");
  printTwoDigits(now.second());

  Serial.println();

  delay(1000);
}

void printTwoDigits(int value) {
  if (value < 10) {
    Serial.print("0");
  }

  Serial.print(value);
}