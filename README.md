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


## Talk



## Improvements

### Queries

The biggest problem with the queries at the moment, is the fact that similarity partly depends on length. So if you ask for a movie by its short name, *narnia* for example, it will not find the film that is specified by its full name: *The Chronicles of Narnia: The Voyage of the Dawn Treader*.

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


