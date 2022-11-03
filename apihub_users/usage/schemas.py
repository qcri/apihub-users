from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel
from enum import Enum


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
    request: str
    username: Optional[str] = None
    tier: str
    status: str
    request_key: Optional[str] = None
    result: Optional[str] = None
    payload: Optional[str] = None
    ip_address: Optional[str] = None
    latency: Optional[float] = None


class ActivityDetails(ActivityCreate):
    created_at: datetime


class ActivityStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    PROCESSED = "PROCESSED"
