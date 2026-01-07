import pytest

from src.domain.users import UserRole
from httpx import AsyncClient
import itertools


AVAILABLE_ROLES = [UserRole.DEFAULT, UserRole.MANAGER, UserRole.ADMIN]

USER_GRANT_ROLE_TEST_CASES = (
    [
        ("user1@example.com", target, role, False)
        for role, target in itertools.product(
            AVAILABLE_ROLES,
            [
                "user1@example.com",
                "user2@example.com",
                "manager@example.com",
                "admin@example.com",
            ],
        )
    ]
    + [
        ("manager@example.com", "user1@example.com", UserRole.DEFAULT, True),
        ("manager@example.com", "user1@example.com", UserRole.MANAGER, True),
        ("manager@example.com", "user1@example.com", UserRole.ADMIN, False),
        (
            "manager@example.com",
            "manager@example.com",
            UserRole.DEFAULT,
            False,
        ),
        (
            "manager@example.com",
            "manager@example.com",
            UserRole.MANAGER,
            False,
        ),
        ("manager@example.com", "manager@example.com", UserRole.ADMIN, False),
        ("manager@example.com", "admin@example.com", UserRole.DEFAULT, False),
        ("manager@example.com", "admin@example.com", UserRole.MANAGER, False),
        ("manager@example.com", "admin@example.com", UserRole.ADMIN, False),
    ]
    + [
        ("admin@example.com", target, role, True)
        for role, target in itertools.product(
            AVAILABLE_ROLES,
            [
                "user1@example.com",
                "user2@example.com",
                "manager@example.com",
            ],
        )
    ]
    + [
        ("admin@example.com", "admin@example.com", role, False)
        for role in AVAILABLE_ROLES
    ]
    + [
        ("admin@example.com", "manager@example.com", role, False)
        for role in AVAILABLE_ROLES
    ]
)


@pytest.mark.parametrize(
    ["invoker_email", "target_email", "role", "success"],
    USER_GRANT_ROLE_TEST_CASES,
)
@pytest.mark.asyncio
async def test_user_grant_role(
    client: AsyncClient,
    user_factory,
    invoker_email,
    target_email,
    success,
    user_jwt_headers,
    role: UserRole,
):

    _, target = (
        await user_factory(invoker_email, role=role),
        await user_factory(target_email, role=role),
    )
    invoker_headers = await user_jwt_headers(invoker_email)

    response = await client.patch(
        f"/api/users/{target.id}/role",
        params={"role": role.value},
        headers=invoker_headers,
    )
    if success:
        assert response.status_code == 200
    else:
        assert response.status_code in [400, 403]

    UNKNOWN_UUID = "b40c24c3-1a8f-4d67-9189-5a0b41ec5d3e"

    response = await client.patch(
        f"/api/users/{UNKNOWN_UUID}/role",
        params={"role": role.value},
        headers=invoker_headers,
    )
    if success:
        assert response.status_code == 400
    else:
        assert response.status_code in [400, 403]
