#!/usr/bin/env python

from celery.app.control import inspect
import producer

if __name__ == '__main__':
    # Scrape once every hour
    while True:
        # Look for pending tasks (from tweet invoke-r)
        i = inspect(['consumer'])
        if len(i.registered()) == 0 and len(i.scheduled()) == 0 and len(i.reserved()) == 0:
            # Start producer
            producer.produce()
        # Chill
        time.sleep(3600)
