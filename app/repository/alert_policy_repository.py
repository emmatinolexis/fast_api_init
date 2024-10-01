import logging
from contextlib import AbstractContextManager
from datetime import datetime, timedelta
from typing import Callable, Optional

from sqlalchemy import Date, and_, cast, desc, func, or_
from sqlalchemy.orm import Session, joinedload

from app.core import messages
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
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, AlertPolicy)

    def read_all_alert_policies(self, page, page_size):
        with self.session_factory() as session:
            offset = (page - 1) * page_size
            alerts = (
                session.query(self.model)
                .order_by(desc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
                .options(joinedload(AlertPolicy.alert_policy_type))
                .options(joinedload(AlertPolicy.assets))
                .options(joinedload(AlertPolicy.maintenance_alert_type))
                .all()
            )
            return alerts

    def toggle_alert_status(self, alert_uuid):
        with self.session_factory() as session:
            alert = (
                session.query(self.model).filter(self.model.uuid == alert_uuid).first()
            )
            if not alert:
                raise Exception("Alert not found")

            alert.status = toggle_status(alert.status)
            session.commit()
            session.refresh(alert)

            return alert

    def toggle_alert_violation_status(self, alert_violation_uuid):
        with self.session_factory() as session:
            violation = (
                session.query(AlertPolicyViolation)
                .filter(AlertPolicyViolation.uuid == alert_violation_uuid)
                .first()
            )

            violation.status = toggle_status(violation.status)
            session.commit()
            session.refresh(violation)

            return violation

    def toggle_maintenance_alert_status(self, alert_uuid, date):
        with self.session_factory() as session:
            maintenance_alert = (
                session.query(self.model).filter(self.model.uuid == alert_uuid).first()
            )

            if not maintenance_alert:
                raise NotFoundError(messages.MAINTENANCE_ALERT_NOT_FOUND + alert_uuid)

            new_status = toggle_maintenance_status(maintenance_alert.service_status)
            maintenance_alert.service_status = new_status

            if date:
                maintenance_alert.maintenance_updated_at = date

            session.commit()
            session.refresh(maintenance_alert)
            return maintenance_alert.service_status

    def read_all_alert_policies_by_user(
        self, user_uuid: str, alert_policy_type_uuid: str = None, page=1, page_size=10
    ):
        with self.session_factory() as session:
            offset = (page - 1) * page_size

            # Start building the query
            query = session.query(self.model).filter(self.model.user_uuid == user_uuid)

            # Apply the asset_type_uuid filter if provided
            if alert_policy_type_uuid:
                query = query.filter(
                    self.model.alert_policy_type_uuid == alert_policy_type_uuid
                )

            # Query to get the total count of alert policies
            total_alert_policies = query.count()

            # Calculate total pages
            total_pages = (total_alert_policies + page_size - 1) // page_size

            # Fetch paginated results with ordering and relationships loaded
            alerts = (
                query.order_by(desc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
                .options(joinedload(self.model.alert_policy_type))
                .options(joinedload(self.model.assets))
                .options(joinedload(self.model.alert_notification_types))
                .options(joinedload(self.model.maintenance_alert_type))
                .all()
            )

            return {
                "alerts": alerts,
                "total_alert_policies": total_alert_policies,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": page_size,
            }

    def read_all_alert_policies_by_business(
        self,
        business_uuid: str,
        alert_policy_type_uuid: str = None,
        page=1,
        page_size=10,
    ):
        with self.session_factory() as session:
            offset = (page - 1) * page_size

            # Start building the query
            query = session.query(self.model).filter(
                self.model.business_profile_uuid == business_uuid
            )

            # Apply the asset_type_uuid filter if provided
            if alert_policy_type_uuid:
                query = query.filter(
                    self.model.alert_policy_type_uuid == alert_policy_type_uuid
                )

            # Query to get the total count of alert policies
            total_alert_policies = query.count()

            # Calculate total pages
            total_pages = (total_alert_policies + page_size - 1) // page_size

            # Fetch paginated results with ordering and relationships loaded
            alerts = (
                query.order_by(desc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
                .options(joinedload(self.model.alert_policy_type))
                .options(joinedload(self.model.assets))
                .options(joinedload(self.model.alert_notification_types))
                .options(joinedload(self.model.maintenance_alert_type))
                .options(joinedload(self.model.alert_recipients))
                .all()
            )

            formatted_alerts = []
            for alert in alerts:
                # Initialize the notification_data dictionary with empty lists for email and sms
                notification_data = {"email": [], "sms": []}

                # Populate recipients into their respective notification types
                for recipient in alert.alert_recipients:
                    if "@" in recipient.recipient:
                        notification_data["email"].append(recipient.recipient)
                    else:
                        notification_data["sms"].append(recipient.recipient)

                # Prepare the final structure for the alert
                alert_data = {
                    **alert.__dict__,
                    "alert_notification_types": [
                        {
                            "alert_notification_type": notification_type,
                            "recipients": recipients,
                        }
                        for notification_type, recipients in notification_data.items()
                    ],
                }

                # Remove SQLAlchemy internal state (if any)
                alert_data.pop("_sa_instance_state", None)

                formatted_alerts.append(alert_data)

            # Return the final structure
            return {
                "alerts": formatted_alerts,
                "total_alert_policies": total_alert_policies,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": page_size,
            }

    def read_all_alert_violations_by_user(
        self,
        user_uuid: str,
        page=1,
        page_size=10,
        policy_type: Optional[str] = None,
        policy_status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        search: Optional[str] = None,
    ):
        with self.session_factory() as session:
            offset = (page - 1) * page_size

            # Start building the query
            query = session.query(AlertPolicyViolation).filter(
                AlertPolicyViolation.user_uuid == user_uuid
            )
            query = query.join(AlertPolicyViolation.alert_policy).join(
                AlertPolicyViolation.asset
            )
            query = query.join(AlertPolicy.alert_policy_type)

            # Apply policy type filter
            if policy_type:
                query = query.filter(
                    AlertPolicy.alert_policy_type.has(name=policy_type)
                )


            # Apply policy status filter
            if policy_status:
                query = query.filter(AlertPolicyViolation.status == policy_status)

            # Apply date filter
            if start_date and end_date:
                # Both start_date and end_date are provided
                try:
                    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
                    # Include the entire end date
                    end_date_obj += timedelta(days=1)
                    query = query.filter(
                        AlertPolicyViolation.created_at >= start_date_obj,
                        AlertPolicyViolation.created_at < end_date_obj,
                    )
                except ValueError:
                    raise ValueError("Invalid date format. Expected 'YYYY-MM-DD'.")
            elif start_date:
                # Only start_date is provided
                try:
                    date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                    next_day = date_obj + timedelta(days=1)
                    query = query.filter(
                        AlertPolicyViolation.created_at >= date_obj,
                        AlertPolicyViolation.created_at < next_day,
                    )
                except ValueError:
                    raise ValueError("Invalid date format. Expected 'YYYY-MM-DD'.")
            elif end_date:
                # Only end_date is provided
                try:
                    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
                    # Include the entire end date
                    end_date_obj += timedelta(days=1)
                    query = query.filter(AlertPolicyViolation.created_at < end_date_obj)
                except ValueError:
                    raise ValueError("Invalid date format. Expected 'YYYY-MM-DD'.")

            # Apply search filter
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    or_(
                        AlertPolicy.policy_name.ilike(search_term),
                        Asset.asset_name.ilike(search_term),
                    )
                )

            # Query to get the total count of alert violations
            total_alerts = query.count()

            # Calculate total pages
            total_pages = (total_alerts + page_size - 1) // page_size

            # Fetch paginated results
            alerts = (
                query.order_by(desc(AlertPolicyViolation.created_at))
                .offset(offset)
                .limit(page_size)
                .options(joinedload(AlertPolicyViolation.alert_policy))
                .options(
                    joinedload(AlertPolicyViolation.asset).joinedload(Asset.driver)
                )
                .options(joinedload(AlertPolicyViolation.user).defer(User.password))
                .all()
            )
            return {
                "alerts": alerts,
                "total_alerts": total_alerts,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": page_size,
            }

    def read_all_alert_violations_by_business(
        self, business_uuid: str, page=1, page_size=10
    ):
        with self.session_factory() as session:
            offset = (page - 1) * page_size

            # Query to get the total count of alert violations
            total_alerts = (
                session.query(func.count(AlertPolicyViolation.id))
                .filter(AlertPolicyViolation.business_profile_uuid == business_uuid)
                .scalar()
            )

            # Calculate total pages
            total_pages = (total_alerts + page_size - 1) // page_size

            # Fetch paginated results
            alerts = (
                session.query(AlertPolicyViolation)
                .filter(AlertPolicyViolation.business_profile_uuid == business_uuid)
                .order_by(desc(AlertPolicyViolation.created_at))
                .offset(offset)
                .limit(page_size)
                .options(joinedload(AlertPolicyViolation.alert_policy))
                .options(
                    joinedload(AlertPolicyViolation.asset).joinedload(Asset.driver)
                )
                .options(joinedload(AlertPolicyViolation.user))
                .all()
            )

            return {
                "alerts": alerts,
                "total_alerts": total_alerts,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": page_size,
            }

    def get_active_geofence_alert_policies(self, session):
        return (
            session.query(AlertPolicy)
            .filter(
                AlertPolicy.alert_policy_type_uuid
                == GeofenceTypeUuid.GEOFENCE_ALERT_POLICY,
                AlertPolicy.status == ActiveStatus.ACTIVE,
            )
            .options(
                joinedload(AlertPolicy.assets), joinedload(AlertPolicy.alert_recipients)
            )
            .all()
        )

    def get_active_over_speeding_alert_policies(self, session):
        return (
            session.query(AlertPolicy)
            .filter(
                AlertPolicy.alert_policy_type_uuid
                == GeofenceTypeUuid.OVER_SPEEDING_ALERT_POLICY,
                AlertPolicy.status == ActiveStatus.ACTIVE,
            )
            .options(
                joinedload(AlertPolicy.assets), joinedload(AlertPolicy.alert_recipients)
            )
            .all()
        )

    def get_active_idling_alert_policies(self, session):
        return (
            session.query(AlertPolicy)
            .filter(
                AlertPolicy.alert_policy_type_uuid
                == GeofenceTypeUuid.IDLING_ALERT_POLICY,
                AlertPolicy.status == ActiveStatus.ACTIVE,
            )
            .options(
                joinedload(AlertPolicy.assets), joinedload(AlertPolicy.alert_recipients)
            )
            .all()
        )

    def get_active_maintenance_policies(self, session):
        return (
            session.query(AlertPolicy)
            .filter(
                AlertPolicy.alert_policy_type_uuid
                == GeofenceTypeUuid.MAINTENANCE_ALERT_POLICY,
                AlertPolicy.status == ActiveStatus.ACTIVE,
            )
            .options(
                joinedload(AlertPolicy.assets), joinedload(AlertPolicy.alert_recipients)
            )
            .all()
        )

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

    def get_last_checked_time(self, session, device_imei, today_date):
        last_checked_time = (
            session.query(func.max(TrackingEvent.last_checked_geofence_violation))
            .filter(TrackingEvent.device_imei == device_imei)
            .scalar()
        )

        if last_checked_time is None:
            return datetime.combine(today_date, datetime.min.time())
        return last_checked_time.replace(microsecond=0)

    def get_last_checked_over_speeding_time(self, session, device_imei, today_date):
        last_checked_time = (
            session.query(func.max(TrackingEvent.last_checked_over_speeding_violation))
            .filter(TrackingEvent.device_imei == device_imei)
            .scalar()
        )

        if last_checked_time is None:
            return datetime.combine(today_date, datetime.min.time())
        return last_checked_time.replace(microsecond=0)

    def get_last_checked_idling_time(self, session, device_imei, today_date):
        last_checked_time = (
            session.query(func.max(TrackingEvent.last_checked_idling_violation))
            .filter(TrackingEvent.device_imei == device_imei)
            .scalar()
        )

        if last_checked_time is None:
            return datetime.combine(today_date, datetime.min.time())
        return last_checked_time.replace(microsecond=0)

    def get_asset_points(self, session, device_imei, last_checked_time):
        return (
            session.query(TrackingEvent)
            .filter(
                TrackingEvent.device_imei == device_imei,
                TrackingEvent.event_datetime > last_checked_time,
            )
            .all()
        )

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

    def create_violation_record(
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

    def get_violation_record(
        self,
        session,
        alert_policy_uuid,
        geofence_asset_uuid,
    ):
        return (
            session.query(AlertPolicyViolation)
            .filter(
                AlertPolicyViolation.asset_uuid == geofence_asset_uuid,
                AlertPolicyViolation.alert_policy_uuid == alert_policy_uuid,
            )
            .first()
        )

    def update_violation_record(
        self,
        session,
        alert_policy_uuid,
        geofence_asset_uuid,
        asset_coordinates_events,
        violation_time=0,
        violation_distance=0,
    ):
        violation = (
            session.query(AlertPolicyViolation)
            .filter(
                AlertPolicyViolation.alert_policy_uuid == alert_policy_uuid,
                AlertPolicyViolation.asset_uuid == geofence_asset_uuid,
            )
            .first()
        )
        violation.asset_coordinates = asset_coordinates_events
        violation.violation_time = violation_time
        violation.violation_distance = violation_distance
        violation.updated_at = datetime.now()

    def create_maintenance_alert_record(
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

    def check_geofence_violation(self):
        with self.session_factory() as session:
            violations = []

            # Get all active geofence alert policies
            alert_policies = self.get_active_geofence_alert_policies(session)

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
                    last_checked_time = self.get_last_checked_time(
                        session, geofence_asset.device_imei, today_date
                    )

                    # Query the database for tracking events that occurred after the last checked time
                    asset_points = self.get_asset_points(
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

                        saved_violation = self.get_violation_record(
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
                            self.update_violation_record(
                                session,
                                alert_policy.uuid,
                                geofence_asset.uuid,
                                updated_coordinates,
                                updated_violation_time,
                                updated_violation_distance,
                            )
                        else:
                            # Create AlertPolicyViolation instance and persist it
                            self.create_violation_record(
                                session,
                                alert_policy,
                                geofence_asset,
                                violated_asset_coordinates,
                                violation_time,
                                violation_distance,
                            )

                    # Update last checked geofence violation timestamp for the processed events
                    self.update_last_checked_time(asset_points)

            session.commit()
            msg = "Geofence policy data fetched successfully"
            logging.info(msg)
            return {"message": msg, "violations": violations}

    def check_over_speeding_violation(self):
        with self.session_factory() as session:
            violations = []

            # Get all active geofence alert policies
            alert_policies = self.get_active_over_speeding_alert_policies(session)

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
                    last_checked_time = self.get_last_checked_over_speeding_time(
                        session, geofence_asset.device_imei, today_date
                    )
                    # if not last_checked_time:
                    #     return geofence_asset
                    # return last_checked_time

                    # Query the database for tracking events that occurred after the last checked time
                    asset_points = self.get_asset_points(
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
                        self.create_violation_record(
                            session,
                            alert_policy,
                            geofence_asset,
                            violated_asset_coordinates,
                            violation_time,
                            violation_distance,
                        )

                    # Update last checked geofence violation timestamp for the processed events
                    self.update_last_checked_over_speeding_time(asset_points)

            session.commit()
            msg = "Geofence policy data fetched successfully"
            logging.info(msg)
            return {"message": msg, "violations": violations}

    def check_idling_violation(self):
        with self.session_factory() as session:
            violations = []

            # Get all active geofence alert policies
            alert_policies = self.get_active_idling_alert_policies(session)

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
                    last_checked_time = self.get_last_checked_idling_time(
                        session, geofence_asset.device_imei, today_date
                    )

                    # Query the database for tracking events that occurred after the last checked time
                    asset_points = self.get_asset_points(
                        session, geofence_asset.device_imei, last_checked_time
                    )

                    (
                        asset_coordinates,
                        asset_coordinates_events,
                    ) = self.extract_coordinates_and_events(asset_points)

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
                        self.create_violation_record(
                            session,
                            alert_policy,
                            geofence_asset,
                            violated_asset_coordinates,
                        )

                    # Update last checked geofence violation timestamp for the processed events
                    self.update_last_checked_idling_time(asset_points)

            session.commit()
            msg = "Geofence policy data fetched successfully"
            logging.info(msg)
            return {"message": msg, "violations": violations}

    def check_maintenance(self):
        with self.session_factory() as session:
            violations = []

            # Get all active maintenance policies
            maintenance_policies = self.get_active_maintenance_policies(session)

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
                        self.create_maintenance_alert_record(
                            session,
                            asset.uuid,
                            maintenance_policy.uuid,
                            asset.business_profile_uuid,
                            asset.user_uuid,
                        )
            session.commit()
            msg = "Maintenance alerts check successful"
            logging.info(msg)
            return {"message": msg, "violations": violations}

    def generate_violations_by_asset_uuids_date_range(
        self, start_date: str, end_date: str, asset_uuids: list
    ):
        with self.session_factory() as session:
            # Query to filter violations by asset UUIDs and date range
            violations = (
                session.query(AlertPolicyViolation)
                .filter(
                    AlertPolicyViolation.asset_uuid.in_(
                        asset_uuids
                    ),  # Filter by list of asset_uuids
                    and_(
                        cast(AlertPolicyViolation.created_at, Date)
                        >= datetime.strptime(start_date, "%d/%m/%Y"),
                        # Start date filter
                        cast(AlertPolicyViolation.created_at, Date)
                        <= datetime.strptime(end_date, "%d/%m/%Y")
                        # End date filter
                    ),
                )
                .options(
                    joinedload(AlertPolicyViolation.asset),  # Load the related Asset
                    joinedload(AlertPolicyViolation.alert_policy).joinedload(
                        AlertPolicy.alert_policy_type
                    ),  # Load related AlertPolicyType
                )
                .all()  # Fetch all matching violations
            )

            # Process the violations to extract individual events or coordinates
            processed_data = []

            for violation in violations:
                asset_name = (
                    violation.asset.asset_name
                )  # Assuming the Asset model has a 'name' attribute
                date_of_incidence = violation.created_at
                incident_name = (
                    violation.alert_policy.policy_name
                )  # Assuming the AlertPolicy model has a 'name' attribute
                incident_type = (
                    violation.alert_policy.geofence_type
                )  # Assuming the AlertPolicyType model has a 'name' attribute

                incident_coordinate = violation.violation_coordinates

                if "events" in incident_coordinate:
                    # If there are multiple events (e.g., idling), process each event
                    for event in incident_coordinate["events"]:
                        processed_data.append(
                            {
                                "asset_name": asset_name,
                                "date_of_incidence": date_of_incidence,
                                "incident_name": incident_name,
                                "incident_type": incident_type,
                                "incident_coordinate": event[0],
                            }
                        )
                else:
                    # For incidents with a single coordinate
                    processed_data.append(
                        {
                            "asset_name": asset_name,
                            "date_of_incidence": date_of_incidence,
                            "incident_name": incident_name,
                            "incident_type": incident_type,
                            "incident_coordinate": incident_coordinate[0],
                        }
                    )

            return processed_data

    def get_all_alert_reminders(self, user_uuid: str):
        with self.session_factory() as session:
            today = datetime.now().date()
            upcoming_date = today + timedelta(days=3)

            opened_reminders_data = (
                session.query(AlertPolicy.policy_name, AlertPolicy.created_at)
                .filter(
                    AlertPolicy.user_uuid == user_uuid,
                    AlertPolicy.service_status == ServiceStatus.NOT_SERVICED,
                    AlertPolicy.alert_policy_type_uuid
                    == GeofenceTypeUuid.MAINTENANCE_ALERT_POLICY,
                )
                .all()
            )

            opened_reminders_list = [
                {"policy_name": policy_name, "created_at": created_at.isoformat()}
                for policy_name, created_at in opened_reminders_data
            ]
            opened_reminders_count = len(opened_reminders_list)

            maintenance_policies = (
                session.query(AlertPolicy)
                .filter(
                    AlertPolicy.user_uuid == user_uuid,
                    AlertPolicy.alert_policy_type_uuid
                    == GeofenceTypeUuid.MAINTENANCE_ALERT_POLICY,
                )
                .all()
            )

            overdue_reminders = []
            upcoming_reminders = []

            for policy in maintenance_policies:
                due_date = policy.created_at.date() + timedelta(
                    days=int(policy.maintenance_alert_schedule)
                )

                reminder_info = {
                    "policy_name": policy.policy_name,
                    "created_at": policy.created_at.isoformat(),
                }

                if due_date < today:
                    overdue_reminders.append(reminder_info)
                elif today <= due_date <= upcoming_date:
                    upcoming_reminders.append(reminder_info)

            overdue_reminders_count = len(overdue_reminders)
            upcoming_reminders_count = len(upcoming_reminders)

            reminders = {
                "opened_reminders_count": opened_reminders_count,
                "overdue_reminders_count": overdue_reminders_count,
                "upcoming_reminders_count": upcoming_reminders_count,
                "opened_reminders": opened_reminders_list,
                "overdue_reminders": overdue_reminders,
                "upcoming_reminders": upcoming_reminders,
            }

        return reminders
