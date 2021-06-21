from fastapi import APIRouter, Depends

from ..common.db_session import create_session
from ..security.schemas import UserBase  # TODO create a model for this UserBase
from ..security.depends import require_token
from .queries import UsageQuery, UsageException


HTTP_429_TOO_MANY_REQUESTS = 429

router = APIRouter()


@router.get("/usages/{application}")
def get_me_usages_application(
    application: str,
    user: UserBase = Depends(require_token),
    session=Depends(create_session),
):
    query = UsageQuery(session)
    try:
        usages = query.get_application_daily_usages(user.username, application)
    except UsageException:
        return {}

    return usages


@router.get("/usages")
def get_me_usages(
    user: UserBase = Depends(require_token),
    session=Depends(create_session),
):
    print(user.username)
    query = UsageQuery(session)
    try:
        usages = query.get_daily_usages(user.username)
    except UsageException:
        raise

    return usages
