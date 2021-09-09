#!/usr/bin/env python

from celery import Celery
import os

app = Celery(
	'infrared',
	broker=f'''amqp://{os.getenv('RABBITMQ_DEFAULT_USER')}:{os.getenv('RABBITMQ_DEFAULT_PASS')}@{os.getenv('RABBITMQ_HOST')}:{os.getenv('RABBITMQ_PORT')}''',
	backend='rpc://redisir:6379',
	include=['distributed.consumer']
)

if __name__ == '__main__':
	app.start()
