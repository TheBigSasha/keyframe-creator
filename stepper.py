import time
import pandas as pd
import pygame
import mecademicpy.robot as mdr

from maxVelCalc import calculateLimitingMaxVel
from mockRobot import MockRobot

IP = "192.168.0.100"
MAX_ANGLE = 180
DEFAULT_SPEED = 100
DEFAULT_SENSITIVITY = 3
TRIGGER_DEADZONE = 0.2

saved_moves = pd.DataFrame(columns=["x", "y", "z", "alpha", "beta", "gamma", "duration"])

"""
    Saves the position to the saved_moves dataframe
"""
def savePos(x, y, z, alpha, beta, gamma, duration):
    saved_moves.loc[-1] = [x, y, z, alpha, beta, gamma, duration]
    print(saved_moves.tail())

"""
    Writes the moves to a file with the name moves_<timestamp>.csv
"""
def writeMovesToFile(filename = f"moves_{time.time()}"):
    saved_moves.to_csv(filename + ".csv")

"""
    Initializes the robot and returns it, after this the invariant is that the robot is ready to move and the initial position is the first position in the saved_moves dataframe
"""
def init_robot():
    robot = mdr.Robot()
    robot.Connect(address='192.168.0.100')
    robot.WaitConnected()
    robot.SetJointVel(0.25)
    robot.ActivateRobot()
    robot.WaitActivated()
    robot.Home()
    robot.WaitHomed()
    coords = robot.GetJoints()
    savePos(coords[0], coords[1], coords[2], coords[3], coords[4], coords[5], 0)
    return robot

"""MOCK version of init_robot"""
def init_robot_mock():
    robot = MockRobot()
    robot.Connect(address='192.168.0.100')
    robot.WaitConnected()
    robot.SetJointVel(0.25)
    robot.ActivateRobot()
    robot.WaitActivated()
    robot.Home()
    robot.WaitHomed()
    coords = robot.GetJoints()
    savePos(coords[0], coords[1], coords[2], coords[3], coords[4], coords[5], 0)
    return robot


"""
    Moves the robot by a delta amount in each axis and saves the new position to the saved_moves dataframe
"""
def moveRobot(robot, dX, dY, dZ, dA, dB, dG, speed):
    prevPos = robot.GetJoints()
    newPos = [prevPos[0] + dX, prevPos[1] + dY, prevPos[2] + dZ, prevPos[3] + dA, prevPos[4] + dB, prevPos[5] + dG]
    newPos = [min(abs(newPos[i]), MAX_ANGLE) for i in range(len(newPos))]
    maxVel = calculateLimitingMaxVel(prevPos, newPos, speed)
    robot.SetJointVel(maxVel)
    robot.MoveJoints(newPos[0], newPos[1], newPos[2], newPos[3], newPos[4], newPos[5])
    robot.WaitIdle()
    settledPos = robot.GetJoints()
    savePos(settledPos[0], settledPos[1], settledPos[2], settledPos[3], settledPos[4], settledPos[5], speed)

# initialize pygame for joystick / kb input
print("Loading pygame... may take a few seconds")
pygame.init()
background_colour = (0, 0, 0)
screen = pygame.display.set_mode((300, 300))
pygame.display.set_caption('Robot Control Input Window')
screen.fill(background_colour)
pygame.display.flip()

# Joystick init
joysticks = []
clock = pygame.time.Clock()
keepPlaying = True
print("initalizing joysticks")
for i in range(0, 10):
    clock.tick(60)
    for i in range(0, pygame.joystick.get_count()):
        # create an Joystick object in our list
        joysticks.append(pygame.joystick.Joystick(i))
        # initialize the appended joystick (-1 means last array item)
        joysticks[-1].init()
        # print a statement telling what the name of the controller is
        print ("Detected joystick "),joysticks[-1].get_name(),"'"
    for event in pygame.event.get():
        # The 0 button is the 'a' button, 1 is the 'b' button, 2 is the 'x' button, 3 is the 'y' button
        print(event)
        # for al the connected joysticks



# clear the terminal
print(chr(27) + "[2J")

robot = init_robot_mock() if input("Use mock robot? (y/n)") == "y" else init_robot()

# main loop
currentoffsets = [0, 0, 0, 0, 0, 0]
cur_speed = DEFAULT_SPEED
lastMoveTime = -1
shift = False
moving = False


MOVING_STR = """
[CONTROLLER] Press A to start moving. Press B to stop moving. Press X to save moves to file and exit. Adjust time between moves with the D-Pad. Use the joysticks and triggers to move.

[KEYBOARD] Press space to start moving. Press escape to stop moving. Press backquote to save moves to file and exit. Adjust time between moves with the arrow keys. Use WASD + QE to move. Hold shift to change the axes being moved.
"""
print(MOVING_STR)

keepPlaying = True
def action_write_and_exit():
    writeMovesToFile()
    global keepPlaying
    keepPlaying = False
    robot.Disconnect()
    robot.WaitDisconnected()
    print("X")

def action_start_moving():
    global moving
    moving = True
    print("A")

def action_stop_moving():
    global moving
    moving = False
    print(MOVING_STR)


