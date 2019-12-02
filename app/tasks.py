from apphelpers.utilities.email import send_email
from celery import Celery
import jinja2
import logging

import app.signals as signals
import settings

RETRY_DELAY = 60  # every 60 sec
RETRIES = (60 * 60) / RETRY_DELAY  # 1 hour of retries

queue = Celery(
    'Queue',
    broker='redis://{}:{}/0'.format(settings.TASKQ_HOST, settings.TASKQ_PORT)
)

logging.basicConfig(filename='logs/tasks.log', level=logging.DEBUG)


if settings.EMAIL_NOTIFICATIONS.ENABLED:

    template_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(settings.EMAIL_NOTIFICATIONS.TEMPLATE_DIR))

    def send_comment_notification(commenter_email, subject, template, comment):
        html = template_env.get_template(template + '.html').render(comment=comment)

        sender = settings.EMAIL_NOTIFICATIONS.SENDER
        subject = settings.EMAIL_NOTIFICATIONS.PREFIX + email_info['mail_subject']

        send_email(sender, recipient=commenter_email, subject=subject, html=html)
        logging.info('{} mail sent to {}'.format( email_info['template_name'], email_id))


    @queue.task(autoretry_for=(Exception,), max_retries=5, default_retry_delay=RETRY_DELAY)
    @signals.comment_approved.connect
    @signals.comment_featured.connect
    def on_comment_action(action, comment, commenter):
        email = commenter['email']
        comment_preview = comment[:215] + '...' if len(comment) > 215 else comment
        subject = f'Comment {action.title()}'
        template = f'comment_{action}.html'
        send_comment_notification(email, subject=subject, template=template,
                                  comment=comment_preview)
