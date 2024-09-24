from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.model.device_event import DeviceEvent
from app.repository.base_repository import BaseRepository


class DeviceEventRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, DeviceEvent)

    def get_device_latest_reading(self, node_id: str):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter(self.model.node_id == str(node_id))
                .order_by(self.model.created_at.desc())
                .first()
            )
