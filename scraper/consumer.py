#!/usr/bin/env python

from requests.exceptions import ConnectionError, ProxyError
from requests_html import HTMLSession
from celery import Celery
import logging
import random
import time
import os

app = Celery(
    'consumer',
    broker=f'''amqp://{os.getenv('RABBITMQ_DEFAULT_USER')}:{os.getenv('RABBITMQ_DEFAULT_PASS')}@{os.getenv('RABBITMQ_HOST')}:{os.getenv('RABBITMQ_PORT')}''',
    backend='rpc://redis:6379'
)

@app.task
def scrape(saveto_dir, id, url, proxies):
    '''
        Scrape and save image from a camera url
    '''
    logging.info(f'[-] Now scraping {url}')
    # Sleep randomly
    time.sleep(random.randint(5,25))
    # Select proxy pair
    proxy = random.choice(proxies)
    # Initialize HTML session
    session = HTMLSession()
    # Request page and render JS
    try:
        r = session.get(
            url,
            proxies={
                'http':f'http://{proxy}',
                'https':f'https://{proxy}'}
        )
    except (ConnectionError, ProxyError):
        r = None
    while not r or r.status_code not in [200, 301, 302, 303, 307]:
        # Select another proxy pair
        proxy = random.choice(proxies)
        # Sleep for short, random time
        time.sleep(random.randint(3,13))
        try:
            r = session.get(
                url,
                proxies={
                    'http':f'http://{proxy}',
                    'https':f'https://{proxy}'}
            )
        except (ConnectionError, ProxyError):
            r = None
    r.html.render()
    logging.info(f'  [-] Page rendered')
    # Find camera image source
    src = r.html.find('.leaflet-image-layer', first=True).attrs['src']
    img = f'http:{src}'
    logging.info(f'  [-] Image found at {img}')
    # Sleep for short, random time
    time.sleep(random.randint(3,13))
    # Download/save image
    # Include referer in header
    if 'https' in url:
        root_domain = f'''https://{url.replace('https://','').split('/')[0]}/'''
    elif 'http' in url:
        root_domain = f'''http://{url.replace('http://','').split('/')[0]}/'''
    else:
        logging.info('  [!] Incorrect protocol detected')
    headers = {'Referer': root_domain}
    try:
        r = session.get(
            img,
            headers=headers,
            proxies={
                'http':f'http://{proxy}',
                'https':f'https://{proxy}'
            }
        )
    except (ConnectionError, ProxyError) as e:
        r = None
    while not r or r.status_code != 200:
        # Select another proxy pair
        proxy = random.choice(proxies)
        # Sleep for short, random time
        time.sleep(random.randint(3,13))
        try:
            r = session.get(
                img,
                headers=headers,
                proxies={
                    'http':f'http://{proxy}',
                    'https':f'https://{proxy}'
                }
            )
        except (ConnectionError, ProxyError) as e:
            r = None
    with open(os.path.join(saveto_dir, f'{id}.jpg'), 'wb') as imgf:
        imgf.write(r.content)
    logging.info(f'  [+] Image saved')
