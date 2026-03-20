from typing import Callable
import pytest

from app.auth.dtos.user import AuthUserJWTData



@pytest.fixture
def regular_user_jwt(make_user_jwt: Callable[..., AuthUserJWTData]) -> AuthUserJWTData:
    return make_user_jwt()


@pytest.fixture
def admin_user_jwt(make_user_jwt: Callable[..., AuthUserJWTData]) -> AuthUserJWTData:
    return make_user_jwt(
        id="2",
        role="super_admin",
        permissions=["user:create", "user:delete", "role:create"],
        security_level=10,
        device_id="device_2",
    )


@pytest.fixture
def system_user_jwt(make_user_jwt: Callable[..., AuthUserJWTData]) -> AuthUserJWTData:
    return make_user_jwt(
        id="3",
        role="system_admin",
        permissions=["user:create", "user:delete", "role:create"],
        security_level=9,
        device_id="device_2",
    )

