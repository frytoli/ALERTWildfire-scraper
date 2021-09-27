#!/usr/bin/env python

from pyArango.connection import *
from pyArango import theExceptions
from requests import exceptions
import datetime
import time
import os

class arangodb():
    def __init__(self):
        # Attempt to establish a connection
        self.db = None
        while not self.db:
            try:
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
            except (theExceptions.ConnectionError, exceptions.ConnectionError) as e:
                print(f'[!] Failed to establish a connection: {e}\n  [-] Trying again in 5 seconds')
                time.sleep(5)

    def update_epoch(self, id, url, epoch):
        '''
            Update infrared camera documents
        '''
        bindVars = {
            'id': id,
            'url': url,
            'epoch':int(epoch),
            'timestamp': datetime.datetime.utcnow().isoformat()
        }
        aql = '''
            FOR doc IN `ir-cameras`
                FILTER doc._id == @id
                UPDATE doc._key WITH { url: @url, epoch: @epoch, timestamp: @timestamp } IN `ir-cameras`
        '''
        return self.db.AQLQuery(aql, bindVars=bindVars)