while keepPlaying:
    for event in pygame.event.get():
        shiftOffset = 0 if shift else 3
        # The 0 button is the 'a' button, 1 is the 'b' button, 2 is the 'x' button, 3 is the 'y' button
        if event.type == pygame.JOYBUTTONUP:
            button_id = event.button
            if button_id == 0:
                action_start_moving()
            elif button_id == 1:
                action_stop_moving()
            elif button_id == 2:
                action_write_and_exit()
            # elif button_id == 3 and event.type == pygame.JOYBUTTONDOWN:
            #     print("Y")
            # elif button_id == 4 and event.type == pygame.JOYBUTTONDOWN:
            #     print("LB")
            # elif button_id == 5 and event.type == pygame.JOYBUTTONDOWN:
            #     print("RB")
            # elif button_id == 6 and event.type == pygame.JOYBUTTONDOWN:
            #     print("LJoy")
            # elif button_id == 7 and event.type == pygame.JOYBUTTONDOWN:
            #     print("RJoy")
        else:
            if event.type == pygame.JOYAXISMOTION:
                if event.axis == 0:
                    currentoffsets[0] = event.value * DEFAULT_SENSITIVITY
                elif event.axis == 1:
                    currentoffsets[1] = event.value * DEFAULT_SENSITIVITY
                elif event.axis == 2:
                    if event.value < TRIGGER_DEADZONE:
                        currentoffsets[2] = 0
                    else:
                        currentoffsets[2] = event.value * DEFAULT_SENSITIVITY
                elif event.axis == 3:
                    currentoffsets[3] = event.value * DEFAULT_SENSITIVITY
                elif event.axis == 4:
                    currentoffsets[4] = event.value * DEFAULT_SENSITIVITY
                elif event.axis == 5:
                    if event.value < TRIGGER_DEADZONE:
                        currentoffsets[5] = 0
                    else:
                        currentoffsets[5] = event.value * DEFAULT_SENSITIVITY
            elif event.type == pygame.JOYHATMOTION:
                if event.value[0] == 1:
                    cur_speed += 10
                elif event.value[0] == -1:
                    cur_speed -= 10
                elif event.value[1] == 1:
                    cur_speed += 1
                elif event.value[1] == -1:
                    cur_speed -= 1
                cur_speed = max(10,cur_speed)
                print(f"Time between move is: {cur_speed * 10}ms")
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LSHIFT:
                    shift = True
                    print(f"SHIFT {shiftOffset}")
                elif event.key == pygame.K_SPACE:
                    action_start_moving()
                elif event.key == pygame.K_ESCAPE:
                    action_stop_moving()
                elif event.key == pygame.K_BACKQUOTE:
                    action_write_and_exit()
                elif event.key == pygame.K_UP:
                    cur_speed += 10
                elif event.key == pygame.K_DOWN:
                    cur_speed -= 10
                elif event.key == pygame.K_LEFT:
                    cur_speed += 1
                elif event.key == pygame.K_RIGHT:
                    cur_speed -= 1
                elif event.key == pygame.K_w:
                    currentoffsets[0 + shiftOffset] = DEFAULT_SENSITIVITY
                elif event.key == pygame.K_s:
                    currentoffsets[0 + shiftOffset] = -DEFAULT_SENSITIVITY
                elif event.key == pygame.K_a:
                    currentoffsets[1 + shiftOffset] = DEFAULT_SENSITIVITY
                elif event.key == pygame.K_d:
                    currentoffsets[1 + shiftOffset] = -DEFAULT_SENSITIVITY
                elif event.key == pygame.K_q:
                    currentoffsets[2 + shiftOffset] = DEFAULT_SENSITIVITY
                elif event.key == pygame.K_e:
                    currentoffsets[2 + shiftOffset] = -DEFAULT_SENSITIVITY
                cur_speed = max(10,cur_speed)
                print(f"Time between move is: {cur_speed * 10}ms")

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LSHIFT:
                    shift = False
                    print(f"UNSHIFT {shiftOffset}")
                elif event.key == pygame.K_w:
                    currentoffsets[0] = 0
                    currentoffsets[3] = 0
                elif event.key == pygame.K_s:
                    currentoffsets[0] = 0
                    currentoffsets[3] = 0
                elif event.key == pygame.K_a:
                    currentoffsets[1] = 0
                    currentoffsets[4] = 0
                elif event.key == pygame.K_d:
                    currentoffsets[1] = 0
                    currentoffsets[4] = 0
                elif event.key == pygame.K_q:
                    currentoffsets[2] = 0
                    currentoffsets[5] = 0
                elif event.key == pygame.K_e:
                    currentoffsets[2] = 0
                    currentoffsets[5] = 0

    tmstmp = time.time_ns() # convert to milliseconds
    if (tmstmp / 1000 / 1000) % cur_speed == 0 and tmstmp / 1000 / 1000 != lastMoveTime and moving:
        print(currentoffsets)
        lastMoveTime = tmstmp / 1000 / 1000
        moveRobot(robot, currentoffsets[0], currentoffsets[1], currentoffsets[2], currentoffsets[3], currentoffsets[4], currentoffsets[5], cur_speed)
