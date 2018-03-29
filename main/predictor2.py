import tensorflow as tf
from tensorflow.python.ops import rnn, rnn_cell
import numpy as np

#class for predicting the correct response in the current conversation
class Predictor:
    max_length = 100
    vec_length = 100
    n_classes  = vec_length
    chunk_size = vec_length
    rnn_size   = 256

    def __init__(self,path):
        self.path = path

    #define RNN structure
    def recurrent_neural_network(self,x):
        layer = {'weights':tf.Variable(tf.random_normal([self.rnn_size,self.n_classes])),
                 'biases':tf.Variable(tf.random_normal([self.n_classes]))}

        x = tf.transpose(x, [1,0,2])
        x = tf.reshape(x, [-1, self.chunk_size])
        x = tf.split(x, self.max_length, 0)

        lstm_cell = rnn_cell.BasicLSTMCell(self.rnn_size,reuse=tf.AUTO_REUSE)
        outputs, states = rnn.static_rnn(lstm_cell, x, dtype=tf.float32)
        

        output = tf.matmul(outputs[-1],layer['weights']) + layer['biases']
        return output

    #pass a query to the RNN and get prediction
    def query_rnn( self, input_vector ):
        tf.reset_default_graph()
        X = tf.placeholder('float')
        y = tf.placeholder('float')
        s1 = self.recurrent_neural_network(X)
        saver = tf.train.Saver()
        with tf.Session() as sess:
            saver.restore(sess, self.path)
            return sess.run([s1], feed_dict={X: np.array([input_vector])})

