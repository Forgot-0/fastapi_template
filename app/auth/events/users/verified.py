from dataclasses import dataclass

from app.core.events.event import BaseEvent, BaseEventHandler
from app.core.services.mail.service import EmailData, MailServiceInterface
from app.core.services.queue.service import QueueServiceInterface


@dataclass(frozen=True)
class VerifiedUserEvent(BaseEvent):
    user_id: int
    email: str

    __event_name__: str = "user_verified"


@dataclass(frozen=True)
class VerifiedUserEventHandler(BaseEventHandler[VerifiedUserEvent, None]):
    mail_service: MailServiceInterface
    queue_service: QueueServiceInterface

    async def handle(self, event: VerifiedUserEvent) -> None:
        email_data = EmailData(subject='Email verified successfully', recipient=event.email)
        
        # For now, send a simple confirmation email
        await self.mail_service.send_plain(
            subject=email_data.subject,
            recipient=email_data.recipient,
            body=f"Hello! Your email {event.email} has been successfully verified."
        )