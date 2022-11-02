from contextlib import contextmanager

from redis import Redis


BALANCE_KEYS = "balance:keys"


def make_key(username: str, application: str, tier: str) -> str:
    return f"balance:{username}:{application}:{tier}"


@contextmanager
def get_and_reset_balance_in_cache(
    username: str, application: str, tier: str, redis: Redis
) -> None:
    """
    Get the balance from the cache and reset it to the credit value
    """
    key = make_key(username, application, tier)
    balance = redis.get(key)

    yield int(balance)

    if int(balance) <= 0:
        redis.srem(BALANCE_KEYS, key)
        redis.delete(key, 0)
