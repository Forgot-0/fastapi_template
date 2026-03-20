import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.commands.permissions.create import CreatePermissionCommand, CreatePermissionCommandHandler
from app.auth.commands.permissions.delete import DeletePermissionCommand, DeletePermissionCommandHandler
from app.auth.dtos.user import AuthUserJWTData
from app.auth.exceptions import (
    AccessDeniedException,
    NotFoundPermissionsException,
    ProtectedPermissionException,
)
from app.auth.models.permission import Permission
from app.auth.models.user import User
from app.auth.repositories.permission import PermissionInvalidateRepository, PermissionRepository
from app.auth.services.rbac import AuthRBACManager


@pytest.mark.integration
@pytest.mark.auth
class TestCreatePermissionCommand:

    @pytest.fixture
    def handler(
        self,
        db_session: AsyncSession,
        rbac_manager: AuthRBACManager,
        permission_repository: PermissionRepository,
    ) -> CreatePermissionCommandHandler:
        return CreatePermissionCommandHandler(
            session=db_session,
            permission_repository=permission_repository,
            rbac_manager=rbac_manager,
        )

    @pytest.mark.asyncio
    async def test_create_permission_success(
        self,
        db_session: AsyncSession,
        permission_repository: PermissionRepository,
        admin_user: User,
        handler
    ) -> None:
        user_jwt = AuthUserJWTData.create_from_user(admin_user)

        command = CreatePermissionCommand(
            name="post:publish",
            user_jwt_data=user_jwt,
        )

        await handler.handle(command)
        await db_session.commit()

        created_perm = await permission_repository.get_permission_by_name("post:publish")
        assert created_perm is not None

    @pytest.mark.asyncio
    async def test_create_permission_duplicate(
        self,
        db_session: AsyncSession,
        admin_user: User,
        handler
    ) -> None:
        perm = Permission(name="duplicate:perm")
        db_session.add(perm)
        await db_session.commit()

        user_jwt = AuthUserJWTData.create_from_user(admin_user)

        command = CreatePermissionCommand(
            name="duplicate:perm",
            user_jwt_data=user_jwt,
        )

        with pytest.raises(NotFoundPermissionsException):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_create_permission_insufficient_permissions(
        self,
        standard_user: User,
        handler
    ) -> None:
        user_jwt = AuthUserJWTData.create_from_user(standard_user)

        command = CreatePermissionCommand(
            name="new:permission",
            user_jwt_data=user_jwt,
        )

        with pytest.raises(AccessDeniedException):
            await handler.handle(command)

    @pytest.mark.ahandlersyncio
    async def test_delete_permission_success(
        self,
        db_session: AsyncSession,
        permission_repository: PermissionRepository,
        admin_user: User,
        rbac_manager: AuthRBACManager,
        permission_blacklist: PermissionInvalidateRepository,
    ) -> None:
        perm = Permission(name="deletable:perm")
        db_session.add(perm)
        await db_session.commit()

        user_jwt = AuthUserJWTData.create_from_user(admin_user)

        command = DeletePermissionCommand(
            name="deletable:perm",
            user_jwt_data=user_jwt,
        )

        handler = DeletePermissionCommandHandler(
            session=db_session,
            permission_repository=permission_repository,
            rbac_manager=rbac_manager,
            permission_blacklist=permission_blacklist,
        )

        await handler.handle(command)
        await db_session.commit()

        deleted_perm = await permission_repository.get_permission_by_name("deletable:perm")
        assert deleted_perm is None

    @pytest.mark.asyncio
    async def test_delete_protected_permission(
        self,
        db_session: AsyncSession,
        permission_repository: PermissionRepository,
        admin_user: User,
        rbac_manager: AuthRBACManager,
        permission_blacklist: PermissionInvalidateRepository
    ) -> None:
        user_jwt = AuthUserJWTData.create_from_user(admin_user)

        command = DeletePermissionCommand(
            name="role:create",
            user_jwt_data=user_jwt,
        )

        handler = DeletePermissionCommandHandler(
            session=db_session,
            permission_repository=permission_repository,
            rbac_manager=rbac_manager,
            permission_blacklist=permission_blacklist,
        )

        with pytest.raises(ProtectedPermissionException):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_delete_permission_insufficient_permissions(
        self,
        db_session: AsyncSession,
        standard_user: User,
        handler,
    ) -> None:
        perm = Permission(name="deletable:perm")
        db_session.add(perm)
        await db_session.commit()

        user_jwt = AuthUserJWTData.create_from_user(standard_user)

        command = DeletePermissionCommand(
            name="deletable:perm",
            user_jwt_data=user_jwt,
        )

        with pytest.raises(AccessDeniedException):
            await handler.handle(command)
