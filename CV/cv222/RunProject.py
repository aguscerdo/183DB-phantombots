import threading
import time
import math
from math import *
from CV.LineFollow import Follow
from CV import settings
from CV.socket_wrapper import SocketWrapper
from CV.cv222.config import ThreadConstants, CVConstants

constants = ThreadConstants()

def goleft(runWrap, RobotNum, diff):
    sleep_amount = constants.sleep
    if diff > 40:
        sleep_amount = 0.5

    bot = runWrap.get_bot(RobotNum)
    l = constants.go_left[RobotNum]
    
    bot.send_motion('~', l[0], l[1])
    time.sleep(sleep_amount)
    bot.send_motion('~', 90, 90)


def goright(runWrap, RobotNum, diff):
    sleep_amount = constants.sleep
    if diff > 40:
        sleep_amount = 0.5
    
    bot = runWrap.get_bot(RobotNum)
    l = constants.go_right[RobotNum]
    
    bot.send_motion('~', l[0], l[1])
    time.sleep(sleep_amount)
    bot.send_motion('~', 90, 90)


def goforward(runWrap, RobotNum, diff):
    sleep_amount = constants.sleep * 2
    if diff > 40:
        sleep_amount = 0.5
    
    bot = runWrap.get_bot(RobotNum)
    l = constants.go_right[RobotNum]
    
    bot.send_motion('#', "F", 0)
    time.sleep(sleep_amount)
    bot.send_motion('~', 90, 90)


def angle_trunc(a):
    while a < 0.0:
        a += pi * 2
    return a


def getAngleBetweenPoints(x_orig, y_orig, x_landmark, y_landmark):
    deltaY = y_landmark - y_orig
    deltaX = x_landmark - x_orig
    return angle_trunc(atan2(deltaY, deltaX))

def dist(start, end):
    sx, sy = start
    ex, ey = end
    return ((sx - ex)**2 + (ey-sy)**2)**0.5

def gotoPos(x, y, botNum, runWrapper):
    sleep_amount = 0.01
    error = 10
    robotx, roboty, actual_h = settings.RobotState[botNum]

    desired_h = getAngleBetweenPoints(robotx, roboty ,x,y )
    desired_h = math.degrees(desired_h)

    difference = 180 - abs(abs(desired_h - actual_h) - 180)
    tolerance = 25
    dist_diff = dist([robotx, roboty], [x,y])
    while dist_diff > tolerance:

        time.sleep(sleep_amount)
        robotx, roboty, actual_h = settings.RobotState[botNum]
        desired_h = getAngleBetweenPoints(robotx, roboty, x, y)
        desired_h = math.degrees(desired_h)
        #print("desired", desired_h)
        #print("actual",actual_h)
        #print("difference", difference)
        difference = 180 - abs(abs(desired_h - actual_h) - 180)

        while difference > error:
            robotx, roboty, actual_h = settings.RobotState[botNum]
            time.sleep(sleep_amount)
            print(str(botNum) + "desired", desired_h)
            print(str(botNum) + "actual", actual_h)
            print(str(botNum) + "difference", difference)

            if actual_h < desired_h:
                if desired_h - actual_h > 180:
                    print("go left, bot:" + str(botNum))
                    goleft(runWrapper, botNum, difference)
                else:
                    print("go right, bot:" + str(botNum))
                    goright(runWrapper, botNum, difference)
            else:
                if actual_h - desired_h > 180:
                    print("go right, bot:" + str(botNum))
                    goright(runWrapper, botNum, difference)
                else:
                    print("go left, bot:" + str(botNum))
                    goleft(runWrapper, botNum, difference)
            difference = 180 - abs(abs(desired_h -actual_h) - 180)
            
        dist_diff = dist([robotx, roboty], [x, y])
        goforward(runWrapper, botNum, dist_diff)
        
        robotx, roboty, actual_h = settings.RobotState[botNum]
        print(robotx, roboty)
        print(x, y)
        dist_diff = dist([robotx, roboty], [x, y])
        
    print("Location Reached, YAY!")
    return


class Thread_A(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        Follow()



class Thread_B(threading.Thread):
    def __init__(self, name, botNum, N, arr, runWrapper):
        threading.Thread.__init__(self)
        self.name = name
        self.botNum = botNum
        self.step = 0
        self.N = N
        self.arr = arr
        self.runWrapper = runWrapper


    def run(self):
        N = self.N
        print("done run")
        time.sleep(4)
        print("HERE IS THE GRID POSITIONS")
        print(settings.Grid)
        i = 0
        j = 0

        while True:
            i, j = self.arr[self.botNum][self.step][0], self.arr[self.botNum][self.step][1]
            time.sleep(0.5)
            settings.CompletedMove[self.botNum] = 0
            #get desiredx/y
            # BOX

            desired_x, desired_y = settings.Grid[i][j][0], settings.Grid[i][j][1]
            self.step = (self.step + 1) % 8

            #move
            gotoPos(desired_x, desired_y, self.botNum,  self.runWrapper)
            settings.CompletedMove[self.botNum] = 1
            print("BOT: " + str(self.botNum) + "completed it's move")
            print("i, j: " + str([i,j]))



            # wait.
            time.sleep(0.5)
            while settings.CompletedMove[0] + settings.CompletedMove[1] + settings.CompletedMove[2] + settings.CompletedMove[3]  < 4:
                print("BOT: " + str(self.botNum) + "completed it's move, and it waiting")
                time.sleep(0.5)


class RunThreadWrap:
    def __init__(self, n):
        self.bots = [
            SocketWrapper(constants.ip[i]) for i in range(n)
        ]
    
    def get_bot(self, i):
        return self.bots[i]


def run_system(nbots, gridSize, instructions):
    if nbots > constants.N_bots:
        raise RuntimeError("More bots than constants")

    rw = RunThreadWrap(nbots)

    bots = []
    for i in range(nbots):
        b = Thread_B("bot{}".format(i), i, gridSize, instructions, rw)
        bots.append(b)

    a = Thread_A("camera_position_tracking")

    a.start()
    for bot in bots:
        bot.start()

    a.join()
    for bot in bots:
        bot.join()
