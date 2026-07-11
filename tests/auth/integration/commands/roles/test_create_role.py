import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.commands.roles.create import CreateRoleCommand, CreateRoleCommandHandler
from app.auth.exceptions import (
    DuplicateRoleError,
    InvalidRoleNameError,
    NotFoundPermissionsError,
)
from app.auth.models.permission import Permission
from app.auth.models.user import User
from app.auth.repositories.role import RoleRepository
from app.core.services.auth.exceptions import AccessDeniedError
from tests.support.jwt import jwt_from_user


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.asyncio
class TestCreateRoleCommand:
    @pytest.fixture
    async def handler(
        self,
        request_container: AsyncContainer
    ) -> CreateRoleCommandHandler:
        return await request_container.get(CreateRoleCommandHandler)

    async def test_create_role_success(
        self,
        role_repository: RoleRepository,
        handler: CreateRoleCommandHandler,
        admin_user: User,
    ) -> None:
        user_jwt = jwt_from_user(admin_user)

        command = CreateRoleCommand(
            user_jwt_data=user_jwt,
            role_name="moderator",
            description="Moderator role",
            security_level=5,
            permissions=set(),
        )

        await handler.handle(command)

        created_role = await role_repository.get_by_name("moderator")
        assert created_role is not None
        assert created_role.description == "Moderator role"
        assert created_role.security_level == 5

    async def test_create_role_with_permissions(
        self,
        db_session: AsyncSession,
        role_repository: RoleRepository,
        handler: CreateRoleCommandHandler,
        admin_user: User,
    ) -> None:
        perm1 = Permission(name="post:create")
        perm2 = Permission(name="post:edit")
        db_session.add_all([perm1, perm2])
        await db_session.commit()

        user_jwt = jwt_from_user(admin_user)

        command = CreateRoleCommand(
            user_jwt_data=user_jwt,
            role_name="content_creator",
            description="Content creator role",
            security_level=3,
            permissions={"post:create", "post:edit"},
        )

        await handler.handle(command)

        created_role = await role_repository.get_with_permission_by_name("content_creator")
        assert created_role is not None
        assert len(created_role.permissions) == 2

    async def test_create_role_duplicate_name(
        self,
        handler: CreateRoleCommandHandler,
        admin_user: User,
    ) -> None:
        user_jwt = jwt_from_user(admin_user)

        command1 = CreateRoleCommand(
            user_jwt_data=user_jwt,
            role_name="duplicate_role",
            description="First role",
            security_level=3,
            permissions=set(),
        )
        await handler.handle(command1)

        command2 = CreateRoleCommand(
            user_jwt_data=user_jwt,
            role_name="duplicate_role",
            description="Second role",
            security_level=3,
            permissions=set(),
        )

        with pytest.raises(DuplicateRoleError):
            await handler.handle(command2)

    async def test_create_role_insufficient_permissions(
        self,
        handler: CreateRoleCommandHandler,
        standard_user: User,
    ) -> None:
        user_jwt = jwt_from_user(standard_user)

        command = CreateRoleCommand(
            user_jwt_data=user_jwt,
            role_name="new_role",
            description="Test role",
            security_level=3,
            permissions=set(),
        )

        with pytest.raises(AccessDeniedError):
            await handler.handle(command)

    async def test_create_role_invalid_name(
        self,
        handler: CreateRoleCommandHandler,
        admin_user: User,
    ) -> None:
        user_jwt = jwt_from_user(admin_user)

        command = CreateRoleCommand(
            user_jwt_data=user_jwt,
            role_name="ab",
            description="Test role",
            security_level=3,
            permissions=set(),
        )

        with pytest.raises(InvalidRoleNameError):
            await handler.handle(command)

    async def test_create_role_nonexistent_permission(
        self,
        handler: CreateRoleCommandHandler,
        admin_user: User,
    ) -> None:
        user_jwt = jwt_from_user(admin_user)

        command = CreateRoleCommand(
            user_jwt_data=user_jwt,
            role_name="test_role",
            description="Test role",
            security_level=3,
            permissions={"nonexistent:permission"},
        )

        with pytest.raises(NotFoundPermissionsError):
            await handler.handle(command)

    async def test_create_role_security_level_too_high(
        self,
        handler: CreateRoleCommandHandler,
        standard_user: User,
    ) -> None:
        user_jwt = jwt_from_user(standard_user)

        command = CreateRoleCommand(
            user_jwt_data=user_jwt,
            role_name="high_level_role",
            description="High level role",
            security_level=8,
            permissions=set(),
        )

        with pytest.raises(AccessDeniedError):
            await handler.handle(command)

    async def test_create_role_empty_name(
        self,
        handler: CreateRoleCommandHandler,
        admin_user: User,
    ) -> None:
        user_jwt = jwt_from_user(admin_user)

        command = CreateRoleCommand(
            user_jwt_data=user_jwt,
            role_name="",
            description="Test role",
            security_level=3,
            permissions=set(),
        )

        with pytest.raises(InvalidRoleNameError):
            await handler.handle(command)

    async def test_create_role_with_invalid_security_level(
        self,
        handler: CreateRoleCommandHandler,
        admin_user: User,
    ) -> None:
        user_jwt = jwt_from_user(admin_user)

        command = CreateRoleCommand(
            user_jwt_data=user_jwt,
            role_name="test_role",
            description="Test role",
            security_level=0,
            permissions=set(),
        )

        with pytest.raises(AccessDeniedError):
            await handler.handle(command)

    async def test_create_role_preserves_description(
        self,
        role_repository: RoleRepository,
        handler: CreateRoleCommandHandler,
        admin_user: User,
    ) -> None:
        user_jwt = jwt_from_user(admin_user)

        description = "This is a detailed description of the editor role"
        command = CreateRoleCommand(
            user_jwt_data=user_jwt,
            role_name="editor_role",
            description=description,
            security_level=4,
            permissions=set(),
        )

        await handler.handle(command)

        created_role = await role_repository.get_by_name("editor_role")
        assert created_role is not None
        assert created_role.description == description

    async def test_create_multiple_roles_with_different_levels(
        self,
        role_repository: RoleRepository,
        handler: CreateRoleCommandHandler,
        admin_user: User,
    ) -> None:
        user_jwt = jwt_from_user(admin_user)

        roles_data = [
            ("viewer_role", "Can view content", 1),
            ("editor_role", "Can edit content", 3),
            ("manager_role", "Can manage content", 5),
        ]

        for role_name, description, security_level in roles_data:
            command = CreateRoleCommand(
                user_jwt_data=user_jwt,
                role_name=role_name,
                description=description,
                security_level=security_level,
                permissions=set(),
            )
            await handler.handle(command)

        for role_name, _, security_level in roles_data:
            created_role = await role_repository.get_by_name(role_name)
            assert created_role is not None
            assert created_role.security_level == security_level
