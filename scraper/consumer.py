#!/usr/bin/env python

from requests.exceptions import ConnectionError, ProxyError, TooManyRedirects
from requests_html import HTMLSession, AsyncHTMLSession
from pyppeteer.errors import TimeoutError
from lxml.etree import ParserError
from celery import Celery
import random
import time
import os

app = Celery(
	'consumer',
	broker=f'''amqp://{os.getenv('RABBITMQ_DEFAULT_USER')}:{os.getenv('RABBITMQ_DEFAULT_PASS')}@{os.getenv('RABBITMQ_HOST')}:{os.getenv('RABBITMQ_PORT')}''',
	backend='rpc://redis:6379'
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
	api_resp = session.get(
		'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all'
	).text
	# Split response blob into proxy ip:port pairs
	pairs = api_resp.split('\r\n')
	# Remove empty values or mis-structured values
	good_pairs = [x for x in pairs if (x != '' and x.count('.') == 3)]
	# Close session
	session.close()
	# Return good proxy pairs
	return good_pairs

def make_afunc(asession, id, url, proxy, headers={}, render=False):
	'''
		Dynamically build an asynchronous function at runtime for use by requests-html's AsyncHTMLSession's run() method

		Args:
			asession: (AsyncHTMLSession) the AsyncHTMLSession object
			id: (str) the document's id
			url: (str) the docuemnt's url to the camera
			proxy: (str) a proxy:port pair
			headers: (dict) (optional) dictionary of desired request headers
			render: (bool) (optional) indicator to render (or not) the javascript of the request's returned html

		Returns:
			asynchronous function
				Returns:
					(requests-html response object)
					(str) the document's id
					(str) the docuemnt's url to the camera
					(str) the provided proxy:port pair
	'''
	async def _afunction():
		try:
			# Add headers if applicable
			if len(headers) > 0:
				r = await asession.get(
					url,
					proxies={
						'http':f'http://{proxy}',
						'https':f'https://{proxy}'
					},
					headers=headers
				)
			else:
				r = await asession.get(
					url,
					proxies={
						'http':f'http://{proxy}',
						'https':f'https://{proxy}'
					},
				)
			# Render JS (This can raise a pyppeteer TimeoutError)
			if render and r:
				await r.html.arender(timeout=20)
		except (ConnectionError, ProxyError, TooManyRedirects, TimeoutError, ParserError):
			r = None
		return r, id, url, proxy
	return _afunction

@app.task(name='scrape')
def scrape(saveto_dir, docs, timeout=3000):
	'''
		Asynchronous scrape and save images from a group of camera urls

		Args:
			saveto_dir: (str) path to the directory where the images are to be saved
			docs: (list(dic())) a list of json documents with keys "id" and "url"
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
	# Sleep randomly
	time.sleep(random.randint(15,30))
	# Fetch proxies
	proxies = get_proxies()
	# Initialize step vars
	active = {doc['id']: {'url': doc['url'], 'proxy': None, 'step':1, 'tries':0} for doc in docs}
	# Initialize Async HTML session
	asession = AsyncHTMLSession() #(browser_args=['--proxy-server={proxy}'])
	# Loop until all good responses are found
	while len(active) > 0 and elapsed < timeout:
		# Shuffle proxies
		random.shuffle(proxies)
		# Craft dynamic arguments for async session
		aargs = []
		for id in active:
			camera = active[id]
			if camera['step'] == 1: # Step 1
				proxy = random.choice(proxies)
				# Make async function for initial page request
				aargs.append(make_afunc(asession, id, camera['url'], proxy, render=True))
			elif camera['step'] == 2: # Step 2
				# Make async function for image page request
				aargs.append(make_afunc(asession, id, camera['url'], camera['proxy'], headers={'Referer': 'http://www.alertwildfire.org/'}))
		# Make async requests and pair with id
		results = asession.run(*aargs)
		# Iterate over results and complete tasks per step if previous request was successful
		for result in results:
			# Parse result
			r = result[0]
			id = result[1]
			url = result[2]
			proxy = result[3]
			step = active[id]['step']
			if r and r.status_code in [200, 301, 302, 303, 307]:
				print(f'[-] Good response from {url}')
				# Step 1
				if step == 1:
					# Find direct image url
					src = r.html.find('.leaflet-image-layer', first=True).attrs['src']
					img = f'http:{src}'
					# Update record
					active[id]['url'] = img
					active[id]['proxy'] = proxy
					active[id]['step'] = 2
				# Step 2
				elif step == 2:
					# Save image to file
					with open(os.path.join(saveto_dir, f'{id}.jpg'), 'wb') as imgf:
						imgf.write(r.content)
					print(f'  [+] {id}.jpg saved')
					# Update record, aka remove it from the list of active tasks
					del active[id]
					# Close request object
					r.close()
			# If not successful
			else:
				print(f'[-] Bad response from {url}')
				# Step 1
				if step == 1:
					# Select a new proxy and update the record
					active[id]['proxy'] = random.choice(proxies)
				# Step 2
				elif step == 2:
					# Select a new proxy and update the record
					active[id]['proxy'] = random.choice(proxies)
					# Increment number of tries
					active[id]['tries'] += 1
					# If five tries have been made, demote the step back to step 1
					if active[id]['tries'] >= 5:
						active[id]['tries'] = 0
						active[id]['step'] = 1
			# Sleep randomly
			time.sleep(random.randint(3,18))
			# Update elapsed time
			elapsed = time.time()-start
	print(f'[-] Elapsed time: {elapsed}')
	# Close browser
	asession.close()
