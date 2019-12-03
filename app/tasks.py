from apphelpers.utilities.email import send_email
from celery import Celery
import jinja2
import logging

from app.libs import member as memberlib
from app.libs import asset as assetlib
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

    def send_comment_notification(commenter_email, subject, template, template_data):
        html = template_env.get_template(template).render(data=template_data)
        sender = settings.EMAIL_NOTIFICATIONS.SENDER
        subject = settings.EMAIL_NOTIFICATIONS.PREFIX + subject
        send_email(sender, recipient=commenter_email, subject=subject, html=html)
        logging.info('{} mail sent to {}'.format(template, commenter_email))

    @queue.task(autoretry_for=(Exception,), max_retries=5, default_retry_delay=RETRY_DELAY)
    @signals.comment_approved.connect
    @signals.comment_featured.connect
    def on_comment_action(action, comment):
        commenter = memberlib.get(comment['commenter']['id'])
        commenter_email = commenter['email']

        asset = assetlib.get(comment['asset'])
        asset_url = asset['url']

        comment_content = comment['content']
        comment_preview = comment_content[:215] + \
            '...' if len(comment_content) > 215 else comment_content

        subject = f'Comment {action.title()}'
        template = f'comment_{action}.html'

        send_comment_notification(
            commenter_email,
            subject=subject,
            template=template,
            template_data=dict(
                comment=comment_preview,
                comment_id=comment['id'],
                asset_url=asset_url
            )
        )
