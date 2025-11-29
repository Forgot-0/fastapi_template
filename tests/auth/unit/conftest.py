import pytest

from app.auth.schemas.user import UserJWTData




@pytest.fixture
def regular_user_jwt() -> UserJWTData:
    return UserJWTData(
        id="1",
        roles=["user"],
        permissions=["user:view"],
        security_level=1,
        device_id="device_1"
    )

@pytest.fixture
def admin_user_jwt() -> UserJWTData:
    return UserJWTData(
        id="2",
        roles=["super_admin"],
        permissions=["user:create", "user:delete", "role:create"],
        security_level=10,
        device_id="device_2"
    )