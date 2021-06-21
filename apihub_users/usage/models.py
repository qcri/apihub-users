from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
)

from ..common.db_session import Base


class DailyUsage(Base):
    __tablename__ = "daily_usages"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    username = Column(String, index=True)
    application = Column(String, index=True)
    usage = Column(Integer, default=0)
