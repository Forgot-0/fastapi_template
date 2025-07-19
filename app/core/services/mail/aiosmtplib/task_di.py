from email.message import EmailMessage
from typing import Optional

import aiosmtplib

from app.core.configs.app import AppConfig
from app.core.services.queue.task import BaseTask
from app.core.services.mail.aiosmtplib.init import smtp_config


class SendEmailTask(BaseTask):
    """DI-aware SendEmail task that can receive configuration via dependency injection."""
    __task_name__ = 'mail.send'

    def __init__(self, config: Optional[AppConfig] = None):
        """Initialize with optional config injection."""
        self.config = config

    async def run(self, content: str, email_data: dict) -> None:
        """Send email using either injected config or global config."""
        # Use injected config or fall back to global config
        config = self.config or self._get_global_config()
        
        sender_name = email_data.get('sender_name') or config.EMAIL_SENDER_NAME
        sender_address = email_data.get('sender_address') or config.EMAIL_SENDER_ADDRESS

        message = EmailMessage()
        message['From'] = f'{sender_name} <{sender_address}>'
        message['To'] = email_data['recipient']
        message['Subject'] = f'{config.PROJECT_NAME} | {email_data["subject"]}'
        message.add_alternative(content, subtype='html')

        await aiosmtplib.send(message, **smtp_config)

    def _get_global_config(self) -> AppConfig:
        """Fallback to global config if DI is not available."""
        from app.core.configs.app import app_config
        return app_config


# For backward compatibility, keep your original approach available
def create_legacy_send_email_task():
    """Create the original SendEmail task without DI (for backward compatibility)."""
    from app.core.services.queue.depends import get_queued_decorator
    
    queued = get_queued_decorator()
    
    @queued
    class SendEmail(BaseTask):
        __task_name__ = 'mail.send'

        async def run(self, content: str, email_data: dict) -> None:
            from app.core.configs.app import app_config
            
            sender_name = email_data.get('sender_name') or app_config.EMAIL_SENDER_NAME
            sender_address = email_data.get('sender_address') or app_config.EMAIL_SENDER_ADDRESS

            message = EmailMessage()
            message['From'] = f'{sender_name} <{sender_address}>'
            message['To'] = email_data['recipient']
            message['Subject'] = f'{app_config.PROJECT_NAME} | {email_data["subject"]}'
            message.add_alternative(content, subtype='html')

            await aiosmtplib.send(message, **smtp_config)
    
    return SendEmail


# Function to register with DI
def register_send_email_with_di(di_decorator):
    """Register SendEmailTask with DI-aware decorator."""
    return di_decorator(SendEmailTask)