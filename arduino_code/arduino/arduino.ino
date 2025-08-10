#include <Servo.h>
#include <ESP8266WiFi.h>
#include <espnow.h>

#define ENA D1  // PWM pin for speed control
#define IN1 D2  // Direction control
#define IN2 D3  // Grounded, no reverse needed

// Create servo objects
Servo servoX;
Servo servoY;

// Servo angle range
const int minAngle = 0;
const int maxAngle = 180;

// Screen dimensions or camera resolution (example: 640x480)
const int screenWidth = 640;
const int screenHeight = 480;

// Pin assignments
const int servoXPin = D5; // Adjust based on your wiring
const int servoYPin = D0;

// Peer MAC address (replace with the MAC address of the second NodeMCU)
uint8_t peerMACAddress[] = {0x98, 0xF4, 0xAB, 0xD5, 0xD6, 0x26};
bool espNowInitialized = false;

void onDataSent(uint8_t *mac_addr, uint8_t sendStatus) {
  Serial.print("ESP-NOW Send Status: ");
  Serial.println(sendStatus == 0 ? "Success" : "Fail");
}

void setup() {
  pinMode(D8, OUTPUT); // Set D8 as an output pin
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);

  // Set initial direction
  digitalWrite(IN1, HIGH);  // Forward direction
  digitalWrite(IN2, LOW);   // Ground IN2 to prevent reverse

  // Attach servos to their respective pins
  servoX.attach(servoXPin);
  servoY.attach(servoYPin);

  // Set initial servo positions to midpoints
  servoX.write(90);
  servoY.write(90);

  // Initialize serial communication
  Serial.begin(9600);

  // Initialize ESP-NOW
  WiFi.mode(WIFI_STA);
  if (esp_now_init() == 0) {
    Serial.println("ESP-NOW initialized successfully.");
    esp_now_register_send_cb(onDataSent);
    esp_now_add_peer(peerMACAddress, ESP_NOW_ROLE_COMBO, 1, NULL, 0);
    espNowInitialized = true;
  } else {
    Serial.println("ESP-NOW initialization failed!");
  }
}

void loop() {
  // Check if data is available on the serial port
  if (Serial.available() > 0) {
    // Read the incoming data
    String input = Serial.readStringUntil('\n'); // Read until newline
    input.trim(); // Remove any whitespace

    // Check if the command is "runesp2"
    if (input.equals("runesp2")) {
      if (espNowInitialized) {
        uint8_t message[] = {1}; // Payload to send
        esp_now_send(peerMACAddress, message, sizeof(message));
        Serial.println("Command sent to second NodeMCU via ESP-NOW.");
      } else {
        Serial.println("ESP-NOW not initialized.");
      }
    } else {
      // Parse the input for X and Y coordinates
      int commaIndex = input.indexOf(',');
      if (commaIndex > 0) {
        String xString = input.substring(0, commaIndex);
        String yString = input.substring(commaIndex + 1);

        // Convert strings to integers
        int x = xString.toInt();
        int y = yString.toInt();

        // Map coordinates to servo angles
        int angleX = map(x, 0, screenWidth, minAngle, maxAngle);
        int angleY = map(y, 0, screenHeight, 52, 148);

        // Write angles to servos
        servoX.write(angleX);
        servoY.write(angleY);

        // Debug output
        Serial.print("X: ");
        Serial.print(x);
        Serial.print(" -> AngleX: ");
        Serial.println(angleX);

        Serial.print("Y: ");
        Serial.print(y);
        Serial.print(" -> AngleY: ");
        Serial.println(angleY);

        // Spray functionality
        delay(600);  
        digitalWrite(D8, HIGH); // Set D8 HIGH
        // Set motor speed using PWM (0-1023 for ESP8266)
        analogWrite(ENA, 1023);  // 50% speed
        delay(250);             // Wait for 250 milliseconds
        digitalWrite(D8, LOW);  // Set D8 LOW
        analogWrite(ENA, 0);  // Stop motor
      }
    }
  }
}
