
import threading
import time
import cv2
import numpy as np
import argparse
import imutils
import time
import copy
import math
from math import pi as PI
from math import *
from LineFollow import Follow
import settings
from socket_wrapper import SocketWrapper

#TODO These need to be static IP addresses so we dont have to keep changing them
#needs to be changed on the arduino IDE

Robot_1_IP = "ws://192.168.137.238:81/ws"
Robot_2_IP = "ws://192.168.137.14:81/ws"
Robot_3_IP = "ws://192.168.137.149:81/ws"
Robot_4_IP = "ws://192.168.137.70:81/ws"

#IDS = 0,28,13,19

Robot1 = SocketWrapper(Robot_1_IP);
#Robot2 = SocketWrapper(Robot_2_IP);
# Robot3 = SocketWrapper(Robot_3_IP);
# Robot4 = SocketWrapper(Robot_4_IP);



def goleft(RobotNum, diff):
    sleep_amount = 0.1
    if diff > 40:
        sleep_amount = 0.5
    sleep_amount = sleep_amount/4

    if(RobotNum==1):
        Robot1.send_motion('~', 100, 80)
        time.sleep(sleep_amount)
        Robot1.send_motion('~', 90, 90)
    elif (RobotNum == 2):
        Robot2.send_motion('~', 110, 70)
        time.sleep(sleep_amount)
        Robot2.send_motion('~', 90, 90)
    elif (RobotNum == 3):
        Robot3.send_motion('~', 100, 80)
        time.sleep(sleep_amount)
        Robot3.send_motion('~', 90, 90)
    elif (RobotNum == 4):
        Robot4.send_motion('~', 100, 80)
        time.sleep(sleep_amount)
        Robot4.send_motion('~', 90, 90)
    else:
        print("error: only 4 robots")


def goright(RobotNum, diff):
    sleep_amount = 0.1
    if diff > 40:
        sleep_amount = 0.5
    sleep_amount = sleep_amount/4

    if (RobotNum == 1):
        Robot1.send_motion('~',80, 100)
        time.sleep(sleep_amount)
        Robot1.send_motion('~', 90, 90)
    elif (RobotNum == 2):
        Robot2.send_motion('~', 80, 100)
        time.sleep(sleep_amount)
        Robot2.send_motion('~', 90, 90)
    elif (RobotNum == 3):
        Robot3.send_motion('~', 80, 100)
        time.sleep(sleep_amount)
        Robot3.send_motion('~', 90, 90)
    elif (RobotNum == 4):
        Robot4.send_motion('~', 80, 100)
        time.sleep(sleep_amount)
        Robot4.send_motion('~', 90, 90)
    else:
        print("error: only 4 robots")


def goforward(RobotNum, diff):
    sleep_amount = 0.2
    if diff > 40:
        sleep_amount = 0.5
    sleep_amount = sleep_amount/4
    if (RobotNum == 1):
        print("correct heading, going fowards")
        Robot1.send_motion('#', "F", 0)
        time.sleep(sleep_amount)
        Robot1.send_motion('~', 90, 90)
    elif (RobotNum == 2):
        print("correct heading, going fowards")
        Robot2.send_motion('#', "F", 0)
        time.sleep(sleep_amount)
        Robot2.send_motion('~', 90, 90)
    elif (RobotNum == 3):
        print("correct heading, going fowards")
        Robot3.send_motion('#', "F", 0)
        time.sleep(sleep_amount)
        Robot3.send_motion('~', 90, 90)
    elif (RobotNum == 4):
        print("correct heading, going fowards")
        Robot4.send_motion('#', "F", 0)
        time.sleep(sleep_amount)
        Robot4.send_motion('~', 90, 90)
    else:
        print("error: only 4 robots")


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
    return ((sx - ex)**2 + (ey-sy)**2)**(0.5)

def goto1( x,y ):
    error = 20
    desired_h = getAngleBetweenPoints(settings.RobotState[0][0],settings.RobotState[0][1] ,x,y )
    desired_h = math.degrees(desired_h)
    print("desired", desired_h)
    print("actual", settings.RobotState[0][2])

    difference = 180 - abs(abs(desired_h - settings.RobotState[0][2]) - 180)
    tolerance = 30
    robotx, roboty, _ = settings.RobotState[0]
    while ( dist([robotx, roboty], [x,y]) > tolerance):
        time.sleep(1)
        desired_h = getAngleBetweenPoints(settings.RobotState[0][0], settings.RobotState[0][1], x, y)
        desired_h = math.degrees(desired_h)
        print("desired", desired_h)
        print("actual", settings.RobotState[0][2])
        print("difference", difference)
        difference = 180 - abs(abs(desired_h - settings.RobotState[0][2]) - 180)

        while (difference > error ):




            time.sleep(1)
            print("desired", desired_h)
            print("actual", settings.RobotState[0][2])
            print("difference", difference)

            if (settings.RobotState[0][2]< desired_h):
                if desired_h - settings.RobotState[0][2] > 180:
                    print("go left")
                    goleft(1)
                else:
                    print("go right")
                    goright(1)
            else:
                if settings.RobotState[0][2] - desired_h > 180:
                    print("go right")
                    goright(1)
                else:
                    print("go left")
                    goleft(1)






            difference = 180 - abs(abs(desired_h - settings.RobotState[0][2]) - 180)

        Robot1.send_motion('~', 90, 90)
        print("correct heading, going fowards")

        time.sleep(.5)

        Robot1.send_motion('#', "F", 0)
        time.sleep(.5)
        Robot1.send_motion('~', 90, 90)
        robotx, roboty, _ = settings.RobotState[0]
        print(robotx,roboty)
        print(x,y,)
    print("Location Reached, YAY!")
    return;


