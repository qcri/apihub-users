from datetime import datetime

from .schemas import ActivityStatus
from sqlalchemy import Column, Integer, String, Date, DateTime, Float, Enum

from ..common.db_session import Base
from ..subscription.schemas import SubscriptionTier


class DailyUsage(Base):
    __tablename__ = "daily_usages"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    username = Column(String, index=True)
    application = Column(String, index=True)
    usage = Column(Integer, default=0)

    def __str__(self):
        return f"{self.application} || {self.username} || {self.usage}"


class Activity(Base):
    """
    This class is used to store activity data.
    """

    __tablename__ = "activity"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.now())
    request = Column(String)
    username = Column(String)
    tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.TRIAL)
    status = Column(Enum(ActivityStatus), default=ActivityStatus.ACCEPTED)
    request_key = Column(String)
    result = Column(String)
    payload = Column(String)
    ip_address = Column(String)
    latency = Column(Float)

    def __str__(self):
        return f"{self.request} || {self.username}"
