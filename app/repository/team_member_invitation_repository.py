from contextlib import AbstractContextManager
from typing import Callable

from pydantic import EmailStr
from sqlalchemy import desc, func
from sqlalchemy.orm import Session, joinedload

from app.model.invitation import Invitation
from app.repository.base_repository import BaseRepository
from app.schema.invitation_schema import InvitationPayload
from app.util.enums import RoleType


class TeamMemberInvitationRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, Invitation)

    def create_invitation(self, payload: InvitationPayload):
        return self.create(payload)

    def get_invitation_by_email(self, email: EmailStr) -> Invitation:
        with self.session_factory() as session:
            return session.query(self.model).filter(self.model.email == email).first()

    def get_user_invitations(self, business_uuid: str, page=1, page_size=10):
        with self.session_factory() as session:
            offset = (page - 1) * page_size

            # Query to get the total count of invitations
            total_invitations = (
                session.query(func.count(self.model.id))
                .filter(self.model.business_profile_uuid == business_uuid)
                .scalar()
            )

            # Calculate total pages
            total_pages = (total_invitations + page_size - 1) // page_size

            invitations = (
                session.query(self.model)
                .filter(self.model.business_profile_uuid == business_uuid)
                .order_by(desc(self.model.created_at))
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

    def get_admin_invitations(self, page=1, page_size=10, email: str = None, role_uuid: str = None):
        with self.session_factory() as session:
            offset = (page - 1) * page_size

            # Build the query for invitations with optional filters
            query = session.query(self.model).filter(self.model.invitation_type == RoleType.ADMIN)

            # Add filters based on provided parameters
            if email:
                query = query.filter(self.model.email.ilike(f"%{email}%"))
            if role_uuid:
                query = query.filter(self.model.role_uuid == role_uuid)

            # Query to get the total count of invitations with filters
            total_invitations = query.with_entities(func.count(self.model.id)).scalar()

            # Calculate total pages
            total_pages = (total_invitations + page_size - 1) // page_size

            # Get the invitations with filters, pagination, and sorting
            invitations = (
                query
                .order_by(desc(self.model.created_at))
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

