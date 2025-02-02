from contextlib import AbstractAsyncContextManager
from typing import Callable, List

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.model.admin_notification import AdminNotifications
from app.repository.base_repository import BaseRepository


class AdminNotificationRepository(BaseRepository):
    def __init__(
        self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]
    ):
        self.session_factory = session_factory
        super().__init__(session_factory, AdminNotifications)

    async def get_admin_notifications(
        self,
        user_uuid: str,
        notification_types: List[str],
        is_super_admin: bool = False,
    ) -> List[AdminNotifications]:
        async with self.session_factory() as session:
            query = select(AdminNotifications)

            # Apply filters based on role
            if not is_super_admin:
                query = query.where(AdminNotifications.user_id == user_uuid)

            query = query.where(
                AdminNotifications.notification_type.in_(notification_types)
            )
            query = query.order_by(
                AdminNotifications.is_read.asc(),  # Unread first
                AdminNotifications.created_at.desc(),  # Newest first
            )

            result = await session.execute(query)
            notifications = result.scalars().all()

            return notifications

    async def read_notification(self, notification_id: str) -> AdminNotifications:
        async with self.session_factory() as session:
            query = select(AdminNotifications).where(
                AdminNotifications.uuid == notification_id
            )
            result = await session.execute(query)
            notification = result.scalar_one()

            notification.is_read = True
            await session.commit()

            return notification

    async def clear_notifications(self, user_uuid: str):
        async with self.session_factory() as session:
            await session.execute(
                update(AdminNotifications)
                .where(AdminNotifications.user_id == user_uuid)
                .values(is_read=True)
            )
            await session.commit()
