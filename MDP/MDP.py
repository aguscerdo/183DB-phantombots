import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt
import itertools
from environment import Environment
import time
from baselines import BaseLine1 as BaseLine

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
		self.verticeMatrix = np.zeros((self.size, self.size))

	def set_vertice_matrix(self, verts):
		"""
		verticeMatrix_i,j = 1 iff vertex at (i,j) in our maze
		"""
		self.verticeMatrix = np.zeros((self.size, self.size))
		for vertex in verts:
			self.verticeMatrix[vertex[0], vertex[1]] = 1
		
	
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
	def __init__(self, size, num_bots):
		self.env = MiniEnv(size)
		self.size = size
		self.target = (1,1)
		self.num_bots = num_bots
		self.value = np.zeros((size**(2*self.num_bots))) #state = pursuer location, target location
		# self.value[self.target[0], self.target[1]] = 100
		self.value_prev = self.value.copy()
		
		self.env.t.move_to(self.target[0], self.target[1])
		

	def linearToBots(self, index):
		bot_positions = []
		current = index
		S = self.size
		for i in range(self.num_bots):
			x = current % S
			current = current // S
			y = current % S
			current = current // S
			bot_positions.append([x,y])
		return bot_positions
		
	def botsToIndex(self, bot_positions):
		index = 0
		S = self.size
		Sn = 1
		for bot in bot_positions:
			x, y = bot
			index += x*Sn + Sn*S*y
			Sn = Sn*S*S
		return index	

	def getNextStates(self, bot_positions):
		states = []
		adjs = self.getAllAdjacent(bot_positions)
		for adj in adjs:
			states.append(self.botsToIndex(adj))
		return states

	def tsp_to_next_states(self, tsp):
		states = []
		for fixed_target_pos in tsp:
			for bot_poses in fixed_target_pos:
				states.append(self.botsToIndex(bot_poses))
		return states

	def bot_pos_list_to_next_states(self, bot_pos_list):
		states = []
		for bot_poses in fixed_target_pos:
			states.append(self.botsToIndex(bot_poses))
		return states
	
	def legal_state(self, bot_positions):
		for bot in bot_positions:
			if not self.legal_spot(bot):
				return False
		for i in range(len(bot_positions)-1):
			for j in range(i):
				if bot_positions[j][0] == bot_positions[i][0] and  bot_positions[j][1] == bot_positions[i][1]:
					return False
		return True

	def legal_spot(self, pos):
		px, py = pos
		if (0 <= px < self.size and 0 <= py < self.size):
			return (self.env.verticeMatrix[px][py] == 1)
			
	def legal_transition(self, bot_positions1, bot_positions2):
		# illegal if 
		# 1: 2 bots swap locations
		for i in range(len(bot_positions1)):
			for j in range(len(bot_positions1)):
				if i != j:
					if (bot_positions1[i][0] == bot_positions2[j][0] and  bot_positions1[i][1] == bot_positions2[j][1]):
						if (bot_positions1[j][0] == bot_positions2[i][0] and  bot_positions1[j][1] == bot_positions2[i][1]):
							return False

		# 2: 2 pursuers start/end in same location
		if not self.legal_state(bot_positions1):
			return False
		if not self.legal_state(bot_positions2):
			return False
		# 3: if game over in pos1, game  over in pos2
		if self.simple_reward(bot_positions1) == 1:
			if self.simple_reward(bot_positions2) == 0:
				return False
		return True

	def dist(self, pos1, pos2):
		return np.abs(pos1[0] - pos2[0]) + np.abs(pos1[1] - pos2[1])

	def target_move(self, bot_positions):
		move1 = None
		
		pos = bot_positions[-1]
		adjacent = self.adjacents(pos[0], pos[1])
		adj = []
		for spot in adjacent:
			if self.legal_spot(spot):
				adj.append(spot)
		listOfDistances = []
		if (len(adj) == 0):
			print("no spots!??!")
		for spot in adj:
			perSpot = []
			for i in range(len(bot_positions) - 1):
				bot = bot_positions[i]
				dists = self.dist(spot, bot)
				perSpot.append(dists)
			listOfDistances.append(perSpot)
		
		minDistances = [min(item) for item in listOfDistances]
		if len(minDistances) > 0:
			max_d = np.argmax(minDistances)
			max_d = max_d if not isinstance(max_d, np.ndarray) else max_d[0]
			move1 = adj[max_d]
		else:
			print("list empty!")
			move1 = pos
		
		return move1

	def target_seperated_positions(self, bot_positions):
		all_adjacents = []
		
		for i in range(len(bot_positions)-1):
			x,y = bot_positions[i]
			adjs = []
			adj = self.adjacents(x,y)
			for pos in adj:
				if self.legal_spot(pos):
					adjs.append(pos)
			all_adjacents.append(adjs)
		puruser_possibles = itertools.product(*all_adjacents)
		pursuer_poss_list = []
		for p in puruser_possibles:
			pursuer_poss_list.append(p)
		target = bot_positions[-1]
		tx, ty = target
		target_possibles = []
		"""
		adj = self.adjacents(tx,ty)
		for pos in adj:
			if self.legal_spot(pos):
				target_possibles.append(pos)
		"""
		target_possibles.append(self.target_move(bot_positions))
		target_seperates = []
		for pos in target_possibles:
			L = []
			for possible in pursuer_poss_list:
				add = possible
				#add.append(pos)
				add = add + (pos,)
				#print("Add is now: " + str(add))
				L.append(add)
			#print("With pos: " + str(pos))
			#print("then L = " + str(L))
			target_seperates.append( L)
		return target_seperates
						
	def adjacents(self, x, y):
		spots = [
			(x, y+1),
			(x+1, y),
			(x, y-1),
			(x-1, y),
			(x, y)
		]
		
		return spots

	def simple_reward(self, bot_positions):
		target = bot_positions[-1]
		tx, ty = target
		for i in range(len(bot_positions)-1):
			bot = bot_positions[i]
			x,y = bot
			if x == tx and y == ty:
				return 1
		return 0

	def next_state(self, bot_positions):
		#gets next_state from value and current state
		next_tsp = self.target_seperated_positions(bot_positions)
		print("next tsp:")
		print(next_tsp)
		pursuer_ql = []
		pursuer_ns = []
		for fixed_target_pos in next_tsp: # loop over target moves
			target_ql = []
			target_ns = []
			for next_bot_pos in fixed_target_pos: # loop over all pursuer moves for given target move
				# if legal transition
				if self.legal_transition(bot_positions, next_bot_pos):
					sprime = self.botsToIndex(next_bot_pos)
					r =  self.simple_reward(next_bot_pos)
					qvalue = self.value[sprime]
					target_ql.append(qvalue)
					target_ns.append(next_bot_pos)
			if len(target_ql) > 0:
				maxq, max_ns = target_ql[0], target_ns[0]
				for i in range(len(target_ql)):
					if target_ql[i] > maxq:
						maxq = target_ql[i]
						max_ns = target_ns[i]
				pursuer_ql.append(maxq)
				pursuer_ns.append(max_ns)
		if len(pursuer_ql) > 0:
			minq, min_ns = pursuer_ql[0], pursuer_ns[0]
			for i in range(len(pursuer_ql)):
				if pursuer_ql[i] < maxq:
					minq = pursuer_ql[i]
					min_ns = pursuer_ns[i]
			return min_ns
		else:
			print("no next state!?")
		return None


	def iteration(self, n, eps=0.8):
		breaker = False
		prev = 0
		tx, ty = self.target
		printed = False
		for i in range(n): #loop up to n times
			if breaker:
				break
			print("Iteration", i)
			self.value_prev = self.value.copy()
			for s in range(len(self.value)): #loop over all states
				if not s % 1000:
					print("\t- Axis", s)
				bot_positions = self.linearToBots(s)
				# if legal state:
				if self.legal_state(bot_positions):
					debug_prints = False
					if (i > self.size**(self.num_bots) and self.value[s] == 0 and not printed):
						debug_prints = True
						printed = True
						print("Curent state is: " + str(bot_positions))
						print("in theory this should not happen")
					next_tsp = self.target_seperated_positions(bot_positions)
					pursuer_ql = []
					for fixed_target_pos in next_tsp: # loop over target moves
						target_ql = []
						for next_bot_pos in fixed_target_pos: # loop over all pursuer moves for given target move
							# if legal transition
							if self.legal_transition(bot_positions, next_bot_pos):
								
								sprime = self.botsToIndex(next_bot_pos)
								r =  self.simple_reward(next_bot_pos)
								"""
								if (r > 0):
									print("s->s' for r>0: ")
									print(bot_positions)
									print(next_bot_pos)
								"""
								qvalue = self.value_prev[sprime] *eps + r
								if debug_prints:
									print("The following transition is legal and gives q: " +str(qvalue))
									print(next_bot_pos)
								target_ql.append(qvalue)
						if debug_prints:
							print("And target_ql is: " + str(target_ql))
						if len(target_ql) > 0:
							maxq = np.max(target_ql)
							pursuer_ql.append(maxq)
					if len(pursuer_ql) > 0:
						minq = np.min(pursuer_ql)
					else:
						r = self.simple_reward(bot_positions)
						minq = r
					self.value[s] = minq
			ssum = np.sum(self.value)
			if np.abs(ssum - prev) < 1e-5*len(self.value):
				breaker = True
			else:
				prev = ssum

		print("that took " + str(i) + "iterations")
	
	def plot(self, title):
		#print(self.value)
		print("These states have 0 value and are legal")
		count = 0
		count_legal = 0
		count_pos = 0
		count_val_not_reward = 0
		for i in range(len(self.value)):
			bot_poses = self.linearToBots(i)
			if self.value[i] == 0:
				count = count + 1
				if self.legal_state(bot_poses):
					count_legal += 1
					if count < 100:
						print(bot_poses)
			else:
				count_pos += 1
				if self.simple_reward(bot_poses) == 0:
					count_val_not_reward += 1

		print("Num 0-val states is: " + str(count))
		print("Num 0-val legal states is: " + str(count_legal))
		print("Num +-val states is: " + str(count_pos))
		print("Num +-val 0-reward states is: " + str(count_val_not_reward))
		#plt.imshow(self.value)
		#plt.colorbar()
		#plt.show()
		#plt.title("{}".format(title))
		# print("Target: {}, {}".format(self.env.t.x, self.env.t.y))

