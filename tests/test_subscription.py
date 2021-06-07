from datetime import datetime, timedelta

import pytest
import factory
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from apihub_users.common.db_session import create_session
from apihub_users.security.schemas import UserBase, UserType
from apihub_users.security.depends import require_user, require_admin, require_token
from apihub_users.subscription.depends import (
    require_subscription,
    update_subscription_balance,
    require_subscription_balance,
)
from apihub_users.subscription.models import Subscription
from apihub_users.subscription.router import router, SubscriptionIn


class SubscriptionFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Subscription

    id = factory.Sequence(int)
    username = factory.Sequence(lambda n: f"tester{n}")
    application = "test"
    credit = 100
    balance = 0
    starts_at = factory.LazyFunction(datetime.now)
    expires_at = factory.LazyFunction(lambda: datetime.now() + timedelta(days=1))
    recurring = False
    created_at = factory.LazyFunction(datetime.now)
    created_by = "admin"
    notes = None


@pytest.fixture(scope="function")
def client(db_session):
    def _create_session():
        try:
            yield db_session
        finally:
            pass

    def _require_admin():
        return "admin"

    def _require_user():
        return "user"

    def _require_token():
        return UserBase(username="tester", role=UserType.ADMIN)

    app = FastAPI()
    app.include_router(router)

    app.dependency_overrides[create_session] = _create_session
    app.dependency_overrides[require_admin] = _require_admin
    app.dependency_overrides[require_user] = _require_user
    app.dependency_overrides[require_token] = _require_token

    @app.get("/api/{application}", dependencies=[Depends(update_subscription_balance)])
    def api_function_1(application: str, username: str = Depends(require_subscription)):
        pass

    @app.get("/api_balance/{application}")
    def api_function_2(
        application: str, username: str = Depends(require_subscription_balance)
    ):
        pass

    yield TestClient(app)


class TestApplication:
    def test_create_and_get_subscription(self, client):
        new_subscription = SubscriptionIn(
            username="tester",
            application="application",
            credit=123,
            expires_at=None,
            recurring=False,
        )
        response = client.post(
            "/subscription",
            data=new_subscription.json(),
        )
        assert response.status_code == 200

        response = client.get(
            "/subscription/application",
        )
        assert response.status_code == 200
        assert response.json().get("credit") == 123

    def test_get_application_token(self, client, db_session):
        SubscriptionFactory._meta.sqlalchemy_session = db_session
        SubscriptionFactory._meta.sqlalchemy_session_persistence = "commit"

        SubscriptionFactory(username="user", application="app", credit=1000)

        response = client.get(
            "/token/app",
        )
        assert response.status_code == 200
        assert response.json().get("token") is not None

    def test_create_duplicate_subscription(self, client):
        new_subscription = SubscriptionIn(
            username="tester",
            application="application",
            credit=123,
            expires_at=None,
            recurring=False,
        )
        response = client.post(
            "/subscription",
            data=new_subscription.json(),
        )
        assert response.status_code == 200

        response = client.post(
            "/subscription",
            data=new_subscription.json(),
        )
        assert response.status_code == 200

    def test_update_balance(self, client, db_session):
        SubscriptionFactory._meta.sqlalchemy_session = db_session
        SubscriptionFactory._meta.sqlalchemy_session_persistence = "commit"

        SubscriptionFactory(username="user", application="test", credit=1)

        response = client.get(
            "/token/test",
        )
        assert response.status_code == 200
        token = response.json().get("token")

        response = client.get("/api/test", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200

    def test_require_balance(self, client, db_session):
        SubscriptionFactory._meta.sqlalchemy_session = db_session
        SubscriptionFactory._meta.sqlalchemy_session_persistence = "commit"

        SubscriptionFactory(username="user", application="test", credit=2)

        response = client.get(
            "/token/test",
        )
        assert response.status_code == 200
        token = response.json().get("token")

        response = client.get(
            "/api_balance/test", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

        response = client.get(
            "/api_balance/test", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

        response = client.get(
            "/api_balance/test", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 429
