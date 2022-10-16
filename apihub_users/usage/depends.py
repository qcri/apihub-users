from datetime import date

from fastapi import Depends
from redis import Redis

from ..common.redis_session import redis_conn
from ..subscription.depends import require_subscription
from .helpers import make_key, USAGE_KEY


def update_daily_usage(
    application: str,
    username: str = Depends(require_subscription),
    redis: Redis = Depends(redis_conn),
) -> None:
    today = date.today().isoformat()
    key = make_key(username, application, today)
    redis.hincrby(USAGE_KEY, key, 1)
