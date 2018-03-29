import warnings
warnings.filterwarnings('ignore')
from gensim.models import word2vec
import numpy as np
import pandas as pd
import os
import re
import pickle
import copy
import sys
import math
from time import sleep
import tensorflow as tf
from tensorflow.python.ops import rnn, rnn_cell

#Train a RNN with tensorflow that takes an input sentence of word vectors and outputs a single sentence vector
# representing the location of the output sentence in the semantic space

#initialize w2v mocel
w2v_model = word2vec.Word2Vec.load('../res/word2vec/semspace')


def init_movie_characters():
    movie_user_dataset = pd.read_csv('../res/cornell/movie_characters_metadata.csv', sep=';')
    characters = {}
    for r in movie_user_dataset.iterrows():
        idx = r[1]['Id'].lstrip().rstrip()
        name = r[1]['Name'].lstrip().rstrip().lower().split(' ')
        characters[idx] = name
    return characters

def VEC(word):
    try:
        return (True,np.array(w2v_model.wv[word]))
    except KeyError:
        return (False,None)

#initialize hyper parameters
max_length = 100
vec_length = 100
hm_epochs  = 100
n_classes  = vec_length
chunk_size = vec_length
batch_size = 32
rnn_size = 256
X = tf.placeholder('float')
y = tf.placeholder('float')

#load dataset
with open('../res/word2vec/conversation_dataset.p','rb') as fp:
    dialogue_data = pickle.load(fp)
movie_conversations = pd.read_csv('../res/cornell/movie_conversations.csv',sep=';')

#work in batches to save RAM
current_row = 0
def next_data_batch(batch_size=100):
    global current_row
    #get a slice for the next batch
    x_out = []
    y_out = []
    if current_row + batch_size >= movie_conversations.shape[0]:
        rows = movie_conversations[current_row:]
        current_row = 0
    else:
        rows = movie_conversations[current_row:(current_row+batch_size)]
        current_row += batch_size

    #extract input and output matrix and vector for entries in the current slice
    for r in rows.iterrows():
        row = r[1]
        buffer = [ np.zeros( vec_length ) for _ in range( max_length ) ]
        line_numbers = re.sub('[^L0-9 ]+','',row['Lines'].lstrip().rstrip()).split(' ')
        for line_idx in line_numbers:
            if dialogue_data[ line_idx ]['next_line_idx'] != None:
                buffer.pop(0)
                buffer.append( np.zeros( vec_length ) )
                for w in dialogue_data[ line_idx ]['sentence_word_vector']:
                    w_known, w_vec = VEC(w)
                    if( w_known ):
                        buffer.pop(0)
                        buffer.append( w_vec )
                next_line_idx = dialogue_data[ line_idx ]['next_line_idx']
                x_out.append( copy.deepcopy(np.array(buffer)) )

                try:
                    chris = len(dialogue_data[ next_line_idx ]['sentence_vector']) #catch NaN entries
                    y_out.append( np.array(dialogue_data[ next_line_idx ]['sentence_vector']) )
                except KeyError:
                    raise
                except:
                    y_out.append( np.zeros( 100 ))

    return ( np.array( x_out ), np.array( y_out ) )

#define structure of the RNN
def recurrent_neural_network(x):
    layer = {'weights':tf.Variable(tf.random_normal([rnn_size,n_classes])),
             'biases':tf.Variable(tf.random_normal([n_classes]))}

    x = tf.transpose(x, [1,0,2])
    x = tf.reshape(x, [-1, chunk_size])
    x = tf.split(x, max_length, 0)

    lstm_cell = rnn_cell.BasicLSTMCell(rnn_size,reuse=tf.AUTO_REUSE)
    outputs, states = rnn.static_rnn(lstm_cell, x, dtype=tf.float32)
    

    output = tf.matmul(outputs[-1],layer['weights']) + layer['biases']
    return output

#train the RNN using tensorflow
def train_neural_network(X):
    prediction = recurrent_neural_network(X)
    cost = tf.reduce_mean( tf.norm( tf.subtract( prediction, y ) ) )
    optimizer = tf.train.AdamOptimizer().minimize(cost)
    saver = tf.train.Saver()

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        for epoch in range(hm_epochs):
            epoch_loss = 0
            total = int(movie_conversations.shape[0]/batch_size)
            for i in range( int(movie_conversations.shape[0]/batch_size)):
                print( float(i)/total*100,' %         ', end='\r')
                sleep(0.01)
                (epoch_x, epoch_y) = next_data_batch(batch_size) # get next data batch

                _, c = sess.run([optimizer,cost], feed_dict={X: epoch_x, y:epoch_y}) # run the optimizer and cost function using the current batch
                epoch_loss += c

            print('Epoch', epoch, 'completed out of', hm_epochs,'loss:',epoch_loss)

            #after each epoch, save the model
            if epoch % 1 == 0:
                if not os.path.exists('../res/models/sentence_predictor/epoch_'+str(epoch)):
                    os.makedirs('../res/models/sentence_predictor/epoch_'+str(epoch))
                save_path = saver.save(sess, '../res/models/sentence_predictor/epoch_'+str(epoch)+'/rnn_model.ckpt')
                                    
            
train_neural_network(X)
