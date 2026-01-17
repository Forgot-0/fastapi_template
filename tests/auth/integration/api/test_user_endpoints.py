from httpx import AsyncClient
import pytest

from app.auth.models.user import User


@pytest.mark.integration
@pytest.mark.auth
class TestUserEndpoints:

    @pytest.mark.asyncio
    async def test_get_users_list_endpoint(
        self,
        client: AsyncClient,
        admin_user: User,
        standard_user: User,
        auth_headers,
    ) -> None:
        headers = auth_headers(admin_user)

        response = await client.get(
            "/api/v1/users/",
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "page" in data
        assert len(data["items"]) >= 2

    @pytest.mark.asyncio
    async def test_get_users_list_unauthorized(
        self,
        client: AsyncClient,
        standard_user: User,
        auth_headers,
    ) -> None:
        headers = auth_headers(standard_user)

        response = await client.get(
            "/api/v1/users/",
            headers=headers
        )

        assert response.status_code == 403
