from baselines import baseline1

if __name__ == '__main__':
	BS1 = baseline1.BaseLine(nbots=3)
	# BS1.set_run_return([[0,0], [0,1], [2,2]])
	BS1.run_baseline()
	i = 0
	while not BS1.env.win_condition():
		BS1.baseline_step()
		if i % 25 == 0:
			BS1.env.plot_grid()
		i += 1
	BS1.env.animate()