import pytest
from httpx import AsyncClient

from app.auth.models.user import User


@pytest.mark.integration
@pytest.mark.auth
class TestAuthEndpoints:

    @pytest.mark.asyncio
    async def test_register_endpoint(
        self,
        client: AsyncClient,
    ):
        response = await client.post(
            "/api/v1/users/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "TestPass123!",
                "password_repeat": "TestPass123!"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_register_duplicate_email(
        self,
        client: AsyncClient,
        standard_user: User,
    ) -> None:
        response = await client.post(
            "/api/v1/users/register",
            json={
                "username": "anotheruser",
                "email": standard_user.email,
                "password": "TestPass123!",
                "password_repeat": "TestPass123!"
            }
        )

        assert response.status_code == 409
        data = response.json()
        assert data["error"]["code"] == "DUPLICATE_USER"

    @pytest.mark.asyncio
    async def test_login_endpoint(
        self,
        client: AsyncClient,
        standard_user: User,
    ) -> None:
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": standard_user.username,
                "password": "TestPass123!"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["access_token"] is not None

        assert "refresh_token" in response.cookies

    @pytest.mark.asyncio
    async def test_login_wrong_password(
        self,
        client: AsyncClient,
        standard_user: User,
    ) -> None:
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": standard_user.username,
                "password": "WrongPassword123!"
            }
        )

        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "WRONG_LOGIN_DATA"

    @pytest.mark.asyncio
    async def test_me_endpoint(
        self,
        client: AsyncClient,
        standard_user: User,
        auth_headers,
    ) -> None:
        headers = auth_headers(standard_user)

        response = await client.get(
            "/api/v1/users/me",
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == standard_user.id
        assert data["username"] == standard_user.username
        assert data["email"] == standard_user.email

    @pytest.mark.asyncio
    async def test_me_endpoint_unauthorized(
        self,
        client: AsyncClient,
    ) -> None:
        response = await client.get("/api/v1/users/me")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_token_endpoint(
        self,
        client: AsyncClient,
        standard_user: User,
        auth_headers
    ) -> None:

        login_response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": standard_user.username,
                "password": "TestPass123!"
            }
        )

        assert login_response.status_code == 200

        cookies = login_response.cookies
        refresh_token = cookies.get("refresh_token")
        assert refresh_token is not None

        headers = auth_headers(standard_user)
        response = await client.post(
            "/api/v1/auth/refresh",
            cookies={"refresh_token": refresh_token},
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["access_token"] != login_response.json()["access_token"]

    @pytest.mark.asyncio
    async def test_logout_endpoint(
        self,
        client: AsyncClient,
        standard_user: User,
    ) -> None:

        login_response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": standard_user.email,
                "password": "TestPass123!"
            }
        )

        cookies = login_response.cookies
        refresh_token = cookies.get("refresh_token")
        assert refresh_token is not None

        response = await client.post(
            "/api/v1/auth/logout",
            cookies={"refresh_token": refresh_token},
        )

        assert response.status_code == 204

        refresh_response = await client.post(
            "/api/v1/auth/refresh",
            cookies=cookies
        )

        assert refresh_response.status_code in [400, 401]

