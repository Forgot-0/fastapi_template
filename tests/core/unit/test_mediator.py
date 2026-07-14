from dataclasses import dataclass

import pytest

from app.core.commands import BaseCommand, BaseCommandHandler
from app.core.mediators.base import CommandRegistry, QueryRegistry
from app.core.queries import BaseQuery, BaseQueryHandler


@dataclass(frozen=True)
class MockMediatorCommand(BaseCommand):
    value: str


@dataclass(frozen=True)
class MockMediatorCommandHandler(BaseCommandHandler[MockMediatorCommand, str]):

    async def handle(self, command: MockMediatorCommand) -> str:
        return f"handled: {command.value}"


@dataclass(frozen=True)
class MockMediatorQuery(BaseQuery):
    id: int


@dataclass(frozen=True)
class MockMediatorQueryHandler(BaseQueryHandler[MockMediatorQuery, dict]):

    async def handle(self, query: MockMediatorQuery) -> dict:
        return {"id": query.id, "name": "test"}


@pytest.mark.unit
class TestCommandRegistry:

    def test_register_command(self) -> None:
        registry = CommandRegistry()

        registry.register_command(MockMediatorCommand, MockMediatorCommandHandler)

        assert MockMediatorCommand in registry.commands_map
        assert registry.commands_map[MockMediatorCommand] == MockMediatorCommandHandler

    def test_get_handler_types_unregistered(self) -> None:
        registry = CommandRegistry()

        command = MockMediatorCommand(value="test")
        handler_types = registry.get_handler_types(command)

        assert handler_types is None


@pytest.mark.unit
class TestQueryRegistry:

    def test_register_query(self) -> None:
        registry = QueryRegistry()

        registry.register_query(MockMediatorQuery, MockMediatorQueryHandler)

        assert MockMediatorQuery in registry.queries_map
        assert registry.queries_map[MockMediatorQuery] == MockMediatorQueryHandler

    def test_get_handler_type(self) -> None:
        registry = QueryRegistry()
        registry.register_query(MockMediatorQuery, MockMediatorQueryHandler)

        query = MockMediatorQuery(id=1)
        handler_type = registry.get_handler_types(query)

        assert handler_type == MockMediatorQueryHandler

    def test_get_handler_type_unregistered(self) -> None:
        registry = QueryRegistry()

        query = MockMediatorQuery(id=1)
        handler_type = registry.get_handler_types(query)

        assert handler_type is None

    def test_register_overwrite(self) -> None:
        @dataclass(frozen=True)
        class Handler2(BaseQueryHandler[MockMediatorQuery, dict]):
            async def handle(self, query: MockMediatorQuery) -> dict:
                return {"overwritten": True}

        registry = QueryRegistry()
        registry.register_query(MockMediatorQuery, MockMediatorQueryHandler)
        registry.register_query(MockMediatorQuery, Handler2)

        assert registry.queries_map[MockMediatorQuery] == Handler2


@pytest.mark.unit
class TestMediatorIntegration:

    @pytest.mark.asyncio
    async def test_mediator_executes_command(self) -> None:

        registry = CommandRegistry()
        registry.register_command(MockMediatorCommand, MockMediatorCommandHandler)

        command = MockMediatorCommand(value="test")
        handler_types = registry.get_handler_types(command)

        assert handler_types is not None

        handler = MockMediatorCommandHandler()
        result = await handler.handle(command)

        assert result == "handled: test"

    @pytest.mark.asyncio
    async def test_mediator_executes_query(self) -> None:
        registry = QueryRegistry()
        registry.register_query(MockMediatorQuery, MockMediatorQueryHandler)

        query = MockMediatorQuery(id=42)
        handler_type = registry.get_handler_types(query)

        assert handler_type is not None

        handler = MockMediatorQueryHandler()
        result = await handler.handle(query)

        assert result["id"] == 42
        assert result["name"] == "test"
