from datetime import datetime

import pytest
import factory
from fastapi import FastAPI
from fastapi.testclient import TestClient

from apihub_users.common.db_session import create_session
from apihub_users.security.schemas import UserBase, UserType
from apihub_users.security.depends import require_token

from apihub_users.subscription.router import router
from apihub_users.usage.models import Activity


class ActivityFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Activity

    id = factory.Sequence(int)
    username = factory.Sequence(lambda n: f"tester{n}")
    application = "test"
    status = "processed"
    request = "/async/app1"
    key = "123"
    created_at = factory.LazyFunction(datetime.now)
    result = ""
    ip_address = ""
    latency = 1


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
    app.dependency_overrides[require_token] = _require_user_token

    ActivityFactory._meta.sqlalchemy_session = db_session
    ActivityFactory._meta.sqlalchemy_session_persistence = "commit"

    ActivityFactory(username="tester", application="app1", status="processed")

    yield TestClient(app)

def _require_user_token():
    return UserBase(username="tester", role=UserType.USER)


class TestStatistics:
    def test_count_requests(self, client):
        response = client.get(
            "/requests", params={"status": "processed"}
        )
        r = response.json()
        assert response.status_code == 200 and r["count"] == 1

        response = client.get(
            "/requests", params={"status": "accepted"}
        )
        r = response.json()
        assert response.status_code == 200 and r["count"] == 0
