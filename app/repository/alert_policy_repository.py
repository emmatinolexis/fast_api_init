import logging
from contextlib import AbstractContextManager
from datetime import date
from typing import Callable

from sqlalchemy.orm import Session, joinedload

from app.model.alert_policy import AlertPolicy
from app.model.alert_policy_violations import AlertPolicyViolation
from app.model.tracking_event import TrackingEvent
from app.repository.base_repository import BaseRepository
from app.util.enums import GeofenceShapeType, GeofenceTypeUuid
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

    def read_all_alert_policies(self):
        with self.session_factory() as session:
            alerts = (
                session.query(self.model)
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

    def read_all_alert_policies_by_user(self, user_uuid: str):
        with self.session_factory() as session:
            alerts = (
                session.query(self.model)
                .filter(self.model.user_uuid == user_uuid)
                .options(joinedload(AlertPolicy.alert_policy_type))
                .options(joinedload(AlertPolicy.assets))
                .options(joinedload(AlertPolicy.alert_notification_types))
                .options(joinedload(AlertPolicy.maintenance_alert_type))
                .all()
            )
            return alerts

    def check_geofence_violation(self):
        with self.session_factory() as session:
            violations = []

            # get all geofence alert policies
            alert_policies = (
                session.query(AlertPolicy)
                .filter(
                    AlertPolicy.alert_policy_type_uuid
                    == GeofenceTypeUuid.GEOFENCE_ALERT_POLICY
                )
                .options(joinedload(AlertPolicy.assets))
                .options(joinedload(AlertPolicy.alert_recipients))
                .all()
            )

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
                    # return user

                    violations.append(
                        {
                            "asset": geofence_asset,
                            "violated_points": violated_asset_coordinates,
                            "alert_policy": alert_policy,
                            "alert_recipients": alert_recipients,
                        }
                    )

                    # return violations
                    # # If violation occurs, create AlertPolicyViolation instance and persist it
                    if violated_asset_coordinates:
                        violation = AlertPolicyViolation(
                            alert_policy_uuid=alert_policy.uuid,
                            asset_uuid=geofence_asset.uuid,
                            violation_coordinates=violated_asset_coordinates,
                        )
                        session.add(violation)
        session.commit()

        logging.info("Alert Notifications Sent")
        return {"message": "Notifications Sent", "violations": violations}
