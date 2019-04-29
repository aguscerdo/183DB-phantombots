import environment
import baseline1
import numpy as np
class Game:
	def __init__(self):
		self.baseline = baseline1.BaseLine()

	def rand_initialise(self):
		self.baseline.env.rand_initialise()

	def get_simulation_history(self, bot=-1, N=10, subsample=0):
		"""
		Simulate N rounds of a game with random initial conditions. return history of state, reward, action
		states are all with respect to a specific bot. If subsample != 0, takes every subsample sample.
		WLOG 
		bot = -1 -> pacman
		bot = 1 -> pursuers 
		"""
		self.rand_initialise()
		states = []
		rewards = []
		moves = [] #stores all positions bots have been, later convert to actions
		initial_positions = self.baseline.env.get_all_positions()
		if bot == -1: #PACMAN CASE
			pacman_position = initial_positions[-1]
			moves =  [pacman_position]
		else: # PURSUER CASE
			pursuer_initial_positions =  initial_positions[0:-1:1] 
			moves = [ pursuer_initial_positions ]
		state = self.baseline.env.get_state_channels(bot=bot)
		states.append( state )
		reward = self.baseline.env.immediate_reward(bot=bot, state=state)
		rewards.append(reward)
		discount_factor = 0.95 # TODO: check this
		current_discount = discount_factor
		for i in range(N):
			print("running baseline with step = " + str(i))
			if self.baseline.env.win_condition():
				break
			pursuer_moves, target_move1, target_move2 = self.baseline.baseline_step() # expected moves
			initial_positions = self.baseline.env.get_all_positions()
			real_pacman_move = initial_positions[-1]
			real_pursuer_moves =  initial_positions[0:-1:1] 
			if bot == -1: #PACMAN CASE
				moves.append(real_pacman_move)
			else: # PURSUER CASE	
				moves.append(real_pursuer_moves)
			state = self.baseline.env.get_state_channels(bot=bot)
			states.append( state )
			reward = self.baseline.env.immediate_reward(bot=bot, state=state)
			rewards.append(reward)
			print("Moved! here is positions now: ")
			if target_move2 is None:
				print("PURSUERS: " + str(real_pursuer_moves))
				print("PACMAN: " + str(real_pacman_move))
			else:
				print("PURSUERS: " + str(real_pursuer_moves))
				print("PACMAN (DOUBLE MOVED): " + str(real_pacman_move))
		rewards = self.baseline.env.immediate_reward_to_total(rewards, discount_factor)
		
		# get actions from moves:
		#print("moves to actions")
		moves = np.array(moves)
		#print("moves size: " )
		#print(moves.shape)
		actions = []
		for i in range(len(moves)-1):
			if (bot == -1): #PACMAN CASE:
				prev_pos = moves[i]
				next_pos = moves[i+1]
				action = self.baseline.env.transition_to_action(prev_pos, next_pos)
				actions.append(action)
			else: # PURSUER CASE:
				pursuer_actions = []
				#print("i is now: " + str(i))
				#print("moves i: " + str(moves[i]))
				for j in range(len(moves[i])):
					prev_pos = moves[i][j]
					next_pos = moves[i+1][j]
					action = self.baseline.env.transition_to_action(prev_pos, next_pos)
					pursuer_actions.append(action)
				actions.append(pursuer_actions)


		#actions = self.baseline.env.history_to_actions() #actions = list of actions from (i->i+1)
		states = states[:-1]  #exclude last state, since we dont have action for last state
		rewards = rewards[1:]  #exclude reward for start state, since we only want rewards on state i+1 given action i->i+1
		#TODO: maybe randomly subsample instead of every nth ?
		if subsample >= 1:
			step = int(subsample)
			states = states[::step] 
			rewards = rewards[::step] 
			actions = actions[::step] 
		# only track one bot, 
		actions = np.array(actions)
		actions = actions[:,bot]

		return states, rewards, actions