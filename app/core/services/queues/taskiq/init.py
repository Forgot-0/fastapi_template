import multiprocessing
from taskiq import AsyncBroker, InMemoryBroker
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend

from app.core.configs.app import app_config
from app.core.tasks import register_tasks

broker: AsyncBroker

is_worker_process = "worker" in multiprocessing.current_process().name.lower()


if app_config.ENVIRONMENT == "testing" and not is_worker_process:
    broker = InMemoryBroker()
else:
    broker = ListQueueBroker(url=app_config.QUEUE_REDIS_BROKER_URL)
    broker.with_result_backend(RedisAsyncResultBackend(app_config.QUEUE_REDIS_RESULT_BACKEND))

register_tasks(broker)
