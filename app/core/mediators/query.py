from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Type

from app.core.exceptions import NotHandlerRegistry
from app.core.queries import QR, BaseQuery, BaseQueryHandler


@dataclass
class QueryRegistry:
    queries_map: dict[Type[BaseQuery], Type[BaseQueryHandler]] = field(
        default_factory=dict,
        kw_only=True,
    )

    def register_query(self, query: Type[BaseQuery], type_handler: Type[BaseQueryHandler]) -> None:
        self.queries_map[query] = type_handler

    def get_handler_types(self, query: BaseQuery) -> Type[BaseQueryHandler]:
        if query.__class__ not in self.queries_map:
            raise NotHandlerRegistry()

        return self.queries_map[query.__class__]


@dataclass(eq=False)
class QueryMediator(ABC):
    query_registy: QueryRegistry

    @abstractmethod
    async def handle_query(self, query: BaseQuery) -> QR:
        ...

