from dishka import Provider, Scope, provide

from app.core.configs.app import AppConfig, app_config


class ConfigProvider(Provider):
    scope = Scope.APP

    @provide
    def get_app_config(self) -> AppConfig:
        return app_config