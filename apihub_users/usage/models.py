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

    user_subscription_id = Column(Integer, ForeignKey("association.id"))
    user_subscription = relationship("UserSubscription", back_populates="daily_usages")

    def __str__(self):
        return f"DailyUsage username={self.user_subscription.username} " \
                f"application={self.user_subscription.application} usage={self.usage}"
