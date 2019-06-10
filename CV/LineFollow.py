import cv2
import numpy as np
import time
import cv2.aruco as aruco
from math import *
import math

from CV.config import CVConstants
from CV import globals


RobotState = globals.RobotState
CornerPositions = globals.CornerPositions
CornerCounter = 0
cornerids = CVConstants.corner_ids

font = cv2.FONT_HERSHEY_SIMPLEX


def angle_trunc(a):
    while a < 0.0:
        a += pi * 2
    return a


def getAngleBetweenPoints(x_orig, y_orig, x_landmark, y_landmark):
    deltaY = y_landmark - y_orig
    deltaX = x_landmark - x_orig
    return angle_trunc(atan2(deltaY, deltaX))


def Follow():
    global CornerCounter
    cap = cv2.VideoCapture(0)
    print(cap.isOpened())
    time.sleep(1)
    _, img = cap.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_250)
    parameters = aruco.DetectorParameters_create()
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

    for i in range(4):
        _, img = cap.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_250)
        parameters = aruco.DetectorParameters_create()
        corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

        for x in range(0, len(ids)):

            Tempx = corners[x][0][0][0] + corners[x][0][1][0] + corners[x][0][2][0] + corners[x][0][3][0]
            Tempx = Tempx / 4
            Tempy = corners[x][0][0][1] + corners[x][0][1][1] + corners[x][0][2][1] + corners[x][0][3][1]
            Tempy = Tempy / 4

            if ids[x] == CVConstants.corner_ids[0]:
                globals.CornerPositions[0] = [Tempx, Tempy]
            elif ids[x] == CVConstants.corner_ids[1]:
                globals.CornerPositions[1] = [Tempx, Tempy]
            elif ids[x] == CVConstants.corner_ids[2]:
                globals.CornerPositions[2] = [Tempx, Tempy]
            elif ids[x] == CVConstants.corner_ids[3]:
                globals.CornerPositions[3] = [Tempx, Tempy]

    #get all vertices:
    lowest_sum = globals.CornerPositions[0][0] + globals.CornerPositions[0][1]
    highest_sum = lowest_sum
    bottom_right = globals.CornerPositions[0]
    bottom_left = globals.CornerPositions[0]
    top_right = globals.CornerPositions[0]
    top_left = globals.CornerPositions[0]
    
    taken = [0, 0]
    
    for i in range(4):
        cx, cy = globals.CornerPositions[i]
        sum = cx +cy
        if sum < lowest_sum:
            lowest_sum = sum
            bottom_right = globals.CornerPositions[i]
            taken[0] = i
        elif sum > highest_sum:
            highest_sum = sum
            top_left = globals.CornerPositions[i]
            taken[1] = i
    for i in range(4):
        if i not in taken:
            bottom_left = globals.CornerPositions[i]
            taken.append(i)
    for i in range(4):
        if i not in taken:
            top_right = globals.CornerPositions[i]
            taken.append(i)
    if bottom_left[0] > top_right[0]:
        bottom_left, top_right = top_right, bottom_left
        
    N = len(globals.Grid)
    hx = (top_left[0] - bottom_right[0])/(N - 1)
    hy = (top_left[1] - bottom_right[1])/(N - 1)
    
    for i in range(N):
        for j in range(N):
            globals.Grid[i][j][0] = bottom_right[0] + hx * i
            globals.Grid[i][j][1] = bottom_right[1] + hy * j

    while (1):
        _, img = cap.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)

        font = cv2.FONT_HERSHEY_SIMPLEX

        aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_250)
        parameters = aruco.DetectorParameters_create()

        corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

        CornerPositions = globals.CornerPositions

        cv2.circle(img, (int(CornerPositions[0][0]), int(CornerPositions[0][1])), 20, (0, 255, 0), -1)
        cv2.circle(img, (int(CornerPositions[1][0]), int(CornerPositions[1][1])), 20, (0, 255, 0), -1)
        cv2.circle(img, (int(CornerPositions[2][0]), int(CornerPositions[2][1])), 20, (0, 250, 0), -1)
        cv2.circle(img, (int(CornerPositions[3][0]), int(CornerPositions[3][1])), 20, (0, 0, 255), -1)


        cv2.line(img,(int(CornerPositions[0][0]),int(CornerPositions[0][1])),(int(CornerPositions[1][0]),int(CornerPositions[1][1])), (255,0,0),2)
        cv2.line(img, (int(CornerPositions[0][0]), int(CornerPositions[0][1])), (int(CornerPositions[3][0]), int(CornerPositions[3][1])), (255, 0, 0), 2)
        cv2.line(img, (int(CornerPositions[3][0]), int(CornerPositions[3][1])), (int(CornerPositions[2][0]), int(CornerPositions[2][1])), (255, 0, 0), 2)
        cv2.line(img, (int(CornerPositions[2][0]), int(CornerPositions[2][1])),(int(CornerPositions[1][0]), int(CornerPositions[1][1])), (255, 0, 0), 2)

        if not corners:
            pass
        else:
            for x in range(0, len(ids)):
                if (len(corners[x][0]) < 4):
                    print("No 4 corners?")
                    print(corners[x][0])
                if ids[x] in CVConstants.bot_ids:
                    idd = ids[x]
                    index = -1
                    for i in range(len(CVConstants.bot_ids)):
                        if idd == CVConstants.bot_ids[i]:
                            index = i
                            break
                    if index == -1:
                        continue
                        
                    globals.RobotState[index][0] = (corners[x][0][0][0] + corners[x][0][1][0] + corners[x][0][2][0] +
                                                    corners[x][0][3][0]) / 4
                    globals.RobotState[index][1] = (corners[x][0][0][1] + corners[x][0][1][1] + corners[x][0][2][1] +
                                                    corners[x][0][3][1]) / 4

                    cv2.line(img, (int(corners[x][0][2][0]),int (corners[x][0][2][1])), (int(corners[x][0][1][0]),int(corners[x][0][1][1])), (65, 255, 32), 2)

                    heading = getAngleBetweenPoints(int(corners[x][0][2][0]),int (corners[x][0][2][1]),int(corners[x][0][1][0]),int(corners[x][0][1][1]))
                    heading_degrees = math.degrees(heading)
                    globals.RobotState[index][2] = heading_degrees
                    cv2.putText(img, str(heading_degrees), (100, 200), font, 0.5, (0, 255, 0), 2, cv2.LINE_AA)

        gray = aruco.drawDetectedMarkers(img, corners, ids, (0, 255, 255))
        cv2.imshow('img', img)


        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    
