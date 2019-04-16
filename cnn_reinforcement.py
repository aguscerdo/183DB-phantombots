import tensorflow as  tf
import numpy as np
import keras as k

class MultiAgentCNN:
	def __init__(self, params):
		self.params = dict()
		self.set_default_params()
	
	
	def set_default_params(self):
		self.params = {
			'N': 64,
			'cnn1': (3, 3, 32),
			'cnn2': (3, 3, 32),
			'cnn3': (3, 3, 32),
			'cnn4': (3, 3, 32),
			'cnn5': (3, 3, 32),
			'cnn6': (3, 3, 32),
		}
	
	
	
	def residual_layer(self, layer_in, layer1, layer2):
		c1 = k.layers.Conv2D(layer1[2], (layer1[0], layer1[1]), padding='SAME', activation='relu')(layer_in)
		b1 = k.layers.BatchNormalization()(c1)
		c2 = k.layers.Conv2D(layer2[2], (layer2[0], layer2[1]), padding='SAME',)(b1)
		
		concat = k.layers.Concatenate([layer_in, c2])
		out = k.layers.MaxPooling2D()(concat)
		
		return out
	
		