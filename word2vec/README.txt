run files in the following:

parse_input_data.py := construct database with tokenized word-tags for movie conversation dataset
word2vec.py         := construct word2vec vectors on the token-word pairs
doc2idf.py          := make idf counts for all token-word pairs
movie_dialogue.py   := construct dataset needed to train RNN
