from typing import List

from sqlalchemy.orm import Query
from sqlalchemy.exc import IntegrityError, NoResultFound

from ..common.queries import BaseQuery
from .models import DailyUsage, ActivityLog
from .schemas import UsageDetails, UsageCreate, ActivityLogCreate


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


class ActivityLogException(Exception):
    pass


class ActivityLogQuery(BaseQuery):
    def get_query(self) -> Query:
        return self.session.query(ActivityLog)

    def create_activity_log(self, activity_log: ActivityLogCreate) -> bool:
        """ """
        db_al = ActivityLog(**activity_log.activity_log_schema().dict())
        self.session.add(db_al)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            return False

        return True
