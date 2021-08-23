#!/usr/bin/env python

import producer
import db

if __name__ == '__main__':
    # Initialize db object
    adb = db.arangodb()
    # Check for new tweets once an hour
    while True:
        # Pull tweets from past 10 minutes
        docs = adb.get_docs('tweets', secsdelta=600)
        if len(docs) > 0:
            # Start producer
            producer.produce()
        # Chill
        time.sleep(600)
