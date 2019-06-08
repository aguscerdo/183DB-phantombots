



class ThreadConstants:
		
		# IP Addresses
		ip = [
			"ws://192.168.137.238:81/ws",
			"ws://192.168.137.14:81/ws",
			"ws://192.168.137.149:81/ws",
			"ws://192.168.137.70:81/ws"
		]
		
		go_left = [
			[100, 80],
			[110, 70],
			[100, 80],
			[100, 80]
		]
		
		go_right = [
			[80, 100],
			[80, 100],
			[80, 100],
			[80, 100]
		]
		
		sleep = 0.1
		
		N_bots = len(ip)
		error = 20
		tolerance = 30
		

class CVConstants:
	corner_ids = [0, 4, 19, 28]
	# top right 28, top left 0, bottom left 13, bottom right, 19
	bot_ids = [13, 5, 6, 3]