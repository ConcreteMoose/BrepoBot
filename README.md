# BrepoBot: the dramatic filmbot

For our chatbot project, we decided to train on a film dialogue database, to create an overly dramatic bot. It generally will answer in long dramatic monologues to your messages, but if you ask it nicely, it will tell you something about your favorite film or tell you a quote from a specific film. 

### Start Example

It starts a conversation with an introduction, also stating the querying possibilities. It does this when the chat-id of the incoming message is unknown to him:

> **USER:**
> Hello.
> 
> **BREPOBOT:**
> Hello, a pleasure as always. I am Brepo, the overly dramatic film bot. I don't like listening to people much, so excuse me if I ignore you and go on a rant. On the bright side, if you'd like to get some 'info' or a 'quote' from some movie and you're too lazy to search for it yourself, just ask me and I'll google it for you.

## Queries

We first created the query functionality. We scraped a database of quotes and information about films from wikiquote using their build-in [export site](https://en.wikiquote.org/wiki/Special:Export). This is saved to an xml-file, which is called `Filmquotes.xml`. The code for the Queries can be found in `database_parser.py`, and it is called and used in the main file `telegram.py`.

To ask for a query, either *quote* or *about* should be added in the message. If this is found, the bot will search for the film that is most similar to the rest of the text in the message, after this text is cleaned. This similarity is calculated using the `Levenshtein` package for python. Once it has found a film, it will take the text of that wikiquote page (which is saved as a string in the xml-file). If the request was made for a quote, it will create a list of all quotes found on that page, and then randomly pick one of these quotes. If the request was for an about section on the film, it will extract the about section. This was done using regular expressions, using the python package *re*. Since the text in the database is written in some kind of mark-up language, the regular expressions to clean the text are quite long and unreadable. 

Once a quote or about section is chosen and cleaned, it is returned to the user that made the request.

### Example

> **USER:**
> Could you give me some info about pulp fiction?
>
> **BREPOBOT:**
> Pulp Fiction is a 1994 neo-noir film about the lives of two mob hit men, a boxer, a gangster's wife, and a pair of diner bandits that intertwine in four tales of violence and redemption.
> Written and directed by Quentin Tarantino.
> You won't know the facts until you've seen the fiction. 
> 
> **USER:**
> How about a quote from hard candy?
> 
> **BREPOBOT:**
> Here's a quote from Hard Candy!
>
> Hayley Stark:
> Playtime is over, Jeff. Now it's time to wake up.

It always answers with a film, so if it does not have a film in its database, it will find the one with the closest name to it.

> **USER:**
> Can I have a quote from Pacific Rim please?
> 
> **BREPOBOT:**
> Here's a quote from Pacific Heights!
> 
> Carter Hayes:
> [to James Danforth in the interrogation room] They're lying. These people are completely pathological.


## Chit chat

Chit Chat is governed by a Recurrent Neural Network (RNN) trained on the cornell movie dialogue corpus, available at http://www.cs.cornell.edu/~cristian//Cornell_Movie-Dialogs_Corpus.html. This dataset contains movie lines of over 500 movies and a table indicating which lines belong to which conversation. The lines in the corpus have been parsed with `pycorenlp` using the `StanfordCoreNLP` package available at https://stanfordnlp.github.io/CoreNLP/. A 100-dimensional word2vec model has been trained on these parsed lines using the `gensim` package and for each tokenized word, IDF has been calculated. For each line in the dataset, a semantic space representation has been calculated by averaging the vectors of the words in the sentence multiplied with their respective IDFs. Next a RNN containing a Long Short-Term Memory (LSTM) cell with 256 nodes has been implemented using tensorflow and trained to predict the semantic space representation of the next sentence in a dialogue, based on a matrix containing the word vectors of the previous 100 words in the conversation. When chatting with Brepo, this RNN is queried to predict the semantic location of the optimal response. Then the actual locations of all sentences in the dataset are compared to the intended location, and the sentence closest to the prediction is sent to the user.

Unfortunately, sentence selection in practice seems rather incoherent. Possibly, movie dialogues are not coherent enough to accurately predict the next interaction in a dialogue. This is plausible, since it has been observed that network loss during training did not improve much from random. Alternatively, other representations of sentence meaning could be tried. We experimented with training a separate RNN which maps sentences to a point in semantic space such that sentences with similar meaning lie close together, whereas sentences with different meaning are far apart. This model was trained on the MRS dataset available at https://github.com/brmson/dataset-sts, however performance was poor. Because no labeled datasets specifically in the domain of movie dialogues was available, we did not explore this possibility further.


## Improvements

### Queries

The biggest problem with the queries at the moment, is the fact that similarity partly depends on length. So if you ask for a movie by its short name, *narnia* for example, it will not find the film that is specified by its full name: *The Chronicles of Narnia: The Voyage of the Dawn Treader*. It would be useful to include some kind of measure that sees whether the given name is actually part of the film, and prioritize those films. This is not necessarily easy however. If the quotes and info are asked for in a natural way, the bot can confuse what is part of the name of the film, and what is part of the sentence surrounding that name. For example: if you ask *"Can you give me a quote of the incredibles?"*, it will search for films with the title *Of the incredibles*. Due to the similarity measure, the right film is found, but completely fitting words in the input to the film could result in high emphasis on words that are not actually part of title (like *of* in this case). We are not yet sure of how these two measures could be succesfully combined.

> **USER:**
> quote narnia
> 
> **BREPOBOT:**
> Here's a quote from Daria!
>
> No quote found
>
> **USER:**
> quote the chronicles of narnia
>
> **BREPOBOT:**
> Here's a quote from The Chronicles of Riddick!
>
> Riddick:
> So now it's back to all the brightness, and everything I hate.
>
> **USER:**
> quote The Chronicles of Narnia: The Voyage of the Dawn Treader
>
> **BREPOBOT:**
> Here's a quote from The Chronicles of Narnia: The Voyage of the Dawn Treader!
>
> Taglines:
> Return to magic. Return to hope. Return to Narnia

### Sequence to sequence RNN

Our current network does not manage to respond with logical sentences (most of the time). We believe that this might be partly due to the incoherence of movie scripts, but we also believe it is due to the limited amount of answers the network can respond with. Although it has 300.000 possible answers, most of these answers are highly specific, and cannot really be used in almost any situation. To combat this limit, we thought of employing sequence to sequence RNNs (seq2seq). Seq2seq predicts the answer per word, instead of the whole sentence in one go, as we have been doing. This makes the total amount of possible answers almost limitless, but it does often result in non-grammatically correct sentences. We did not have the time to actually train a new network (since training costs most of a day), but if we continue this project, this is probably the first change we will implement.

