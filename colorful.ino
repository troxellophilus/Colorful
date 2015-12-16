/******************************************************************************
 * Colorful Firmware by Drew Troxell
 * 
 * Based on:
 * ISL29125_basics.ino by Jordan McConnell @ SparkFun Electronics
 * https://github.com/sparkfun/ISL29125_Breakout
******************************************************************************/

#include <String.h>
#include <Wire.h>
#include "SFE_ISL29125.h"

#define DISCOVER       440
#define AWAIT_TRIGGER  441
#define FIRE_ZE_COLORS 442

// Declare sensor object
SFE_ISL29125 RGB_sensor;

/*
 * Setup
 */
void setup() {
  // Initialize serial communication
  Serial.begin(115200);

  // Initialize the ISL29125 with simple configuration so it starts sampling
  if (RGB_sensor.init()) {
    Serial.println("Sensor initialization successful!\n\r");
  }
}

/*
 * discover()
 * Handshake w/ the desktop program.
 * return true if hand shook
 */
uint16_t discover(char *handshake) {
  String rcv_str;
  if (Serial.available() > 0) {
    rcv_str = Serial.readString();
    if (rcv_str.equals(String(handshake))) {
      Serial.println("{\"device_name\":\"Colorful Color Reader\",\"version\":0.1,\"author\":\"Drew Troxell\"}");
      return AWAIT_TRIGGER;
    }
  }
  return DISCOVER;
}

/*
 * await_trigger()
 * Return true if 4 byte trigger received.
 */
uint16_t await_trigger(char *trigger) {
  String rcv_str;
  if (Serial.available() > 0) {
    rcv_str = Serial.readString();
    if (rcv_str.equals(String(trigger))) return FIRE_ZE_COLORS;
  }
  return AWAIT_TRIGGER;
}

/*
 * read_colors()
 * Read sensor values for each color and write them to a string as a json object
 */
void read_colors(char* json) {
  unsigned int red = RGB_sensor.readRed();
  unsigned int green = RGB_sensor.readGreen();
  unsigned int blue = RGB_sensor.readBlue();
  sprintf(json, "{\"red\":%d,\"blue\":%d,\"green\":%d}", red, green, blue);
}

/*
 * Main Loop
 */
void loop() {
  static uint16_t state = DISCOVER;
  char json[128];
  switch (state) {
    case DISCOVER:
      state = discover("connect colorful");
      delay(2000);
      break;
    case AWAIT_TRIGGER:
      state = await_trigger("run colorful");
      delay(200);
      break;
    case FIRE_ZE_COLORS:
      read_colors(json);
      Serial.println(json);
      state = AWAIT_TRIGGER;
      delay(200);
      break;
    default:
      state = DISCOVER;
      delay(2000);
  }
}

