from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    DateTime,
    String,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from ..common.db_session import Base


# # right table
# class Subscription(Base):
#     __tablename__ = "subscription"
#
#     id = Column(Integer, primary_key=True, index=True)
#     application = Column(String, index=True, unique=True, nullable=False)
#     credit = Column(Integer, default=0)
#     recurring = Column(Boolean, default=False)
#
#     users = relationship("UserSubscription",  back_populates="subscription")
#
#     def __str__(self):
#         return f"Subscription application={self.application} credit={self.credit}"
#

# Middle table between User and Subscription.
class Subscription(Base):
    __tablename__ = "association"

    id = Column(Integer, primary_key=True, index=True)
    application = Column(String, index=True, unique=True, nullable=False)
    credit = Column(Integer, default=0)
    balance = Column(Integer, default=0)
    recurring = Column(Boolean, default=False)
    starts_at = Column(DateTime, default=datetime.now())
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now())
    created_by = Column(String, nullable=True)
    notes = Column(String, nullable=True)

    username = Column(Integer, ForeignKey("user.username"))
    user = relationship("User", back_populates="subscription")

    def __str__(self):
        return f"Subscription username={self.username} " \
                f"application={self.application} balance={self.balance}"
