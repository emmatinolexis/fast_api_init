from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.model.role_permission_assignment import RolePermissionAssignment
from app.repository.base_repository import BaseRepository


class RolePermissionAssignmentRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AsyncSession]):
        self.session_factory = session_factory
        super().__init__(session_factory, RolePermissionAssignment)

    async def create_role_permission(self, payload: dict):
        async with self.session_factory() as session:
            data = self.model(
                role_uuid=payload.get("role_uuid"),
                permission_uuid=payload.get("permission_uuid"),
            )
            session.add(data)
            await session.commit()
            await session.refresh(data)
            return data

    async def delete_role_permission(self, role_uuid):
        async with self.session_factory() as session:
            try:
                result = await session.execute(
                    select(self.model).filter_by(role_uuid=role_uuid)
                )
                role_permission = result.scalars().first()
                if role_permission:
                    await session.delete(role_permission)
                    await session.commit()
                    return True
                return False
            except Exception as e:
                raise e
