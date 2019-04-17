import environment
import baseline1

if __name__ == '__main__':
	BS1 = baseline1.BaseLine()
	
	while not BS1.env.win_condition():
		BS1.baseline_step()
	
	BS1.env.animate()