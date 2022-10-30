from datetime import date

from typing import Optional
from pydantic import BaseModel
from enum import Enum


class Status(str, Enum):
    ACCEPTED = "accepted"
    PROCESSED = "processed"


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

    def make_activity(self):
        return ActivityCreate(
            request=self.request,
            username=self.username,
            subscription_type=self.subscription_type,
            status=self.status,
            request_key=self.request_key,
            result=self.result,
            payload=self.payload,
            ip_address=self.ip_address,
            latency=self.latency,
        )


class ActivityDetails(ActivityCreate):
    created_at: str
