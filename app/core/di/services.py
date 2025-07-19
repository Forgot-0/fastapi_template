from dishka import Provider, Scope, provide
from taskiq import AsyncBroker

from app.core.configs.app import AppConfig
from app.core.services.mail.service import MailServiceInterface
from app.core.services.mail.aiosmtplib.service import AioSmtpLibMailService
from app.core.services.queue.service import QueueServiceInterface
from app.core.services.queue.taskiq.service import TaskiqQueueService
from app.core.services.queue.taskiq.init import broker
from app.core.services.log.service import LogService


class ServiceProvider(Provider):
    scope = Scope.APP

    @provide
    def taskiq_broker(self) -> AsyncBroker:
        """Provide the Taskiq broker."""
        return broker

    @provide
    def queue_service(self, taskiq_broker: AsyncBroker) -> QueueServiceInterface:
        """Provide TaskiqQueueService with the broker."""
        return TaskiqQueueService(broker=taskiq_broker)

    @provide
    def mail_service(self, queue_service: QueueServiceInterface) -> MailServiceInterface:
        """Provide AioSmtpLibMailService with queue service dependency."""
        return AioSmtpLibMailService(queue_service=queue_service)

    @provide
    def log_service(self, config: AppConfig) -> LogService:
        """Provide logging service."""
        return LogService(
            level=config.LOG_LEVEL,
            handlers=config.LOG_HANDLERS,
        )