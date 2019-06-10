global RobotState
global CornerPositions

import numpy as np

RobotState = []
CompletedMove = []
CornerPositions =[[0,0],[0,0],[0,0],[0,0]]
Grid = []
def update_state(state):
    RobotState = state

def g_start(nbots, gsize):
    global RobotState
    RobotState = [[0,0,0] for i in range(nbots)]

    global CompletedMove
    CompletedMove = [1 for j in range(nbots)]

    global Grid
    Grid = [[[0,0] for ii in range(gsize)] for jj in range(gsize)]

