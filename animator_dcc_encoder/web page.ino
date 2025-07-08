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

// Set web server port number to 80
WiFiServer server(80);

// Variable to store the HTTP request
String header;

// Variable to store onboard LED state
String picoLEDState = "off";

// Timing
unsigned long currentTime = millis();
unsigned long previousTime = 0;
const long timeoutTime = 2000;

void setup()
{
  Serial.begin(115200);

  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);

  if (!LittleFS.begin())
  {
    Serial.println("LittleFS Mount Failed");
    return;
  }
  Serial.println("LittleFS Mounted Successfully");

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.print("WiFi connected at IP Address ");
  Serial.println(WiFi.localIP());
  server.begin();
}

void loop()
{
  WiFiClient client = server.available();
  if (client)
  {
    currentTime = millis();
    previousTime = currentTime;
    Serial.println("New Client.");
    String currentLine = "";

    while (client.connected() && currentTime - previousTime <= timeoutTime)
    {
      currentTime = millis();
      if (client.available())
      {
        char c = client.read();
        Serial.write(c);
        header += c;
        if (c == '\n')
        {
          if (currentLine.length() == 0)
          {
            String contentType = "text/html";
            String responseBody = "";
            bool handled = false;

            if (header.indexOf("GET / ") >= 0 || header.indexOf("GET /index.html") >= 0)
            {
              File file = LittleFS.open("/index.html", "r");
              if (file)
              {
                client.println("HTTP/1.1 200 OK");
                client.println("Content-type: text/html");
                client.println("Connection: close");
                client.println("Content-Length: " + String(file.size()));
                client.println();

                while (file.available())
                  client.write(file.read());
                file.close();
                handled = true;
              }
            }
            else if (header.indexOf("GET /mui.min.css") >= 0)
            {
              File file = LittleFS.open("/mui.min.css", "r");
              if (file)
              {
                client.println("HTTP/1.1 200 OK");
                client.println("Content-type: text/css");
                client.println("Connection: close");
                client.println("Content-Length: " + String(file.size()));
                client.println();

                while (file.available())
                  client.write(file.read());
                file.close();
                handled = true;
              }
            }
            else if (header.indexOf("GET /mui.min.js") >= 0)
            {
              File file = LittleFS.open("/mui.min.js", "r");
              if (file)
              {
                client.println("HTTP/1.1 200 OK");
                client.println("Content-type: text/javascript");
                client.println("Connection: close");
                client.println("Content-Length: " + String(file.size()));
                client.println();

                while (file.available())
                  client.write(file.read());
                file.close();
                handled = true;
              }
            }
            else if (header.indexOf("GET /api/led/on") >= 0)
            {
              picoLEDState = "on";
              digitalWrite(LED_BUILTIN, HIGH);
              responseBody = "{\"status\":\"success\",\"ledState\":\"on\"}";
              contentType = "application/json";
              handled = true;
            }
            else if (header.indexOf("GET /api/led/off") >= 0)
            {
              picoLEDState = "off";
              digitalWrite(LED_BUILTIN, LOW);
              responseBody = "{\"status\":\"success\",\"ledState\":\"off\"}";
              contentType = "application/json";
              handled = true;
            }
            else if (header.indexOf("GET /api/led/state") >= 0)
            {
              responseBody = "{\"status\":\"success\",\"ledState\":\"" + picoLEDState + "\"}";
              contentType = "application/json";
              handled = true;
            }

            if (!handled)
            {
              client.println("HTTP/1.1 404 Not Found");
              contentType = "text/html";
              responseBody = "<!DOCTYPE html><html><body><h1>404 Not Found</h1></body></html>";
            }

            if (responseBody != "")
            {
              client.println("HTTP/1.1 200 OK");
              client.println("Content-type: " + contentType);
              client.println("Connection: close");
              client.println("Content-Length: " + String(responseBody.length()));
              client.println();
              client.println(responseBody);
            }

            break;
          }
          else
          {
            currentLine = "";
          }
        }
        else if (c != '\r')
        {
          currentLine += c;
        }
      }
    }
    header = "";
    client.stop();
    Serial.println("Client disconnected.");
    Serial.println();
  }
}
