from datetime import timedelta
from pydantic import BaseSettings
from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT

from ..common.db_session import create_session
from ..security.schemas import UserBase  # TODO create a model for this UserBase
from ..security.depends import require_admin, require_token
from .queries import *
from apihub_users.security.queries import UserQuery
HTTP_429_TOO_MANY_REQUESTS = 429

router = APIRouter()


class SubscriptionSettings(BaseSettings):
    default_subscription_days: int = 30
    subscription_token_expires_days: int = 1


@router.post("/subscription")
def create_subscription(
        subscription: SubscriptionIn,
        username: str = Depends(require_admin),
        session=Depends(create_session),
):
    if subscription.expires_at is None:
        subscription.expires_at = datetime.now() + timedelta(
            days=SubscriptionSettings().default_subscription_days
        )

    user_query = UserQuery(session)
    if not user_query.check_username(username):
        raise HTTPException(status_code=404, detail="This user is not registered.")

    us_create = UserSubscriptionCreate(
        username=subscription.username,
        application=subscription.application,
        credit=subscription.credit,
        starts_at=datetime.now(),
        expires_at=subscription.expires_at,
        recurring=subscription.recurring,
        created_by=username,
    )
    try:
        query = UserSubscriptionQuery(session)
        query.create_user_subscription(us_create)
        return us_create
    except UserSubscriptionException:
        return {}


@router.get("/subscription/{application}")
def get_active_subscription(
        application: str,
        user: UserBase = Depends(require_token),
        session=Depends(create_session),
):
    query = UserSubscriptionQuery(session)
    try:
        return query.get_active_user_subscription(user.username, application)
    except UserSubscriptionException:
        return {}


@router.get("/subscription")
def get_active_subscriptions(
        user: UserBase = Depends(require_token),
        session=Depends(create_session)):
    if not user.is_user:
        return []

    username = user.username
    query = UserSubscriptionQuery(session)
    try:
        return query.get_active_user_subscriptions(username)
    except UserSubscriptionException:
        return []


# delete plan
# @router.post("/subscription/_disable")
# def disable_subscription(
#     username: str = Depends(require_admin),
#     session=Depends(create_session),
# )

# disable plan

# enable plan

# get usage summary

# get ap your limitplication token


class UserSubscriptionTokenResponse(BaseModel):
    username: str
    application: str
    token: str
    expires_time: int


@router.get("/token/{application}")
async def get_application_token(
        application: str,
        user: UserBase = Depends(require_token),
        username: Optional[str] = None,
        expires_days: Optional[
            int
        ] = SubscriptionSettings().subscription_token_expires_days,
        session=Depends(create_session),
):
    query = UserSubscriptionQuery(session)

    if user.is_user:
        username = user.username
        expires_days = SubscriptionSettings().subscription_token_expires_days
    else:
        if username is None:
            raise HTTPException(401, "username is missing")
    try:
        us = query.get_active_user_subscription(username, application)
    except UserSubscriptionException:
        raise HTTPException(401, f"No active subscription found for user {username}")

    if us.balance > us.credit:
        raise HTTPException(HTTP_429_TOO_MANY_REQUESTS, "You have used up your credit")

    # limit token expire time to subscription expire time
    subscription_expires_timedelta = us.expires_at - datetime.now()
    if expires_days > subscription_expires_timedelta.days:
        expires_days = subscription_expires_timedelta.days

    Authorize = AuthJWT()
    expires_time = timedelta(days=expires_days)
    access_token = Authorize.create_access_token(
        subject=username,
        user_claims={"subscription": application},
        expires_time=expires_time,
    )
    return UserSubscriptionTokenResponse(
        username=username,
        application=application,
        token=access_token,
        expires_time=expires_time.seconds,
    )
