from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.core.services.mail.template import BaseTemplate
from app.core.services.queue.service import QueueResult


@dataclass
class EmailData:
    subject: str
    recipient: str
    sender_address: str | None = None
    sender_name: str | None = None


class BaseMailService(ABC):
    @abstractmethod
    async def send(self, template: BaseTemplate, email_data: EmailData) -> None:
        ...

    @abstractmethod
    async def queue(self, template: BaseTemplate, email_data: EmailData) -> QueueResult | None:
        ...

    @abstractmethod
    async def send_plain(self, subject: str, recipient: str, body: str) -> None:
        ...

    @abstractmethod
    async def queue_plain(self, subject: str, recipient: str, body: str) -> None:
        ...