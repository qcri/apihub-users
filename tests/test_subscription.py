from datetime import datetime, timedelta

import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from apihub_users.security.models import User
# don't remove these two lines.
from apihub_users.subscription.models import Subscription, UserSubscription
from apihub_users.usage.models import DailyUsage
from apihub_users.common.db_session import create_session
from apihub_users.security.schemas import UserBase, UserType
from apihub_users.subscription.schemas import SubscriptionIn
from apihub_users.security.depends import require_user, require_admin, require_token
from apihub_users.subscription.depends import require_subscription_balance
from apihub_users.subscription.models import UserSubscription, Subscription
from apihub_users.subscription.router import router
import factory.fuzzy


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        abstract = True


class UserFactory(BaseFactory):
    class Meta:
        model = User

    id = factory.Sequence(int)
    username = factory.Sequence(lambda n: f"tester{n}")
    email = "sas@df.ds"
    role = "admin"
    is_active = True
    created_at = factory.LazyFunction(datetime.now)


class SubscriptionFactory(BaseFactory):
    class Meta:
        model = Subscription

    id = factory.Sequence(int)
    recurring = False
    application = "test"
    credit = 100


class UserSubscriptionFactory(BaseFactory):
    class Meta:
        model = UserSubscription

    id = factory.Sequence(int)
    username = factory.Sequence(lambda n: f"tester{n}")
    application = "test"
    # user = factory.SubFactory(UserFactory)
    # subscription = factory.SubFactory(SubscriptionFactory)
    balance = 0
    starts_at = factory.LazyFunction(datetime.now)
    expires_at = factory.LazyFunction(lambda: datetime.now() + timedelta(days=1))
    created_at = factory.LazyFunction(datetime.now)
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

    def _require_admin_token():
        return UserBase(username="tester", role=UserType.ADMIN)

    def _require_user_token():
        return UserBase(username="tester", role=UserType.USER)

    app = FastAPI()
    app.include_router(router)

    app.dependency_overrides[create_session] = _create_session
    app.dependency_overrides[require_admin] = _require_admin
    app.dependency_overrides[require_user] = _require_user
    app.dependency_overrides[require_token] = _require_user_token

    @app.get("/api/{application}", dependencies=[Depends(update_subscription_balance)])
    def api_function_1(application: str, username: str = Depends(require_subscription)):
        pass

    @app.get("/api_balance/{application}")
    def api_function_2(
        application: str, username: str = Depends(require_subscription_balance)
    ):
        pass

    yield TestClient(app)


def _require_admin_token():
    return UserBase(username="tester", role=UserType.ADMIN)


def _require_user_token():
    return UserBase(username="tester", role=UserType.USER)


class TestSubscription:
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

    def test_create_subscription_non_existing_user(self, client):
        new_subscription = SubscriptionIn(
            username="new user",
            application="application",
            credit=123,
            expires_at=None,
            recurring=False,
        )
        response = client.post(
            "/subscription",
            data=new_subscription.json(),
        )
        assert response.status_code == 404

    def test_get_application_token(self, client, db_session):
        UserSubscriptionFactory._meta.sqlalchemy_session = db_session
        UserSubscriptionFactory._meta.sqlalchemy_session_persistence = "commit"

        UserSubscriptionFactory(username="test", application="app", balance=100)

        response = client.get(
            "/token/app",
        )
        assert response.status_code == 200, response.json()
        assert response.json().get("token") is not None

    def test_get_application_token_admin(self, client, db_session):
        client.app.dependency_overrides[require_token] = _require_admin_token
        UserSubscriptionFactory._meta.sqlalchemy_session = db_session
        UserSubscriptionFactory._meta.sqlalchemy_session_persistence = "commit"

        UserSubscriptionFactory(username="tester", application="app", credit=1000)

        response = client.get(
            "/token/app",
            params={
                "username": "tester",
                "expires_days": 30,
            },
        )
        client.app.dependency_overrides[require_token] = _require_user_token
        assert response.status_code == 200, response.json()
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
        assert response.status_code == 200, response.json()

        response = client.post(
            "/subscription",
            data=new_subscription.json(),
        )
        assert response.status_code == 200, response.json()

    def test_update_balance(self, client, db_session):
        UserSubscriptionFactory._meta.sqlalchemy_session = db_session
        UserSubscriptionFactory._meta.sqlalchemy_session_persistence = "commit"

        UserSubscriptionFactory(username="tester", application="test", credit=1)

        response = client.get(
            "/token/test",
        )
        assert response.status_code == 200, response.json()
        token = response.json().get("token")

        response = client.get("/api/test", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200, response.json()

    def test_require_balance(self, client, db_session):
        UserSubscriptionFactory._meta.sqlalchemy_session = db_session
        UserSubscriptionFactory._meta.sqlalchemy_session_persistence = "commit"

        UserSubscriptionFactory(username="tester", application="test", credit=2)

        response = client.get(
            "/token/test",
        )
        assert response.status_code == 200, response.json()
        token = response.json().get("token")

        response = client.get(
            "/api_balance/test", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.json()

        response = client.get(
            "/api_balance/test", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.json()

        response = client.get(
            "/api_balance/test", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 429, response.json()
