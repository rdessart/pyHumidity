#include <WiFiNINA.h>
#include <ArduinoHttpClient.h>
#include "DHTStable.h"


/*
    required libraries:
        - WiFiNINA - Arduino - v1.8.13
        - DHTStable - Rob Tilaart - v1.1.0
        - ArduinoHttpClient - Arduino - v0.3.2
*/

char ssid[] = "Rom&Max2";
char pass[] = "RominouMaxou1435";

int led =  LED_BUILTIN;
int status = WL_IDLE_STATUS;
DHTStable DHT;
int sensorPin = 5;

WiFiClient wifi;
HttpClient client = HttpClient(wifi, "192.168.0.X", 80);

void setup() {
  Serial.begin(115200);
  while (!Serial) { ; }
  Serial.println("Access Point Web Server");
  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("Communication with WiFi module failed!");
  }

  String fv = WiFi.firmwareVersion();
  if (fv < WIFI_FIRMWARE_LATEST_VERSION) {
    Serial.println("Please upgrade the firmware");
  }
  Serial.print("Connecting to: ");
  Serial.println(ssid);

  status = WiFi.begin(ssid, pass);
  while (status != WL_CONNECTED) {
    Serial.print(".");
      delay(250);
  }
  //server.begin();
  printWiFiStatus();
}


void loop() {
  int chk = DHT.read22(sensorPin);
  float temperature = DHT.getTemperature();
  float humidity = DHT.getHumidity();
  if(chk != DHTLIB_OK)
  {
    Serial.println("Error with sensor");
    delay(2000);
    return;
  }
  String postData = String("temperature=") + String(temperature) + String("&humidity=") + String(humidity);
  Serial.print(humidity, 1);
  Serial.print(";");
  Serial.println(temperature, 1);

  client.beginRequest();
  client.post("/add/");
  client.sendHeader("Content-Type", "application/x-www-form-urlencoded");
  client.sendHeader("Content-Length", postData.length());
  client.beginBody();
  client.print(postData);
  client.endRequest();
  int statusCode = client.responseStatusCode();
  Serial.print("Status code: ");
  Serial.println(statusCode);
  delay(2000);
}

void printWiFiStatus() {
  // print the SSID of the network you're attached to:
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print your WiFi shield's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);
}
