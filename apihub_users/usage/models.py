from ..common.db_session import Base
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Date
)
from sqlalchemy.orm import relationship
from datetime import datetime


class DailyUsage(Base):
    __tablename__ = "daily_usage"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, default=datetime.now())
    usage = Column(Integer, default=0)

    application = Column(Integer, ForeignKey("subscription.application"))
    subscription = relationship("Subscription", back_populates="daily_usages")

    def __str__(self):
        return f"DailyUsage username={self.subscription.username} " \
                f"application={self.application} usage={self.usage}"
