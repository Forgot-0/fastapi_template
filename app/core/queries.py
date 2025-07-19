from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, TypeVar, Dict, Type, Optional


@dataclass(frozen=True)
class BaseQuery(ABC):
    ...


QT = TypeVar('QT', bound=BaseQuery)
QR = TypeVar('QR', bound=Any)


@dataclass(frozen=True)
class BaseQueryHandler(ABC, Generic[QT, QR]):
    @abstractmethod
    async def handle(self, query: QT) -> QR:
        ...


@dataclass
class QueryHandlerInfo:
    handler_type: Type[BaseQueryHandler]
    instance: Optional[BaseQueryHandler] = None


class QueryHandlerRegistry:
    def __init__(self):
        self._handlers: Dict[Type[BaseQuery], QueryHandlerInfo] = {}
    
    def register(self, query_type: Type[BaseQuery], handler_type: Type[BaseQueryHandler], instance: Optional[BaseQueryHandler] = None):
        """Register a query handler."""
        self._handlers[query_type] = QueryHandlerInfo(
            handler_type=handler_type,
            instance=instance
        )
    
    def get_handler_types(self, query: BaseQuery) -> Optional[QueryHandlerInfo]:
        """Get registered handler for a query."""
        query_type = type(query)
        return self._handlers.get(query_type)