import time
import math
from math import atan2, pi
from CV.socket_wrapper import SocketWrapper
from CV.wrapped.config import ThreadConstants

from CV.wrapped.CVSystem import CVSystem
from CV.wrapped.ThreadClasses import Thread_A, Thread_B


class ThreadedSystem:
	def __init__(self, nbots, grid_size, instructions):
		self.instructions = instructions

		self.constants = ThreadConstants()
		
		self.bots = self.make_bots(nbots)
		self.bot_threads = self.make_bot_threads(nbots, grid_size)
		self.completed = [0 for _ in range(nbots)]
		
		self.cv = CVSystem(nbots, grid_size)
		self.cv_thread = Thread_A("cv", self)
	
		if len(instructions) != nbots:
			raise ValueError("Instructions need to be of shape: (nbots, k, 2)")


	def make_bots(self, nbots):
		print("INIT")
		ret = []

		for i in range(nbots):
			print("Socket", self.constants.ip[i])
			s = SocketWrapper(self.constants.ip[i])
			ret.append(s)

		return ret
	
	def make_bot_threads(self, nbots, grid_size):
		return [
			Thread_B("bot_{}".format(i), i, grid_size, self, self.instructions) for i in range(nbots)
		]
	
	def start_threads(self):
		self.cv_thread.start()
		for thread in self.bot_threads:
			print("Starting", thread.getName())
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
	
	def get_bot(self, idx):
		return self.bots[idx]
	
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
	
	"""
	# ---- Movement Functions ---- #
	def goleft(self, idx, diff=40):
		sleep_amount = self.constants.sleep
		if diff > 40:
			sleep_amount /= 2
		
		if idx >= self.constants.N_bots:
			raise RuntimeError("Bot number {} has no ip address".format(idx))
		
		speed = self.constants.go_left[idx]
		bot = self.bots[idx]
		
		bot.send_motion('~', speed[0], speed[1])
		time.sleep(sleep_amount)
		bot.send_motion('~', 90, 90)
	
	def goright(self, idx, diff=40):
		sleep_amount = self.constants.sleep
		if diff > 40:
			sleep_amount /= 2
		
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
		print(actual_x, x)
		dist_diff = self.dist([actual_x, actual_y], [x, y])
		
		while dist_diff > tolerance:
			time.sleep(sleep_amount)
			actual_x, actual_y, actual_h = self.cv.get_state(botNum)
			
			desired_h = self.getAngleBetweenPoints(actual_x, actual_y, x, y)
			difference = 180 - abs(abs(desired_h - actual_h) - 180)
			
			while difference > error:
				print("HEADING ADJ", botNum, actual_h, desired_h)
				actual_x, actual_y, actual_h = self.cv.get_state(botNum)
				time.sleep(sleep_amount)
				
				if (actual_h < desired_h):
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
			
			actual_x, actual_y, actual_h = self.cv.get_state(botNum)
			
			print(actual_x, actual_y, '--', x, y)
			dist_diff = self.dist([actual_x, actual_y], [x, y])
		
		print("Location Reached, YAY!")
		return
	"""
