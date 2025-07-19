from dataclasses import dataclass
from email.message import EmailMessage
from typing import Optional

import aiosmtplib

from app.core.services.mail.service import EmailData, MailServiceInterface
from app.core.services.mail.template import BaseTemplate
from app.core.services.queue.service import QueueResult, QueueServiceInterface


@dataclass
class AioSmtpMailService(MailServiceInterface):
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_tls: bool = True
    smtp_ssl: bool = False
    sender_address: Optional[str] = None
    sender_name: Optional[str] = None

    def __post_init__(self):
        """Initialize SMTP configuration."""
        self.smtp_config = {
            'hostname': self.smtp_host,
            'port': self.smtp_port,
            'username': self.smtp_user,
            'password': self.smtp_password,
            'use_tls': self.smtp_tls,
            'start_tls': not self.smtp_ssl,
        }

    async def send(self, template: BaseTemplate, email_data: EmailData) -> None:
        """Send email using template."""
        sender_name = email_data.sender_name or self.sender_name
        sender_address = email_data.sender_address or self.sender_address

        message = EmailMessage()
        message['From'] = f'{sender_name} <{sender_address}>'
        message['To'] = email_data.recipient
        message['Subject'] = email_data.subject
        message.add_alternative(template.render(), subtype='html')

        await aiosmtplib.send(message, **self.smtp_config)

    async def queue(self, template: BaseTemplate, email_data: EmailData) -> QueueResult | None:
        """Queue email for later sending (requires queue_service injection)."""
        # This would need to be injected separately or use a different pattern
        # For now, we'll send immediately
        await self.send(template, email_data)
        return QueueResult(response="sent_immediately", status=0)
    
    async def send_plain(self, subject: str, recipient: str, body: str) -> None:
        """Send plain text email."""
        message = EmailMessage()
        sender_name = self.sender_name
        sender_address = self.sender_address

        message["From"] = f"{sender_name} <{sender_address}>"
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(body)

        await aiosmtplib.send(message, **self.smtp_config)

    async def queue_plain(self, subject: str, recipient: str, body: str) -> None:
        """Queue plain text email for later sending."""
        # For now, send immediately
        await self.send_plain(subject, recipient, body)

