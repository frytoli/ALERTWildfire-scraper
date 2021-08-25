#!/usr/bin/env python

from pyArango.connection import *
import datetime
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

    def insert_new_tweet(self, tweetid, text):
        '''
            Insert a new tweet document into the collection and ignore previously-seen tweets
        '''
        bindVars = {
            'tweetid': tweetid,
            'text': text,
            'timestamp': datetime.datetime.utcnow().isoformat()
        }
        aql = '''
            UPSERT { id: @tweetid }
            INSERT { id: @tweetid, text: @text, scrape_timestamp: @timestamp }
            UPDATE { } IN tweets

            RETURN { doc: NEW, type: OLD ? 'update' : 'insert' }
        '''
        return self.db.AQLQuery(aql, bindVars=bindVars)
