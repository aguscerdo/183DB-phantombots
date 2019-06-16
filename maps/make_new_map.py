import csv
import os

def make_map(n):
	pos = [[i, j] for i in range(n) for j in range(n)]
	
	file_name = '{0}x{0}.csv'.format(n)
	
	with open(file_name, 'w') as file:
		for t in pos:
			file.write("{},{}\n".format(t[0], t[1]))
	
	return file_name


if __name__ == '__main__':
	n = 6
	make_map(n)