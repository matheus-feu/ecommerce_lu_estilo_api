from unittest.mock import Mock

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from src import app
from src.auth.dependencies import AccessTokenBearer, RefreshTokenBearer
from src.auth.security import RoleChecker
from src.db.database import get_session

mock_session = Mock()
mock_user_service = Mock()


def get_mock_session():
    yield mock_session


acess_token_bearer = AccessTokenBearer()
refresh_token_bearer = RefreshTokenBearer()
role_checker = RoleChecker(["admin", "customer"])

app.dependency_overrides[get_session] = get_mock_session
app.dependency_overrides[role_checker] = Mock()
app.dependency_overrides[refresh_token_bearer] = Mock()


@pytest.fixture
def fake_session():
    """
    Mock session for testing.
    """
    return mock_session


@pytest.fixture
def fake_user_service():
    """
    Mock user service for testing.
    """
    return mock_user_service


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
