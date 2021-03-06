from ws4py.client.threadedclient import WebSocketClient
import socket
import time

class SocketWrapper:
	def __init__(self, IP):
		sock = socket.gethostbyname(socket.gethostname())

		# self.addr = "ws://{}:81/ws".format(sock)
		print('Connecting...')
		self.addr = IP
		self.socket = WebSocketClient(self.addr)

		self.socket.connect()
		print('Socket connected:', IP)


	def send_motion(self,ID ,arg1,arg2 ):
		if ID == "~":
			ID = 126
		elif ID == "#":
			ID = 35

		if arg1 == "F":
			arg1 = 70

		payload = [ID, arg1,arg2]
		payload = bytearray(payload)

		self.socket.send(bytearray(payload), True)

	def close(self):
		self.close()
