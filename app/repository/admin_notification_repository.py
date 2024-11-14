from contextlib import AbstractContextManager
from typing import Callable, List

from sqlalchemy.orm import Session

from app.model.admin_notification import AdminNotifications
from app.repository.base_repository import BaseRepository


class AdminNotificationRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, AdminNotifications)

    def get_admin_notifications(
        self,
        user_uuid: str,
        notification_types: List[str],
        is_super_admin: bool = False,
    ) -> List[AdminNotifications]:
        with self.session_factory() as session:
            query = session.query(AdminNotifications)

            # Apply filters based on role
            if not is_super_admin:
                query = query.filter(AdminNotifications.user_id == user_uuid)

            notifications = query.filter(
                AdminNotifications.notification_type.in_(notification_types)
            ).order_by(
                AdminNotifications.is_read.asc(),  # Unread first
                AdminNotifications.created_at.desc()  # Newest first
            ).all()

            return notifications

        

    def read_notification(self, notification_id: str) -> AdminNotifications:
        with self.session_factory() as session:
            notification = session.query(AdminNotifications).filter(
                AdminNotifications.uuid == notification_id
            ).first()

            notification.is_read = True
            session.commit()

            return notification
        


    def clear_notifications(self, user_uuid: str):
        with self.session_factory() as session:
            session.query(AdminNotifications).filter(
                AdminNotifications.user_id == user_uuid
            ).update({"is_read": True})
            session.commit()
