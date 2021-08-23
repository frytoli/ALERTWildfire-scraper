#!/usr/bin/env python

from celery import Celery
import os

app = Celery(
    'consumer',
    broker=f'''amqp://{os.getenv('RABBITMQ_DEFAULT_USER')}:{os.getenv('RABBITMQ_DEFAULT_PASS')}@{os.getenv('RABBITMQ_HOST')}:{os.getenv('RABBITMQ_PORT')}''',
    backend='rpc://redis:6379'
)

@app.task
def scrape(saveto_dir, id, url, proxies):
    print('woot')
    # Scrape and save image
