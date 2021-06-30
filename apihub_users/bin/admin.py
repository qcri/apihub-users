import sys

from pydantic import BaseSettings

from apihub_users.common.db_session import db_context, Base, DB_ENGINE
from apihub_users.common.redis_session import redis_conn
from apihub_users.security.schemas import UserCreate, UserType
from apihub_users.security.queries import UserQuery
from apihub_users.usage.helpers import copy_yesterday_usage
from apihub_users.security.models import *  # noqa
from apihub_users.subscription.models import *  # noqa
from apihub_users.usage.models import *  # noqa


class SuperUser(BaseSettings):
    username: str
    password: str
    email: str

    def as_usercreate(self):
        return UserCreate(
            username=self.username,
            password=self.password,
            email=self.email,
            role=UserType.ADMIN,
        )


def init():
    Base.metadata.bind = DB_ENGINE
    Base.metadata.create_all()

    with db_context() as session:
        user = SuperUser().as_usercreate()
        if UserQuery(session).create_user(user):
            sys.stderr.write(f"Admin {user.username} is created!")
        else:
            sys.stderr.write(f"Admin {user.username} already exists!")


def deinit():
    Base.metadata.bind = DB_ENGINE
    Base.metadata.drop_all()
    sys.stderr.write("deinit is done!")


def sync_usage():
    with redis_conn() as redis:
        with db_context() as session:
            copy_yesterday_usage(redis, session)
