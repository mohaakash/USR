#define ENA D1  // PWM pin for speed control
#define IN1 D2  // Direction control
#define IN2 D3  // Grounded, no reverse needed

void setup() {
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);

  // Set initial direction
  digitalWrite(IN1, HIGH);  // Forward direction
  digitalWrite(IN2, LOW);   // Ground IN2 to prevent reverse
}

void loop() {
  // Set motor speed using PWM (0-1023 for ESP8266)
  analogWrite(ENA, 1023);  // 50% speed
  
  delay(5000);  // Run for 5 seconds
  
  analogWrite(ENA, 0);  // Stop motor
  delay(1000);  // Wait for 2 seconds
}
