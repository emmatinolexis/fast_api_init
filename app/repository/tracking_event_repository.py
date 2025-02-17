from datetime import datetime, timedelta
from typing import Callable, Dict, List

from sqlalchemy import Date, and_, cast
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.future import select
from typing import Tuple

from app.core.constants import ALLOWED_EVENT_TYPES
from app.model.asset import Asset
from app.model.device import Device
from app.model.tracking_event import TrackingEvent
from app.repository.base_repository import BaseRepository
from app.util.utils import calculate_average_speed, get_status
import asyncio
from sqlalchemy.sql import func


class TrackingEventRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AsyncSession]):
        self.session_factory = session_factory
        super().__init__(session_factory, TrackingEvent)

    async def read_all_events_by_device_imei(self, device_imei: str, date: str):
        """Asynchronously retrieves all events for a device IMEI on a given date."""
        async with self.session_factory() as session:
            date_obj = datetime.strptime(
                date, "%d/%m/%Y"
            ).date()  # ✅ Convert string to date

            result = await session.execute(
                select(self.model)
                .where(
                    self.model.device_imei == device_imei,
                    cast(self.model.event_datetime, Date) == date_obj,
                    self.model.event_type.in_(ALLOWED_EVENT_TYPES),
                )
                .order_by(self.model.event_datetime)
            )

            return result.scalars().all()

    async def get_event_by_device_imei(self, device_imei: str):
        """Asynchronously retrieves an event by device IMEI."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(self.model).where(
                    self.model.device_imei.ilike(f"%{device_imei}%")
                )
            )
            return result.scalars().first()

    async def read_all_events_by_date_range(
        self, device_imei: str, date_from: str, date_to: str
    ):
        # Parse the given date range with proper format
        start_date = datetime.strptime(date_from, "%d/%m/%Y").date()
        end_date = datetime.strptime(date_to, "%d/%m/%Y").date()

        # Calculate the past date range
        date_diff = (end_date - start_date).days
        past_start_date = start_date - timedelta(days=date_diff + 1)
        past_end_date = end_date - timedelta(days=date_diff + 1)

        async with self.session_factory() as session:
            # Query for the given date range
            current_query = (
                select(self.model)
                .filter(
                    self.model.device_imei == device_imei,
                    cast(self.model.event_datetime, Date).between(start_date, end_date),
                    self.model.event_type.in_(ALLOWED_EVENT_TYPES),
                )
                .order_by(self.model.event_datetime)
            )

            past_query = (
                select(self.model)
                .filter(
                    self.model.device_imei == device_imei,
                    cast(self.model.event_datetime, Date).between(
                        past_start_date, past_end_date
                    ),
                    self.model.event_type.in_(ALLOWED_EVENT_TYPES),
                )
                .order_by(self.model.event_datetime)
            )

            # Execute queries asynchronously
            current_range_events, past_range_events = await asyncio.gather(
                session.execute(current_query),
                session.execute(past_query),
            )

            # Return results in dictionary format
            return {
                "current_range_events": current_range_events.scalars().all(),
                "past_range_events": past_range_events.scalars().all(),
            }

    async def read_all_events_by_device_imei_date_range(
        self, device_imei: str, start_date: str, end_date: str
    ):
        async with self.session_factory() as session:
            query = (
                select(self.model)
                .filter(
                    self.model.device_imei == device_imei,
                    and_(
                        cast(self.model.event_datetime, Date)
                        >= datetime.strptime(start_date, "%d/%m/%Y").date(),
                        cast(self.model.event_datetime, Date)
                        <= datetime.strptime(end_date, "%d/%m/%Y").date(),
                    ),
                    self.model.event_type.in_(ALLOWED_EVENT_TYPES),
                )
                .order_by(self.model.event_datetime)
            )

            result = await session.execute(query)
            return result.scalars().all()

    async def read_all_events_by_user(
        self, date: str, user_uuid: str = None, business_uuid: str = None
    ) -> Dict[str, List[TrackingEvent]]:
        async with self.session_factory() as session:
            events_by_device = {}
            if user_uuid:
                user_assets = await session.execute(
                    session.query(Asset).filter(
                        Asset.user_uuid == user_uuid, Asset.device_imei.isnot(None)
                    )
                )
                user_assets = user_assets.scalars().all()

            if business_uuid:
                user_assets = await session.execute(
                    session.query(Asset).filter(
                        Asset.business_profile_uuid == business_uuid,
                        Asset.device_imei.isnot(None),
                    )
                )
                user_assets = user_assets.scalars().all()

            for asset in user_assets:
                device_imei = asset.device_imei
                query = await session.execute(
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
                )
                events_by_device[device_imei] = {
                    "events": query.unique().scalars().all(),
                    "asset": asset,
                }

            return events_by_device

    async def read_all_route_replay_events_by_device_imei(
        self, device_imei: str, date: str
    ):
        async with self.session_factory() as session:
            query = await session.execute(
                session.query(self.model)
                .filter(
                    self.model.device_imei == device_imei,
                    cast(self.model.event_datetime, Date)
                    == datetime.strptime(date, "%d/%m/%Y"),
                    self.model.event_type.in_(ALLOWED_EVENT_TYPES),
                )
                .order_by(self.model.event_datetime)
            )
            query = query.scalars().all()

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

    async def read_latest_tracking_event_by_device_imei(self, device_imei: str):
        async with self.session_factory() as session:
            query = await session.execute(
                session.query(self.model)
                .filter(self.model.device_imei == device_imei)
                .order_by(self.model.event_datetime.desc())
            )
            return query.scalars().first()

    async def read_asset_average_speed(
        self, device_imei: str, date_from: datetime, date_to: datetime
    ):
        async with self.session_factory() as session:
            query = await session.execute(
                session.query(self.model)
                .filter(self.model.device_imei == device_imei)
                .filter(self.model.event_datetime >= date_from)
                .filter(self.model.event_datetime <= date_to)
            )

            events = query.scalars().all()

            if not events:
                raise ValueError("No events found for the specified criteria.")

            event_data = [
                {
                    "speed": event.speed,
                    "latitude": event.latitude,
                    "longitude": event.longitude,
                    "event_datetime": event.event_datetime,
                }
                for event in events
                if event.speed is not None
            ]

            speeds = [event["speed"] for event in event_data]

            if not speeds:
                raise ValueError(
                    "No valid speed data available for the specified criteria."
                )

            average_speed = calculate_average_speed(speeds)
            return event_data, average_speed

    async def get_all_unique_imeis(self):
        async with self.session_factory() as session:
            query = await session.execute(
                session.query(self.model.device_imei).distinct()
            )
            return [imei[0] for imei in query.scalars().all()]
        with self.session_factory() as session:
            query = session.query(self.model.device_imei).distinct().all()
            return [imei[0] for imei in query]

    async def get_events_for_all_imeis_on_date(
        self, date: str
    ) -> Dict[str, List[TrackingEvent]]:
        """Asynchronously retrieves tracking events for all IMEIs on a given date."""
        async with self.session_factory() as session:
            date_obj = datetime.strptime(
                date, "%d/%m/%Y"
            ).date()  # Convert string to date

            result = await session.execute(
                select(self.model)
                .where(
                    cast(self.model.event_datetime, Date) == date_obj,
                    self.model.event_type.in_(ALLOWED_EVENT_TYPES),
                )
                .order_by(self.model.event_datetime)
            )

            events_by_imei = {}
            for event in result.scalars().all():
                if not hasattr(event, "device_imei"):
                    raise ValueError(
                        f"Event {event} does not have device_imei attribute"
                    )
                events_by_imei.setdefault(event.device_imei, []).append(event)

            return events_by_imei

    async def get_inactive_assets_paginated(
        self, inactive_imeis: List[str], page: int, page_size: int
    ) -> Tuple[List[dict], int]:
        """Asynchronously fetches inactive assets with pagination."""
        async with self.session_factory() as session:
            offset = (page - 1) * page_size

            # Build query with filters and joins
            query = (
                select(Asset)
                .options(joinedload(Asset.device))
                .where(Asset.device_imei.in_(inactive_imeis))
            )

            # Get total count of records
            total_records_result = await session.execute(
                select(func.count()).select_from(query.subquery())
            )
            total_records = (
                total_records_result.scalar()
            )  # ✅ Correct way to get a single value

            # Fetch paginated results
            result = await session.execute(query.offset(offset).limit(page_size))
            assets = result.scalars().all()

            # Prepare response data
            paginated_assets = [
                {
                    "asset_name": asset.asset_name,
                    "vehicle_license_no": asset.vehicle_license_no,
                    "device_imei": asset.device_imei,
                    "sim_number": (
                        asset.device.sim_phone_number if asset.device else None
                    ),
                }
                for asset in assets
            ]

            return paginated_assets, total_records
