from httpx import AsyncClient
import pytest

from app.auth.models.user import User
from tests.support.http import api_path


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.asyncio
class TestUserEndpoints:

    async def test_get_users_list_endpoint(
        self,
        client: AsyncClient,
        admin_user: User,
        standard_user: User,
        auth_headers,
    ) -> None:
        headers = auth_headers(admin_user)

        response = await client.get(
            api_path("users/"),
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "page" in data
        assert len(data["items"]) >= 2

    async def test_get_users_list_unauthorized(
        self,
        client: AsyncClient,
        standard_user: User,
        auth_headers,
    ) -> None:
        headers = auth_headers(standard_user)

        response = await client.get(
            api_path("users/"),
            headers=headers
        )

        assert response.status_code == 403
