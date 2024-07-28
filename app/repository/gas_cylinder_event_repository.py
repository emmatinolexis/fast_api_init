from contextlib import AbstractContextManager
from datetime import datetime
from typing import Callable

from sqlalchemy import Date, and_, cast
from sqlalchemy.orm import Session

from app.model.gas_cylinders import GasCylinderEvent
from app.repository.base_repository import BaseRepository


class GasCylinderEventRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, GasCylinderEvent)

    def read_all_gas_events_by_date_range(
        self, device_serial_number: str, start_date: str, end_date: str
    ):
        with self.session_factory() as session:
            query = (
                session.query(self.model)
                .filter(
                    self.model.device_serial_number == device_serial_number,
                    and_(
                        cast(self.model.event_timestamp, Date)
                        >= datetime.strptime(start_date, "%d/%m/%Y"),
                        cast(self.model.event_timestamp, Date)
                        <= datetime.strptime(end_date, "%d/%m/%Y"),
                    ),
                )
                .order_by(self.model.event_timestamp)
                .all()
            )

            return query
