#run in StanfordCoreNLP folder:
# java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer
from gensim.models import word2vec
import numpy as np
import pandas as pd
import os
import re
import pickle
import copy
import sys
from scipy.spatial.distance import euclidean
import re

from time import sleep
import tensorflow as tf
from tensorflow.python.ops import rnn, rnn_cell
from gensim.models import word2vec


sys.path.append('../word2vec')
from predictor2 import Predictor

from parse_input_data import Parser

#main class for accessing the predictive model
class Main():

    def __init__(self):
        self.predictor = Predictor('../res/models/sentence_predictor/epoch_23/rnn_model.ckpt')
        self.w2v_model = word2vec.Word2Vec.load('../res/word2vec/semspace')
        self.buffer    = [""]*1000
        self.wv_buffer = [np.zeros(100)]*100
        self.parser    = Parser('')
        self.characters = self.init_movie_characters()
        with open('../res/word2vec/conversation_dataset.p','rb') as fp:
            self.conv_data = pickle.load(fp)
        print("Listening...")

    # pass a sentence to Brepo, returns what Brepo has to say about that.
    def brepo_says(self, sentence):
        parsed_sentence = self.parse(sentence)
        word_vector     = self.word_vector(parsed_sentence)
        prediction      = self.predictor.query_rnn( self.wv_buffer )
        output_sentence = self.findSent( prediction )
        return output_sentence
        
        
    #track movie characters, to differentiat speaker and listener
    def init_movie_characters(self):
        movie_user_dataset = pd.read_csv('../res/cornell/movie_characters_metadata.csv', sep=';')
        characters = []
        for r in movie_user_dataset.iterrows():
            idx = r[1]['Id'].lstrip().rstrip()
            name = ' ' + r[1]['Name'].lstrip().rstrip().lower() + ' '
            characters.append(re.compile(re.escape(name),re.IGNORECASE))
        return characters

    #parse the sentence using StanfordNLP
    def parse(self, sentence):
        return self.parser.parse_sentence(sentence)

    #convert the sentence to a list of word vectors, including vectors from previous sentences
    # so that brepo remembers the context of the conversation
    def word_vector( self, parsed_sentence ):
        sentence_word_vector = []
        self.wv_buffer.pop(0)
        self.wv_buffer.append(np.zeros(100))
        for word in parsed_sentence:
            try:
                word_vec = self.w2v_model.wv[word]
                sentence_word_vector.append(word_vec)
                self.wv_buffer.pop(0)
                self.wv_buffer.append(word_vec)
                self.buffer.pop(0)
                self.buffer.append(word)
            except KeyError:
                continue
        return sentence_word_vector

    # given a prediction of a location in the semantic space,
    # find the sentence from the movie database that most accurately captures
    # this meaning.
    def findSent(self,semVec):
        best = None
        sent = None
        for key in self.conv_data:
            tempSent = self.conv_data[key]['sentence_vector']
            try:
                dist = euclidean(tempSent, semVec)
                
                if best is None:
                    best = dist
                    sent = self.conv_data[key]['sentence_string']
                else:
                    if dist < best:
                        best = dist
                        sent = self.conv_data[key]['sentence_string']
            except:
                continue
        print(best)
        return sent

    #telegram was down while testing this, so you can also talk chit-chat with brepo
    # via a text file
    def test_environ(self):
        sentence = ""
        while True:
            updated = False
            try:
                with open('buffer.txt','r') as f:
                    sleep(0.5)
                    for line in f:
                        if line.split(' ')[0] == "me:":
                            sentence = line.rstrip().replace('me: ','')
                            sentence = "BREPO: " + self.brepo_says(sentence)
                            updated = True
                if updated:
                    updated = False
                    with open('buffer.txt','w') as f:
                        f.write(sentence)
            except KeyboardInterrupt:
                raise
            except:
                continue
                        
    
    def close_rnn_session(self):
        pass
        #self.predictor.close_session()
        
if __name__ == '__main__':
    m = Main()
    m.test_environ()
    #m.brepo_says('Hello')
    m.close_rnn_session()
