from ML import MultiAgentCNN, TfSimulator
import numpy as np
from environment import Game
import matplotlib.pyplot as plt
import os
from time import time

def main():
	game = Game()
	env_size = 4
	m = MultiAgentCNN("pursuers", env_size)
	# target_m = MultiAgentCNN("target")
	ml_simulator = TfSimulator(4, m)#, target_m)
	
	eps_per_radius = 50
	sim_per_epoch = 25
	steps_per_run = 15
	radius_top = 25
	
	memory_size = 10000
	
	subsample = 2
	epsilon = 1.
	base_cap = 0.0
	
	save_top = 2500
	total_steps_performed = 0
	
	run_dir = '{}_{}_{}'.format(time(), sim_per_epoch, steps_per_run)
	print('Saving to {}'.format(run_dir))
	os.mkdir('animations/'+run_dir)

	decay = (1 - 5e-5)
	
	loss_history = []
	
	memory_actions = []
	memory_states = []
	memory_rewards = []
	memory_end_states = []
	
	for radius in range(1, radius_top):
		for ep in range(eps_per_radius):
			print("EPOCH {} ---- Radius {}".format(ep, radius))
			
			states = []
			rewards = []
			actions = []
			end_states = []
			
			for sim in range(sim_per_epoch):
				n_bots = (sim % (len(ml_simulator.env.bots)-1) + 1)
				pos = ml_simulator.env.rand_position()
				ml_simulator.env.rand_initialise_within_radius(radius, n_bots, pos, bot_on_radius=True)
				
				base_cap *= decay
				if len(memory_rewards) > memory_size * 0.9:
					epsilon *= decay
				
				if np.random.uniform(0, 1) < base_cap:
					s, r, a, e_s = game.get_simulation_history(bot=0, N=steps_per_run,subsample=0)
				else:
					s, r, a, e_s = ml_simulator.run_simulation(0, steps_per_run, subsample=subsample, epsilon=epsilon)
					
				if s is None or r is None or a is None:
					continue
				
				s = np.asarray(s)
				r = np.asarray(r)
				a = np.asarray(a)
				e_s = np.asarray(e_s)
				
				if s.shape[1:] != (env_size, env_size, 3):
					s = s.transpose((0, 2, 3, 1))
				if e_s.shape[1:] != (env_size, env_size, 3):
					e_s = e_s.transpose((0, 2, 3, 1))
				
				states.append(s)
				rewards.append(r)
				actions.append(a)
				end_states.append(e_s)
			
			# Soft train
			try:
				s_train = np.concatenate(states, axis=0)
				r_train = np.concatenate(rewards, axis=0)
				a_train = np.concatenate(actions, axis=0)
				e_s_train = np.concatenate(end_states, axis=0)
			except Exception as e:
				print("Soft", e)
				continue
			ml_simulator.model.train(s_train, r_train, a_train, e_s_train)
			
			
			n = len(r_train)
			total_steps_performed += n

			if len(memory_rewards) > memory_size:
				memory_rewards = memory_rewards[n * 2:] + rewards
				memory_actions = memory_actions[n * 2:] + actions
				memory_states = memory_states[n * 2:] + states
				memory_end_states = memory_end_states[n * 2:] + end_states
			else:
				memory_rewards = memory_rewards + rewards
				memory_actions = memory_actions + actions
				memory_states = memory_states + states
				memory_end_states = memory_end_states + end_states
				
				print("\t~ Building memory DB", len(memory_rewards))


		# Hard Training
		try:
			statesTrain = np.concatenate(memory_states, axis=0)
			rewardsTrain = np.concatenate(memory_rewards, axis=0)
			actionsTrain = np.concatenate(memory_actions, axis=0)
			endStateTrain = np.concatenate(memory_end_states, axis=0)
		except Exception as e:
			print("Concat error:", e)
			continue
			
		env_shape = ml_simulator.env.verticeMatrix.shape
		while statesTrain.shape[1] != env_shape[0] or statesTrain.shape[2] != env_shape[1] or statesTrain.shape[
			3] != 3:
			statesTrain = statesTrain.transpose((0, 2, 3, 1))
		
		while endStateTrain.shape[1] != env_shape[0] or endStateTrain.shape[2] != env_shape[1] or \
				endStateTrain.shape[
					3] != 3:
			endStateTrain = endStateTrain.transpose((0, 2, 3, 1))
			
		
		save = (total_steps_performed > save_top)
		print("\t- Memory Training...")
		loss = ml_simulator.model.train(statesTrain, rewardsTrain, actionsTrain, endStateTrain, save=save)
		print('\tLoss: {}'.format(loss))
		loss_history.append(loss)

		if save:
			save_top += 2500
			plot_history(loss_history)
		
		if save:
			ml_simulator.run_and_plot(run_dir, radius, radius)
	
	m.save()
	ml_simulator.run_and_plot(run_dir, 'FINAL')
	
	plot_history(loss_history)


def plot_history(loss_history):
	plt.plot(np.arange(len(loss_history)), loss_history)
	plt.title("Loss over epochs")
	plt.xlabel("epoch")
	plt.ylabel("loss")
	plt.show()

if __name__ == '__main__':
	main()