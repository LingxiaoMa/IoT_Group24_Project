#include <WiFi.h>

// Replace with your network credentials (SSID and password)
const char* ssid = "iPhone";
const char* password = "20030528";

void setup() {
  Serial.begin(115200);  // Start the Serial Monitor

  // Connect to Wi-Fi
  Serial.printf("Connecting to %s", ssid);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }

  // Print the IP address
  Serial.println("\nConnected to Wi-Fi!");
  Serial.print("ESP32 IP Address: ");
  Serial.println(WiFi.localIP());  // Print the IP address
}

void loop() {
  // Your loop code here
}

