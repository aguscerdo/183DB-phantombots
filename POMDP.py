import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt


class Bot:
	def __init__(self):
		self.x = 0
		self.y = 0
	
	def move_to(self, x, y):
		self.x = x
		self.y = y
		


class MiniEnv:
	def __init__(self, size=3):
		self.size = size
		
		self.t = Bot()
		self.p = Bot()
		
	
	def random_position(self, target=False):
		x, y = np.random.randint(0, self.size, 2)
		if target:
			self.t.move_to(x, y)
		else:
			self.p.move_to(x, y)
	
	def reward(self, x, y):
		if self.t.x == x and self.t.y == y:
			return 100
		elif not (0 <= x < self.size) or not (0 <= y < self.size):
			return None
		else:
			return -1
	

class MDPSim:
	def __init__(self, size):
		self.env = MiniEnv(size)
		self.size = size
		self.value = np.zeros((size, size))
		self.target = (size - 1, size // 2)
		
		# self.value[self.target[0], self.target[1]] = 100
		self.value_prev = self.value.copy()
		
		self.env.t.move_to(self.target[0], self.target[1])
		

	def adjacents(self, x, y):
		spots = [
			(x, y+1),
			(x+1, y),
			(x, y-1),
			(x-1, y)
		]
		
		return spots
		

	def iteration(self, n, eps=0.8):
		breaker = False
		prev = 0
		
		for i in range(n):
			if breaker:
				break
			print("Iteration", i)
			if i % 5 == 0:
				self.print(i)
			self.value_prev = self.value.copy()
			for x in range(self.size):
				for y in range(self.size):
					value = 0
					ql = []
					for xy in self.adjacents(x, y):
						if not (0 <= xy[0] < self.size) or not (0 <= xy[1] < self.size):
							continue
						qvalue = self.value_prev[xy[0], xy[1]] * eps + self.env.reward(xy[0], xy[1])
						ql.append(qvalue)
					
					self.value[x, y] = np.max(ql)
					if x == self.target[0] and y == self.target[1]:
						ssum = np.sum(self.value)
						if np.abs(ssum - prev) < 1e-5:
							breaker = True
						else:
							prev = ssum
					
	
	def print(self, title):
		plt.imshow(self.value)
		plt.colorbar()
		plt.show()
		plt.title("{}".format(title))
		# print("Target: {}, {}".format(self.env.t.x, self.env.t.y))

def main():
	
	mdp = MDPSim(100)
	
	mdp.iteration(1000)
	mdp.print("Final")


if __name__ == '__main__':
	main()