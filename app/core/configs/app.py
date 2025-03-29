from typing import Annotated, Literal

from pydantic import BeforeValidator, PostgresDsn, computed_field
from pydantic_core import MultiHostUrl

from app.core.configs.base import BaseConfig


class AppConfig(BaseConfig):

    ENVIRONMENT: Literal['local', 'production', 'testing'] = 'local'
    PROJECT_NAME: str = 'Tactical Hub'
    DOMAIN: str = 'localhost'
    HOST: str = '0.0.0.0'
    PORT: int = 80

    API_V1_STR: str = '/api/v1'
    SECRET_KEY: str = ''
    BACKEND_CORS_ORIGINS: Annotated[list[str] | str, BeforeValidator(BaseConfig.parse_list)] = []
    RATE_LIMITER_ENABLED: bool = True

    POSTGRES_SERVER: str = ''
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = ''
    POSTGRES_PASSWORD: str = ''
    POSTGRES_DB: str = ''
    SQL_ECHO: bool = False

    @computed_field
    @property
    def app_url(self) -> str:
        if self.ENVIRONMENT in ['local', 'testing']:
            return f'http://{self.DOMAIN}'
        return f'https://{self.DOMAIN}'

    @computed_field
    @property
    def postgres_url(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme='postgresql+psycopg',
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        ) # type: ignore

    REDIS_HOST: str = ''
    REDIS_PORT: int = 6379

    @computed_field
    @property
    def redis_url(self) -> str:
        return f'redis://{self.REDIS_HOST}:{self.REDIS_PORT}'

    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None

    EMAIL_SENDER_ADDRESS: str | None = None
    EMAIL_SENDER_NAME: str | None = None

    QUEUE_REDIS_BROKER_URL: str = ''
    QUEUE_REDIS_RESULT_BACKEND: str = ''

    LOG_LEVEL: str = 'ERROR'
    LOG_HANDLERS: Annotated[list[Literal['stream', 'file']] | str, BeforeValidator(BaseConfig.parse_list)] = ['stream']


app_config = AppConfig()