from maxVelCalc import calculateLimitingMaxVel
import time

class MockRobot:
    def __init__(self, address: str = ""):
        self.ip_address = address
        self.is_connected = False
        self.is_activated = False
        self.is_homed = False
        self.max_velocity = 0.25
        self.position = [0, 0, 0, 0, 0, 0]
        print("USING MOCK ROBOT")

    def Connect(self, address: str):
        self.is_connected = True
        print(f"Connected to robot at {address}")

    def Disconnect(self):
        self.is_connected = False
        print(f"Disconnected from robot at {self.ip_address}")

    def WaitConnected(self):
        pass

    def ActivateRobot(self):
        self.is_activated = True

    def ActivateSim(self):
        self.is_activated = True

    def WaitActivated(self):
        pass

    def Home(self):
        self.is_homed = True
        print("Homing robot")

    def WaitHomed(self):
        pass

    def GetJoints(self):
        return self.position

    def MovePose(self, x, y, z, rx, ry, rz):
        print(f"Moving to pose: ({x}, {y}, {z}, {rx}, {ry}, {rz})")
        deltaPos = [x - self.position[0], y - self.position[1], z - self.position[2], rx - self.position[3], ry - self.position[4], rz - self.position[5]]
        maxVel = calculateLimitingMaxVel(self.position, [x, y, z, rx, ry, rz], self.max_velocity)
        largestDelta = max([abs(deltaPos[i]) for i in range(len(deltaPos))])
        timeToMove = largestDelta / maxVel
        print(f"Time to move: {timeToMove}s")
        time.sleep(timeToMove / 1000)
        self.position = [x, y, z, rx, ry, rz]
        print(f"Moved to pose: ({x}, {y}, {z}, {rx}, {ry}, {rz})")

    def MoveJoints(self, x, y, z, rx, ry, rz):
        self.MovePose(x, y, z, rx, ry, rz)

    def SetJointVel(self, vel):
        self.max_velocity = vel

    def WaitIdle(self, duration = 0):
        time.sleep(duration)

