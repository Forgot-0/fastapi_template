from app.core.configs.base import BaseConfig


class AuthConfig(BaseConfig):
    USER_REGISTRATION_ALLOWED: bool = False

    EMAIL_RESET_TOKEN_EXPIRE_MINUTES: int = 15
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 60

    JWT_SECRET_KEY: str = ''
    JWT_ALGORITHM: str = 'HS256'


auth_config = AuthConfig()