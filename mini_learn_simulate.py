from environment import Environment
from tf_reinforcement import MultiAgentCNN
import numpy as np
from game import Game
import matplotlib.pyplot as plt
from tf_simulator import TfSimulator
import os
from time import time


def main():
	game = Game()
	m = MultiAgentCNN("pursuers")
	ml_simulator = TfSimulator(m)