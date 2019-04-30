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
	m = MultiAgentCNN()
	epsilon = 1
	for e in range(epochs):
		print("---- EPOCH {} ----".format(e))
		states = []
		rewards = []
		actions = []
		for sim in range(sim_per_epoch):
			
			s, r, a = game.get_simulation_history(bot=1, N=steps_per_run, subsample=subsample)
			if s is None:
				continue
				
			s0 = np.transpose(s, axes=(0, 2, 3, 1))
			states.append(s0)
			rewards.append(r)
			actions.append(a)
		
		states = np.concatenate(states)
		rewards = np.concatenate(rewards)
		actions = np.concatenate(actions)
		
		loss = m.train(states, rewards, actions, save=(e % 10 == 0))
		print('\tLoss: {}'.format(loss))
		
		
if __name__ == '__main__':
	main()