import cv2
import numpy as np
import time
import cv2.aruco as aruco
from math import *
import math
from CV.wrapped.config import CVConstants



class CVSystem:
	def __init__(self, nbots, grid_size):
		self.const = CVConstants()
		self.nbots = nbots
		
		self.grid_size = grid_size
		self.grid = np.zeros((grid_size, grid_size, 2))
		
		self.states = [[0,0,0] for i in range(nbots)]

		self.corners = [[0,0] for i in range(4)]
		self.corner_ids = self.const.corner_ids
		self.corner_counter = 0

		self.font = cv2.FONT_HERSHEY_SIMPLEX
	
		
	def Follow(self):
		cap = cv2.VideoCapture(0)

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
				Tempx /= 4
				Tempy = corners[x][0][0][1] + corners[x][0][1][1] + corners[x][0][2][1] + corners[x][0][3][1]
				Tempy /=  4
				
				if ids[x] == self.corner_ids[0]:
					self.corners[0] = [Tempx, Tempy]
				elif ids[x] == self.corner_ids[1]:
					self.corners[1] = [Tempx, Tempy]
				elif ids[x] == self.corner_ids[2]:
					self.corners[2] = [Tempx, Tempy]
				elif ids[x] == self.corner_ids[3]:
					self.corners[3] = [Tempx, Tempy]
		
		# get all vertices:
		lowest_sum = self.corners[0][0] + self.corners[0][1]
		highest_sum = lowest_sum
		
		bottom_right = self.corners[0]
		bottom_left = self.corners[0]
		top_right = self.corners[0]
		top_left = self.corners[0]
		
		taken = [0, 0]
		for i in range(4):
			cx, cy = self.corners[i]
			pos_sum = cx + cy
			if pos_sum < lowest_sum:
				lowest_sum = pos_sum
				bottom_right = self.corners[i]
				taken[0] = i
			elif pos_sum > highest_sum:
				highest_sum = pos_sum
				top_left = self.corners[i]
				taken[1] = i
				
		for i in range(4):
			if i not in taken:
				bottom_left = self.corners[i]
				taken.append(i)
		for i in range(4):
			if i not in taken:
				top_right = self.corners[i]
				taken.append(i)
				
		if bottom_left[0] > top_right[0]:
			bottom_left, top_right = top_right, bottom_left
			
		N = self.grid_size
		
		hx = (top_left[0] - bottom_right[0]) / (N - 1)
		hy = (top_left[1] - bottom_right[1]) / (N - 1)
		for i in range(N):
			for j in range(N):
				self.grid[i][j][0] = bottom_right[0] + hx * i
				self.grid[i][j][1] = bottom_right[1] + hy * j
		
		while True:
			_, img = cap.read()
			gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
			edges = cv2.Canny(gray, 50, 150, apertureSize=3)
			
			font = cv2.FONT_HERSHEY_SIMPLEX
			
			aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_250)
			parameters = aruco.DetectorParameters_create()
			
			corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
			
			CornerPositions = self.corners
			
			cv2.circle(img, (int(CornerPositions[0][0]), int(CornerPositions[0][1])), 20, (0, 255, 0), -1)
			cv2.circle(img, (int(CornerPositions[1][0]), int(CornerPositions[1][1])), 20, (0, 255, 0), -1)
			cv2.circle(img, (int(CornerPositions[2][0]), int(CornerPositions[2][1])), 20, (0, 250, 0), -1)
			cv2.circle(img, (int(CornerPositions[3][0]), int(CornerPositions[3][1])), 20, (0, 0, 255), -1)
			
			cv2.line(img, (int(CornerPositions[0][0]), int(CornerPositions[0][1])),
			         (int(CornerPositions[1][0]), int(CornerPositions[1][1])), (255, 0, 0), 2)
			cv2.line(img, (int(CornerPositions[0][0]), int(CornerPositions[0][1])),
			         (int(CornerPositions[3][0]), int(CornerPositions[3][1])), (255, 0, 0), 2)
			cv2.line(img, (int(CornerPositions[3][0]), int(CornerPositions[3][1])),
			         (int(CornerPositions[2][0]), int(CornerPositions[2][1])), (255, 0, 0), 2)
			cv2.line(img, (int(CornerPositions[2][0]), int(CornerPositions[2][1])),
			         (int(CornerPositions[1][0]), int(CornerPositions[1][1])), (255, 0, 0), 2)
			
		
			if corners:
				# TODO Make all aruco tags show up
				for x in range(0, len(ids)):
					if len(corners[x][0]) < 4:
						print("No 4 corners?")
						print(corners[x][0])
						
					if ids[x] in self.const.bot_ids:
						bid = ids[x]
						index = -1
						for i, rid in enumerate(self.const.bot_ids):
							if rid == bid:
								index = i
								break
							
							
						x0 = (corners[x][0][0][0] + corners[x][0][1][0] +
						                         corners[x][0][2][0] + corners[x][0][3][0]) / 4
						
						y0 = (corners[x][0][0][1] + corners[x][0][1][1] +
						                         corners[x][0][2][1] + corners[x][0][3][1]) / 4
						
						cv2.line(img,
						         (int(corners[x][0][2][0]), int(corners[x][0][2][1])),
						         (int(corners[x][0][1][0]), int(corners[x][0][1][1])),
						         (65, 255, 32),
						         2)
						
						heading = CVSystem.getAngleBetweenPoints(int(corners[x][0][2][0]),
						                                         int(corners[x][0][2][1]),
						                                         int(corners[x][0][1][0]),
						                                         int(corners[x][0][1][1]))
												
						h0 = math.degrees(heading)
						self.states[index][0] = x0
						self.states[index][1] = y0
						self.states[index][2] = h0

						
						cv2.putText(img, str(h0), (100, 200), font, 0.5, (0, 255, 0), 2, cv2.LINE_AA)
						
			gray = aruco.drawDetectedMarkers(img, corners, ids, (0, 255, 255))
			cv2.imshow('img', img)
			
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break
		cap.release()
		cv2.destroyAllWindows()
	
	@staticmethod
	def angle_trunc(a):
		while a < 0.0:
			a += pi * 2
		return a

	@staticmethod
	def getAngleBetweenPoints(x_orig, y_orig, x_landmark, y_landmark):
		deltaY = y_landmark - y_orig
		deltaX = x_landmark - x_orig
		return CVSystem.angle_trunc(atan2(deltaY, deltaX))

	
	def get_state(self, idx):
		return self.states[idx]
	
	def get_grid(self, i, j):
		return self.grid[i][j][0], self.grid[i][j][1]