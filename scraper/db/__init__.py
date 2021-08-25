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

    def get_docs(self, collection, tweetid=0):
        '''
            Fetch documents from database with optional time range filtering
        '''
        bindVars = {'@collection': collection}
        if tweetid:
            starttime = (datetime.datetime.utcnow() - datetime.timedelta(seconds=secsdelta)).isoformat
            aql = '''
                FOR doc IN @@collection
                    FILTER doc.tweetid > @tweetid
                    RETURN doc
            '''
            bindVars['tweetid'] = tweetid
        else:
            aql = '''
                FOR doc IN @@collection
                    RETURN doc
            '''
        return list(self.db.AQLQuery(aql, bindVars=bindVars, rawResults=True))

    def insert_doc(self, collection, doc):
        '''
            Insert a document into a collection
        '''
        bindVars = {
            '@collection': collection,
            'doc': doc
        }
        aql = '''
            INSERT @doc INTO @@collection
        '''
        return self.db.AQLQuery(aql, bindVars=bindVars)
