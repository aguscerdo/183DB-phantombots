import tensorflow as  tf
import numpy as np
import keras as k

class MultiAgentCNN:
	def __init__(self, params=None):
		self.params = dict()
		self.set_default_params()
		self.model = k.Model()
	
	def set_default_params(self):
		self.params = {
			'N': 64,
			'cnn1': (3, 3, 32),
			'cnn2': (3, 3, 32),
			'cnn3': (3, 3, 32),
			'cnn4': (3, 3, 32),
			'cnn5': (3, 3, 32),
			'cnn6': (3, 3, 32),
			'dropout': 0.3,
			'nn1': 128,
			'nn2': 64,
			'output': 4
		}
	
	
	
	def residual_layer(self, layer_in, layer1, layer2):
		c1 = k.layers.Conv2D(layer1[2], (layer1[0], layer1[1]), padding='SAME', activation='relu')(layer_in)
		b1 = k.layers.BatchNormalization()(c1)
		c2 = k.layers.Conv2D(layer2[2], (layer2[0], layer2[1]), padding='SAME',)(b1)
		
		concat = k.layers.Concatenate()([layer_in, c2])
		out = k.layers.MaxPooling2D()(concat)
		
		return out
	
	
	def fully_connected(self, layer_in):
		nn = k.layers.Dense(self.params['nn1'], activation='relu')(layer_in)
		nn = k.layers.BatchNormalization()(nn)
		nn = k.layers.Dropout(self.params['dropout'])(nn)
		nn = k.layers.Dense(self.params['nn2'], activation='relu')(nn)
		nn = k.layers.BatchNormalization()(nn)
		nn = k.layers.Dropout(self.params['dropout'])(nn)
		
		return k.layers.Dense(self.params['output'], activation='softmax')(nn)

	
	def build(self):
		layer_in = k.layers.Input((10, 10, 4), (None, 10, 10, 4), sparse=False)
		res = self.residual_layer(layer_in, self.params['cnn1'], self.params['cnn2'])
		res = self.residual_layer(res, self.params['cnn3'], self.params['cnn4'])
		
		flat = k.layers.Flatten()(res)
		out = self.fully_connected(flat)
		
		self.model = k.Model(inputs=layer_in, outputs=out)
		
		
	def compile(self):
		if self.model is None:
			return
		
		self.model.compile('ADAM')
	
	

if __name__ == '__main__':
	m = MultiAgentCNN()
	m.build()
	# m.compile()
	m.model.summary()