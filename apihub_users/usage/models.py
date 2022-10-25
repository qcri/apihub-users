from datetime import datetime

from sqlalchemy import Column, Integer, String, Date, DateTime

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


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.now())
    request = Column(String, nullable=False)
    username = Column(String, index=True)
    request_type = Column(String)
    ip_address = Column(String)

    def __str__(self):
        return f"{self.request} || {self.username}"
