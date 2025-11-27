from dataclasses import dataclass
from email.message import EmailMessage

import aiosmtplib

from app.core.configs.app import app_config
from app.core.configs.smtp import SMTPConfig
from app.core.services.mail.aiosmtplib.task import SendEmail
from app.core.services.mail.service import BaseMailService, EmailData
from app.core.services.mail.template import BaseTemplate
from app.core.services.queues.service import QueueResult, QueueServiceInterface


@dataclass
class AioSmtpLibMailService(BaseMailService):
    queue_service: QueueServiceInterface
    smtp_config: SMTPConfig

    async def send(self, template: BaseTemplate, email_data: EmailData) -> None:
        sender_name = email_data.sender_name or app_config.EMAIL_SENDER_NAME
        sender_address = email_data.sender_address or app_config.EMAIL_SENDER_ADDRESS

        message = EmailMessage()
        message["From"] = f"{sender_name} <{sender_address}>"
        message["To"] = email_data.recipient
        message["Subject"] = f"{app_config.PROJECT_NAME} | {email_data.subject}"
        message.add_alternative(template.render(), subtype="html")

        await aiosmtplib.send(message, **self.smtp_config)

    async def queue(self, template: BaseTemplate, email_data: EmailData)  -> str:
        return await self.queue_service.push(
            task=SendEmail,
            data={"content": template.render(), "email_data": email_data},
        )

    async def send_plain(self, subject: str, recipient: str, body: str) -> None:
        """Просто отправляем письмо без шаблона, сразу."""
        message = EmailMessage()
        sender_name = app_config.EMAIL_SENDER_NAME
        sender_address = app_config.EMAIL_SENDER_ADDRESS

        message["From"] = f"{sender_name} <{sender_address}>"
        message["To"] = recipient
        message["Subject"] = f"{app_config.PROJECT_NAME} | {subject}"
        message.set_content(body)

        await aiosmtplib.send(message, **self.smtp_config)

    async def queue_plain(self, subject: str, recipient: str, body: str) -> str:
        """Ставим задачу в очередь на отправку письма без шаблона."""
        email_data = {
            "subject": subject,
            "recipient": recipient,
            "sender_name": app_config.EMAIL_SENDER_NAME,
            "sender_address": app_config.EMAIL_SENDER_ADDRESS,
        }
        return await self.queue_service.push(
            task=SendEmail,
            data={"content": body, "email_data": email_data}
        )

