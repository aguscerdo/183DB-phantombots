from tf_reinforcement import MultiAgentCNN
from environment import Environment
import numpy as np
from baseline1 import BaseLine


class TfSimulator:
	def __init__(self, model):
		self.model = model
		self.env = Environment()
		self.reset()
		self.baseline = BaseLine()
		self.baseline.env = self.env
	
	
	def reset(self):
		self.env.rand_initialise()
	
	
	def run_simulation(self, bot, N=50, subsample=5, epsilon=0):
		states = []
		rewards = []
		actions = []
		
		bot_states = np.array([self.env.get_state_channels(bb) for bb in [0, 1, 2, 3, -1]])
		
		states.append(bot_states[bot])
		instant_rewards = self.env.immediate_reward(bot, states[-1])
		rewards.append(instant_rewards)
		
		for i in range(N):
			if self.env.win_condition():
				break
			
			_, target_move1, target_move2 = self.baseline.baseline_moves()
			
			if bot_states.shape[1:] != (11, 11, 4):
				bot_states = np.transpose(bot_states, axes=(0, 2, 3, 1))
			predicted_movements = self.model.predict(bot_states, epsilon)
			action_to_do = predicted_movements[bot]
			action_to_do = action_to_do[0] if isinstance(action_to_do, np.ndarray) else action_to_do
			actions.append(action_to_do)
			
			next_bot_state = [self.env.action_to_transition(predicted_movements[b], self.env.bots[b].get_position())
			              for b in [0, 1, 2, 3]]
			
			ok, bot_crashes = self.env.play_round_no_checks(next_bot_state, target_move1, target_move2)
			# check if bot crashed, if it did then we give -reward, else give whatever it was supposed to get
			if bot_crashes[bot]:
				rewards.append(-100)
			else:
				rewards.append(self.env.immediate_reward(bot))
			states.append(self.env.get_state_channels(bot))
		
		rewards = self.env.immediate_reward_to_total(rewards, 0.95)
		states = states[:-1]
		rewards = rewards[1:]
		
		if subsample > 0:
			step = int(subsample)
			states = states[::step]
			rewards = rewards[::step]
			actions = actions[::step]
		# only track one bot,
		if len(actions) == 0:
			return None, None, None
		
		return states, rewards, actions


	def run_and_plot(self, dir, epoch):
		self.run_simulation(0, 250)
		self.env.animate(dir, epoch)

# if __name__ == '__main__':
#
# 	runner = TfSimulator()