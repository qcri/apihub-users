from fastapi import HTTPException, Depends
from fastapi_jwt_auth import AuthJWT
from redis import Redis
from apihub_users.common.redis_session import redis_conn
from apihub_users.subscription.helpers import make_key, USAGE_KEYS


HTTP_403_FORBIDDEN = 403


def require_subscription(application: str, Authorize: AuthJWT = Depends()) -> str:
    Authorize.jwt_required()

    claims = Authorize.get_raw_jwt()
    subscription_claim = claims.get("subscription")
    if subscription_claim != application:
        raise HTTPException(
            HTTP_403_FORBIDDEN,
            "The API key doesn't have permission to perform the request",
        )
    return Authorize.get_jwt_subject()


def update_subscription_balance(
    application: str,
    redis: Redis = Depends(redis_conn),
    username=Depends(require_subscription),
) -> None:
    """increment usage counter in redis"""
    key = make_key(username, application)
    count = redis.incr(key)
    if count == 1:
        redis.sadd(USAGE_KEYS, key)
    # TODO: for every 1k usage, check against subscription
