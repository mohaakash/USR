#include <Servo.h>

Servo servo1; // Create servo object for the first servo
Servo servo2; // Create servo object for the second servo

void setup() {
  servo1.attach(D5); // Attach first servo to D5
  servo2.attach(D0); // Attach second servo to D6
  Serial.begin(115200); // Start serial communication at 115200 baud rate
}

void loop() {
  if (Serial.available() > 0) {
    // Read the input as a string
    String input = Serial.readStringUntil('\n');
    input.trim(); // Remove any trailing whitespace

    // Parse the input format "servo1_angle,servo2_angle"
    int commaIndex = input.indexOf(',');
    if (commaIndex > 0) {
      String servo1AngleStr = input.substring(0, commaIndex);
      String servo2AngleStr = input.substring(commaIndex + 1);

      int servo1Angle = servo1AngleStr.toInt();
      int servo2Angle = servo2AngleStr.toInt();

      // Ensure angles are within range (0-180 degrees)
      servo1Angle = constrain(servo1Angle, 0, 180);
      servo2Angle = constrain(servo2Angle, 0, 180);

      // Move the servos to the specified angles
      servo1.write(servo1Angle);
      servo2.write(servo2Angle);
    }
  }
}
