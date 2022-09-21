from contextlib import contextmanager
from typing import Iterator, ContextManager, Callable
from pydantic import BaseSettings
from redis import Redis


class RedisSettings(BaseSettings):
    redis: str = "redis://localhost:6379"


def redis_conn(settings: RedisSettings = RedisSettings()) -> Iterator[Redis]:
    try:
        redis = Redis.from_url(settings.redis)
    except Exception as e:
        raise e
    try:
        yield redis
        redis.close()
    except:
        redis.close()


redis_context: Callable[[], ContextManager[Redis]] = contextmanager(redis_conn)
