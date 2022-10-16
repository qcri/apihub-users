from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    DateTime,
    String,
    ForeignKey,
)
from enum import Enum
from sqlalchemy.orm import relationship
from ..common.db_session import Base
from .schemas import ApplicationType


class Subscription(Base):
    __tablename__ = "subscription"

    id = Column(Integer, primary_key=True, index=True)
    application = Column(Enum(ApplicationType), default=ApplicationType.API1_TRIAL)
    credit = Column(Integer, default=0)
    balance = Column(Integer, default=0)
    recurring = Column(Boolean, default=False)
    starts_at = Column(DateTime, default=datetime.now())
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now())
    created_by = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    # User table FK.
    username = Column(Integer, ForeignKey("user.username"))
    user = relationship("User", back_populates="subscription")
    # DailyUsage back_populate.
    daily_usages = relationship("DailyUsage", back_populates="subscription")

    def __str__(self):
        return f"Subscription username={self.username} " \
                f"application={self.application} balance={self.balance}"
