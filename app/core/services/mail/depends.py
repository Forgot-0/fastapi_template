from typing import Annotated

from fastapi import Depends

from app.core.services.mail.service import MailServiceInterface
from app.core.services.mail.aiosmtplib.service import AioSmtpLibMailService
from app.core.services.queue.depends import get_queue_service
from app.core.services.queue.service import QueueServiceInterface


def get_mail_service(
    queue_service: Annotated[QueueServiceInterface, Depends(get_queue_service)],
) -> MailServiceInterface:
    return AioSmtpLibMailService(queue_service)