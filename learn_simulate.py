from environment import Environment
from tf_reinforcement import MultiAgentCNN
import numpy as np
from game import Game
import matplotlib.pyplot as plt
from tf_simulator import TfSimulator
import os

def main():
	epochs = 1
	sim_per_epoch = 3
	game = Game()
	batch_size = 10
	steps_per_run = 50
	subsample = 4
	m = MultiAgentCNN()
	epsilon = 1
	base_cap = 0.5
	
	run_dir = '{}_{}_{}_{}'.format(np.random.randint(1000000), epochs, sim_per_epoch, steps_per_run)
	print('Saving to {}'.format(run_dir))
	os.mkdir('animations/'+run_dir)
	
	decay = 5e-5
	
	ml_simulator = TfSimulator(m)
	
	
	loss_history = []
	for e in range(epochs):
		print("---- EPOCH {} ----".format(e))
		states = []
		rewards = []
		actions = []
		
		randy = np.random.uniform(0, 1)
		
		for sim in range(sim_per_epoch):
			base_cap *= (1 - decay)
			epsilon *= (1 - decay)
			
			if randy < base_cap:
				s, r, a = game.get_simulation_history(bot=1, N=steps_per_run, subsample=subsample)
				# s = np.transpose(s, axes=(0, 2, 3, 1))
			else:
				ml_simulator.reset()
				s, r, a = ml_simulator.run_simulation(0, steps_per_run, subsample, epsilon)
				s = np.array(s)
				r = np.array(r)
				a = np.array(a)
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

		save = (e % 10 == 0 and e > 0)
		loss = m.train(states, rewards, actions, save=save)
		# if save or len(ml_simulator.env.history) > 15:
		# 	ml_simulator.env.animate()
		#
		print('\tLoss: {}'.format(loss))
		loss_history.append(loss)
	
	m.save()
	ml_simulator.run_and_plot(run_dir, 'FINAL')
	
	plt.plot(np.arange(epochs), loss_history)
	plt.title("Loss over epochs")
	plt.xlabel("epoch")
	plt.ylabel("loss")
	plt.show()
	
	
		
if __name__ == '__main__':
	main()