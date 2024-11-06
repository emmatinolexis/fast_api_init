from contextlib import AbstractContextManager
from typing import Callable, List
from uuid import UUID

from pydantic import EmailStr
from sqlalchemy import desc, func
from sqlalchemy.orm import Session, joinedload

from app.model.invitation import Invitation
from app.repository.base_repository import BaseRepository
from app.schema.invitation_schema import InvitationPayload
from app.util.enums import InvitationStatus, RoleType


class TeamMemberInvitationRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, Invitation)

    def create_invitation(self, payload: InvitationPayload):
        return self.create(payload)

    def get_invitation_by_email(self, email: EmailStr) -> Invitation:
        with self.session_factory() as session:
            return session.query(self.model).filter(self.model.email == email).first()

    def get_user_invitations(
        self,
        business_uuid: str,
        page: int = 1,
        page_size: int = 10,
        search: str = None,
        role_uuids: List[str] = None,
        status: InvitationStatus = None,
    ):
        with self.session_factory() as session:
            query = session.query(self.model).filter(
                self.model.business_profile_uuid == business_uuid
            )

            # Apply filters
            if search:
                query = query.filter(self.model.email.ilike(f"%{search}%"))
            if role_uuids:
                valid_role_uuids = []
                for role_uuid in role_uuids:
                    try:
                        valid_role_uuids.append(UUID(role_uuid))
                    except ValueError:
                        continue
                query = query.filter(self.model.role_uuid.in_(valid_role_uuids))
            if status:
                query = query.filter(self.model.status == status)

            # Get total count and calculate pagination
            total_invitations = query.count()
            total_pages = (total_invitations + page_size - 1) // page_size
            offset = (page - 1) * page_size

            # Fetch invitations with pagination and eager loading
            invitations = (
                query.order_by(desc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
                .options(joinedload(self.model.role))
                .all()
            )

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

    def get_admin_invitations(
        self,
        page=1,
        page_size=10,
        email: str = None,
        role_uuids: list[str] = None,
        status=None,
    ):
        with self.session_factory() as session:
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
            total_invitations = query.with_entities(func.count(self.model.id)).scalar()

            # Calculate total pages
            total_pages = (total_invitations + page_size - 1) // page_size

            # Get the invitations with filters, pagination, and sorting
            invitations = (
                query.order_by(desc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
                .options(joinedload(self.model.role))
                .all()
            )

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
