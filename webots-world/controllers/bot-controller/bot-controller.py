from controller import Supervisor
from controller import LED
from controller import DistanceSensor
import sys
from paho.mqtt import client as mqtt_client
import time
import json

# create the Robot instance
robot = Supervisor()
supervisorNode = robot.getSelf()

BOT_ID = robot.getName()

MQTT_BROKER = "broker.mqtt-dashboard.com" 
MQTT_PORT = 1883
MQTT_CLIENTID = "TINCOS01-BHT-" + str(BOT_ID) + "-DT" # DT means Digital Twin
MQTT_TOPIC = "TINCOS/comms"
MQTT_EMERGENCY_TOPIC = "TINCOS/protocol/emergency"

global emergency
emergency = 0

##################################################
################ MQTT CONNECTION #################
##################################################

client = mqtt_client.Client(MQTT_CLIENTID)

def connect_mqtt() -> mqtt_client:
    # def on_connect(client, userdata, flags, rc):
        # if rc == 0:
            # print("Connected to MQTT Broker!")
        # else:
            # print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(MQTT_CLIENTID)
    # client.username_pw_set(username, password)
    # client.on_connect = on_connect
    client.connect(MQTT_BROKER, MQTT_PORT)
    return client
    
def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        payload = msg.payload.decode()
        topic = msg.topic
        # print(payload)
        executeServerCommand(payload)
    print(BOT_ID + " subscribed on " + MQTT_TOPIC)
    client.subscribe(MQTT_TOPIC)
    client.on_message = on_message


##################################################
################## WEBOTS CODE ###################
##################################################

print(BOT_ID + " started")

# Set start and target positions
if (BOT_ID == "bot1"):
    start_pos = [0, 0, 0]
if (BOT_ID == "bot2"):
    start_pos = [0.1, 0.0, 0]
if (BOT_ID == "bot3"):
    start_pos = [0.0, 0.1, 0]

trans = supervisorNode.getField("translation")
trans.setSFVec3f(start_pos)

STEP = 0.1
# get the time step of the current world
timestep = int (robot.getBasicTimeStep())

LED_N = robot.getDevice('LED_N')
LED_E = robot.getDevice('LED_E')
LED_S = robot.getDevice('LED_S')
LED_W = robot.getDevice('LED_W')

DS_N = robot.getDevice('DS_N')
DS_E = robot.getDevice('DS_E')
DS_S = robot.getDevice('DS_S')
DS_W = robot.getDevice('DS_W')

DS_N.enable(timestep)
DS_E.enable(timestep)
DS_S.enable(timestep)
DS_W.enable(timestep)
current_pos = supervisorNode.getPosition()
print(BOT_ID + " location: " + str(current_pos))

