from ML import MultiAgentCNN, TfSimulator
import numpy as np
from environment import Game
import matplotlib.pyplot as plt
from time import time

def main():
	game = Game()
	env_size = 4
	m = MultiAgentCNN("pursuers", env_size)
	# target_m = MultiAgentCNN("target")
	ml_simulator = TfSimulator(m)#, target_m)

	epochs = 100
	sim_per_epoch = 20
	steps_per_run = 25
	
	memory_size = 20000

	subsample = 2

	epsilon = 1.2
	base_cap = 1
	
	saver = 1000
	
	run_dir = '{}_{}_{}_{}'.format(time(), epochs, sim_per_epoch, steps_per_run)
	print('Saving to {}'.format(run_dir))
	#os.mkdir('animations/'+run_dir)
	
	decay = (1 - 6e-5)
	decayer = 1.

	loss_history = []
	
	memory_actions = []
	memory_states = []
	memory_rewards = []
	memory_end_states = []
	
	total_steps_performed = 0
	
	# Run epochs until 2.5M examples have been visited
	
	for radius in range(1, 4):
		for ep in range(epochs):
			decayer = 1.
			if total_steps_performed > 4000000:
				break
			states = []
			rewards = []
			actions = []
			end_states = []
			
			for sim in range(sim_per_epoch):
				# print("\tRun {}".format(sim))
				n_bots = (sim % 3 + 2) % len(ml_simulator.env.bots)
				
				# Initialize randomly target
				pos = ml_simulator.env.rand_position()
				ml_simulator.env.rand_initialise_within_radius(radius, n_bots, pos, bot_on_radius=True)
				
				decayer *= decay
				base_cap0 = base_cap * decayer
				
				if len(memory_rewards) > memory_size / 2:
					epsilon = epsilon * decay
				
				# Baseline vs Model
				#if np.random.uniform(0, 1) < :
				if np.random.uniform(0, 1) < base_cap0:
					s, r, a, e_s = game.get_simulation_history(bot=0, N=steps_per_run, subsample=subsample)
				else:
					s, r, a, e_s = ml_simulator.run_simulation(0, steps_per_run, subsample=subsample, epsilon=epsilon)

				if s is None or r is None or a is None:
					continue

				s = np.asarray(s)
				r = np.asarray(r)
				a = np.asarray(a)
				e_s = np.asarray(e_s)
					
				# Soft training
				try:
					statesTrain = np.concatenate(s, axis=0)
					rewardsTrain = np.concatenate(r, axis=0)
					actionsTrain = np.concatenate(a, axis=0)
					endStateTrain = np.concatenate(e_s, axis=0)
					
					if statesTrain.shape[1:] != (env_size, env_size, 3):
						statesTrain = statesTrain.transpose((0, 2, 3, 1))
					if endStateTrain.shape[1:] != (env_size, env_size, 3):
						endStateTrain = endStateTrain.transpose((0, 2, 3, 1))
						
					ml_simulator.model.train(statesTrain, rewardsTrain, actionsTrain, endStateTrain)
					
					# Expand memory DB
					rewards += [s]
					actions += [r]
					states += [s]
					end_states += [e_s]
				except Exception as e:
					# print("Error:", e)
					continue

			try:
				_ = np.concatenate(states, axis=0)
				_ = np.concatenate(rewards, axis=0)
				_ = np.concatenate(actions, axis=0)
			except Exception as e:
				print("Concat error:", e)
				continue
			
			n = len(rewards)
			total_steps_performed += n
			
			if len(memory_rewards) > memory_size:
				memory_rewards = memory_rewards[n*2:] + rewards
				memory_actions = memory_actions[n*2:] + actions
				memory_states = memory_states[n*2:] + states
				memory_end_states = memory_end_states[n*2:] + end_states
			else:
				memory_rewards = memory_rewards + rewards
				memory_actions = memory_actions + actions
				memory_states = memory_states + states
				memory_end_states = memory_end_states + end_states

				print("\t~ Building memory DB", len(memory_rewards))
			
			try:
				statesTrain = np.concatenate(memory_states, axis=0)
				rewardsTrain = np.concatenate(memory_rewards, axis=0)
				actionsTrain = np.concatenate(memory_actions, axis=0)
				endStateTrain = np.concatenate(memory_end_states, axis=0)
			except Exception as e:
				print("Concat error:", e)
				continue
			
			env_shape = ml_simulator.env.verticeMatrix.shape
			while statesTrain.shape[1] != env_shape[0] or statesTrain.shape[2] != env_shape[1] or statesTrain.shape[3] != 3:
				statesTrain = statesTrain.transpose((0, 2, 3, 1))
				
			while endStateTrain.shape[1] != env_shape[0] or endStateTrain.shape[2] != env_shape[1] or endStateTrain.shape[
				3] != 3:
				endStateTrain = endStateTrain.transpose((0, 2, 3, 1))

			# Hard training
			save = (total_steps_performed > saver)
			if save:
				saver += 2500
				
			print("\t- Memory Training...")
			loss = ml_simulator.model.train(statesTrain, rewardsTrain, actionsTrain, endStateTrain, save=save)
			print('\tLoss: {}'.format(loss))
			if save:
				ml_simulator.run_and_plot(run_dir, ep, radius)
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