from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session, joinedload

from app.model.alert_policy import AlertPolicy
from app.repository.base_repository import BaseRepository


class AlertPolicyRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, AlertPolicy)

    def read_all_alert_policies(self):
        with self.session_factory() as session:
            alerts = (
                session.query(self.model)
                .options(joinedload(AlertPolicy.alert_policy_type))
                .options(joinedload(AlertPolicy.assets))
                .options(joinedload(AlertPolicy.maintenance_alert_type))
                .all()
            )
            return alerts

    def read_all_alert_policies_by_user(self, user_uuid: str):
        with self.session_factory() as session:
            alerts = (
                session.query(self.model)
                .filter(self.model.user_uuid == user_uuid)
                .options(joinedload(AlertPolicy.alert_policy_type))
                .options(joinedload(AlertPolicy.assets))
                .options(joinedload(AlertPolicy.maintenance_alert_type))
                .all()
            )
            return alerts
