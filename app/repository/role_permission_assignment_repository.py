from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.model.role_permission_assignment import RolePermissionAssignment
from app.repository.base_repository import BaseRepository


class RolePermissionAssignmentRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, RolePermissionAssignment)

    def create_role_permission(self, payload: dict):
        with self.session_factory() as session:
            data = self.model(
                role_uuid=payload.get("role_uuid"),
                permission_uuid=payload.get("permission_uuid"),
            )
            session.add(data)
            session.commit()
            session.refresh(data)
            return data

    def delete_role_permission(self, role_uuid):
        with self.session_factory() as session:
            try:
                (session.query(self.model).filter_by(role_uuid=role_uuid).delete())
                session.commit()
                return True
            except Exception as e:
                raise e
