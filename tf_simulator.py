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
	
	
	def reset(self, test_mode=False):
		self.env.rand_initialise(test_mode)
	
	
	def run_simulation(self, bot, N=50, subsample=5, epsilon=0, test_mode=False):
		states = []
		rewards = []
		actions = []
		
		self.reset()    # TODO allow for restart on point
		
		bot_states = np.array([self.env.get_state_channels(bb) for bb in [0, 1, 2, 3, -1]])
		
		states.append(bot_states[bot])
		instant_rewards = self.env.immediate_reward(bot, states[-1])
		rewards.append(instant_rewards)
		
		for i in range(N):
			if self.env.win_condition():
				break
			_, target_move1, target_move2 = self.baseline.baseline_moves()

			predicted_movements = []
			
			if np.random.uniform() < epsilon:
				for bb in range(len(self.env.bots)-1):
					moves = self.env.adjacent(self.env.bots[bb].get_position())
					legal_moves = np.array([moves for idx, m in enumerate(moves)
					                        if self.env.legal_move_bot(bb, m)])
					rand_move = np.random.choice(legal_moves, 1)
					predicted_movements.append(rand_move)
			else:
				if bot_states.shape[1:] != (11, 11, 4):
					bot_states = np.transpose(bot_states, axes=(0, 2, 3, 1))
				predicted_reward = self.model.predict(bot_states)
				
				for bb in range(len(self.env.bots)-1):
					moves = self.env.adjacent(self.env.bots[bb].get_position())
					legal_moves = np.array([[predicted_reward[bb][idx], m] for idx, m in enumerate(moves)
					                        if self.env.legal_move_bot(bb, m)])
					max_move = legal_moves[np.argmax(legal_moves[:, 0])][1]
					predicted_movements.append(max_move)
			
			action_to_do = predicted_movements[bot]
			action_to_do = action_to_do[0] if isinstance(action_to_do, np.ndarray) else action_to_do
			actions.append(action_to_do)
			
			next_bot_state = [self.env.action_to_transition(predicted_movements[b], self.env.bots[b].get_position())
			              for b in [0, 1, 2, 3]]
			
			ok, bot_crashes = self.env.play_round(next_bot_state, target_move1, target_move2)
			# check if bot crashed, if it did then we give -reward, else give whatever it was supposed to get
			if bot_crashes[bot]:
				rewards.append(-200)
			else:
				rewards.append(self.env.immediate_reward(bot))
			states.append(self.env.get_state_channels(bot))
		
		rewards = self.env.immediate_reward_to_total(rewards, 0.992)
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
		self.reset(True)
		self.run_simulation(0, 250)
		self.env.animate(dir, epoch)

# if __name__ == '__main__':
#
# 	runner = TfSimulator()