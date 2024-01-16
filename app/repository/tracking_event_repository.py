from contextlib import AbstractContextManager
from datetime import datetime
from typing import Callable

from sqlalchemy import Date, cast
from sqlalchemy.orm import Session

from app.model.tracking_event import TrackingEvent
from app.repository.base_repository import BaseRepository
from app.util.utils import get_status


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
                    cast(self.model.event_datetime, Date)
                    == datetime.strptime(date, "%d/%m/%Y"),
                    self.model.event_type.in_(
                        [
                            "Stop_Moving",
                            "Start_Moving",
                            "Idling_Alarm",
                            "Ignition_Off",
                            "Time_Interval_Tracking",
                        ]
                    ),
                )
                .limit(limit)
                .all()
            )

            return query

    def read_all_route_replay_events_by_device_imei(
        self, device_imei: str, date: str, limit: int
    ):
        with self.session_factory() as session:
            query = (
                session.query(self.model)
                .filter(
                    self.model.device_imei == device_imei,
                    cast(self.model.event_datetime, Date)
                    == datetime.strptime(date, "%d/%m/%Y"),
                    self.model.event_type.in_(
                        [
                            "Stop_Moving",
                            "Start_Moving",
                            "Idling_Alarm",
                            "Ignition_Off",
                            "Time_Interval_Tracking",
                        ]
                    ),
                )
                .limit(limit)
                .all()
            )
            formatted_data = (
                {
                    "longitude": entry.latitude,
                    "latitude": entry.longitude,
                    "speed": entry.speed,
                    "timestamp": entry.event_datetime,
                    "event_type": get_status(entry.event_type),
                }
                for entry in query
            )
            return formatted_data
