 #  server.py
 #
 #  version 3.0
 #  
 #  CMI-TI 22 TINCOS01
 #  Studenten: Bartholomeus Petrus, Hidde-Jan Daniels, Thijs Dregmans
 #  Connected Systems
 #  Last edited: 2023-06-08 
 #


# TODO:
    # Expand on naming systems of bots in README 
    #

from paho.mqtt import client as mqtt_client
import time

BOT_ID = 1 # Must be different for each bot

MQTT_BROKER = "broker.mqtt-dashboard.com" 
MQTT_PORT = 1883
MQTT_CLIENTID = "TINCOS01-BHT-" + str(BOT_ID) + "-DT" # DT means Digital Twin
MQTT_TOPIC = "TINCOS/protocol/communication"
MQTT_EMERGENCY_TOPIC = "TINCOS/protocol/emergency"

def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(MQTT_CLIENTID)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(MQTT_BROKER, MQTT_PORT)
    return client


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    client.subscribe(MQTT_TOPIC)
    client.on_message = on_message

    msg = "hi"
    client.publish(MQTT_TOPIC, msg)

    for x in range(10):
        client.publish(MQTT_TOPIC, str(x))

def publish(client):
    msg_count = 1
    while True:
        time.sleep(1)
        msg = f"messages: {msg_count}"
        result = client.publish(MQTT_TOPIC, msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{MQTT_TOPIC}`")
        else:
            print(f"Failed to send message to topic {MQTT_TOPIC}")
        msg_count += 1
        if msg_count > 5:
            break



def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()
