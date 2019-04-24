import keras as k
from environment import Environment
from cnn_reinforcement import MultiAgentCNN



def main():
	epochs = 100
	sim_per_epoch = 100
	
	net_p = MultiAgentCNN()
	net_t = MultiAgentCNN()
	
	net_p.build()
	net_t.build()
	