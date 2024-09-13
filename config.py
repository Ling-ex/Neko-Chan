import logging
import sys

from pydantic_core import ValidationError
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


log = logging.getLogger('Config')


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_ignore_empty=True,
    )

    API_ID: int
    API_HASH: str
    BOT_TOKEN: str
    MONGO_URL: str

    # Some Configuration
    OWNER: int = 5050907047
    CHAT_ID: int = 0


try:
    Config = Settings()
except ValidationError as e:
    errors = e.errors()
    for error in errors:
        field = error['loc'][0]
        if field == 'API_ID':
            log.info('API_ID is missing')
        elif field == 'API_HASH':
            log.info('API_HASH is missing')
        elif field == 'BOT_TOKEN':
            log.info('BOT_TOKEN is missing')
        elif field == 'MONGO_URL':
            log.info('MONGO_URL is missing')

    sys.exit(1)
