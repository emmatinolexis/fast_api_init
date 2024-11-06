from contextlib import AbstractContextManager
from typing import Callable,List,Optional

from sqlalchemy.orm import Session

from app.model.notification import Notification
from app.repository.base_repository import BaseRepository


class NotificationRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, Notification)
        


    def get_user_notifications(self, user_uuid: str, is_read: Optional[bool] = None) -> List[Notification]:
        with self.session_factory() as session:
            query = session.query(self.model).filter(self.model.user_id == user_uuid)
            
            # Apply the `is_read` filter if it is provided
            if is_read is not None:                                                                                                                                                                                                                                                                                                                             
                query = query.filter(self.model.is_read == is_read)
            
            # Order by read status (unread first) and then by creation date descending
            query = query.order_by(self.model.is_read.asc(), self.model.created_at.desc())
            
            # Execute the query and retrieve the results
            notifications = query.all()
            
            return notifications



    def read_notification(self, notification_uuid: str) -> Notification:
        with self.session_factory() as session:
            notification = (
                session.query(self.model)
                .filter(self.model.uuid == str(notification_uuid))
                .first()
            )
            if notification:
                notification.is_read = True
                session.commit()
            return notification


    def clear_all_notifications(self, user_uuid: str):
        with self.session_factory() as session:
            notifications = session.query(self.model).filter(self.model.user_id == user_uuid)

            # Mark each unread notification as read
            for notification in notifications:
                if not notification.is_read:
                    notification.is_read = True

            # Commit changes to save updates
            session.commit()

            return notifications
