import environment, numpy as np

class BaseLine2:
	def __init__(self, env=None):
		if env is not None:
			self.env = env
		else:
			self.env = environment.Environment()
	
	def target_move(self):
		
		move1, move2 = None, None
		
		target = self.env.bots[-1]
		target_pos = target.get_position()
		target_adj = [target_spot for target_spot in self.env.adjacent(target_pos) if
		              self.env.legal_move_pos(target_pos, target_spot)]
		if len(target_adj) == 0:
			move1 = target_pos
		else:
			pursuer_bots = self.env.bots[:-1]
			dist = [self.env.dist(target_pos, pursuer_bots[i].get_position()) for i in range(len(pursuer_bots))]
			min_pursuer_index = np.argmin(dist)
			min_pursuer_index = min_pursuer_index if isinstance(min_pursuer_index, np.int64) else min_pursuer_index[0]
			max_adjacent_dist = [self.env.dist(pursuer_bots[min_pursuer_index].get_position(), spot) for spot in
			                     target_adj]
			best_adjacent_spot = np.argmax(max_adjacent_dist)
			best_adjacent_spot = best_adjacent_spot if not isinstance(best_adjacent_spot, np.ndarray) else \
				best_adjacent_spot[0]
			move1 = target_adj[best_adjacent_spot]
		if target.double_move():
			target_pos = move1
			target_adj = [spot for spot in self.env.adjacent(target_pos) if self.env.legal_move_pos(target_pos, spot)]
			if len(target_adj) == 0:
				move2 = target_pos
			else:
				pursuer_bots = self.env.bots[:-1]
				dist = [self.env.dist(target_pos, pursuer_bots[i].get_position()) for i in range(len(pursuer_bots))]
				min_pursuer_index = np.argmin(dist)
				min_pursuer_index = min_pursuer_index if isinstance(min_pursuer_index, np.int64) else min_pursuer_index[
					0]
				max_adjacent_dist = [self.env.dist(pursuer_bots[min_pursuer_index].get_position(), spot) for spot in
				                     target_adj]
				best_adjacent_spot = np.argmax(max_adjacent_dist)
				best_adjacent_spot = best_adjacent_spot if not isinstance(best_adjacent_spot, np.ndarray) else \
					best_adjacent_spot[0]
				move2 = target_adj[best_adjacent_spot]
		
		return move1, move2
	
	def pursuer_move(self):
		moves = []
		target = self.env.bots[-1]
		target_pos = target.get_position()
		pursuer_bots = self.env.bots[:-1]
		target_adj = [target_spot for target_spot in self.env.adjacent(target_pos) if
		              self.env.legal_move_pos(target_pos, target_spot)]
		bot_number_tasked = []
		bot_move_dict = {}
		
		for target_spot in target_adj:
			
			d1 = [(self.env.dist(pursuer_bots[i].get_position(), target_spot)) for i in
			      [x for x in range(len(pursuer_bots)) if
			       not bot_number_tasked.__contains__(x)]]
			if len(d1) == 0:
				min_d1 = 0
			else:
				min_d1 = np.argmin(d1)
				
			try:
				min_d1 =  min_d1[0]
			except:
				pass

			bot_number_tasked.append(min_d1)
			pursuer_pos = pursuer_bots[min_d1].get_position()
			pursuer_adj = [pursuer_spot for pursuer_spot in self.env.adjacent(pursuer_pos) if
			               self.env.legal_move_pos(pursuer_pos, pursuer_spot)]
			if len(pursuer_adj) == 0:  # stay
				bot_move_dict[min_d1] = pursuer_pos
			else:
				d2 = [(self.env.dist(pursuer_spot, target_spot)) for pursuer_spot in pursuer_adj]
				min_d2 = np.argmin(d2)
				
				try:
					min_d2 = min_d2[0]
				except:
					pass
				
				bot_move_dict[min_d1] = pursuer_adj[min_d2]
		
		if len(bot_number_tasked) != len(pursuer_bots):
			
			pursuer_bots_index = [i for i in range(len(pursuer_bots))]
			remaining_bots = list(set(pursuer_bots_index) - set(bot_number_tasked))
			
			for i in remaining_bots:
				pos = self.env.bots[i].get_position()
				adj = [spot for spot in self.env.adjacent(pos) if self.env.legal_move_pos(pos, spot)]
				if len(adj) == 0:  # stay!
					bot_move_dict[i] = pos
				else:
					d = [(self.env.dist(spot, self.env.bots[-1].get_position())) for spot in adj]
					min_d = np.argmin(d)
					min_d = min_d if isinstance(min_d, np.int64) else min_d[0]
					bot_move_dict[i] = adj[min_d]
		
		for i in range(len(bot_move_dict)):
			moves.append(bot_move_dict[i])
		return moves
	
	def baseline_step(self):
		pursuer_moves = self.pursuer_move()
		target_move1, target_move2 = self.target_move()
		
		ok = self.env.play_round(pursuer_moves, target_move1, target_move2)
		# if not ok:
		#     raise ValueError("Failed to play round: {} -- {} -- {}".format(pursuer_moves, target_move1, target_move2))
		return pursuer_moves, target_move1, target_move2
	
	def baseline_moves(self):
		pursuer_moves = self.pursuer_move
		target_move1, target_move2 = self.target_move()
		return pursuer_moves, target_move1, target_move2
