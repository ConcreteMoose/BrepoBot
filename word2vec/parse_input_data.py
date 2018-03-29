# IMPORTANT
#run in StanfordCoreNLP folder:
# java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer
import os
import re
import logging as lo
from pycorenlp import StanfordCoreNLP
from gensim.models import word2vec
import sys
import pickle
import pandas as pd
import numpy as np

#Class that parses input sentences using StanfordCoreNLP
class Parser():
    def __init__(self, folder_name):
        self.folder_name = folder_name
        try:
            self.nlp = StanfordCoreNLP('http://localhost:9000')
        except:
            print("INSTRUCTIONS")
            print("in folder ./word2vec/stanford-corenlp-full-2018-02-27, open terminal and perform:")
            print("java -mx4g -cp \"*\" edu.stanford.nlp.pipeline.StanfordCoreNLPServer")
            raise
        
    #First remove punctuation from sentences and convert to lower case
    def clean_sentence( self, s ):
        try:
            s = s.replace('...',' ')
            s = s.lower()
            s = re.sub('<[A-Za-z0-9/]>','',s)
            s = re.sub('[^A-Za-z0-9 \',:;.?!]+', '', s)
            s = s.replace('.','.')
            s = s.replace('?','.')
            s = s.replace('!','.')
            while '  ' in s: s = s.replace('  ',' ')
            s = s.lstrip().rstrip()
            if s[-1] == ';':
                s = s[:-1] + s[-1:].replace(';','.')
            return s.lstrip().rstrip()
        except KeyboardInterrupt:
            raise
        except:
            print("Error with",s)
            raise

    #Split up the line in sentences by splitting on '.' then parse each sentence separately and extract POS tags
    def parse_sentence( self, s ):
        sentences = s.lower().split('.')
        parsed_sentence = []
        for sentence in sentences:
            if len(sentence)>0:
                try:
                    output = self.nlp.annotate(sentence, properties={
                        'annotators': 'parse',
                        'outputFormat': 'json',
                        'timeout': 100000
                    })
                    json = output['sentences'][0]['parse']
                    words = [m for m in re.findall('\([A-Z:.]+ [a-z0-9\',.?:;!]+\)', json)]
                    for w in words:
                        parsed_sentence.append(w)
                except KeyboardInterrupt:
                    raise
                except:
                    continue
        return parsed_sentence

    #Parse the entire cornell movie line dataset
    def parse_data(self):
        #sys.exit(0) # I don't really want to run this again
        lines = {}
        with open('../res/cornell/movie_lines.txt','rb') as f:
            total = 304713.
            i = 0
            for line in f:
                print(i/total*100,'%        ',end='\r')
                i += 1
                line = line.decode("ISO-8859-1",errors='ignore')
                l_data = line.split('+++$+++')
                sentence = self.clean_sentence( l_data[4] )
                parsed   = self.parse_sentence( sentence )
                lines[l_data[0]] = {'user':l_data[1],
                                    'movie':l_data[2],
                                    'name':l_data[3],
                                    'line':parsed}
        with open('movie_lines.p','w+b') as fp:
            pickle.dump(lines,fp,protocol=pickle.HIGHEST_PROTOCOL)

    #Parse MSR dataset. Currently unused because we changed sentence representation to a more comprehensible model
    def parse_sem_spacer(self):
        sentences = []
        train_data = pd.read_csv('../res/dataset/msr/train_data.csv',sep='\t',error_bad_lines=False).dropna()
        test_data  = pd.read_csv('../res/dataset/msr/test_data.csv',sep='\t',error_bad_lines=False).dropna()
        #train_labels = np.array(train_data['Quality'])
        #train_inputs = np.array( [[sent2vecs(r[1]['#1 String']),sent2vecs(r[1]['#2 String'])] for r in train_data.iterrows()])

        #no train-test set separation here since the dataset is quite small compared to the cornell dataset
        total = train_data.shape[0]+test_data.shape[0]
        i = 0.
        for r in train_data.iterrows():
            print( i/total*100,'%           ',end='\r')
            i += 1
            qu = r[1]['Quality']
            s1 = self.parse_sentence(self.clean_sentence(r[1]['#1 String']))
            s2 = self.parse_sentence(self.clean_sentence(r[1]['#2 String']))
            sentences.append({'Quality':qu,
                              '#1 String':s1,
                              '#2 String':s2})

        for r in test_data.iterrows():
            print( i/total*100, '%                 ', end='\r')
            i += 1
            qu = r[1]['Quality']
            s1 = self.parse_sentence(self.clean_sentence(r[1]['#1 String']))
            s2 = self.parse_sentence(self.clean_sentence(r[1]['#2 String']))
            sentences.append({'Quality':qu,
                              '#1 String':s1,
                              '#2 String':s2})
        data_array = np.array(sentences)
        np.save('../res/word2vec/msr_dataset.npy', data_array)

if __name__ == '__main__':
    parser = Parser('../res')
    parser.parse_data()
    parser.parse_sem_spacer()
