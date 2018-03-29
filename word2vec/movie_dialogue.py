from gensim.models import word2vec
import numpy as np
import pandas as pd
import os
import re
import pickle
import copy
import sys

from time import sleep

max_length = 50 #max nr of words in sentence
vec_length = 100 #dimensions in word vector

#track movie characters, to differentiat speaker and listener
def init_movie_characters():
    movie_user_dataset = pd.read_csv('../res/cornell/movie_characters_metadata.csv', sep=';')
    characters = {}
    for r in movie_user_dataset.iterrows():
        idx = r[1]['Id'].lstrip().rstrip()
        name = r[1]['Name'].lstrip().rstrip().lower().split(' ')
        characters[idx] = name
    return characters

#return the wordvector of word if it is known
def VEC(word):
    try:
        return (True,np.array(w2v_model.wv[word]))
    except KeyError:
        return (False,None)


#initialize w2v and IDF models
w2v_model = word2vec.Word2Vec.load('../res/word2vec/semspace')
idf_model = np.load('../res/word2vec/idf.npy').item()

#load the dataset with parsed movie lines
with open('movie_lines.p','rb') as f:
    movie_lines = pickle.load(f)

#load the dataset with movie conversations. Conversations are represented as a list of movie lines corresponding with
# keys in movie_lines
movie_conversations = pd.read_csv('../res/cornell/movie_conversations.csv',sep=';')
movie_characters    = init_movie_characters()
movie_line_strings = {}
with open('../res/cornell/movie_lines.txt','r') as f:
    for line in f:
        columns = line.split(' +++$+++ ')
        movie_line_strings[columns[0]] = columns[4].lstrip().rstrip()

#track number of entries for progress reporting
total = movie_conversations['Person1'].count()
j = 0.

#construct the conversation dataset
conversation_dataset = {}
for r in movie_conversations.iterrows():
    sleep(0.0001) #save some CPU space
    print(j/total*100, ' %           ', end='\r')
    j += 1

    #keep a buffer of word vectors on hand, so that context information from previous sentences can be
    #input in the rnn along with the current sentence
    word_buffer = [ np.zeros(100) for _ in range(100) ]

    #try to recognise when a character is talking about themselves or directly at the listener,
    #if so, replace their names with names more suitable for the chatbot scenario
    person1 = movie_characters[ r[1]['Person1'].lstrip().rstrip() ]
    person2 = movie_characters[ r[1]['Person2'].lstrip().rstrip() ]
    line_numbers = re.sub('[^L0-9 ]+','',r[1]['Lines'].lstrip().rstrip()).split(' ')
    
    conversation = [ (line_idx,movie_lines[line_idx+' ']) for line_idx in line_numbers ]
    sentences = []
    for i,(line_idx,sentence) in enumerate(conversation):
        speaker = person1 if sentence['user'].lstrip().rstrip() == r[1]['Person1'].lstrip().rstrip() else person2
        listener = person2 if speaker == person1 else person1
        line = sentence['line']
        try:
            for speaker_name in speaker:
                line = [re.sub(' '+speaker_name+'\)', ' brepo)', word) for word in line ]
            for listener_name in listener:
                line = [re.sub(' '+listener_name+'\)', ' human)', word) for word in line ]
        except KeyError:
            raise
        except Exception as e:
            print(e)
        print("I fucked up with",speaker, "or", listener)

        sentence_word_vector = []
        for word in line:
            try:
                word_vec = w2v_model.wv[word] * idf_model[word]
                sentence_word_vector.append(word_vec)
            except KeyError:
                continue

        #the meaning of a sentence is represented as the mean of the word vectors multiplied with the idf of the word
        sentence_vector = np.mean( np.array(sentence_word_vector) , axis=0 )     

        #keep track of the original line        
        sentence_string = movie_line_strings[line_idx]

        #store which movie line is the desired response to this sentence
        next_line_idx = None if i+1 >= len(conversation) else conversation[i+1][0]

        #store in dictionary
        conversation_dataset[line_idx] = {  'line_idx':line_idx,
                                            'sentence_string':sentence_string,
                                            'sentence_word_vector':sentence['line'],
                                            'sentence_vector':sentence_vector,
                                            'next_line_idx':next_line_idx}

#save dictionary
with open('../res/word2vec/conversation_dataset.p','w+b') as fp:
    pickle.dump(conversation_dataset,fp,protocol=pickle.HIGHEST_PROTOCOL)
                                          

