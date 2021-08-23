#!/usr/bin/env python

from requests_html import HTMLSession
from consumer import scrape
import datetime
import random
import shutil
import drive
import time
import db
import os

def get_proxies():
    user_agents = [
    	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    	'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0',
    	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393',
    	'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)',
    	'Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)',
    	'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)',
    	'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0;  Trident/5.0)',
    	'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0; MDDCJS)',
    	'Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko'
    ]
    # Initialize HTML session
    session = HTMLSession()
    # Request data from proxyscrape API
    api_resp = session.get(
        'https://api.proxyscrape.com/?request=getproxies&proxytype=https&timeout=10000&country=all',
        headers={'User-Agent':random.choice(user_agents)}
    ).text
    # Split response blob into proxy ip:port pairs
    pairs = api_resp.split('\r\n')
    # Remove empty values or mis-structured values
    good_pairs = [x for x in pairs if (x != '' and x.count('.') == 3)]
    # Return good proxy pairs
    return good_pairs

def produce():
    # Name of temporary local directory where images are saved to
    dirname = os.path.join(os.getcwd(), 'images')
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
    # Fetch proxies
    proxies = get_proxies()
    # Push to queue
    for doc in docs:
        scrape.delay(dirname, doc['id'], doc['url'], proxies)
    # After queue is done, zip, upload to google drive, and delete locally
    filename = f'''{datetime.datetime.now().strftime('%Y%m%d')}'''
    shutil.make_archive(filename, 'zip', dirname)
    # Upload zip to Google Drive
    gd.upload(f'{filename}.zip', mimetype='application/zip')
    # Delete local directory
    shutil.rmtree(dirname)
