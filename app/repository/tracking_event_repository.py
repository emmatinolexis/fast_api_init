from contextlib import AbstractContextManager
from datetime import datetime, timedelta
from typing import Callable, Dict, List

from sqlalchemy import Date, and_, cast
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
        


    def get_event_by_device_imei(self, device_imei: str):
        with self.session_factory() as session:
            query = session.query(self.model).filter(self.model.device_imei.ilike(f"%{device_imei}%")).first()
            return query

    def read_all_events_by_date_range(
        self, device_imei: str, date_from: str, date_to: str
    ):
        # Parse the given date range
        start_date = datetime.strptime(date_from, "%d/%m/%Y")
        end_date = datetime.strptime(date_to, "%d/%m/%Y")

        # Calculate the difference in days
        date_diff = end_date - start_date

        # Calculate the past date range
        past_start_date = start_date - timedelta(days=date_diff.days + 1)
        past_end_date = end_date - timedelta(days=date_diff.days + 1)

        with self.session_factory() as session:
            # Query for the given date range
            current_range_events = (
                session.query(self.model)
                .filter(
                    self.model.device_imei == device_imei,
                    and_(
                        cast(self.model.event_datetime, Date) >= start_date,
                        cast(self.model.event_datetime, Date) <= end_date,
                    ),
                    self.model.event_type.in_(ALLOWED_EVENT_TYPES),
                )
                .order_by(self.model.event_datetime)
                .all()
            )

            # Query for the past date range
            past_range_events = (
                session.query(self.model)
                .filter(
                    self.model.device_imei == device_imei,
                    and_(
                        cast(self.model.event_datetime, Date) >= past_start_date,
                        cast(self.model.event_datetime, Date) <= past_end_date,
                    ),
                    self.model.event_type.in_(ALLOWED_EVENT_TYPES),
                )
                .order_by(self.model.event_datetime)
                .all()
            )

            # Return results in a dictionary form
            return {
                "current_range_events": current_range_events,
                "past_range_events": past_range_events,
            }

    def read_all_events_by_device_imei_date_range(
        self, device_imei: str, start_date: str, end_date: str
    ):
        with self.session_factory() as session:
            query = (
                session.query(self.model)
                .filter(
                    self.model.device_imei == device_imei,
                    and_(
                        cast(self.model.event_datetime, Date)
                        >= datetime.strptime(start_date, "%d/%m/%Y"),
                        cast(self.model.event_datetime, Date)
                        <= datetime.strptime(end_date, "%d/%m/%Y"),
                    ),
                    self.model.event_type.in_(ALLOWED_EVENT_TYPES),
                )
                .order_by(self.model.event_datetime)
                .all()
            )

            return query

    def read_all_events_by_user(
        self, date: str, user_uuid: str = None, business_uuid: str = None
    ) -> Dict[str, List[TrackingEvent]]:
        with self.session_factory() as session:
            # get all device imei for user's assets
            events_by_device = {}
            if user_uuid:
                user_assets = (
                    session.query(Asset)
                    .filter(Asset.user_uuid == user_uuid, Asset.device_imei.isnot(None))
                    .all()
                )

            if business_uuid:
                user_assets = (
                    session.query(Asset)
                    .filter(
                        Asset.business_profile_uuid == business_uuid,
                        Asset.device_imei.isnot(None),
                    )
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
                events_by_device[device_imei] = {"events": query, "asset": asset}

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
