from taskiq import AsyncBroker

from app.auth.tasks import RemoveInactiveTokens
from app.core.services.mail.aiosmtplib.task import SendEmail


def register_tasks(broker: AsyncBroker) -> None:
    broker.register_task(
        RemoveInactiveTokens.run,
        task_name=RemoveInactiveTokens.get_name(),
        schedule=[{"cron": "0 0 * * *"}],
    )
    broker.register_task(
        SendEmail.run,
        task_name=SendEmail.get_name()
    )