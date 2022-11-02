from datetime import date, datetime

from fastapi import Depends

from .queries import UsageQuery, ActivityQuery
from .schemas import UsageCreate, ActivityCreate
from apihub_users.common.db_session import create_session

USAGE_KEY = "dailyusage"


def make_key(username: str, application: str, date: str) -> str:
    return f"{username}:{application}:{date}"


def copy_yesterday_usage(redis, session):
    query = UsageQuery(session)
    today = date.today().isoformat()
    for k, v in redis.hgetall(USAGE_KEY).items():
        k = k.decode("utf-8")
        v = int(v.decode("utf-8"))
        username, application, date_str = k.split(":")
        if date_str != today:
            usage = UsageCreate(
                date=datetime.fromisoformat(date_str),
                username=username,
                application=application,
                usage=v,
            )
            query.create_usage(usage)
            redis.hdel(USAGE_KEY, k)


def create_activity_helper(session=Depends(create_session), **kwargs):
    ActivityQuery(session).create_activity(
        ActivityCreate(
            request=kwargs.get("request"),
            username=kwargs.get("username"),
            tier=kwargs.get("tier"),
            status=kwargs.get("status"),
            request_key=kwargs.get("request_key"),
            result=kwargs.get("result"),
            payload=kwargs.get("payload"),
            ip_address=kwargs.get("ip_address"),
            latency=kwargs.get("latency"),
        )
    )
