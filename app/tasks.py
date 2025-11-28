from dishka.integrations.taskiq import TaskiqProvider, setup_dishka
from taskiq import TaskiqEvents, TaskiqScheduler, TaskiqState
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_redis import RedisScheduleSource

from app.core.configs.app import app_config
from app.core.di.container import create_container
from app.core.message_brokers.base import BaseMessageBroker
from app.core.services.queues.taskiq.init import broker

container = create_container(TaskiqProvider())

setup_dishka(container=container, broker=broker)

@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def startup(state: TaskiqState) -> None:
    message_broker = await container.get(BaseMessageBroker)
    await message_broker.start()


@broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def shutdown(state: TaskiqState) -> None:
    message_broker = await container.get(BaseMessageBroker)
    await message_broker.close()


if app_config.ENVIRONMENT == "testing":
    sources = [LabelScheduleSource(broker=broker)]

else:
    redis_schedule_source = RedisScheduleSource(
        url=app_config.QUEUE_REDIS_BROKER_URL,
    )
    sources = [redis_schedule_source, LabelScheduleSource(broker=broker)]



scheduler = TaskiqScheduler(
    broker=broker,
    sources=sources, # type: ignore
)
