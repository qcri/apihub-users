from contextlib import contextmanager

from redis import Redis


USAGE_KEYS = "usage:keys"


def make_key(username: str, application: str) -> str:
    return f"usage:{username}:{application}"


@contextmanager
def get_and_reset_balance_in_cache(
    username: str, application: str, redis: Redis
) -> None:
    key = make_key(username, application)
    count = redis.get(key)

    yield count

    if count == "0":
        redis.srem(USAGE_KEYS, key)
    elif count is not None:
        redis.set(key, 0)
