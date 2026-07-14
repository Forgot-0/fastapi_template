import pytest

from app.auth.dtos.user import AuthUserJWTData
from app.auth.exceptions import (
    InvalidRoleNameError,
    ProtectedPermissionError,
)
from app.auth.services.rbac import AuthRBACManager
from app.core.services.auth.exceptions import AccessDeniedError


@pytest.mark.unit
@pytest.mark.auth
class TestRBACManager:

    @pytest.mark.parametrize(
        "user_perms, required_perms, expected",
        [
            (["user:view"], {"user:view"}, True),
            (["user:view"], {"user:delete"}, False),
            (["user:view", "user:update"], {"user:view", "user:update"}, True),
            (["user:view"], {"user:view", "user:delete"}, False),
            ([], set(), True),
        ],
    )
    def test_check_permission_various(
        self,
        rbac_manager: AuthRBACManager,
        make_auth_user_jwt,
        user_perms: list[str],
        required_perms: set[str],
        expected: bool,
    ) -> None:
        user = make_auth_user_jwt(role="user", permissions=user_perms)
        assert rbac_manager.check_permission(user, required_perms) is expected

    @pytest.mark.parametrize(
        "role_name,expected",
        [
            ("user", False),
            ("moderator", False),
            ("super_admin", True),
            ("system_admin", True),
        ],
    )
    def test_is_system_user_various_roles(
        self,
        rbac_manager: AuthRBACManager,
        make_auth_user_jwt,
        role_name: str,
        expected: bool,
    ) -> None:
        user = make_auth_user_jwt(role=role_name, permissions=[])
        assert rbac_manager.is_system_user(user) == expected

    def test_is_system_user_specific_fixtures(
        self,
        rbac_manager: AuthRBACManager,
        admin_auth_user_jwt: AuthUserJWTData,
        system_auth_user_jwt: AuthUserJWTData,
        regular_auth_user_jwt: AuthUserJWTData,
    ) -> None:
        assert rbac_manager.is_system_user(admin_auth_user_jwt) is True
        assert rbac_manager.is_system_user(system_auth_user_jwt) is True
        assert rbac_manager.is_system_user(regular_auth_user_jwt) is False

    def test_system_user_bypasses_permission_check(
        self,
        rbac_manager: AuthRBACManager,
        admin_auth_user_jwt: AuthUserJWTData,
    ) -> None:
        assert rbac_manager.check_permission(admin_auth_user_jwt, {"any:permission"}) is True

    @pytest.mark.parametrize(
        "user_level, role_level, should_raise",
        [
            (10, 5, False),
            (5, 5, True),
            (3, 5, True),
            (10, 0, True),
        ],
    )
    def test_check_security_level_cases(
        self,
        rbac_manager: AuthRBACManager,
        user_level: int,
        role_level: int,
        should_raise: bool,
    ) -> None:
        if should_raise:
            with pytest.raises(AccessDeniedError):
                rbac_manager.check_security_level(user_level=user_level, role_level=role_level)
        else:
            rbac_manager.check_security_level(user_level=user_level, role_level=role_level)

    def test_validate_role_name_valid_and_invalid(
        self,
        rbac_manager: AuthRBACManager,
        admin_auth_user_jwt: AuthUserJWTData,
        regular_auth_user_jwt: AuthUserJWTData,
    ) -> None:
        rbac_manager.validate_role_name(admin_auth_user_jwt, "custom_role")

        with pytest.raises(InvalidRoleNameError):
            rbac_manager.validate_role_name(admin_auth_user_jwt, "ab")

        with pytest.raises(InvalidRoleNameError):
            rbac_manager.validate_role_name(admin_auth_user_jwt, "a" * 30)

        with pytest.raises(AccessDeniedError):
            rbac_manager.validate_role_name(regular_auth_user_jwt, "system_custom")

        rbac_manager.validate_role_name(admin_auth_user_jwt, "system_custom")

        with pytest.raises(AccessDeniedError):
            rbac_manager.validate_role_name(regular_auth_user_jwt, "admin_custom")

    def test_validate_permissions_various(
        self,
        rbac_manager: AuthRBACManager,
        make_auth_user_jwt,
        regular_auth_user_jwt: AuthUserJWTData,
        admin_auth_user_jwt: AuthUserJWTData,
    ) -> None:
        with pytest.raises(ProtectedPermissionError):
            rbac_manager.validate_permissions(regular_auth_user_jwt, "role:create")

        rbac_manager.validate_permissions(admin_auth_user_jwt, "role:create")

        with pytest.raises(AccessDeniedError):
            rbac_manager.validate_permissions(regular_auth_user_jwt, "user:delete")

        user_with_perm = make_auth_user_jwt(role="user", permissions=["user:delete"])
        rbac_manager.validate_permissions(user_with_perm, "user:delete")
