#!/usr/bin/env python

from searchtweets import load_credentials, gen_request_parameters, collect_results
from celery import Celery, signature, group
import datetime
import random
import time
import db
import os

app = Celery(
	broker=f'''amqp://{os.getenv('RABBITMQ_USER')}:{os.getenv('RABBITMQ_PASS')}@{os.getenv('RABBITMQ_HOST')}:{os.getenv('RABBITMQ_PORT')}''',
	backend=f'''rpc://{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}''',
)

# Set size of chunks
n = int(os.getenv('CHUNK_SIZE'))

def prioritize(tweets, docs):
	high = []
	low = []
	# Iterate over documents
	for doc in docs:
		# Iterate over tweets
		for tweet in tweets:
			# If a camera was mentioned in a tweet, designate it as a high-priority camera
			if doc['title'].lower() in tweet.lower() or doc['title'].lower().replace(' ','') in tweet.lower():
				high.append(doc)
			else:
				low.append(doc)
	return high, low

def produce(new_tweets):
	# Name of temporary local directory where images are saved to
	foldername = f'''{datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%S')}'''
	print(f'[-] Scraping commencing at {datetime.datetime.utcnow().isoformat()}')
	# Send makedir task to queue and wait for folder ID
	folderid = app.send_task('gdrive-mkdir', args=(foldername,), queue=os.getenv('QUEUE')).get()
	if folderid:
		# Initialize db object
		adb = db.arangodb()
		# Retrieve links from 'cameras' collection in database
		docs = adb.get_docs('cameras')
		# Prioritize cameras that were mentioned in new tweets
		high, low = prioritize(new_tweets, docs)
		random.shuffle(low)
		# Combine prioritized documents
		sorted_docs = high + low
		# Chunk the docs into n-long groups
		chunked_docs = [sorted_docs[i:i+n] for i in range(0, len(sorted_docs), n)]
		# Push scraping tasks to queue
		for chunk in chunked_docs:
			app.send_task('scrape-classic', args=(folderid, chunk,), kwargs={'timeout':1800}, queue=os.getenv('QUEUE'))

def schedule():
	# Initialize db object
	adb = db.arangodb()
	# Query tweets every minute
	while True:
		# Load credentials from environment vars
		search_args = load_credentials(None)
		# Craft query
		query = gen_request_parameters('@alertwildfire', granularity=None, results_per_call=10)
		# Collect tweet results
		tweets = collect_results(query, max_tweets=10, result_stream_args=search_args)[0]['data']
		# Toggle for new tweet
		new_tweets = []
		# Write to database
		for tweet in tweets:
			upsert_resp = adb.insert_new_tweet(tweet['id'], tweet['text'])[0]
			if upsert_resp['type'] == 'insert':
				new_tweets.append(tweet['text'])
		# If a new tweet was found, kick off scraping of alertwildfire camera images
		if len(new_tweets)>0:
			produce(new_tweets)
		# Try again in 1 minute
		time.sleep(3600)

if __name__ == '__main__':
	schedule()
