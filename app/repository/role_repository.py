from contextlib import AbstractAsyncContextManager
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.model.role import Role
from app.repository.base_repository import BaseRepository
from app.schema.permission_schema import RolePayload


class RoleRepository(BaseRepository):
    def __init__(
        self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]
    ):
        self.session_factory = session_factory
        super().__init__(session_factory, Role)

    async def get_all_roles(self, role_type: str = None):
        async with self.session_factory() as session:
            query = select(self.model).options(joinedload(self.model.permissions))
            if role_type:
                query = query.filter_by(role_type=role_type)
            result = await session.execute(query)
            return result.scalars().all()

    async def create_role(self, payload: RolePayload):
        async with self.session_factory() as session:
            role_data = self.model(
                role_name=payload.role_name,
                role_type=payload.role_type,
            )
            session.add(role_data)
            await session.commit()
            await session.refresh(role_data)
            return role_data

    async def update_role(self, payload: RolePayload, role_uuid: str):
        async with self.session_factory() as session:
            result = await session.execute(select(self.model).filter_by(uuid=role_uuid))
            role = result.scalar_one()
            role.role_name = payload.role_name
            role.role_type = payload.role_type
            await session.commit()
            await session.refresh(role)
            return role

    async def get_role(self, role_uuid: str):
        async with self.session_factory() as session:
            try:
                result = await session.execute(
                    select(self.model)
                    .filter_by(uuid=role_uuid)
                    .options(joinedload(self.model.permissions))
                )
                return result.scalar_.one_or_none()
            except Exception as e:
                raise e
