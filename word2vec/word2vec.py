import sys
import os
import re
import logging
import pickle
import numpy as np
import pandas as pd
from gensim.models import word2vec

STOREPATH = '../res/word2vec'
DATAPATH  = '../res/dataset/method1'
vec_len   = 100

# construct word2vec vectors on the parsed sentences using gensim
class MySentences(object):
    def __init__(self, dirname):
        self.dirname = dirname

    #remove any trailing punctuation thats not used
    def clean_sentence(self, s):
        s = s.replace('...',' ')
        s = s.replace(',',' ')
        while '  ' in s: s = s.replace('  ',' ')
        s = s.lower()
        s = re.sub('[^A-Za-z0-9@ \']+', '', s)
        return s.lstrip().rstrip()

    #iterator object for gensim training
    def __iter__(self):
        #movie database
        with open('movie_lines.p', 'rb') as f:
            data_lines = pickle.load(f)
            for key in data_lines:
                yield data_lines[key]['line']

        #MSR database
        msr_dataset = np.load('../res/word2vec/msr_dataset.npy')
        for r in msr_dataset:
            yield r['#1 String']
            yield r['#2 String']
            

sentences = MySentences(DATAPATH)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
model = word2vec.Word2Vec(sentences, iter=10, min_count=10, size=vec_len, workers=4)
model.save(os.path.join(STOREPATH,'semspace'))
