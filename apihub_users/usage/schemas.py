from datetime import date

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
    request: str
    username: Optional[str] = None
    application: Optional[str] = None
    ip_address: Optional[str] = None
    key: Optional[str] = None
    result: Optional[str] = None
    latency: Optional[float] = None

    def activity_log_schema(self):
        return ActivityCreate(
            request=self.request,
            username=self.username,
            application=self.application,
            ip_address=self.ip_address,
            key=self.key,
            result=self.result,
            latency=self.latency,
        )


class ActivityDetails(ActivityCreate):
    created_at: str
