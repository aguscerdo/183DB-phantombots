from environment import Environment, PhantomBot
from CV import ThreadedSystem
from baselines import BaseLine
import numpy as np

def execute_simulation(bot_pos, target_pos, map_name="4x4.csv"):
	bot_list = [
		PhantomBot(printAll=False, pos=p) for p in bot_pos
	]
	bot_list.append(PhantomBot(printAll=False, pos=target_pos, pacman=True))
	
	env = Environment(nbots=len(bot_list), bots=bot_list, map_path="maps/"+map_name)
	
	baseline = BaseLine(env)
	baseline.run_baseline()
	
	history = np.array(env.history.copy())
	print(history)

	n_bots = len(bot_list)
	grid_size = env.size
	return n_bots, grid_size, history

	
def physical_execution(n_bots, grid_size, instructions):
	system = ThreadedSystem(n_bots, grid_size, instructions)

	system.start_threads()
	system.join_threads()
	
	
if __name__ == '__main__':
	nbots = 4
	pursuers = [
		[0, 0],
		[0, 1],
		[0, 2]
	]
	target = [2, 2]
	
	map_f = "4x4.csv"
	
	n_bots, grid_size, instructions = execute_simulation(pursuers[:nbots-1], target, map_f)
	
	# physical_execution(n_bots, grid_size, instructions)