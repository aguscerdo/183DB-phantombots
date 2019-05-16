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
	ml_simulator = TfSimulator(m)

	epochs = 100
	sim_per_epoch = 25
	re_sim_per_epoch = 5
	steps_per_run = 50

	subsample = 2

	epsilon = 1.
	base_cap = 0.4
	
	run_dir = '{}_{}_{}_{}'.format(time(), epochs, sim_per_epoch, steps_per_run)
	print('Saving to {}'.format(run_dir))
	os.mkdir('animations/'+run_dir)
	
	decay = (1 - 5e-5)
	decayer = 1.

	loss_history = []
	
	memory_actions = []
	memory_states = []
	memory_rewards = []
	
	total_steps_performed = 0
	
	for e in range(epochs*10):
		decayer = 1.
		if total_steps_performed > 2500000:
			break
		for radius in range(3, 10):
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
				
				pos = [5,5]
				ml_simulator.env.rand_initialise_within_radius(radius, n_bots, pos, bot_on_radius=True)
				
				for re_sim in range(re_sim_per_epoch):
					
					ml_simulator.env.back_to_start()

					decayer *= decay
					base_cap0 = base_cap * decayer
					if len(memory_rewards) > 40000:
						epsilon = epsilon * decay
					randy = np.random.uniform(0, 1)
					
					if randy < base_cap0:
						s, r, a = game.get_simulation_history(bot=0, N=steps_per_run, subsample=subsample)

					else:
						s, r, a = ml_simulator.run_simulation(0, steps_per_run, subsample=subsample, epsilon=epsilon)

					if s is None or r is None or a is None:
						continue
						
					s = np.asarray(s)
					r = np.asarray(r)
					a = np.asarray(a)
					
					states.append(s)
					rewards.append(r)
					actions.append(a)
				try:
					statesC = np.concatenate(states, axis=0)
					rewardsC = np.concatenate(rewards, axis=0)
					actionsC = np.concatenate(actions, axis=0)
					if statesC.shape[1:] != (11, 11, 4):
						statesC = statesC.transpose((0, 2, 3, 1))
					ml_simulator.model.train(statesC, rewardsC, actionsC)
				except:
					pass
			
			try:
				_ = np.concatenate(states, axis=0)
				_ = np.concatenate(rewards, axis=0)
				_ = np.concatenate(actions, axis=0)
				
				n = len(rewards)
				total_steps_performed += n
				if len(memory_rewards) > 50000:
					memory_rewards = memory_rewards[n*2:] + rewards
					memory_actions = memory_actions[n*2:] + actions
					memory_states = memory_states[n*2:] + states
				else:
					memory_rewards = memory_rewards + rewards
					memory_actions = memory_actions + actions
					memory_states = memory_states + states
			except Exception as e:
				pass
			
			try:
				statesC = np.concatenate(memory_states, axis=0)
				rewardsC = np.concatenate(memory_rewards, axis=0)
				actionsC = np.concatenate(memory_actions, axis=0)
				
				if statesC.shape[1:] != (11, 11, 4):
					statesC = statesC.transpose((0, 2, 3, 1))
				
				save = (e % 10 == 0)
				print("\t- Training...")
				loss = ml_simulator.model.train(statesC, rewardsC, actionsC, save=save)
				if save:
					ml_simulator.run_and_plot(run_dir, e, radius)
				print('\tLoss: {}'.format(loss))
				loss_history.append(loss)
			except:
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