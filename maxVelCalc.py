
"""
    Derives the max velocity by finding the axis with the highest ratio of the target velocity to the max velocity and then limiting the target velocity to the max velocity of that axis
    # MAKE SURE THIS IS IN SYNC WITH FLOJOY::PYTHON::NODES::IO::ROBOTICS::ARMS::MECADEMIC::MOVE_KEYFRAMES::MOVE_KEYFRAMES.PY
"""
def calculateLimitingMaxVel(current, next, timeDeltaMS) -> float:
    deltaPosititons = [abs(current[i] - next[i]) for i in range(len(current))]  # the delta positions of each axis in degrees
    velocities = [150, 150, 180, 300, 300, 500]  # the max velocities of each axis in degrees per second
    maxVelocities = [deltaPosititons[i] / (timeDeltaMS) for i in range(len(deltaPosititons))]  # the max velocities of each axis in degrees per second
    highestVelRatio = (-1, -1)  # the highest velocity ratio and the index of the axis
    for i in range(len(maxVelocities)):
        ratio = maxVelocities[i] / velocities[i]
        if ratio > highestVelRatio[0]:
            highestVelRatio = (ratio, i)

    idxOfAxisToLimit = highestVelRatio[1]
    targetVelofAxisToLimit = max(maxVelocities[idxOfAxisToLimit], 0.001)
    ratioOfMaxtoTarget = velocities[idxOfAxisToLimit] / targetVelofAxisToLimit
    if ratioOfMaxtoTarget > 1:
        print("WARNING: The target velocity is higher than the max velocity of the axis. The axis will be limited to 100% of its max velocity.")
    if ratioOfMaxtoTarget < 0:
        print("WARNING: The target velocity is negative. The axis will be limited to 100% of its max velocity.")
    return abs(min(1, ratioOfMaxtoTarget))
