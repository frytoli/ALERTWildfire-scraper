#!/usr/bin/env python

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

def produce():
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
		random.shuffle(docs)
		# Chunk the docs into n-long groups
		chunked_docs = [docs[i:i+n] for i in range(0, len(docs), n)]
		# Push scraping tasks to queue
		for chunk in chunked_docs:
			app.send_task('scrape-classic', args=(folderid, chunk,), kwargs={'timeout':1800}, queue=os.getenv('QUEUE'))

def schedule():
	# Scrape indefinitely
	while True:
		produce()
		# Sleep for six hours and start again
		time.sleep(21600)

if __name__ == '__main__':
	schedule()
