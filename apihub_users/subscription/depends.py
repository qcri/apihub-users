from apihub_users.subscription.schemas import SubscriptionBase
from fastapi import HTTPException, Depends
from fastapi_jwt_auth import AuthJWT
from redis import Redis

from ..common.db_session import create_session
from ..common.redis_session import redis_conn
from ..subscription.queries import SubscriptionQuery
from ..subscription.helpers import make_key, BALANCE_KEYS


HTTP_403_FORBIDDEN = 403
HTTP_429_QUOTA = 429


def require_subscription(
    application: str, Authorize: AuthJWT = Depends()
) -> SubscriptionBase:
    Authorize.jwt_required()
    username = Authorize.get_jwt_subject()

    claims = Authorize.get_raw_jwt()
    subscription_claim = claims.get("subscription")
    tier_claim = claims.get("tier")
    if subscription_claim != application:
        raise HTTPException(
            HTTP_403_FORBIDDEN,
            "The API key doesn't have permission to perform the request",
        )
    return SubscriptionBase(
        username=username, tier=tier_claim, application=subscription_claim
    )


def require_subscription_balance(
    subscription: SubscriptionBase = Depends(require_subscription),
    redis: Redis = Depends(redis_conn),
    session=Depends(create_session),
) -> str:
    username = subscription.username
    tier = subscription.tier
    application = subscription.application

    key = make_key(username, application, tier)
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
        SubscriptionQuery(session).update_balance_in_subscription(
            username, application, tier, redis
        )

    if balance < 0:
        raise HTTPException(
            HTTP_429_QUOTA,
            "You have used up all credit for this API",
        )

    return username
