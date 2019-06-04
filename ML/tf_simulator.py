from environment import Environment
import numpy as np
from baselines import BaseLine


class TfSimulator:
	def __init__(self, nbots, model, target_model=None):
		self.model = model
		self.target_model = target_model
		self.env = Environment(nbots=nbots)
		self.reset()
		self.baseline = BaseLine()
		self.baseline.env = self.env
	
	
	def reset(self, test_mode=False):
		self.env.rand_initialise(test_mode)
	
	
	def run_simulation(self, bot, N=50, subsample=5, epsilon=0, test_mode=False):
		states = []
		rewards = []
		actions = []

		bot_states = np.array([self.env.get_state_channels(bb) for bb in range(len(self.env.bots))])
		states.append(bot_states[bot])

		instant_reward = self.env.immediate_reward(bot, states[-1])
		rewards.append(instant_reward)

		for i in range(N):
			if self.env.win_condition():
				break
			_, target_move1, target_move2 = self.baseline.baseline_moves()
			
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
				predicted_value = self.model.predict(bot_states)
				
				for bb in range(len(self.env.bots)-1):
					moves = self.env.adjacent(self.env.bots[bb].get_position())
					
					legal_moves = []
					for idx, m in enumerate(moves):
						if self.env.legal_move_bot(bb, m) and idx < 4:
							legal_moves.append([predicted_value[bb][idx], idx])
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
			# check if bot crashed, if it did then we give -value, else give whatever it was supposed to get
			if bot_crashes[bot]:
				rewards.append(-200)
			else:
				rewards.append(self.env.immediate_reward(bot))

			states.append(self.env.get_state_channels(bot))
		
		# This is because we dont want first state , or value for last state
		rewards = rewards[1:]
		end_states = states[1:]
		states = states[:-1]
		
		if subsample > 0:
			step = int(subsample)
			states = states[::step] + states[-1]
			rewards = rewards[::step] + rewards[-1]
			actions = actions[::step] + actions[-1]
			end_states = end_states[::step] + end_states[-1]
		# only track one bot,
		if len(actions) == 0:
			return None, None, None, None
		
		return states, rewards, actions, end_states


	def run_and_plot(self, dir, epoch, radius=5):
		self.env.rand_initialise_within_radius(radius, 3, [0, 0])
		self.run_simulation(0, 30)
		self.env.animate(dir, epoch, radius)
		print("Animating...")

# if __name__ == '__main__':
#
# 	runner = TfSimulator()