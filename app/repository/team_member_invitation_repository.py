from contextlib import AbstractContextManager
from typing import Callable

from pydantic import EmailStr
from sqlalchemy.orm import Session, joinedload

from app.model.invitation import Invitation
from app.repository.base_repository import BaseRepository
from app.schema.invitation_schema import InvitationPayload


class TeamMemberInvitationRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, Invitation)

    def create_invitation(self, payload: InvitationPayload):
        return self.create(payload)

    def get_invitation_by_email(self, email: EmailStr) -> Invitation:
        with self.session_factory() as session:
            return session.query(self.model).filter(self.model.email == email).first()

    def get_user_invitations(self, business_uuid: str):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter(self.model.business_profile_uuid == business_uuid)
                .options(joinedload(self.model.role))
                .all()
            )
