import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.commands.permissions.delete import DeletePermissionCommand, DeletePermissionCommandHandler
from app.auth.exceptions import ProtectedPermissionError
from app.auth.models.permission import Permission
from app.auth.models.user import User
from app.auth.repositories.permission import PermissionRepository
from app.core.services.auth.exceptions import AccessDeniedError
from tests.support.jwt import jwt_from_user


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.asyncio
class TestDeletePermissionCommand:

    @pytest.fixture
    async def handler(
        self,
        request_container: AsyncContainer
    ) -> DeletePermissionCommandHandler:
        return await request_container.get(DeletePermissionCommandHandler)

    async def test_delete_permission_success(
        self,
        db_session: AsyncSession,
        permission_repository: PermissionRepository,
        handler: DeletePermissionCommandHandler,
        admin_user: User,
    ) -> None:
        perm = Permission(name="deletable:perm")
        db_session.add(perm)
        await db_session.commit()

        user_jwt = jwt_from_user(admin_user)

        command = DeletePermissionCommand(
            name="deletable:perm",
            user_jwt_data=user_jwt,
        )

        await handler.handle(command)

        deleted_perm = await permission_repository.get_permission_by_name("deletable:perm")
        assert deleted_perm is None

    async def test_delete_protected_permission(
        self,
        handler: DeletePermissionCommandHandler,
        admin_user: User,
    ) -> None:
        user_jwt = jwt_from_user(admin_user)

        command = DeletePermissionCommand(
            name="role:create",
            user_jwt_data=user_jwt,
        )

        with pytest.raises(ProtectedPermissionError):
            await handler.handle(command)

    async def test_delete_permission_insufficient_permissions(
        self,
        db_session: AsyncSession,
        handler: DeletePermissionCommandHandler,
        standard_user: User,
    ) -> None:
        perm = Permission(name="deletable:perm")
        db_session.add(perm)
        await db_session.commit()

        user_jwt = jwt_from_user(standard_user)

        command = DeletePermissionCommand(
            name="deletable:perm",
            user_jwt_data=user_jwt,
        )

        with pytest.raises(AccessDeniedError):
            await handler.handle(command)
