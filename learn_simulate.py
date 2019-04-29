from environment import Environment
from tf_reinforcement import MultiAgentCNN
import numpy as np
from game import Game



def main():
	epochs = 100
	sim_per_epoch = 100
	game = Game()
	batch_size = 10
	steps_per_run = 100
	subsample = 5
	states, rewards, actions = game.get_simulation_history(bot=1, N=steps_per_run, subsample=subsample)
	print("SHAPES: expect: ~Bx11x11x4, Bx1, Bx4")
	states = np.array(states)
	rewards = np.array(rewards)
	actions = np.array(actions)
	print(states.shape)
	print(rewards.shape)
	print(actions.shape)
	transposed_states = np.transpose(states, axes=(0,2,3,1))
	print(transposed_states.shape)
	"""for i in range(batch_size):
		trial_states, trial_rewards, trial_actions = game.get_simulation_history(bot=1, N=steps_per_run, subsample=subsample)
		states = np.concatenate((states, trial_states), axis=0)
		rewards = np.concatenate((rewards, trial_rewards), axis=0)
		actions = np.concatenate((actions, trial_actions), axis=0)
	"""
	transposed_states = np.transpose(states, axes=(0,2,3,1))
	m = MultiAgentCNN()
	m.train(transposed_states, rewards, actions, save=False)


main()