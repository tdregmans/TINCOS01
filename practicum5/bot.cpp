/**
 * bot.cpp
 * TINCOS01
 * Bartholomeus Petrus, Hidde-Jan Daniels, Thijs Dregmans
 * Last edited: 2023-05-10
 *
 * Code is copied from manual
 */



# include < ESP8266WiFi .h >

void setup () {
    Serial.begin(115200);
    Serial.print("\nConnecting");
    WiFi.begin("Tesla IoT", "fsL6HgjN");
    while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    }
    Serial.print("\nConnected, IP address: ");
    Serial.println(WiFi.localIP());
}

WiFiClient client;

void loop () {
    client.setTimeout(1000); // set timeout for establishing connection
    if (!client.connect( " 192.168.1.1 " , 1024)) { // fill in IP address and port number
        Serial.println("connection failed; wait 5 sec ...");
        delay(5000);
        return;
    }
    Serial.println("connected to server");
    
    client.setTimeout(1); // set timeout for end - of - message
    while (client.connected()) {
        if (client.available()) {
            String line = client.readString();
            Serial.print("message from server : ");
            Serial.println(line);
        }
        yield();
    }
    Serial.println("connection lost");
}