def gotoPos( x,y, botNum ):
    sleep_amount = 0.01
    error = 10
    robotx, roboty, actual_h = settings.RobotState[botNum]

    desired_h = getAngleBetweenPoints(robotx, roboty ,x,y )
    desired_h = math.degrees(desired_h)

    difference = 180 - abs(abs(desired_h - actual_h) - 180)
    tolerance = 25
    dist_diff = dist([robotx, roboty], [x,y])
    while (dist_diff > tolerance ):

        time.sleep(sleep_amount)
        robotx, roboty, actual_h = settings.RobotState[botNum]
        desired_h = getAngleBetweenPoints(robotx, roboty, x, y)
        desired_h = math.degrees(desired_h)
        #print("desired", desired_h)
        #print("actual",actual_h)
        #print("difference", difference)
        difference = 180 - abs(abs(desired_h - actual_h) - 180)

        while (difference > error ):
            robotx, roboty, actual_h = settings.RobotState[botNum]
            time.sleep(sleep_amount)
            print(str(botNum) + "desired", desired_h)
            print(str(botNum) + "actual", actual_h)
            print(str(botNum) + "difference", difference)

            if (actual_h < desired_h):
                if desired_h - actual_h > 180:
                    print("go left, bot:" + str(botNum))
                    goleft(botNum+1,difference)
                else:
                    print("go right, bot:" + str(botNum))
                    goright(botNum+1,difference)
            else:
                if actual_h - desired_h > 180:
                    print("go right, bot:" + str(botNum))
                    goright(botNum+1,difference)
                else:
                    print("go left, bot:" + str(botNum))
                    goleft(botNum+1,difference)
            difference = 180 - abs(abs(desired_h -actual_h) - 180)
        dist_diff = dist([robotx, roboty], [x, y])
        goforward(botNum+1,dist_diff)
        robotx, roboty, actual_h = settings.RobotState[botNum]
        print(robotx,roboty)
        print(x,y,)
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
    def __init__(self, name, botNum, N):
        threading.Thread.__init__(self)
        self.name = name
        self.botNum = botNum
        self.step = 0
        self.N = N


    def run(self):
        N = self.N
        print("done run")
        time.sleep(4)
        print("HERE IS THE GRID POSITIONS")
        print(settings.Grid)
        #TODO: Get desiredx/y from algorithm
        #psuedocode: Get desired x/y, move, wait for other bots, repeat
        i = 0
        j = 0
        arr = [
            [0,0],
            [0,1],
            [0,2],
            [1,2],
            [2,2],
            [2,1],
            [1,1],
            [1,0]
        ]
        while True:
            i, j = arr[self.step][0], arr[self.step][1]
            time.sleep(0.5)
            settings.CompletedMove[self.botNum] = 0
            #get desiredx/y
            # BOX
            """"
            ii = (self.step + self.botNum*2) %4
            if ii == 0:
                desired_x = settings.CornerPositions[1][0]
                desired_y = settings.CornerPositions[1][1]
            elif ii == 1:
                desired_x = settings.CornerPositions[3][0]
                desired_y = settings.CornerPositions[3][1]
            elif ii == 2:
                desired_x = settings.CornerPositions[2][0]
                desired_y = settings.CornerPositions[2][1]
            else:
                desired_x = settings.CornerPositions[0][0]
                desired_y = settings.CornerPositions[0][1]
            """

            desired_x, desired_y = settings.Grid[i][j][0],  settings.Grid[i][j][1]
            self.step = (self.step + 1) % 8

            #move
            gotoPos(desired_x, desired_y, self.botNum)
            settings.CompletedMove[self.botNum] = 1
            print("BOT: " + str(self.botNum) + "completed it's move")
            print("i, j: " + str([i,j]))



            # wait.
            time.sleep(0.5)
            while settings.CompletedMove[0] + settings.CompletedMove[1] + settings.CompletedMove[2] + settings.CompletedMove[3]  < 4:
                print("BOT: " + str(self.botNum) + "completed it's move, and it waiting")
                time.sleep(0.5)













        # Robot1.send_motion('#','R',0)
        # Robot2.send_motion('#', 'R', 0)
        # Robot3.send_motion('#', 'R', 0)
        # Robot4.send_motion('#', 'R', 0)
        #
        #
        #
        #
        #
        # time.sleep(3)
        # Robot1.send_motion('~',90,90)
        # Robot2.send_motion('~', 90, 90)
        # Robot3.send_motion('~', 90, 90)
        # Robot4.send_motion('~', 90, 90)

def main():
    n = 1
    gridSize = 3
    arr = [
        [0, 0],
        [0, 1],
        [0, 2],
        [1, 2],
        [2, 2],
        [2, 1],
        [1, 1],
        [1, 0]
    ]

    bots = []
    for i in range(n):
        b = Thread_B("bot{}".format(i), i, gridSize)
        bots.append(b)

    a = Thread_A("camera_position_tracking")

    a.start()
    for bot in bots:
        bot.start()

    a.join()
    for bot in bots:
        bot.join()

if __name__ == '__main__':
    main()