def value_simulation(mdp, env):
	pos = [[0,0], [0,1], [2, 2]]
	history = []
	history.append(pos)
	
	bs1 = BaseLine(env)
	
	while pos[0] != pos[-1] and pos[1] != pos[-1]:
		tpos = bs1.set_run_return(pos)
		pos = mdp.next_state(pos)
		
		pos = [[a[0], a[1]] for a in pos]
		pos = pos[:-1] + [tpos[-1]]
		history.append(pos)
		
	
	a = np.array(history).swapaxes(0, 1)
	
	return a.tolist()


def main():
	size = 5
	#size = 3
	bots = 4
	mdp = MDPSim(size, bots)
	
	verts = [[i, j] for i in range(size) for j in range(size)]
	
	print(verts)
	
	now = time.time()
	mdp.env.set_vertice_matrix(verts)
	env = Environment(3, map_path="maps/5x5.csv")

	
	mdp.iteration(100, 0.5)
	mdp.plot("Final")
	bps = [ [0,3], [0,1]]
	# print(mdp.next_state(bps))
	
	delta = time.time()-now
	print("----- TIME ------", delta)
	
	# history = value_simulation(mdp, env)
	#
	#
	# env.history = history
	#
	# env.animate()
	
	#for i in range(size):
	#	for j in range(size):
	#		print("Value matrix for i,j: " + str((i,j)))
	#		print(mdp.value[:,:,i,j])


if __name__ == '__main__':
	main()