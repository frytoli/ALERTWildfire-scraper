#!/usr/bin/env python

from pyArango.connection import *
import datetime
import uuid
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

    def get_docs(self, collection, secsdelta=None):
        '''
            Fetch documents from database with optional time range filtering
        '''
        bindVars = {'@collection': collection}
        if secsdelta:
            starttime = (datetime.datetime.utcnow() - datetime.timedelta(seconds=secdelta)).isoformat
            aql = '''
                FOR doc IN @@collection
                    FILTER doc.timestamp > @starttime
                    RETURN doc
            '''
            bindVars['starttime'] = starttime
        else:
            aql = '''
                FOR doc IN @@collection
                    RETURN doc
            '''
        return self.db.AQLQuery(aql, bindVars=bindVars)
