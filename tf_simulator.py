from tf_reinforcement import MultiAgentCNN
from environment import Environment
import numpy as np
from baseline1 import BaseLine


class TfSimulator:
	def __init__(self, model, target_model):
		self.model = model
		self.target_model = target_model
		self.env = Environment()
		self.reset()
		self.baseline = BaseLine()
		self.baseline.env = self.env
	
	
	def reset(self, test_mode=False):
		self.env.rand_initialise(test_mode)
	
	
	def run_simulation(self, bot, N=50, subsample=5, epsilon=0, test_mode=False):
		states = []
		rewards = []
		actions = []
		target_states = []
		target_rewards = []
		target_actions = []
		bot_states = np.array([self.env.get_state_channels(bb) for bb in range(len(self.env.bots))])
		
		states.append(bot_states[bot])
		target_states.append(bot_states[-1])

		instant_rewards = self.env.immediate_reward(bot, states[-1])
		rewards.append(instant_rewards)
		target_instant_rewards = self.env.immediate_reward(-1, states[-1])
		rewards.append(target_instant_rewards)

		for i in range(N):
			if self.env.win_condition():
				break
			#_, target_move1, target_move2 = self.baseline.baseline_moves()
			target_predicted_move1 = []
			target_predicted_move2 = None
			# Exploration target
			if np.random.uniform() < epsilon:
				moves = self.env.adjacent(self.env.bots[-1].get_position())
				legal_moves = np.array([idx for idx, m in enumerate(moves)
										if self.env.legal_move_bot(-1, m)])
				ss_rand = np.arange(legal_moves.shape[0])
				np.random.shuffle(ss_rand)
				
				rand_move = legal_moves[ss_rand[0]]
				target_predicted_move1 = (int(rand_move))
			# Exploitation target
			else:
				#if bot_states.shape[1:] != (11, 11, 3):
				#	bot_states = np.transpose(bot_states, axes=(0, 2, 3, 1))
				predicted_reward = self.target_model.predict(target_states[-1])
				moves = self.env.adjacent(self.env.bots[-1].get_position())
				legal_moves = []
				for idx, m in enumerate(moves):
					if self.env.legal_move_bot(-1, m) and idx < 4:
						legal_moves.append([predicted_reward[-1][idx], idx])
					else:
						pass
				legal_moves = np.array(legal_moves)
				if len(legal_moves) == 0:
					max_move = 4
				else:
					max_move = legal_moves[np.argmax(legal_moves[:, 0])][1]
				target_predicted_move1 = (int(max_move))
			target_actions.append(target_predicted_move1)
			target_move1 = self.env.action_to_transition(target_predicted_move1, self.env.bots[-1].get_position())
			target_move2 = None
			if self.env.bots[-1].double_move():
				pacpos = self.env.bots[-1].get_position()
				self_state, ally_state, enemy_state = self.env.get_state_channels(-1)
				self_state[pacpos[0], pacpos[1]] = 0
				self_state[target_move1[0], target_move1[1]] = 1
				target_new_state = [self_state, self_state, enemy_state]
				target_states.append(target_new_state)

				# Exploration target
				if np.random.uniform() < epsilon:
					moves = self.env.adjacent(target_move1)
					legal_moves = np.array([idx for idx, m in enumerate(moves)
											if self.env.legal_move_bot(-1, m)])
					ss_rand = np.arange(legal_moves.shape[0])
					np.random.shuffle(ss_rand)
					
					rand_move = legal_moves[ss_rand[0]]
					target_predicted_move2 = (int(rand_move))
				# Exploitation target
				else:
					#if bot_states.shape[1:] != (11, 11, 3):
					#	bot_states = np.transpose(bot_states, axes=(0, 2, 3, 1))
					predicted_reward = self.target_model.predict(target_states[-1])
					
					moves = self.env.adjacent(target_move1)
					
					legal_moves = []
					for idx, m in enumerate(moves):
						if self.env.legal_move_bot(-1, m) and idx < 4:
							legal_moves.append([predicted_reward[-1][idx], idx])
						else:
							pass
					legal_moves = np.array(legal_moves)
					if len(legal_moves) == 0:
						max_move = 4
					else:
						max_move = legal_moves[np.argmax(legal_moves[:, 0])][1]
					target_predicted_move2 = (int(max_move))
				target_actions.append(target_predicted_move2)
				target_instant_rewards = self.env.immediate_reward(-1, target_new_state)
				target_rewards.append(target_instant_rewards)
				target_move2 =  self.env.action_to_transition(target_predicted_move2, target_move1)

			predicted_movements = []
			# Exploration pursuer
			if np.random.uniform() < epsilon:
				for bb in range(len(self.env.bots)-1):
					moves = self.env.adjacent(self.env.bots[bb].get_position())
					legal_moves = np.array([idx for idx, m in enumerate(moves)
					                        if self.env.legal_move_bot(bb, m)])
					ss_rand = np.arange(legal_moves.shape[0])
					np.random.shuffle(ss_rand)
					
					rand_move = legal_moves[ss_rand[0]]
					predicted_movements.append(int(rand_move))
			# Exploitation pursuer
			else:
				if bot_states.shape[1:] != (11, 11, 3):
					bot_states = np.transpose(bot_states, axes=(0, 2, 3, 1))
				predicted_reward = self.model.predict(bot_states)
				
				for bb in range(len(self.env.bots)-1):
					moves = self.env.adjacent(self.env.bots[bb].get_position())
					
					legal_moves = []
					for idx, m in enumerate(moves):
						if self.env.legal_move_bot(bb, m) and idx < 4:
							legal_moves.append([predicted_reward[bb][idx], idx])
						else:
							pass
					legal_moves = np.array(legal_moves)
					if len(legal_moves) == 0:
						max_move = 4
					else:
						max_move = legal_moves[np.argmax(legal_moves[:, 0])][1]
					predicted_movements.append(int(max_move))
			
			action_to_do = predicted_movements[bot]
			action_to_do = action_to_do[0] if isinstance(action_to_do, np.ndarray) else action_to_do
			actions.append(action_to_do)
			
			
			next_bot_state = [self.env.action_to_transition(predicted_movements[b], self.env.bots[b].get_position())
			              for b in range(len(self.env.bots) - 1)]
			
			
			ok, bot_crashes = self.env.play_round(next_bot_state, target_move1, target_move2)
			# check if bot crashed, if it did then we give -reward, else give whatever it was supposed to get
			if bot_crashes[bot]:
				rewards.append(-200)
			else:
				rewards.append(self.env.immediate_reward(bot))

			if bot_crashes[-1]:
				target_rewards.append(-200)
			else:
				target_rewards.append(self.env.immediate_reward(bot))
			states.append(self.env.get_state_channels(bot))
			target_states.append(self.env.get_state_channels(-1))
		
		# This is because we dont want first state , or reward for last state
		rewards = self.env.immediate_reward_to_total(rewards, 0.8)
		states = states[:-1]
		rewards = rewards[1:]
		target_rewards = self.env.immediate_reward_to_total(target_rewards, 0.8)
		target_states = target_states[:-1]
		target_rewards = target_rewards[1:]
		
		if subsample > 0:
			step = int(subsample)
			states = states[::step]
			rewards = rewards[::step]
			actions = actions[::step]
			target_states = target_states[::step]
			target_rewards = target_rewards[::step]
			target_actions = target_actions[::step]
		# only track one bot,
		if len(actions) == 0:
			return None, None, None, None, None, None
		
		return states, rewards, actions, target_states, target_rewards, target_actions


	def run_and_plot(self, dir, epoch, radius=5):
		self.env.rand_initialise_within_radius(radius, 3, [5, 5])
		self.run_simulation(0, 30)
		self.env.animate(dir, epoch, radius)
		print("Animating...")

# if __name__ == '__main__':
#
# 	runner = TfSimulator()