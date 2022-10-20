from datetime import datetime
from .schemas import SubscriptionType
from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from ..common.db_session import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    application = Column(String, unique=True, index=True, nullable=False)
    subscription_type = Column(Enum(SubscriptionType), default=SubscriptionType.TRIAL)
    credit = Column(Integer, default=0)
    balance = Column(Integer, default=0)
    starts_at = Column(DateTime, default=datetime.now())
    expires_at = Column(DateTime)
    recurring = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now())
    created_by = Column(String)
    notes = Column(String)
    # User table FK.
    username = Column(String, ForeignKey("users.username"), nullable=False)
    user = relationship("User", back_populates="subscriptions")

    def __str__(self):
        return f"{self.application} || {self.subscription_type} || {self.username}"
