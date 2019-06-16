import numpy as np
import environment


class BaseLine3:
	def __init__(self, env=None):
		if env is not None:
			self.env = env
		else:
			self.env = environment.Environment()
			
			
	def target_move(self):
		move1, move2 = None, None
		target = self.env.bots[-1]
		target_pos = target.get_position()
		target_adj = [target_spot for target_spot in self.env.adjacent(target_pos) if self.env.legal_move_pos(target_pos, target_spot)]
		rand_num = np.random.randint(1, 4)
		if rand_num <= 2:
			pursuer_bots = self.env.bots[:-1]
			if len(target_adj) == 0:
				move1 = target_pos
			else:
				dist = [self.env.dist(target_pos, pursuer_bots[i].get_position()) for i in range(len(pursuer_bots))]
				min_pursuer_index = np.argmin(dist)
				min_pursuer_index = min_pursuer_index if isinstance(min_pursuer_index, np.int64) else min_pursuer_index[0]
				max_adjacent_dist = [self.env.dist(pursuer_bots[min_pursuer_index].get_position(), spot) for spot in target_adj]
				best_adjacent_spot = np.argmax(max_adjacent_dist)
				best_adjacent_spot = best_adjacent_spot if not isinstance(best_adjacent_spot, np.ndarray) else best_adjacent_spot[0]
				move1 = target_adj[best_adjacent_spot]
		else:
			x = len(target_adj)
			rand_adj = np.random.randint(0, x)
			if len(target_adj) == 0:
				move1 = target_pos
			else:
				move1 = target_adj[rand_adj]
		
		if target.double_move():
			target_pos = move1
			target_adj = [target_spot for target_spot in self.env.adjacent(target_pos) if self.env.legal_move_pos(target_pos, target_spot)]
			x = len(target_adj)
			rand_adj = np.random.randint(0, x)
			if len(target_adj) == 0:
				move2 = target_pos
			else:
				move2 = target_adj[rand_adj]
		
		return move1, move2
	
	
	def pursuer_move(self):
		moves = []
		pursuer_bots = self.env.bots[:-1]
		target = self.env.bots[-1]
		target_pos = target.get_position()
		for i in range(len(pursuer_bots)):
			rand_num = np.random.randint(1, 4)
			pursuer_pos = pursuer_bots[i].get_position()
			pursuer_adj = [pursuer_spot for pursuer_spot in self.env.adjacent(pursuer_pos) if self.env.legal_move_pos(pursuer_pos, pursuer_spot)]
			if rand_num <= 1:
				if len(pursuer_adj) == 0:
					moves.append(pursuer_pos)
				else:
					dist = [self.env.dist(target_pos, spot) for spot in pursuer_adj]
					min_dist = np.argmin(dist)
					min_dist = min_dist if isinstance(min_dist, np.int64) else min_dist[0]
					moves.append(pursuer_adj[min_dist])
			
			else:
				x = len(pursuer_adj)
				rand_adj = np.random.randint(0, x)
				if len(pursuer_adj) == 0:
					moves.append(pursuer_pos)
				else:
					moves.append(pursuer_adj[rand_adj])
		return moves
	
	def baseline_step(self):
		pursuer_moves = self.pursuer_move
		target_move1, target_move2 = self.target_move()
		
		ok = self.env.play_round(pursuer_moves, target_move1, target_move2)
		# if not ok:
		#     raise ValueError("Failed to play round: {} -- {} -- {}".format(pursuer_moves, target_move1, target_move2))
		return pursuer_moves, target_move1, target_move2
	
	def baseline_moves(self):
		pursuer_moves = self.pursuer_move
		target_move1, target_move2 = self.target_move()
		return pursuer_moves, target_move1, target_move2
