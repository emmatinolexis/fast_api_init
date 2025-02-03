from contextlib import AbstractAsyncContextManager
from typing import Callable

from sqlalchemy import asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.model.asset_type import AssetType
from app.repository.base_repository import BaseRepository
from app.util.enums import ActiveStatus


class AssetTypeRepository(BaseRepository):
    def __init__(
        self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]
    ):
        self.session_factory = session_factory
        super().__init__(session_factory, AssetType)

    async def get_asset_types(self, status: str = None):
        async with self.session_factory() as session:
            query = select(self.model)

            if status:
                query = query.where(self.model.status == ActiveStatus(status))

            # Order by created_at in descending order
            query = query.order_by(asc(self.model.created_at))

            result = await session.execute(query)
            asset_types = result.scalars().all()
            return asset_types
