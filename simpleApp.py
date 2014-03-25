from flask import Flask, render_template, url_for, request, jsonify
import requests
import json
import nltk

app = Flask(__name__)

# intitialize everything
import twitter # Tell Python to use the twitter package
CONSUMER_KEY = 'oy1fFOFLfulcT9GVnTUcZg'
CONSUMER_SECRET = 'G8jpuiQ0GFxyFtq7pDPmuGiBQ7SQdbwKjyC2zA2ppw'
OAUTH_TOKEN = '2322817648-npNVa1PhLaspojJ4z04qkfnCKZPtvFR5LqPX8Fa' 
OAUTH_TOKEN_SECRET = 'DmuYAL9RivUMZmCa7zlOD4tG3Nx6G4qj24pLT9MI8oUjl'
auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,CONSUMER_KEY, CONSUMER_SECRET)
twitter_api = twitter.Twitter(auth=auth) 
related = []

@app.route("/")
def first_page():
    return render_template('index.html')
    return render_template('index.html')

@app.route('/search', methods=["GET"])
def search():
	app.logger.debug('You arrived at: Search')
	app.logger.debug('I received the following arguments: ' + str(request.args) )
	query = request.args.get('query', None)
	
	q = query
	count = 20
	search_results = twitter_api.search.tweets(q=q, count=count, lang="en")
	statuses = search_results['statuses'] 
	status_texts = [ status['text']#.replace('"', '\\"')
		for status in statuses ]
	analyse(search_results)
	return jsonify(search_results)
	
# def analyse(search_results):
	# app.logger.debug('You arrived at: Analyse')
	# app.logger.debug('I received the following arguments: ' + str(request.args) )
	# statuses = search_results['statuses'] 
	# status_texts = [ status['text']#.replace('"', '\\"')
		# for status in statuses ]
	# tokens = []
	# for text in status_texts:
		# app.logger.debug(nltk.word_tokenize(text)[0])
		# tokens.append(nltk.word_tokenize(text))

#@app.route('/analyse', methods=["GET"])
def analyse(search_results):
  app.logger.debug('You arrived at: Analyse')
  app.logger.debug('I received the following arguments: ' + str(request.args) )
  hashtags = []	
  screenNames = []
  texts = []
  statuses = search_results['statuses'] 
  for tweet in statuses:
    texts.append(tweet['text'].encode('utf-8'));
    for tag in tweet['entities']['hashtags']:
       hashtags.append(tag['text'])
    for mention in tweet['entities']['user_mentions']:
      screenNames.append(mention['screen_name'])
  #analyseHashTags()
  #analyseScreenNames()
  return analyseText(texts)

def analyseText(texts):
  prefixes = ('http:','#','@','RT')
  tokenized = []
  skip = []
  for text in texts:
    tokens = []
    tokens = text.split()
    for token in tokens:
      if token.startswith(prefixes) and token not in skip:
        skip.append(token)
      elif token not in skip:
        tokenized.append(token)
  fd = nltk.FreqDist(tokenized)
  #tf_idf[token] = TextCollection.tf_idf(collection, token, txt)
  #sorted(tokenized, key=tf_idf.__getitem__)
  related.append(fd)
  return jsonify(fd)		
	
@app.route('/getRelated', methods=["GET"])
def getRelated():
  return "related"
	
def fdist(arr):
	return 

if __name__ == "__main__":
	app.debug = True
	app.run()
