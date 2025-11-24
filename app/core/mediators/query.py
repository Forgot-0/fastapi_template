from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from app.core.queries import QR, BaseQuery, BaseQueryHandler


@dataclass
class QueryRegistry:
    queries_map: dict[type[BaseQuery], type[BaseQueryHandler]] = field(
        default_factory=dict,
        kw_only=True,
    )

    def register_query(self, query: type[BaseQuery], type_handler: type[BaseQueryHandler]) -> None:
        self.queries_map[query] = type_handler

    def get_handler_types(self, query: BaseQuery) -> type[BaseQueryHandler]  | None:
        return self.queries_map.get(query.__class__)


@dataclass(eq=False)
class QueryMediator(ABC):
    query_registy: QueryRegistry

    @abstractmethod
    async def handle_query(self, query: BaseQuery) -> QR:
        ...

