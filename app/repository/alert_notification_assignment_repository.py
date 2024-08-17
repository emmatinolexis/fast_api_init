from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.model.alert_notification_assignment import AlertNotificationAssignment
from app.repository.base_repository import BaseRepository


class AlertNotificationAssignmentRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, AlertNotificationAssignment)

    def read_all_by_uuid(self, uuid):
        with self.session_factory() as session:
            return session.query(self.model).filter_by(alert_policy_uuid=uuid).all()

    def read_all_by_alert_policy_uuid(self, alert_policy_uuid):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter_by(alert_policy_uuid=alert_policy_uuid)
                .all()
            )

    def delete_by_recipient(self, alert_policy_uuid, recipient):
        with self.session_factory() as session:
            session.query(self.model).filter_by(
                alert_policy_uuid=alert_policy_uuid, recipient=recipient
            ).delete()
            session.commit()
            return True
