from environment import Environment, PhantomBot
from baselines import baseline1 as bs1
import numpy as np

def execute_simulation(bot_pos, target_pos):
	bot_list = [
		PhantomBot(printAll=False, pos=p) for p in bot_pos
	]
	bot_list.append(PhantomBot(printAll=False, pos=target_pos, pacman=True))
	
	env = Environment(nbots=len(bot_list), bots=bot_list, map_path="maps/map.csv")
	baseline = bs1.BaseLine(env)
	baseline.run_baseline()
	history = np.array(env.history.copy())
	print(history.shape)
	
	env.animate()





if __name__ == '__main__':
	pursuers = [
		[0, 0],
		[0, 1],
		[0, 2]
	]
	target = [5, 5]
	
	execute_simulation(pursuers, target)
	
