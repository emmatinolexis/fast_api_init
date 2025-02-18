from typing import Callable

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.model.alert_polcy_notification_type_assignment import (
    AlertPolicyNotificationTypeAssignment,
)
from app.repository.base_repository import BaseRepository


class AlertPolicyNotificationTypeAssignmentRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AsyncSession]):
        self.session_factory = session_factory
        super().__init__(session_factory, AlertPolicyNotificationTypeAssignment)

    async def read_all_by_uuid(self, uuid):
        async with self.session_factory() as session:
            result = await session.execute(
                select(self.model).filter_by(alert_policy_uuid=uuid)
            )
            return result.scalars().all()

    async def read_all_by_alert_policy_uuid(self, alert_policy_uuid):
        async with self.session_factory() as session:
            result = await session.execute(
                select(self.model).filter_by(alert_policy_uuid=alert_policy_uuid)
            )
            return result.scalars().all()

    async def delete_by_notification_type(
        self, alert_policy_uuid, alert_notification_type
    ):
        async with self.session_factory() as session:
            await session.execute(
                delete(self.model).filter_by(
                    alert_policy_uuid=alert_policy_uuid,
                    alert_notification_type=alert_notification_type,
                )
            )
            await session.commit()
            return True

    async def delete_by_notification_type_by_policy_uuid(self, alert_policy_uuid):
        async with self.session_factory() as session:
            await session.execute(
                delete(self.model).filter_by(alert_policy_uuid=alert_policy_uuid)
            )
            await session.commit()
            return True
