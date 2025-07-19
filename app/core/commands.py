from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, TypeVar, Dict, Type, Optional, List


@dataclass(frozen=True)
class BaseCommand(ABC):
    ...


CT = TypeVar('CT', bound=BaseCommand)
CR = TypeVar('CR', bound=Any)


@dataclass(frozen=True)
class BaseCommandHandler(ABC, Generic[CT, CR]):

    @abstractmethod
    async def handle(self, command: CT) -> CR: ...


@dataclass
class HandlerInfo:
    handler_type: Type[BaseCommandHandler]
    instance: Optional[BaseCommandHandler] = None


class CommandHandlerRegistry:
    def __init__(self):
        self._handlers: Dict[Type[BaseCommand], List[HandlerInfo]] = {}
    
    def register(self, command_type: Type[BaseCommand], handler_type: Type[BaseCommandHandler], instance: Optional[BaseCommandHandler] = None):
        """Register a command handler."""
        if command_type not in self._handlers:
            self._handlers[command_type] = []
        
        self._handlers[command_type].append(HandlerInfo(
            handler_type=handler_type,
            instance=instance
        ))
    
    def get_handler_types(self, command: BaseCommand) -> List[HandlerInfo]:
        """Get registered handlers for a command."""
        command_type = type(command)
        return self._handlers.get(command_type, [])