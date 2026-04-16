from taskiq import AsyncBroker

from app.auth.tasks import register_auth_tasks
from app.core.services.mail.aiosmtplib.task import SendEmail

def register_tasks(broker: AsyncBroker) -> None:
    broker.register_task(
        SendEmail.run,
        task_name=SendEmail.get_name()
    )

    register_auth_tasks(broker)
