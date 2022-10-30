import datetime
from typing import List

from sqlalchemy.orm import Query
from sqlalchemy.exc import IntegrityError, NoResultFound

from ..common.queries import BaseQuery
from .models import DailyUsage, Activity
from .schemas import UsageDetails, UsageCreate, ActivityCreate, ActivityDetails


class UsageException(Exception):
    pass


class UsageQuery(BaseQuery):
    def create_usage(self, usage_create: UsageCreate) -> None:
        new_usage = DailyUsage(
            date=usage_create.date,
            username=usage_create.username,
            application=usage_create.application,
            usage=usage_create.usage,
        )
        self.session.add(new_usage)
        self.session.commit()

    def get_application_daily_usages(
        self, username: str, application: str
    ) -> List[UsageDetails]:
        try:
            usages = self.session.query(DailyUsage).filter(
                DailyUsage.username == username,
                DailyUsage.application == application,
            )
        except NoResultFound:
            return []

        data = []
        for usage in usages:
            data.append(
                UsageDetails(
                    date=usage.date,
                    username=usage.username,
                    application=usage.application,
                    usage=usage.usage,
                )
            )
        return data

    def get_daily_usages(self, username: str) -> List[UsageDetails]:
        try:
            usages = self.session.query(DailyUsage).filter(
                DailyUsage.username == username,
            )
        except NoResultFound:
            return []

        data = []
        for usage in usages:
            data.append(
                UsageDetails(
                    date=usage.date,
                    username=usage.username,
                    application=usage.application,
                    usage=usage.usage,
                )
            )
        return data


class ActivityException(Exception):
    pass


class ActivityQuery(BaseQuery):
    def get_query(self) -> Query:
        return self.session.query(Activity)

    def create_activity_helper(self, activity_log: ActivityCreate) -> bool:
        """ """
        db_al = Activity(**activity_log.make_activity().dict())
        self.session.add(db_al)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            return False

        return True

    def get_activity_by_key(self, key: str) -> ActivityDetails:
        activity = self.get_query().filter(Activity.request_key == key).one()
        return ActivityDetails(
            created_at=activity.created_at,
            request=activity.request,
            subscription_type=activity.subscription_type,
            status=activity.status,
            request_key=activity.request_key,
            result=activity.result,
            payload=activity.payload,
            ip_address=activity.ip_address,
            latency=activity.latency,
        )

    def get_activities_count(self, **kwargs) -> int:

        return self.get_query().filter_by(**kwargs).count()

    def update_activity(self, key, set_latency=True, **kwargs) -> bool:
        activity = self.get_query().filter(Activity.request_key == key).one()
        if set_latency:
            kwargs["latency"] = (datetime.datetime.now() - activity.created_at).seconds

        activity = activity.dict(exclude_unset=True)
        for key, value in kwargs.items():
            setattr(activity, key, value)

        self.session.add(activity)
        try:
            self.session.commit()
            self.session.refresh(activity)
        except IntegrityError:
            self.session.rollback()
            return False

        return True
