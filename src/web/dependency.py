from fastapi import Depends
from src.db.dependency import get_db_session

from src.domain.users import UserRepository
from src.domain.teams import TeamRepository
from src.domain.tasks import TaskRepository
from src.domain.meetings import MeetingRepository

from src.db.repositories.user import SQLAUserRepository
from src.db.repositories.team import SQLATeamRepository
from src.db.repositories.task import SQLATaskRepository
from src.db.repositories.meeting import SQLAMeetingRepository

from src.services.users.grant_role import GrantRoleUseCase
from src.services.users.delete_me import DeleteMeUseCase

from src.services.teams.create_team import CreateTeamUseCase
from src.services.teams.get_team import GetTeamUseCase
from src.services.teams.list_teams import ListTeamsUseCase
from src.services.teams.get_members import GetMembersUseCase
from src.services.teams.get_member import GetMemberUseCase
from src.services.teams.add_member import AddMemberUseCase
from src.services.teams.grant_member_role import GrantMemberRoleUseCase
from src.services.teams.remove_member import RemoveMemberUseCase
from src.services.teams.create_invite import CreateInviteUseCase
from src.services.teams.accept_invite import AcceptInviteUseCase
from src.services.teams.remove_invite import RemoveInviteUseCase
from src.services.teams.rename_team import RenameTeamUseCase

from src.services.tasks.add_comment import AddCommentUseCase
from src.services.tasks.assign_to_task import AssignToTaskUseCase
from src.services.tasks.complete_task import CompleteTaskUseCase
from src.services.tasks.create_task import CreateTaskUseCase
from src.services.tasks.delete_task import DeleteTaskUseCase
from src.services.tasks.get_task import GetTaskUseCase
from src.services.tasks.list_tasks import ListTasksUseCase
from src.services.tasks.rate_task import RateTaskUseCase
from src.services.tasks.update_task import UpdateTaskUseCase

from src.services.meetings.create_meeting import CreateMeetingUseCase
from src.services.meetings.get_meeting import GetMeetingUseCase
from src.services.meetings.cancel_meeting import CancelMeetingUseCase
from src.services.meetings.list_meetings import ListMeetingsUseCase

from src.services.calendar.view import CalendarViewUseCase


def get_user_repo(session=Depends(get_db_session)) -> UserRepository:
    return SQLAUserRepository(session)


def get_team_repo(session=Depends(get_db_session)) -> TeamRepository:
    return SQLATeamRepository(session)


def get_task_repo(session=Depends(get_db_session)) -> TaskRepository:
    return SQLATaskRepository(session)


def get_meeting_repo(session=Depends(get_db_session)) -> MeetingRepository:
    return SQLAMeetingRepository(session)


def get_grant_role_use_case(
    repo: UserRepository = Depends(get_user_repo),
) -> GrantRoleUseCase:
    return GrantRoleUseCase(repo)


def get_delete_me_use_case(
    repo: UserRepository = Depends(get_user_repo),
) -> DeleteMeUseCase:
    return DeleteMeUseCase(repo)


def get_create_team_use_case(
    repo: TeamRepository = Depends(get_team_repo),
) -> CreateTeamUseCase:
    return CreateTeamUseCase(repo)


def get_get_teams_use_case(
    repo: TeamRepository = Depends(get_team_repo),
) -> ListTeamsUseCase:
    return ListTeamsUseCase(repo)


def get_get_member_use_case(
    repo: TeamRepository = Depends(get_team_repo),
):
    return GetMemberUseCase(repo)


def get_get_team_use_case(
    repo: TeamRepository = Depends(get_team_repo),
    get_member: GetMemberUseCase = Depends(get_get_member_use_case),
) -> GetTeamUseCase:
    return GetTeamUseCase(repo, get_member)


def get_get_members_use_case(
    repo: TeamRepository = Depends(get_team_repo),
):
    return GetMembersUseCase(repo)


def get_grant_member_role_use_case(
    repo: TeamRepository = Depends(get_team_repo),
    get_member: GetMemberUseCase = Depends(get_get_member_use_case),
):
    return GrantMemberRoleUseCase(repo, get_member)


def get_add_member_use_case(
    repo: TeamRepository = Depends(get_team_repo),
    get_member: GetMemberUseCase = Depends(get_get_member_use_case),
):
    return AddMemberUseCase(repo, get_member)


