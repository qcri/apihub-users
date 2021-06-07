from contextlib import contextmanager

from redis import Redis


BALANCE_KEYS = "balance:keys"


def make_key(username: str, application: str) -> str:
    return f"balance:{username}:{application}"


@contextmanager
def get_and_reset_balance_in_cache(
    username: str, application: str, redis: Redis
) -> None:
    key = make_key(username, application)
    balance = redis.get(key)

    yield int(balance)

    if int(balance) <= 0:
        redis.srem(BALANCE_KEYS, key)
        redis.delete(key, 0)
