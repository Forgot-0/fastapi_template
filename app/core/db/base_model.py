import copy
from datetime import datetime
from typing import Any, Self

from sqlalchemy import DateTime, Select, inspect, select
from sqlalchemy.orm import DeclarativeBase, InstanceState, Mapped, declared_attr, mapped_column, reconstructor
from sqlalchemy.sql import func

from app.core.events.event import BaseEvent
from app.core.utils import now_utc


class BaseModel(DeclarativeBase):
    def __init__(self, **kw: Any) -> None:
        for key, value in kw.items():
            setattr(self, key, value)
        self.events: list[BaseEvent] = []

    @reconstructor
    def init_on_load(self) -> None:
        self.events = []

    def register_event(self, event: BaseEvent) -> None:
        self.events.append(event)

    def pull_events(self) -> list[BaseEvent]:
        registered_events = copy.copy(self.events)
        self.events.clear()
        return registered_events

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(**{k: v for k, v in data.items() if k in cls._get_field_names()})

    @classmethod
    def _get_field_names(cls) -> list[str]:
        return [column.name for column in cls.__table__.columns]


class DateMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class SoftDeleteMixin:
    @declared_attr
    @classmethod
    def deleted_at(cls) -> Mapped[datetime | None]:
        return mapped_column(DateTime(timezone=True), nullable=True)

    @classmethod
    def select_not_deleted(cls) -> Select[tuple[Self]]:
        return select(cls).where(cls.deleted_at.is_(None))

    def soft_delete(self) -> None:
        self.deleted_at = now_utc()

    def is_deleted(self) -> bool:
        return self.deleted_at is not None
