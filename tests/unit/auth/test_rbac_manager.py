# tests/unit/auth/test_rbac_manager.py
import pytest

from app.auth.exceptions import AccessDeniedException, InvalidRoleNameException, ProtectedPermissionException
from app.auth.schemas.user import UserJWTData
from app.auth.services.rbac import RBACManager


@pytest.mark.unit
@pytest.mark.auth
class TestRBACManager:

    def test_check_permission_has_permission(self, rbac_manager: RBACManager, regular_user_jwt: UserJWTData):
        result = rbac_manager.check_permission(regular_user_jwt, {"user:view"})

        assert result is True

    def test_check_permission_missing_permission(self, rbac_manager: RBACManager, regular_user_jwt: UserJWTData):
        result = rbac_manager.check_permission(regular_user_jwt, {"user:delete"})

        assert result is False

    def test_check_multiple_permissions_all_present(self, rbac_manager: RBACManager):
        user = UserJWTData(
            id="1",
            roles=["user"],
            permissions=["user:view", "user:update"],
            security_level=1
        )

        result = rbac_manager.check_permission(user, {"user:view", "user:update"})

        assert result is True

    def test_check_multiple_permissions_one_missing(self, rbac_manager: RBACManager):
        user = UserJWTData(
            id="1",
            roles=["user"],
            permissions=["user:view"],
            security_level=1
        )

        result = rbac_manager.check_permission(user, {"user:view", "user:delete"})

        assert result is False

    def test_is_system_user_super_admin(self, rbac_manager: RBACManager):
        user = UserJWTData(
            id="1",
            roles=["super_admin"],
            permissions=[],
            security_level=10
        )

        result = rbac_manager.is_system_user(user)

        assert result is True

    def test_is_system_user_system_admin(self, rbac_manager: RBACManager):
        user = UserJWTData(
            id="1",
            roles=["system_admin"],
            permissions=[],
            security_level=9
        )

        result = rbac_manager.is_system_user(user)

        assert result is True

    def test_is_system_user_regular_user(self, rbac_manager: RBACManager, regular_user_jwt: UserJWTData):
        result = rbac_manager.is_system_user(regular_user_jwt)

        assert result is False

    def test_system_user_bypasses_permission_check(self, rbac_manager: RBACManager, admin_user_jwt: UserJWTData):
        result = rbac_manager.check_permission(admin_user_jwt, {"any:permission"})

        assert result is True

    def test_check_security_level_higher_level(self, rbac_manager: RBACManager):
        rbac_manager.check_security_level(user_level=10, role_level=5)

    def test_check_security_level_equal(self, rbac_manager: RBACManager):
        with pytest.raises(AccessDeniedException):
            rbac_manager.check_security_level(user_level=5, role_level=5)

    def test_check_security_level_lower(self, rbac_manager: RBACManager):
        with pytest.raises(AccessDeniedException):
            rbac_manager.check_security_level(user_level=3, role_level=5)

    def test_check_security_level_zero_role(self, rbac_manager: RBACManager):
        with pytest.raises(AccessDeniedException):
            rbac_manager.check_security_level(user_level=10, role_level=0)

    def test_validate_role_name_valid(self, rbac_manager: RBACManager, admin_user_jwt: UserJWTData):
        rbac_manager.validate_role_name(admin_user_jwt, "custom_role")

    def test_validate_role_name_too_short(self, rbac_manager: RBACManager, admin_user_jwt: UserJWTData):
        with pytest.raises(InvalidRoleNameException):
            rbac_manager.validate_role_name(admin_user_jwt, "ab")

    def test_validate_role_name_too_long(self, rbac_manager: RBACManager, admin_user_jwt: UserJWTData):
        with pytest.raises(InvalidRoleNameException):
            rbac_manager.validate_role_name(admin_user_jwt, "a" * 30)

    def test_validate_role_name_system_prefix_non_admin(self, rbac_manager: RBACManager, regular_user_jwt: UserJWTData):
        with pytest.raises(AccessDeniedException):
            rbac_manager.validate_role_name(regular_user_jwt, "system_custom")

    def test_validate_role_name_system_prefix_admin(self, rbac_manager: RBACManager, admin_user_jwt: UserJWTData):
        rbac_manager.validate_role_name(admin_user_jwt, "system_custom")

    def test_validate_role_name_admin_prefix_non_admin(self, rbac_manager: RBACManager, regular_user_jwt: UserJWTData):
        with pytest.raises(AccessDeniedException):
            rbac_manager.validate_role_name(regular_user_jwt, "admin_custom")

    def test_validate_permissions_protected_non_system(self, rbac_manager: RBACManager, regular_user_jwt: UserJWTData):
        with pytest.raises(ProtectedPermissionException):
            rbac_manager.validate_permissions(regular_user_jwt, "role:create")

    def test_validate_permissions_protected_system_user(self, rbac_manager: RBACManager, admin_user_jwt: UserJWTData):
        rbac_manager.validate_permissions(admin_user_jwt, "role:create")

    def test_validate_permissions_not_owned(self, rbac_manager: RBACManager):
        user = UserJWTData(
            id="1",
            roles=["user"],
            permissions=["user:view"],
            security_level=1
        )

        with pytest.raises(AccessDeniedException):
            rbac_manager.validate_permissions(user, "user:delete")

    def test_validate_permissions_owned(self, rbac_manager: RBACManager):
        user = UserJWTData(
            id="1",
            roles=["user"],
            permissions=["user:delete"],
            security_level=1
        )

        rbac_manager.validate_permissions(user, "user:delete")

    @pytest.mark.parametrize("role_name,expected", [
        ("user", False),
        ("moderator", False),
        ("super_admin", True),
        ("system_admin", True),
    ])
    def test_is_system_user_various_roles(self, rbac_manager: RBACManager, role_name: str, expected: bool):
        user = UserJWTData(
            id="1",
            roles=[role_name],
            permissions=[],
            security_level=1
        )

        result = rbac_manager.is_system_user(user)

        assert result == expected

    def test_check_permission_empty_permissions(self, rbac_manager: RBACManager):
        user = UserJWTData(
            id="1",
            roles=["user"],
            permissions=["user:view"],
            security_level=1
        )

        result = rbac_manager.check_permission(user, set())

        assert result is True