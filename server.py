 #  server.py
 #
 #  version 4.1
 #  
 #  CMI-TI 22 TINCOS01
 #  Studenten: Bartholomeus Petrus, Hidde-Jan Daniels, Thijs Dregmans
 #  Connected Systems
 #  Last edited: 2023-06-15
 #

# import libaries
from paho.mqtt import client as mqtt_client
import time
import json
import math
import sys

# define MQTT constants
MQTT_BROKER = "broker.mqtt-dashboard.com" 
MQTT_PORT = 1883
MQTT_CLIENTID = "server"
MQTT_TOPIC = "TINCOS/comms"
MQTT_EMERGENCY_TOPIC = "TINCOS/protocol/emergency"

# global emergency variable
global emergency
emergency = 0

# fill empty fields with ""
fieldSize = 10
fields = []
for x in range(fieldSize):
    fields.append(["" for y in range(fieldSize)])

# global variable that stores the bots in the program
# bots = []
bots = ["bot1"] 
# hardcoded bot to assign targest, while there is no dashboard

# global variable that stores the targetFields that the bots want to go to
targetFields = [[9, 5]]
# hardcoded fields, while there is no dashboard 

# helper-function: converts Webots coördinates to fields
def coords2fieldId(coords):
    # from Webots coördinates to field index
    x = (int) ((coords["x"] + 0.4) * 10)
    y = (int) ((coords["y"] + 0.4) * 10)
    return [x, y]

# helper-function: converts fields to webots coördinates
def fieldId2coords(fieldId):
    # from field index to Webots coördinates
    try:
        x = (fieldId[0] / 10) - 0.4
        y = (fieldId[1] / 10) - 0.4
    except KeyError:
        x = 0
        y = 0
        print("KEYERROR! Something went wrong!")
    return {"x": round(x,1), "y": round(y,1)}

# helper-function: get distance between two fields
def distance(a, b):
    # calculate the distance between a and b
    xi = a[0] - b[0]
    yi = a[1] - b[1]
    return math.sqrt(math.pow(xi, 2) + math.pow(yi, 2))

# debug-function: prints all fields
def printFields():
    for row in fields:
        print(row)

### MQTT function: connect to broker
def connect_mqtt() -> mqtt_client:
    # on-connect function
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(MQTT_CLIENTID)
    client.on_connect = on_connect
    # connect to broker
    client.connect(MQTT_BROKER, MQTT_PORT)
    return client

### MQTT function: subscribe to topic
def subscribe(client: mqtt_client):
    # on-message function
    def on_message(client, userdata, msg):
        payload = msg.payload.decode()
        topic = msg.topic
        print(payload)
        
        # process the incomming command
        processCommand(payload)

    # subscribe to topic
    client.subscribe(MQTT_TOPIC)
    client.on_message = on_message

def stripImpossibleLocations(possibleNewLocations):
    for location in possibleNewLocations:
        x = location["coords"][0]
        y = location["coords"][1]
        if (x < 0 or x > 9):
            possibleNewLocations.remove(location)
            print("striped: " + str(location))
        elif (y < 0 or y > 9):
            possibleNewLocations.remove(location)
            print("striped: " + str(location))
    return possibleNewLocations

# find next target location
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

    # # add obstacles
    # for obstacle in obstacles:
    #     x, y = coords2fieldId(obstacle)
    #     fields[x][y] = "o"
    # this code above creates the INDEXERROR
    
    # possible feature for later: Remove obstacle if they are no longer there.
    # First calcuate if bot should be able to see obstacle. Then, if not detected by bot, deleted by server

    # find new location for bot to go to
    target = targetFields[bots.index(sender)]

    
    possibleNewLocations = [
        {"direction": "N", "coords": [x + 1, y]},
        {"direction": "E", "coords": [x, y - 1]},
        {"direction": "S", "coords": [x - 1, y]},
        {"direction": "W", "coords": [x, y + 1]}]
    
    
    possibleNewLocations = stripImpossibleLocations(possibleNewLocations)

    # check for obstacles
    for location in possibleNewLocations:
        x = location["coords"][0]
        y = location["coords"][1]
        if (fields[x][y] != ""):
            possibleNewLocations.remove(location)

    newLocation = {"direction": "", "coords": [x, y]}
    
    if (currentLocation == fieldId2coords(target)):
        print(sender + " reached destination")
        sys.exit()
    else:
        for possibleNewLocation in possibleNewLocations:
            if(distance(possibleNewLocation["coords"], target) <= distance(newLocation["coords"], target)):
                newLocation = possibleNewLocation

    # debug option: print coords
    print(fieldId2coords(newLocation["coords"]))
    return newLocation["direction"]

# process the incomming command from server
def processCommand(payload):
    global emergency
    request = json.loads(payload)
    if (request["protocolVersion"] == 4.1):
        data = request["data"]

        if (data["emergency"]):
            print("EMERGENCY STOP")
            emergency = 1
            sys.exit()
        elif (data["target"] == MQTT_CLIENTID):
            sender = data["sender"]

            # add bot to global bots list
            if(not(sender in bots)):
                bots.append(sender)

            currentLocation = data["msg"]["currentLocation"]
            obstacles = data["msg"]["obstacles"]

            # process location in memory
            try:
                target = processLocation(sender, currentLocation, obstacles)
            except IndexError:
                print("INDEXERROR! Could not process location")
                return
            
            response = {
                "data": 
                {
                    "sender": MQTT_CLIENTID,
                    "target": sender,
                    "emergency": emergency,
                    "msg":
                    {
                        "direction": target,
                        "LED": target
                    }
                },
                "protocolVersion": 4.1
            }
            print(response)

            # send new targetLocation to bot
            client.publish(MQTT_TOPIC, json.dumps(response))
            
        # else:
        #     print("Recieved message that wasn't addressed to me.")
    else:
        if (request["protocolVersion"] < 4.1):
            print("WARNING! Deprecated protocol was used.")
        else:
            print("ERROR! Didn't understand syntax of request bot.")


client = connect_mqtt()

def run():
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()
