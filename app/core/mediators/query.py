from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Type

from app.core.queries import QR, BaseQuery, BaseQueryHandler


@dataclass
class QueryHandleRegistry:
    handler_type: Type[BaseQueryHandler]
    instance: Optional[BaseQueryHandler] = None



@dataclass
class QueryRegisty:
    quries_map: dict[Type[BaseQuery], QueryHandleRegistry] = field(
        default_factory=dict,
        kw_only=True,
    )

    def register_query(self, query: Type[BaseQuery], type_handlers: QueryHandleRegistry) -> None:
        self.quries_map[query] = type_handlers

    def get_handler_types(self, query: BaseQuery) -> QueryHandleRegistry:
        if query.__class__ not in self.quries_map:
            raise

        return self.quries_map[query.__class__]


@dataclass(eq=False)
class QueryMediator(ABC):
    query_registy: QueryRegisty

    @abstractmethod
    async def handle_query(self, query: BaseQuery) -> QR:
        ...

