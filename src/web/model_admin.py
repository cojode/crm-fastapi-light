from sqladmin import ModelView

from src.db.models.user import User
from src.db.models.team import Team, TeamInvite, TeamMember
from src.db.models.task import Task, TaskComment
from src.db.models.meeting import Meeting, MeetingParticipant


class UserAdmin(ModelView, model=User):
    column_list = [
        User.id,
        User.email,
        User.first_name,
        User.last_name,
        User.role,
        User.created_at,
    ]


class TeamAdmin(ModelView, model=Team):
    column_list = [
        Team.id,
        Team.name,
        Team.created_at,
        Team.members,
    ]


class TeamInviteAdmin(ModelView, model=TeamInvite):
    column_list = [
        TeamInvite.code,
        TeamInvite.creator_id,
        TeamInvite.expires_at,
        TeamInvite.max_uses,
        TeamInvite.used_count,
    ]


class TeamMemberAdmin(ModelView, model=TeamMember):
    column_list = [
        TeamMember.team_id,
        TeamMember.user_id,
        TeamMember.joined_at,
        TeamMember.role,
    ]


class TaskAdmin(ModelView, model=Task):
    column_list = [
        Task.id,
        Task.title,
        Task.description,
        Task.status,
        Task.created_at,
    ]


class TaskCommentAdmin(ModelView, model=TaskComment):
    column_list = [
        TaskComment.id,
        TaskComment.task,
        TaskComment.author,
        TaskComment.text,
        TaskComment.created_at,
    ]


class MeetingAdmin(ModelView, model=Meeting):
    column_list = [
        Meeting.id,
        Meeting.title,
        Meeting.organizer_id,
        Meeting.start_time,
        Meeting.duration,
        Meeting.participants,
        Meeting.cancelled,
    ]


class MeetingParticipantAdmin(ModelView, model=MeetingParticipant):
    column_list = [
        MeetingParticipant.meeting_id,
        MeetingParticipant.meeting,
        MeetingParticipant.participant_id,
        MeetingParticipant.participant,
    ]


admin_view_list = [
    UserAdmin,
    TeamAdmin,
    TeamInviteAdmin,
    TeamMemberAdmin,
    TaskAdmin,
    TaskCommentAdmin,
    MeetingAdmin,
    MeetingParticipantAdmin,
]
