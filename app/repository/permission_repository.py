from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session
from app.util.enums import PermissionType

from app.model.permission import Permission
from app.repository.base_repository import BaseRepository


class PermissionRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, Permission)

    def get_list(self):
        with self.session_factory() as session:
            return session.query(Permission).all()

    def get_all_permissions(self, permission_type: str = None):
        with self.session_factory() as session:
            # Get all permissions
            permissions = session.query(self.model).all()

            # If permission_type is specified and is either admin or customer
            if permission_type == PermissionType.admin:
                # Filter permissions for admin, allowing 'all' permission type
                filtered_permissions = [
                    perm for perm in permissions
                    if perm.permission_type == PermissionType.admin or perm.permission_type == PermissionType.all
                ]
                return filtered_permissions

            if permission_type == PermissionType.customer:
                # Filter permissions for customer, allowing 'all' permission type
                filtered_permissions = [
                    perm for perm in permissions
                    if perm.permission_type == PermissionType.customer or perm.permission_type == PermissionType.all
                ]
                return filtered_permissions

            # If permission_type is None or unrecognized, return all permissions
            return permissions

    def create(self, permission: Permission) -> Permission:
        with self.session_factory() as session:
            session.add(permission)
            session.commit()
            session.refresh(permission)
            return permission
