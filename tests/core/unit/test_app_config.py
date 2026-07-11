import pytest
from pydantic import ValidationError

from app.core.configs.app import AppConfig


def test_production_config_requires_critical_settings() -> None:
    with pytest.raises(ValidationError, match="Missing required production settings"):
        AppConfig(ENVIRONMENT="production")
