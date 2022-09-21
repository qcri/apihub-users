from contextlib import contextmanager
from typing import Iterator, ContextManager, Callable

import sqlalchemy
from pydantic import BaseSettings
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base


class Settings(BaseSettings):
    db_uri: str = 'sqlite:///./test.db'
    db_uri_q: str = 'sqlite:///./test.db?check_same_thread=False'


settings = Settings()
Base: DeclarativeMeta = declarative_base()


def get_db_engine():
    return sqlalchemy.engine_from_config(
        {
            'db.url': settings.db_uri_q,
            'db.echo': 'True'
        },
        prefix="db.",
    )


def create_session() -> Iterator[Session]:
    session = sessionmaker(bind=get_db_engine())()

    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


db_context: Callable[[], ContextManager[Session]] = contextmanager(create_session)
