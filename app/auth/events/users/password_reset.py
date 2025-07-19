from dataclasses import dataclass

from app.core.events.event import BaseEvent, BaseEventHandler
from app.core.services.mail.service import EmailData, MailServiceInterface
from app.core.services.queue.service import QueueServiceInterface


@dataclass(frozen=True)
class PasswordResetEvent(BaseEvent):
    user_id: int
    email: str
    reset_token: str

    __event_name__: str = "password_reset"


@dataclass(frozen=True)
class PasswordResetEventHandler(BaseEventHandler[PasswordResetEvent, None]):
    mail_service: MailServiceInterface
    queue_service: QueueServiceInterface

    async def handle(self, event: PasswordResetEvent) -> None:
        email_data = EmailData(subject='Password reset request', recipient=event.email)
        
        # For now, send a simple reset email
        reset_body = f"""
        Hello!
        
        You have requested a password reset for your account.
        Your reset token is: {event.reset_token}
        
        If you did not request this reset, please ignore this email.
        """
        
        await self.mail_service.send_plain(
            subject=email_data.subject,
            recipient=email_data.recipient,
            body=reset_body
        )