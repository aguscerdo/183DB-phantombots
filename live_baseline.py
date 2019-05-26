from environment import Environment
from phantomBot import PhantomBot
import baseline1 as bs1
import numpy as np

def main(bot_pos, target_pos):
	bot_list = [
		PhantomBot(printAll=False, pos=p) for p in (bot_pos + [target_pos])
	]
	
	env = Environment(bots=bot_list)
	baseline = bs1.BaseLine(env)
	baseline.run_baseline()
	history = np.array(env.history.copy())
	env.animate()





if __name__ == '__main__':
	pursuers = [
		[0, 0],
		[0, 5],
		[0, 10]
	]
	target = [5, 5]
	
	main(pursuers, target)
	
