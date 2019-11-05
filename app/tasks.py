from celery import Celery

import settings

queue = Celery(
    'Queue',
    broker='redis://{}:{}/0'.format(settings.REDIS_HOST, settings.REDIS_PORT)
)
