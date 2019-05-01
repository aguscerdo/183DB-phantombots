from environment import Environment
from tf_reinforcement import MultiAgentCNN
import numpy as np
from game import Game
import matplotlib.pyplot as plt
from tf_simulator import TfSimulator

def main():
	epochs = 15
	sim_per_epoch = 25
	game = Game()
	batch_size = 10
	steps_per_run = 30
	subsample = 5
	m = MultiAgentCNN()
	epsilon = 1
	
	ml_simulator = TfSimulator(m)
	
	
	loss_history = []
	for e in range(epochs):
		print("---- EPOCH {} ----".format(e))
		states = []
		rewards = []
		actions = []
		epsilon *= 0.9
		
		for sim in range(sim_per_epoch):
			if e % 2:
				s, r, a = game.get_simulation_history(bot=1, N=steps_per_run, subsample=subsample)
				# s = np.transpose(s, axes=(0, 2, 3, 1))
			else:
				ml_simulator.reset()
				s, r, a = ml_simulator.run_simulation(0, steps_per_run, subsample, epsilon)
			
			if s is None:
				continue
			states.append(s)
			rewards.append(r)
			actions.append(a)
		
		states = np.concatenate(states)
		rewards = np.concatenate(rewards)
		actions = np.concatenate(actions)
		
		if states.shape[1:] != (11, 11, 4):
			states = states.transpose((0, 2, 3, 1))

		loss = m.train(states, rewards, actions, save=(e % 10 == 0 and e > 0))
		print('\tLoss: {}'.format(loss))
		loss_history.append(loss)
	
	m.save()
	
	
	plt.plot(np.arange(epochs), loss_history)
	plt.title("Loss over epochs")
	plt.xlabel("epoch")
	plt.ylabel("loss")
	plt.show()
	
	
		
if __name__ == '__main__':
	main()