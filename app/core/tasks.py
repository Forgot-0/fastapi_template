from taskiq import AsyncBroker

from app.auth.tasks import register_auth_tasks


def register_tasks(broker: AsyncBroker) -> None:

    register_auth_tasks(broker)
