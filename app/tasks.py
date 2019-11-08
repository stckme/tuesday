from celery import Celery

import settings

queue = Celery(
    'Queue',
    broker='redis://{}:{}/0'.format(settings.TASKQ_HOST, settings.TASKQ_PORT)
)
