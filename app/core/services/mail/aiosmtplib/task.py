from email.message import EmailMessage

import aiosmtplib

from app.core.configs.app import app_config
from app.core.services.queue.depends import get_queued_decorator
from app.core.services.queue.task import BaseTask
from app.core.services.mail.aiosmtplib.init import smtp_config

# Option 1: Your original approach (works as before)
queued = get_queued_decorator()


@queued
class SendEmail(BaseTask):
    __task_name__ = 'mail.send'

    async def run(self, content: str, email_data: dict) -> None:
        sender_name = email_data.get('sender_name') or app_config.EMAIL_SENDER_NAME
        sender_address = email_data.get('sender_address') or app_config.EMAIL_SENDER_ADDRESS

        message = EmailMessage()
        message['From'] = f'{sender_name} <{sender_address}>'
        message['To'] = email_data['recipient']
        message['Subject'] = f'{app_config.PROJECT_NAME} | {email_data["subject"]}'
        message.add_alternative(content, subtype='html')

        await aiosmtplib.send(message, **smtp_config)


# Option 2: Function to register with DI system
def register_send_email_with_di():
    """Register SendEmail task with the DI system for enhanced capabilities."""
    from app.core.di import get_container
    from app.core.di.tasks import DIAwareTaskiqDecorator
    from app.core.services.mail.aiosmtplib.task_di import SendEmailTask
    from taskiq import AsyncBroker
    
    container = get_container()
    
    try:
        with container() as app_scope:
            broker = app_scope.get(AsyncBroker)
            
            # Create DI-aware decorator
            di_decorator = DIAwareTaskiqDecorator(broker, container)
            
            # Register DI-aware version alongside the original
            di_decorator(SendEmailTask)
            
            print("✅ SendEmail task registered with DI capabilities")
            
    except Exception as e:
        print(f"⚠️  Could not register SendEmail with DI: {e}")
        print("   Falling back to original task registration")


# Auto-register with DI if available
try:
    register_send_email_with_di()
except ImportError:
    # DI system not available, use original approach only
    pass