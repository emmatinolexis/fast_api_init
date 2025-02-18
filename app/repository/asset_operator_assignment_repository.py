from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app.model.asset_operator_assignment import AssetOperatorAssignment
from app.repository.base_repository import BaseRepository


class AssetOperatorTypeAssignmentRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AsyncSession]):
        self.session_factory = session_factory
        super().__init__(session_factory, AssetOperatorAssignment)

    async def get_assignment_by_operator_uuid(
        self, operator_uuid: str
    ) -> AssetOperatorAssignment:
        async with self.session_factory() as session:
            result = await session.execute(
                session.query(AssetOperatorAssignment).filter_by(
                    operator_uuid=operator_uuid
                )
            )
            return result.scalars().first()

    async def get_assignment_by_asset_uuid(
        self, asset_uuid: str
    ) -> AssetOperatorAssignment:
        async with self.session_factory() as session:
            result = await session.execute(
                session.query(AssetOperatorAssignment).filter_by(asset_uuid=asset_uuid)
            )
            return result.scalars().first()
