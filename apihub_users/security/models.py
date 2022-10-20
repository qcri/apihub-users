from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    DateTime,
    Enum,
)
from .schemas import UserType
from sqlalchemy.orm import relationship
from ..common.db_session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, index=True)
    salt = Column(String)
    hashed_password = Column(String)
    role = Column(Enum(UserType), default=UserType.USER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now())
    # Subscription back_populate.
    subscriptions = relationship("Subscription", back_populates="user")

    def __str__(self):
        return f"{self.username} | {self.role}"
