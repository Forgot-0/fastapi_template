from functools import lru_cache

from app.core.events.service import BaseEventBus
from app.core.events.mediator.service import MediatorEventBus


@lru_cache(1)
def get_event_bus() -> BaseEventBus:
    return MediatorEventBus()