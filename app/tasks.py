from apphelpers.utilities.email import send_email
from celery import Celery
import jinja2
import logging

import app.signals as signals
import settings

RETRY_DELAY = 60  # every 30 sec
RETRIES = (60 * 60) / RETRY_DELAY  # 1 hour of retries

queue = Celery(
    'Queue',
    broker='redis://{}:{}/0'.format(settings.TASKQ_HOST, settings.TASKQ_PORT)
)

logging.basicConfig(filename='logs/tasks.log', level=logging.DEBUG)


@queue.task(autoretry_for=(Exception,), max_retries=RETRIES, default_retry_delay=RETRY_DELAY)
def notify_commentor(email_id, **email_info):
    html = jinja2.Environment(
        loader=jinja2.FileSystemLoader(
            settings.ARTICLE_EMAIL_TEMPLATE_DIR + '/')
    ).get_template(email_info['template_name'] + '.html'
                   ).render(data=email_info['template_data'])

    sender = settings.EMAIL_NOTIFICATION_SENDER
    subject = settings.ARTICLE_EMAIL_SUBJECT_PREFIX + email_info['mail_subject']

    try:
        send_email(sender, recipient=email_id, subject=subject, html=html)
        logging.info('{} mail sent to {}'.format(
            email_info['template_name'], email_id))
    except Exception as e:
        logging.info(e)


@signals.send_notification.connect
def on_send_notification(email_id, **email_info):
    notify_commentor.apply_async(email_id, email_info)
