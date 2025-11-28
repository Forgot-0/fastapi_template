import pytest
from dataclasses import dataclass
from uuid import UUID

from app.core.events.event import BaseEvent, BaseEventHandler, EventRegisty
from app.core.exceptions import FieldRequiredException


@dataclass(frozen=True)
class UserCreatedEvent(BaseEvent):
    user_id: int
    email: str
    
    __event_name__: str = "user.created"


@dataclass(frozen=True)
class UserDeletedEvent(BaseEvent):
    user_id: int
    
    __event_name__: str = "user.deleted"


@dataclass(frozen=True)
class InvalidEvent(BaseEvent):
    data: str


@pytest.mark.unit
class TestEvents:
    
    def test_event_creation(self):
        event = UserCreatedEvent(user_id=1, email="test@example.com")

        assert event.user_id == 1
        assert event.email == "test@example.com"
        assert isinstance(event.event_id, UUID)
        assert event.created_at is not None

    def test_event_is_frozen(self):
        event = UserCreatedEvent(user_id=1, email="test@example.com")

        with pytest.raises(Exception):
            event.user_id = 2  # type: ignore

    def test_event_has_unique_id(self):
        event1 = UserCreatedEvent(user_id=1, email="test1@example.com")
        event2 = UserCreatedEvent(user_id=1, email="test1@example.com")

        assert event1.event_id != event2.event_id

    def test_event_get_name(self):
        event = UserCreatedEvent(user_id=1, email="test@example.com")

        assert event.get_name() == "user.created"
        assert UserCreatedEvent.get_name() == "user.created"

    def test_event_without_name_raises_error(self):
        with pytest.raises(FieldRequiredException):
            InvalidEvent.get_name()


@dataclass(frozen=True)
class RecordingEventHandler(BaseEventHandler[UserCreatedEvent, None]):
    events_log: list

    async def __call__(self, event: UserCreatedEvent) -> None:
        self.events_log.append({
            "event_id": str(event.event_id),
            "user_id": event.user_id,
            "email": event.email
        })


@dataclass(frozen=True)
class EmailNotificationHandler(BaseEventHandler[UserCreatedEvent, str]):

    async def __call__(self, event: UserCreatedEvent) -> str:
        return f"Email sent to {event.email}"


@pytest.mark.unit
class TestEventHandlers:

    @pytest.mark.asyncio
    async def test_event_handler_execution(self):
        events_log = []
        handler = RecordingEventHandler(events_log=events_log)
        event = UserCreatedEvent(user_id=1, email="test@example.com")

        await handler(event)

        assert len(events_log) == 1
        assert events_log[0]["user_id"] == 1
        assert events_log[0]["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_multiple_events_processing(self):
        events_log = []
        handler = RecordingEventHandler(events_log=events_log)

        events = [
            UserCreatedEvent(user_id=1, email="user1@example.com"),
            UserCreatedEvent(user_id=2, email="user2@example.com"),
            UserCreatedEvent(user_id=3, email="user3@example.com"),
        ]

        for event in events:
            await handler(event)

        assert len(events_log) == 3
        assert events_log[0]["user_id"] == 1
        assert events_log[1]["user_id"] == 2
        assert events_log[2]["user_id"] == 3

    @pytest.mark.asyncio
    async def test_handler_with_return_value(self):
        handler = EmailNotificationHandler()
        event = UserCreatedEvent(user_id=1, email="test@example.com")

        result = await handler(event)

        assert result == "Email sent to test@example.com"


@pytest.mark.unit
class TestEventRegistry:

    def test_registry_creation(self):
        registry = EventRegisty()

        assert registry.events_map == {}

    def test_subscribe_handler(self):
        registry = EventRegisty()

        registry.subscribe(UserCreatedEvent, [RecordingEventHandler])

        assert UserCreatedEvent in registry.events_map
        assert RecordingEventHandler in registry.events_map[UserCreatedEvent]

    def test_subscribe_multiple_handlers(self):
        registry = EventRegisty()

        registry.subscribe(UserCreatedEvent, [
            RecordingEventHandler,
            EmailNotificationHandler
        ])

        handlers = registry.events_map[UserCreatedEvent]
        assert len(handlers) == 2
        assert RecordingEventHandler in handlers
        assert EmailNotificationHandler in handlers

    def test_subscribe_different_events(self):
        registry = EventRegisty()
        
        registry.subscribe(UserCreatedEvent, [RecordingEventHandler])
        registry.subscribe(UserDeletedEvent, [EmailNotificationHandler])

        assert len(registry.events_map) == 2
        assert UserCreatedEvent in registry.events_map
        assert UserDeletedEvent in registry.events_map

    def test_get_handler_types(self):
        registry = EventRegisty()
        registry.subscribe(UserCreatedEvent, [
            RecordingEventHandler,
            EmailNotificationHandler
        ])

        event = UserCreatedEvent(user_id=1, email="test@example.com")
        handler_types = list(registry.get_handler_types([event]))

        assert len(handler_types) == 2
        assert RecordingEventHandler in handler_types
        assert EmailNotificationHandler in handler_types

    def test_get_handler_types_for_multiple_events(self):
        registry = EventRegisty()
        registry.subscribe(UserCreatedEvent, [RecordingEventHandler])
        registry.subscribe(UserDeletedEvent, [EmailNotificationHandler])

        events = [
            UserCreatedEvent(user_id=1, email="test@example.com"),
            UserDeletedEvent(user_id=2),
        ]

        handler_types = list(registry.get_handler_types(events))

        assert len(handler_types) == 2
        assert RecordingEventHandler in handler_types
        assert EmailNotificationHandler in handler_types

    def test_get_handler_types_for_unregistered_event(self):
        registry = EventRegisty()

        event = UserCreatedEvent(user_id=1, email="test@example.com")
        handler_types = list(registry.get_handler_types([event]))

        assert len(handler_types) == 0


@dataclass(frozen=True)
class FailingEventHandler(BaseEventHandler[UserCreatedEvent, None]):

    async def __call__(self, event: UserCreatedEvent) -> None:
        raise RuntimeError("Handler failed")


@pytest.mark.unit
class TestEventHandlerErrors:

    @pytest.mark.asyncio
    async def test_handler_raises_exception(self):
        handler = FailingEventHandler()
        event = UserCreatedEvent(user_id=1, email="test@example.com")

        with pytest.raises(RuntimeError, match="Handler failed"):
            await handler(event)