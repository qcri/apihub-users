from datetime import date, timedelta
from unittest import mock

import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from apihub_users.common.db_session import create_session
from apihub_users.common.redis_session import redis_conn
from apihub_users.security.schemas import UserBase, UserType
from apihub_users.security.depends import require_user, require_admin, require_token
from apihub_users.subscription.depends import require_subscription
from apihub_users.usage.depends import update_daily_usage
from apihub_users.usage.helpers import copy_yesterday_usage
from apihub_users.usage.router import router


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

    def _require_subscription():
        return "tester"

    app = FastAPI()
    app.include_router(router)

    app.dependency_overrides[create_session] = _create_session
    app.dependency_overrides[require_admin] = _require_admin
    app.dependency_overrides[require_user] = _require_user
    app.dependency_overrides[require_token] = _require_token
    app.dependency_overrides[require_subscription] = _require_subscription

    @app.get("/api/{application}", dependencies=[Depends(update_daily_usage)])
    def api_function_1(username: str = Depends(require_user)):
        pass

    yield TestClient(app)


@pytest.fixture(scope="function")
def redis():
    for r in redis_conn():
        r.flushdb()
        yield r


class TestUsage:
    def test_update_daily_usage(self, client, db_session, redis, monkeypatch):
        import apihub_users.usage.depends

        _date = mock.MagicMock()
        _date.today.return_value = date.today() + timedelta(days=-1)

        monkeypatch.setattr(apihub_users.usage.depends, "date", _date)

        response = client.get(
            "/api/test",
        )
        assert response.status_code == 200
        assert _date.today.called

        response = client.get(
            "/api/test",
        )

        copy_yesterday_usage(redis, db_session)

        response = client.get(
            "/usages",
        )
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["usage"] == 2
