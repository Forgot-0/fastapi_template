import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.commands.permissions.add_permission_user import (
    AddPermissionToUserCommand,
    AddPermissionToUserCommandHandler,
)
from app.auth.exceptions import (
    NotFoundPermissionsError,
    NotFoundUserError,
)
from app.auth.models.permission import Permission
from app.auth.models.user import User
from app.auth.repositories.user import UserRepository
from app.core.services.auth.exceptions import AccessDeniedError
from tests.support.jwt import jwt_from_user


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.asyncio
class TestAddPermissionToUserCommand:
    @pytest.fixture
    async def handler(
        self,
        request_container: AsyncContainer
    ) -> AddPermissionToUserCommandHandler:
        return await request_container.get(AddPermissionToUserCommandHandler)

    async def test_add_permission_to_user_success(
        self,
        db_session: AsyncSession,
        user_repository: UserRepository,
        handler: AddPermissionToUserCommandHandler,
        admin_user: User,
        standard_user: User,
    ) -> None:
        perm = Permission(name="custom:action")
        db_session.add(perm)
        await db_session.commit()

        user_jwt = jwt_from_user(admin_user)

        command = AddPermissionToUserCommand(
            user_jwt_data=user_jwt,
            user_id=standard_user.id,
            permissions={"custom:action"},
        )

        await handler.handle(command)

        updated_user = await user_repository.get_user_with_permission_by_id(standard_user.id)
        assert updated_user is not None

        perm_names = {p.name for p in updated_user.permissions}
        assert "custom:action" in perm_names

    async def test_add_nonexistent_permission(
        self,
        handler: AddPermissionToUserCommandHandler,
        admin_user: User,
        standard_user: User,
    ) -> None:
        user_jwt = jwt_from_user(admin_user)

        command = AddPermissionToUserCommand(
            user_jwt_data=user_jwt,
            user_id=standard_user.id,
            permissions={"nonexistent:permission"},
        )

        with pytest.raises(NotFoundPermissionsError):
            await handler.handle(command)

    async def test_add_permission_to_nonexistent_user(
        self,
        db_session: AsyncSession,
        handler: AddPermissionToUserCommandHandler,
        admin_user: User,
    ) -> None:
        perm = Permission(name="test:perm")
        db_session.add(perm)
        await db_session.commit()

        user_jwt = jwt_from_user(admin_user)

        command = AddPermissionToUserCommand(
            user_jwt_data=user_jwt,
            user_id=99999,
            permissions={"test:perm"},
        )

        with pytest.raises(NotFoundUserError):
            await handler.handle(command)

    async def test_add_multiple_permissions_to_user(
        self,
        db_session: AsyncSession,
        user_repository: UserRepository,
        handler: AddPermissionToUserCommandHandler,
        admin_user: User,
        standard_user: User,
    ) -> None:
        perm1 = Permission(name="action:create")
        perm2 = Permission(name="action:edit")
        perm3 = Permission(name="action:delete")
        db_session.add_all([perm1, perm2, perm3])
        await db_session.commit()

        user_jwt = jwt_from_user(admin_user)

        command = AddPermissionToUserCommand(
            user_jwt_data=user_jwt,
            user_id=standard_user.id,
            permissions={"action:create", "action:edit", "action:delete"},
        )

        await handler.handle(command)

        updated_user = await user_repository.get_user_with_permission_by_id(standard_user.id)
        assert updated_user is not None

        perm_names = {p.name for p in updated_user.permissions}
        assert "action:create" in perm_names
        assert "action:edit" in perm_names
        assert "action:delete" in perm_names

    async def test_add_permission_insufficient_permissions(
        self,
        db_session: AsyncSession,
        handler: AddPermissionToUserCommandHandler,
        standard_user: User,
    ) -> None:
        perm = Permission(name="test:perm")
        db_session.add(perm)
        await db_session.commit()

        user_jwt = jwt_from_user(standard_user)

        command = AddPermissionToUserCommand(
            user_jwt_data=user_jwt,
            user_id=standard_user.id,
            permissions={"test:perm"},
        )

        with pytest.raises(AccessDeniedError):
            await handler.handle(command)

    async def test_add_same_permission_twice(
        self,
        db_session: AsyncSession,
        user_repository: UserRepository,
        handler: AddPermissionToUserCommandHandler,
        admin_user: User,
        standard_user: User,
    ) -> None:
        perm = Permission(name="duplicate:perm")
        db_session.add(perm)
        await db_session.commit()

        user_jwt = jwt_from_user(admin_user)

        command = AddPermissionToUserCommand(
            user_jwt_data=user_jwt,
            user_id=standard_user.id,
            permissions={"duplicate:perm"},
        )

        await handler.handle(command)

        await handler.handle(command)

        updated_user = await user_repository.get_user_with_permission_by_id(standard_user.id)
        assert updated_user is not None

        perm_count = sum(1 for p in updated_user.permissions if p.name == "duplicate:perm")
        assert perm_count == 1
