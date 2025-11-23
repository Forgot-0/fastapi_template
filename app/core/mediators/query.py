from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Type

from app.core.queries import QR, BaseQuery, BaseQueryHandler


@dataclass
class QueryRegistry:
    queries_map: dict[Type[BaseQuery], Type[BaseQueryHandler]] = field(
        default_factory=dict,
        kw_only=True,
    )

    def register_query(self, query: Type[BaseQuery], type_handler: Type[BaseQueryHandler]) -> None:
        self.queries_map[query] = type_handler

    def get_handler_types(self, query: BaseQuery) -> Type[BaseQueryHandler]  | None:
        return self.queries_map.get(query.__class__)


@dataclass(eq=False)
class QueryMediator(ABC):
    query_registy: QueryRegistry

    @abstractmethod
    async def handle_query(self, query: BaseQuery) -> QR:
        ...

