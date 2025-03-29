from loguru import logger
import sys


logger.remove()

logger.add(
    sys.stderr,
    format="[<green>{time:YYYY-MM-DD HH:mm:ss}</green>] <level>{level: <8}</level>: {message}",
    level="info" # app_config.LOG_LEVEL
)

logger.add(
    "logs/app.log",
    format="[<green>{time:YYYY-MM-DD HH:mm:ss}</green>] <level>{level: <8}</level>: {message}",
    rotation="00:00",
    retention="7 days",
    level="info", # TODO: Дабавить env "app_config.LOG_LEVEL"
    utc=True,
    delay=True,
)

