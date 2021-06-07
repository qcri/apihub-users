from fastapi import HTTPException, Depends
from fastapi_jwt_auth import AuthJWT
from redis import Redis

from ..common.db_session import create_session
from ..common.redis_session import redis_conn
from ..subscription.queries import SubscriptionQuery
from ..subscription.helpers import make_key, BALANCE_KEYS


HTTP_403_FORBIDDEN = 403
HTTP_429_QUOTA = 429


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
    username: str = Depends(require_subscription),
    redis: Redis = Depends(redis_conn),
    session=Depends(create_session),
) -> str:
    key = make_key(username, application)
    balance = redis.decr(key)

    if balance == -1:
        subscription = SubscriptionQuery(session).get_active_subscription(
            username, application
        )
        balance = subscription.credit - subscription.balance - 1
        if balance > 0:
            redis.set(key, balance)
            redis.sadd(BALANCE_KEYS, key)

    if balance <= 0:
        subscription = SubscriptionQuery(session).update_balance_in_subscription(
            username, application, redis
        )

    return username


def require_subscription_balance(
    application: str,
    username: str = Depends(require_subscription),
    redis: Redis = Depends(redis_conn),
    session=Depends(create_session),
) -> str:
    key = make_key(username, application)
    balance = redis.decr(key)

    if balance == -1:
        subscription = SubscriptionQuery(session).get_active_subscription(
            username, application
        )
        balance = subscription.credit - subscription.balance - 1
        if balance > 0:
            redis.set(key, balance)
            redis.sadd(BALANCE_KEYS, key)

    if balance <= 0:
        subscription = SubscriptionQuery(session).update_balance_in_subscription(
            username, application, redis
        )

    if balance < 0:
        raise HTTPException(
            HTTP_429_QUOTA,
            "You have used up all credit for this API",
        )

    return username
