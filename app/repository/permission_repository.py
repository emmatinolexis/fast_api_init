from contextlib import AbstractAsyncContextManager
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.model.permission import Permission
from app.repository.base_repository import BaseRepository
from app.util.enums import PermissionType


class PermissionRepository(BaseRepository):
    def __init__(
        self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]
    ):
        self.session_factory = session_factory
        super().__init__(session_factory, Permission)

    async def get_list(self):
        async with self.session_factory() as session:
            result = await session.execute(select(Permission))
            return result.scalars().all()

    async def get_all_permissions(self, permission_type: str = None):
        async with self.session_factory() as session:
            # Get all permissions
            result = await session.execute(select(self.model))
            permissions = result.scalars().all()

            # If permission_type is specified and is either admin or customer
            if permission_type == PermissionType.admin:
                # Filter permissions for admin, allowing 'all' permission type
                filtered_permissions = [
                    perm
                    for perm in permissions
                    if perm.permission_type == PermissionType.admin
                    or perm.permission_type == PermissionType.all
                ]
                return filtered_permissions

            if permission_type == PermissionType.customer:
                # Filter permissions for customer, allowing 'all' permission type
                filtered_permissions = [
                    perm
                    for perm in permissions
                    if perm.permission_type == PermissionType.customer
                    or perm.permission_type == PermissionType.all
                ]
                return filtered_permissions

            # If permission_type is None or unrecognized, return all permissions
            return permissions

    async def create(self, permission: Permission) -> Permission:
        async with self.session_factory() as session:
            session.add(permission)
            await session.commit()
            await session.refresh(permission)
            return permission
