from datetime import date
from pydantic import BaseModel
from apihub_users.subscription.models import UserSubscription


class UsageBase(BaseModel):
    pass


class UsageCreateOld(UsageBase):
    date: date
    usage: int
    username: str
    application: int


class UsageCreate(UsageBase):
    date: date
    usage: int
    user_subscription_id: int
    user_subscription: UserSubscription


class UsageDetails(UsageCreateOld):
    pass
