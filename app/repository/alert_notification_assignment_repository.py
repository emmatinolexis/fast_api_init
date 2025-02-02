from contextlib import AbstractAsyncContextManager
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app.model.alert_notification_assignment import AlertNotificationAssignment
from app.repository.base_repository import BaseRepository


class AlertNotificationAssignmentRepository(BaseRepository):
    def __init__(
        self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]
    ):
        self.session_factory = session_factory
        super().__init__(session_factory, AlertNotificationAssignment)

    async def read_all_by_uuid(self, uuid):
        async with self.session_factory() as session:
            result = await session.execute(
                session.query(self.model).filter_by(alert_policy_uuid=uuid)
            )
            return result.scalars().all()

    async def read_all_by_alert_policy_uuid(self, alert_policy_uuid):
        async with self.session_factory() as session:
            result = await session.execute(
                session.query(self.model).filter_by(alert_policy_uuid=alert_policy_uuid)
            )
            return result.scalars().all()

    async def delete_by_recipient(self, alert_policy_uuid, recipient):
        async with self.session_factory() as session:
            await session.execute(
                session.query(self.model)
                .filter_by(alert_policy_uuid=alert_policy_uuid, recipient=recipient)
                .delete()
            )
            await session.commit()
            return True

    async def delete_recipient_by_policy_uuid(self, alert_policy_uuid):
        async with self.session_factory() as session:
            await session.execute(
                session.query(self.model)
                .filter_by(alert_policy_uuid=alert_policy_uuid)
                .delete()
            )
            await session.commit()
            return True
