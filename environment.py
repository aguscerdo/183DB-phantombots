### ENVIRONMENT CLASS
#	size is [x,y], which gives the number of vertices in our grid 
#	vertices is the set of all vertices in our maze,
# 	a vertice is defined by its x and y coordinate ([x, y])
#	We assume that all adjacent vertices connected if they are in the grid
#	bots is a list of PhantomBots in our simulation
"""
how to make something move:
use play_round. If it returns false, then your moves were illegal and nothing worked.
If there is supposed to be a double_move for pacman, input it in play_round.
Examples on how to move are below (first_motion, psuedo_rand_motion)
"""
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from phantomBot import PhantomBot
import csv
import baseline1 as bs1

import itertools


# TODO: change these later
presetSize = [11, 11]
presetVertices = []
with open('map.csv') as csvfile:
	readCSV = csv.reader(csvfile, delimiter=",")
	for row in readCSV:
		x_val = int(row[0])
		y_val = int(row[1])
		presetVertices.append([x_val,y_val])




# for i in range(presetSize[0]):
# 	for j in range(presetSize[1]):
# 		if (i !=j and (i != 6 or j > 5) and (j!=9 or i <2) ) or ((j == 6 or j == 2) and i == 6):
# 			presetVertices.append([i,j])

class Environment:
	def __init__(self, printAll=False, size=None, vertices=None, bots=None ):
		self.printAll = printAll
		if (self.printAll):
			print("Print all mode on!")
		if size is None or vertices is None or bots is None:
			self.size = presetSize
			self.vertices = presetVertices
			pursuer1 = PhantomBot(printAll=False, pos=[10,10], pacman=False)
			pursuer2 = PhantomBot(printAll=False, pos=[0,0])
			pursuer3 = PhantomBot(printAll=False, pos=[0,10])
			pursuer4 = PhantomBot(printAll=False, pos=[10,0])
			pacmanBot = PhantomBot(printAll=False, pos=[5, 5], pacman=True, speed=1.2)
			self.bots = [pursuer1, pursuer2, pursuer3, pursuer4, pacmanBot]
			if (self.printAll):
				print("Using preset size/edges/bots!")
		else:
			self.size = size
			self.vertices = vertices
			self.bots = bots
			if (self.printAll):
				print("Using grid of size " + str(self.size))

		self.verticeMatrix = np.zeros(self.size)
		self.set_vertice_matrix()
		self.occupiedVertices = []
		self.history = []
		for bot in self.bots:
			self.occupiedVertices.append(bot.get_position())
			self.history.append([bot.get_position()])
		
		

	def set_vertice_matrix(self):
		"""
		verticeMatrix_i,j = 1 iff vertex at (i,j) in our maze
		"""
		self.verticeMatrix = np.zeros(self.size)
		for vertex in self.vertices:
			self.verticeMatrix[vertex[0], vertex[1]] = 1

	def load_grid(self, size, vertices):
		"""
		Loads the grid
		:param size: size of grid, tuple of (x, y)
		:param edges: list of edges, e in edges => e = (v1, v2) and vi = (xi, yi)
		:return:
		"""
		self.size = size
		self.vertices = vertices
		self.set_vertice_matrix()
	
		if (self.printAll):
			print("Loaded new grid, size is " + str(self.size))

	def plot_grid(self, ax=None, plot_points=True):
		"""
		Plots the edges by plotting a line for each edge
		"""
		bot_positions = [bot.get_position() for bot in self.bots]
		print("bot positions: " + str(bot_positions))
		ax = plt.gca() if ax is None else ax
		ax.set_aspect('equal')
		ax.grid(True, 'both')
		ax.set_xticks(np.arange(0, self.size[0]))
		ax.set_yticks(np.arange(0, self.size[1]))

		
		if (self.printAll):
			print("Plotting Grid!")
		for i in range(self.size[0]):
			for j in range(self.size[1]):
				#plot vertex i,j
				# if (self.verticeMatrix[i,j]):
				# 	ax.plot(i, j, 'bx', label='point', alpha=0.8)
				#plot line from i,j -> i+1,j 
				if (i+1 < self.size[0] and self.verticeMatrix[i,j] and self.verticeMatrix[i+1,j]):
					xs = [i, i+1]
					ys = [j, j]
					ax.plot(xs, ys, 'k', alpha=0.8)
				#plot line from i,j -> i,j+1
				if (j+1 < self.size[1] and self.verticeMatrix[i,j] and self.verticeMatrix[i,j+1]):
					xs = [i, i]
					ys = [j, j+1]
					ax.plot(xs, ys, 'k', alpha=0.8)
		#plot bots:
		radius = 0.1
		if plot_points:
			for bot in self.bots:
				if bot.is_pacman():
					circle = plt.Circle(bot.get_position(), radius, color='r')
				else:
					circle = plt.Circle(bot.get_position(), radius, color='blue')
				ax.add_artist(circle)

		plt.title('The Maze')
		# x from -0.5 -> size_x - 0.5, y from -0.5 -> size_y - 0.5
		# -0.5 to show full grid
		plt.axis([-0.5, self.size[0]-0.5, -0.5, self.size[1]-0.5])
		plt.show()

	def legal_move_bot(self, bot, end_pos):
		"""
		Checks if move if legal given bot
		:param bot: which bot is moving, i
		:param end_pos: where a bot will end, (x1, y1)
		:return: True if move is legal else false
		"""
		start_pos = self.bots[bot].get_position()
		# True if dist == 1 and both vertices in set and no collision
		valid_move = True
		valid_move &= (self.dist(start_pos, end_pos) == 1)
		#check if points are even valid
		valid_move &= (end_pos[0] < self.size[0] and end_pos[1] < self.size[1])
		valid_move &= (end_pos[0] >= 0 and end_pos[1] >= 0)
		valid_move &= (start_pos[0] < self.size[0] and start_pos[1] < self.size[1])
		valid_move &= (start_pos[0] >= 0 and start_pos[1] >= 0)
		if valid_move == False:
			return valid_move
		valid_move &= (self.verticeMatrix[end_pos[0], end_pos[1]] == 1)
		valid_move &= (self.verticeMatrix[start_pos[0], start_pos[1]] == 1)
		# check collisions, TODO maybe change this(?)
		for i in range(len(self.bots)):
			valid_move &= (self.dist(end_pos, self.bots[i].get_position()) > 0)
		if (self.printAll):
			print("Moving from " + str(start_pos) + " to " + str(end_pos) + " is: ")
			if (valid_move):
				print("legal")
			else:
				print("illegal")
		return valid_move

	def legal_move_pos(self, start_pos, end_pos):
		"""
		Checks if move if legal given pos
		:param start_pos: start position, (x0, y0)
		:param end_pos: where a bot will end, (x1, y1)
		:return: True if move is legal else false
		"""
		# True if dist == 1 and both vertices in set and no collision
		valid_move = True
		#check if points are even valid
		valid_move &= (end_pos[0] < self.size[0] and end_pos[1] < self.size[1])
		valid_move &= (end_pos[0] >= 0 and end_pos[1] >= 0)
		valid_move &= (start_pos[0] < self.size[0] and start_pos[1] < self.size[1])
		valid_move &= (start_pos[0] >= 0 and start_pos[1] >= 0)
		if valid_move == False:
			return valid_move
		valid_move &= (self.dist(start_pos, end_pos) == 1)
		valid_move &= (self.verticeMatrix[end_pos[0], end_pos[1]] == 1)
		valid_move &= (self.verticeMatrix[start_pos[0], start_pos[1]] == 1)
		# check collisions, TODO maybe change this(?)
		for i in range(len(self.bots)):
			valid_move &= (self.dist(end_pos, self.bots[i].get_position()) > 0)
		if (self.printAll):
			print("Moving from " + str(start_pos) + " to " + str(end_pos) + " is: ")
			if (valid_move):
				print("legal")
			else:
				print("illegal")
		return valid_move

	def legal_move_all_pursuers(self, pursuer_moves):
		"""
		Takes in moves of all pursuers and returns True if no collisions AND legal
		"""
		#legal = not self.collision_pursuers(pursuer_moves)
		legal = True # Don;t check for collision !
		for i in range(len(self.bots)-1):
			legal &= self.legal_move_bot(i, pursuer_moves[i])
		return legal
	
	def legal_move_pacman(self, pacman_move):
		"""
		Takes in move of pacman and returns whether this is legal or not
		"""
		return self.legal_move_bot(-1, pacman_move)

	def legal_second_move_pacman(self, pacman_move, pacman_second_move):
		"""
		Takes in move and second move of pacman and returns whether this is legal or not
		"""
		start_pos = pacman_move
		end_pos = pacman_second_move
		valid_move = True
		#check if points are even valid
		valid_move &= (end_pos[0] < self.size[0] and end_pos[1] < self.size[1])
		valid_move &= (end_pos[0] >= 0 and end_pos[1] >= 0)
		valid_move &= (start_pos[0] < self.size[0] and start_pos[1] < self.size[1])
		valid_move &= (start_pos[0] >= 0 and start_pos[1] >= 0)
		if valid_move == False:
			return valid_move
		valid_move &= (self.dist(start_pos, end_pos) == 1)
		valid_move &= (self.verticeMatrix[end_pos[0], end_pos[1]] == 1)
		valid_move &= (self.verticeMatrix[start_pos[0], start_pos[1]] == 1)
		# check collisions, TODO maybe change this(?)
		for i in range(len(self.bots)-1):
			valid_move &= (self.dist(end_pos, self.bots[i].get_position()) > 0)
		return valid_move
	
	def collision_current_state(self, bot, end_pos):
		""" 
		Return True if bot moving to end_pos will collide with another bot
		"""
		collision = False
		for i in range(len(self.bots)-1):
			if i != bot:
				collision |= self.dist(end_pos, self.bots[i].get_position())
		return collision

	def collision_pursuers(self, pursuer_moves):
		"""
		Returns True if there is a collision in their moves, false otherwise
		:param pursuer_moves: list of all pursuer moves, [[xi, yi]]
		"""
		### check if endpoints collide
		collision = False
		hashs = []
		sz = self.size[0] * self.size[1]
		for i in range(len(pursuer_moves)):
			x,y = pursuer_moves[i]
			hashs.append(x+y*sz)
		# check dupes in hashs
		for i in range(len(hashs)):
			for j in range(i):
				collision |= (hashs[i] == hashs[j])

		### check if paths cross
		for i in range(len(hashs)):
			bot_posx, bot_posy = self.bots[i].get_position()
			bot_hash = bot_posx+bot_posy*sz
			# TODO no stay still? 
			collision |= (bot_hash in hashs)
			
		return collision

	def collision_pacman(self, pursuer_moves, pacman_move):
		"""
		Returns True if there is a collision between pacman and pursuers
		Pacman should aim for False, pursuers aim for True.
		:param pursuer_moves: list of all pursuer moves, [[xi, yi]]
		:param pacman_move: pacman's move, [xi, yi]
		"""
		### check if endpoints collide
		collision = False
		hashs = []
		sz = self.size[0] * self.size[1]
		for i in range(len(pursuer_moves)):
			x,y = pursuer_moves[i]
			hashs.append(x+y*sz)
		# check if pacman hash in hashs
		pacx, pacy = pacman_move
		pac_hash = pacx+pacy*sz
		for i in range(len(hashs)):
			collision |= (hashs[i] == pac_hash)

		### check if paths cross
		pac_posx, pac_posy = self.bots[-1].get_position()
		pac_hash = pac_posx+pac_posy*sz
		# TODO no stay still?
		collision |= (pac_hash in hashs)
		
		return collision


	def move(self, bot, end_pos):
		"""
		Moves bot to location
		:param bot: which bot is moving, i
		:param end_pos: where a bot will end, (x1, y1)
		"""
		self.bots[bot].move(end_pos)
		self.occupiedVertices[bot] = end_pos

	def get_state(self):
		"""
		Returns the state of the system
		"""
		# state[i] = position of bot i, 
		# i = -1 corresponds to pacman. 
		state = np.copy(self.occupiedVertices)
		# TODO: manipulate state if necessary
		return state

	def get_state_channels(self):
		"""
		Returns state as channels
		"""
		state = [self.verticeMatrix]
		for bot in self.bots:
			bot_state = np.zeros(self.size)
			bot_posx, bot_posy = bot.get_position()
			bot_state[bot_posx, bot_posy] = 1
			#TODO: add more to state? 
			state.append[bot_state]
		return state
		

	def adjacent(self, pos):
		"""
		Returns all adjacent spots to pos
		:param pos: tuple (x,y)
		:return: list of tuples [(xi, yi)]
		"""
		x, y = pos
		adj = [ [x+1, y], [x-1, y], [x, y+1], [x, y-1] ]
		return adj

	def update_history(self):
		"""
		Updates history given current positions
		"""
		for i in range(len(self.bots)):
			self.history[i].append(self.bots[i].get_position())

	def play_round(self, pursuer_moves, pacman_move, pacman_second_move=None):
		"""
		Plays one round, moving pursuers and pacman, if possible.
		Returns True if succesful, false if invalid
		:param pursuer_moves: list of moves for each pursure, [[xi,yi]]
		:param pacman_move: move for pacman [x, y]
		:param pacman_second_move: second move for pacman (if it can move twice) [x, y]
		:return: boolean
		"""	
		if (self.win_condition()):
			print("you've already won")
			return False
		double_move = self.bots[-1].double_move()
		if double_move and pacman_second_move is None:
			return False # pacman should move twice here 

		#check if moves legal
		legal = self.legal_move_all_pursuers(pursuer_moves)
		legal &= self.legal_move_pacman(pacman_move)
		#check if doublemove legal
		if double_move:
			legal &= self.legal_second_move_pacman(pacman_move, pacman_second_move)
		if not legal:
			return False
		#it is legal, so now we can move
		self.move(-1, pacman_move)
		for i in range(len(self.bots)-1):
			if not self.collision_current_state(i, pursuer_moves[i]):
				self.move(i, pursuer_moves[i]) # move
			else:
				self.move(i, self.bots[i].get_position()) #stay still
		self.update_history()
		#if pacman can move again, move again
		if  double_move:
			self.move(-1, pacman_second_move)
			self.update_history()
		return True

	def win_condition(self):
		"""
		return True if game is over and pursuers have won, false otherwise
		"""
		pacman = self.bots[-1]
		pacman_pos = pacman.get_position()
		adjacent_spaces = self.adjacent(pacman_pos)
		# check if no available moves
		win = True
		for space in adjacent_spaces:
			win &= (not self.legal_move_pos(pacman_pos, space))
		# check if pacman and pursuer share location
		for i in range(len(self.bots)-1):
			win |= (self.dist(self.bots[i].get_position(), pacman_pos) == 0)
		return win
		

	def dist(self, a, b):
		"""
		Gets railroad/manhattan/L1 distance
		:param a: (x0, y0)
		:param b: (x1, y1)
		:return: L1 d(a,b)
		"""
		return np.abs(a[0] - b[0]) + np.abs(a[1] - b[1])


	def animate(self):
		"""
		Animate the bot history
		:return:
		"""
		history = np.array(self.history)
		
		# Format: list containing tuples (or lists) of coordinates, where idx 0 is target, idx 1.. are hunters
		fig = plt.figure(figsize=(8,8))
		ax = fig.add_axes([0, 0, 1, 1])
		ax.set_title("0")
		self.plot_grid(ax, plot_points=False)
		# ax.set_xlim(0, self.size)
		# ax.set_ylim(0, self.size)

		scatT = ax.scatter(history[-1, 0, 0], history[-1, 0, 1], c='r')
		scatP = ax.scatter(history[-1:, 0, 0], history[-1:, 0, 1], c='b')
		psT = ax.scatter(history[-1, 0, 0], history[-1, 0, 1], c='r', alpha=0.25)
		psP = ax.scatter(history[-1:, 0, 0], history[-1:, 0, 1], c='b', alpha=0.25)
		
		def update(i):
			if i % 50 == 0:
				print("Step", i)
			if i > 0:
				psT.set_offsets(history[-1, i-1])
				psP.set_offsets(history[:-1, i-1])
			scatT.set_offsets(history[-1, i])
			scatP.set_offsets(history[:-1, i])
			ax.set_title("Step {}".format(i))
		
		anim = FuncAnimation(fig, update, frames=history.shape[1], interval=100)
		anim.save('the_movie.mp4', writer='ffmpeg')
	
	
	def first_motion(self):
		"""
		Test case, produces first move possible that is legal, given 4 bots
		"""
		pacman_moves_list = self.adjacent(self.bots[-1].get_position())
		adjacent_spots = self.adjacent(self.bots[0].get_position())
		L1 = adjacent_spots
		adjacent_spots = self.adjacent(self.bots[1].get_position())
		L2 = adjacent_spots
		adjacent_spots = self.adjacent(self.bots[2].get_position())
		L3 = adjacent_spots
		adjacent_spots = self.adjacent(self.bots[3].get_position())
		L4 = adjacent_spots
		all_pursuer_moves = itertools.product(L1, L2, L3, L4)

		# check for anything in move_list that is legal
		n = 0
		for pac_move in pacman_moves_list:
			for pursuer_moves in all_pursuer_moves:
				if self.bots[-1].double_move():
					pacman_second_move = self.bots[-1].get_position()
				else:
					pacman_second_move = None
				if self.play_round(pursuer_moves, pac_move, pacman_second_move):
					# If it's true, we played a round, return
					return True
		print(":(")
		return False
	
	
	def psuedo_rand_motion(self):
		"""
		Test, each bot does a random thing that is legal
		"""
		randmax = 1000
		curr = 0
		while curr < randmax:
			curr = curr + 1
			pursuer_moves = []
			for i in range(len(self.bots)-1):
				bot = self.bots[i]
				bot_pos = bot.get_position()
				adjacent = self.adjacent(bot_pos)
				# TODO: random with prob p "not backward"
				rand_num = np.random.randint(0, high=4)
				bot_move = adjacent[rand_num]
				pursuer_moves.append(bot_move)
			pacman = self.bots[-1]
			pacman_pos = pacman.get_position()
			adjacent = self.adjacent(pacman_pos)
			rand_num = np.random.randint(0, high=4)
			pacman_move = adjacent[rand_num]
			if pacman.double_move():
				adjacent = self.adjacent(pacman_move)
				rand_num = np.random.randint(0, high=4)
				pacman_second_move = adjacent[rand_num]
			else:
				pacman_second_move = None
			if self.play_round(pursuer_moves, pacman_move, pacman_second_move):
				return True # if we moved, then great!
		print("err :( curr > randmax")
		return False # we did not move
		
	def baseline_motion(self):
		pursuer_pos = []
		evader = self.bots[-1]
		evader_pos = evader.get_position()
		evader_second_move = None
		for i in range(0, len(self.bots)-1):
			pursuer_pos.append(self.bots[i].get_position())
		pursuer_moves = self.bs1.pursuerAlg(pursuer_pos)
		evader_move = self.bs1.evaderAlg(evader_pos)
		if evader.double_move():
			evader_second_move = self.bs1.evaderAlg((evader.get_position()))
		if self.play_round(pursuer_moves, evader_move, evader_second_move):
			return True	#we moved!
		print ("err!!")
		return False
		