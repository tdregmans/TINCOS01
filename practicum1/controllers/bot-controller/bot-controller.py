from controller import Supervisor
print("running")

start_pos = [0, 0, 0]
target_pos = [0.2, 0.4, 0]

STEP = 0.1

# create the Robot instance
robot = Supervisor()
supervisorNode = robot.getSelf()

trans = supervisorNode.getField("translation")
# trans.setSFVec3f(supervisorNode.getField("startpoint"))
trans.setSFVec3f(start_pos)

# get the time step of the current world
timestep = int (robot.getBasicTimeStep())

# calculate a multiple of timestep close to one second
duration = (1000 // timestep) * timestep

def getCloser(value, target):
    if value > target:
        return value - STEP
    elif value < target:
        return value + STEP
    else:
        return value
    
    
# execute every second
while robot.step(duration) != -1:
    
    # get handle to translation field
    trans = supervisorNode.getField("translation")
    # set position ; pos is a list with 3 elements : x , y and z coordinates
    current_pos = supervisorNode.getPosition()
    # target_pos = supervisorNode.getField("endpoint")
    new_pos = [getCloser(current_pos[0], target_pos[0]), getCloser(current_pos[1], target_pos[1]), 0]
    trans.setSFVec3f(new_pos)
    