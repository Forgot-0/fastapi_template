import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models.user import User
from tests.auth.integration.factories import SessionFactory
from tests.support.http import api_path


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.asyncio
class TestSessionEndpoints:

    async def test_get_sessions_endpoint(
        self,
        client: AsyncClient,
        admin_user: User,
        auth_headers,
    ) -> None:
        headers = auth_headers(admin_user)

        response = await client.get(
            api_path("sessions/"),
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    async def test_deactivate_session_endpoint(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        standard_user: User,
        auth_headers,
    ) -> None:
        test_session = SessionFactory.create(user_id=standard_user.id)
        db_session.add(test_session)
        await db_session.commit()

        headers = auth_headers(standard_user)

        response = await client.delete(
            api_path(f"sessions/{test_session.id}"),
            headers=headers
        )

        assert response.status_code == 204
