from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session, joinedload

from app.model.role import Role
from app.repository.base_repository import BaseRepository
from app.schema.permission_schema import RolePayload


class RoleRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, Role)

    def get_all_roles(self):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .options(joinedload(self.model.permissions))
                .all()
            )

    def create_role(self, payload: RolePayload):
        with self.session_factory() as session:
            role_data = self.model(
                role_name=payload.role_name,
                role_type=payload.role_type,
            )
            session.add(role_data)
            session.commit()
            session.refresh(role_data)
            return role_data

    def update_role(self, payload: RolePayload, role_uuid: str):
        with self.session_factory() as session:
            role = session.query(self.model).filter_by(uuid=role_uuid).first()
            role.role_name = payload.role_name
            role.role_type = payload.role_type
            session.commit()
            session.refresh(role)
            return role

    def get_role(self, role_uuid: str):
        with self.session_factory() as session:
            try:
                role = (
                    session.query(self.model)
                    .filter_by(uuid=role_uuid)
                    .options(joinedload(self.model.permissions))
                    .first()
                )
                return role
            except Exception as e:
                raise e
