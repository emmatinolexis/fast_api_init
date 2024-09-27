from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session, joinedload

from app.model.device_alert_notification import DeviceAlertNotification
from app.repository.base_repository import BaseRepository


class DeviceAlertNotificationRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, DeviceAlertNotification)

    def get_recipients_by_node_id(self, node_id: str):
        with self.session_factory() as session:
            recipients = []
            data = (
                session.query(self.model)
                .filter(self.model.node_id == str(node_id))
                .options(joinedload(self.model.user))
                .all()
            )
            for record in data:
                user = {
                    "name": f"{record.user.first_name} {record.user.last_name}",
                    "email": record.user.email_address,
                    "phone_number": record.user.phone_number,
                }
                recipients.append(user)

            return recipients
