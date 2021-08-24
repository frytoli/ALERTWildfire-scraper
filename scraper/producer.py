#!/usr/bin/env python

from requests_html import HTMLSession
from consumer import scrape
from celery import group
import datetime
import random
import shutil
import drive
import time
import db
import os

def get_proxies():
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
    # Return good proxy pairs
    return good_pairs

def produce(invoked, tweet_ids=None):
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
    # Fetch proxies
    proxies = get_proxies()
    # Push to queue and wait for all tasks to complete
    jobs = group([scrape(dirname, doc['id'], doc['url'], proxies) for doc in docs])
    results = jobs.apply_async()
    result = results.join()
    # After queue is done, zip, upload to google drive, and delete locally
    shutil.make_archive(filename, 'zip', dirname)
    # Upload zip to Google Drive
    gd.upload(f'{filename}.zip', mimetype='application/zip')
    # Delete local directory
    shutil.rmtree(dirname)
    # Log event
    adb.insert_doc('log', file=filename, invoked=invoked, tweets=tweet_ids)
