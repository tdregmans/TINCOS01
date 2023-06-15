/*
  bot.ino

  version 5.0

  CMI-TI 22 TINCOS01
  Studenten: Bartholomeus Petrus, Hidde-Jan Daniels, Thijs Dregmans
  Connected Systems
  Last edited: 2023-06-15

*/

#include <WiFi.h>
#include <PubSubClient.h>
#include "password.h"

#define LED_NORTH 32
#define LED_EAST 12
#define LED_SOUTH 33
#define LED_WEST 13
#define BUTTON 2


#define MSG_BUFFER_SIZE  (50)

#define BOT_ID 1 // Must be different for each bot

const char* mqtt_server = "broker.mqtt-dashboard.com";
const char* mqtt_clientId = "TINCOS01-BHT-" + BOT_ID;
const char* mqtt_topic = "TINCOS/comms";

volatile bool shouldTerminate = false;

WiFiClient espClient;
PubSubClient client(espClient);
unsigned long lastMsg = 0;

char msg[MSG_BUFFER_SIZE];
int value = 0;

void setup_wifi() {

  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, pass);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  randomSeed(micros());

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

String getValue(String data, char separator, int index)
{
  int found = 0;
  int strIndex[] = {0, -1};
  int maxIndex = data.length()-1;

  for(int i=0; i<=maxIndex && found<=index; i++){
    if(data.charAt(i)==separator || i==maxIndex){
        found++;
        strIndex[0] = strIndex[1]+1;
        strIndex[1] = (i == maxIndex) ? i+1 : i;
    }
  }

  return found>index ? data.substring(strIndex[0], strIndex[1]) : "";
}

void processMessage(String message) {
    // get x and y
    String x = (getValue(message, ',', 3).substring(33));
    String y = (getValue(message, ',', 4).substring(6).substring(0, 4));

    if (y[0] != '-') {
      y = y.substring(0, 3);
    }

    // get target
    String targeti = (getValue(message, ',', 1));
    String target = (getValue(targeti, '"', 3).substring(0, 4));

    if (target == "bot"+String(BOT_ID)) {
        // message addressed to this bot

        
        // get LED
        String led = (getValue(message, ':', 9).substring(2,3));

        Serial.println(led);

        digitalWrite(LED_NORTH, led == "N");
        digitalWrite(LED_EAST, led == "E");
        digitalWrite(LED_SOUTH, led == "S");
        digitalWrite(LED_WEST, led == "W");
    }
    else {
        // ignore message
        return;
    }

}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");

  String message;

  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println(message);

  // Implement use of protocol
  processMessage(message);
  
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = mqtt_clientId;
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    if (client.connect(clientId.c_str())) {
      Serial.println("connected to mqtt");
      
      client.subscribe(mqtt_topic);
      String message = clientId + "=" + mqtt_clientId;
      
//      client.publish(mqtt_topic, "test"); // put message in, to let server know client is connected
      
    } 
    else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void calibrateLEDs() {

  digitalWrite(LED_NORTH, HIGH);
  digitalWrite(LED_EAST, HIGH);
  digitalWrite(LED_SOUTH, HIGH);
  digitalWrite(LED_WEST, HIGH);

  delay(500);
  
  digitalWrite(LED_NORTH, HIGH);
  digitalWrite(LED_EAST, LOW);
  digitalWrite(LED_SOUTH, LOW);
  digitalWrite(LED_WEST, LOW);

  delay(500);
  
  digitalWrite(LED_NORTH, LOW);
  digitalWrite(LED_EAST, HIGH);
  digitalWrite(LED_SOUTH, LOW);
  digitalWrite(LED_WEST, LOW);

  delay(500);
  
  digitalWrite(LED_NORTH, LOW);
  digitalWrite(LED_EAST, LOW);
  digitalWrite(LED_SOUTH, HIGH);
  digitalWrite(LED_WEST, LOW);

  delay(500);
  
  digitalWrite(LED_NORTH, LOW);
  digitalWrite(LED_EAST, LOW);
  digitalWrite(LED_SOUTH, LOW);
  digitalWrite(LED_WEST, HIGH);

  delay(500);
  
  digitalWrite(LED_NORTH, LOW);
  digitalWrite(LED_EAST, LOW);
  digitalWrite(LED_SOUTH, LOW);
  digitalWrite(LED_WEST, LOW);
}

void emergency() {
  // send signal to server
  shouldTerminate = true;

  for (int i = 0; i < 10; i++) {
      if ((i % 2) == 0) {
        digitalWrite(LED_NORTH, HIGH);
        digitalWrite(LED_EAST, HIGH);
        digitalWrite(LED_SOUTH, HIGH);
        digitalWrite(LED_WEST, HIGH);
      }
      else {
        digitalWrite(LED_NORTH, LOW);
        digitalWrite(LED_EAST, LOW);
        digitalWrite(LED_SOUTH, LOW);
        digitalWrite(LED_WEST, LOW);
      }
      delay(40);
      
  }
  
  Serial.println("Emergency stop broadcasted");
  client.publish(mqtt_topic, "{\"data\":{\"sender\": \"bot1\", \"emergency\": 1}, \"protocolVersion\": 4.1}");
}

void setup() {
  Serial.begin(115200);
  
  pinMode(BUILTIN_LED, OUTPUT);

  pinMode(LED_NORTH, OUTPUT);
  pinMode(LED_EAST, OUTPUT);
  pinMode(LED_SOUTH, OUTPUT);
  pinMode(LED_WEST, OUTPUT);
  pinMode(BUTTON, INPUT_PULLUP);
  
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);

  calibrateLEDs();

}



void loop() {

  if (!client.connected()) {
    reconnect();
  }
  client.loop();

    //  unsigned long now = millis();
    //  if (now - lastMsg > 2000) {
    //    lastMsg = now;
    //    ++value;
    //    snprintf (msg, MSG_BUFFER_SIZE, "hello world #%ld", value);
    //    Serial.print("Publish message: ");
    //    Serial.println(msg);
    //    client.publish(mqtt_topic, msg);
    //  }

  if (!digitalRead(BUTTON)) {
      emergency();
  }
}
