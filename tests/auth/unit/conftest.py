from typing import Callable
import pytest

from app.auth.dtos.user import AuthUserJWTData


@pytest.fixture
def make_auth_user_jwt() -> Callable[..., AuthUserJWTData]:
    def _make_user_jwt(
        *,
        id: str = "1",
        username: str = "test",
        role: str = "user",
        permissions: list[str] | None = None,
        security_level: int = 1,
        device_id: str = "device_1",
    ) -> AuthUserJWTData:
        return AuthUserJWTData(
            id=id,
            username=username,
            roles=[role],
            permissions=permissions or [],
            security_level=security_level,
            device_id=device_id,
        )

    return _make_user_jwt


@pytest.fixture
def regular_auth_user_jwt(make_auth_user_jwt: Callable[..., AuthUserJWTData]) -> AuthUserJWTData:
    return make_auth_user_jwt()


@pytest.fixture
def admin_auth_user_jwt(make_auth_user_jwt: Callable[..., AuthUserJWTData]) -> AuthUserJWTData:
    return make_auth_user_jwt(
        id="2",
        role="super_admin",
        permissions=["user:create", "user:delete", "role:create"],
        security_level=10,
        device_id="device_2",
    )


@pytest.fixture
def system_auth_user_jwt(make_auth_user_jwt: Callable[..., AuthUserJWTData]) -> AuthUserJWTData:
    return make_auth_user_jwt(
        id="3",
        role="system_admin",
        permissions=["user:create", "user:delete", "role:create"],
        security_level=9,
        device_id="device_2",
    )

