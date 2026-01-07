import pytest
from httpx import AsyncClient
from uuid import uuid4
from fastapi import status
from src.domain.teams import TeamRole


@pytest.mark.asyncio
async def test_team_creation_assigns_owner_role(
    client: AsyncClient, admin_user, user_jwt_headers
):
    headers = await user_jwt_headers(admin_user.email)
    response = await client.post(
        "/api/teams",
        json={"name": "New Team"},
        headers=headers,
    )
    assert response.status_code == status.HTTP_201_CREATED

    # Verify the creator becomes OWNER
    team_id = response.json()["data"]["id"]
    member_response = await client.get(
        f"/api/teams/{team_id}/members/{admin_user.id}",
        headers=headers,
    )
    assert member_response.status_code == status.HTTP_200_OK
    assert member_response.json()["data"]["role"] == TeamRole.OWNER.value


@pytest.mark.asyncio
async def test_protected_owner_role(
    client: AsyncClient,
    team_with_owner,
    admin_user,
    manager_user,
    user_jwt_headers,
):
    admin_headers = await user_jwt_headers(admin_user.email)

    # Attempt to change OWNER role (should be protected)
    response = await client.patch(
        f"/api/teams/{team_with_owner['id']}/members/{admin_user.id}/role",
        params={"role": TeamRole.ADMIN.value},
        headers=admin_headers,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "insufficient" in response.json()["detail"].lower()

    # Attempt to remove OWNER (should be protected)
    response = await client.delete(
        f"/api/teams/{team_with_owner['id']}/members/{admin_user.id}",
        headers=admin_headers,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "protected role" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_role_hierarchy(
    client: AsyncClient,
    team_with_member,
    admin_user,
    manager_user,
    common_user,
    user_jwt_headers,
):
    admin_headers = await user_jwt_headers(admin_user.email)
    manager_headers = await user_jwt_headers(manager_user.email)
    user_headers = await user_jwt_headers(common_user.email)

    # Add manager and user to a team
    response = await client.post(
        f"/api/teams/{team_with_member['id']}/members",
        json={"new_member_id": str(manager_user.id)},
        headers=admin_headers,
    )
    assert response.status_code == status.HTTP_201_CREATED

    response = await client.post(
        f"/api/teams/{team_with_member['id']}/members",
        json={"new_member_id": str(common_user.id)},
        headers=admin_headers,
    )
    assert response.status_code == status.HTTP_201_CREATED

    # Make manager an ADMIN to test hierarchy
    response = await client.patch(
        f"/api/teams/{team_with_member['id']}/members/{manager_user.id}/role",
        params={"role": TeamRole.ADMIN.value},
        headers=admin_headers,
    )
    assert response.status_code == status.HTTP_200_OK

    # Manager (now ADMIN) attempts to promote regular user to MANAGER
    response = await client.patch(
        f"/api/teams/{team_with_member['id']}/members/{common_user.id}/role",
        params={"role": TeamRole.MANAGER.value},
        headers=manager_headers,
    )
    assert response.status_code == status.HTTP_200_OK

    # Regular user attempts to change manager's role (should fail hierarchy check)
    response = await client.patch(
        f"/api/teams/{team_with_member['id']}/members/{manager_user.id}/role",
        params={"role": TeamRole.EMPLOYEE.value},
        headers=user_headers,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "insufficient" in response.json()["detail"].lower()

    # Revert regular user back to EMPLOYEE role
    response = await client.patch(
        f"/api/teams/{team_with_member['id']}/members/{common_user.id}/role",
        params={"role": TeamRole.EMPLOYEE.value},
        headers=manager_headers,
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_permission_system(
    client: AsyncClient,
    team_with_member,
    admin_user,
    manager_user,
    common_user,
    user_jwt_headers,
):
    admin_headers = await user_jwt_headers(admin_user.email)
    manager_headers = await user_jwt_headers(manager_user.email)
    user_headers = await user_jwt_headers(common_user.email)

    # Verify EMPLOYEE can only view
    response = await client.get(
        f"/api/teams/{team_with_member['id']}",
        headers=user_headers,
    )
    assert response.status_code == status.HTTP_200_OK

    # EMPLOYEE cannot add members
    response = await client.post(
        f"/api/teams/{team_with_member['id']}/members",
        json={"new_member_id": str(uuid4())},
        headers=user_headers,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Make user a MANAGER
    response = await client.patch(
        f"/api/teams/{team_with_member['id']}/members/{common_user.id}/role",
        params={"role": TeamRole.MANAGER.value},
        headers=admin_headers,
    )
    assert response.status_code == status.HTTP_200_OK

    # Now MANAGER can add members
    response = await client.post(
        f"/api/teams/{team_with_member['id']}/members",
        json={"new_member_id": str(uuid4())},
        headers=user_headers,
    )
    assert response.status_code == status.HTTP_201_CREATED

    # But cannot change roles (only ADMIN and above)
    response = await client.patch(
        f"/api/teams/{team_with_member['id']}/members/{manager_user.id}/role",
        params={"role": TeamRole.EMPLOYEE.value},
        headers=user_headers,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Revert user back to EMPLOYEE role
    response = await client.patch(
        f"/api/teams/{team_with_member['id']}/members/{common_user.id}/role",
        params={"role": TeamRole.EMPLOYEE.value},
        headers=manager_headers,
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_invite_system_permissions(
    client: AsyncClient,
    team_with_member,
    admin_user,
    manager_user,
    common_user,
    user_jwt_headers,
):
    admin_headers = await user_jwt_headers(admin_user.email)
    manager_headers = await user_jwt_headers(manager_user.email)
    user_headers = await user_jwt_headers(common_user.email)

    # ADMIN can generate invites
    response = await client.post(
        f"/api/teams/{team_with_member['id']}/invite",
        headers=admin_headers,
    )
    assert response.status_code == status.HTTP_200_OK

    # MANAGER can generate invites
    response = await client.post(
        f"/api/teams/{team_with_member['id']}/invite",
        headers=manager_headers,
    )
    assert response.status_code == status.HTTP_200_OK

    # EMPLOYEE cannot generate invites
    response = await client.post(
        f"/api/teams/{team_with_member['id']}/invite",
        headers=user_headers,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
