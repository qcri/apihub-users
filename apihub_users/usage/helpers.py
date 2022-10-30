from datetime import date, datetime

from fastapi import Depends

from .queries import UsageQuery, ActivityQuery
from .schemas import UsageCreate, ActivityCreate
from ..common.db_session import create_session

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


def create_activity_log(session=Depends(create_session), **kwargs):
    al_q = ActivityQuery(session)
    return al_q.create_activity_helper(
        ActivityCreate(
            request=kwargs.get("request"),
            username=kwargs.get("username"),
            ip_address=kwargs.get("ip_address"),
            application=kwargs.get("application"),
            key=kwargs.get("key"),
            result=kwargs.get("result"),
            latency=kwargs.get("latency"),
            status=kwargs.get("status"),
        )
    )
