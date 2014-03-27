from flask import Flask, render_template, url_for, request, jsonify
from collections import Counter
import requests
import json
import nltk
import xmltodict
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn

app = Flask(__name__)

# intitialize everything
import twitter # Tell Python to use the twitter package
CONSUMER_KEY = 'oy1fFOFLfulcT9GVnTUcZg'
CONSUMER_SECRET = 'G8jpuiQ0GFxyFtq7pDPmuGiBQ7SQdbwKjyC2zA2ppw'
OAUTH_TOKEN = '2322817648-npNVa1PhLaspojJ4z04qkfnCKZPtvFR5LqPX8Fa' 
OAUTH_TOKEN_SECRET = 'DmuYAL9RivUMZmCa7zlOD4tG3Nx6G4qj24pLT9MI8oUjl'
auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,CONSUMER_KEY, CONSUMER_SECRET)
twitter_api = twitter.Twitter(auth=auth) 

relatedKey = 'sampleapikey'

@app.route("/")
def first_page():
    return render_template('index.html')

@app.route('/search', methods=["GET"])
def search():
	app.logger.debug('You arrived at: Search')
	app.logger.debug('I received the following arguments: ' + str(request.args) )
	q = request.args.get('query', None)
	count = 5
	search_results = twitter_api.search.tweets(q=q, count=count, lang="en")
	statuses = search_results['statuses'] 
	status_texts = [ status['text']
		for status in statuses ]	
	locations = []
	for status in statuses:
		if 'coordinate' in status:
			locations.append(status['coordinate'])
		else:
			locations.append('No location')
	p = {'key': relatedKey, 'base': q}
	req = requests.get('http://www.veryrelated.com/related-api-v1.php', params = p)
	synonyms = []
	for syn in wn.synsets(q):
		for lemma in syn.lemma_names:
			synonyms.append(lemma)
	synset = set(synonyms)
	if req.status_code == requests.codes.ok:
		related = getRelated(req.content)	
	return json.dumps([search_results, analyse(search_results),related, list(synset), locations])

def getRelated(xml):
	parsed = xmltodict.parse(xml)
	if 'Error' in parsed:
		return {'No very related words': 0}
	related = {rel['Text']: rel['HowRelated'] for rel in parsed['ResultSet']['Result']} 
	return sorted(related.items(), key=lambda t: t[1], reverse=True)
	
def analyse(search_results):
	app.logger.debug('You arrived at: Analyse')
	hashtags = []	
	screenNames = []
	words = []
	texts = []
	statuses = search_results['statuses'] 
	for tweet in statuses:
		texts.append(tweet['text'].encode('utf-8'));
		for tag in tweet['entities']['hashtags']:
			hashtags.append(tag['text'])
		for mention in tweet['entities']['user_mentions']:
			screenNames.append(mention['screen_name'])
	words = analyseText(texts)
	return {"hashtags": sorted(Counter(hashtags).items(), key=lambda t: t[1], reverse=True), "screenNames": sorted(Counter(screenNames).items(), key=lambda t: t[1], reverse=True), "words": sorted(Counter(words).items(), key=lambda t: t[1], reverse=True)}

def analyseText(texts):
	prefixes = ('http:','#','@','RT')
	tokenized = []
	skip = []
	for text in texts:
		tokens = []
		tokens = text.split()
		for token in tokens:
			if token.startswith(prefixes) and token not in skip:
				skip.append(token.lower())
			elif token.lower() not in stopwords.words('english') and token.lower() not in skip:
				tokenized.append(token.lower())
	return tokenized
	                                                                                                                                                                                                                                                                                                                                                    

if __name__ == "__main__":
	app.debug = True
	app.run()
