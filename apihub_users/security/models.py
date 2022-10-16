from .schemas import UserType
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    DateTime,
    String,
    Enum
)
from sqlalchemy.orm import relationship
from ..common.db_session import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, index=True)
    salt = Column(String)
    hashed_password = Column(String)
    role = Column(Enum(UserType), default=UserType.ADMIN)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now())
    # Subscription back_populate.
    subscriptions = relationship("Subscription", back_populates="user")

    def __str__(self):
        return f"User username={self.username} role={self.role}"
