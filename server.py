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
import math

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

bots = []
bots = ["bot1", "bot2", "bot3"] # hardcoded bot to assign targest, while there is no dashboard

targetFields = [[0, 0], [9, 9], [0, 0]]

def coords2fieldId(coords):
    # from Webots coördinates to field index
    x = (int) ((coords["x"] + 0.4) * 10)
    y = (int) ((coords["y"] + 0.4) * 10)
    return [x, y]

def fieldId2coords(fieldId):
    # from Webots coördinates to field index
    try:
        x = (fieldId[0] / 10) - 0.4
        y = (fieldId[1] / 10) - 0.4
    except KeyError:
        x = Null
        y = Null
    return {"x": round(x,1), "y": round(y,1)}

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


client = connect_mqtt()

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        payload = msg.payload.decode()
        topic = msg.topic
        print(payload)
        
        processCommand(payload)

    client.subscribe(MQTT_TOPIC)
    client.on_message = on_message


def distance(a, b):
    # calculate the distance between a and b
    xi = a[0] - b[0]
    yi = a[1] - b[1]
    return math.sqrt(math.pow(xi, 2) + math.pow(yi, 2))

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

    # find new location for bot to go to
    target = targetFields[bots.index(sender)]

    
    possibleNewLocations = [[x+1, y], [x-1, y], [x, y+1], [x, y-1]]
    # check for obstacles
    for location in possibleNewLocations:
        if(fields[location[0]][location[1]]):
            # not empty -> remove
            possibleNewLocations.remove(location)
    # check what possible new location is closest to target
    newLocation = [x, y]
    max = 0
    for possibleNewLocation in possibleNewLocations:
        if(distance(possibleNewLocation, target) >= distance(newLocation, target)):
            max = distance(possibleNewLocation, target)
            newLocation = possibleNewLocation
    return newLocation

def processCommand(payload):
    request = json.loads(payload)
    if (request["protocolVersion"] == 2.0):
        data = request["data"]

        if (data["target"] == MQTT_CLIENTID):
            sender = data["sender"]

            if(not(sender in bots)):
                bots.append(sender)
            print(sender)
            currentLocation = data["msg"]["currentLocation"]
            obstacles = data["msg"]["obstacles"]

            # process location in memory
            try:
                target = processLocation(sender, currentLocation, obstacles)
            except IndexError:
                target = currentLocation
            
            response = {
                "data": 
                {
                    "sender": MQTT_CLIENTID,
                    "target": sender,
                    "msg":
                    {
                        "targetLocation": fieldId2coords(target)
                    }
                },
                "protocolVersion": 2.0
            }

            # send new targetLocation to bot
            client.publish(MQTT_TOPIC, json.dumps(response))
            
        # else:
        #     print("Recieved message that wasn't addressed to me.")
    else:
        if(request["protocolVersion"] < 2.0):
            print("WARNING! Deprecated protocol was used.")
        else:
            print("ERROR! Didn't understand syntax of request bot.")

def run():
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()
