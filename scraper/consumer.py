#!/usr/bin/env python

from requests.exceptions import ConnectionError, ProxyError, TooManyRedirects
from requests_html import AsyncHTMLSession
from celery import Celery
import random
import time
import os

app = Celery(
	'consumer',
	broker=f'''amqp://{os.getenv('RABBITMQ_DEFAULT_USER')}:{os.getenv('RABBITMQ_DEFAULT_PASS')}@{os.getenv('RABBITMQ_HOST')}:{os.getenv('RABBITMQ_PORT')}''',
	backend='rpc://redis:6379'
)

def make_afunc(asession, id, url, proxy, headers={}, render=False):
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
			# Render JS
			if render:
				await r.html.arender(timeout=20)
		except (ConnectionError, ProxyError, TooManyRedirects):
			r = None
		return r, id, url, proxy
	return _afunction

@app.task
def scrape(saveto_dir, docs, proxies):
	'''
		Scrape and save image from a camera url
	'''
	print(f'[-] Now scraping {len(docs)} cameras')
	# Sleep randomly
	time.sleep(random.randint(15,30))
	# Initialize step vars
	active = {doc['id']: {'url': doc['url'], 'proxy': None, 'step':1} for doc in docs}
	# Initialize Async HTML session
	asession = AsyncHTMLSession() #(browser_args=['--proxy-server={proxy}'])
	# Loop until all good responses are found
	while len(active) > 0:
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
				print(f'  [-] Good response from {url}')
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
					print(f'    [+] {id}.jpg saved')
					# Update record, aka remove it from the
					del active[id]
			# If not successful
			else:
				print(f'  [-] Bad response from {url}')
				# Step 1
				if step == 1:
					# Select a new proxy and update the record
					active[id]['proxy'] = random.choice(proxies)
				# Step 2
				elif step == 2:
					# Select a new proxy and update the record
					active[id]['proxy'] = random.choice(proxies)
			# Sleep randomly
			time.sleep(random.randint(3,18))
	# Close browser
	asession.close()
