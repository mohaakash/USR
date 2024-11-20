#include <Servo.h>

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

void setup() {
  // Attach servos to their respective pins
  servoX.attach(servoXPin);
  servoY.attach(servoYPin);

  // Set initial servo positions to midpoints
  servoX.write(90);
  servoY.write(90);

  // Initialize serial communication
  Serial.begin(9600);
}

void loop() {
  // Check if data is available on the serial port
  if (Serial.available() > 0) {
    // Read the incoming data
    String input = Serial.readStringUntil('\n'); // Read until newline
    input.trim(); // Remove any whitespace

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
    }
  }
}
