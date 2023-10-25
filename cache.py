from typing import Union
from functools import cache
from upstash_redis import Redis
from config import Credentials, get_credentials_singleton, settings
from langchain.cache import SQLiteCache, UpstashRedisCache
from pydantic import SecretStr

from logger import logger


class RedisCredentials(Credentials):
    """
    Access Redis credentials via volume mount

    Access via singleton, eg:
      from app.settings import sendgrid
      sendgrid.API_KEY.get_secret_value()

    """

    type: str = "redis"

    URL: SecretStr
    TOKEN: SecretStr

    class Config:
        secrets_dir = f"{settings.WORKING_DIR}/credentials/redis"


@cache
def get_cache(override_type: str = None) -> Union[SQLiteCache, UpstashRedisCache]:
    cache_type = override_type or settings.CACHE_TYPE
    if cache_type == "redis":
        logger.debug("Using Redis cache.")
        redis_credentials = get_credentials_singleton("redis")
        redis = Redis(
            url=redis_credentials.URL.get_secret_value(),
            token=redis_credentials.TOKEN.get_secret_value(),
        )
        return UpstashRedisCache(redis)
    else:
        logger.debug("Using SQLite cache.")
        return SQLiteCache()
