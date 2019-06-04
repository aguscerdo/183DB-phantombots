import tensorflow as tf
import os
import numpy as np
import time


class MultiAgentCNN:
	def __init__(self, name, size=6):
		self.path = './weights'
		if not os.path.exists(self.path):
			os.mkdir(self.path)
		self.name = name
		
		self.i = 0
		self.epsilon = 0.8
		self.size = size
		
		self.build_network()
		self.sess = tf.Session()
		self.sess.run(tf.global_variables_initializer())
	
	def build_network(self):
		with tf.variable_scope(self.name):
			self.images = tf.placeholder(tf.float32, shape=(None, self.size, self.size, 3), name='in_image')
			
			nn = tf.layers.conv2d(inputs=self.images, filters=16,
			                        kernel_size=[3, 3], padding='same',
			                        activation='relu')
			
			with tf.variable_scope('residual_1'):
				nn = self.residual_layer(nn)
			with tf.variable_scope('residual_2'):
				nn = self.residual_layer(nn)
	
			with tf.variable_scope('fully_connected'):
				flat = tf.layers.flatten(nn)
				nn1 = tf.layers.Dense(64, activation='relu')(flat)
	
				self.predicted_reward = tf.layers.Dense(5, activation="linear")(nn1)
			
			self.action_in = tf.placeholder(tf.int32, shape=(None, 1), name='action_in')
			self.reward_in = tf.placeholder(tf.float32, shape=(None, 1), name='actual_rewards')
			
			with tf.variable_scope('loss'):
				self.gathered_rewards = tf.gather(self.predicted_reward, self.action_in, axis=1)[:, 0, :]
				self.loss = tf.losses.mean_squared_error(self.reward_in,  self.gathered_rewards)
				#self.MSE(self.reward_in, self.gathered_rewards)
			
			self.opt = tf.train.GradientDescentOptimizer(learning_rate=0.0001).minimize(self.loss)
			tf.summary.scalar('loss', self.loss)
		
	
	def MSE(self, y_true, y_pred):
		return tf.reduce_mean((y_true - y_pred) ** 2, name='loss')
	
	
	def cross_entropy(self, y_true, y_pred):
		with tf.variable_scope('cross_entropy'):
			one_hot = tf.one_hot(y_true, 5)
			return tf.losses.softmax_cross_entropy(one_hot, y_pred)
	
	
	@staticmethod
	def residual_layer(layer_in):
		nn = tf.layers.conv2d(inputs=layer_in, filters=16,
		                        kernel_size=[3, 3], padding='same',
		                        activation='relu')
		
		nn = tf.layers.batch_normalization(nn)
		
		nn = tf.layers.conv2d(inputs=nn, filters=16,
		                        kernel_size=[3, 3], padding='same',
		                        activation=None)
		
		concat = tf.concat([layer_in, nn], axis=-1)
		return tf.layers.max_pooling2d(concat, [2, 2], [1, 1])
	
	
	@staticmethod
	def __inception_layer_helper(layer_in):
		# 1x1
		cnn11 = tf.layers.conv2d(inputs=layer_in, filters=32,
	                        kernel_size=[1, 1], padding='same',
	                        activation='relu')
			
		# 2x2
		cnn12 = tf.layers.conv2d(inputs=layer_in, filters=32,
	                        kernel_size=[1, 1], padding='same',
	                        activation='relu')
		
		cnn22 = tf.layers.conv2d(inputs=cnn12, filters=32,
		                        kernel_size=[2, 2], padding='same',
		                        activation='relu')

		# 3x3
		cnn13 = tf.layers.conv2d(inputs=layer_in, filters=32,
	                        kernel_size=[1, 1], padding='same',
	                        activation='relu')
		
		cnn23 = tf.layers.conv2d(inputs=cnn13, filters=32,
		                        kernel_size=[3, 3], padding='same',
		                        activation='relu')
			
		
		# Concat
		concat = tf.concat([cnn11, cnn22, cnn23], axis=-1)
		out = tf.layers.conv2d(inputs=concat, filters=32,
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
		
	
	def get_max_value(self, end_tensor_list, reward_list):
		rewards = np.asarray(reward_list).reshape(-1, 1)
		end_state = np.asarray(end_tensor_list)

		value = self.sess.run(self.predicted_reward, feed_dict={self.images: end_state})
		value = np.array(np.max(value, axis=1)).reshape((-1, 1))
		return rewards * self.epsilon + value
	
	
	def train(self, tensor_list, reward_list, actions_list, end_tensor_list, save=False):
		images = np.asarray(tensor_list)
		actions = np.asarray(actions_list).reshape(-1, 1)
		values = self.get_max_value(end_tensor_list, reward_list)

		batch_size = 32
		num_samples = len(values)
		
		aranged = np.arange(num_samples)
		
		np.random.shuffle(aranged)
		sampled_images = images
		sampled_values = values
		sampled_actions = actions
		
		for i in range(num_samples // batch_size):
			if i * batch_size > 15000:
				break
			getter = aranged[i*batch_size:(i+1)*batch_size]
			
			sampled_images = images[getter]
			sampled_values = values[getter]
			sampled_actions = actions[getter]
			
			while sampled_images.shape[1] != self.size or sampled_images.shape[2] != self.size or sampled_images.shape[3] != 3:
				sampled_images = sampled_images.transpose((0, 2, 3, 1))

			self.sess.run(self.opt,
			              feed_dict={
				              self.images: sampled_images,
				              self.reward_in: sampled_values,
				              self.action_in: sampled_actions,
			              })
	
		if save:
			self.save()
		
		rand_sample = np.arange(num_samples // 2)
		np.random.shuffle(rand_sample)
		
		sampled_actions = actions[rand_sample]
		sampled_images = images[rand_sample]
		sampled_values = values[rand_sample]

		
		return self.sess.run(self.loss,
		                     feed_dict={
				              self.images: sampled_images,
				              self.reward_in: sampled_values,
				              self.action_in: sampled_actions,
			              })
		

	def save(self):
		saver = tf.train.Saver()
		path = '{}/{}'.format(self.path, time.time())
		os.mkdir(path)
		out_path = saver.save(self.sess, path + '/model.cpkt')
		print('Saved to {}'.format(out_path))
		
		writer = tf.summary.FileWriter('./summary', self.sess.graph)
		writer.flush()
		

	def predict(self, tensor_in):
		tensor = np.array(tensor_in)
		if len(tensor.shape) == 3:
			tensor = tensor.reshape((1, -3, -2, -1))
			
		while tensor.shape[1] != self.size or tensor.shape[2] != self.size or tensor.shape[3] != 3:
			tensor = tensor.transpose((0, 3, 1, 2))
			
		out = self.sess.run(self.predicted_reward,
		              feed_dict={
			              self.images: tensor,
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
	size = 6
	l = 10
	
	m = MultiAgentCNN(name="Base0", size=size)

	batch_in = np.random.randint(0, 1, size=(l, size, size, 3))

	reward = np.random.uniform(size=(1, l-1))
	action = np.random.randint(0, 4, size=(1, l-1))

	# out = m.predict(batch_in, 0.3)
	m.train(batch_in[1:], reward, action, batch_in[:-1], save=True)
	m.load()

	