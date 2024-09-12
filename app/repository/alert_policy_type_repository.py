from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.model.alert_policy_type import AlertPolicyType
from app.repository.base_repository import BaseRepository


class AlertPolicyTypeRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, AlertPolicyType)

    def delete_alert_policy_type_by_alert_uuid(self, alert_uuid: str):
        with self.session_factory() as session:
            try:
                alert_types = (
                    session.query(self.model).filter_by(alert_uuid=alert_uuid).delete()
                )
                return alert_types
            except Exception as e:
                session.rollback()
                raise e
