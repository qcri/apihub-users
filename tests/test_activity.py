import pytest
from datetime import datetime
import factory
from fastapi import FastAPI
from fastapi.testclient import TestClient

from apihub_users.common.db_session import create_session
from apihub_users.subscription.router import router
from apihub_users.subscription.models import SubscriptionTier
from apihub_users.usage.models import Activity
from apihub_users.usage.queries import ActivityQuery, ActivityException
from apihub_users.usage.schemas import ActivityCreate, ActivityStatus


class ActivityFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Activity

    id = factory.Sequence(int)
    created_at = factory.LazyFunction(datetime.now)
    request = "/async/app1"
    username = factory.Sequence(lambda n: f"tester{n}")
    tier = SubscriptionTier.TRIAL
    status = ActivityStatus.PROCESSED
    request_key = "123"
    result = ""
    payload = ""
    ip_address = ""
    latency = 0.0


@pytest.fixture(scope="function")
def client(db_session):
    def _create_session():
        try:
            yield db_session
        finally:
            pass

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[create_session] = _create_session
    ActivityFactory._meta.sqlalchemy_session = db_session
    ActivityFactory._meta.sqlalchemy_session_persistence = "commit"
    ActivityFactory(
        username="tester",
        request="async/app1",
        request_key="app1_key",
        status=ActivityStatus.PROCESSED,
    )
    ActivityFactory(
        username="tester",
        request="async/app2",
        request_key="app2_key",
        status=ActivityStatus.ACCEPTED,
    )

    yield TestClient(app)


class TestStatistics:
    def test_create_activity(self, db_session):
        ActivityFactory._meta.sqlalchemy_session = db_session
        ActivityFactory._meta.sqlalchemy_session_persistence = "commit"

        query = ActivityQuery(db_session)
        assert (
            query.create_activity(
                ActivityCreate(
                    request="async/test",
                    username="ahmed",
                    tier=SubscriptionTier.TRIAL,
                    status=ActivityStatus.ACCEPTED,
                    request_key="async/test_key",
                    result="",
                    payload="",
                    ip_address="",
                    latency=0.0,
                )
            )
            is None
        )
        assert (
            query.get_activity_by_key("async/test_key").request_key == "async/test_key"
        )

    def test_get_activity_by_key(self, client, db_session):
        query = ActivityQuery(db_session)
        assert query.get_activity_by_key("app1_key").request_key == "app1_key"

        with pytest.raises(ActivityException):
            query.get_activity_by_key("key 2")

    def test_update_activity(self, client, db_session):
        query = ActivityQuery(db_session)
        assert (
            query.update_activity(
                "app1_key",
                **{"tier": SubscriptionTier.STANDARD, "ip_address": "test ip"},
            )
            is None
        )
        activity = query.get_activity_by_key("app1_key")
        assert (
            activity.tier == SubscriptionTier.STANDARD
            and activity.ip_address == "test ip"
            and activity.latency > 0.0
        )

        with pytest.raises(ActivityException):
            query.update_activity(
                "not existing",
                **{"tier": SubscriptionTier.STANDARD, "ip_address": "test ip"},
            )
