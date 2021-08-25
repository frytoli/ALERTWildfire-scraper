#!/usr/bin/env python

import producer
import time

if __name__ == '__main__':
    # Start by sleeping an hour (twitter producer will run by default first)
    time.sleep(3600)
    # Scrape once every hour
    while True:
        # Start producer
        producer.produce('hourly')
        # Chill
        time.sleep(3600)
