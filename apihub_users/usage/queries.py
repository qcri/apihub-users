from typing import List

from sqlalchemy.exc import NoResultFound
from ..subscription.models import UserSubscription

from ..common.queries import BaseQuery
from .models import DailyUsage
from .schemas import UsageCreate, UsageDetails


class UsageException(Exception):
    pass


class UsageQuery(BaseQuery):
    def create_usage(self, usage_create: UsageCreate):
        us = self.session.query(UserSubscription) \
            .filter(UserSubscription.application == usage_create.user_subscription.application,
                    UserSubscription.username == usage_create.user_subscription.username).one()
        new_usage = DailyUsage(
            date=usage_create.date,
            user_subscription_id=us.id,
            user_subscription=us,
            usage=usage_create.usage)
        self.session.add(new_usage)
        self.session.commit()

    def get_application_daily_usages(
        self, username: str, application: str
    ) -> List[UsageDetails]:
        try:
            usages = self.session.query(DailyUsage).filter(
                DailyUsage.user_subscription.username == username,
                DailyUsage.user_subscription.application == application,
            )
        except NoResultFound:
            return []

        data = []
        for usage in usages:
            data.append(
                UsageDetails(
                    date=usage.date,
                    username=username,
                    application=application,
                    usage=usage.usage,
                )
            )
        return data

    def get_daily_usages(self, username: str) -> List[UsageDetails]:
        try:
            usages = self.session.query(DailyUsage).filter(
                DailyUsage.user_subscription.username == username,
            )
        except NoResultFound:
            return []

        data = []
        for usage in usages:
            data.append(
                UsageDetails(
                    date=usage.date,
                    username=username,
                    application=usage.user_subscription.application,
                    usage=usage.usage,
                )
            )
        return data
