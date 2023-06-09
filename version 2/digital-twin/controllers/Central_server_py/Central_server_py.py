import json
import logging
import random
import time
from paho.mqtt import client as mqtt_client

from controller import Supervisor
from controller import Robot


# Create a Webots robot instance
supervisor = Supervisor() 

web_robot_0 = supervisor.getFromDef("pick_up_robot_0")
web_robot_1 = supervisor.getFromDef("pick_up_robot_1")
web_robot_2 = supervisor.getFromDef("pick_up_robot_2")
web_robot_3 = supervisor.getFromDef("pick_up_robot_3")

web_robots = [web_robot_0,web_robot_1,web_robot_2,web_robot_3]

Old_locations = [[-1,-1,-1],[-1,-1,-1],[-1,-1,-1],[-1,-1,-1]]

Old_directions = ["off","off","off","off"]
direction_options = ["off","forward","backwards","left","right"]

Old_sensor_values = [[-1,-1,-1,-1],[-1,-1,-1,-1],[-1,-1,-1,-1],[-1,-1,-1,-1]]

broker = 'localhost'
port = 1883
topic_server = "publish/server"
topic_robots = "publish/robots"
client_id = f'python-mqtt-{random.randint(0, 1000)}'
username = 'emqx'
password = 'public'

client = None

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60

FLAG_EXIT = False

#De functies location direction en sensor_values kunnen 1 functie worden.
def location(msg,robot):
    global client
    number_robot = int(msg[10])
    location = [round(round(web_robots[number_robot].getField('translation').getSFVec3f()[0],1)*10), round(round(web_robots[number_robot].getField('translation').getSFVec3f()[1],1)*10)]
    print(f"The location of `{robot}` is x : {location[0]} and y : {location[1]}")
    
    msg = (msg+f":({location[0]},{location[1]})")
    result = client.publish(topic_server, msg)
    status = result[0]
    if status == 0:
        print(f'Send `{msg}` to topic `{topic_server}`')
    else:
        print(f'Failed to send message to topic {topic_server}')
        return False
        
def direction(msg,robot):
    global client
    number_robot = int(msg[10])
    direction = web_robots[number_robot].getField('direction_lamps').getSFString()
    print(f"The direction of `{robot}` is x : {direction}")
    msg = (msg+f":{direction}")
    result = client.publish(topic_server, msg)
    status = result[0]
    if status == 0:
        print(f'Send `{msg}` to topic `{topic_server}`')
    else:
        print(f'Failed to send message to topic {topic_server}')
        return False
        
def sensor_value(msg,robot):
    global client
    number_robot = int(msg[10])
    sensor_values = [web_robots[number_robot].getField('sensors').getMFInt32(0), web_robots[number_robot].getField('sensors').getMFInt32(1),web_robots[number_robot].getField('sensors').getMFInt32(2),web_robots[number_robot].getField('sensors').getMFInt32(3)]     
    print(f"The sensor values of `{robot}` is x : {sensor_values}")
    msg = (msg+f":{sensor_values}")
    result = client.publish(topic_server, msg)
    status = result[0]
    if status == 0:
        print(f'Send `{msg}` to topic `{topic_server}`')
    else:
        print(f'Failed to send message to topic {topic_server}')
        return False

#Options are "web_robot_x:emgc:on_" and "web_robot_x:emgc:off"
def emergency(msg,robot):

    value_emergency = msg[17:20]
    if(value_emergency == "on_"):
        print(f"Emergency button has been pushed by `{robot}`")
        for web_robot in web_robots:
            web_robot.getField('emergency').setSFBool(True)
    elif(value_emergency == "off" and robot == "dsh_board_0"):
        print(f"Emergency button has been reset by `{robot}`")
        for web_robot in web_robots:
            web_robot.getField('emergency').setSFBool(False)
    else:
        print(f"Error while parsing command : `{msg}` from `{robot}`") 
        
def target(msg,robot):
    #Wat als de gebruiker -1 of 10 doorstuurt. Ik lees het dan uit als 1 of 0 etc
    valid_command = False
    try:
        number_robot = int(msg[10])
        target_robot_x = int(msg[18:19])
        target_robot_y = int(msg[20:21])
        valid_command = True
    except:
        print(f"Error while parsing command : `{msg}` from `{robot}`") 
    # if(valid_command and len(msg) > 21 and -1 < target_robot_x < 10 and  -1 < target_robot_y < 10):
    if(valid_command and len(msg) > 21):
        number_robot = int(msg[10])
        #Misschien moet ik doorgeven dat het gelukt is 
        target = [target_robot_x,target_robot_y]
        web_robots[number_robot].getField('target').setSFVec2f(target)

commands_web = ["loca","targ","dire","sens"]
commands_esp = ["emgc"]
commands_dsh = ["emgc"]
web_robots_str = ["web_robot_0","web_robot_1","web_robot_2","web_robot_3"]
esp_robots_str = ["esp_robot_0","esp_robot_1","esp_robot_2","esp_robot_3"]
dsh_boards_str =  ["dsh_board_0"]
functions = {
             'loca':location,
             'targ':target,
             'dire':direction,
             'sens':sensor_value,
             'emgc':emergency
            }

def connect_mqtt():
   
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            client.subscribe(topic_robots)
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    return client

