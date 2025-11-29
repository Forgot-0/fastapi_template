import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.commands.permissions.create import CreatePermissionCommand, CreatePermissionCommandHandler
from app.auth.commands.permissions.delete import DeletePermissionCommand, DeletePermissionCommandHandler
from app.auth.exceptions import (
    AccessDeniedException,
    NotFoundPermissionsException,
    ProtectedPermissionException,
)
from app.auth.models.permission import Permission
from app.auth.models.user import User
from app.auth.repositories.permission import PermissionInvalidateRepository, PermissionRepository
from app.auth.schemas.user import UserJWTData
from app.auth.services.rbac import RBACManager


@pytest.mark.integration
@pytest.mark.auth
class TestCreatePermissionCommand:

    @pytest.mark.asyncio
    async def test_create_permission_success(
        self,
        db_session: AsyncSession,
        permission_repository: PermissionRepository,
        rbac_manager: RBACManager,
        admin_user: User,
    ) -> None:
        handler = CreatePermissionCommandHandler(
            session=db_session,
            permission_repository=permission_repository,
            rbac_manager=rbac_manager,
        )

        user_jwt = UserJWTData.create_from_user(admin_user)

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
        permission_repository: PermissionRepository,
        rbac_manager: RBACManager,
        admin_user: User,
    ) -> None:
        perm = Permission(name="duplicate:perm")
        db_session.add(perm)
        await db_session.commit()

        handler = CreatePermissionCommandHandler(
            session=db_session,
            permission_repository=permission_repository,
            rbac_manager=rbac_manager,
        )

        user_jwt = UserJWTData.create_from_user(admin_user)

        command = CreatePermissionCommand(
            name="duplicate:perm",
            user_jwt_data=user_jwt,
        )

        with pytest.raises(NotFoundPermissionsException):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_create_permission_insufficient_permissions(
        self,
        db_session: AsyncSession,
        permission_repository: PermissionRepository,
        rbac_manager: RBACManager,
        standard_user: User,
    ) -> None:
        handler = CreatePermissionCommandHandler(
            session=db_session,
            permission_repository=permission_repository,
            rbac_manager=rbac_manager,
        )

        user_jwt = UserJWTData.create_from_user(standard_user)

        command = CreatePermissionCommand(
            name="new:permission",
            user_jwt_data=user_jwt,
        )

        with pytest.raises(AccessDeniedException):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_delete_permission_success(
        self,
        db_session: AsyncSession,
        permission_repository: PermissionRepository,
        admin_user: User,
        permission_blacklist: PermissionInvalidateRepository,
        rbac_manager: RBACManager,
    ) -> None:
        perm = Permission(name="deletable:perm")
        db_session.add(perm)
        await db_session.commit()

        handler = DeletePermissionCommandHandler(
            session=db_session,
            permission_repository=permission_repository,
            rbac_manager=rbac_manager,
            permission_blacklist=permission_blacklist,
        )

        user_jwt = UserJWTData.create_from_user(admin_user)

        command = DeletePermissionCommand(
            name="deletable:perm",
            user_jwt_data=user_jwt,
        )

        await handler.handle(command)
        await db_session.commit()

        deleted_perm = await permission_repository.get_permission_by_name("deletable:perm")
        assert deleted_perm is None

    @pytest.mark.asyncio
    async def test_delete_protected_permission(
        self,
        db_session: AsyncSession,
        admin_user: User,
        rbac_manager: RBACManager,
        permission_repository: PermissionRepository,
        permission_blacklist: PermissionInvalidateRepository
    ) -> None:
        handler = DeletePermissionCommandHandler(
            session=db_session,
            permission_repository=permission_repository,
            rbac_manager=rbac_manager,
            permission_blacklist=permission_blacklist,
        )

        user_jwt = UserJWTData.create_from_user(admin_user)

        command = DeletePermissionCommand(
            name="role:create",
            user_jwt_data=user_jwt,
        )

        with pytest.raises(ProtectedPermissionException):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_delete_permission_insufficient_permissions(
        self,
        db_session: AsyncSession,
        standard_user: User,
        permission_repository: PermissionRepository,
        rbac_manager: RBACManager,
        permission_blacklist: PermissionInvalidateRepository
    ) -> None:
        perm = Permission(name="deletable:perm")
        db_session.add(perm)
        await db_session.commit()

        handler = DeletePermissionCommandHandler(
            session=db_session,
            permission_repository=permission_repository,
            rbac_manager=rbac_manager,
            permission_blacklist=permission_blacklist,
        )

        user_jwt = UserJWTData.create_from_user(standard_user)

        command = DeletePermissionCommand(
            name="deletable:perm",
            user_jwt_data=user_jwt,
        )

        with pytest.raises(AccessDeniedException):
            await handler.handle(command)
