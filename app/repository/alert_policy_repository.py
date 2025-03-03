import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, List, Optional
from uuid import UUID

from sqlalchemy import Date, and_, case, cast, desc, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.future import select
from app.core import messages
from sqlalchemy.orm import selectinload
from app.core.exceptions import NotFoundError
from app.model.alert_policy import AlertPolicy
from app.model.alert_policy_violations import AlertPolicyViolation
from app.model.asset import Asset
from app.model.maintenance_alert import MaintenanceAlert
from app.model.tracking_event import TrackingEvent
from app.model.user import User
from app.repository.base_repository import BaseRepository
from app.util.enums import (
    ActiveStatus,
    GeofenceShapeType,
    GeofenceTypeUuid,
    ServiceStatus,
)
from app.util.utils import (
    calculate_time_traveled,
    check_idle_time_exceeds_limit,
    check_overspeeding,
    check_violated_geofence,
    generate_circle_geofence_coordinates,
    generate_polygon_geofence_coordinates,
    get_distance_travelled_by_coordinates,
    get_status,
    is_time_to_send_maintenance_alert,
    toggle_maintenance_status,
    toggle_status,
)


class AlertPolicyRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AsyncSession]):
        self.session_factory = session_factory
        super().__init__(session_factory, AlertPolicy)

    async def read_all_alert_policies(self, page, page_size):
        async with self.session_factory() as session:
            offset = (page - 1) * page_size

            query = (
                select(self.model)
                .order_by(desc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
                .options(
                    joinedload(AlertPolicy.alert_policy_type),
                    joinedload(AlertPolicy.assets),
                    joinedload(AlertPolicy.maintenance_alert_type),
                )
            )

            result = await session.execute(query)
            return result.scalars().all()  # No need for `.unique()`

    async def toggle_alert_status(self, alert_uuid):
        async with self.session_factory() as session:
            query = select(self.model).where(self.model.uuid == alert_uuid)
            result = await session.execute(query)
            alert = result.scalar_one_or_none()

            if not alert:
                raise Exception("Alert not found")

            alert.status = toggle_status(alert.status)
            await session.commit()
            await session.refresh(alert)

            return alert

    async def toggle_alert_violation_status(self, alert_violation_uuid):
        async with self.session_factory() as session:
            query = select(AlertPolicyViolation).where(
                AlertPolicyViolation.uuid == alert_violation_uuid
            )
            result = await session.execute(query)
            violation = result.scalar_one_or_none()

            if not violation:
                raise NotFoundError(
                    f"Alert Violation not found: {alert_violation_uuid}"
                )

            violation.status = toggle_status(violation.status)
            await session.commit()
            await session.refresh(violation)

            return violation

    async def toggle_maintenance_alert_status(self, alert_uuid, date=None):
        async with self.session_factory() as session:
            query = select(self.model).where(self.model.uuid == alert_uuid)
            result = await session.execute(query)
            maintenance_alert = result.scalar_one_or_none()

            if not maintenance_alert:
                raise NotFoundError(f"Maintenance Alert not found: {alert_uuid}")

            maintenance_alert.service_status = toggle_maintenance_status(
                maintenance_alert.service_status
            )

            if date:
                maintenance_alert.maintenance_updated_at = date

            await session.commit()
            await session.refresh(maintenance_alert)
            return maintenance_alert.service_status

    async def read_all_alert_policies_by_user(
        self,
        user_uuid: str,
        page: int = 1,
        page_size: int = 10,
        policy_status: Optional[ActiveStatus] = None,
        policy_types: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        search: Optional[str] = None,
    ):
        async with self.session_factory() as session:
            offset = (page - 1) * page_size

            # Start building the query
            query = select(self.model).where(self.model.user_uuid == user_uuid)

            query = query.join(self.model.assets)

            # Apply policy status filter
            if policy_status:
                query = query.where(self.model.status == policy_status)

            # Apply policy type filter
            if policy_types:
                valid_alert_policy_type = [
                    UUID(policy_type)
                    for policy_type in policy_types
                    if UUID(policy_type)
                ]
                if valid_alert_policy_type:
                    query = query.where(
                        self.model.alert_policy_type_uuid.in_(valid_alert_policy_type)
                    )

            # Apply date filter
            if start_date and end_date:
                query = query.where(
                    self.model.created_at >= start_date,
                    self.model.created_at < end_date,
                )

            # Apply search filter
            if search:
                search_term = f"%{search}%"
                query = query.where(
                    or_(
                        self.model.policy_name.ilike(search_term),
                        Asset.asset_name.ilike(search_term),
                    )
                )

            # Query to get the total count of alert policies
            count_query = select(func.count()).select_from(query.subquery())
            total_alert_policies = await session.execute(count_query)
            total_alert_policies = total_alert_policies.scalar()

            # Calculate total pages
            total_pages = (total_alert_policies + page_size - 1) // page_size

            # Fetch paginated results with ordering and relationships loaded
            paginated_query = (
                query.order_by(desc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
                .options(
                    joinedload(self.model.alert_policy_type),
                    joinedload(self.model.assets),
                    joinedload(self.model.alert_notification_types),
                    joinedload(self.model.maintenance_alert_type),
                )
            )

            result = await session.execute(paginated_query)
            alerts = result.unique().scalars().all()

            return {
                "alerts": alerts,
                "total_alert_policies": total_alert_policies,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": page_size,
            }

    async def read_all_alert_policies_by_business(
        self,
        business_uuid: str,
        page: int = 1,
        page_size: int = 10,
        policy_status: Optional[str] = None,
        policy_types: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        async with self.session_factory() as session:
            offset = (page - 1) * page_size

            base_query = self.build_base_query(
                business_uuid, policy_status, policy_types, start_date, end_date, search
            )
            total_alert_policies = await self.count_alert_policies(session, base_query)
            total_pages = (total_alert_policies + page_size - 1) // page_size

            alerts = await self.fetch_paginated_alerts(
                session, base_query, offset, page_size
            )
            formatted_alerts = [self.format_alert(alert) for alert in alerts]

            return {
                "alerts": formatted_alerts,
                "total_alert_policies": total_alert_policies,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": page_size,
            }

    def build_base_query(
        self,
        business_uuid: str,
        policy_status: Optional[str],
        policy_types: Optional[List[str]],
        start_date: Optional[str],
        end_date: Optional[str],
        search: Optional[str],
    ):
        query = select(self.model).where(
            self.model.business_profile_uuid == business_uuid
        )
        query = query.join(self.model.assets)

        if policy_status:
            query = query.where(self.model.status == policy_status)

        if policy_types:
            valid_types = [UUID(policy) for policy in policy_types if UUID(policy)]
            if valid_types:
                query = query.where(self.model.alert_policy_type_uuid.in_(valid_types))

        if start_date and end_date:
            query = query.where(
                self.model.created_at >= start_date, self.model.created_at < end_date
            )

        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    self.model.policy_name.ilike(search_term),
                    Asset.asset_name.ilike(search_term),
                )
            )

        return query

    async def count_alert_policies(self, session: AsyncSession, query):
        count_query = select(func.count()).select_from(query.subquery())
        result = await session.execute(count_query)
        return result.scalar()

    async def fetch_paginated_alerts(
        self, session: AsyncSession, query, offset: int, page_size: int
    ):
        paginated_query = (
            query.order_by(desc(self.model.created_at))
            .offset(offset)
            .limit(page_size)
            .options(
                joinedload(self.model.alert_policy_type),
                joinedload(self.model.assets),
                joinedload(self.model.alert_notification_types),
                joinedload(self.model.maintenance_alert_type),
                joinedload(self.model.alert_recipients),
            )
        )
        result = await session.execute(paginated_query)
        return result.unique().scalars().all()

    def format_alert(self, alert: Any) -> Dict[str, Any]:
        notification_data = {"email": [], "sms": []}
        for recipient in alert.alert_recipients:
            if "@" in recipient.recipient:
                notification_data["email"].append(recipient.recipient)
            else:
                notification_data["sms"].append(recipient.recipient)

        return {
            "uuid": alert.uuid,
            "policy_name": alert.policy_name,
            "geofence_location_name": alert.geofence_location_name or None,
            "minimum_idle_time": alert.minimum_idle_time or None,
            "created_at": alert.created_at,
            "geofence_type": alert.geofence_type or None,
            "geofence_shape_type": alert.geofence_shape_type or None,
            "geofence_coordinate_data": alert.geofence_coordinate_data or None,
            "maximum_speed_limit": alert.maximum_speed_limit or None,
            "status": alert.status,
            "maintenance_alert_schedule": alert.maintenance_alert_schedule or None,
            "service_status": alert.service_status or None,
            "maintenance_alert_type": (
                {
                    "uuid": alert.maintenance_alert_type.uuid,
                    "name": alert.maintenance_alert_type.name,
                }
                if alert.maintenance_alert_type
                else {}
            ),
            "assets": [
                {
                    "vehicle_license_no": asset.vehicle_license_no,
                    "asset_name": asset.asset_name,
                }
                for asset in alert.assets
            ],
            "alert_recipients": [
                {"recipient": recipient.recipient}
                for recipient in alert.alert_recipients
            ],
            "alert_notification_types": [
                {"alert_notification_type": n_type, "recipients": recipients}
                for n_type, recipients in notification_data.items()
            ],
            "alert_policy_type": {"name": alert.alert_policy_type.name},
        }

    async def read_all_alert_violations_by_user(
        self,
        user_uuid: str,
        page: int = 1,
        page_size: int = 10,
        policy_type: Optional[str] = None,
        policy_status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        search: Optional[str] = None,
    ):
        async with self.session_factory() as session:
            offset = (page - 1) * page_size

            # Start building the query
            query = select(AlertPolicyViolation).where(
                AlertPolicyViolation.user_uuid == user_uuid
            )

            query = query.join(AlertPolicyViolation.alert_policy).join(
                AlertPolicyViolation.asset
            )
            query = query.join(AlertPolicy.alert_policy_type)

            # Apply policy type filter
            if policy_type:
                query = query.where(AlertPolicy.alert_policy_type.has(name=policy_type))

            # Apply policy status filter
            if policy_status:
                query = query.where(AlertPolicyViolation.status == policy_status)

            # Apply date filter
            try:
                if start_date:
                    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                    query = query.where(
                        AlertPolicyViolation.created_at >= start_date_obj
                    )
                if end_date:
                    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(
                        days=1
                    )
                    query = query.where(AlertPolicyViolation.created_at < end_date_obj)
            except ValueError:
                raise ValueError("Invalid date format. Expected 'YYYY-MM-DD'.")

            # Apply search filter
            if search:
                search_term = f"%{search}%"
                query = query.where(
                    or_(
                        AlertPolicy.policy_name.ilike(search_term),
                        Asset.asset_name.ilike(search_term),
                    )
                )

            # Query to get the total count of alert violations
            count_query = select(func.count()).select_from(query.subquery())
            total_alerts = await session.execute(count_query)
            total_alerts = total_alerts.scalar()

            # Calculate total pages
            total_pages = (total_alerts + page_size - 1) // page_size

            # Fetch paginated results with ordering and relationships loaded
            paginated_query = (
                query.order_by(
                    case(
                        (AlertPolicyViolation.status == ActiveStatus.ACTIVE, 1), else_=2
                    ),  # Active first
                    desc(AlertPolicyViolation.created_at),  # Then sort by created_at
                )
                .offset(offset)
                .limit(page_size)
                .options(
                    joinedload(AlertPolicyViolation.alert_policy),
                    joinedload(AlertPolicyViolation.asset).joinedload(Asset.driver),
                    joinedload(AlertPolicyViolation.user).defer(User.password),
                )
            )

            result = await session.execute(paginated_query)
            alerts = result.scalars().all()

            return {
                "alerts": alerts,
                "total_alerts": total_alerts,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": page_size,
            }

    async def read_all_alert_violations_by_business(
        self,
        business_uuid: str,
        page: int = 1,
        page_size: int = 10,
        policy_status: Optional[str] = None,
        policy_types: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        search: Optional[str] = None,
    ):
        async with self.session_factory() as session:
            offset = (page - 1) * page_size

            # Base query
            query = select(AlertPolicyViolation).where(
                AlertPolicyViolation.business_profile_uuid == business_uuid
            )

            # Apply policy type filter
            if policy_types:
                try:
                    valid_policy_types = [UUID(pt) for pt in policy_types if pt]
                    if valid_policy_types:
                        query = query.where(
                            AlertPolicy.alert_policy_type_uuid.in_(valid_policy_types)
                        )
                except ValueError:
                    raise ValueError("Invalid policy type UUID format.")

            # Apply policy status filter
            if policy_status:
                query = query.where(AlertPolicyViolation.status == policy_status)

            # Apply date filter
            try:
                if start_date:
                    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                    query = query.where(
                        AlertPolicyViolation.created_at >= start_date_obj
                    )
                if end_date:
                    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(
                        days=1
                    )
                    query = query.where(AlertPolicyViolation.created_at < end_date_obj)
            except ValueError:
                raise ValueError("Invalid date format. Expected 'YYYY-MM-DD'.")

            # Apply search filter
            if search:
                search_term = f"%{search}%"
                query = query.where(
                    or_(
                        AlertPolicy.policy_name.ilike(search_term),
                        Asset.asset_name.ilike(search_term),
                    )
                )

            # Get total count
            total_alerts = await session.execute(
                select(func.count()).select_from(query.subquery())
            )
            total_alerts = total_alerts.scalar()

            # Calculate total pages
            total_pages = (total_alerts + page_size - 1) // page_size

            # Fetch paginated results with optimized relationship loading
            paginated_query = (
                query.order_by(
                    case(
                        (AlertPolicyViolation.status == ActiveStatus.ACTIVE, 1), else_=2
                    ),
                    AlertPolicyViolation.created_at.desc(),
                )
                .offset(offset)
                .limit(page_size)
                .options(
                    selectinload(AlertPolicyViolation.alert_policy),
                    selectinload(AlertPolicyViolation.asset),
                    selectinload(AlertPolicyViolation.user).defer(User.password),
                )
            )

            result = await session.execute(paginated_query)
            alerts = result.scalars().all()
            serialized_alerts = []
            for alert in alerts:

                alert = {
                    "uuid": alert.uuid,
                    "status": alert.status,
                    "violation_time": alert.violation_time,
                    "violation_distance": alert.violation_distance,
                    "created_at": alert.created_at,
                    "alert_policy": {"policy_name": alert.alert_policy.policy_name},
                    "user": alert.user,
                    "asset": {"asset_name": alert.asset.asset_name},
                }
                serialized_alerts.append(alert)

            return {
                "alerts": serialized_alerts,
                "total_alerts": total_alerts,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": page_size,
            }

    async def get_active_geofence_alert_policies(self, session):
        result = await session.execute(
            select(AlertPolicy)
            .where(
                AlertPolicy.alert_policy_type_uuid
                == GeofenceTypeUuid.GEOFENCE_ALERT_POLICY.value,
                AlertPolicy.status == ActiveStatus.ACTIVE,
            )
            .options(
                joinedload(AlertPolicy.assets),
                joinedload(AlertPolicy.alert_recipients),
            )
        )
        return result.unique().scalars().all()

    async def get_active_over_speeding_alert_policies(self, session):
        result = await session.execute(
            select(AlertPolicy)
            .where(
                AlertPolicy.alert_policy_type_uuid
                == GeofenceTypeUuid.OVER_SPEEDING_ALERT_POLICY,
                AlertPolicy.status == ActiveStatus.ACTIVE,
            )
            .options(
                joinedload(AlertPolicy.assets),
                joinedload(AlertPolicy.alert_recipients),
            )
        )
        return result.unique().scalars().all()

    async def get_active_idling_alert_policies(self, session):
        result = await session.execute(
            select(AlertPolicy)
            .where(
                AlertPolicy.alert_policy_type_uuid
                == GeofenceTypeUuid.IDLING_ALERT_POLICY,
                AlertPolicy.status == ActiveStatus.ACTIVE,
            )
            .options(
                joinedload(AlertPolicy.assets),
                joinedload(AlertPolicy.alert_recipients),
            )
        )
        return result.unique().scalars().all()

    async def get_active_maintenance_policies(self, session):
        result = await session.execute(
            select(AlertPolicy)
            .where(
                AlertPolicy.alert_policy_type_uuid
                == GeofenceTypeUuid.MAINTENANCE_ALERT_POLICY,
                AlertPolicy.status == ActiveStatus.ACTIVE,
            )
            .options(
                joinedload(AlertPolicy.assets),
                joinedload(AlertPolicy.alert_recipients),
            )
        )
        return result.unique().scalars().all()

    def generate_geofence_points(self, alert_policy):
        geofence_violation_data = alert_policy.geofence_coordinate_data
        if alert_policy.geofence_shape_type == GeofenceShapeType.CIRCULAR:
            return generate_circle_geofence_coordinates(
                geofence_violation_data.get("center_point"),
                geofence_violation_data.get("radius"),
                100,
            )
        else:
            return generate_polygon_geofence_coordinates(geofence_violation_data, 100)

    async def get_last_checked_time(self, session, device_imei, today_date):
        result = await session.execute(
            select(func.max(TrackingEvent.last_checked_geofence_violation)).where(
                TrackingEvent.device_imei == device_imei
            )
        )
        last_checked_time = result.scalar_one_or_none()  # Handles None case safely

        return (
            last_checked_time.replace(microsecond=0)
            if last_checked_time
            else datetime.combine(today_date, datetime.min.time())
        )

    async def get_last_checked_over_speeding_time(
        self, session, device_imei, today_date
    ):
        result = await session.execute(
            select(func.max(TrackingEvent.last_checked_over_speeding_violation)).where(
                TrackingEvent.device_imei == device_imei
            )
        )
        last_checked_time = result.scalar_one_or_none()  # Handles None case safely

        return (
            last_checked_time.replace(microsecond=0)
            if last_checked_time
            else datetime.combine(today_date, datetime.min.time())
        )

    async def get_last_checked_idling_time(self, session, device_imei, today_date):
        result = await session.execute(
            select(func.max(TrackingEvent.last_checked_idling_violation)).where(
                TrackingEvent.device_imei == device_imei
            )
        )
        last_checked_time = result.scalar_one_or_none()  # Avoids None errors

        return (
            last_checked_time.replace(microsecond=0)
            if last_checked_time
            else datetime.combine(today_date, datetime.min.time())
        )

    async def get_asset_points(self, session, device_imei, last_checked_time):
        result = await session.execute(
            select(TrackingEvent).where(
                TrackingEvent.device_imei == device_imei,
                TrackingEvent.event_datetime > last_checked_time,
            )
        )
        return result.unique().scalars().all()

    def extract_coordinates_and_events(self, asset_points):
        asset_coordinates_events = [
            {
                "latitude": point.latitude,
                "longitude": point.longitude,
                "speed": point.speed,
                "course": point.course,
                "timestamp": str(point.event_datetime),
                "event_type": get_status(point.event_type),
            }
            for point in asset_points
        ]
        return asset_coordinates_events

    def check_violations(
        self, asset_coordinates_events, geofence_points, geofence_type
    ):
        return check_violated_geofence(
            asset_coordinates_events, geofence_points, geofence_type
        )

    def check_over_speeding(self, asset_coordinates_events, speed_limit):
        return check_overspeeding(asset_coordinates_events, speed_limit)

    def check_idling(self, asset_coordinates_events, idle_minimum_time):
        return check_idle_time_exceeds_limit(
            asset_coordinates_events, idle_minimum_time
        )

    async def create_violation_record(
        self,
        session,
        alert_policy,
        geofence_asset,
        asset_coordinates_events,
        violation_time=0,
        violation_distance=0,
    ):
        violation = AlertPolicyViolation(
            alert_policy_uuid=alert_policy.uuid,
            asset_uuid=geofence_asset.uuid,
            violation_coordinates=asset_coordinates_events,
            user_uuid=alert_policy.user_uuid,
            business_profile_uuid=alert_policy.business_profile_uuid,
            status=ActiveStatus.ACTIVE,
            violation_time=violation_time,
            violation_distance=violation_distance,
        )
        session.add(violation)
        await session.commit()

    async def get_violation_record(
        self, session, alert_policy_uuid, geofence_asset_uuid
    ):
        result = await session.execute(
            select(AlertPolicyViolation).where(
                AlertPolicyViolation.asset_uuid == geofence_asset_uuid,
                AlertPolicyViolation.alert_policy_uuid == alert_policy_uuid,
            )
        )
        return result.scalar_one_or_none()

    async def update_violation_record(
        self,
        session,
        alert_policy_uuid,
        geofence_asset_uuid,
        asset_coordinates_events,
        violation_time=0,
        violation_distance=0,
    ):
        # Fetch the violation record
        result = await session.execute(
            select(AlertPolicyViolation).where(
                AlertPolicyViolation.alert_policy_uuid == alert_policy_uuid,
                AlertPolicyViolation.asset_uuid == geofence_asset_uuid,
            )
        )
        violation = result.scalar_one_or_none()

        # Ensure the record exists before updating
        if violation:
            violation.asset_coordinates = asset_coordinates_events
            violation.violation_time = violation_time
            violation.violation_distance = violation_distance
            violation.updated_at = datetime.utcnow()  # Ensure consistent UTC timestamps

            await session.commit()  # Commit the changes to the database
            return violation
        else:
            return None

    async def create_maintenance_alert_record(
        self, session, asset_uuid, alert_policy_uuid, business_profile_uuid, user_uuid
    ):
        maintenance_alert = MaintenanceAlert(
            alert_policy_uuid=alert_policy_uuid,
            asset_uuid=asset_uuid,
            user_uuid=user_uuid,
            business_profile_uuid=business_profile_uuid,
            status=ServiceStatus.NOT_SERVICED,
        )

        session.add(maintenance_alert)

    def update_last_checked_time(self, asset_points):
        for point in asset_points:
            point.last_checked_geofence_violation = datetime.now()

    def update_last_checked_over_speeding_time(self, asset_points):
        for point in asset_points:
            point.last_checked_over_speeding_violation = datetime.now()

    def update_last_checked_idling_time(self, asset_points):
        for point in asset_points:
            point.last_checked_idling_violation = datetime.now()

    async def check_geofence_violation(self):
        async with self.session_factory() as session:
            violations = []

            # Get all active geofence alert policies
            alert_policies = await self.get_active_geofence_alert_policies(session)

            # Get the current date
            today_date = datetime.now().date()

            for alert_policy in alert_policies:
                # Generate geofence points based on shape type
                geofence_points = self.generate_geofence_points(alert_policy)

                # Get all assets for the current alert policy
                geofence_assets = alert_policy.assets

                # Get all alert recipients
                alert_recipients = alert_policy.alert_recipients

                for geofence_asset in geofence_assets:
                    # Get the last checked time for the asset
                    last_checked_time = await self.get_last_checked_time(
                        session, geofence_asset.device_imei, today_date
                    )

                    # Query the database for tracking events that occurred after the last checked time
                    asset_points = await self.get_asset_points(
                        session, geofence_asset.device_imei, last_checked_time
                    )

                    # Extract coordinates and events
                    asset_coordinates_events = self.extract_coordinates_and_events(
                        asset_points
                    )

                    # Check for geofence violations
                    violated_asset_coordinates = self.check_violations(
                        asset_coordinates_events,
                        geofence_points,
                        alert_policy.geofence_type,
                    )

                    if violated_asset_coordinates:
                        violation_time = calculate_time_traveled(
                            violated_asset_coordinates
                        )
                        violation_distance = get_distance_travelled_by_coordinates(
                            violated_asset_coordinates
                        )

                        violations.append(
                            {
                                "asset": {"asset_name": geofence_asset.asset_name},
                                "violation_time": violation_time,
                                "violation_distance": violation_distance,
                                "violated_points": violated_asset_coordinates,
                                "alert_policy": {
                                    "policy_name": alert_policy.policy_name
                                },
                                "alert_recipients": [
                                    {"recipient": recipient.recipient}
                                    for recipient in alert_recipients
                                ],
                            }
                        )

                        saved_violation = await self.get_violation_record(
                            session, alert_policy.uuid, geofence_asset.uuid
                        )

                        if saved_violation:
                            updated_coordinates = (
                                violated_asset_coordinates
                                + saved_violation.violation_coordinates
                            )
                            updated_violation_time = calculate_time_traveled(
                                updated_coordinates
                            )
                            updated_violation_distance = (
                                get_distance_travelled_by_coordinates(
                                    updated_coordinates
                                )
                            )
                            # update existing violation
                            await self.update_violation_record(
                                session,
                                alert_policy.uuid,
                                geofence_asset.uuid,
                                updated_coordinates,
                                updated_violation_time,
                                updated_violation_distance,
                            )
                        else:
                            # Create AlertPolicyViolation instance and persist it
                            await self.create_violation_record(
                                session,
                                alert_policy,
                                geofence_asset,
                                violated_asset_coordinates,
                                violation_time,
                                violation_distance,
                            )

                    # Update last checked geofence violation timestamp for the processed events
                    self.update_last_checked_time(asset_points)

            await session.commit()
            msg = "Geofence policy data fetched successfully"
            logging.info(msg)
            return {"message": msg, "violations": violations}

    async def check_over_speeding_violation(self):
        async with self.session_factory() as session:
            violations = []

            # Get all active geofence alert policies
            alert_policies = await self.get_active_over_speeding_alert_policies(session)

            # Get the current date
            today_date = datetime.now().date()

            for alert_policy in alert_policies:
                # Get policy speed limit value
                speed_limit_value = float(alert_policy.maximum_speed_limit)

                # Get all assets for the current alert policy
                alert_assets = alert_policy.assets

                # Get all alert recipients
                alert_recipients = alert_policy.alert_recipients

                for geofence_asset in alert_assets:
                    # Get the last checked time for the asset
                    last_checked_time = await self.get_last_checked_over_speeding_time(
                        session, geofence_asset.device_imei, today_date
                    )

                    # Query the database for tracking events that occurred after the last checked time
                    asset_points = await self.get_asset_points(
                        session, geofence_asset.device_imei, last_checked_time
                    )

                    asset_coordinates_events = self.extract_coordinates_and_events(
                        asset_points
                    )

                    # Check for geofence violations
                    violated_asset_coordinates = self.check_over_speeding(
                        asset_coordinates_events, speed_limit_value
                    )

                    if violated_asset_coordinates:
                        violation_time = calculate_time_traveled(
                            violated_asset_coordinates
                        )

                        violation_distance = get_distance_travelled_by_coordinates(
                            asset_coordinates_events
                        )

                        violations.append(
                            {
                                "asset": {"asset_name": geofence_asset.asset_name},
                                "violation_time": violation_time,
                                "violation_distance": violation_distance,
                                "violated_points": violated_asset_coordinates,
                                "alert_policy": {
                                    "policy_name": alert_policy.policy_name
                                },
                                "alert_recipients": [
                                    {"recipient": recipient.recipient}
                                    for recipient in alert_recipients
                                ],
                            }
                        )

                        # Create AlertPolicyViolation instance and persist it
                        await self.create_violation_record(
                            session,
                            alert_policy,
                            geofence_asset,
                            violated_asset_coordinates,
                            violation_time,
                            violation_distance,
                        )

                    # Update last checked geofence violation timestamp for the processed events
                    self.update_last_checked_over_speeding_time(asset_points)

            await session.commit()
            msg = "Geofence policy data fetched successfully"
            logging.info(msg)
            return {"message": msg, "violations": violations}

    async def check_idling_violation(self):
        async with self.session_factory() as session:
            violations = []

            # Get all active geofence alert policies
            alert_policies = await self.get_active_idling_alert_policies(session)

            # Get the current date
            today_date = datetime.now().date()

            for alert_policy in alert_policies:
                # Get policy speed limit value
                idling_minimum_time = float(alert_policy.minimum_idle_time)

                # Get all assets for the current alert policy
                alert_assets = alert_policy.assets

                # Get all alert recipients
                alert_recipients = alert_policy.alert_recipients

                for geofence_asset in alert_assets:
                    # Get the last checked time for the asset
                    last_checked_time = await self.get_last_checked_idling_time(
                        session, geofence_asset.device_imei, today_date
                    )

                    # Query the database for tracking events that occurred after the last checked time
                    asset_points = await self.get_asset_points(
                        session, geofence_asset.device_imei, last_checked_time
                    )

                    asset_coordinates_events = self.extract_coordinates_and_events(
                        asset_points
                    )

                    # Check for geofence violations
                    violated_asset_coordinates = self.check_idling(
                        asset_coordinates_events, idling_minimum_time
                    )

                    if violated_asset_coordinates:
                        violations.append(
                            {
                                "asset": {"asset_name": geofence_asset.asset_name},
                                "violated_points": violated_asset_coordinates,
                                "alert_policy": {
                                    "policy_name": alert_policy.policy_name
                                },
                                "alert_recipients": [
                                    {"recipient": recipient.recipient}
                                    for recipient in alert_recipients
                                ],
                            }
                        )

                        # Create AlertPolicyViolation instance and persist it
                        await self.create_violation_record(
                            session,
                            alert_policy,
                            geofence_asset,
                            violated_asset_coordinates,
                        )

                    # Update last checked geofence violation timestamp for the processed events
                    self.update_last_checked_idling_time(asset_points)

            await session.commit()
            msg = "Geofence policy data fetched successfully"
            logging.info(msg)
            return {"message": msg, "violations": violations}

    async def check_maintenance(self):
        async with self.session_factory() as session:
            violations = []

            # Get all active maintenance policies
            maintenance_policies = await self.get_active_maintenance_policies(session)

            for maintenance_policy in maintenance_policies:
                # Get policy speed limit value
                maintenance_alert_schedule = int(
                    maintenance_policy.maintenance_alert_schedule
                )

                # Get all assets for the current alert policy
                alert_assets = maintenance_policy.assets

                # Get all alert recipients
                alert_recipients = maintenance_policy.alert_recipients

                fire_alert = is_time_to_send_maintenance_alert(
                    maintenance_policy.created_at, maintenance_alert_schedule
                )
                if fire_alert:
                    for asset in alert_assets:
                        violations.append(
                            {
                                "asset": {"asset_name": asset.asset_name},
                                "alert_policy": {
                                    "policy_name": maintenance_policy.policy_name
                                },
                                "alert_recipients": [
                                    {"recipient": recipient.recipient}
                                    for recipient in alert_recipients
                                ],
                            }
                        )

                        # save maintenance alert into db here
                        await self.create_maintenance_alert_record(
                            session,
                            asset.uuid,
                            maintenance_policy.uuid,
                            asset.business_profile_uuid,
                            asset.user_uuid,
                        )
            await session.commit()
            msg = "Maintenance alerts check successful"
            logging.info(msg)
            return {"message": msg, "violations": violations}

    async def generate_violations_by_asset_uuids_date_range(
        self, start_date: str, end_date: str, asset_uuids: list
    ):
        async with self.session_factory() as session:
            # Convert dates to proper format (UTC)
            start_date_obj = datetime.strptime(start_date, "%d/%m/%Y").replace(
                tzinfo=timezone.utc
            )
            end_date_obj = datetime.strptime(end_date, "%d/%m/%Y").replace(
                tzinfo=timezone.utc
            ) + timedelta(days=1)

            # Query violations with optimized filtering
            violations = await session.execute(
                select(AlertPolicyViolation)
                .filter(
                    AlertPolicyViolation.asset_uuid.in_(asset_uuids),
                    AlertPolicyViolation.created_at >= start_date_obj,
                    AlertPolicyViolation.created_at < end_date_obj,
                )
                .options(
                    joinedload(AlertPolicyViolation.asset),
                    joinedload(AlertPolicyViolation.alert_policy).joinedload(
                        AlertPolicy.alert_policy_type
                    ),
                )
            )
            violations = violations.scalars().all()

            # Process data safely
            processed_data = []
            for violation in violations:
                asset_name = getattr(violation.asset, "asset_name", "Unknown")
                date_of_incidence = violation.created_at
                incident_name = getattr(
                    violation.alert_policy, "policy_name", "Unknown"
                )
                incident_type = getattr(
                    violation.alert_policy, "geofence_type", "Unknown"
                )

                incident_coordinate = violation.violation_coordinates or {}
                if "events" in incident_coordinate:
                    for event in incident_coordinate.get("events", [[None]]):
                        processed_data.append(
                            {
                                "asset_name": asset_name,
                                "date_of_incidence": date_of_incidence,
                                "incident_name": incident_name,
                                "incident_type": incident_type,
                                "incident_coordinate": event[0] if event else None,
                            }
                        )
                else:
                    processed_data.append(
                        {
                            "asset_name": asset_name,
                            "date_of_incidence": date_of_incidence,
                            "incident_name": incident_name,
                            "incident_type": incident_type,
                            "incident_coordinate": incident_coordinate.get(
                                "coordinates", [None]
                            )[0],
                        }
                    )

            return processed_data

    async def get_all_alert_reminders(self, user_uuid: str):
        async with self.session_factory() as session:
            today = datetime.now(timezone.utc).date()
            upcoming_date = today + timedelta(days=3)

            # Fetch all required fields in a single query
            query = select(AlertPolicy).filter(
                AlertPolicy.user_uuid == user_uuid,
                AlertPolicy.alert_policy_type_uuid
                == GeofenceTypeUuid.MAINTENANCE_ALERT_POLICY.value,
            )

            maintenance_policies = await session.execute(query)
            maintenance_policies = maintenance_policies.scalars().all()

            opened_reminders = []
            overdue_reminders = []
            upcoming_reminders = []

            for policy in maintenance_policies:
                due_date = policy.created_at.date() + timedelta(
                    days=int(policy.maintenance_alert_schedule or 0)
                )
                reminder_info = {
                    "policy_name": policy.policy_name,
                    "created_at": policy.created_at.isoformat(),
                }

                if policy.service_status == ServiceStatus.NOT_SERVICED:
                    opened_reminders.append(reminder_info)

                if due_date < today:
                    overdue_reminders.append(reminder_info)
                elif today <= due_date <= upcoming_date:
                    upcoming_reminders.append(reminder_info)

            reminders = {
                "opened_reminders_count": len(opened_reminders),
                "overdue_reminders_count": len(overdue_reminders),
                "upcoming_reminders_count": len(upcoming_reminders),
                "opened_reminders": opened_reminders,
                "overdue_reminders": overdue_reminders,
                "upcoming_reminders": upcoming_reminders,
            }

        return reminders
