 #  server.py
 #
 #  version 3.0
 #  
 #  CMI-TI 22 TINCOS01
 #  Studenten: Bartholomeus Petrus, Hidde-Jan Daniels, Thijs Dregmans
 #  Connected Systems
 #  Last edited: 2023-06-09
 #


from paho.mqtt import client as mqtt_client
import time
import json

MQTT_BROKER = "broker.mqtt-dashboard.com" 
MQTT_PORT = 1883
MQTT_CLIENTID = "server"
MQTT_TOPIC = "TINCOS/protocol/communication"
MQTT_EMERGENCY_TOPIC = "TINCOS/protocol/emergency"

# fill empty field
fieldSize = 10
fields = []
for x in range(fieldSize):
    fields.append(["" for y in range(fieldSize)])

def coords2fieldId(coords):
    # from Webots coördinates to field index
    x = (int) ((coords["x"] + 0.4) * 10)
    y = (int) ((coords["y"] + 0.4) * 10)
    return [x, y]

def fieldId2coords(fieldId):
    # from Webots coördinates to field index
    x = (fieldId[0] / 10) - 0.4
    y = (fieldId[1] / 10) - 0.4
    return {"x": x, "y": y}

def printFields():
    for row in fields:
        print(row)

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
        payload = msg.payload.decode()
        topic = msg.topic
        print(MQTT_CLIENTID + " received `{payload}` from `{topic}` topic")
        
        processCommand(payload)

    client.subscribe(MQTT_TOPIC)
    client.on_message = on_message

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

def processLocation(sender, currentLocation, obstacles):
    # In fields[x][y] "" means empty field, "bot1" means bot1 in this field, "O" means obstacle in this field 

    # remove sender from fields
    for row in fields:
        for field in row:
            if(field == sender):
                field = ""
    
    # add sender on new location
    x, y = coords2fieldId(currentLocation)
    fields[x][y] = sender

    # add obstacles
    for obstacle in obstacles:
        x = coords2fieldId(obstacle)[0]
        y = coords2fieldId(obstacle)[1]
        fields[x][y] = "o"
    
    # possible feature for later: Remove obstacle if they are no longer there.
    # First calcuate if bot should be able to see obstacle. Then, if not detected by bot, deleted by server

def processCommand(payload):
    print("-------------------------------------------")
    request = json.loads(payload)
    if (request["protocolVersion"] == 2.0):
        data = request["data"]

        if (data["target"] == MQTT_CLIENTID):
            sender = data["sender"]
            print(sender)
            currentLocation = data["msg"]["currentLocation"]
            obstacles = data["msg"]["obstacles"]

            # print(currentLocation)
            # print(obstacles)

            processLocation(sender, currentLocation, obstacles)
            printFields()
        else:
            print("Recieved message that wasn't addressed to me.")
    else:
        if(request["protocolVersion"] < 2.0):
            print("WARNING! Deprecated protocol was used.")
        else:
            print("ERROR! Didn't understand syntax of request bot.")

def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()
