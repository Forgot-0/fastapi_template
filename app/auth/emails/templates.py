from abc import abstractmethod
from pathlib import Path

from app.core.configs.app import app_config
from app.core.services.mail.template import BaseTemplate


class AuthTemplate(BaseTemplate):
    def _get_dir(self) -> Path:
        return Path("app/auth/emails/views")

    @abstractmethod
    def _get_name(self) -> str:
        ...


class UserRegistration(AuthTemplate):
    def __init__(self, username: str, project_name: str) -> None:
        self.username = username
        self.project_name = project_name

    def _get_name(self) -> str:
        return "user_registration.html"


class ResetTokenTemplate(AuthTemplate):
    def __init__(self, username: str, token: str, valid_minutes: int) -> None:
        self.username = username
        self.link = f"{app_config.app_url}/reset_password?token={token}"
        self.token = token
        self.valid_minutes = valid_minutes

    def _get_name(self) -> str:
        return "reset_token.html"


class VerifyTokenTemplate(AuthTemplate):
    def __init__(self, email: str, token: str) -> None:
        self.email = email
        self.token = token
        self.link = f"{app_config.app_url}/verify_email?token={token}"

    def _get_name(self) -> str:
        return "verify.html"
