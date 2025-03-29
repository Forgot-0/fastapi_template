from abc import abstractmethod
from pathlib import Path

from app.core.services.mail.template import BaseTemplate



class AuthTemplate(BaseTemplate):
    def _get_dir(self) -> Path:
        return Path('app/auth/emails/views')

    @abstractmethod
    def _get_name(self) -> str:
        ...


class UserRegistration(AuthTemplate):
    def __init__(self, username: str, project_name: str):
        self.username = username
        self.project_name = project_name

    def _get_name(self) -> str:
        return 'user_registration.html'


class ResetTokenTemplate(AuthTemplate):
    def __init__(self, username: str, link: str, token: str, valid_minutes: int):
        self.username = username
        self.link = link
        self.token = token
        self.valid_minutes = valid_minutes

    def _get_name(self) -> str:
        return 'reset_token.html'
    

class VerifyTokenTemplate(AuthTemplate):
    def __init__(self, username: str, link: str, token: str, valid_minutes: int):
        self.username = username
        self.link = link
        self.token = token
        self.valid_minutes = valid_minutes

    def _get_name(self) -> str:
        return 'verify.html'