import os
import re
import numpy as np
import math as m
import pickle
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import TfidfVectorizer

DATAPATH  = '../res/dataset/method1'
STOREPATH = '../res/word2vec'

corpus = []
#movie database
with open('movie_lines.p', 'rb') as f:
    data_lines = pickle.load(f)
    for key in data_lines:
        corpus.append( data_lines[key]['line'] )
#MSR database
msr_dataset = np.load('../res/word2vec/msr_dataset.npy')
for r in msr_dataset:
    corpus.append( r['#1 String'] )
    corpus.append( r['#2 String'] )

"""
for fname in os.listdir(DATAPATH):
    doc = ""
    for line in open(os.path.join(DATAPATH, fname)):
        line = line.lower()
        line = line.replace('...',' ')
        while '  ' in line: line = line.replace('  ',' ')
        line = re.sub('[^A-Za-z0-9@ \']+', '', line)
        line = line.lstrip().rstrip()
        if len(line)>0:
            doc += ' ' + line
    corpus.append( doc )
corpus = np.array(corpus)
"""
df_dict = {}
for doc in corpus:
    words_in_doc = {}
    for word in doc:#.split(' '):
            words_in_doc[word] = True
    for word in words_in_doc:
        try:
            df_dict[word] += 1
        except KeyError:
            df_dict[word] = 1
    del words_in_doc

idf_dict = {}
N = float(len(corpus))
for word in df_dict:
    idf_dict[word] = m.log(N/df_dict[word])

np.save( os.path.join(STOREPATH,'idf.npy'), idf_dict ) 
