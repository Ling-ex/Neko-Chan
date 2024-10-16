import sys

from pydantic_core import ValidationError
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_ignore_empty=True,
    )

    API_ID: int
    API_HASH: str
    BOT_TOKEN: str
    MONGO_URL: str

    # Some Configuration
    OWNER: int = 1983980399
    CHAT_ID: int = 0
    CHAT_LOG: int = -1002489494471
    REPO_URL: str = 'https://github.com/lunaticsm/Neko-Chan'
    REPO_BRANCH: str = 'dev'


try:
    Config = Settings()
except ValidationError as e:
    errors = e.errors()
    for error in errors:
        field = error['loc'][0]
        if field == 'API_ID':
            print('API_ID is missing')
        elif field == 'API_HASH':
            print('API_HASH is missing')
        elif field == 'BOT_TOKEN':
            print('BOT_TOKEN is missing')
        elif field == 'MONGO_URL':
            print('MONGO_URL is missing')
        else:
            print(
                (
                    'Make sure the ENV is valid and there '
                    'are no typos or filling errors!'
                ),
            )

    sys.exit(1)
