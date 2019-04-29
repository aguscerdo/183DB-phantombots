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
		self.images = tf.placeholder(tf.float32, shape=(None, 11, 11, 4), name='in_image')
		
		self.epsilon = tf.placeholder(tf.float32, (1,))
		cnn0 = tf.layers.conv2d(inputs=self.images, filters=32,
		                        kernel_size=[3, 3], padding='same',
		                        activation='relu')
		
		with tf.variable_scope('residual_1'):
			res1 = self.residual_layer(cnn0)
		with tf.variable_scope('residual_2'):
			res2 = self.residual_layer(res1)
			
		
		with tf.variable_scope('fully_connected'):
			flat = tf.layers.flatten(res2)
			nn1 = tf.layers.Dense(64, activation='relu')(flat)
			drop1 = tf.layers.Dropout(0.2)(nn1)
			batchnorm = tf.layers.batch_normalization(drop1)
			self.predicted_reward = tf.layers.Dense(4)(batchnorm)
		
		with tf.variable_scope('exploration'):
			randy = tf.random.uniform((1, ))
			self.action = tf.cond(tf.reduce_any(tf.less(self.epsilon, randy)),
			              lambda: tf.cast(tf.random.uniform((1, ), 0, 4), dtype=tf.int64),
			              lambda: tf.argmax(self.predicted_reward))
		
		self.action_in = tf.placeholder(tf.int32, shape=(None, 1), name='action_in')
		self.reward_in = tf.placeholder(tf.float32, shape=(None, 1), name='actual_rewards')
		
		self.gathered_rewards = tf.gather(self.predicted_reward, self.action_in, axis=1)
		
		self.loss = tf.reduce_sum((self.gathered_rewards - self.reward_in) ** 2, name='loss')
		self.opt = tf.train.AdamOptimizer().minimize(self.loss)
		
	
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
	
	
	def train(self, tensor_list, reward_list, actions_list, epsilon, save=False):
		images = np.asarray(tensor_list)
		rewards = np.asarray(reward_list).reshape(-1, 1)
		actions = np.asarray(actions_list).reshape(-1, 1)
		epsilon = np.array(epsilon).reshape((1,))
		
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
			path = '{}/{}.cpkt'.format(self.path, time.time())
			out_path = saver.save(self.sess, path)
			print('Saved to {}'.format(out_path))


	def predict(self, tensor_in, epsilon):
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
	
		
	
if __name__ == '__main__':
	pass
	
	m = MultiAgentCNN()
	
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
	
	# out = m.predict(batch_in, 0.3)
	# m.train(batch_in, reward, action, 0.2)
	writer = tf.summary.FileWriter('./summary', m.sess.graph)
	writer.flush()
	