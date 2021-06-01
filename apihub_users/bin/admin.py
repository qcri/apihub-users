import sys

from pydantic import BaseSettings

from apihub_users.common.db_session import db_context, Base, DB_ENGINE
from apihub_users.security.schemas import UserCreate, UserType
from apihub_users.security.queries import UserQuery


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
        UserQuery(session).create_user(user)
        sys.stderr.write(f"Admin {user.username} is created!")


def deinit():
    Base.metadata.bind = DB_ENGINE
    Base.metadata.drop_all()
    sys.stderr.write("deinit is done!")
