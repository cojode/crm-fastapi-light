from src.db.models.team import (
    Team as TeamDB,
    TeamMember as TeamMemberDB,
    TeamInvite as TeamInviteDB,
)
from src.domain.teams import (
    Team,
    TeamMember,
    TeamInvite,
    TeamRepository,
)
from src.domain.users import User
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import RepositoryError

from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload, joinedload


class SQLATeamRepositoryError(RepositoryError): ...


class SaveTeamNotFound(SQLATeamRepositoryError): ...


class SaveTeamMemberNotFound(SQLATeamRepositoryError): ...


class SaveTeamInviteNotFound(SQLATeamRepositoryError): ...


import datetime


class SQLATeamRepository(TeamRepository):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @staticmethod
    def _team_from_object(db_team: TeamDB) -> Team:
        """Shortcut method with provided conversions."""
        return Team.from_object(
            db_team,
            [
                ("members", TeamMember),
                ("invites", TeamInvite),
            ],
            members=[
                ("user", User),
            ],
            invites=[
                ("creator", User),
            ],
        )

    async def get_team(self, team_id: UUID) -> Team | None:
        stmt = (
            select(TeamDB)
            .where(TeamDB.id == team_id)
            .options(
                selectinload(TeamDB.members).joinedload(TeamMemberDB.user),
                selectinload(TeamDB.invites).joinedload(TeamInviteDB.creator),
            )
        )
        result = await self.session.execute(stmt)

        db_team = result.scalars().first()

        return self._team_from_object(db_team) if db_team else None

    async def list_teams(self, member_id: UUID | None = None) -> list[Team]:
        stmt = select(TeamDB)
        if member_id:
            stmt = stmt.join(
                TeamMemberDB, TeamDB.id == TeamMemberDB.team_id
            ).where(TeamMemberDB.user_id == member_id)
        result = await self.session.execute(stmt)
        db_teams = result.scalars().unique().all()
        return [self._team_from_object(db_team) for db_team in db_teams]

    async def save_team(self, team: Team) -> Team:
        return Team.from_object(
            await self.session.merge(
                TeamDB.from_dataclass(
                    team, ignore_fields=["members", "invites"]
                )
            )
        )

    async def list_members(self, team_id: UUID) -> list[TeamMember]:
        result = await self.session.execute(
            select(TeamMemberDB).where(TeamMemberDB.team_id == team_id)
        )
        db_members = result.scalars().all()
        return [TeamMember.from_object(db_member) for db_member in db_members]

    async def get_member(
        self, team_id: UUID, user_id: UUID
    ) -> TeamMember | None:
        stmt = (
            select(TeamMemberDB)
            .where(
                (TeamMemberDB.team_id == team_id)
                & (TeamMemberDB.user_id == user_id)
            )
            .options(joinedload(TeamMemberDB.user))
        )
        result = await self.session.execute(stmt)
        db_member = result.scalars().first()

        return (
            TeamMember.from_object(db_member, [("user", User)])
            if db_member
            else None
        )

    async def save_member(self, member: TeamMember) -> TeamMember:
        return TeamMember.from_object(
            await self.session.merge(
                TeamMemberDB.from_dataclass(member, ignore_fields=["user"])
            ),
            [("user", User)],
        )

    async def delete_member(self, member: TeamMember) -> None:
        await self.session.execute(
            delete(TeamMemberDB)
            .where(TeamMemberDB.team_id == member.team_id)
            .where(TeamMemberDB.user_id == member.user_id)
        )

        await self.session.flush()

    async def get_invite(
        self,
        code: UUID,
        expires_at: datetime.datetime | None = None,
        is_used_up: bool | None = None,
    ) -> TeamInvite | None:
        stmt = select(TeamInviteDB).where(TeamInviteDB.code == code)
        if expires_at is not None:
            stmt = stmt.where(TeamInviteDB.expires_at < expires_at)
        if is_used_up is not None:
            stmt = stmt.where(TeamInviteDB.max_uses < TeamInviteDB.used_count)

        result = await self.session.execute(stmt)
        db_invite = result.scalars().one_or_none()
        return TeamInvite.from_object(db_invite) if db_invite else None

    async def save_invite(self, invite: TeamInvite) -> TeamInvite:
        return TeamInvite.from_object(
            await self.session.merge(
                TeamInviteDB.from_dataclass(invite, ignore_fields=["creator"])
            ),
            [("creator", User)],
        )

    async def delete_invite(self, code: UUID) -> None:
        await self.session.execute(
            delete(TeamInviteDB).where(TeamInviteDB.code == code)
        )

        await self.session.flush()
