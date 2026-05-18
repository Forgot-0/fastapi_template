import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.commands.roles.assign_role_to_user import AssignRoleCommand, AssignRoleCommandHandler
from app.auth.commands.roles.remove_role_user import RemoveRoleCommand, RemoveRoleCommandHandler
from app.auth.exceptions import NotFoundRoleException, NotFoundUserException
from app.auth.models.user import User
from app.auth.repositories.permission import PermissionRepository
from app.auth.repositories.role import RoleRepository
from app.auth.repositories.session import TokenBlacklistRepository
from app.auth.repositories.user import UserRepository
from app.auth.services.rbac import AuthRBACManager
from app.core.services.auth.exceptions import AccessDeniedException
from tests.auth.integration.factories import RoleFactory, UserFactory
from tests.support.jwt import jwt_from_user


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.asyncio
class TestAssignRoleCommand:
    @pytest.fixture
    def assign_role_handler(
        self,
        db_session: AsyncSession,
        role_repository: RoleRepository,
        user_repository: UserRepository,
        permission_repository: PermissionRepository,
        rbac_manager: AuthRBACManager,
        token_blacklist_repository: TokenBlacklistRepository,
    ) -> AssignRoleCommandHandler:
        return AssignRoleCommandHandler(
            session=db_session,
            role_repository=role_repository,
            user_repository=user_repository,
            permission_repository=permission_repository,
            rbac_manager=rbac_manager,
            token_blacklist=token_blacklist_repository,
        )

    @pytest.fixture
    def remove_role_handler(
        self,
        db_session: AsyncSession,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        permission_repository: PermissionRepository,
        rbac_manager: AuthRBACManager,
        token_blacklist_repository: TokenBlacklistRepository,
    ) -> RemoveRoleCommandHandler:
        return RemoveRoleCommandHandler(
            session=db_session,
            user_repository=user_repository,
            role_repository=role_repository,
            permission_repository=permission_repository,
            rbac_manager=rbac_manager,
            token_blacklist=token_blacklist_repository,
        )

    async def test_assign_role_success(
        self,
        db_session: AsyncSession,
        user_repository: UserRepository,
        assign_role_handler: AssignRoleCommandHandler,
        admin_user: User,
        standard_user: User,
    ) -> None:
        test_role = RoleFactory.create(name="test_assignable_role", security_level=2)
        db_session.add(test_role)
        await db_session.commit()

        user_jwt = jwt_from_user(admin_user)

        command = AssignRoleCommand(
            assign_to_user=standard_user.id,
            role_name="test_assignable_role",
            user_jwt_data=user_jwt,
        )

        await assign_role_handler.handle(command)
        await db_session.commit()

        updated_user = await user_repository.get_user_with_permission_by_id(standard_user.id)
        assert updated_user is not None
        role_names = {r.name for r in updated_user.roles}
        assert "test_assignable_role" in role_names

    async def test_assign_role_nonexistent_user(
        self,
        db_session: AsyncSession,
        assign_role_handler: AssignRoleCommandHandler,
        admin_user: User,
    ) -> None:
        test_role = RoleFactory.create(name="test_role_ne", security_level=2)
        db_session.add(test_role)
        await db_session.commit()

        user_jwt = jwt_from_user(admin_user)

        command = AssignRoleCommand(
            assign_to_user=99999,
            role_name="test_role_ne",
            user_jwt_data=user_jwt,
        )

        with pytest.raises(NotFoundUserException):
            await assign_role_handler.handle(command)

    async def test_assign_nonexistent_role(
        self,
        assign_role_handler: AssignRoleCommandHandler,
        admin_user: User,
        standard_user: User,
    ) -> None:
        user_jwt = jwt_from_user(admin_user)

        command = AssignRoleCommand(
            assign_to_user=standard_user.id,
            role_name="nonexistent_role",
            user_jwt_data=user_jwt,
        )

        with pytest.raises(NotFoundRoleException):
            await assign_role_handler.handle(command)

    async def test_assign_role_insufficient_permissions(
        self,
        db_session: AsyncSession,
        assign_role_handler: AssignRoleCommandHandler,
        standard_user: User,
    ) -> None:
        test_role = RoleFactory.create(name="test_role_ip", security_level=2)
        db_session.add(test_role)
        await db_session.flush()

        another_user = UserFactory.create_verified(
            email="another@example.com",
            username="anotheruser",
            roles={test_role},
        )
        db_session.add(another_user)
        await db_session.commit()

        user_jwt = jwt_from_user(standard_user)

        command = AssignRoleCommand(
            assign_to_user=another_user.id,
            role_name="test_role_ip",
            user_jwt_data=user_jwt,
        )

        with pytest.raises(AccessDeniedException):
            await assign_role_handler.handle(command)

    async def test_remove_role_success(
        self,
        db_session: AsyncSession,
        user_repository: UserRepository,
        remove_role_handler: RemoveRoleCommandHandler,
        admin_user: User,
    ) -> None:
        test_role = RoleFactory.create(name="removable_role", security_level=2)
        db_session.add(test_role)
        await db_session.flush()

        test_user = UserFactory.create_verified(
            email="hasrole@example.com",
            username="hasroleuser",
            roles={test_role},
        )
        db_session.add(test_user)
        await db_session.commit()

        user_jwt = jwt_from_user(admin_user)

        command = RemoveRoleCommand(
            remove_from_user=test_user.id,
            role_name="removable_role",
            user_jwt_data=user_jwt,
        )

        await remove_role_handler.handle(command)
        await db_session.commit()

        updated_user = await user_repository.get_user_with_permission_by_id(test_user.id)
        assert updated_user is not None

        role_names = {r.name for r in updated_user.roles}
        assert "removable_role" not in role_names

    async def test_assign_multiple_roles(
        self,
        db_session: AsyncSession,
        user_repository: UserRepository,
        assign_role_handler: AssignRoleCommandHandler,
        admin_user: User,
        standard_user: User,
    ) -> None:
        role1 = RoleFactory.create(name="role_one", security_level=2)
        role2 = RoleFactory.create(name="role_two", security_level=3)
        db_session.add_all([role1, role2])
        await db_session.commit()

        user_jwt = jwt_from_user(admin_user)

        command1 = AssignRoleCommand(
            assign_to_user=standard_user.id,
            role_name="role_one",
            user_jwt_data=user_jwt,
        )
        await assign_role_handler.handle(command1)
        await db_session.commit()

        command2 = AssignRoleCommand(
            assign_to_user=standard_user.id,
            role_name="role_two",
            user_jwt_data=user_jwt,
        )
        await assign_role_handler.handle(command2)
        await db_session.commit()

        updated_user = await user_repository.get_user_with_permission_by_id(standard_user.id)
        assert updated_user is not None
        role_names = {r.name for r in updated_user.roles}
        assert "role_one" in role_names
        assert "role_two" in role_names

    async def test_remove_role_user_without_role(
        self,
        db_session: AsyncSession,
        remove_role_handler: RemoveRoleCommandHandler,
        admin_user: User,
        standard_user: User,
    ) -> None:
        test_role = RoleFactory.create(name="nonexistent_on_user", security_level=2)
        db_session.add(test_role)
        await db_session.commit()

        user_jwt = jwt_from_user(admin_user)

        command = RemoveRoleCommand(
            remove_from_user=standard_user.id,
            role_name="nonexistent_on_user",
            user_jwt_data=user_jwt,
        )

        with pytest.raises(Exception):
            await remove_role_handler.handle(command)

    async def test_assign_role_same_role_twice(
        self,
        db_session: AsyncSession,
        user_repository: UserRepository,
        assign_role_handler: AssignRoleCommandHandler,
        admin_user: User,
        standard_user: User,
    ) -> None:
        test_role = RoleFactory.create(name="duplicate_assign", security_level=2)
        db_session.add(test_role)
        await db_session.commit()

        user_jwt = jwt_from_user(admin_user)

        command = AssignRoleCommand(
            assign_to_user=standard_user.id,
            role_name="duplicate_assign",
            user_jwt_data=user_jwt,
        )

        await assign_role_handler.handle(command)
        await db_session.commit()

        await assign_role_handler.handle(command)
        await db_session.commit()

        updated_user = await user_repository.get_user_with_permission_by_id(standard_user.id)
        assert updated_user is not None

        role_count = sum(1 for r in updated_user.roles if r.name == "duplicate_assign")
        assert role_count == 1

    async def test_remove_role_insufficient_permissions(
        self,
        db_session: AsyncSession,
        remove_role_handler: RemoveRoleCommandHandler,
        standard_user: User,
    ) -> None:
        test_role = RoleFactory.create(name="removable_protected", security_level=2)
        db_session.add(test_role)
        await db_session.flush()

        target_user = UserFactory.create_verified(
            email="target@example.com",
            username="targetuser",
            roles={test_role},
        )
        db_session.add(target_user)
        await db_session.commit()

        user_jwt = jwt_from_user(standard_user)

        command = RemoveRoleCommand(
            remove_from_user=target_user.id,
            role_name="removable_protected",
            user_jwt_data=user_jwt,
        )

        with pytest.raises(AccessDeniedException):
            await remove_role_handler.handle(command)
