import logging
from contextlib import AbstractContextManager
from datetime import date
from typing import Callable

from sqlalchemy import desc, func
from sqlalchemy.orm import Session, joinedload

from app.model.alert_policy import AlertPolicy
from app.model.alert_policy_violations import AlertPolicyViolation
from app.model.asset import Asset
from app.model.tracking_event import TrackingEvent
from app.repository.base_repository import BaseRepository
from app.util.enums import ActiveStatus, GeofenceShapeType, GeofenceTypeUuid
from app.util.utils import (
    check_violated_geofence,
    generate_circle_geofence_coordinates,
    generate_polygon_geofence_coordinates,
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

    def read_all_alert_policies_by_user(self, user_uuid: str, page=1, page_size=10):
        with self.session_factory() as session:
            offset = (page - 1) * page_size

            # Query to get the total count of alert policies
            total_alert_policies = (
                session.query(func.count(self.model.id))
                .filter(self.model.user_uuid == user_uuid)
                .scalar()
            )

            # Calculate total pages
            total_pages = (total_alert_policies + page_size - 1) // page_size

            # Fetch paginated results
            alerts = (
                session.query(self.model)
                .filter(self.model.user_uuid == user_uuid)
                .order_by(desc(self.model.created_at))
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

    def read_all_alert_violations_by_user(self, user_uuid: str, page=1, page_size=10):
        with self.session_factory() as session:
            offset = (page - 1) * page_size

            # Query to get the total count of alert violations
            total_alerts = (
                session.query(func.count(AlertPolicyViolation.id))
                .filter(AlertPolicyViolation.user_uuid == user_uuid)
                .scalar()
            )

            # Calculate total pages
            total_pages = (total_alerts + page_size - 1) // page_size

            # Fetch paginated results
            alerts = (
                session.query(AlertPolicyViolation)
                .filter(AlertPolicyViolation.user_uuid == user_uuid)
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

    def check_geofence_violation(self):
        with self.session_factory() as session:
            violations = []

            # get all active geofence alert policies
            alert_policies = (
                session.query(AlertPolicy)
                .filter(
                    AlertPolicy.alert_policy_type_uuid
                    == GeofenceTypeUuid.GEOFENCE_ALERT_POLICY
                )
                .filter(AlertPolicy.status == ActiveStatus.ACTIVE)
                .options(joinedload(AlertPolicy.assets))
                .options(joinedload(AlertPolicy.alert_recipients))
                .all()
            )

            # return alert_policies

            for alert_policy in alert_policies:
                # return alert_policy
                geofence_violation_data = alert_policy.geofence_coordinate_data

                # Generate geofence points based on shape type
                if alert_policy.geofence_shape_type == GeofenceShapeType.CIRCULAR:
                    geofence_points = generate_circle_geofence_coordinates(
                        geofence_violation_data.get("center_point"),
                        geofence_violation_data.get("radius"),
                        100,
                    )
                else:
                    geofence_points = generate_polygon_geofence_coordinates(
                        geofence_violation_data, 100
                    )

                # Get all assets for the current alert policy
                geofence_assets = alert_policy.assets

                # Get all alert recipient
                alert_recipients = alert_policy.alert_recipients

                # Get the current date
                today_date = date.today()
                today_date_str = today_date

                # Convert the current date to the format of event_datetime for comparison
                today_date_str = today_date_str.strftime("%Y-%m-%d")

                for geofence_asset in geofence_assets:
                    # Query the database for tracking events for today
                    asset_points = (
                        session.query(TrackingEvent)
                        .filter(
                            TrackingEvent.event_datetime
                            >= f"{today_date_str} 00:00:00.000"
                        )
                        .filter(
                            TrackingEvent.event_datetime
                            <= f"{today_date_str} 23:59:59.999"
                        )
                        .all()
                    )

                    asset_coordinates = [
                        (point.latitude, point.longitude) for point in asset_points
                    ]

                    violated_asset_coordinates = check_violated_geofence(
                        asset_coordinates, geofence_points, alert_policy.geofence_type
                    )

                    violations.append(
                        {
                            "asset": geofence_asset,
                            "violated_points": violated_asset_coordinates,
                            "alert_policy": alert_policy,
                            "alert_recipients": alert_recipients,
                        }
                    )

                    # # If violation occurs, create AlertPolicyViolation instance and persist it
                    if violated_asset_coordinates:
                        violation = AlertPolicyViolation(
                            alert_policy_uuid=alert_policy.uuid,
                            asset_uuid=geofence_asset.uuid,
                            violation_coordinates=violated_asset_coordinates,
                            user_uuid=alert_policy.user_uuid,
                            status=ActiveStatus.ACTIVE,
                        )
                        session.add(violation)

        session.commit()

        logging.info("Alert Notifications Sent")
        return {"message": "Notifications Sent", "violations": violations}
