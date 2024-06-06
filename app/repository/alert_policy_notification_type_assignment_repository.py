from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.model.alert_polcy_notification_type_assignment import (
    AlertPolicyNotificationTypeAssignment,
)
from app.repository.base_repository import BaseRepository


class AlertPolicyNotificationTypeAssignmentRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, AlertPolicyNotificationTypeAssignment)

    def read_all_by_uuid(self, uuid):
        with self.session_factory() as session:
            return session.query(self.model).filter_by(alert_policy_uuid=uuid).all()
