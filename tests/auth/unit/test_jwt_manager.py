import pytest
from jose import jwt

from app.auth.dtos.tokens import TokenType
from app.auth.dtos.user import AuthUserJWTData
from app.auth.services.jwt import AuthJWTManager
from app.core.services.auth.dto import JwtTokenType
from app.core.services.auth.exceptions import ExpiredTokenException, InvalidTokenException
from tests.auth.integration.factories import TokenFactory


@pytest.mark.unit
@pytest.mark.auth
class TestJWTManager:

    def test_create_token_pair(self, auth_jwt_manager: AuthJWTManager, admin_auth_user_jwt: AuthUserJWTData):
        token_group = auth_jwt_manager.create_token_pair(admin_auth_user_jwt)

        assert token_group.access_token, "access token must be created"
        assert token_group.refresh_token, "refresh token must be created"

        access_payload = auth_jwt_manager.decode(token_group.access_token)
        assert access_payload["type"] == "access"
        assert access_payload["sub"] == admin_auth_user_jwt.id
        assert access_payload["roles"] == admin_auth_user_jwt.roles
        assert access_payload["permissions"] == admin_auth_user_jwt.permissions

        refresh_payload = auth_jwt_manager.decode(token_group.refresh_token)
        assert refresh_payload["type"] == "refresh"
        assert refresh_payload["sub"] == admin_auth_user_jwt.id

    @pytest.mark.asyncio
    async def test_validate_valid_token(self, auth_jwt_manager: AuthJWTManager, admin_auth_user_jwt: AuthUserJWTData):
        token_group = auth_jwt_manager.create_token_pair(admin_auth_user_jwt)

        token_data = await auth_jwt_manager.validate_token(token_group.access_token, JwtTokenType.ACCESS)

        assert token_data.sub == admin_auth_user_jwt.id
        assert str(token_data.type).lower() == "access"
        assert token_data.roles == admin_auth_user_jwt.roles
        assert token_data.permissions == admin_auth_user_jwt.permissions

    @pytest.mark.asyncio
    async def test_validate_wrong_token_type(self, auth_jwt_manager: AuthJWTManager, regular_auth_user_jwt: AuthUserJWTData):
        token_group = auth_jwt_manager.create_token_pair(regular_auth_user_jwt)

        with pytest.raises(InvalidTokenException):
            await auth_jwt_manager.validate_token(token_group.refresh_token, JwtTokenType.ACCESS)

    @pytest.mark.asyncio
    async def test_validate_invalid_token(self, auth_jwt_manager: AuthJWTManager):
        invalid_token = "invalid.token.here"

        with pytest.raises(InvalidTokenException):
            await auth_jwt_manager.validate_token(invalid_token, JwtTokenType.ACCESS)

    @pytest.mark.asyncio
    async def test_validate_expired_token(self, auth_jwt_manager: AuthJWTManager):
        payload = TokenFactory.create_access_token_payload(
            user_id=123,
            exp_minutes=-1,
        )
        expired_token = jwt.encode(payload, auth_jwt_manager.jwt_secret, algorithm=auth_jwt_manager.jwt_algorithm)

        with pytest.raises(ExpiredTokenException):
            await auth_jwt_manager.validate_token(expired_token, JwtTokenType.ACCESS)

    def test_generate_payload_access_token(self, auth_jwt_manager: AuthJWTManager, admin_auth_user_jwt: AuthUserJWTData):
        payload = auth_jwt_manager.generate_payload(admin_auth_user_jwt, TokenType.ACCESS)

        assert payload["type"] == "access"
        assert payload["sub"] == admin_auth_user_jwt.id
        assert payload["lvl"] == admin_auth_user_jwt.security_level
        assert payload["did"] == admin_auth_user_jwt.device_id
        assert "jti" in payload
        assert "exp" in payload
        assert "iat" in payload
        assert payload["roles"] == admin_auth_user_jwt.roles
        assert payload["permissions"] == admin_auth_user_jwt.permissions

    def test_generate_payload_refresh_token(self, auth_jwt_manager: AuthJWTManager, regular_auth_user_jwt: AuthUserJWTData):
        payload = auth_jwt_manager.generate_payload(regular_auth_user_jwt, TokenType.REFRESH)

        assert payload["type"] == "refresh"
        assert payload["sub"] == regular_auth_user_jwt.id
        assert payload["lvl"] == regular_auth_user_jwt.security_level
        assert payload["did"] == regular_auth_user_jwt.device_id
        assert "jti" in payload
        assert "exp" in payload
        assert "iat" in payload

        assert "roles" not in payload
        assert "permissions" not in payload
