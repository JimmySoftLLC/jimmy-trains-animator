/*
# MIT License
#
# Copyright (c) 2024 JimmySoftLLC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
*/

// Load Wi-Fi and LittleFS libraries
#include <WiFi.h>
#include <LittleFS.h>

// Replace with your network credentials
const char* ssid = "YOUR_SSID";
const char* password = "YOUR_PASSWORD";

WiFiServer server(80);
String header;
String picoLEDState = "off";

unsigned long currentTime = 0;
unsigned long previousTime = 0;
const long timeoutTime = 2000;

void setup() {
  Serial.begin(115200);

  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);

  if (!LittleFS.begin()) {
    Serial.println("LittleFS Mount Failed");
    return;
  }
  Serial.println("LittleFS Mounted Successfully");

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.print("WiFi connected. IP address: ");
  Serial.println(WiFi.localIP());

  server.begin();
}

void streamFile(WiFiClient& client, const char* path, const char* contentType) {
  File file = LittleFS.open(path, "r");
  if (!file) {
    client.println("HTTP/1.1 404 Not Found");
    client.println("Content-type: text/html");
    client.println("Connection: close");
    client.println();
    client.println("<html><body><h1>404 File Not Found</h1></body></html>");
    return;
  }

  size_t totalSize = file.size();
  Serial.println(String("Serving ") + path + " (" + totalSize + " bytes)");

  client.println("HTTP/1.1 200 OK");
  client.println("Content-type: " + String(contentType));
  client.println("Connection: close");
  client.println("Content-Length: " + String(totalSize));
  client.println();

  uint8_t buffer[256];
  size_t bytesSent = 0;
  int chunkCount = 0;

  while (file.available()) {
    size_t len = file.read(buffer, sizeof(buffer));
    client.write(buffer, len);
    bytesSent += len;

    // Yield every 2 chunks to avoid TCP buffer overflow
    if (++chunkCount % 2 == 0) {
      delay(1); // brief yield for network stack
    }
  }

  file.close();
  client.flush();
  delay(1);

  Serial.println("Finished sending file. Bytes sent: " + String(bytesSent));
}

void sendJson(WiFiClient& client, const char* state) {
  client.println("HTTP/1.1 200 OK");
  client.println("Content-type: application/json");
  client.println("Connection: close");
  client.println();
  client.print("{\"status\":\"success\",\"ledState\":\"");
  client.print(state);
  client.println("\"}");
  client.flush();
  delay(1);
}

void loop() {
  WiFiClient client = server.available();
  if (client) {
    currentTime = millis();
    previousTime = currentTime;
    Serial.println("New Client.");
    String currentLine = "";
    header = "";

    while (client.connected() && currentTime - previousTime <= timeoutTime) {
      currentTime = millis();
      if (client.available()) {
        char c = client.read();
        Serial.write(c);
        if (header.length() < 512) header += c;

        if (c == '\n') {
          if (currentLine.length() == 0) {
            bool handled = false;

            if (header.indexOf("GET / ") >= 0 || header.indexOf("GET /index.html") >= 0) {
              streamFile(client, "/index.html", "text/html");
              handled = true;
            } else if (header.indexOf("GET /mui.min.css") >= 0) {
              streamFile(client, "/mui.min.css", "text/css");
              handled = true;
            } else if (header.indexOf("GET /mui.min.js") >= 0) {
              streamFile(client, "/mui.min.js", "text/javascript");
              handled = true;
            } else if (header.indexOf("GET /api/led/on") >= 0) {
              picoLEDState = "on";
              digitalWrite(LED_BUILTIN, HIGH);
              sendJson(client, "on");
              handled = true;
            } else if (header.indexOf("GET /api/led/off") >= 0) {
              picoLEDState = "off";
              digitalWrite(LED_BUILTIN, LOW);
              sendJson(client, "off");
              handled = true;
            } else if (header.indexOf("GET /api/led/state") >= 0) {
              sendJson(client, picoLEDState.c_str());
              handled = true;
            }

            if (!handled) {
              client.println("HTTP/1.1 404 Not Found");
              client.println("Content-type: text/html");
              client.println("Connection: close");
              client.println();
              client.println("<html><body><h1>404 Not Found</h1></body></html>");
              client.flush();
              delay(1);
            }

            break;  // Exit client-handling loop after one request
          } else {
            currentLine = "";
          }
        } else if (c != '\r') {
          currentLine += c;
        }
      }
    }

    client.stop();
    Serial.println("Client disconnected.\n");
  }
}
