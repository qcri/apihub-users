from datetime import datetime
from typing import Optional

from enum import Enum
from pydantic import BaseModel


class SubscriptionType(str, Enum):
    TRIAL = "trial"
    STANDARD = "standard"
    PREMIUM = "premium"


class SubscriptionBase(BaseModel):
    pass


class SubscriptionCreate(SubscriptionBase):
    username: str
    application: str
    credit: int
    starts_at: datetime = datetime.now()
    expires_at: Optional[datetime] = None
    recurring: bool = False
    created_by: str
    notes: Optional[str] = None


class SubscriptionDetails(SubscriptionCreate):
    created_at: datetime
    balance: int
