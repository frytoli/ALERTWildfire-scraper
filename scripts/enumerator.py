#!/usr/bin/python3

'''
One-time enumerator to scrape and save camera URLs to database
Last updated: 2021-09-07
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

    def insert_camera(self, axis, url):
        aql = '''
            INSERT @doc INTO cameras
        '''
        bindVars = {
            'doc': {
                'axis':axis,
                'url':url,
                'timestamp':datetime.datetime.utcnow().isoformat()
            }
        }
        self.db.AQLQuery(aql, bindVars=bindVars)

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
    # Initialize HTML session
    session = HTMLSession()
    # Iterate over regions and collect/save camera urls
    for region in regions:
        print(f'[-] Retrieving cameras in {region}')
        region_url = f'{root_url}{region}/index.html'
        # Request page and render JS
        r = session.get(region_url, headers={'User-Agent':ua})
        r.html.render()
        # Find camera axis
        block = r.html.find('#thumbnail-block', first=True)
        thumbnails = block.find('div')
        # Iterate over thumbnails, craft urls, and save to database
        for elem in thumbnails:
            if elem.attrs['class']:
                axis = elem.find('p', first=True).attrs['id'].strip().replace('-label', '')
                camera_url = f'{region_url}?camera={axis}'
                # Save to database
                axis = f'{region}.{axis}'
                adb.insert_camera(axis, camera_url)
                print(f'  [+] Camera {axis} saved')
        time.sleep(random.randint(4,20))
    session.close()

if __name__ == '__main__':
    enumerate()
