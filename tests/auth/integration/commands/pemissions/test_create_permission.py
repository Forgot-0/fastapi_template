import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.commands.permissions.create import CreatePermissionCommand, CreatePermissionCommandHandler
from app.auth.exceptions import DuplicatePermissionException
from app.auth.models.permission import Permission
from app.auth.models.user import User
from app.auth.repositories.permission import PermissionRepository
from app.auth.services.rbac import AuthRBACManager
from app.core.services.auth.exceptions import AccessDeniedException
from tests.support.jwt import jwt_from_user


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.asyncio
class TestCreatePermissionCommand:
    @pytest.fixture
    def handler(
        self,
        db_session: AsyncSession,
        permission_repository: PermissionRepository,
        rbac_manager: AuthRBACManager,
    ) -> CreatePermissionCommandHandler:
        return CreatePermissionCommandHandler(
            session=db_session,
            permission_repository=permission_repository,
            rbac_manager=rbac_manager,
        )

    async def test_create_permission_success(
        self,
        db_session: AsyncSession,
        permission_repository: PermissionRepository,
        handler: CreatePermissionCommandHandler,
        admin_user: User,
    ) -> None:
        user_jwt = jwt_from_user(admin_user)

        command = CreatePermissionCommand(
            name="post:publish",
            user_jwt_data=user_jwt,
        )

        await handler.handle(command)
        await db_session.commit()

        created_perm = await permission_repository.get_permission_by_name("post:publish")
        assert created_perm is not None

    async def test_create_permission_duplicate(
        self,
        db_session: AsyncSession,
        handler: CreatePermissionCommandHandler,
        admin_user: User,
    ) -> None:
        perm = Permission(name="duplicate:perm")
        db_session.add(perm)
        await db_session.commit()

        user_jwt = jwt_from_user(admin_user)

        command = CreatePermissionCommand(
            name="duplicate:perm",
            user_jwt_data=user_jwt,
        )

        with pytest.raises(DuplicatePermissionException):
            await handler.handle(command)

    async def test_create_permission_insufficient_permissions(
        self,
        handler: CreatePermissionCommandHandler,
        standard_user: User,
    ) -> None:
        user_jwt = jwt_from_user(standard_user)

        command = CreatePermissionCommand(
            name="new:permission",
            user_jwt_data=user_jwt,
        )

        with pytest.raises(AccessDeniedException):
            await handler.handle(command)
