#!/usr/bin/env python

from celery import Celery
import os

app = Celery(
    'consumer',
    broker=f'''amqp://{os.getenv('RABBITMQ_USER')}:{os.getenv('RABBITMQ_PASS')}@rabbitmq:5672''',
    backend='rpc://redis:6379'
)

@app.task
def add(x, y):
    return x + y
