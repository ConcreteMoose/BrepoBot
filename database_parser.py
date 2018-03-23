import xml.etree.ElementTree as ET
import re
import random



class Querier():
	root = None

	def __init__(self, database):
		tree = ET.parse(database)
		Querier.root = tree.getroot()


	def findFilm(self, name):
		for page in Querier.root.findall('{http://www.mediawiki.org/xml/export-0.10/}page'):
			film = page.find('{http://www.mediawiki.org/xml/export-0.10/}title').text
			if name.lower() in film.lower() or film.lower() in name.lower():
				rev = page.find('{http://www.mediawiki.org/xml/export-0.10/}revision')
				return film, rev.find('{http://www.mediawiki.org/xml/export-0.10/}text').text
		return None, None


	def pickQuote(self, raw):
		splitCast = re.compile(r'==\sCast|==Cast|==\sEx|==Ex')                  # Remove Cast, which also employs asterisks.
		noCast = splitCast.split(raw)[0]
		matches = re.findall(r'[^*]\*[^*].*(?!\*)' ,noCast)         # Find all possible quotes
		if not matches:                                             # If there are no quotes, return 'No quote found'
			return "No quote found"

		quote = random.choice(matches)                              # Choose a random quote
		findChar = re.findall(r'==[^=]*==', noCast.split(quote)[0]) # Find the Character that spoke that quote
		char = findChar[-1]
		remEq = re.compile(r"==\s|\s==|==")                            # Remove unnecessary characters from char
		char = remEq.sub('',char)

		remSp = re.compile(r"'''|''|\[\[|\]\]|\*\s*|^\s*")          # Remove unnecessary characters from quote
		remBr = re.compile(r"<br>")
		quote = remSp.sub('', quote)
		quote = remBr.sub(" ", quote)

		quote = char + ":\n" + quote                                # Add char and quote
		return quote                                                # return the combination

	def getInfo(self, raw):
		start = raw.split("==")[0]
		rem = re.compile(r"'''|''|\[\[(File:|#)[^]]*\]\]|\[\[w:[^|]*\||\[\[|\]\]|^\s*|\{\{[^}]*\}\}|\{|italic title\}\}|<[^>]*>")
		info = rem.sub('', start)
		remn = re.compile(r"^\W")
		info = remn.sub('', info)
		rems = re.compile(r"^\s*")
		info = rems.sub('', info)
		remsc= re.compile(r"^:\s*",flags=re.MULTILINE)
		info = remsc.sub('', info)
		return info


	def returnQuote(self, film):
		filmtitle, rawtext = self.findFilm(film)

		if filmtitle:
			return "Quote from " + filmtitle + ":\n\n" + self.pickQuote(rawtext)
		else:
			return "no quote found"

	def returnInfo(self, film):
		filmtitle, rawtext = self.findFilm(film)
		if filmtitle:
			return self.getInfo(rawtext)
		else:
			return "no info found"

