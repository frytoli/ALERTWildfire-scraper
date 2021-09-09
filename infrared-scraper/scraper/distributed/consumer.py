#!/usr/bin/env python

#from requests.exceptions import ConnectionError, ProxyError, TooManyRedirects, ReadTimeout
#from asyncio.exceptions import CancelledError, InvalidStateError
#from lxml.etree import ParserError
#import pyppeteer

from requests_html import HTMLSession
from .celery import app
import random
import drive
import time
import os
import db

@app.task(name='scrape-ir')
def scrape_ir(proxies, saveto_dir, id, axis, url, epoch, timeout=600):
	'''
		Scrape and save image from a camera url

		Args:
			proxies: (list(str)) a list of proxy ip:port strings
			id: (str) a string document id from the database
			url: (str) a string url from which to scrape the image
			timeout: (int) (optional) an integer timeout value in seconds

		Returns:
			None
	'''
	print(f'[-] Now scraping {url}')
	# Setup timer
	start = time.time()
	elapsed = time.time()-start
	# Ensure that timeout var is correct type
	if not (isinstance(timeout, int) or isinstance(timeout, int)):
		print('[!] Provided value for timeout is not int or float. Defaulting to timeout of 600 seconds.')
		timeout = 600
	# Initialize a session
	session = HTMLSession()
	# Initialize an downloaded image toggle
	img_success = False
	# Set file name
	filename = os.path.join(saveto_dir, f'{axis}_{epoch}.jpg')
	# Loop until response is found
	while not img_success and elapsed < timeout:
		# Sleep randomly
		time.sleep(random.randint(13,30))
		# Select proxy
		proxy = random.choice(proxies)
		# Request page
		try:
			r = session.get(
				url,
				proxies={
					'http':f'http://{proxy}',
					'https':f'https://{proxy}'
				},
				headers={
					'Referer': 'http://beta.alertwildfire.org/'
				},
				timeout=30
			)
		except Exception as e:
			#print(f'  [!] Error {e}')
			r = None
		# If good response, save image
		if r and r.status_code in [200, 301, 302, 303, 307]:
			with open(filename, 'wb') as imgf:
				imgf.write(r.content)
			# Flip toggle
			img_success = True
			print(f'  [+] Image saved to {filename}')
		elapsed = time.time()-start
	# Close session
	session.close()
	# If file exists...
	if os.path.exists(filename):
		# Upload to Drive
		gd = drive.gdrive()
		gd.upload(filename, mimetype='image/jpg')
		print('  [+] Image uploaded to Drive')
		# Update database entry
		adb = db.arangodb()
		adb.update_epoch(id, url, epoch)
		# Delete local file
		os.remove(filename)
