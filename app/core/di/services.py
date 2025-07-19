from dishka import Provider, provide, Scope

from app.core.services.mail.service import MailServiceInterface
from app.core.services.mail.aiosmtplib.service import AioSmtpLibMailService
from app.core.services.queue.service import QueueServiceInterface
from app.core.services.queue.taskiq.service import TaskiqQueueService
from app.core.services.queue.taskiq.init import broker


class ServicesProvider(Provider):
    scope = Scope.APP

    @provide
    def get_queue_service(self) -> QueueServiceInterface:
        return TaskiqQueueService(broker)
    
    @provide
    def get_mail_service(self, queue_service: QueueServiceInterface) -> MailServiceInterface:
        return AioSmtpLibMailService(queue_service)