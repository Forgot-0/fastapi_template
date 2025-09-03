import copy
from datetime import datetime
from typing import Any, Self

from sqlalchemy import DateTime, inspect, select
from sqlalchemy.orm import DeclarativeBase, reconstructor, Mapped, declared_attr, mapped_column
from sqlalchemy.orm.state import InstanceState
from sqlalchemy.sql import func

from app.core.events.event import BaseEvent
from app.core.utils import now_utc


class BaseModel(DeclarativeBase):
    def __init__(self, **kw: Any):
        for key, value in kw.items():
            setattr(self, key, value)
        self.events = list()

    @reconstructor
    def init_on_load(self) -> None:
        self.events = []

    def register_event(self, event: BaseEvent) -> None:
        self.events.append(event)

    def pull_events(self) -> list[BaseEvent]:
        registered_events = copy.copy(self.events)
        self.events.clear()
        return registered_events

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

        state: InstanceState = inspect(self)
        mapper = state.mapper

        for rel in mapper.relationships:
            key = rel.key

            if key in state.dict:  
                value = getattr(self, key)

                if value is None:
                    data[key] = None
                elif rel.uselist:
                    data[key] = [item.to_dict() if hasattr(item, "to_dict") else repr(item)
                                 for item in value]
                else:
                    data[key] = (value.to_dict()
                                 if hasattr(value, "to_dict")
                                 else repr(value))

        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(**{k: v for k, v in data.items() if k in cls._get_field_names()})

    def update(self, data: dict[str, Any]) -> None:
        for key, value in data.items():
            if key in self._get_field_names():
                setattr(self, key, value)

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
    def deleted_at(cls) -> Mapped[datetime | None]:
        return mapped_column(DateTime, nullable=True)

    @classmethod
    def select_not_deleted(cls):
        return select(cls).where(cls.deleted_at.is_(None))

    def soft_delete(self) -> None:
        self.deleted_at = now_utc()

    def is_deleted(self) -> bool:
        return self.deleted_at is not None