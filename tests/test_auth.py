import pytest
from httpx import AsyncClient
from src.domain.users import UserRole


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    response = await client.get("/api/health")
    assert response.status_code == 307


REGISTRATION_TEST_CASES = [
    ("user1@example.com", 201, 200),
    ("user2@example.com", 201, 200),
    ("user2@example.com", 400, 200),
    ("admin@example.com", 400, 200),
]


@pytest.mark.parametrize(
    "email,expected_register_status,expected_login_status",
    REGISTRATION_TEST_CASES,
)
@pytest.mark.asyncio
async def test_user_registration_lifecycle(
    client: AsyncClient,
    user_data_factory,
    login_data_factory,
    correct_password,
    wrong_password,
    email: str,
    expected_register_status: int,
    expected_login_status: int,
):
    register_data = user_data_factory(email, correct_password)
    register_response = await client.post("/api/auth/register", json=register_data)
    assert register_response.status_code == expected_register_status

    correct_login_data = login_data_factory(email, correct_password)
    login_response = await client.post(
        "/api/auth/login",
        data=correct_login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login_response.status_code == expected_login_status

    wrong_login_data = login_data_factory(email, wrong_password)
    wrong_login_response = await client.post(
        "/api/auth/login",
        data=wrong_login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert wrong_login_response.status_code == 400


USER_AUTH_TEST_CASES = [
    ("auth_flow_user1@example.com", UserRole.DEFAULT),
    ("auth_flow_manager@example.com", UserRole.MANAGER),
    ("auth_flow_admin@example.com", UserRole.ADMIN),
]


@pytest.mark.parametrize("email,role", USER_AUTH_TEST_CASES)
@pytest.mark.asyncio
async def test_user_auth_flow(
    client: AsyncClient,
    user_factory,
    user_jwt_headers,
    email: str,
    role: UserRole,
):

    await user_factory(email, role=role)
    headers = await user_jwt_headers(email)

    profile_response = await client.get("/api/users/me", headers=headers)
    assert profile_response.status_code == 200
    profile_data = profile_response.json()

    assert profile_data["email"] == email
    assert profile_data["role"] == role.value
    assert profile_data["is_active"] is True
    assert profile_data["is_verified"] is True
    assert profile_data["first_name"] is None
    assert profile_data["last_name"] is None

    update_data = {"first_name": "Test", "last_name": "User"}
    update_response = await client.patch(
        "/api/users/me", json=update_data, headers=headers
    )
    assert update_response.status_code == 200

    updated_profile_response = await client.get("/api/users/me", headers=headers)
    updated_data = updated_profile_response.json()
    assert updated_data["first_name"] == "Test"
    assert updated_data["last_name"] == "User"

    protected_response = await client.post(
        "/api/teams",
        json={"name": "Test Team"},
        headers=headers,
    )
    if role == UserRole.ADMIN:
        assert protected_response.status_code == 201
    else:
        assert protected_response.status_code == 403

    logout_response = await client.post("/api/auth/logout", headers=headers)
    assert logout_response.status_code == 204

    verify_logout_response = await client.get("/api/users/me", headers=headers)
    assert verify_logout_response.status_code == 200