# calculate a multiple of timestep close to one second
duration = (1000 // timestep) * timestep

def getCloser(value, target):
    if value > target:
        return value - STEP
    elif value < target:
        return value + STEP
    else:
        return value

def calcuateObstacles():
    obstacles = []
    current_pos = supervisorNode.getPosition()
    # North
    if (round(DS_N.getValue(), 2) < STEP):
        obstacle = {
            "x": round(current_pos[0] + 0.1, 1),
            "y": round(current_pos[1], 1)
        }
        obstacles.append(obstacle)
    # East
    if (round(DS_E.getValue(), 2) < STEP):
        obstacle = {
            "x": round(current_pos[0], 1),
            "y": round(current_pos[1] - 0.1, 1)
        }
        obstacles.append(obstacle)
    # South
    if (round(DS_S.getValue(), 2) < STEP):
        obstacle = {
            "x": round(current_pos[0] - 0.1, 1),
            "y": round(current_pos[1], 1)
        }
        obstacles.append(obstacle)
    # West
    if (round(DS_W.getValue(), 2) < STEP):
        obstacle = {
            "x": round(current_pos[0], 1),
            "y": round(current_pos[1] + 0.1, 1)
        }
        obstacles.append(obstacle)

    print(round(DS_N.getValue(), 2))
    print(round(DS_E.getValue(), 2))
    print(round(DS_S.getValue(), 2))
    print(round(DS_W.getValue(), 2))
    return obstacles

def createRequest():
    # return a valid request of the bot to the server with protocol 2.0
    global emergency
    current_pos = supervisorNode.getPosition()
    obstacles = calcuateObstacles()
    request = {
        "data": 
        {
            "sender": BOT_ID,
            "target": "server",
            "emergency": emergency,
            "msg":
            {
                "currentLocation":
                {
                    "x": current_pos[0],
                    "y": current_pos[1]
                },
                "obstacles": obstacles,
            }
        },
        "protocolVersion": 4.1
    }
    
    
    return json.dumps(request)

def callEmergency():
    print(BOT_ID + " stopped for emergency")
    sys.exit()

def isEmergency():
    return emergency

def isEmptyField(x, y):
    # # double check if targetLocation is free
    location = {
        "x": round(x, 2),
        "y": round(y, 2)
    }
    print(calcuateObstacles())
    return not location in calcuateObstacles()
    
def goTo(direction):
    currentX = round(supervisorNode.getPosition()[0], 2)
    currentY = round(supervisorNode.getPosition()[1], 2)
    if (direction == "N"):
        targetX = currentX + 0.1
        targetY = currentY
        if isEmptyField(targetX, targetY):
            trans.setSFVec3f([targetX, targetY, 0])
        else:
            print(BOT_ID + " wanted to collide with obstacle!")
    elif (direction == "E"):
        targetX = currentX
        targetY = currentY + -0.1
        if isEmptyField(targetX, targetY):
            trans.setSFVec3f([targetX, targetY, 0])
        else:
            print(BOT_ID + " wanted to collide with obstacle!")
    elif (direction == "S"):
        targetX = currentX + -0.1
        targetY = currentY
        if isEmptyField(targetX, targetY):
            trans.setSFVec3f([targetX, targetY, 0])
        else:
            print(BOT_ID + " wanted to collide with obstacle!")
    elif (direction == "W"):
        targetX = currentX
        targetY = currentY + 0.1
        if isEmptyField(targetX, targetY):
            trans.setSFVec3f([targetX, targetY, 0])
        else:
            print(BOT_ID + " wanted to collide with obstacle!")
    else:
        print(BOT_ID + " didn't change location. current location: " + str(current_pos))
    # print(supervisorNode.getPosition()[0] + -0.1)
    print([currentX, currentY])
    
    # x = targetLocation["x"]
    # y = targetLocation["y"]
    



def turnOnLed(led):
    LED_N.set(led == "N")
    LED_E.set(led == "E")
    LED_S.set(led == "S")
    LED_W.set(led == "W")


def executeServerCommand(payload):
    request = json.loads(payload)
    if (request["protocolVersion"] == 4.1):
        data = request["data"]
        # print(request)
        if (data["emergency"] == 1):
            callEmergency()
        elif (data["target"] == BOT_ID):
            sender = data["sender"]
            led = data["msg"]["LED"]


            targetLocation = data["msg"]["direction"]

            goTo(targetLocation)

            turnOnLed(led)
            
            client.publish(MQTT_TOPIC, createRequest())
            
        # else:
        #     print("Recieved message that wasn't addressed to me.")
    else:
        if(request["protocolVersion"] < 4.1):
            print("WARNING! Deprecated protocol was used.")
        else:
            print("ERROR! Didn't understand syntax of request bot.")

client = connect_mqtt()
subscribe(client)
client.publish(MQTT_TOPIC, createRequest())
    
# execute every second
while robot.step(duration) != -1:
    current_pos = supervisorNode.getPosition()
    
    
    client.loop(timeout=0.01, max_packets=10000)

    if(isEmergency() == 1):
        print(BOT_ID + " stopped for emergency")
        sys.exit()
    
    
    