def get_remove_member_use_case(
    repo: TeamRepository = Depends(get_team_repo),
    get_member: GetMemberUseCase = Depends(get_get_member_use_case),
):
    return RemoveMemberUseCase(repo, get_member)


def get_create_invite_use_case(
    repo: TeamRepository = Depends(get_team_repo),
    get_member: GetMemberUseCase = Depends(get_get_member_use_case),
):
    return CreateInviteUseCase(repo, get_member)


def get_accept_invite_use_case(
    repo: TeamRepository = Depends(get_team_repo),
    get_member: GetMemberUseCase = Depends(get_get_member_use_case),
):
    return AcceptInviteUseCase(repo, get_member)


def get_remove_invite_use_case(
    repo: TeamRepository = Depends(get_team_repo),
    get_member: GetMemberUseCase = Depends(get_get_member_use_case),
):
    return RemoveInviteUseCase(repo, get_member)


def get_rename_team_use_case(
    repo: TeamRepository = Depends(get_team_repo),
    get_team: GetTeamUseCase = Depends(get_get_team_use_case),
):
    return RenameTeamUseCase(repo, get_team)


def get_create_task_use_case(
    repo: TaskRepository = Depends(get_task_repo),
    get_member: GetMemberUseCase = Depends(get_get_member_use_case),
):
    return CreateTaskUseCase(repo, get_member)


def get_get_task_use_case(
    repo: TaskRepository = Depends(get_task_repo),
    get_member: GetMemberUseCase = Depends(get_get_member_use_case),
):
    return GetTaskUseCase(repo, get_member)


def get_list_tasks_use_case(
    repo: TaskRepository = Depends(get_task_repo),
):
    return ListTasksUseCase(repo)


def get_update_task_use_case(
    repo: TaskRepository = Depends(get_task_repo),
    get_task: GetTaskUseCase = Depends(get_get_task_use_case),
):
    return UpdateTaskUseCase(repo, get_task)


def get_delete_task_use_case(
    repo: TaskRepository = Depends(get_task_repo),
    get_task: GetTaskUseCase = Depends(get_get_task_use_case),
):
    return DeleteTaskUseCase(repo, get_task)


def get_assign_to_task_use_case(
    repo: TaskRepository = Depends(get_task_repo),
    get_task: GetTaskUseCase = Depends(get_get_task_use_case),
    get_member: GetMemberUseCase = Depends(get_get_member_use_case),
):
    return AssignToTaskUseCase(repo, get_task, get_member)


def get_complete_task_use_case(
    repo: TaskRepository = Depends(get_task_repo),
    get_task: GetTaskUseCase = Depends(get_get_task_use_case),
):
    return CompleteTaskUseCase(repo, get_task)


def get_rate_task_use_case(
    repo: TaskRepository = Depends(get_task_repo),
    get_task: GetTaskUseCase = Depends(get_get_task_use_case),
):
    return RateTaskUseCase(repo, get_task)


def get_add_comment_use_case(
    repo: TaskRepository = Depends(get_task_repo),
    get_task: GetTaskUseCase = Depends(get_get_task_use_case),
):
    return AddCommentUseCase(repo, get_task)


def get_create_meeting_use_case(
    repo: MeetingRepository = Depends(get_meeting_repo),
    get_member: GetMemberUseCase = Depends(get_get_member_use_case),
):
    return CreateMeetingUseCase(repo, get_member)


def get_get_meeting_use_case(
    repo: MeetingRepository = Depends(get_meeting_repo),
    get_member: GetMemberUseCase = Depends(get_get_member_use_case),
):
    return GetMeetingUseCase(repo, get_member)


def get_cancel_meeting_use_case(
    repo: MeetingRepository = Depends(get_meeting_repo),
    get_member: GetMemberUseCase = Depends(get_get_member_use_case),
    get_meeting: GetMeetingUseCase = Depends(get_get_meeting_use_case),
):
    return CancelMeetingUseCase(repo, get_member, get_meeting)


def get_list_meetings_use_case(
    repo: MeetingRepository = Depends(get_meeting_repo),
):
    return ListMeetingsUseCase(repo)


def get_calendar_view_use_case(
    list_tasks: ListTasksUseCase = Depends(get_list_tasks_use_case),
    list_meetings: ListMeetingsUseCase = Depends(get_list_meetings_use_case),
):
    return CalendarViewUseCase(
        list_tasks_use_case=list_tasks, list_meetings_use_case=list_meetings
    )
