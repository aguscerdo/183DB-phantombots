import environment
import baseline1

if __name__ == '__main__':
	BS1 = baseline1.BaseLine()
	
	i = 0
	while not BS1.env.win_condition():
		BS1.baseline_step()
		if i % 25 == 0:
			BS1.env.plot_grid()
		i += 1