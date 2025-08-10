#include <ESP8266WiFi.h>
#include <espnow.h>

// BTS7960 Pin Definitions
const int RPWM = D1; // Forward direction PWM
const int LPWM = D2; // Reverse direction PWM (not used)
const int R_EN = D3; // Enable pin for forward
const int L_EN = D4; // Enable pin for reverse (not used)

// MAC address of the first NodeMCU
uint8_t senderMACAddress[] = {0x40, 0x91, 0x51, 0x55, 0xC2, 0x67};

// Callback function to handle received data
void onDataReceive(uint8_t *mac, uint8_t *data, uint8_t len) {
  Serial.print("Data received from: ");
  for (int i = 0; i < 6; i++) {
    Serial.print(mac[i], HEX);
    if (i < 5) Serial.print(":");
  }
  Serial.println();

  // Print received data
  Serial.print("Data: ");
  for (int i = 0; i < len; i++) {
    Serial.print(data[i]);
    Serial.print(" ");
  }
  Serial.println();

  // Perform action if specific data is received
  if (memcmp(mac, senderMACAddress, 6) == 0 && data[0] == 1) {
    Serial.println("Running motor forward for 300ms.");
    runMotorForward(300); // Run the motor forward for 300ms
  }
}

// Function to run the motor forward
void runMotorForward(int durationMs) {
  digitalWrite(R_EN, HIGH);    // Enable forward motor
  digitalWrite(L_EN, LOW);     // Ensure reverse is disabled
  analogWrite(RPWM, 255);      // Set full speed forward (adjust if needed)
  analogWrite(LPWM, 0);        // Ensure reverse direction is off
  delay(durationMs);           // Run motor for specified time
  analogWrite(RPWM, 0);        // Stop motor
  digitalWrite(R_EN, LOW);     // Disable motor
}

void setup() {
  // Initialize Serial Monitor
  Serial.begin(9600);

  // Initialize motor control pins
  pinMode(RPWM, OUTPUT);
  pinMode(LPWM, OUTPUT);
  pinMode(R_EN, OUTPUT);
  pinMode(L_EN, OUTPUT);

  // Ensure motor is stopped
  digitalWrite(R_EN, LOW);
  digitalWrite(L_EN, LOW);
  analogWrite(RPWM, 0);
  analogWrite(LPWM, 0);

  // Set device as Wi-Fi Station
  WiFi.mode(WIFI_STA);

  // Initialize ESP-NOW
  if (esp_now_init() == 0) {
    Serial.println("ESP-NOW initialized successfully.");
    esp_now_register_recv_cb(onDataReceive);
  } else {
    Serial.println("ESP-NOW initialization failed!");
    while (true); // Halt the program if initialization fails
  }
}

void loop() {
  // Keep the loop empty as actions are handled in the callback function
}

