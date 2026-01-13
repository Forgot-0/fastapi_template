import pytest
from dataclasses import dataclass

from app.core.commands import BaseCommand, BaseCommandHandler


@dataclass(frozen=True)
class MockCommand(BaseCommand):
    value: str
    number: int = 0


@dataclass(frozen=True)
class MockCommandResult:
    processed_value: str
    doubled_number: int


@dataclass(frozen=True)
class MockCommandHandler(BaseCommandHandler[MockCommand, MockCommandResult]):
    prefix: str = "processed_"

    async def handle(self, command: MockCommand) -> MockCommandResult:
        return MockCommandResult(
            processed_value=f"{self.prefix}{command.value}",
            doubled_number=command.number * 2
        )


@pytest.mark.unit
class TestCommands:
    
    @pytest.mark.asyncio
    async def test_command_creation(self):
        command = MockCommand(value="test", number=42)

        assert command.value == "test"
        assert command.number == 42

    @pytest.mark.asyncio
    async def test_command_is_frozen(self):
        command = MockCommand(value="test", number=42)

        with pytest.raises(Exception):
            command.value = "new_value"  # type: ignore

    @pytest.mark.asyncio
    async def test_command_handler_execution(self):
        handler = MockCommandHandler(prefix="custom_")
        command = MockCommand(value="test", number=10)

        result = await handler.handle(command)

        assert result.processed_value == "custom_test"
        assert result.doubled_number == 20

    @pytest.mark.asyncio
    async def test_multiple_commands(self):
        handler = MockCommandHandler()

        commands = [
            MockCommand(value="first", number=1),
            MockCommand(value="second", number=2),
            MockCommand(value="third", number=3),
        ]

        results = [await handler.handle(cmd) for cmd in commands]

        assert len(results) == 3
        assert results[0].processed_value == "processed_first"
        assert results[1].doubled_number == 4
        assert results[2].processed_value == "processed_third"

    @pytest.mark.asyncio
    async def test_command_with_defaults(self):
        command = MockCommand(value="test")

        assert command.number == 0

        handler = MockCommandHandler()
        result = await handler.handle(command)

        assert result.doubled_number == 0


@dataclass(frozen=True)
class FailingCommand(BaseCommand):
    should_fail: bool = False


@dataclass(frozen=True)
class FailingCommandHandler(BaseCommandHandler[FailingCommand, None]):

    async def handle(self, command: FailingCommand) -> None:
        if command.should_fail:
            raise ValueError("Command failed intentionally")


@pytest.mark.unit
class TestCommandErrorHandling:

    @pytest.mark.asyncio
    async def test_handler_raises_exception(self):
        handler = FailingCommandHandler()
        command = FailingCommand(should_fail=True)

        with pytest.raises(ValueError, match="Command failed intentionally"):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_handler_success_case(self):
        handler = FailingCommandHandler()
        command = FailingCommand(should_fail=False)

        result = await handler.handle(command)
        assert result is None