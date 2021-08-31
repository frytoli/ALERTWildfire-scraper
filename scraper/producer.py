#!/usr/bin/env python

from consumer import app
from celery import group
import datetime
import random
import shutil
import drive
import db
import os

# Set size of chunks
n = int(os.getenv('CHUNK_SIZE'))

def produce():
	# Name of temporary local directory where images are saved to
	filename = f'''{datetime.datetime.now().strftime('%Y%m%dT%H%M%S')}'''
	dirname = os.path.join(os.getcwd(), filename)
	# Initialize db object
	adb = db.arangodb()
	# Initialize drive object
	gd = drive.gdrive()
	# If directory exists, delete it
	if os.path.exists(dirname):
		shutil.rmtree(dirname)
	# Make a temp directory
	os.mkdir(dirname)
	# Retrieve links from 'cameras' collection in database
	docs = adb.get_docs('cameras')
	random.shuffle(docs)
	# Chunk the docs into n-long groups
	chunked_docs = [docs[i:i+n] for i in range(0, len(docs), n)]
	# Push to queue and wait for all tasks to complete
	jobs = group([app.send_task('scrape', (dirname, chunk), kwargs={'timeout':1800}) for chunk in chunked_docs]).apply_async() # .apply_async() raises an error in the drain_events_until method in celery.backends.asynchronous
	results = jobs.join()
	# After queue is done, zip, upload to google drive, and delete locally
	shutil.make_archive(filename, 'zip', dirname)
	# Upload zip to Google Drive
	gd.upload(f'{filename}.zip', mimetype='application/zip')
	# Delete local directory
	shutil.rmtree(dirname)

def schedule():
	# Scrape indefinitely
	while True:
		produce()
		# Sleep for a minute, and start again
		time.sleep(60)

if __name__ == '__main__':
	schedule()
