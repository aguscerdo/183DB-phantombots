from environment import Environment
from tf_reinforcement import MultiAgentCNN
import numpy as np
from game import Game
import matplotlib.pyplot as plt
from tf_simulator import TfSimulator
import os
from time import time

def main():
	game = Game()
	m = MultiAgentCNN()

	epochs = 10
	sim_per_epoch = 25
	re_sim_per_epoch = 5
	steps_per_run = 50

	subsample = 1

	epsilon = 0.7
	base_cap = 0.6
	
	run_dir = '{}_{}_{}_{}'.format(time(), epochs, sim_per_epoch, steps_per_run)
	print('Saving to {}'.format(run_dir))
	os.mkdir('animations/'+run_dir)
	
	decay = (1 - 10e-5)
	decayer = 1.

	ml_simulator = TfSimulator(m)
	
	
	loss_history = []
	
	
	for radius in range(2, 10):
		decayer = 1.
		for e in range(epochs):
			print("Radius {} ---- EPOCH {} ----".format(radius, e))
			states = []
			rewards = []
			actions = []
			
			for sim in range(sim_per_epoch):
				print("\tRun {}".format(sim))
				if radius < 5:
					n_bots = sim % 4 + 1
				else:
					n_bots = sim % 2 + 3
					
				pos = [5, 5]
				
				ml_simulator.env.rand_initialise_within_radius(radius, n_bots, pos, bot_on_radius=True)
				
				for re_sim in range(re_sim_per_epoch):
					
					ml_simulator.env.back_to_start()

					decayer *= decay
					base_cap0 = base_cap * decayer
					epsilon = epsilon * decay
					randy = np.random.uniform(0, 1)
					
					if randy < base_cap0:
						s, r, a = game.get_simulation_history(bot=0, N=steps_per_run, subsample=subsample)
						# s = np.transpose(s, axes=(0, 2, 3, 1))

					else:
						# ml_simulator.reset()
						s, r, a = ml_simulator.run_simulation(0, steps_per_run, subsample=subsample, epsilon=epsilon)

					if s is None or r is None or a is None:
						continue
					
					if s is not None and len(s) > 20:
						r = r[::2]
						s = s[::2]
						a = a[::2]
						
					s = np.asarray(s)
					r = np.asarray(r)
					a = np.asarray(a)
					
					states.append(s)
					rewards.append(r)
					actions.append(a)
			try:
				states = np.concatenate(states, axis=0)
				rewards = np.concatenate(rewards, axis=0)
				actions = np.concatenate(actions, axis=0)
				
				if states.shape[1:] != (11, 11, 4):
					states = states.transpose((0, 2, 3, 1))
				
				save = (e % 3 == 0)
				print("\t- Training...")
				loss = m.train(states, rewards, actions, save=save)
				if save:
					ml_simulator.run_and_plot(run_dir, e, radius)
				
				print('\tLoss: {}'.format(loss))
				loss_history.append(loss)
			except Exception as e:
				pass

	
	m.save()
	ml_simulator.run_and_plot(run_dir, 'FINAL')
	
	plt.plot(np.arange(epochs), loss_history)
	plt.title("Loss over epochs")
	plt.xlabel("epoch")
	plt.ylabel("loss")
	plt.show()
	
	
		
if __name__ == '__main__':
	main()