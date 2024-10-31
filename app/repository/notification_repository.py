from contextlib import AbstractContextManager
from typing import Callable,List

from sqlalchemy.orm import Session

from app.model.notification import Notification
from app.repository.base_repository import BaseRepository


class NotificationRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, Notification)
        


    def get_user_notifications(self,user_uuid:str) -> List[Notification]:
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter(self.model.user_id == str(user_uuid))
                .filter(self.model.is_read==False)
                .order_by(self.model.created_at.desc())
                .all()
            )
        

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
