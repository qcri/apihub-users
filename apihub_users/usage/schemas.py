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
    status: Optional[str] = None
    username: Optional[str] = None
    request_type: Optional[str] = None
    body: Optional[str] = None
    params: Optional[str] = None

    def activity_log_schema(self):
        return ActivityLogCreate(
            request=self.request,
            status=self.status,
            username=self.username,
            request_type=self.request_type,
            body=self.body,
            params=self.params,
        )


class ActivityLogDetails(ActivityLogCreate):
    created_at: str
