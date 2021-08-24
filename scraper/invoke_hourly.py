#!/usr/bin/env python

import producer
import time

if __name__ == '__main__':
    # Scrape once every hour
    while True:
        # Start producer
        producer.produce('hourly')
        # Chill
        time.sleep(3600)
