from environment import Environment, PhantomBot
from CV import ThreadedSystem
from baselines import BaseLine
import numpy as np


def execute_simulation(bot_pos, target_pos, map_name="4x4.csv"):
	bot_list = [
		PhantomBot(printAll=False, pos=p) for p in bot_pos
	]
	bot_list.append(PhantomBot(printAll=False, pos=target_pos, pacman=True))
	
	env = Environment(nbots=len(bot_list), bots=bot_list, map_path="maps/" + map_name)
	
	baseline = BaseLine(env)
	baseline.run_baseline()
	
	history = np.array(env.history.copy())
	print(history)
	
	n_bots = len(bot_list)
	grid_size = env.size
	return n_bots, grid_size, history


def physical_execution(n_bots, grid_size, instructions):
	print("Start physical exec")
	system = ThreadedSystem(n_bots, grid_size, instructions)
	
	print("Starting thrads")
	system.start_threads()
	system.join_threads()


if __name__ == '__main__':
	print("Start")
	nbots = 4
	pursuers = [
		[0, 0],
		[0, 1],
		[0, 2]
	]
	target = [2, 2]
	
	map_f = "4x4.csv"
	
	# n_bots, grid_size, instructions = execute_simulation(pursuers[:nbots-1], target, map_f)
	
	instructions = [[[0, 0],
	                 [1, 0],
	                 [2, 0],
	                 [3, 0],
	                 [3, 1]],
	
	                [[0, 1],
	                 [1, 1],
	                 [2, 1],
	                 [2, 2],
	                 [2, 1]],
	
	                [[0, 2],
	                 [1, 2],
	                 [1, 3],
	                 [2, 3],
	                 [3, 3]],
	
	                [[2, 2],
	                 [2, 3],
	                 [3, 3],
	                 [3, 2],
	                 [3, 3]]]
	n_bots = 2
	grid_size = 4
	
	physical_execution(n_bots, grid_size, instructions[:n_bots])