from dishka import Provider, Scope, provide, from_context

from app.core.configs.app import AppConfig
from app.core.services.mail.service import MailServiceInterface
from app.core.services.mail.aiosmtplib.service import AioSmtpMailService
from app.core.services.queue.service import QueueServiceInterface
from app.core.services.queue.taskiq.service import TaskiqQueueService
from app.core.services.log.service import LogService


class ServiceProvider(Provider):
    scope = Scope.APP

    @provide
    def mail_service(self, config: AppConfig) -> MailServiceInterface:
        return AioSmtpMailService(
            smtp_host=config.SMTP_HOST,
            smtp_port=config.SMTP_PORT,
            smtp_user=config.SMTP_USER,
            smtp_password=config.SMTP_PASSWORD,
            smtp_tls=config.SMTP_TLS,
            smtp_ssl=config.SMTP_SSL,
            sender_address=config.EMAIL_SENDER_ADDRESS,
            sender_name=config.EMAIL_SENDER_NAME,
        )

    @provide
    def queue_service(self, config: AppConfig) -> QueueServiceInterface:
        return TaskiqQueueService(
            broker_url=config.QUEUE_REDIS_BROKER_URL,
            result_backend=config.QUEUE_REDIS_RESULT_BACKEND,
        )

    @provide
    def log_service(self, config: AppConfig) -> LogService:
        return LogService(
            level=config.LOG_LEVEL,
            handlers=config.LOG_HANDLERS,
        )