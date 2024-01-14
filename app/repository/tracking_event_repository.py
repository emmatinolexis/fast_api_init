from contextlib import AbstractContextManager
from datetime import datetime
from typing import Callable, List, Tuple

from sqlalchemy.orm import Session

from app.model.tracking_event import TrackingEvent
from app.repository.base_repository import BaseRepository


class TrackingEventRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, TrackingEvent)

    def read_all_events_by_device_imei(
        self, device_imei: str, date: str, limit: int
    ) -> TrackingEvent:
        with self.session_factory() as session:
            query = (
                session.query(self.model)
                .filter(
                    self.model.device_imei == device_imei,
                    self.model.event_datetime >= datetime.strptime(date, "%d/%m/%Y"),
                    self.model.event_type.in_(
                        ["Stop_Moving", "Start_Moving", "Idling_Alarm", "Ignition_Off"]
                    ),
                )
                .limit(limit)
                .all()
            )

            return query

    def read_all_route_replay_events_by_device_imei(
        self, device_imei: str
    ) -> List[Tuple[float, float, float, datetime]]:
        with self.session_factory() as session:
            query = (
                session.query(
                    self.model.latitude,
                    self.model.longitude,
                    self.model.speed,
                    self.model.event_datetime,
                )
                .filter(
                    self.model.device_imei == device_imei,
                )
                .all()
            )

            # Convert the results to a list of tuples
            result = [
                (latitude, longitude, speed, event_datetime)
                for latitude, longitude, speed, event_datetime in query
            ]
            return result
