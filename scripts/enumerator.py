#!/usr/bin/python3

'''
One-time enumerator to scrape and save camera URLs to database
Last updated: 2021-08-20
'''

from requests_html import HTMLSession
from pyArango.connection import *
import datetime
import random
import time
import os

class arangodb():
    def __init__(self):
        DB_HOST = os.getenv('DB_HOST')
        DB_PORT = os.getenv('DB_PORT')
        DB_USER = os.getenv('DB_USER')
        DB_PASS = os.getenv('DB_PASS')
        DB_NAME = os.getenv('DB_NAME')
        self.db = Connection(
            arangoURL='http://{}:{}'.format(DB_HOST, DB_PORT),
            username=DB_USER,
            password=DB_PASS
        )[DB_NAME]

    def insert_camera(self, id, url):
        aql = '''
            INSERT @doc INTO cameras
        '''
        bindVars = {'doc': {'id':id, 'url':url, 'timestamp':datetime.datetime.utcnow().isoformat()}}
        self.db.AQLQuery(aql, bindVars=bindVars)

def select_ua():
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
    return random.choice(user_agents)

def enumerate():
    # Initialize db object
    adb = arangodb()
    # Set root url and regions
    root_url = 'http://www.alertwildfire.org/'
    regions = [
        'oregon',
        'shastamodoc',
        'northcoast',
        'blmnv',
        'utah',
        'tahoe',
        'northbay',
        'southeastbay',
        'sierra',
        'centralcoast',
        'orangecoca',
        'inlandempire',
        'sdge'
    ]
    random.shuffle(regions)
    # Select User Agent string
    ua = select_ua()
    # Initialize HTML session
    session = HTMLSession()
    # Iterate over regions and collect/save camera urls
    for region in regions:
        print(f'[-] Retrieving cameras in {region}')
        region_url = f'{root_url}{region}/index.html'
        # Request page and render JS
        r = session.get(region_url, headers={'User-Agent':ua})
        r.html.render()
        # Find camera ids
        block = r.html.find('#thumbnail-block', first=True)
        thumbnails = block.find('div')
        # Iterate over thumbnails, craft urls, and save to database
        for elem in thumbnails:
            if elem.attrs['class']:
                axis = elem.find('p', first=True).attrs['id'].strip().replace('-label', '')
                camera_url = f'{region_url}?camera={axis}'
                # Save to database
                docid = f'{region}.{axis}'
                docurl = f'{region_url}/?camera={axis}'
                adb.insert_camera(docid, docurl)
                print(f'  [+] Camera {docid} saved')
        time.sleep(random.randint(4,20))

if __name__ == '__main__':
    enumerate()
