import pytest
import datetime
import factory
from fastapi import FastAPI
from fastapi.testclient import TestClient

from apihub_users.common.db_session import create_session
from apihub_users.subscription.router import router
from apihub_users.subscription.models import SubscriptionType
from apihub_users.usage.models import Activity
from apihub_users.usage.queries import ActivityQuery, ActivityException
from apihub_users.usage.schemas import ActivityCreate


class ActivityFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Activity

    id = factory.Sequence(int)
    created_at = factory.LazyFunction(datetime.now)
    request = "/async/app1"
    username = factory.Sequence(lambda n: f"tester{n}")
    subscription_type = SubscriptionType.TRIAL
    status = "processed"
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
        status="processed",
    )
    ActivityFactory(
        username="tester",
        request="async/app2",
        request_key="app2_key",
        status="accepted",
    )

    yield TestClient(app)


class TestStatistics:
    def test_create_activity_helper(self, db_session):
        ActivityFactory._meta.sqlalchemy_session = db_session
        ActivityFactory._meta.sqlalchemy_session_persistence = "commit"

        assert (
            ActivityQuery(db_session).create_activity_helper(
                ActivityCreate(
                    request="async/test",
                    username="ahmed",
                    subscription_type="trial",
                    status="accepted",
                    request_key="test_key",
                    result="",
                    payload="",
                    ip_address="",
                    latency=0.0,
                )
            )
            is True
        )

    def test_get_activity_by_key(self, client, db_session):
        query = ActivityQuery(db_session)
        assert query.get_activity_by_key("app1_key") is not None

        with pytest.raises(ActivityException):
            query.get_activity_by_key("key 2")

    def test_get_activities_count(self, client, db_session):
        query = ActivityQuery(db_session)
        count = query.get_activities_count(**{"status": "accepted"})
        assert count == 1

        count = query.get_activities_count(**{"status": "processed"})
        assert count == 1

        count = query.get_activities_count()
        assert count == 2

    def test_update_activity(self, client, db_session):
        query = ActivityQuery(db_session)
        assert (
            query.update_activity(
                "app1_key", **{"subscription_type": "standard", "ip_address": "test ip"}
            )
            is True
        )
        activity = query.get_activity_by_key("app1_key")
        assert (
            activity.subscription_type == "standard"
            and activity.ip_address == "test ip"
            and activity.latency > 0.0
        )
