import threading
import time

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
		time.sleep(4)   # TODO check this number
		
		while self.loop or self.step < self.n_steps:
			i, j = self.arr[self.step][0], self.arr[self.step][1]
			time.sleep(0.5)
			self.parent.set_complete(self.botNum, 0)
			
			desired_x, desired_y = self.parent.cv.get_grid(i, j)
			
			self.step += 1
			if self.loop:
				self.step %= self.n_steps
				
			self.parent.gotoPos(desired_x, desired_y, self.botNum)
			self.parent.set_complete(self.botNum)
			
			time.sleep(0.5)
			while not self.parent.all_complete():
				time.sleep(0.5)


class Thread_A(threading.Thread):
	def __init__(self, name, parent):
		threading.Thread.__init__(self)
		self.name = name
		self.parent = parent
	
	def run(self):
		self.parent.cv.Follow()