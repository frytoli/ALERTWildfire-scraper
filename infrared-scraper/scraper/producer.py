#!/usr/bin/env python

from distributed.consumer import scrape
from requests_html import HTMLSession
import datetime
import time
import re
import db
import os

WAIT_SECS = 15

def get_proxies():
	'''
		Fetch a free list of proxies from Proxyscrape.com

		Returns:
			(list(str)) A list of valid proxy:port pair strings
	'''
	# Initialize HTML session
	session = HTMLSession()
	# Request data from proxyscrape API
	try:
		api_resp = session.get(
			'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all',
			timeout=30
		).text
	except Exception as e:
		# If there's an error, sleep and try again
		time.sleep(random.randint(3,6))
		try:
			api_resp = session.get(
				'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all',
				timeout=30
			).text
		except Exception as e:
			api_resp = None
	# Close session
	session.close()
	# If a good response was retrieved, process the list
	if api_resp:
		# Split response blob into proxy ip:port pairs
		pairs = api_resp.split('\r\n')
		# Remove empty values or mis-structured values
		good_pairs = [x for x in pairs if (x != '' and x.count('.') == 3)]
	# Otherwise, return an empty list
	else:
		good_pairs = []
	# Return good proxy pairs
	return good_pairs

def produce():
	# Make temp directory for image downloads
	tempdir = os.path.join(os.getcwd(), 'temp')
	if not os.path.exists(tempdir):
		os.mkdir(tempdir)
	# Compile epoch time regex pattern
	epoch_ptrn = re.compile(r'[0-9]{10,}')
	# Initialize db object
	adb = db.arangodb()
	# Retrieve last scraped pages of each infrared camera
	docs = adb.get_docs('ir-cameras')
	# Get initial proxy list
	proxies = get_proxies()
	# If request to proxyscrape was bad, sleep and try again
	if len(proxies) < 1:
		# Sleep randomly
		time.sleep(random.randint(13,30))
		# Try again
		proxies = get_proxies()
	# Set timer for proxies
	proxytime = time.time()
	# Generate 15 second increment urls up to the current time for each camera
	while True:
		# Check if it's time for new proxies (15 minutes have passed), and if so fetch some and reset the proxy timer
		if time.time()-proxytime > 900:
			proxies = get_proxies()
			# If request to proxyscrape was bad, sleep and try again
			if len(proxies) < 1:
				# Sleep randomly
				time.sleep(random.randint(13,30))
				# Try again
				proxies = get_proxies()
			proxytime = time.time()
		# Placeholder for incremented docs
		inc_docs = []
		# Iterate over returned docs
		for doc in docs:
			# If the image exists (aka it's epoch time < current epoch time), push it to the queue
			if doc['epoch'] < int(datetime.datetime.now().timestamp()):
				scrape.delay(proxies, tempdir, doc['_id'], doc['axis'], doc['url'], doc['epoch'])
			# Otherwise, wait 15 seconds and push it to the queue
			else:
				time.sleep(WAIT_SECS)
				scrape.delay(proxies, tempdir, doc['_id'], doc['axis'], doc['url'], doc['epoch'])
			# Update doc's epoch time by 15 seconds
			doc['epoch'] = doc['epoch']+15
			doc['url'] = epoch_ptrn.sub(str(doc['epoch']), doc['url'])
			inc_docs.append(doc)
		# Update docs
		docs = inc_docs.copy()

if __name__ == '__main__':
	produce()
