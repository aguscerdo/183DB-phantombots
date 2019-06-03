import cv2
import numpy as np
import time
import cv2.aruco as aruco
from CV import settings
from math import *
import math

RobotState = settings.RobotState
CornerPositions = settings.CornerPositions
CornerCounter =0
cornerids = [0, 13, 19, 28]
#top right 28, top left 0, bottom left 13, bottom right, 19
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

            Tempx = corners[x][0][0][0] + corners[x][0][1][0] + corners[x][0][2][0] + corners[x][0][3][0];
            Tempx = Tempx / 4;
            Tempy = corners[x][0][0][1] + corners[x][0][1][1] + corners[x][0][2][1] + corners[x][0][3][1];
            Tempy = Tempy / 4;

            if (ids[x] == 0):
                settings.CornerPositions[0] = [Tempx, Tempy]
            else:
                if (ids[x] == 4):
                    settings.CornerPositions[1] = [Tempx, Tempy]
                else:
                    if ids[x] == 19:
                        settings.CornerPositions[2] = [Tempx, Tempy]
                    else:
                        if ids[x] == 28:
                            settings.CornerPositions[3] = [Tempx, Tempy]

    #get all vertices:
    lowest_sum = settings.CornerPositions[0][0] + settings.CornerPositions[0][1]
    highest_sum = lowest_sum
    bottom_right = settings.CornerPositions[0]
    bottom_left = settings.CornerPositions[0]
    top_right = settings.CornerPositions[0]
    top_left = settings.CornerPositions[0]
    taken = [0, 0]
    for i in range(4):
        cx, cy = settings.CornerPositions[i]
        sum = cx +cy
        if sum < lowest_sum:
            lowest_sum = sum
            bottom_right = settings.CornerPositions[i]
            taken[0] = i
        elif sum > highest_sum:
            highest_sum = sum
            top_left = settings.CornerPositions[i]
            taken[1] = i
    for i in range(4):
        if i not in taken:
            bottom_left = settings.CornerPositions[i]
            taken.append(i)
    for i in range(4):
        if i not in taken:
            top_right = settings.CornerPositions[i]
            taken.append(i)
    if bottom_left[0] > top_right[0]:
        bottom_left, top_right = top_right, bottom_left
    N = 3
    settings.Grid = np.zeros((N, N, 2))
    hx = (top_left[0] - bottom_right[0])/(N - 1)
    hy = (top_left[1] - bottom_right[1])/(N - 1)
    for i in range(N):
        for j in range(N):
            settings.Grid[i][j][0] = bottom_right[0] + hx * i
            settings.Grid[i][j][1] = bottom_right[1] + hy * j




    while (1):
        _, img = cap.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)

        font = cv2.FONT_HERSHEY_SIMPLEX

        aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_250)
        parameters = aruco.DetectorParameters_create()

        corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)





        CornerPositions = settings.CornerPositions;


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



            #TODO Make all aruco tags show up
            for  x in range(0,len(ids)):

                if (len(corners[x][0]) < 4):
                    print("No 4 corners?")
                    print(corners[x][0])
                if (ids[x]==5 or ids[x]==3 or ids[x]==6 or ids[x]==13):
                    id = ids[x]
                    if id == 13:
                        index = 0
                    elif id == 5:
                        index = 1
                    elif id == 6:
                        index = 2
                    else:
                        index = 3

                    settings.RobotState[index][0] = corners[x][0][0][0] + corners[x][0][1][0] + corners[x][0][2][0] + \
                                                    corners[x][0][3][0]
                    settings.RobotState[index][0] = settings.RobotState[index][0] / 4;
                    settings.RobotState[index][1] = corners[x][0][0][1] + corners[x][0][1][1] + corners[x][0][2][1] + \
                                                    corners[x][0][3][1]
                    settings.RobotState[index][1] = settings.RobotState[index][1] / 4;


                    #print(settings.RobotState[0])
                    #print(settings.CornerPositions)

                    cv2.line(img, (int(corners[x][0][2][0]),int (corners[x][0][2][1])), (int(corners[x][0][1][0]),int(corners[x][0][1][1])), (65, 255, 32), 2)

                    heading = getAngleBetweenPoints(int(corners[x][0][2][0]),int (corners[x][0][2][1]),int(corners[x][0][1][0]),int(corners[x][0][1][1]));
                    heading_degrees = math.degrees(heading);
                    settings.RobotState[index][2] = heading_degrees;
                    cv2.putText(img, str(heading_degrees), (100, 200), font, 0.5, (0, 255, 0), 2, cv2.LINE_AA)

                    #cv2.circle(img, (int(settings.RobotState[x][0]), int(settings.RobotState[x][1])), 20, (100, 100, 0), -1)














        gray = aruco.drawDetectedMarkers(img, corners, ids, (0, 255, 255))
        cv2.imshow('img', img)


        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    
