#!/usr/bin/env python

import producer
import time
import db

if __name__ == '__main__':
    # Initialize db object
    adb = db.arangodb()
    # Set temp last tweet id
    lasttweetid = 0
    # Check for new tweets once every 15 minutes
    while True:
        # Pull newest tweets by id
        docs = adb.get_docs('tweets', tweetid=lasttweetid)
        if len(docs) > 0:
            # Sort tweets by id (larger id is more recent)
            docs = sorted(docs, key=lambda k: k['id'], reverse=True)
            # Set new last tweet id
            lasttweetid = docs[0]['id']
            # Start producer
            ids = [doc['id'] for doc in docs]
            producer.produce('tweet', tweet_ids=ids)
        # Chill for 15 minutes
        time.sleep(900)
