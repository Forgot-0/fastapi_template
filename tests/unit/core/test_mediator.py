import pytest
from dataclasses import dataclass

from app.core.commands import BaseCommand, BaseCommandHandler
from app.core.exceptions import NotHandlerRegisterException
from app.core.mediators.command import CommandRegisty
from app.core.mediators.query import QueryRegistry
from app.core.queries import BaseQuery, BaseQueryHandler


@dataclass(frozen=True)
class TestMediatorCommand(BaseCommand):
    value: str


@dataclass(frozen=True)
class TestMediatorCommandHandler(BaseCommandHandler[TestMediatorCommand, str]):

    async def handle(self, command: TestMediatorCommand) -> str:
        return f"handled: {command.value}"


@dataclass(frozen=True)
class TestMediatorQuery(BaseQuery):
    id: int


@dataclass(frozen=True)
class TestMediatorQueryHandler(BaseQueryHandler[TestMediatorQuery, dict]):

    async def handle(self, query: TestMediatorQuery) -> dict:
        return {"id": query.id, "name": "test"}


@pytest.mark.unit
class TestCommandRegistry:

    def test_register_command(self):
        registry = CommandRegisty()

        registry.register_command(TestMediatorCommand, [TestMediatorCommandHandler])

        assert TestMediatorCommand in registry.commands_map
        assert TestMediatorCommandHandler in registry.commands_map[TestMediatorCommand]

    def test_register_multiple_handlers(self):
        @dataclass(frozen=True)
        class Handler2(BaseCommandHandler[TestMediatorCommand, str]):
            async def handle(self, command: TestMediatorCommand) -> str:
                return "handler2"

        registry = CommandRegisty()
        registry.register_command(TestMediatorCommand, [TestMediatorCommandHandler, Handler2])

        handlers = registry.commands_map[TestMediatorCommand]
        assert len(handlers) == 2

    def test_get_handler_types(self):
        registry = CommandRegisty()
        registry.register_command(TestMediatorCommand, [TestMediatorCommandHandler])

        command = TestMediatorCommand(value="test")
        handler_types = list(registry.get_handler_types(command))

        assert len(handler_types) == 1
        assert TestMediatorCommandHandler in handler_types

    def test_get_handler_types_unregistered(self):
        registry = CommandRegisty()

        command = TestMediatorCommand(value="test")
        handler_types = list(registry.get_handler_types(command))

        assert len(handler_types) == 0


@pytest.mark.unit
class TestQueryRegistry:

    def test_register_query(self):
        registry = QueryRegistry()

        registry.register_query(TestMediatorQuery, TestMediatorQueryHandler)

        assert TestMediatorQuery in registry.queries_map
        assert registry.queries_map[TestMediatorQuery] == TestMediatorQueryHandler

    def test_get_handler_type(self):
        registry = QueryRegistry()
        registry.register_query(TestMediatorQuery, TestMediatorQueryHandler)

        query = TestMediatorQuery(id=1)
        handler_type = registry.get_handler_types(query)

        assert handler_type == TestMediatorQueryHandler

    def test_get_handler_type_unregistered(self):
        registry = QueryRegistry()

        query = TestMediatorQuery(id=1)
        handler_type = registry.get_handler_types(query)

        assert handler_type is None

    def test_register_overwrite(self):
        @dataclass(frozen=True)
        class Handler2(BaseQueryHandler[TestMediatorQuery, dict]):
            async def handle(self, query: TestMediatorQuery) -> dict:
                return {"overwritten": True}

        registry = QueryRegistry()
        registry.register_query(TestMediatorQuery, TestMediatorQueryHandler)
        registry.register_query(TestMediatorQuery, Handler2)

        assert registry.queries_map[TestMediatorQuery] == Handler2


@pytest.mark.unit  
class TestMediatorIntegration:

    @pytest.mark.asyncio
    async def test_mediator_executes_command(self):

        registry = CommandRegisty()
        registry.register_command(TestMediatorCommand, [TestMediatorCommandHandler])

        command = TestMediatorCommand(value="test")
        handler_types = list(registry.get_handler_types(command))

        assert len(handler_types) > 0

        handler = TestMediatorCommandHandler()
        result = await handler.handle(command)

        assert result == "handled: test"

    @pytest.mark.asyncio
    async def test_mediator_executes_query(self):
        registry = QueryRegistry()
        registry.register_query(TestMediatorQuery, TestMediatorQueryHandler)

        query = TestMediatorQuery(id=42)
        handler_type = registry.get_handler_types(query)

        assert handler_type is not None

        handler = TestMediatorQueryHandler()
        result = await handler.handle(query)

        assert result["id"] == 42
        assert result["name"] == "test"