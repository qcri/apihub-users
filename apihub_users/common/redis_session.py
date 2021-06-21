from typing import Iterator
from pydantic import BaseSettings
from redis import Redis


class RedisSettings(BaseSettings):
    redis: str = "redis://localhost:6379"


def redis_conn(settings: RedisSettings = RedisSettings()) -> Iterator[Redis]:
    redis = Redis.from_url(settings.redis)
    yield redis
    redis.close()
