import time
import math
from math import atan2, pi
from CV.socket_wrapper import SocketWrapper
from CV.wrapped.config import ThreadConstants

from CV.wrapped.CVSystem import CVSystem
from CV.wrapped.ThreadClasses import Thread_A, Thread_B


class ThreadedSystem:
	def __init__(self, nbots, grid_size, instructions):
		self.constants = ThreadConstants()
		
		self.bots = self.make_bots(nbots)
		self.bot_threads = self.make_bot_threads(nbots, grid_size)
		self.completed = [0 for _ in range(nbots)]
		
		self.cv = CVSystem(nbots, grid_size)
		self.cv_thread = Thread_A("cv", self)
	
		if len(instructions) != nbots:
			raise ValueError("Instructions need to be of shape: (nbots, k, 2)")
		self.instructions = instructions
		

	def make_bots(self, nbots):
		return [
			SocketWrapper(self.constants.ip[i]) for i in range(nbots)
		]
	
	def make_bot_threads(self, nbots, grid_size):
		return [
			Thread_B("bot_{}".format(i), i, grid_size, self) for i in range(nbots)
		]
	
	def start_threads(self):
		self.cv_thread.start()
		for thread in self.bot_threads:
			thread.start()
	
	
	def join_threads(self):
		self.cv_thread.join()
		for thread in self.bot_threads:
			thread.join()
	
	# --- State --- #
	def set_complete(self, idx, to=1):
		self.completed[idx] = to
	
	def reset_complete(self):
		for i in range(len(self.completed)):
			self.completed[i] = 0
	
	def all_complete(self):
		return 0 not in self.completed
	
	
	# ---- Movement Functions ---- #
	def goleft(self, idx, diff=40):
		sleep_amount = self.constants.sleep
		if diff > 40:
			sleep_amount /= 2
		
		sleep_amount /= 4
		
		if idx >= self.constants.N_bots:
			raise RuntimeError("Bot number {} has no ip address".format(idx))
		
		speed = self.constants.go_left[idx]
		bot  = self.bots[idx]
		
		bot.send_motion('~', speed[0], speed[1])
		time.sleep(sleep_amount)
		bot.send_motion('~', 90, 90)
	
	
	def goright(self, idx, diff=40):
		sleep_amount = self.constants.sleep
		if diff > 40:
			sleep_amount /= 2
		
		sleep_amount /= 4
		
		if idx >= self.constants.N_bots:
			raise RuntimeError("Bot number {} has no ip address".format(idx))
		
		speed = self.constants.go_right[idx]
		bot = self.bots[idx]
		
		bot.send_motion('~', speed[0], speed[1])
		time.sleep(sleep_amount)
		bot.send_motion('~', 90, 90)
	
	
	def goforward(self, idx, diff=40):
		sleep_amount = self.constants.sleep
		if diff > 40:
			sleep_amount /= 2
		
		sleep_amount /= 4
		
		if idx >= self.constants.N_bots:
			raise RuntimeError("Bot number {} has no ip address".format(idx))
		
		bot = self.bots[idx]
		
		bot.send_motion('#', 'F', 0)
		time.sleep(sleep_amount)
		bot.send_motion('~', 90, 90)
		
		
	def gotoPos(self, x, y, botNum):
		sleep_amount = self.constants.sleep
		error = self.constants.error
		tolerance = self.constants.tolerance
		
		actual_x, actual_y, actual_h = self.cv.get_state(botNum)
		dist_diff = self.dist([actual_x, actual_y], [x, y])
		
		while dist_diff > tolerance:
			time.sleep(sleep_amount)
			actual_x, actual_y, actual_h = self.cv.get_state(botNum)
			
			desired_h = self.getAngleBetweenPoints(actual_x, actual_y, x, y)
			difference = 180 - abs(abs(desired_h - actual_h) - 180)
			
			while difference > error:
				actual_x, actual_y, actual_h = self.cv.get_state(botNum)
				time.sleep(sleep_amount)
				
				delta = abs(desired_h - actual_h)
				if delta > 180:
					self.goleft(botNum, difference)
				else:
					self.goright(botNum, difference)
				difference = 180 - abs(delta - 180)
				
				
			dist_diff = self.dist([actual_x, actual_y], [x, y])
			self.goforward(botNum, dist_diff)
			
			actual_x, actual_y, actual_h = self.cv.get_state(botNum)
			
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
		return  math.degrees(self.angle_trunc(atan2(deltaY, deltaX)))
	
	@staticmethod
	def dist(start, end):
		sx, sy = start
		ex, ey = end
		return ((sx - ex) ** 2 + (ey - sy) ** 2) ** 0.5
		