
import logging

from app.core.events.event import BaseEvent, BaseEventHandler

logger = logging.getLogger(__name__)


class LogHandlerEvent(BaseEventHandler[BaseEvent, None]):
    async def handle(self, event: BaseEvent) -> None:
        logger.info("Event LogHandlerEvent", extra={"data": event})
