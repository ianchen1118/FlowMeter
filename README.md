# FlowMeter

Arduino sketches for developing and testing a YF-DN80 flow meter logger.

## Hardware

- Adafruit Feather M0
- YF-DN80 flow meter
- DS3231 RTC
- SD card module
- Level shifter for the flow meter signal line

## Sketches

- `Code/FlowMeterComponetTest/FlowMeterComponetTest.ino`  
  Basic flow meter pulse counting and flow-rate calculation test.

- `Code/FlowMeterFirst/FlowMeterFirst.ino`  
  Main logger sketch. Combines flow meter input, DS3231 timestamps, SD card CSV logging, and total volume accumulation.

- `Code/FlowMeterCalibration/FlowMeterCalibration.ino` - Interactive serial calibration tool for calculating the flow meter K factor from multiple pulse-count and measured-volume trials.

- `Code/FlowMeterTest/FlowMeterTest.ino`  
  SD card write test that creates `dummy.csv` and records dummy flow values.

- `Code/RTCTest/RTCTest.ino`  
  DS3231 RTC setup and serial timestamp test.

## Notes

- The default YF-DN80 calculation uses `Frequency (Hz) = 0.5 * Flow rate (L/min)`.
- Calibration values are exposed in the sketches and should be adjusted after field testing.
- `FlowMeterComponetTest` appears to be a legacy folder name and may be renamed later.
