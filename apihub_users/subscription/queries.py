from typing import List
from sqlalchemy import or_
from sqlalchemy.exc import NoResultFound
from redis import Redis

from ..common.queries import BaseQuery
from .models import UserSubscription, Subscription
from .schemas import *
from .helpers import get_and_reset_balance_in_cache


class UserSubscriptionException(Exception):
    pass


class UserSubscriptionQuery(BaseQuery):

    def create_or_get_subscription(self, subscription_create: SubscriptionCreate):
        try:
            return self.get_subscription(subscription_create.application)
        except:
            try:
                new_subscription = Subscription(
                    application=subscription_create.application,
                    credit=subscription_create.credit,
                    recurring=subscription_create.recurring,
                )
                self.session.add(new_subscription)
                self.session.commit()
            except Exception as e:
                raise e

    def get_subscription(self, application: str) -> SubscriptionDetails:
        try:
            subscription = (
                self.session.query(Subscription)
                .filter(Subscription.application == application).one())
        except NoResultFound:
            raise UserSubscriptionException

        return SubscriptionDetails(
            application=application,
            credit=subscription.credit,
            recurring=subscription.recurring)

    def create_user_subscription(self, usc: UserSubscriptionCreate):
        try:
            sc = SubscriptionCreate(application=usc.application, credit=usc.credit,
                                    reccuring=usc.recurring)
            self.create_or_get_subscription(sc)
            us = UserSubscription(
                username=usc.username,
                application=usc.application,
                balance=usc.balance,
                expires_at=usc.expires_at,
                created_by=usc.created_by,
            )
            self.session.add(us)
            self.session.commit()
        except UserSubscriptionException:
            raise UserSubscriptionException

    def get_active_user_subscription(self, username: str,
                                     application: str) -> UserSubscriptionDetails:

        try:
            us = (self.session.query(UserSubscription)
                  .filter(
                UserSubscription.username == username,
                UserSubscription.application == application,
                or_(
                    UserSubscription.expires_at.is_(None),
                    UserSubscription.expires_at > datetime.now(),
                ),
            ).one())

        except NoResultFound:
            raise UserSubscriptionException

        return UserSubscriptionDetails(
            username=us.username,
            application=us.application,
            credit=us.subscription.credit,
            balance=us.balance,
            expires_at=us.expires_at,
            recurring=us.subscription.recurring,
            created_by=us.created_by,
            created_at=us.created_at)

    def get_active_user_subscriptions(self, username: str) -> List[UserSubscriptionDetails]:
        try:
            uss = self.session.query(UserSubscription).filter(
                UserSubscription.username == username,
                or_(
                    UserSubscription.expires_at.is_(None),
                    UserSubscription.expires_at > datetime.now(),
                ),
            )
        except NoResultFound:
            raise UserSubscriptionException

        data = []
        for us in uss:
            us_details = UserSubscriptionDetails(
                username=us.username,
                application=us.application,
                credit=us.subscription.credit,
                balance=us.balance,
                expires_at=us.expires_at,
                recurring=us.subscription.recurring,
                created_by=us.subscription.created_by,
                created_at=us.created_at)
            data.append(us_details)

        return data

    def update_balance_in_user_subscription(self, username: str,
                                            application: str,
                                            redis: Redis) -> UserSubscriptionDetails:
        try:
            us = (self.session.query(UserSubscription)
                  .filter(
                UserSubscription.username == username,
                UserSubscription.application == application,
                or_(
                    UserSubscription.expires_at.is_(None),
                    UserSubscription.expires_at > datetime.now(),
                ),
            ).one())
        except NoResultFound:
            raise UserSubscriptionException

        with get_and_reset_balance_in_cache(username, application, redis) as balance:
            us.balance = us.subscription.credit - balance
            self.session.add(us)
            self.session.commit()

        return UserSubscriptionDetails(
            username=us.username,
            application=us.application,
            credit=us.subscription.credit,
            balance=us.balance,
            expires_at=us.expires_at,
            recurring=us.subscription.recurring,
            created_by=us.subscription.created_by,
            created_at=us.created_at)
