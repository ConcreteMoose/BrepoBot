import xml.etree.ElementTree as ET
import re
import random
import Levenshtein



class Querier():
	root = None

	def __init__(self, database):
		tree = ET.parse(database)
		Querier.root = tree.getroot()

	def extract_film(self,film):                 # Extract film name from text
		qfilm = re.findall(r"\"[^\"]+\"", film)  # See if there is something in quotes
		if qfilm:
			rem = re.compile(r"\"")              # If there is, return that
			return rem.sub("", qfilm[0])

		# If not, remove common words: from, about, and please
		remWords = re.compile(r"from\s+|\s+from|about\s+|\s+about|please\s+|\s+please")
		film = remWords.sub("", film)
		film = re.sub(r'[^a-zA-Z0-9\s]', "", film)
		print(film)
		return film


	def findFilm(self, name):
		bestSim = 0
		bestFilm = None
		for page in Querier.root.findall('{http://www.mediawiki.org/xml/export-0.10/}page'):
			film = page.find('{http://www.mediawiki.org/xml/export-0.10/}title').text
			remBrackets = re.compile(r"\s*\([^\)]*\)\s*")         # Remove subtext in brackets
			film = remBrackets.sub("",film)
			sim = Levenshtein.ratio(name.lower(),film.lower())
			if sim > bestSim:
				bestSim = sim
				rev = page.find('{http://www.mediawiki.org/xml/export-0.10/}revision')
				bestFilm = (film, rev.find('{http://www.mediawiki.org/xml/export-0.10/}text').text)
		return bestFilm


	def pickQuote(self, raw):
		splitCast = re.compile(r'==\sCast|==Cast|==\sEx|==Ex')      # Remove Cast, which also employs asterisks.
		noCast = splitCast.split(raw)[0]
		matches = re.findall(r'[^*]\*[^*].*(?!\*)' ,noCast)         # Find all possible quotes
		if not matches:                                             # If there are no quotes, return 'No quote found'
			return "No quote found"

		quote = random.choice(matches)                              # Choose a random quote
		findChar = re.findall(r'==[^=]*==', noCast.split(quote)[0]) # Find the Character that spoke that quote
		char = findChar[-1]
		remEq = re.compile(r"==\s|\s==|==")                         # Remove unnecessary characters from char
		char = remEq.sub('',char)

		remSp = re.compile(r"'''|''|\[\[|\]\]|\*\s*|^\s*")          # Remove unnecessary characters from quote
		remBr = re.compile(r"<br>")
		quote = remSp.sub('', quote)
		quote = remBr.sub(" ", quote)

		quote = char + ":\n" + quote                                # Add char and quote
		return quote                                                # return the combination

	def getInfo(self, raw):
		start = raw.split("==")[0]
		# Remove all random characters that are found in the about-section of wikiquote.
		rem  = re.compile(r"'''|''|\[\[(File:|#)[^]]*\]\]|\[\[w:[^|]*\||\[\[|\]\]|^\s*|\{\{[^}]*\}\}|\{|italic title\}\}|<[^>]*>")
		info = rem.sub('', start)
		remn = re.compile(r"^\W")
		info = remn.sub('', info)
		rems = re.compile(r"^\s*")
		info = rems.sub('', info)
		remsc= re.compile(r"^:\s*",flags=re.MULTILINE)
		info = remsc.sub('', info)
		return info


	def returnQuote(self, film):
		film = self.extract_film(film)
		filmtitle, rawtext = self.findFilm(film)

		if filmtitle:
			return "Here's a quote from " + filmtitle + "!\n\n" + self.pickQuote(rawtext)
		else:
			return "no quote found"

	def returnInfo(self, film):
		film = self.extract_film(film)
		filmtitle, rawtext = self.findFilm(film)
		if filmtitle:
			return self.getInfo(rawtext)
		else:
			return "no info found"

