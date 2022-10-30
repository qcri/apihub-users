from datetime import datetime

from sqlalchemy import Column, Integer, String, Date, DateTime, Float

from ..common.db_session import Base


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
    __tablename__ = "activity"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.now())
    request = Column(String)
    username = Column(String)
    subscription_type = Column(String)
    status = Column(String)
    request_key = Column(String)
    result = Column(String)
    payload = Column(String)
    ip_address = Column(String)
    latency = Column(Float)

    def __str__(self):
        return f"{self.request} || {self.username}"
