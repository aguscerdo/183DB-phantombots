import tensorflow as  tf
import numpy as np
import keras as k
import os
import time

class MultiAgentCNN:
	def __init__(self, params=None):
		self.params = dict()
		self.set_default_params()
		self.model = k.Model()
		self.i = 0
		self.path = './weights'
		if not os.path.exists(self.path):
			os.mkdir(self.path)
			
		self.action_list = []
		
	
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
		nn = k.layers.Dropout(self.params['dropout'])(nn)
		nn = k.layers.BatchNormalization()(nn)
		# nn = k.layers.Dense(self.params['nn2'], activation='relu')(nn)
		# nn = k.layers.BatchNormalization()(nn)
		# nn = k.layers.Dropout(self.params['dropout'])(nn)
		
		return k.layers.Dense(self.params['output'], activation='softmax')(nn)

	
	def build(self):
		layer_in = k.layers.Input((11, 11, 4), (None, 11, 11, 4), sparse=False)
		actions = k.layers.Input((1,), (None, 1), dtype=tf.int32)
		
		with tf.name_scope('res1'):
			res = self.residual_layer(layer_in, self.params['cnn1'], self.params['cnn2'])
		with tf.name_scope('res2'):
			res = self.residual_layer(res, self.params['cnn3'], self.params['cnn4'])
		
		flat = k.layers.Flatten()(res)
		
		with tf.name_scope('fully_connected'):
			out = self.fully_connected(flat)
			
		reward = tf.gather(out, actions)
		
		self.model = k.Model(inputs=layer_in, outputs=[out, reward])
		
		
	def compile(self):
		if self.model is None:
			return
		
		self.model.compile(optimizer='ADAM', loss=[None, 'mse'], metrics=['accuracy'], loss_weights=[0., 1.])
	
	
	def exec(self):
		self.build()
		self.compile()
	
	
	def loss_function(self, y_pred, y_label):
		# rewards = y_pred[0:4]
		# action = y_pred[4]
		
		loss = tf.reduce_sum(tf.square(y_label - y_pred))
		return loss
	
	
	def predict(self, tensor_vals, epsilon):
		out = self.model.predict(tensor_vals)
		if np.random.uniform() < epsilon:
			return np.random.randint(0, 4)
		else:
			return np.argmax(out)
	
	
	def train(self, tensor_list, rewards, actions):
		# self.action_list = tf.cast(np.asarray(actions), tf.int32)  # list of ints [0, 4]
		
		np_list = np.asarray(tensor_list)
		np_rewards = np.asarray(rewards)
		
		history = self.model.fit(np_list, np_rewards, epochs=5)
		self.save_weights(history['loss'][-1])
		
		
	def save_weights(self, loss):
		if self.i % 25:
			return
		
		now = time.time()
		path = '{}/{}-{}.k'.format(self.path, now, loss)
		os.mkdir(path)
		
		self.model.save_weights(path, overwrite=False)
	
	
	def load_weights(self):
		ldir = [l for l in os.listdir(self.path) if l.endswith('.k')]
		ldir.sort(reverse=True)
		self.model.load_weights(ldir[0])
		
		
		
if __name__ == '__main__':
	m = MultiAgentCNN()
	m.exec()
	m.model.summary()
	
	batch_in = [
		[
			[[1, 0, 0, 0],
			 [0, 0, 0, 0],
			 [0, 0, 0, 0],
			 [0, 0, 0, 0]],
			[[1, 0, 1, 0],
			 [1, 0, 0, 0],
			 [0, 0, 0, 0],
			 [0, 0, 0, 0]],
			[[0, 0, 0, 0],
			 [0, 0, 0, 0],
			 [0, 1, 0, 0],
			 [0, 0, 0, 0]],
			[[1, 0, 0, 0],
			 [1, 0, 0, 0],
			 [1, 1, 1, 0],
			 [0, 0, 0, 0]]
		]
	]
	
	reward = [-3.4351]
	action = [1]
	
	# m.train(batch_in, reward, action)