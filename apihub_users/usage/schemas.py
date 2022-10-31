from datetime import date, datetime

from typing import Optional
from pydantic import BaseModel


class UsageBase(BaseModel):
    pass


class UsageCreate(UsageBase):
    date: date
    username: str
    application: str
    usage: int


class UsageDetails(UsageCreate):
    pass


class ActivityBase(BaseModel):
    pass


class ActivityCreate(ActivityBase):
    request: Optional[str] = None
    username: Optional[str] = None
    subscription_type: Optional[str] = None
    status: Optional[str] = None
    request_key: Optional[str] = None
    result: Optional[str] = None
    payload: Optional[str] = None
    ip_address: Optional[str] = None
    latency: Optional[float] = None


class ActivityDetails(ActivityCreate):
    created_at: datetime
