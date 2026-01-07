import pytest
from fastapi import status
from httpx import AsyncClient
from src.domain.teams import TeamRole


@pytest.mark.asyncio
async def test_task_creation(
    client: AsyncClient,
    team_with_member,
    other_team_with_owner,
    admin_user,
    manager_user,
    common_user,
    user_jwt_headers,
):
    admin_headers = await user_jwt_headers(admin_user.email)
    user_headers = await user_jwt_headers(common_user.email)

    with_user_team_id = team_with_member["id"]
    without_user_team_id = other_team_with_owner["id"]

    UNKNOWN_UUID = "b40c24c3-1a8f-4d67-9189-5a0b41ec5d3e"

    response = await client.post(
        "/api/tasks",
        json={
            "team_id": UNKNOWN_UUID,
            "title": "unknown",
            "deadline": "2025-05-22T15:25:22.037Z",
            "description": "Test description",
        },
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    # Admin creates five tasks
    for i in range(1, 6):
        task_title = f"Task №{i}"
        response = await client.post(
            "/api/tasks",
            json={
                "team_id": team_with_member["id"],
                "title": task_title,
                "deadline": "2025-05-22T15:25:22.037Z",
                "description": "Test description",
            },
            headers=admin_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["data"]["author_id"] == str(admin_user.id)
        assert response.json()["data"]["title"] == task_title

    # All of them appears on an personal authored task list
    response = await client.get("/api/tasks/authored", headers=admin_headers)

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["count"] == 5
    assert all([value["author_id"] == str(admin_user.id) for value in json["values"]])
    assert all([value["title"].startswith("Task №") for value in json["values"]])

    # User attempts to create a task
    response = await client.post(
        "/api/tasks",
        json={
            "team_id": with_user_team_id,
            "title": "User task",
            "deadline": "2025-05-22T15:25:22.037Z",
            "description": "Test description",
        },
        headers=user_headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "permissions" in response.json()["detail"]

    # User is not a member of this team, so the id of a team is not recognized.

    response = await client.post(
        "/api/tasks",
        json={
            "team_id": without_user_team_id,
            "title": "User task",
            "deadline": "2025-05-22T15:25:22.037Z",
            "description": "Test description",
        },
        headers=user_headers,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    # Same happens with unknown team_id (like with an admin)

    response = await client.post(
        "/api/tasks",
        json={
            "team_id": UNKNOWN_UUID,
            "title": "User task",
            "deadline": "2025-05-22T15:25:22.037Z",
            "description": "Test description",
        },
        headers=user_headers,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    # User granted with manager role to be able to create tasks

    response = await client.patch(
        f"/api/teams/{with_user_team_id}/members/{common_user.id}/role",
        params={"role": TeamRole.MANAGER.value},
        headers=admin_headers,
    )
    assert response.status_code == status.HTTP_200_OK

    for i in range(1, 6):
        task_title = f"Task №{i}"
        response = await client.post(
            "/api/tasks",
            json={
                "team_id": with_user_team_id,
                "title": task_title,
                "deadline": "2025-05-22T15:25:22.037Z",
                "description": "Test description",
            },
            headers=user_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["data"]["author_id"] == str(common_user.id)
        assert response.json()["data"]["title"] == task_title

    # All of them appears on an personal authored task list
    response = await client.get("/api/tasks/authored", headers=user_headers)

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["count"] == 5
    assert all([value["author_id"] == str(common_user.id) for value in json["values"]])
    assert all([value["title"].startswith("Task №") for value in json["values"]])

    # User still can not create a task outside of a target team
    # ? (but would be able if user becomes member of an outer team and gets a role)

    response = await client.post(
        "/api/tasks",
        json={
            "team_id": without_user_team_id,
            "title": "User task",
            "deadline": "2025-05-22T15:25:22.037Z",
            "description": "Test description",
        },
        headers=user_headers,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    # Same with the unknown team

    response = await client.post(
        "/api/tasks",
        json={
            "team_id": UNKNOWN_UUID,
            "title": "User task",
            "deadline": "2025-05-22T15:25:22.037Z",
            "description": "Test description",
        },
        headers=user_headers,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_task_deletion(
    client: AsyncClient,
    team_with_member,
    other_team_with_owner,
    admin_user,
    manager_user,
    common_user,
    user_jwt_headers,
):
    admin_headers = await user_jwt_headers(admin_user.email)
    user_headers = await user_jwt_headers(common_user.email)

    with_user_team_id = team_with_member["id"]

    UNKNOWN_UUID = "b40c24c3-1a8f-4d67-9189-5a0b41ec5d3e"

    # Can not remove unexistent task

    response = await client.delete(f"/api/tasks/{UNKNOWN_UUID}", headers=admin_headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND

    # * Get all tasks authored by the admin and the user (from previous state there are five tasks)

    response = await client.get("/api/tasks/authored", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 5
    admin_task_ids = [value["id"] for value in response.json()["values"]]

    response = await client.get("/api/tasks/authored", headers=user_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 5
    user_task_ids = [value["id"] for value in response.json()["values"]]

    # * Remove first admin task by admin (author) with an owner role (success)

    response = await client.delete(
        f"/api/tasks/{admin_task_ids[0]}", headers=admin_headers
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # * Remove second admin task by user (stranger) with manager role (failure)

    response = await client.delete(
        f"/api/tasks/{admin_task_ids[1]}", headers=user_headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # * Remove first user task by user (author) with a manager role (success)

    response = await client.delete(
        f"/api/tasks/{user_task_ids[0]}", headers=user_headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # * Remove second user task by admin (stranger) with an owner role (success)
    response = await client.delete(
        f"/api/tasks/{user_task_ids[1]}", headers=admin_headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # * Grant user an admin team role

    response = await client.patch(
        f"/api/teams/{with_user_team_id}/members/{common_user.id}/role",
        params={"role": TeamRole.ADMIN.value},
        headers=admin_headers,
    )
    assert response.status_code == status.HTTP_200_OK

    # * Remove second admin task by user (stranger) with admin role (success)

    response = await client.delete(
        f"/api/tasks/{admin_task_ids[1]}", headers=user_headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # * Grant user an employee team role

    response = await client.patch(
        f"/api/teams/{with_user_team_id}/members/{common_user.id}/role",
        params={"role": TeamRole.EMPLOYEE.value},
        headers=admin_headers,
    )
    assert response.status_code == status.HTTP_200_OK

    # * Remove third admin task by user (stranger) with admin role (failure)

    response = await client.delete(
        f"/api/tasks/{admin_task_ids[3]}", headers=user_headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # * Remove third user task by user (author) with employee role (success!)

    response = await client.delete(
        f"/api/tasks/{user_task_ids[3]}", headers=user_headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_get_task(
    client: AsyncClient,
    team_with_member,
    admin_user,
    common_user,
    user_jwt_headers,
):
    admin_headers = await user_jwt_headers(admin_user.email)
    user_headers = await user_jwt_headers(common_user.email)

    # Create task as admin
    response = await client.post(
        "/api/tasks",
        json={
            "team_id": team_with_member["id"],
            "title": "Test Task",
            "deadline": "2025-05-22T15:25:22.037Z",
            "description": "Test description",
        },
        headers=admin_headers,
    )
    assert response.status_code == status.HTTP_201_CREATED
    task_id = response.json()["data"]["id"]

    # Admin can get the task
    response = await client.get(f"/api/tasks/{task_id}", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["id"] == task_id

    # User can't get the task (not assigned)
    response = await client.get(f"/api/tasks/{task_id}", headers=user_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Assign task to user
    response = await client.post(
        f"/api/tasks/{task_id}/assign",
        json={"assignee_id": str(common_user.id)},
        headers=admin_headers,
    )
    assert response.status_code == status.HTTP_200_OK

    # Now user can get the task
    response = await client.get(f"/api/tasks/{task_id}", headers=user_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["id"] == task_id

    # Non-existent task
    response = await client.get(
        "/api/tasks/b40c24c3-1a8f-4d67-9189-5a0b41ec5d3e",
        headers=admin_headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_update_task(
    client: AsyncClient,
    team_with_member,
    admin_user,
    common_user,
    user_jwt_headers,
):
    admin_headers = await user_jwt_headers(admin_user.email)
    user_headers = await user_jwt_headers(common_user.email)

    # Create task as admin
    response = await client.post(
        "/api/tasks",
        json={
            "team_id": team_with_member["id"],
            "title": "Test Task",
            "deadline": "2025-05-22T15:25:22.037Z",
            "description": "Test description",
        },
        headers=admin_headers,
    )
    assert response.status_code == status.HTTP_201_CREATED
    task_id = response.json()["data"]["id"]

    # Admin can update the task
    new_title = "Updated Title"
    response = await client.patch(
        f"/api/tasks/{task_id}",
        json={"title": new_title},
        headers=admin_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["title"] == new_title

    # User can't update the task (not author)
    response = await client.patch(
        f"/api/tasks/{task_id}",
        json={"title": "User Updated Title"},
        headers=user_headers,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Update user role to manager
    response = await client.patch(
        f"/api/teams/{team_with_member["id"]}/members/{common_user.id}/role",
        params={"role": TeamRole.MANAGER.value},
        headers=admin_headers,
    )
    assert response.status_code == status.HTTP_200_OK

    # Create task as user with manager role
    response = await client.post(
        "/api/tasks",
        json={
            "team_id": team_with_member["id"],
            "title": "User Task",
            "deadline": "2025-05-22T15:25:22.037Z",
            "description": "Test description",
        },
        headers=user_headers,
    )
    assert response.status_code == status.HTTP_201_CREATED
    user_task_id = response.json()["data"]["id"]

    # User can update their own task
    response = await client.patch(
        f"/api/tasks/{user_task_id}",
        json={"title": "User Updated Title"},
        headers=user_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["title"] == "User Updated Title"


@pytest.mark.asyncio
async def test_assign_task(
    client: AsyncClient,
    team_with_member,
    admin_user,
    common_user,
    another_user,
    user_jwt_headers,
):
    admin_headers = await user_jwt_headers(admin_user.email)
    user_headers = await user_jwt_headers(common_user.email)

    # Create task as admin
    response = await client.post(
        "/api/tasks",
        json={
            "team_id": team_with_member["id"],
            "title": "Test Task",
            "deadline": "2025-05-22T15:25:22.037Z",
            "description": "Test description",
        },
        headers=admin_headers,
    )
    assert response.status_code == status.HTTP_201_CREATED
    task_id = response.json()["data"]["id"]

    # Admin can assign task
    response = await client.post(
        f"/api/tasks/{task_id}/assign",
        json={"assignee_id": str(common_user.id)},
        headers=admin_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["assignee_id"] == str(common_user.id)

    # User can't assign task (no permissions)
    response = await client.post(
        f"/api/tasks/{task_id}/assign",
        json={"assignee_id": str(another_user.id)},
        headers=user_headers,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Assign to non-team member should fail
    non_member_id = "b40c24c3-1a8f-4d67-9189-5a0b41ec5d3e"
    response = await client.post(
        f"/api/tasks/{task_id}/assign",
        json={"assignee_id": non_member_id},
        headers=admin_headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_complete_task(
    client: AsyncClient,
    team_with_member,
    admin_user,
    common_user,
    user_jwt_headers,
):
    admin_headers = await user_jwt_headers(admin_user.email)
    user_headers = await user_jwt_headers(common_user.email)

    # Create task as admin
    response = await client.post(
        "/api/tasks",
        json={
            "team_id": team_with_member["id"],
            "title": "Test Task",
            "deadline": "2025-05-22T15:25:22.037Z",
            "description": "Test description",
        },
        headers=admin_headers,
    )
    assert response.status_code == status.HTTP_201_CREATED
    task_id = response.json()["data"]["id"]

    # Assign task to user
    response = await client.post(
        f"/api/tasks/{task_id}/assign",
        json={"assignee_id": str(common_user.id)},
        headers=admin_headers,
    )
    assert response.status_code == status.HTTP_200_OK

    # User can complete assigned task
    response = await client.post(
        f"/api/tasks/{task_id}/complete",
        headers=user_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["status"] == "completed"

    # Can't complete already completed task
    response = await client.post(
        f"/api/tasks/{task_id}/complete",
        headers=user_headers,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_rate_task(
    client: AsyncClient,
    team_with_member,
    admin_user,
    common_user,
    user_jwt_headers,
):
    admin_headers = await user_jwt_headers(admin_user.email)
    user_headers = await user_jwt_headers(common_user.email)

    # Create task as admin
    response = await client.post(
        "/api/tasks",
        json={
            "team_id": team_with_member["id"],
            "title": "Test Task",
            "deadline": "2025-05-22T15:25:22.037Z",
            "description": "Test description",
        },
        headers=admin_headers,
    )
    assert response.status_code == status.HTTP_201_CREATED
    task_id = response.json()["data"]["id"]

    # Assign and complete task
    await client.post(
        f"/api/tasks/{task_id}/assign",
        json={"assignee_id": str(common_user.id)},
        headers=admin_headers,
    )
    await client.post(
        f"/api/tasks/{task_id}/complete",
        headers=user_headers,
    )

    # Admin can rate completed task
    response = await client.post(
        f"/api/tasks/{task_id}/rate",
        json={"score": 5},
        headers=admin_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["score"] == 5

    # Can't rate non-completed task
    # Create another task
    response = await client.post(
        "/api/tasks",
        json={
            "team_id": team_with_member["id"],
            "title": "Test Task 2",
            "deadline": "2025-05-22T15:25:22.037Z",
            "description": "Test description",
        },
        headers=admin_headers,
    )
    task_id_2 = response.json()["data"]["id"]

    response = await client.post(
        f"/api/tasks/{task_id_2}/rate",
        json={"score": 5},
        headers=admin_headers,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_task_comments(
    client: AsyncClient,
    team_with_member,
    admin_user,
    common_user,
    user_jwt_headers,
):
    admin_headers = await user_jwt_headers(admin_user.email)
    user_headers = await user_jwt_headers(common_user.email)

    # Create task as admin
    response = await client.post(
        "/api/tasks",
        json={
            "team_id": team_with_member["id"],
            "title": "Test Task",
            "deadline": "2025-05-22T15:25:22.037Z",
            "description": "Test description",
        },
        headers=admin_headers,
    )
    assert response.status_code == status.HTTP_201_CREATED
    task_id = response.json()["data"]["id"]

    # Add comment as admin
    comment_text = "Admin comment"
    response = await client.post(
        f"/api/tasks/{task_id}/comment",
        json={"text": comment_text},
        headers=admin_headers,
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["data"]["text"] == comment_text

    # Assign task to user
    await client.post(
        f"/api/tasks/{task_id}/assign",
        json={"assignee_id": str(common_user.id)},
        headers=admin_headers,
    )

    # Add comment as user
    comment_text = "User comment"
    response = await client.post(
        f"/api/tasks/{task_id}/comment",
        json={"text": comment_text},
        headers=user_headers,
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["data"]["text"] == comment_text

    # Can't comment on non-existent task
    response = await client.post(
        "/api/tasks/b40c24c3-1a8f-4d67-9189-5a0b41ec5d3e/comment",
        json={"text": "Test"},
        headers=admin_headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
