from abc import ABC
from os.path import join
from pathlib import Path

from pydantic import BaseSettings, Field, SecretStr


BASE_DIR = Path(__file__).resolve().parent.parent


BASE_CURRENCY_CODE = "USD"
CURRENCY_DECIMAL_PLACES = 4
CURRENCY_CODE_LENGTH = 3


class Settings(BaseSettings, ABC):
    class Config:
        env_file = join(BASE_DIR, ".env")


class AppSettings(Settings):
    debug: bool = Field(env="DEBUG", default=False)


class RedisSettings(Settings):
    db: int = Field(env="REDIS_DB", ge=0, le=16)
    host: str = Field(env="REDIS_HOST")
    port: int = Field(env="REDIS_PORT")
    password: SecretStr = Field(env="REDIS_PASSWORD")
