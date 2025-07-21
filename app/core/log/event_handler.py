
import logging

from app.core.events.event import BaseEvent, BaseEventHandler


logger = logging.getLogger(__name__)


class LogHandlerEvent(BaseEventHandler[BaseEvent, None]):
    async def handle(self, event: BaseEvent) -> None:
        logger.info(f"Event {event.__class__.__name__}", extra={"data": event})