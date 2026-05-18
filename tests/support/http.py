from app.core.configs.app import app_config


def api_path(suffix: str) -> str:
    base = app_config.API_V1_STR.rstrip("/")
    tail = suffix.lstrip("/")
    return f"{base}/{tail}" if tail else base
