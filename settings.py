global RobotState;
global CornerPositions;

RobotState = [[0,0,0],[0,0,0],[0,0,0],[0,0,0]]
CompletedMove = [1,1,1,1]
CornerPositions =[[0,0],[0,0],[0,0],[0,0],[0,0]]
Grid = []
def update_state(state):
    RobotState = state;

