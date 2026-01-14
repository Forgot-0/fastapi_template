import pytest

from app.auth.dtos.user import AuthUserJWTData





@pytest.fixture
def regular_user_jwt() -> AuthUserJWTData:
    return AuthUserJWTData(
        id="1",
        roles=["user"],
        permissions=["user:view"],
        security_level=1,
        device_id="device_1"
    )

@pytest.fixture
def admin_user_jwt() -> AuthUserJWTData:
    return AuthUserJWTData(
        id="2",
        roles=["super_admin"],
        permissions=["user:create", "user:delete", "role:create"],
        security_level=10,
        device_id="device_2"
    )