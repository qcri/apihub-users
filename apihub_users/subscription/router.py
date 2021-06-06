from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel, BaseSettings
from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT

from ..common.db_session import create_session
from ..security.schemas import UserBase  # TODO create a model for this UserBase
from ..security.depends import require_admin, require_user, require_token
from .schemas import SubscriptionCreate
from .queries import SubscriptionQuery, SubscriptionException


HTTP_429_TOO_MANY_REQUESTS = 429

router = APIRouter()


class SubscriptionSettings(BaseSettings):
    subscription_token_expires_days: int = 1


# FIXME move this to schemas
class SubscriptionIn(BaseModel):
    username: str
    application: str
    credit: int
    expires_at: Optional[datetime] = None
    recurring: bool = False


@router.post("/subscription")
def create_subscription(
    subscription: SubscriptionIn,
    username: str = Depends(require_admin),
    session=Depends(create_session),
):
    subscription_create = SubscriptionCreate(
        username=subscription.username,
        application=subscription.application,
        credit=subscription.credit,
        starts_at=datetime.now(),
        expires_at=subscription.expires_at,
        recurring=subscription.recurring,
        created_by=username,
    )
    try:
        query = SubscriptionQuery(session)
        query.create_subscription(subscription_create)
        return subscription_create
    except SubscriptionException:
        return {}


@router.get("/subscription/{application}")
def get_active_subscription(
    application: str,
    user: UserBase = Depends(require_token),
    session=Depends(create_session),
):
    query = SubscriptionQuery(session)
    try:
        subscription = query.get_active_subscription(user.username, application)
    except SubscriptionException:
        return {}

    return subscription


@router.get("/subscription")
def get_active_subscriptions(
    user: UserBase = Depends(require_token),
    session=Depends(create_session),
):
    if user.is_user:
        username = user.username

    query = SubscriptionQuery(session)
    try:
        subscriptions = query.get_active_subscriptions(username)
    except SubscriptionException:
        return []

    return subscriptions


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
class SubscriptionTokenResponse(BaseModel):
    username: str
    application: str
    token: str
    expires_time: int


@router.get("/token/{application}")
async def get_application_token(
    application: str,
    username: str = Depends(require_user),
    session=Depends(create_session),
):
    query = SubscriptionQuery(session)
    try:
        subscription = query.get_active_subscription(username, application)
    except SubscriptionException:
        raise HTTPException(401, "NOt permitted")

    if subscription.balance > subscription.credit:
        raise HTTPException(HTTP_429_TOO_MANY_REQUESTS, "You have used up your credit")

    Authorize = AuthJWT()
    expires_days = SubscriptionSettings().subscription_token_expires_days
    expires_time = timedelta(days=expires_days)
    access_token = Authorize.create_access_token(
        subject=username,
        user_claims={"subscription": application},
        expires_time=expires_time,
    )
    return SubscriptionTokenResponse(
        username=username,
        application=application,
        token=access_token,
        expires_time=expires_time.seconds,
    )
