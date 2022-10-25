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


class ActivityLogBase(BaseModel):
    pass


class ActivityLogCreate(ActivityLogBase):
    request: str
    username: Optional[str] = None
    request_type: Optional[str] = None
    ip_address: Optional[str] = None

    def activity_log_schema(self):
        return ActivityLogCreate(
            request=self.request,
            username=self.username,
            request_type=self.request_type,
            ip_address=self.ip_address,
        )


class ActivityLogDetails(ActivityLogCreate):
    created_at: str
