import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from fastapi_users.password import PasswordHelper
from fastapi import status
from src.db.database import AsyncDatabase
from src.db.models import Base, load_all_models
from src.web.application import get_app
from src.db.models.user import User, UserRole
from typing import Dict, Any, AsyncGenerator
from sqlalchemy import select
from uuid import UUID


@pytest_asyncio.fixture(scope="session")
async def db() -> AsyncGenerator[AsyncDatabase, None]:
    db = AsyncDatabase("sqlite+aiosqlite:///:memory:", isolation_level="AUTOCOMMIT")
    load_all_models()
    await db.create_tables(Base, with_drop=True)
    yield db
    await db.close_db()


@pytest_asyncio.fixture(scope="session")
async def client(db: AsyncDatabase) -> AsyncGenerator[AsyncClient, None]:
    app = get_app()
    app.state.db_session_factory = db.session_factory
    app.state.db_engine = db.engine
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest_asyncio.fixture(scope="module", autouse=True)
async def clean_db_between_modules(db: AsyncDatabase):
    yield
    async with db.get_session() as session:
        tables = Base.metadata.tables.values()
        for table in reversed(tables):
            await session.execute(table.delete())
        await session.commit()


@pytest.fixture(scope="session")
def correct_password() -> str:
    return "correct_password"


@pytest.fixture(scope="session")
def wrong_password() -> str:
    return "wrong_password"


@pytest.fixture
def user_data_factory():
    def _factory(email: str, password: str, **kwargs) -> Dict[str, Any]:
        return {
            "email": email,
            "password": password,
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
            **kwargs,
        }

    return _factory


@pytest.fixture(scope="module")
def login_data_factory():
    def _factory(username: str, password: str) -> Dict[str, str]:
        return {
            "grant_type": "password",
            "username": username,
            "password": password,
            "scope": "",
            "client_id": "string",
            "client_secret": "string",
        }

    return _factory


@pytest_asyncio.fixture(scope="session")
async def user_factory(db, correct_password):
    async def _factory(email: str, role: UserRole = UserRole.DEFAULT, **kwargs) -> User:
        user_data = {
            "email": email,
            "hashed_password": PasswordHelper().hash(correct_password),
            "role": role,
            "is_active": True,
            "is_verified": True,
            **kwargs,
        }
        async with db.get_session() as session:
            result = await session.execute(select(User).where(User.email == email))
            existing_user = result.scalars().one_or_none()
            if existing_user:
                return existing_user
            user = User(**user_data)
            session.add(user)
            await session.commit()
            await session.refresh(user)
        return user

    return _factory


@pytest_asyncio.fixture(scope="module", autouse=True)
async def admin_user(user_factory):
    return await user_factory("admin@example.com", role=UserRole.ADMIN)


@pytest_asyncio.fixture(scope="module", autouse=True)
async def manager_user(user_factory):
    return await user_factory("manager@example.com", role=UserRole.MANAGER)


@pytest_asyncio.fixture(scope="module", autouse=True)
async def common_user(user_factory):
    return await user_factory("user@example.com", role=UserRole.DEFAULT)


@pytest_asyncio.fixture(scope="module", autouse=True)
async def another_user(user_factory):
    return await user_factory("user@example.com", role=UserRole.DEFAULT)


@pytest_asyncio.fixture(scope="module")
async def common_user_id(common_user) -> UUID:
    return common_user.id


@pytest_asyncio.fixture(scope="module")
async def auth_headers(client, login_data_factory):
    async def _factory(email: str, password: str) -> Dict[str, str]:
        login_data = login_data_factory(email, password)
        response = await client.post("/api/auth/login", data=login_data)
        assert response.status_code == 200
        return {
            "Authorization": f"Bearer {response.json()['access_token']}",
            "Content-Type": "application/json",
        }

    return _factory


@pytest_asyncio.fixture(scope="module")
async def user_jwt_headers(auth_headers, correct_password):
    async def _factory(email: str) -> Dict[str, str]:
        return await auth_headers(email, correct_password)

    return _factory


@pytest_asyncio.fixture(scope="module")
async def team_with_owner(client: AsyncClient, admin_user, user_jwt_headers) -> dict:
    """Fixture creates a team with an owner (admin)"""
    headers = await user_jwt_headers(admin_user.email)
    response = await client.post(
        "/api/teams",
        json={"name": "Team with Owner"},
        headers=headers,
    )
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()["data"]


@pytest_asyncio.fixture(scope="module")
async def team_with_member(
    client: AsyncClient,
    team_with_owner,
    admin_user,
    common_user,
    user_jwt_headers,
) -> dict:
    """Fixture creates a team with a member (EMPLOYEE)"""
    headers = await user_jwt_headers(admin_user.email)
    response = await client.post(
        f"/api/teams/{team_with_owner['id']}/members",
        json={"new_member_id": str(common_user.id)},
        headers=headers,
    )
    assert response.status_code == status.HTTP_201_CREATED
    return team_with_owner


@pytest_asyncio.fixture(scope="module")
async def other_team_with_owner(
    client: AsyncClient, admin_user, user_jwt_headers
) -> dict:
    """Fixture creates a team with an owner (admin)"""
    headers = await user_jwt_headers(admin_user.email)
    response = await client.post(
        "/api/teams",
        json={"name": "Other team with Owner"},
        headers=headers,
    )
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()["data"]
