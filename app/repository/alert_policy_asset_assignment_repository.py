from contextlib import AbstractAsyncContextManager
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.model.alert_policy_asset_assignment import AlertPolicyAssetAssignment
from app.model.asset import Asset
from app.repository.base_repository import BaseRepository


class AlertPolicyAssetAssignmentRepository(BaseRepository):
    def __init__(
        self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]
    ):
        self.session_factory = session_factory
        super().__init__(session_factory, AlertPolicyAssetAssignment)

    async def read_all_by_uuid(self, uuid):
        async with self.session_factory() as session:
            result = await session.execute(
                select(Asset)
                .join(self.model, Asset.uuid == self.model.asset_uuid)
                .filter(self.model.alert_policy_uuid == uuid)
            )
            return result.scalars().all()

    async def read_all_by_alert_policy_uuid(self, alert_policy_uuid):
        async with self.session_factory() as session:
            result = await session.execute(
                select(Asset)
                .join(self.model, Asset.uuid == self.model.asset_uuid)
                .filter(self.model.alert_policy_uuid == alert_policy_uuid)
            )
            return result.scalars().all()

    async def delete_by_asset(self, alert_policy_uuid, asset_uuid):
        async with self.session_factory() as session:
            await session.execute(
                self.model.__table__.delete().where(
                    self.model.alert_policy_uuid == alert_policy_uuid,
                    self.model.asset_uuid == asset_uuid,
                )
            )
            await session.commit()
            return True
