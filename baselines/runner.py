class BaseLineRunner:
	"""
	This class is used to generate a simulation history through baselines
	"""
	
	def __init__(self, bs):
		self.bs = bs
	
	def run_baseline(self, rand=False):
		i = 0
		if rand:
			self.bs.env.rand_initialise()
		while not self.bs.env.win_condition():
			self.bs.baseline_step()
			if i % 25 == 0:
				self.bs.env.plot_grid()
			i += 1
	
	def set_run_return(self, bot_pos):
		for i, b in enumerate(bot_pos):
			self.bs.env.bots[i].move((b[0], b[1]))
		
		pm, tm1, tm2 = self.bs.baseline_moves()
		
		return pm + [tm1]
		
		move1, move2 = None, None
		
		target = self.bs.env.bots[-1]
		target_pos = target.get_position()
		target_adj = [target_spot for target_spot in self.bs.env.adjacent(target_pos) if
		              self.bs.env.legal_move_pos(target_pos, target_spot)]
		if len(target_adj) == 0:
			move1 = target_pos
		else:
			pursuer_bots = self.bs.env.bots[:-1]
			dist = [self.bs.env.dist(target_pos, pursuer_bots[i].get_position()) for i in range(len(pursuer_bots))]
			min_pursuer_index = np.argmin(dist)
			min_pursuer_index = min_pursuer_index if isinstance(min_pursuer_index, np.int64) else min_pursuer_index[0]
			max_adjacent_dist = [self.bs.env.dist(pursuer_bots[min_pursuer_index].get_position(), spot) for spot in
			                     target_adj]
			best_adjacent_spot = np.argmax(max_adjacent_dist)
			best_adjacent_spot = best_adjacent_spot if not isinstance(best_adjacent_spot, np.ndarray) else \
				best_adjacent_spot[0]
			move1 = target_adj[best_adjacent_spot]
		if target.double_move():
			target_pos = move1
			target_adj = [spot for spot in self.bs.env.adjacent(target_pos) if
			              self.bs.env.legal_move_pos(target_pos, spot)]
			if len(target_adj) == 0:
				move2 = target_pos
			else:
				pursuer_bots = self.bs.env.bots[:-1]
				dist = [self.bs.env.dist(target_pos, pursuer_bots[i].get_position()) for i in range(len(pursuer_bots))]
				min_pursuer_index = np.argmin(dist)
				min_pursuer_index = min_pursuer_index if isinstance(min_pursuer_index, np.int64) else min_pursuer_index[
					0]
				max_adjacent_dist = [self.bs.env.dist(pursuer_bots[min_pursuer_index].get_position(), spot) for spot in
				                     target_adj]
				best_adjacent_spot = np.argmax(max_adjacent_dist)
				best_adjacent_spot = best_adjacent_spot if not isinstance(best_adjacent_spot, np.ndarray) else \
					best_adjacent_spot[0]
				move2 = target_adj[best_adjacent_spot]
		
		return move1, move2
