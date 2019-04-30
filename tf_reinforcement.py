import tensorflow as tf
import os
import numpy as np
import time


class MultiAgentCNN:
	def __init__(self):
		self.path = './weights'
		if not os.path.exists(self.path):
			os.mkdir(self.path)
			
		self.build_network()
		self.sess = tf.Session()
		self.sess.run(tf.global_variables_initializer())
	
		
	
	def build_network(self):
		self.images = tf.placeholder(tf.float32, shape=(None, 11, 11, 5), name='in_image')
		
		self.epsilon = tf.placeholder(tf.float32, (1,))
		nn = tf.layers.conv2d(inputs=self.images, filters=32,
		                        kernel_size=[3, 3], padding='same',
		                        activation='relu')
		
		# with tf.variable_scope('residual_1'):
		# 	nn = self.residual_layer(nn)
		# with tf.variable_scope('residual_2'):
		# 	nn = self.residual_layer(nn)
		
		with tf.variable_scope('inception_1'):
			nn = self.inception_layer(nn, True)
		with tf.variable_scope('inception_2'):
			nn = self.inception_layer(nn, True)
		
		with tf.variable_scope('fully_connected'):
			flat = tf.layers.flatten(nn)
			nn1 = tf.layers.Dense(64, activation='relu')(flat)
			drop1 = tf.layers.Dropout(0.2)(nn1)
			batchnorm = tf.layers.batch_normalization(drop1)
			self.predicted_reward = tf.layers.Dense(5)(batchnorm)
		
		with tf.variable_scope('exploration'):
			randy = tf.random.uniform((1, ))
			self.action = tf.cond(tf.reduce_any(tf.less(self.epsilon, randy)),
			              lambda: tf.cast(tf.random.uniform((1, ), 0, 5), dtype=tf.int64),
			              lambda: tf.argmax(self.predicted_reward))
		
		self.action_in = tf.placeholder(tf.int32, shape=(None, 1), name='action_in')
		self.reward_in = tf.placeholder(tf.float32, shape=(None, 1), name='actual_rewards')
		
		
		with tf.variable_scope('loss'):
			self.gathered_rewards = tf.gather(self.predicted_reward, self.action_in, axis=1)[:, 0, :]
			self.loss = tf.losses.mean_squared_error(self.reward_in,  self.gathered_rewards)
			#self.MSE(self.reward_in, self.gathered_rewards)
		
		self.opt = tf.train.AdamOptimizer().minimize(self.loss)
		
	
	def MSE(self, y_true, y_pred):
		return tf.reduce_mean((y_true - y_pred) ** 2, name='loss')
	
	
	def cross_entropy(self, y_true, y_pred):
		with tf.variable_scope('cross_entropy'):
			one_hot = tf.one_hot(y_true, 5)
			return tf.losses.softmax_cross_entropy(one_hot, y_pred)
	
	
	@staticmethod
	def residual_layer(layer_in):
		cnn1 = tf.layers.conv2d(inputs=layer_in, filters=32,
		                        kernel_size=[3, 3], padding='same',
		                        activation='relu')
		
		batch1 = tf.layers.batch_normalization(cnn1)
		
		cnn2 = tf.layers.conv2d(inputs=batch1, filters=32,
		                        kernel_size=[3, 3], padding='same',
		                        activation=None)
		
		concat = tf.concat([layer_in, cnn2], axis=-1)
		return tf.layers.max_pooling2d(concat, [2, 2], [2, 2])
	
	
	@staticmethod
	def __inception_layer_helper(layer_in):
		# 1x1
		cnn11 = tf.layers.conv2d(inputs=layer_in, filters=64,
	                        kernel_size=[1, 1], padding='same',
	                        activation='relu')
			
		# 2x2
		cnn12 = tf.layers.conv2d(inputs=layer_in, filters=256,
	                        kernel_size=[1, 1], padding='same',
	                        activation='relu')
		
		cnn22 = tf.layers.conv2d(inputs=cnn12, filters=256,
		                        kernel_size=[2, 2], padding='same',
		                        activation='relu')

		# 3x3
		cnn13 = tf.layers.conv2d(inputs=layer_in, filters=256,
	                        kernel_size=[1, 1], padding='same',
	                        activation='relu')
		
		cnn23 = tf.layers.conv2d(inputs=cnn13, filters=64,
		                        kernel_size=[3, 3], padding='same',
		                        activation='relu')
			
		
		# Concat
		concat = tf.concat([cnn11, cnn22, cnn23], axis=-1)
		out = tf.layers.conv2d(inputs=concat, filters=64,
		                        kernel_size=[1, 1], padding='same',
		                        activation='relu')
		
		return out
	
	
	def inception_layer(self, layer_in, residual=False):
		with tf.variable_scope('inception1'):
			nn = self.__inception_layer_helper(layer_in)
		with tf.variable_scope('inception2'):
			nn = self.__inception_layer_helper(nn)
		
		if residual:
			nn = tf.concat([layer_in, nn], axis=-1)
		
		return tf.layers.max_pooling2d(nn, [2, 2], [2, 2])
		
	
	def train(self, tensor_list, reward_list, actions_list, save=False):
		images = np.asarray(tensor_list)
		rewards = np.asarray(reward_list).reshape(-1, 1)
		actions = np.asarray(actions_list).reshape(-1, 1)
		epsilon = np.array(0).reshape((1,))

		for i in range(5):
			self.sess.run(self.opt,
			              feed_dict={
				              self.images: images,
				              self.reward_in: rewards,
				              self.action_in: actions,
				              self.epsilon: epsilon
			              })
		
		if save:
			saver = tf.train.Saver()
			path = '{}/{}'.format(self.path, time.time())
			os.mkdir(path)
			out_path = saver.save(self.sess, path + '/model.cpkt')
			print('Saved to {}'.format(out_path))
			
			writer = tf.summary.FileWriter('./summary', self.sess.graph)
			writer.flush()
		
		return self.sess.run(self.loss,
		                     feed_dict={
				              self.images: images,
				              self.reward_in: rewards,
				              self.action_in: actions,
				              self.epsilon: epsilon
			              })
		


	def predict(self, tensor_in, epsilon=0):
		tensor = np.asarray(tensor_in)
		if len(tensor.shape) == 3:
			tensor = tensor.reshape((1, -3, -2, -1))
		epsilon = np.array(epsilon).reshape((1,))
		# pl_reward = np.array([-1.])
		# pl_action = np.array([0])
		out = self.sess.run(self.action,
		              feed_dict={
			              self.images: tensor,
			              self.epsilon: epsilon
		              })
		return out
	
		
	def load(self, path=None):
		if path is None:
			ldir = [l for l in os.listdir(self.path) if l[0] != '.']
			ldir.sort(reverse=True)
			path = ldir[0]
		
		saver = tf.train.Saver()
		saver.restore(self.sess, '{}/{}/model.cpkt'.format(self.path, path))
		print("Restored model at: {}".format(path))
	
	
if __name__ == '__main__':
	pass
	
	m = MultiAgentCNN()
	
	# batch_in = [
	# 	[
	# 		[[1, 0, 0, 0],
	# 		 [0, 0, 0, 0],
	# 		 [0, 0, 0, 0],
	# 		 [0, 0, 0, 0]],
	# 		[[1, 0, 1, 0],
	# 		 [1, 0, 0, 0],
	# 		 [0, 0, 0, 0],
	# 		 [0, 0, 0, 0]],
	# 		[[0, 0, 0, 0],
	# 		 [0, 0, 0, 0],
	# 		 [0, 1, 0, 0],
	# 		 [0, 0, 0, 0]],
	# 		[[1, 0, 0, 0],
	# 		 [1, 0, 0, 0],
	# 		 [1, 1, 1, 0],
	# 		 [0, 0, 0, 0]]
	# 	]
	# ]
	
	batch_in = np.random.randint(0, 1, size=(1, 11, 11, 5))

	reward = [[-3.4351]]
	action = [1]
	
	# out = m.predict(batch_in, 0.3)
	m.train(batch_in, reward, action, save=True)
	m.load()

	