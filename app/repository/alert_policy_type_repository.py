from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.model.alert_policy_type import AlertPolicyType
from app.repository.base_repository import BaseRepository


class AlertPolicyTypeRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AsyncSession]):
        self.session_factory = session_factory
        super().__init__(session_factory, AlertPolicyType)

    async def delete_alert_policy_type_by_alert_uuid(self, alert_uuid: str):
        async with self.session_factory() as session:
            try:
                result = await session.execute(
                    select(self.model).filter_by(alert_uuid=alert_uuid)
                )
                alert_types = result.scalars().all()
                for alert_type in alert_types:
                    await session.delete(alert_type)
                await session.commit()
                return len(alert_types)
            except Exception as e:
                await session.rollback()
                raise e
