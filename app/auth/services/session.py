from dataclasses import dataclass

import orjson

from app.auth.models.session import Session
from app.auth.repositories.session import SessionRepository
from app.auth.schemas.token import DeviceInfo
from app.auth.services.device import generate_device_info
from app.core.utils import now_utc


@dataclass
class SessionManager:
    session_repository: SessionRepository

    async def get_or_create_session(self, user_id: int, user_agent: str) -> Session:
        device_data = generate_device_info(user_agent)

        if existing_session := await self.get_user_session(
            user_id=user_id, device_id=device_data.device_id
        ):
            return existing_session

        session = Session(
            user_id=user_id,
            device_id=device_data.device_id,
            device_info=device_data.device_info,
            user_agent=device_data.user_agent,
        )

        await self.session_repository.create(session=session)

        return session

    async def get_user_session(
        self, user_id: int, device_id: str
    ) -> Session | None:
        active_session = await self.session_repository.get_by_device(
            user_id=user_id,
            device_id=device_id,
        )

        if active_session:
            active_session.last_activity = now_utc()
            return active_session

        return active_session

