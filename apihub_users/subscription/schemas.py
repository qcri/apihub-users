from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum


class ApplicationType(str, Enum):
    API1_TRIAL = "api1_trial"
    API1_PREMIUM = "api1_premium"
    API2_TRIAL = "api2_trial"
    API2_PREMIUM = "api2_premium"
    API3_TRIAL = "api3_trial"
    API3_PREMIUM = "api3_premium"


class SubscriptionBase(BaseModel):
    pass


class SubscriptionCreate(SubscriptionBase):
    application: str
    credit: int
    recurring: bool = False


class SubscriptionDetails(SubscriptionCreate):
    application: str
    credit: int


class SubscriptionIn(BaseModel):
    username: str
    application: str
    credit: int
    recurring: bool = False
    expires_at: Optional[datetime] = None


class UserSubscriptionBase(BaseModel):
    pass


class UserSubscriptionCreate(UserSubscriptionBase):
    username: str
    application: str
    balance: Optional[int] = 0
    expires_at: Optional[datetime] = None
    created_by: str
    recurring: bool
    credit: int


class UserSubscriptionDetails(UserSubscriptionCreate):
    pass
