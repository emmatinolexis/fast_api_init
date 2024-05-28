from contextlib import AbstractContextManager
from datetime import datetime
from typing import Callable, Dict, List

from sqlalchemy import Date, cast
from sqlalchemy.orm import Session, joinedload

from app.core.constants import ALLOWED_EVENT_TYPES
from app.model.asset import Asset
from app.model.device import Device
from app.model.tracking_event import TrackingEvent
from app.repository.base_repository import BaseRepository
from app.util.utils import calculate_average_speed, get_status


class TrackingEventRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, TrackingEvent)

    def read_all_events_by_device_imei(self, device_imei: str, date: str):
        with self.session_factory() as session:
            query = (
                session.query(self.model)
                .filter(
                    self.model.device_imei == device_imei,
                    cast(self.model.event_datetime, Date)
                    == datetime.strptime(date, "%d/%m/%Y"),
                    self.model.event_type.in_(ALLOWED_EVENT_TYPES),
                )
                .order_by(self.model.event_datetime)
                .all()
            )

            return query

    def read_all_events_by_user(
        self, user_uuid: str, date: str
    ) -> Dict[str, List[TrackingEvent]]:
        with self.session_factory() as session:
            # get all device imei for user's assets
            events_by_device = {}
            user_assets = (
                session.query(Asset)
                .filter(Asset.user_uuid == user_uuid, Asset.device_imei.isnot(None))
                .all()
            )

            # get all events for each device IMEI
            for asset in user_assets:
                device_imei = asset.device_imei
                query = (
                    session.query(self.model)
                    .filter(
                        self.model.device_imei == device_imei,
                        cast(self.model.event_datetime, Date)
                        == datetime.strptime(date, "%d/%m/%Y"),
                        self.model.event_type.in_(ALLOWED_EVENT_TYPES),
                    )
                    .options(
                        joinedload(self.model.device).joinedload(Device.asset),
                    )
                    .order_by(self.model.event_datetime)
                    .all()
                )
                # Store the events for each device IMEI in the dictionary
                events_by_device[device_imei] = query

            return events_by_device

    def read_all_route_replay_events_by_device_imei(self, device_imei: str, date: str):
        with self.session_factory() as session:
            query = (
                session.query(self.model)
                .filter(
                    self.model.device_imei == device_imei,
                    cast(self.model.event_datetime, Date)
                    == datetime.strptime(date, "%d/%m/%Y"),
                    self.model.event_type.in_(ALLOWED_EVENT_TYPES),
                )
                .order_by(self.model.event_datetime)
                .all()
            )
        unique_entries = set()
        formatted_data = []
        for entry in query:
            if (entry.latitude, entry.longitude, entry.course) not in unique_entries:
                formatted_data.append(
                    {
                        "lat": entry.latitude,
                        "lng": entry.longitude,
                        "speed": entry.speed,
                        "course": entry.course,
                        "timestamp": entry.event_datetime,
                        "event_type": get_status(entry.event_type),
                    }
                )
                unique_entries.add((entry.latitude, entry.longitude, entry.course))
        return formatted_data

    def read_latest_tracking_event_by_device_imei(self, device_imei: str):
        with self.session_factory() as session:
            query = (
                session.query(self.model)
                .filter(self.model.device_imei == device_imei)
                .order_by(self.model.event_datetime.desc())
                .first()
            )
            return query

    def read_asset_average_speed(
        self, device_imei: str, date_from: datetime, date_to: datetime
    ):
        with self.session_factory() as session:
            query = (
                session.query(self.model)
                .filter(self.model.device_imei == device_imei)
                .filter(self.model.event_datetime >= date_from)
                .filter(self.model.event_datetime <= date_to)
                .all()
            )

            if not query:
                raise ValueError("No events found for the specified criteria.")

            event_data = [
                {
                    "speed": event.speed,
                    "latitude": event.latitude,
                    "longitude": event.longitude,
                    "event_datetime": event.event_datetime,
                }
                for event in query
                if event.speed is not None
            ]

            speeds = [event["speed"] for event in event_data]

            if not speeds:
                raise ValueError(
                    "No valid speed data available for the specified criteria."
                )

            average_speed = calculate_average_speed(speeds)
            return event_data, average_speed
