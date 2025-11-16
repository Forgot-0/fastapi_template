from app.core.configs.base import BaseConfig


class AuthConfig(BaseConfig):
    USER_REGISTRATION_ALLOWED: bool = False

    EMAIL_RESET_TOKEN_EXPIRE_MINUTES: int = 15
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 60

    JWT_SECRET_KEY: str = ''
    JWT_ALGORITHM: str = 'HS256'
    
    # OAuth Google
    OAUTH_GOOGLE_CLIENT_ID: str = ''
    OAUTH_GOOGLE_CLIENT_SECRET: str = ''
    OAUTH_GOOGLE_REDIRECT_URI: str = ''
    
    # OAuth Yandex
    OAUTH_YANDEX_CLIENT_ID: str = ''
    OAUTH_YANDEX_CLIENT_SECRET: str = ''
    OAUTH_YANDEX_REDIRECT_URI: str = ''
    
    # OAuth GitHub
    OAUTH_GITHUB_CLIENT_ID: str = ''
    OAUTH_GITHUB_CLIENT_SECRET: str = ''
    OAUTH_GITHUB_REDIRECT_URI: str = ''


auth_config = AuthConfig()