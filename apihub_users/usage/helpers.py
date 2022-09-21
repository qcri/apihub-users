from datetime import date, datetime
from ..subscription.models import UserSubscription
from .queries import UsageQuery
from .schemas import UsageCreate


USAGE_KEY = "dailyusage"


def make_key(username: str, application: str, date_str: str) -> str:
    return f"{username}:{application}:{date_str}"


def copy_yesterday_usage(redis, session):
    query = UsageQuery(session)
    today = date.today().isoformat()
    for k, v in redis.hgetall(USAGE_KEY).items():
        k = k.decode("utf-8")
        v = int(v.decode("utf-8"))
        username, application, date_str = k.split(":")
        if date_str != today:
            us = session.query(UserSubscription)\
                .filter(UserSubscription.application == application,
                        UserSubscription.username == username).one()
            usage = UsageCreate(
                date=datetime.fromisoformat(date_str),
                user_subscription_id=us.id,
                user_subscription=us,
                usage=v)

            query.create_usage(usage)
            redis.hdel(USAGE_KEY, k)
