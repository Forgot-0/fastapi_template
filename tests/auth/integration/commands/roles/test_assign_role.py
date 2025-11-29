import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.commands.roles.assign_role_to_user import AssignRoleCommand, AssignRoleCommandHandler
from app.auth.commands.roles.remove_role_user import RemoveRoleCommand, RemoveRoleCommandHandler
from app.auth.exceptions import AccessDeniedException, NotFoundRoleException, NotFoundUserException
from app.auth.models.role import Role
from app.auth.models.user import User
from app.auth.repositories.permission import PermissionRepository
from app.auth.repositories.role import RoleRepository
from app.auth.repositories.session import TokenBlacklistRepository
from app.auth.repositories.user import UserRepository
from app.auth.schemas.user import UserJWTData
from app.auth.services.rbac import RBACManager
from tests.auth.integration.factories import RoleFactory, UserFactory


@pytest.mark.integration
@pytest.mark.auth
class TestAssignRoleCommand:

    @pytest.mark.asyncio
    async def test_assign_role_success(
        self,
        db_session: AsyncSession,
        rbac_manager: RBACManager,
        role_repository: RoleRepository,
        user_repository: UserRepository,
        permission_repository: PermissionRepository,
        token_blacklist_repository: TokenBlacklistRepository,
        admin_user: User,
        standard_user: User,
    ) -> None:
        test_role = RoleFactory.create(name="test_assignable_role", security_level=2)
        db_session.add(test_role)
        await db_session.commit()

        handler = AssignRoleCommandHandler(
            session=db_session,
            role_repository=role_repository,
            user_repository=user_repository,
            permission_repository=permission_repository,
            rbac_manager=rbac_manager,
            token_blacklist=token_blacklist_repository,
        )

        user_jwt = UserJWTData.create_from_user(admin_user)

        command = AssignRoleCommand(
            assign_to_user=standard_user.id,
            role_name="test_assignable_role",
            user_jwt_data=user_jwt,
        )

        await handler.handle(command)
        await db_session.commit()

        updated_user = await user_repository.get_user_with_permission_by_id(standard_user.id)
        assert updated_user is not None
        role_names = {r.name for r in updated_user.roles}
        assert "test_assignable_role" in role_names

    @pytest.mark.asyncio
    async def test_assign_role_nonexistent_user(
        self,
        db_session: AsyncSession,
        rbac_manager: RBACManager,
        role_repository: RoleRepository,
        user_repository: UserRepository,
        permission_repository: PermissionRepository,
        token_blacklist_repository: TokenBlacklistRepository,
        admin_user: User,
    ) -> None:
        test_role = RoleFactory.create(name="test_role_ne", security_level=2)
        db_session.add(test_role)
        await db_session.commit()

        handler = AssignRoleCommandHandler(
            session=db_session,
            role_repository=role_repository,
            user_repository=user_repository,
            permission_repository=permission_repository,
            rbac_manager=rbac_manager,
            token_blacklist=token_blacklist_repository,
        )

        user_jwt = UserJWTData.create_from_user(admin_user)

        command = AssignRoleCommand(
            assign_to_user=99999,
            role_name="test_role_ne",
            user_jwt_data=user_jwt,
        )

        with pytest.raises(NotFoundUserException):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_assign_nonexistent_role(
        self,
        db_session: AsyncSession,
        rbac_manager: RBACManager,
        role_repository: RoleRepository,
        user_repository: UserRepository,
        permission_repository: PermissionRepository,
        token_blacklist_repository: TokenBlacklistRepository,
        admin_user: User,
        standard_user: User,
    ) -> None:
        handler = AssignRoleCommandHandler(
            session=db_session,
            role_repository=role_repository,
            user_repository=user_repository,
            permission_repository=permission_repository,
            rbac_manager=rbac_manager,
            token_blacklist=token_blacklist_repository,
        )

        user_jwt = UserJWTData.create_from_user(admin_user)

        command = AssignRoleCommand(
            assign_to_user=standard_user.id,
            role_name="nonexistent_role",
            user_jwt_data=user_jwt,
        )

        with pytest.raises(NotFoundRoleException):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_assign_role_insufficient_permissions(
        self,
        db_session: AsyncSession,
        rbac_manager: RBACManager,
        role_repository: RoleRepository,
        user_repository: UserRepository,
        permission_repository: PermissionRepository,
        token_blacklist_repository: TokenBlacklistRepository,
        standard_user: User,
    ) -> None:
        test_role = RoleFactory.create(name="test_role_ip", security_level=2)
        db_session.add(test_role)
        await db_session.flush()

        another_user = UserFactory.create_verified(
            email="another@example.com",
            username="anotheruser",
            roles={test_role}
        )
        db_session.add(another_user)
        await db_session.commit()

        handler = AssignRoleCommandHandler(
            session=db_session,
            role_repository=role_repository,
            user_repository=user_repository,
            permission_repository=permission_repository,
            rbac_manager=rbac_manager,
            token_blacklist=token_blacklist_repository,
        )

        user_jwt = UserJWTData.create_from_user(standard_user)

        command = AssignRoleCommand(
            assign_to_user=another_user.id,
            role_name="test_role_ip",
            user_jwt_data=user_jwt,
        )

        with pytest.raises(AccessDeniedException):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_remove_role_success(
        self,
        db_session: AsyncSession,
        rbac_manager: RBACManager,
        role_repository: RoleRepository,
        user_repository: UserRepository,
        permission_repository: PermissionRepository,
        token_blacklist_repository: TokenBlacklistRepository,
        admin_user: User,
    ) -> None:

        test_role = RoleFactory.create(name="removable_role", security_level=2)
        db_session.add(test_role)
        await db_session.flush()

        test_user = UserFactory.create_verified(
            email="hasrole@example.com",
            username="hasroleuser",
            roles={test_role}
        )
        db_session.add(test_user)
        await db_session.commit()

        handler = RemoveRoleCommandHandler(
            session=db_session,
            user_repository=user_repository,
            role_repository=role_repository,
            permission_repository=permission_repository,
            rbac_manager=rbac_manager,
            token_blacklist=token_blacklist_repository,
        )

        user_jwt = UserJWTData.create_from_user(admin_user)

        command = RemoveRoleCommand(
            remove_from_user=test_user.id,
            role_name="removable_role",
            user_jwt_data=user_jwt,
        )

        await handler.handle(command)
        await db_session.commit()

        updated_user = await user_repository.get_user_with_permission_by_id(test_user.id)
        assert updated_user is not None

        role_names = {r.name for r in updated_user.roles}
        assert "removable_role" not in role_names