from email.message import EmailMessage

import aiosmtplib

from app.core.configs.app import app_config
from app.core.services.queue.depends import get_queued_decorator
from app.core.services.queue.task import BaseTask
from app.core.services.mail.aiosmtplib.init import smtp_config

queued = get_queued_decorator()


@queued
class SendEmail(BaseTask):
    __task_name__ = 'mail.send'

    async def run(self, content: str, email_data: dict) -> None:
        sender_name = email_data['sender_name'] or app_config.EMAIL_SENDER_NAME
        sender_address = email_data['sender_address'] or app_config.EMAIL_SENDER_ADDRESS

        message = EmailMessage()
        message['From'] = f'{sender_name} <{sender_address}>'
        message['To'] = email_data['recipient']
        message['Subject'] = f'{app_config.PROJECT_NAME} | {email_data['subject']}'
        message.add_alternative(content, subtype='html')

        await aiosmtplib.send(message, **smtp_config)