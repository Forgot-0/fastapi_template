from dataclasses import dataclass

from app.core.configs.app import app_config
from app.auth.config import auth_config
from app.auth.emails.templates import ResetTokenTemplate, VerifyTokenTemplate
from app.auth.exceptions import AlreadyUserEmail, AlreadyUserUsername, NotFoundUserBy
from app.auth.models.user import User
from app.auth.repositories.user import UserRepository
from app.auth.schemas.user import UserCreate
from app.auth.security import (
    decode_reset_token,
    decode_verify_token,
    generate_reset_token,
    generate_verify_token,
    hash_password
)
from app.core.services.mail.service import EmailData, MailServiceInterface


@dataclass
class UserService:
    user_repository: UserRepository
    mail_service: MailServiceInterface

    async def send_reset_password(self, email: str) -> None:
        user = await self.user_repository.get_by_email(email=email)
        if not user:
            return

        token = generate_reset_token(email=email)
        email_data = EmailData(subject="Код для сброса пароля", recipient=user.email)
        template = ResetTokenTemplate(
            username=user.username,
            link=f'{app_config.app_url}/reset_password?token={token}',
            token=token,
            valid_minutes=auth_config.EMAIL_RESET_TOKEN_EXPIRE_MINUTES,
        )
        await self.mail_service.queue(template=template, email_data=email_data)

    async def reset_password(self, token: str, password: str, repeat_password: str) -> None:
        reset_token = decode_reset_token(token=token)
        user = await self.user_repository.get_by_email(email=reset_token.sub)

        if not user: return

        if password != repeat_password:
            raise

        user.password_hash = hash_password(password)

    async def send_verify(self, email: str) -> None:
        user = await self.user_repository.get_by_email(email=email)

        if not user:
            raise

        token = generate_verify_token(email=email)
        email_data = EmailData(subject="Код для верификации почты", recipient=user.email)
        template = VerifyTokenTemplate(
            email=user.email,
            token=token,
        )
        await self.mail_service.queue(template=template, email_data=email_data)

    async def verify(self, token: str) -> None:
        verify_token = decode_verify_token(token=token)
        user = await self.user_repository.get_by_email(email=verify_token.sub)

        if not user:
            raise

        user.is_verified = True

    async def get_by_id(self, user_id: int) -> User:
        user = await self.user_repository.get_by_id(user_id=user_id)
        if not user:
            raise NotFoundUserBy("id")

        return user

    async def create(self, user_data: UserCreate) -> User:
        user = await self.user_repository.get_by_username(user_data.username)

        if user:
            raise AlreadyUserUsername(user_data.username)


        user = await self.user_repository.get_by_email(user_data.email)
        if user:
            raise AlreadyUserEmail(user_data.username)

        if user_data.password != user_data.password_repeat:
            raise


        user = User.create(
            email=user_data.email,
            username=user_data.username,
            password_hash=hash_password(user_data.password)
        )
        await self.user_repository.create(user)
        return user