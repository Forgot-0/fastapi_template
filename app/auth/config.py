from app.core.configs.base import BaseConfig


class AuthConfig(BaseConfig):
    USER_REGISTRATION_ALLOWED: bool = False

    EMAIL_RESET_TOKEN_EXPIRE_MINUTES: int = 15
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5
    REFRESH_TOKEN_EXPIRE_DAYS: int = 60

    # OAuth Google
    OAUTH_GOOGLE_CLIENT_ID: str = ""
    OAUTH_GOOGLE_CLIENT_SECRET: str = ""
    OAUTH_GOOGLE_REDIRECT_URI: str = ""
    OAUTH_GOOGLE_BASE_AUTH_URL: str = "https://accounts.google.com/o/oauth2/v2/auth"
    OAUTH_GOOGLE_TOKEN_URL: str = "https://oauth2.googleapis.com/token" # noqa: S105
    OAUTH_GOOGLE_USERINFO_URL: str = "https://openidconnect.googleapis.com/v1/userinfo"

    # OAuth Yandex
    OAUTH_YANDEX_CLIENT_ID: str = ""
    OAUTH_YANDEX_CLIENT_SECRET: str = ""
    OAUTH_YANDEX_REDIRECT_URI: str = ""
    OAUTH_YANDEX_BASE_AUTH_URL: str = "https://oauth.yandex.ru/authorize"
    OAUTH_YANDEX_TOKEN_URL: str = "https://oauth.yandex.ru/token" # noqa: S105
    OAUTH_YANDEX_USERINFO_URL: str = "https://login.yandex.ru/info"

    # OAuth GitHub
    OAUTH_GITHUB_CLIENT_ID: str = ""
    OAUTH_GITHUB_CLIENT_SECRET: str = ""
    OAUTH_GITHUB_REDIRECT_URI: str = ""
    OAUTH_GITHUB_BASE_AUTH_URL: str = "https://github.com/login/oauth/authorize"
    OAUTH_GITHUB_TOKEN_URL: str = "https://github.com/login/oauth/access_token" # noqa: S105
    OAUTH_GITHUB_USERINFO_URL: str = "https://api.github.com/user"

    USER_TOPIC: str = "users"


auth_config = AuthConfig()
