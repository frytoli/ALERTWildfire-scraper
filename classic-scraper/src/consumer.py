#!/usr/bin/env python

#from requests.exceptions import ConnectionError, ProxyError, TooManyRedirects, ReadTimeout
#from asyncio.exceptions import CancelledError, InvalidStateError
#from lxml.etree import ParserError
#import pyppeteer

from requests_html import HTMLSession, AsyncHTMLSession
from celery import Celery
import asyncio
import random
import drive
import time
import os
import re

app = Celery(
	broker=f'''amqp://{os.getenv('RABBITMQ_USER')}:{os.getenv('RABBITMQ_PASS')}@{os.getenv('RABBITMQ_HOST')}:{os.getenv('RABBITMQ_PORT')}''',
	backend=f'''rpc://{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}''',
)

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

def make_afunc(asession, axis, url, proxy, headers={}, render=False):
	'''
		Dynamically build an asynchronous function at runtime for use by requests-html's AsyncHTMLSession's run() method

		Args:
			asession: (AsyncHTMLSession) the AsyncHTMLSession object
			axis: (str) the document's axis
			url: (str) the docuemnt's url to the camera
			proxy: (str) a proxy:port pair
			headers: (dict) (optional) dictionary of desired request headers
			render: (bool) (optional) indicator to render (or not) the javascript of the request's returned html

		Returns:
			asynchronous function
				Returns:
					(requests-html response object)
					(str) the document's axis
					(str) the docuemnt's url to the camera
					(str) the provided proxy:port pair
	'''
	async def _afunction():
		r = None
		try:
			# Add headers if applicable
			if len(headers) > 0:
				r = await asession.get(
					url,
					proxies={
						'http':f'http://{proxy}',
						'https':f'https://{proxy}'
					},
					headers=headers,
					timeout=30
				)
			else:
				r = await asession.get(
					url,
					proxies={
						'http':f'http://{proxy}',
						'https':f'https://{proxy}'
					},
					timeout=30
				)
			# Render JS (This can raise a pyppeteer TimeoutError)
			if render and r:
				await r.html.arender(timeout=30, sleep=random.randint(2,5))
		#except (AttributeError, ConnectionError, ProxyError, TooManyRedirects, ReadTimeout, pyppeteer.errors.TimeoutError, pyppeteer.errors.BrowserError, pyppeteer.errors.ConnectionError, ParserError, CancelledError, InvalidStateError) as e:
		except Exception as e:
			print(f'  [!] Error: {e}')
			r = None
		return r, axis, url, proxy
	return _afunction

@app.task(name='scrape-classic')
def scrape(folder_id, docs, timeout=3000):
	'''
		Asynchronous scrape and save images from a group of camera urls

		Args:
			saveto_dir: (str) path to the directory where the images are to be saved
			docs: (list(dic())) a list of json documents with keys "axis" and "url"
			timeout: (int) (optional) number of seconds until timeout; this defaults to 50 minutes, 10 minutes less than RabbitMQ's timeout

		Returns:
			None
	'''
	# Setup timer
	start = time.time()
	elapsed = time.time()-start
	# Ensure that timeout var is correct type
	if not (isinstance(timeout, int) or isinstance(timeout, int)):
		print('[!] Provided value for timeout is not int or float. Defaulting to timeout of 3000 seconds.')
		timeout = 3000
	# Initialize drive object
	gd = drive.gdrive()
	# Fetch proxies
	proxies = get_proxies()
	# If request to proxyscrape was bad, sleep and try again
	if len(proxies) < 1:
		# Sleep randomly
		time.sleep(random.randint(13,30))
		# Try again
		proxies = get_proxies()
	# Initialize step vars
	active = {doc['axis']: {'url': doc['url'], 'proxy': None, 'step':1, 'tries':0} for doc in docs}
	# Initialize temp Async HTML session
	asession = None
	# Loop until all good responses are found
	while len(active) > 0 and elapsed < timeout:
		# Sleep randomly
		time.sleep(random.randint(13,30))
		# Initialize Async HTML session (sometimes these break)
		if not asession:
			try:
				# Set existing event loop
				loop = asyncio.get_event_loop()
			except RuntimeError:
				# If no event loop exists, create/set a new one
				loop = asyncio.new_event_loop()
				asyncio.set_event_loop(loop)
			asession = AsyncHTMLSession(loop=loop)
		# Shuffle proxies
		random.shuffle(proxies)
		# Craft dynamic arguments for async session
		aargs = []
		for axis in active:
			camera = active[axis]
			if camera['step'] == 1: # Step 1
				proxy = random.choice(proxies)
				# Make async function for initial page request
				aargs.append(make_afunc(asession, axis, camera['url'], proxy, render=True))
			elif camera['step'] == 2: # Step 2
				# Make async function for image page request
				aargs.append(make_afunc(asession, axis, camera['url'], camera['proxy'], headers={'Referer': 'http://www.alertwildfire.org/'}))
		# Make async requests and pair with axis
		results = asession.run(*aargs)
		# Iterate over results and complete tasks per step if previous request was successful
		for result in results:
			# Parse result
			r = result[0]
			axis = result[1]
			url = result[2]
			proxy = result[3]
			step = active[axis]['step']
			if r and r.status_code in [200, 301, 302, 303, 307]:
				print(f'[-] Good response from {url}')
				# Step 1
				if step == 1:
					# Find direct image url
					img = r.html.find('.leaflet-image-layer', first=True).attrs['src']
					src = f'http:{img}'
					# Update record
					active[axis]['url'] = src
					active[axis]['proxy'] = proxy
					active[axis]['step'] = 2
					# Close request object
					r.close()
				# Step 2
				elif step == 2:
					# Save image to file
					filename = os.path.join('imgs', f'{axis}.jpg')
					with open(filename, 'wb') as imgf:
						imgf.write(r.content)
					# Upload file to Google Drive
					gd.upload(folder_id, filename, mimetype='image/jpg')
					print(f'  [+] {axis}.jpg uploaded to Drive')
					# Remove local file
					os.remove(filename)
					# Update record, aka remove it from the list of active tasks
					del active[axis]
					# Close request object
					r.close()
			# If not successful
			else:
				print(f'[-] Bad response from {url}')
				# Step 1
				if step == 1:
					# Select a new proxy and update the record
					active[axis]['proxy'] = random.choice(proxies)
					# Close request object
					if r:
						r.close()
				# Step 2
				elif step == 2:
					# Select a new proxy and update the record
					active[axis]['proxy'] = random.choice(proxies)
					# Increment number of tries
					active[axis]['tries'] += 1
					# If five tries have been made, demote the step back to step 1
					if active[axis]['tries'] >= 5:
						active[axis]['tries'] = 0
						active[axis]['step'] = 1
					# Close request object
					if r:
						r.close()
			# Update elapsed time
			elapsed = time.time()-start
	print(f'[-] Elapsed time: {elapsed}')
	# Close browser
	asyncio.run(asession.close())

@app.task(name='gdrive-mkdir')
def gdrive_mkdir(folder_name):
	# Initialize drive object
	gd = drive.gdrive()
	# Create a folder in the set parent directory
	id = gd.mkdir(folder_name)
	# Return
	return id
