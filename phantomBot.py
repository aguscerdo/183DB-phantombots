### PHANTOMBOT CLASS
#	pos is (x,y)
#	speed is how many edges the car can traverse each time step
#	pacman is True if the car the evader, false if the car is a pursuer
# 	double_step is how often the car can move twice
#	E.g. speed = 1.2 -> double_step = 5 => every 5th timestep, car can move twice
#	current_step keeps track of what timestep we are on

class PhantomBot:
	def __init__(self, printAll=False, pos=None, pacman=False, speed=None ):
		self.printAll = printAll
		if (self.printAll):
			print("Print all mode on!")
		if (pos is None):
			self.pos = [0,0]
			if (self.printAll):
				print("Using presets!")
		else:
			self.pos = pos
		self.pacman = pacman
		if (speed is None):
			self.speed = 1.0
		else:
			self.speed = speed
		self.double_step = 0 if self.speed == 1 else int(1/(self.speed - 1))
		#start from 1 => need double_step moves before able to move twice
		self.current_step = 1
	
	def double_move(self):
		"""
		return True if car can move twice, False otherwise
		"""
		return (self.double_step != 0) and (self.current_step % self.double_step == 0)

	def move(self, pos):
		"""
		Moves to target position, updates current_step
		:param pos: position to move to, (x,y)
		"""
		self.pos = pos
		self.current_step = ( self.current_step + 1 ) % self.double_step

	def get_position(self):
		"""
		returns position
		"""
		return self.pos
	
	def is_pacman(self):
		"""
		returns True if pacman
		"""
		return self.pacman

	
		
		