import pytest
from jose import jwt

from app.auth.exceptions import ExpiredTokenException, InvalidTokenException
from app.auth.schemas.tokens import TokenType
from app.auth.schemas.user import UserJWTData
from app.auth.services.jwt import JWTManager
from tests.integration.auth.factories import TokenFactory


@pytest.mark.unit
@pytest.mark.auth
class TestJWTManager:

    def test_create_token_pair(self, jwt_manager: JWTManager):
        user_data = UserJWTData(
            id="123",
            roles=["user"],
            permissions=["user:view"],
            security_level=1,
            device_id="test_device"
        )

        token_group = jwt_manager.create_token_pair(user_data)

        assert token_group.access_token is not None
        assert token_group.refresh_token is not None

        access_payload = jwt.decode(
            token_group.access_token,
            jwt_manager.jwt_secret,
            algorithms=[jwt_manager.jwt_algorithm]
        )
        assert access_payload["type"] == "access"
        assert access_payload["sub"] == "123"
        assert access_payload["roles"] == ["user"]
        assert access_payload["permissions"] == ["user:view"]

        refresh_payload = jwt.decode(
            token_group.refresh_token,
            jwt_manager.jwt_secret,
            algorithms=[jwt_manager.jwt_algorithm]
        )
        assert refresh_payload["type"] == "refresh"
        assert refresh_payload["sub"] == "123"

    @pytest.mark.asyncio
    async def test_validate_valid_token(self, jwt_manager: JWTManager):

        user_data = UserJWTData(
            id="123",
            roles=["user"],
            permissions=["user:view"],
            security_level=1,
            device_id="test_device"
        )
        token_group = jwt_manager.create_token_pair(user_data)

        token_data = await jwt_manager.validate_token(
            token_group.access_token,
            TokenType.ACCESS
        )

        assert token_data.sub == "123"
        assert token_data.type == "access"
        assert token_data.roles == ["user"]
        assert token_data.permissions == ["user:view"]
    
    @pytest.mark.asyncio
    async def test_validate_wrong_token_type(self, jwt_manager: JWTManager):
        user_data = UserJWTData(
            id="123",
            roles=[],
            permissions=[],
            security_level=1,
            device_id="test_device"
        )
        token_group = jwt_manager.create_token_pair(user_data)

        with pytest.raises(InvalidTokenException):
            await jwt_manager.validate_token(
                token_group.refresh_token,
                TokenType.ACCESS
            )

    @pytest.mark.asyncio
    async def test_validate_invalid_token(self, jwt_manager: JWTManager):
        invalid_token = "invalid.token.here"

        with pytest.raises(InvalidTokenException):
            await jwt_manager.validate_token(invalid_token, TokenType.ACCESS)

    @pytest.mark.asyncio
    async def test_validate_expired_token(self, jwt_manager: JWTManager):
        payload = TokenFactory.create_access_token_payload(
            user_id=123,
            exp_minutes=-1
        )
        expired_token = jwt.encode(
            payload,
            jwt_manager.jwt_secret,
            algorithm=jwt_manager.jwt_algorithm
        )

        with pytest.raises(ExpiredTokenException):
            await jwt_manager.validate_token(expired_token, TokenType.ACCESS)

    def test_generate_payload_access_token(self, jwt_manager: JWTManager):
        user_data = UserJWTData(
            id="123",
            roles=["admin"],
            permissions=["user:create", "user:delete"],
            security_level=5,
            device_id="test_device"
        )

        payload = jwt_manager.generate_payload(user_data, TokenType.ACCESS)

        assert payload["type"] == TokenType.ACCESS
        assert payload["sub"] == "123"
        assert payload["lvl"] == 5
        assert payload["did"] == "test_device"
        assert "jti" in payload
        assert "exp" in payload
        assert "iat" in payload
        assert payload["roles"] == ["admin"]
        assert payload["permissions"] == ["user:create", "user:delete"]

    def test_generate_payload_refresh_token(self, jwt_manager: JWTManager):
        user_data = UserJWTData(
            id="456",
            roles=["user"],
            permissions=["user:view"],
            security_level=1,
            device_id="device_123"
        )

        payload = jwt_manager.generate_payload(user_data, TokenType.REFRESH)

        assert payload["type"] == TokenType.REFRESH
        assert payload["sub"] == "456"
        assert payload["lvl"] == 1
        assert payload["did"] == "device_123"
        assert "jti" in payload
        assert "exp" in payload
        assert "iat" in payload

        assert "roles" not in payload
        assert "permissions" not in payload