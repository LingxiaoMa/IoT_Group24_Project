#include <WiFi.h>
#include <ESP32Servo.h>  // Library to control servo on ESP32

// Define the pin connected to the servo signal
const int servoPin = 1;  // Adjust this based on your setup

Servo myServo;  // Create a Servo object

// Variables to store angles
int pos = 0;    // Starting position (0 degrees)
int increment = 1;  // Angle increment for each step
bool isSwinging = false;  // Flag to track whether the servo should be swinging
unsigned long swingStartTime = 0;  // Track the time when the swinging started


// Replace with your network credentials
const char* ssid = "iPhone";
const char* password = "20030528";

// Define the port the ESP32 will listen on
WiFiServer server(5012);  // ESP32 listening on port 5012

void setup() {
  Serial.begin(115200);  // Start the Serial Monitor

  myServo.attach(servoPin);  // Attach the servo to the pin
  myServo.write(pos);  // Initialize servo to start at 0 degrees

  // Connect to Wi-Fi
  Serial.printf("Connecting to %s ", ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nConnected to Wi-Fi!");

  // Start the TCP server
  server.begin();  // Start listening on port 5012
  Serial.println("TCP server started. Waiting for clients...");
  Serial.print("ESP32 IP Address: ");
  Serial.println(WiFi.localIP());  // Print ESP32 IP address
}

void loop() {
  // Check if a client has connected
  WiFiClient client = server.available();

  if (client) {
    Serial.println("Client connected.");

    while (client.connected()) {
      if (client.available()) {
        String message = client.readStringUntil('\n');  // Read data from the client
        Serial.print("Received message: ");
        Serial.println(message);

        if (message == "ON") {
          // Start swinging the servo for 3 seconds
          isSwinging = true;
          swingStartTime = millis();  // Record the time the swinging starts
        } else if (message == "OFF") {
          // Stop swinging the servo immediately
          isSwinging = false;
          myServo.write(0);  // Set the servo to 0° position
        }
      }
    }

    // Client disconnected
    client.stop();
    Serial.println("Client disconnected.");
  }

  // Call the modified loop function for swinging the servo
  if (isSwinging) {
    unsigned long currentTime = millis();
    
    if (currentTime - swingStartTime <= 3000) {
      // Move the servo back and forth between 0° and 90°
      pos += increment;

      if (pos >= 120 || pos <= 0) {
        increment = -increment;  // Reverse direction
      }

      myServo.write(pos);  // Set the servo to the current position
      delay(15);  // Adjust the speed of movement by changing the delay
    } else {
      // Stop swinging after 3 seconds
      isSwinging = false;
      myServo.write(0);  // Return the servo to the 0 position
    }
  }
}