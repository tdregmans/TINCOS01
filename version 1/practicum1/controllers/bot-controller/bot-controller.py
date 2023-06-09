from controller import Supervisor
from controller import LED
from controller import DistanceSensor

from paho.mqtt import client as mqtt_client
import time

# create the Robot instance
robot = Supervisor()
supervisorNode = robot.getSelf()

BOT_ID = robot.getName()

MQTT_BROKER = "broker.mqtt-dashboard.com" 
MQTT_PORT = 1883
MQTT_CLIENTID = "TINCOS01-BHT-" + str(BOT_ID) + "-DT" # DT means Digital Twin
MQTT_TOPIC = "TINCOS/protocol/communication"
MQTT_EMERGENCY_TOPIC = "TINCOS/protocol/emergency"

##################################################
################ MQTT CONNECTION #################
##################################################

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
        print(BOT_ID + " received `{payload}` from `{topic}` topic")
        
        executeServerCommand(payload, topic)

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


##################################################
################## WEBOTS CODE ###################
##################################################

print("Robot '"+str(BOT_ID)+"' started")

# Set start and target positions
if (BOT_ID == "bot1"):
    start_pos = [0.5, 0, 0]
    target_pos = [-0.3, 0.4, 0]
if (BOT_ID == "bot2"):
    start_pos = [0.3, 0.4, 0]
    target_pos = [-0.2, 0.4, 0]
if (BOT_ID == "bot3"):
    start_pos = [-0.2, 0.5, 0]
    target_pos = [0, -0.3, 0]

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

trans = supervisorNode.getField("translation")
# trans.setSFVec3f(supervisorNode.getField("startpoint"))
trans.setSFVec3f(start_pos)

def executeServerCommand(payload, topic):
    print(payload)

# calculate a multiple of timestep close to one second
duration = (1000 // timestep) * timestep

def getCloser(value, target):
    if value > target:
        return value - STEP
    elif value < target:
        return value + STEP
    else:
        return value
    
def updateLEDS():
    # Turn on LEDS of distances where bot cannot move
    LED_N.set(DS_N.getValue() < STEP)
    LED_E.set(DS_E.getValue() < STEP)
    LED_S.set(DS_S.getValue() < STEP)
    LED_W.set(DS_W.getValue() < STEP)
    
    
# execute every second
while robot.step(duration) != -1:
    current_pos = supervisorNode.getPosition()
    print(BOT_ID + " DS N: " + str(DS_N.getValue()))
    print(BOT_ID + " DS E: " + str(DS_E.getValue()))
    print(BOT_ID + " DS S: " + str(DS_S.getValue()))
    print(BOT_ID + " DS W: " + str(DS_W.getValue()))
    
    if(target_pos == current_pos):
        print(BOT_ID + " arrived at target position.")
    
    # get handle to translation field
    # trans = supervisorNode.getField("translation")
    # set position ; pos is a list with 3 elements : x , y and z coordinates
    
    # target_pos = supervisorNode.getField("endpoint")
    # new_pos = [getCloser(current_pos[0], target_pos[0]), getCloser(current_pos[1], target_pos[1]), 0]
    # trans.setSFVec3f(new_pos)
    
    updateLEDS()
    