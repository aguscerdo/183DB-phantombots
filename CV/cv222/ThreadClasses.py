import threading
import time
import math
from math import atan2, pi

class Thread_B(threading.Thread):
	def __init__(self, name, botNum, N, parent, instructions, loop=False):
		threading.Thread.__init__(self)
		self.name = name
		self.botNum = botNum
		
		self.step = 0
		self.N = N
		
		self.parent = parent
		self.arr = instructions
		self.n_steps = len(self.arr[0])
		
		self.loop = loop
	
	
	def run(self):
		time.sleep(1)   # TODO check this number
		
		while self.loop or self.step < self.n_steps:
			i, j = self.arr[self.botNum][self.step][0], self.arr[self.botNum][self.step][1]
			self.parent.set_complete(self.botNum, 0)
			
			desired_x, desired_y = self.parent.cv.get_grid(i, j)
			
			self.step += 1
			if self.loop:
				self.step %= self.n_steps
				
			self.gotoPos(desired_x, desired_y, self.botNum)
			self.parent.set_complete(self.botNum)
			
			time.sleep(0.5)
			while not self.parent.all_complete():
				time.sleep(0.5)
	
	
	def goleft(self, idx, diff=40):
		sleep_amount = self.parent.constants.sleep
		if diff > 40:
			sleep_amount /= 2
		
		if idx >= self.parent.constants.N_bots:
			raise RuntimeError("Bot number {} has no ip address".format(idx))
		
		speed = self.parent.constants.go_left[idx]
		bot = self.parent.get_bot(idx)
		
		bot.send_motion('~', speed[0], speed[1])
		time.sleep(sleep_amount)
		bot.send_motion('~', 90, 90)
	
	
	def goright(self, idx, diff=40):
		sleep_amount = self.parent.constants.sleep
		if diff > 40:
			sleep_amount /= 2
		
		if idx >= self.parent.constants.N_bots:
			raise RuntimeError("Bot number {} has no ip address".format(idx))
		
		speed = self.parent.constants.go_right[idx]
		bot = self.parent.get_bot(idx)
		
		bot.send_motion('~', speed[0], speed[1])
		time.sleep(sleep_amount)
		bot.send_motion('~', 90, 90)
	
	
	def goforward(self, idx, diff=40):
		sleep_amount = self.parent.constants.sleep
		if diff > 40:
			sleep_amount /= 2
		
		if idx >= self.parent.constants.N_bots:
			raise RuntimeError("Bot number {} has no ip address".format(idx))
		
		bot = self.parent.get_bot(idx)
		
		bot.send_motion('#', 'F', 0)
		time.sleep(sleep_amount)
		bot.send_motion('~', 90, 90)
	
	
	def gotoPos(self, x, y, botNum):
		sleep_amount = self.parent.constants.sleep
		error = self.parent.constants.error
		tolerance = self.parent.constants.tolerance
		
		actual_x, actual_y, actual_h = self.parent.cv.get_state(botNum)
		print(actual_x, x)
		dist_diff = self.dist([actual_x, actual_y], [x, y])
		
		while dist_diff > tolerance:
			time.sleep(sleep_amount)
			actual_x, actual_y, actual_h = self.parent.cv.get_state(botNum)
			
			desired_h = self.parent.getAngleBetweenPoints(actual_x, actual_y, x, y)
			difference = 180 - abs(abs(desired_h - actual_h) - 180)
			
			while difference > error:
				print("HEADING ADJ", botNum, actual_h, desired_h)
				actual_x, actual_y, actual_h = self.parent.cv.get_state(botNum)
				time.sleep(sleep_amount)
				
				if actual_h < desired_h:
					print("H ADJ", actual_h, desired_h)
					if desired_h - actual_h > 180:
						print("go left, bot:" + str(botNum))
						self.goleft(botNum, difference)
					else:
						print("go right, bot:" + str(botNum))
						self.goright(botNum, difference)
				else:
					if actual_h - desired_h > 180:
						print("go right, bot:" + str(botNum))
						self.goright(botNum, difference)
					else:
						print("go left, bot:" + str(botNum))
						self.goleft(botNum, difference)
				
				difference = 180 - abs(abs(desired_h - actual_h) - 180)
			
			dist_diff = self.dist([actual_x, actual_y], [x, y])
			self.goforward(botNum, dist_diff)
			
			actual_x, actual_y, actual_h = self.parent.cv.get_state(botNum)
			
			print(actual_x, actual_y, '--', x, y)
			dist_diff = self.dist([actual_x, actual_y], [x, y])
		print("Location Reached, YAY!")
		return
	
	
	@staticmethod
	def angle_trunc(a):
		while a < 0.0:
			a += pi * 2
		return a
	
	def getAngleBetweenPoints(self, x_orig, y_orig, x_landmark, y_landmark):
		deltaY = y_landmark - y_orig
		deltaX = x_landmark - x_orig
		return math.degrees(self.angle_trunc(atan2(deltaY, deltaX)))
	
	@staticmethod
	def dist(start, end):
		sx, sy = start
		ex, ey = end
		return ((sx - ex) ** 2 + (ey - sy) ** 2) ** 0.5


class Thread_A(threading.Thread):
	def __init__(self, name, parent):
		threading.Thread.__init__(self)
		self.name = name
		self.parent = parent
	
	def run(self):
		self.parent.cv.Follow()