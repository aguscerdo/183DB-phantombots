from environment import Environment
from tf_reinforcement import MultiAgentCNN
import numpy as np


def main():
	epochs = 100
	sim_per_epoch = 100
	
	env = Environment()
	batch_size = 10
	steps_per_run = 100
	subsample = 5
	states, rewards, actions = env.get_simulation_history(algorithm="bs1", bot=0, N=steps_per_run, subsample=subsample)
	print("SHAPES: expect: ~20x11x11x4, 20x1, 20x1")
	print(states.shape())
	print(rewards.shape())
	print(actions.shape())
	for i in range(batch_size):
		trial_states, trial_rewards, trial_actions = env.get_simulation_history(algorithm="bs1", bot=0, N=100, subsample=5)
		states = np.concatenate((states, trial_states), axis=0)
		rewards = np.concatenate((rewards, trial_rewards), axis=0)
		actions = np.concatenate((actions, trial_actions), axis=0)
	
main()