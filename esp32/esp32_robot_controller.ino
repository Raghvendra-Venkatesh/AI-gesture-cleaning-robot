#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>

// Choose one mode. Do not commit real router credentials.
#define WIFI_AP_MODE true

const char* AP_SSID = "GestureRobot";
const char* AP_PASSWORD = "change-this-password";
const char* STA_SSID = "your-router-ssid";
const char* STA_PASSWORD = "your-router-password";

// One L298N channel drives the two motors on each side, wired in parallel.
struct SidePins {
  int input1;
  int input2;
  bool reversed;
};

const SidePins leftSide = {26, 27, false};
const SidePins rightSide = {32, 33, true};

WebServer server(80);

const unsigned long WATCHDOG_MS = 2000;
int motorSpeed = 150;
String currentCommand = "STOP";
unsigned long lastCommandMs = 0;
int leftInput1Duty = 0;
int leftInput2Duty = 0;
int rightInput1Duty = 0;
int rightInput2Duty = 0;

bool isValidCommand(const String& cmd) {
  return cmd == "FORWARD" || cmd == "BACKWARD" || cmd == "LEFT" || cmd == "RIGHT" || cmd == "STOP";
}

void setupSide(const SidePins& side) {
  pinMode(side.input1, OUTPUT);
  pinMode(side.input2, OUTPUT);
  analogWrite(side.input1, 0);
  analogWrite(side.input2, 0);
}

void driveSide(const SidePins& side, int direction, int speedValue, int& input1Duty, int& input2Duty) {
  if (side.reversed) {
    direction = -direction;
  }
  if (direction > 0 && speedValue > 0) {
    input1Duty = speedValue;
    input2Duty = 0;
  } else if (direction < 0 && speedValue > 0) {
    input1Duty = 0;
    input2Duty = speedValue;
  } else {
    input1Duty = 0;
    input2Duty = 0;
  }
  analogWrite(side.input1, input1Duty);
  analogWrite(side.input2, input2Duty);
}

void stopMotors() {
  driveSide(leftSide, 0, 0, leftInput1Duty, leftInput2Duty);
  driveSide(rightSide, 0, 0, rightInput1Duty, rightInput2Duty);
  currentCommand = "STOP";
}

void applyCommand(const String& cmd) {
  if (cmd == "FORWARD") {
    driveSide(leftSide, 1, motorSpeed, leftInput1Duty, leftInput2Duty);
    driveSide(rightSide, 1, motorSpeed, rightInput1Duty, rightInput2Duty);
  } else if (cmd == "BACKWARD") {
    driveSide(leftSide, -1, motorSpeed, leftInput1Duty, leftInput2Duty);
    driveSide(rightSide, -1, motorSpeed, rightInput1Duty, rightInput2Duty);
  } else if (cmd == "LEFT") {
    driveSide(leftSide, -1, motorSpeed, leftInput1Duty, leftInput2Duty);
    driveSide(rightSide, 1, motorSpeed, rightInput1Duty, rightInput2Duty);
  } else if (cmd == "RIGHT") {
    driveSide(leftSide, 1, motorSpeed, leftInput1Duty, leftInput2Duty);
    driveSide(rightSide, -1, motorSpeed, rightInput1Duty, rightInput2Duty);
  } else {
    stopMotors();
  }
  currentCommand = cmd;
  lastCommandMs = millis();
}

void sendJson(bool ok, const String& message) {
  String json = "{\"ok\":";
  json += ok ? "true" : "false";
  json += ",\"command\":\"" + currentCommand + "\"";
  json += ",\"message\":\"" + message + "\"";
  json += ",\"speed\":" + String(motorSpeed);
  json += ",\"command_age_ms\":" + String(millis() - lastCommandMs);
  json += ",\"left_input_pwm\":[" + String(leftInput1Duty) + "," + String(leftInput2Duty) + "]";
  json += ",\"right_input_pwm\":[" + String(rightInput1Duty) + "," + String(rightInput2Duty) + "]";
  json += "}";
  server.send(ok ? 200 : 400, "application/json", json);
}

void handleCommand() {
  if (!server.hasArg("cmd")) {
    stopMotors();
    sendJson(false, "missing cmd");
    return;
  }

  String cmd = server.arg("cmd");
  cmd.toUpperCase();
  if (!isValidCommand(cmd)) {
    stopMotors();
    sendJson(false, "invalid cmd");
    return;
  }

  applyCommand(cmd);
  sendJson(true, "accepted");
}

void handleStatus() {
  sendJson(true, "status");
}

void handleSpeed() {
  if (!server.hasArg("value")) {
    sendJson(false, "missing value");
    return;
  }
  String valueArg = server.arg("value");
  if (valueArg.length() == 0) {
    sendJson(false, "speed must be 0..255");
    return;
  }
  for (unsigned int i = 0; i < valueArg.length(); i++) {
    if (!isDigit(valueArg.charAt(i))) {
      sendJson(false, "speed must be 0..255");
      return;
    }
  }
  int value = valueArg.toInt();
  if (value < 0 || value > 255) {
    sendJson(false, "speed must be 0..255");
    return;
  }
  motorSpeed = value;
  if (currentCommand != "STOP") {
    applyCommand(currentCommand);
  }
  sendJson(true, "speed updated");
}

void setupWifi() {
  if (WIFI_AP_MODE) {
    WiFi.mode(WIFI_AP);
    WiFi.softAP(AP_SSID, AP_PASSWORD);
    Serial.print("AP IP: ");
    Serial.println(WiFi.softAPIP());
  } else {
    WiFi.mode(WIFI_STA);
    WiFi.begin(STA_SSID, STA_PASSWORD);
    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
    }
    Serial.print("STA IP: ");
    Serial.println(WiFi.localIP());
  }
}

void setup() {
  Serial.begin(115200);
  setupSide(leftSide);
  setupSide(rightSide);
  stopMotors();

  setupWifi();
  server.on("/command", HTTP_GET, handleCommand);
  server.on("/status", HTTP_GET, handleStatus);
  server.on("/speed", HTTP_GET, handleSpeed);
  server.begin();
  lastCommandMs = millis();
}

void loop() {
  server.handleClient();
  if (currentCommand != "STOP" && millis() - lastCommandMs > WATCHDOG_MS) {
    stopMotors();
  }
}
