from contextlib import AbstractAsyncContextManager
from typing import Callable, List, Optional

from sqlalchemy.ext import AsynSession
from sqlalchemy.future import select

from app.model.notification import Notification
from app.repository.base_repository import BaseRepository


class NotificationRepository(BaseRepository):
    def __init__(
        self, session_factory: Callable[..., AbstractAsyncContextManager[AsynSession]]
    ):
        self.session_factory = session_factory
        super().__init__(session_factory, Notification)

    async def get_user_notifications(
        self, user_uuid: str, is_read: Optional[bool] = None
    ) -> List[Notification]:
        async with self.session_factory() as session:
            query = select(self.model).where(self.model.user_id == user_uuid)

            # Apply the `is_read` filter if it is provided
            if is_read is not None:
                query = query.where(self.model.is_read == is_read)

            # Order by read status (unread first) and then by creation date descending
            query = query.order_by(
                self.model.is_read.asc(), self.model.created_at.desc()
            )

            # Execute the query asynchronously
            result = await session.execute(query)
            notifications = result.scalars().all()

            return notifications

    async def read_notification(self, notification_uuid: str) -> Notification:
        async with self.session_factory() as session:  # Async session
            notification = await session.get(self.model, notification_uuid)
            if notification:
                notification.is_read = True
                await session.commit()
            return notification

    async def clear_all_notifications(self, user_uuid: str):
        async with self.session_factory() as session:  # Async session
            result = await session.execute(
                select(self.model).where(self.model.user_id == user_uuid)
            )
            notifications = result.scalars().all()

            # Mark each unread notification as read
            for notification in notifications:
                if not notification.is_read:
                    notification.is_read = True

            await session.commit()
            return notifications
