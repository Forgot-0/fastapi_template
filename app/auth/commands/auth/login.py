from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.config import auth_config
from app.auth.repositories.token import TokenRepository
from app.auth.repositories.user import UserRepository
from app.auth.schemas.token import RefreshTokenCreate, TokenGroup
from app.auth.security import create_access_token, create_refresh_token, verify_password
from app.auth.services.tokens import AuthService
from app.core.commands import BaseCommand, BaseCommandHandler


@dataclass(frozen=True)
class LoginCommand(BaseCommand):
    username: str
    password: str


@dataclass(frozen=True)
class LoginCommandHandler(BaseCommandHandler[LoginCommand, TokenGroup]):
    session: AsyncSession
    auth_service: AuthService

    async def handle(self, command: LoginCommand) -> TokenGroup:
        token_group = await self.auth_service.login(
            username=command.username,
            password=command.password
        )
        await self.session.commit()
        return token_group