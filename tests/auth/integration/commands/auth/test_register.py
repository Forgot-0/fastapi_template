import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.commands.users.register import RegisterCommand, RegisterCommandHandler
from app.auth.exceptions import DuplicateUserException, PasswordMismatchException
from app.auth.models.user import User
from app.auth.repositories.role import RoleRepository
from app.auth.repositories.user import UserRepository
from app.auth.services.hash import HashService
from tests.auth.integration.factories import CommandFactory
from tests.conftest import MockEventBus


@pytest.mark.integration
@pytest.mark.auth
class TestRegisterCommand:
    @pytest.mark.asyncio
    async def test_register_new_user_success(
        self,
        db_session: AsyncSession,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        hash_service: HashService,
        mock_event_bus: MockEventBus,
    ) -> None:
        handler = RegisterCommandHandler(
            session=db_session,
            event_bus=mock_event_bus,
            user_repository=user_repository,
            role_repository=role_repository,
            hash_service=hash_service,
        )

        cmd_data = CommandFactory.create_register_command(
            username="newuser",
            email="new@example.com",
        )

        command = RegisterCommand(**cmd_data)

        user_dto = await handler.handle(command)

        assert user_dto is not None
        assert user_dto.username == "newuser"
        assert user_dto.email == "new@example.com"
        assert user_dto.is_active is True
        assert user_dto.is_verified is False

        created_user = await user_repository.get_by_username("newuser")
        assert created_user is not None
        assert created_user.password_hash is not None

        assert len(mock_event_bus.published_events) == 1
        assert mock_event_bus.published_events[0].__class__.__name__ == "CreatedUserEvent"

    @pytest.mark.asyncio
    async def test_register_duplicate_username(
        self,
        db_session: AsyncSession,
        mock_event_bus: MockEventBus,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        hash_service: HashService,
        standard_user: User,
    ) -> None:

        handler = RegisterCommandHandler(
            session=db_session,
            event_bus=mock_event_bus,
            user_repository=user_repository,
            role_repository=role_repository,
            hash_service=hash_service,
        )

        cmd_data = CommandFactory.create_register_command(
            username=standard_user.username,
            email="different@example.com",
        )

        command = RegisterCommand(**cmd_data)

        with pytest.raises(DuplicateUserException) as exc_info:
            await handler.handle(command)

        assert exc_info.value.field == "username"
        assert exc_info.value.value == standard_user.username

    @pytest.mark.asyncio
    async def test_register_duplicate_email(
        self,
        db_session: AsyncSession,
        mock_event_bus: MockEventBus,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        hash_service: HashService,
        standard_user,
    ) -> None:

        handler = RegisterCommandHandler(
            session=db_session,
            event_bus=mock_event_bus,
            user_repository=user_repository,
            role_repository=role_repository,
            hash_service=hash_service,
        )

        cmd_data = CommandFactory.create_register_command(
            username="differentuser",
            email=standard_user.email,
        )

        command = RegisterCommand(**cmd_data)

        with pytest.raises(DuplicateUserException) as exc_info:
            await handler.handle(command)

        assert exc_info.value.field == "email"
        assert exc_info.value.value == standard_user.email

    @pytest.mark.asyncio
    async def test_register_password_mismatch(
        self,
        db_session: AsyncSession,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        hash_service: HashService,
        mock_event_bus: MockEventBus,
    ) -> None:

        handler = RegisterCommandHandler(
            session=db_session,
            event_bus=mock_event_bus,
            user_repository=user_repository,
            role_repository=role_repository,
            hash_service=hash_service,
        )

        command = RegisterCommand(
            username="testuser",
            email="test@example.com",
            password="TestPass123!",
            password_repeat="DifferentPass123!",  # Разные пароли
        )

        with pytest.raises(PasswordMismatchException):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_register_user_has_default_role(
        self,
        db_session: AsyncSession,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        hash_service: HashService,
        mock_event_bus: MockEventBus,
    ) -> None:

        handler = RegisterCommandHandler(
            session=db_session,
            event_bus=mock_event_bus,
            user_repository=user_repository,
            role_repository=role_repository,
            hash_service=hash_service,
        )

        cmd_data = CommandFactory.create_register_command()
        command = RegisterCommand(**cmd_data)

        user_dto = await handler.handle(command)
        await db_session.commit()

        created_user = await user_repository.get_user_with_permission_by_id(user_dto.id)
        assert created_user is not None
        assert len(created_user.roles) == 1
        assert list(created_user.roles)[0].name == "user"

    @pytest.mark.asyncio
    async def test_register_password_is_hashed(
        self,
        db_session: AsyncSession,
        mock_event_bus: MockEventBus,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        hash_service: HashService,
    ) -> None:

        handler = RegisterCommandHandler(
            session=db_session,
            event_bus=mock_event_bus,
            user_repository=user_repository,
            role_repository=role_repository,
            hash_service=hash_service,
        )

        plain_password = "TestPass123!"
        cmd_data = CommandFactory.create_register_command(password=plain_password)
        command = RegisterCommand(**cmd_data)

        user_dto = await handler.handle(command)
        await db_session.commit()

        created_user = await user_repository.get_by_id(user_dto.id)
        assert created_user is not None
        assert created_user.password_hash is not None
        assert created_user.password_hash != plain_password
        assert hash_service.verify_password(plain_password, created_user.password_hash)