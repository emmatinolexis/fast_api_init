from datetime import datetime
from typing import Callable, List, Optional
from uuid import UUID

from pydantic import EmailStr
from sqlalchemy import and_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.model.invitation import Invitation
from app.repository.base_repository import BaseRepository
from app.schema.invitation_schema import InvitationPayload
from app.util.enums import InvitationStatus, RoleType
from sqlalchemy.future import select


class TeamMemberInvitationRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AsyncSession]):
        self.session_factory = session_factory
        super().__init__(session_factory, Invitation)

    async def create_invitation(self, payload: InvitationPayload):
        return await self.create(payload)

    async def get_invitation_by_email(self, email: EmailStr) -> Optional[Invitation]:
        """Asynchronously retrieves an invitation by email."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(self.model).filter(self.model.email == email)
            )
            return result.scalars().first()

    async def get_user_invitations(
        self,
        business_uuid: str,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        role_uuids: Optional[List[str]] = None,
        status: Optional[InvitationStatus] = None,
    ):
        """Fetch user invitations with pagination and filtering asynchronously."""
        async with self.session_factory() as session:
            # Start building the query
            query = select(self.model).filter(
                self.model.business_profile_uuid == business_uuid
            )

            # Apply filters
            if search:
                query = query.filter(self.model.email.ilike(f"%{search}%"))
            if role_uuids:
                valid_role_uuids = [
                    UUID(role_uuid) for role_uuid in role_uuids if role_uuid
                ]
                if valid_role_uuids:
                    query = query.filter(self.model.role_uuid.in_(valid_role_uuids))
            if status:
                query = query.filter(self.model.status == status)

            # Get total count for pagination
            total_invitations = await session.scalar(
                select(func.count()).select_from(query.subquery())
            )
            total_pages = (total_invitations + page_size - 1) // page_size
            offset = (page - 1) * page_size

            # Fetch invitations with pagination and eager loading
            result = await session.execute(
                query.order_by(desc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
                .options(joinedload(self.model.role))
            )
            invitations = result.unique().scalars().all()

            invitations_data = [
                {
                    "uuid": invitation.uuid,
                    "email": invitation.email,
                    "role": invitation.role,
                    "status": invitation.status,
                    "created_at": invitation.created_at,
                }
                for invitation in invitations
            ]

            return {
                "invitations": invitations_data,
                "total_invitations": total_invitations,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": page_size,
            }

    async def get_admin_invitations(
        self,
        page=1,
        page_size=10,
        email: str = None,
        role_uuids: list[str] = None,
        status=None,
    ):
        async with self.session_factory() as session:
            offset = (page - 1) * page_size

            # Build the query for invitations with optional filters
            query = session.query(self.model).filter(
                self.model.invitation_type == RoleType.ADMIN
            )

            # Add filters based on provided parameters
            if email:
                query = query.filter(self.model.email.ilike(f"%{email}%"))

            if status:
                query = query.filter(self.model.status == InvitationStatus(status))

            if role_uuids:
                valid_role_uuids = []
                for role_uuid in role_uuids:
                    try:
                        valid_role_uuids.append(UUID(role_uuid))
                    except ValueError:
                        # Skip invalid UUIDs
                        continue
                if valid_role_uuids:
                    query = query.filter(self.model.role_uuid.in_(valid_role_uuids))

            # Query to get the total count of invitations with filters
            total_invitations = await query.with_entities(
                func.count(self.model.id)
            ).scalar()

            # Calculate total pages
            total_pages = (total_invitations + page_size - 1) // page_size

            # Get the invitations with filters, pagination, and sorting
            result = await session.execute(
                query.order_by(desc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
                .options(joinedload(self.model.role))
            )
            invitations = result.unique().scalars().all()

            # Prepare the invitation data
            invitations_data = [
                {
                    "uuid": invitation.uuid,
                    "email": invitation.email,
                    "role": invitation.role,
                    "status": invitation.status,
                    "created_at": invitation.created_at,
                }
                for invitation in invitations
            ]

            return {
                "invitations": invitations_data,
                "total_invitations": total_invitations,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": page_size,
            }

    async def update_expired_invitations(self):
        """Asynchronously updates expired invitations to EXPIRED status."""
        async with self.session_factory() as session:
            # Get the current timestamp
            current_time = datetime.utcnow()

            # Query to find all expired invitations
            result = await session.execute(
                select(self.model).filter(
                    and_(
                        self.model.expired_at < current_time,
                        self.model.status == InvitationStatus.PENDING,
                    )
                )
            )
            expired_invitations = result.scalars().all()

            # Update the status of each expired invitation
            for invitation in expired_invitations:
                invitation.status = InvitationStatus.EXPIRED

            # Commit changes to the database
            await session.commit()

            return len(expired_invitations)
