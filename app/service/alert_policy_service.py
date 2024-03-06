from app.core import messages
from app.core.exceptions import NotFoundError
from app.repository.alert_maintenance_type_repository import (
    AlertMaintenanceTypeRepository,
)
from app.repository.alert_notification_assignment_repository import (
    AlertNotificationAssignmentRepository,
)
from app.repository.alert_policy_asset_assignment_repository import (
    AlertPolicyAssetAssignmentRepository,
)
from app.repository.alert_policy_notification_type_assignment_repository import (
    AlertPolicyNotificationTypeAssignmentRepository,
)
from app.repository.alert_policy_repository import AlertPolicyRepository
from app.repository.alert_policy_type_repository import AlertPolicyTypeRepository
from app.repository.asset_repository import AssetRepository
from app.schema.alert_policy_schema import (
    AlertNotificationAssignment,
    AlertPolicyAssetAssignment,
    AlertPolicyInput,
    AlertPolicyNotificationTypeAssignment,
    AlertPolicyPayload,
    GeofenceAlertPolicyInput,
    GeofenceAlertPolicyPayload,
)
from app.service.base_service import BaseService


class AlertPolicyService(BaseService):
    def __init__(
        self,
        alert_policy_repository: AlertPolicyRepository,
        alert_policy_type_repository: AlertPolicyTypeRepository,
        alert_maintenance_type_repository: AlertMaintenanceTypeRepository,
        alert_notification_assignment_repository: AlertNotificationAssignmentRepository,
        alert_policy_notification_type_assignment_repository: AlertPolicyNotificationTypeAssignmentRepository,
        alert_policy_asset_assignment_repository: AlertPolicyAssetAssignmentRepository,
        asset_repository: AssetRepository,
    ):
        self.alert_policy_repository = alert_policy_repository
        self.alert_policy_type_repository = alert_policy_type_repository
        self.alert_maintenance_type_repository = alert_maintenance_type_repository
        self.alert_notification_assignment_repository = (
            alert_notification_assignment_repository
        )
        self.alert_policy_notification_type_assignment_repository = (
            alert_policy_notification_type_assignment_repository
        )
        self.alert_policy_asset_assignment_repository = (
            alert_policy_asset_assignment_repository
        )
        self.asset_repository = asset_repository
        super().__init__(alert_policy_repository)

    def get_all_alert_policies(self):
        try:
            return self.alert_policy_repository.read_all_alert_policies()
        except Exception as e:
            raise e

    def get_all_alert_policies_by_user(self, user_uuid: str):
        try:
            return self.alert_policy_repository.read_all_alert_policies_by_user(
                user_uuid
            )
        except Exception as e:
            raise e

    def create_alert_policy(self, alert_policy: AlertPolicyPayload, user_uuid: str):
        try:
            # create policy
            alert_policy_data = AlertPolicyInput(
                policy_name=alert_policy.policy_name,
                alert_policy_type_uuid=alert_policy.alert_policy_type_uuid,
                geofence_location_name=alert_policy.geofence_location_name,
                geofence_type=alert_policy.geofence_type,
                minimum_idle_time=alert_policy.minimum_idle_time,
                maintenance_alert_type_uuid=alert_policy.maintenance_alert_policy_type_uuid,
                maintenance_alert_schedule=alert_policy.maintenance_alert_schedule,
                user_uuid=user_uuid,
            )

            if (
                self.alert_policy_type_repository.read_by_uuid(
                    alert_policy.alert_policy_type_uuid
                )
                is None
            ):
                raise NotFoundError(
                    detail=messages.ALERT_POLICY_TYPE_NOT_FOUND
                    + str(alert_policy.alert_policy_type_uuid)
                )

            for item in alert_policy.alert_assets:
                if self.asset_repository.read_by_uuid(item) is None:
                    raise NotFoundError(detail=messages.ASSET_NOT_FOUND + str(item))

            created_policy = self.add(alert_policy_data)

            # create alert recipients
            for item in alert_policy.alert_reciepients:
                alert_recipients_data = {
                    "alert_policy_uuid": created_policy.uuid,
                    "recipient": item,
                }
                self.alert_notification_assignment_repository.create(
                    AlertNotificationAssignment(**alert_recipients_data)
                )

            # create alert types
            for item in alert_policy.alert_types:
                alert_types_data = {
                    "alert_policy_uuid": created_policy.uuid,
                    "alert_notification_type": item,
                }
                self.alert_policy_notification_type_assignment_repository.create(
                    AlertPolicyNotificationTypeAssignment(**alert_types_data)
                )

            # create alert assets
            for item in alert_policy.alert_assets:
                alert_assets_data = {
                    "alert_policy_uuid": created_policy.uuid,
                    "asset_uuid": item,
                }
                self.alert_policy_asset_assignment_repository.create(
                    AlertPolicyAssetAssignment(**alert_assets_data)
                )

            return alert_policy_data
        except Exception as e:
            raise e

    def create_geofence_alert_policy(
        self, alert_policy: GeofenceAlertPolicyPayload, user_uuid
    ):
        try:
            geofence_data_wkt = []

            for coordinates in alert_policy.geofence_data:
                latitude = coordinates.latitude
                longitude = coordinates.longitude
                point = {"latitude": latitude, "longitude": longitude}

                geofence_data_wkt.append(point)

            # create policy
            alert_policy_data = GeofenceAlertPolicyInput(
                policy_name=alert_policy.policy_name,
                alert_policy_type_uuid=alert_policy.alert_policy_type_uuid,
                geofence_location_name=alert_policy.geofence_location_name,
                geofence_type=alert_policy.geofence_type,
                geofence_data=geofence_data_wkt,
                user_uuid=user_uuid,
            )

            if (
                self.alert_policy_type_repository.read_by_uuid(
                    alert_policy.alert_policy_type_uuid
                )
                is None
            ):
                raise NotFoundError(
                    detail=messages.ALERT_POLICY_TYPE_NOT_FOUND
                    + str(alert_policy.alert_policy_type_uuid)
                )

            # assign assets
            for item in alert_policy.alert_assets:
                if self.asset_repository.read_by_uuid(item) is None:
                    raise NotFoundError(detail=messages.ASSET_NOT_FOUND + str(item))

            created_policy = self.add(alert_policy_data)

            # create alert reciepients
            for item in alert_policy.alert_recipients:
                alert_recipients_data = {
                    "alert_policy_uuid": created_policy.uuid,
                    "recipient": item,
                }
                self.alert_notification_assignment_repository.create(
                    AlertNotificationAssignment(**alert_recipients_data)
                )

            # create alert types
            for item in alert_policy.alert_types:
                alert_types_data = {
                    "alert_policy_uuid": created_policy.uuid,
                    "alert_notification_type": item,
                }
                self.alert_policy_notification_type_assignment_repository.create(
                    AlertPolicyNotificationTypeAssignment(**alert_types_data)
                )

            # create alert assets
            for item in alert_policy.alert_assets:
                alert_assets_data = {
                    "alert_policy_uuid": created_policy.uuid,
                    "asset_uuid": item,
                }
                self.alert_policy_asset_assignment_repository.create(
                    AlertPolicyAssetAssignment(**alert_assets_data)
                )

            return alert_policy_data
        except Exception as e:
            raise e