def on_disconnect(client, userdata, rc):
    logging.info("Disconnected with result code: %s", rc)
    reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
    while reconnect_count < MAX_RECONNECT_COUNT:
        logging.info("Reconnecting in %d seconds...", reconnect_delay)
        time.sleep(reconnect_delay)

        try:
            client.reconnect()
            logging.info("Reconnected successfully!")
            return
        except Exception as err:
            logging.error("%s. Reconnect failed. Retrying...", err)

        reconnect_delay *= RECONNECT_RATE
        reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
        reconnect_count += 1
    logging.info("Reconnect failed after %s attempts. Exiting...", reconnect_count)
    global FLAG_EXIT
    FLAG_EXIT = True


def publish(client):

    if not client.is_connected():
        print("publish: MQTT client is not connected!")
        return False
    
    i = 0
    for web_robot in web_robots:
        location = [round(round(web_robot.getField('translation').getSFVec3f()[0],1)*10), round(round(web_robot.getField('translation').getSFVec3f()[1],1)*10)]
        direction = web_robot.getField('direction_lamps').getSFString()
        sensor_values = [web_robot.getField('sensors').getMFInt32(0), web_robot.getField('sensors').getMFInt32(1),web_robot.getField('sensors').getMFInt32(2),web_robot.getField('sensors').getMFInt32(3)]
        if(location[0] == Old_locations[i][0] and location[1] == Old_locations[i][1]):
            pass
        else:
            msg = f"{web_robots_str[i]}:loca:({location[0]},{location[1]})"
            result = client.publish(topic_server, msg)
            status = result[0]
            if status == 0:
                print(f'Send `{msg}` to topic `{topic_server}`')
            else:
                print(f'Failed to send message to topic {topic_server}')
                return False
                
        Old_locations[i][0] = location[0]
        Old_locations[i][1] = location[1]
        
        if(direction == Old_directions[i] and direction == Old_directions[i]):
            pass
        else:
            if direction not in direction_options:
                print(f"{web_robots_str[i]} with invalid direction : {direction}")
            else:
                msg = f"{web_robots_str[i]}:dire:{direction}"
                result = client.publish(topic_server, msg)
                status = result[0]
                if status == 0:
                    print(f'Send `{msg}` to topic `{topic_server}`')
                else:
                    print(f'Failed to send message to topic {topic_server}')
                    return False
                    
        Old_directions[i] = direction

        
        j = 0
        sensor_has_same_values = False
        for value in Old_sensor_values:
            if(Old_sensor_values[i][j] != sensor_values[j]):
                sensor_has_same_values = True
                break
            j += 1    
           
        if(sensor_has_same_values):
            msg = f"{web_robots_str[i]}:sens:{sensor_values}"
            result = client.publish(topic_server, msg)
            status = result[0]
            if status == 0:
                print(f'Send `{msg}` to topic `{topic_server}`')
            else:
                print(f'Failed to send message to topic {topic_server}')
                return False
        
        Old_sensor_values[i][0] = sensor_values[0]
        Old_sensor_values[i][1] = sensor_values[1]
        Old_sensor_values[i][2] = sensor_values[2]
        Old_sensor_values[i][3] = sensor_values[3]
        
        if(i == 3):
            return True
        i += 1
        
    return True


def on_message(client, userdata, msg):
    incoming = msg.payload.decode()
    print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
    pick_up_robot = None
    incoming_robot = incoming[:11]

    if incoming_robot in web_robots_str:
        print(f"This is robot : `{incoming_robot}`")
        pick_up_robot = incoming_robot
    elif incoming_robot in esp_robots_str:
        print(f"This is robot : `{incoming_robot}`")
        pick_up_robot = incoming_robot
    elif incoming_robot in dsh_boards_str:
        print(f"This is dashboard : `{incoming_robot}`")
        pick_up_robot = incoming_robot
    else:
        print(f"Incoming robot `{incoming}` not recognized")
        return
    
    incoming_command = incoming[12:16]
    if incoming_command in commands_web and pick_up_robot[0:3] == "web":
        print(f"{pick_up_robot} sent command `{incoming_command}`")
        functions[incoming_command](incoming,pick_up_robot)
    elif incoming_command in commands_esp and pick_up_robot[0:3] == "esp":
        print(f"{pick_up_robot} sent command `{incoming_command}`")
        functions[commands_esp[0]](incoming,pick_up_robot)
    elif incoming_command in commands_dsh and pick_up_robot[0:3] == "dsh":
        print(f"{pick_up_robot} sent command `{incoming_command}`")
        functions[incoming_command](incoming,pick_up_robot)
    elif incoming_command in commands_web and (pick_up_robot[0:3] == "esp" or pick_up_robot[0:3] == "dsh") or incoming_command in commands_esp and pick_up_robot[0:3] == "web" :
        print(f"{pick_up_robot} sent command `{incoming_command}` but has no rights to use this commands")
    else:
        print(f"Incoming command `{incoming_command}` not recognized")
        return

def run():
    i = 0
    global client
    client = connect_mqtt()
    client.loop_start()
    time.sleep(1)
    timer = 0
    while supervisor.step(64) != -1:
        if timer == 960:
            publish(client)
            timer = 0
        timer += 64
        pass
    
  
if __name__ == '__main__':
    run()