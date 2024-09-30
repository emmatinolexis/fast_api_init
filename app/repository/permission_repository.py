from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.model.permission import Permission
from app.repository.base_repository import BaseRepository


class PermissionRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, Permission)

    def get_list(self):
        with self.session_factory() as session:
            return session.query(Permission).all()

    def create(self, permission: Permission) -> Permission:
        with self.session_factory() as session:
            session.add(permission)
            session.commit()
            session.refresh(permission)
            return permission
