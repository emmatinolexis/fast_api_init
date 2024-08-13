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
    AlertPolicyUpdatePayload,
    GeofenceAlertPolicyInput,
    GeofenceAlertPolicyPayload,
)
from app.service.base_service import BaseService
from app.transfomers.alert_policy_transformer import alert_policy_transformer
from app.util.enums import ActiveStatus, GeofenceShapeType


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

    def get_all_alert_policies(self, page=1, page_size=10):
        try:
            return self.alert_policy_repository.read_all_alert_policies(page, page_size)
        except Exception as e:
            raise e

    def get_all_alert_policies_by_user(self, user_uuid: str, page=1, page_size=10):
        try:
            return self.alert_policy_repository.read_all_alert_policies_by_user(
                user_uuid, page, page_size
            )
        except Exception as e:
            raise e

    def get_all_alert_policies_by_business(
        self, business_uuid: str, page=1, page_size=10
    ):
        try:
            return self.alert_policy_repository.read_all_alert_policies_by_business(
                business_uuid, page, page_size
            )
        except Exception as e:
            raise e

    def get_all_alert_violations_by_user(self, user_uuid: str, page=1, page_size=10):
        try:
            return self.alert_policy_repository.read_all_alert_violations_by_user(
                user_uuid, page, page_size
            )
        except Exception as e:
            raise e

    def get_all_alert_violations_by_business(
        self, business_uuid: str, page=1, page_size=10
    ):
        try:
            return self.alert_policy_repository.read_all_alert_violations_by_business(
                business_uuid, page, page_size
            )
        except Exception as e:
            raise e

    def toggle_alert_status(self, alert_uuid: str):
        try:
            return self.alert_policy_repository.toggle_alert_status(alert_uuid)
        except Exception as e:
            raise e

    def toggle_alert_violation_status(self, alert_violation_uuid: str):
        try:
            return self.alert_policy_repository.toggle_alert_violation_status(
                alert_violation_uuid
            )
        except Exception as e:
            raise e

    def check_geofence_violation(self):
        try:
            return self.alert_policy_repository.check_geofence_violation()
        except Exception as e:
            raise e

    def check_over_speeding_violation(self):
        try:
            return self.alert_policy_repository.check_over_speeding_violation()
        except Exception as e:
            raise e

    def check_idling_violation(self):
        try:
            return self.alert_policy_repository.check_idling_violation()
        except Exception as e:
            raise e

    def check_maintenance(self):
        try:
            return self.alert_policy_repository.check_maintenance()
        except Exception as e:
            raise e

    def create_alert_policy(
        self,
        alert_policy: AlertPolicyPayload,
        user_uuid: str,
        business_uuid: str = None,
    ):
        try:
            self.validate_alert_policy(alert_policy)

            # create policy
            alert_policy_data = AlertPolicyInput(
                policy_name=alert_policy.policy_name,
                alert_policy_type_uuid=alert_policy.alert_policy_type_uuid,
                minimum_idle_time=alert_policy.minimum_idle_time,
                maintenance_alert_type_uuid=alert_policy.maintenance_alert_policy_type_uuid,
                maintenance_alert_schedule=alert_policy.maintenance_alert_schedule,
                maximum_speed_limit=alert_policy.maximum_speed_limit,
                user_uuid=user_uuid,
                business_profile_uuid=business_uuid,
                status=ActiveStatus.ACTIVE,
            )

            created_policy = self.add(alert_policy_data)

            # create alert recipients
            self.assign_alert_recipients(alert_policy, created_policy)

            # create alert types
            self.assign_alert_types(alert_policy, created_policy)

            # create alert assets
            self.assign_alert_assets(alert_policy, created_policy)

            return created_policy
        except Exception as e:
            raise e

    def create_geofence_alert_policy(
        self,
        alert_policy: GeofenceAlertPolicyPayload,
        user_uuid: str,
        business_uuid: str = None,
    ):
        try:
            self.validate_alert_policy(alert_policy)
            created_policy = self.create_alert_geofence_policy(
                alert_policy, user_uuid, business_uuid
            )
            self.assign_alert_recipients(alert_policy, created_policy)
            self.assign_alert_types(alert_policy, created_policy)
            self.assign_alert_assets(alert_policy, created_policy)
            return created_policy
        except Exception as e:
            raise e

    def validate_alert_policy(self, alert_policy):
        if (
            self.alert_policy_type_repository.read_by_uuid(
                alert_policy.alert_policy_type_uuid
            )
            is None
        ):
            raise Exception("Alert policy type not found")
        for item in alert_policy.alert_assets:
            if self.asset_repository.read_by_uuid(item) is None:
                msg = f"Asset: {item} not found"
                raise Exception(msg)

    def create_alert_geofence_policy(
        self, alert_policy, user_uuid: str, business_uuid: str = None
    ):
        if alert_policy.geofence_shape_type == GeofenceShapeType.CIRCULAR:
            alert_policy_data = GeofenceAlertPolicyInput(
                policy_name=alert_policy.policy_name,
                alert_policy_type_uuid=alert_policy.alert_policy_type_uuid,
                geofence_location_name=alert_policy.geofence_location_name,
                geofence_type=alert_policy.geofence_type,
                geofence_coordinate_data=alert_policy.circle_geofence_data,
                geofence_shape_type=alert_policy.geofence_shape_type,
                user_uuid=user_uuid,
                business_profile_uuid=business_uuid,
                status=ActiveStatus.ACTIVE,
            )
        else:
            geofence_data_wkt = self.create_geofence_data_wkt(alert_policy)

            alert_policy_data = GeofenceAlertPolicyInput(
                policy_name=alert_policy.policy_name,
                alert_policy_type_uuid=alert_policy.alert_policy_type_uuid,
                geofence_location_name=alert_policy.geofence_location_name,
                geofence_type=alert_policy.geofence_type,
                geofence_coordinate_data=geofence_data_wkt,
                geofence_shape_type=alert_policy.geofence_shape_type,
                user_uuid=user_uuid,
                business_profile_uuid=business_uuid,
                status=ActiveStatus.ACTIVE,
            )
        return self.add(alert_policy_data)

    def create_geofence_data_wkt(self, alert_policy):
        geofence_data_wkt = []
        if alert_policy.geofence_shape_type is not GeofenceShapeType.CIRCULAR:
            for coordinates in alert_policy.geofence_coordinate_data:
                latitude = coordinates.latitude
                longitude = coordinates.longitude
                point = {"latitude": latitude, "longitude": longitude}

                geofence_data_wkt.append(point)
        return geofence_data_wkt

    def assign_alert_recipients(self, alert_policy, created_policy):
        for item in alert_policy.alert_recipients:
            alert_recipients_data = {
                "alert_policy_uuid": created_policy.uuid,
                "recipient": item,
            }
            self.alert_notification_assignment_repository.create(
                AlertNotificationAssignment(**alert_recipients_data)
            )

    def assign_alert_types(self, alert_policy, created_policy):
        for item in alert_policy.alert_types:
            alert_types_data = {
                "alert_policy_uuid": created_policy.uuid,
                "alert_notification_type": item,
            }
            self.alert_policy_notification_type_assignment_repository.create(
                AlertPolicyNotificationTypeAssignment(**alert_types_data)
            )

    def assign_alert_assets(self, alert_policy, created_policy):
        for item in alert_policy.alert_assets:
            alert_assets_data = {
                "alert_policy_uuid": created_policy.uuid,
                "asset_uuid": item,
            }
            self.alert_policy_asset_assignment_repository.create(
                AlertPolicyAssetAssignment(**alert_assets_data)
            )

    def update_alert_policy(
        self, alert_policy_uuid: str, payload: AlertPolicyUpdatePayload
    ):
        try:
            alert_policy = self.alert_policy_repository.read_by_uuid(
                alert_policy_uuid,
                eager=["alert_notification_types", "alert_recipients"],
            )

            if not alert_policy:
                raise NotFoundError(messages.ALERT_POLICY_NOT_FOUND + alert_policy_uuid)

            if payload.alert_recipients:
                existing_recipients = [
                    recipient.recipient
                    for recipient in self.alert_notification_assignment_repository.read_all_by_alert_policy_uuid(
                        alert_policy_uuid
                    )
                ]

                for recipient in payload.alert_recipients:
                    if recipient not in existing_recipients:
                        alert_recipients_data = {
                            "alert_policy_uuid": alert_policy_uuid,
                            "recipient": recipient,
                        }
                        self.alert_notification_assignment_repository.create(
                            AlertNotificationAssignment(**alert_recipients_data)
                        )

                        # delete recipients that are not in the payload
                        for recipient in existing_recipients:
                            if recipient not in payload.alert_recipients:
                                self.alert_notification_assignment_repository.delete_by_recipient(
                                    alert_policy_uuid, recipient
                                )

            if payload.alert_notification_types:
                existing_notification_types = [
                    notification.alert_notification_type
                    for notification in self.alert_policy_notification_type_assignment_repository.read_all_by_alert_policy_uuid(
                        alert_policy_uuid
                    )
                ]

                for notification_type in payload.alert_notification_types:
                    if notification_type not in existing_notification_types:
                        alert_types_data = {
                            "alert_policy_uuid": alert_policy_uuid,
                            "alert_notification_type": notification_type,
                        }
                        self.alert_policy_notification_type_assignment_repository.create(
                            AlertPolicyNotificationTypeAssignment(**alert_types_data)
                        )

                        # delete notification types that are not in the payload
                        for notification_type in existing_notification_types:
                            if (
                                notification_type
                                not in payload.alert_notification_types
                            ):
                                self.alert_policy_notification_type_assignment_repository.delete_by_notification_type(
                                    alert_policy_uuid, notification_type
                                )

            if payload.alert_assets:
                existing_assets = [
                    asset.asset_uuid
                    for asset in self.alert_policy_asset_assignment_repository.read_all_by_alert_policy_uuid(
                        alert_policy_uuid
                    )
                ]

                for asset in payload.alert_assets:
                    if asset not in existing_assets:
                        alert_assets_data = {
                            "alert_policy_uuid": alert_policy_uuid,
                            "asset_uuid": asset,
                        }
                        self.alert_policy_asset_assignment_repository.create(
                            AlertPolicyAssetAssignment(**alert_assets_data)
                        )

                        # delete assets that are not in the payload
                        for asset in existing_assets:
                            if asset not in payload.alert_assets:
                                self.alert_policy_asset_assignment_repository.delete_by_asset(
                                    alert_policy_uuid, asset
                                )

            if payload.policy_name:
                self.alert_policy_repository.update_attr_by_uuid(
                    alert_policy_uuid, "policy_name", payload.policy_name
                )

            policy = self.alert_policy_repository.read_by_uuid(alert_policy_uuid)
            return alert_policy_transformer(policy)
        except Exception as e:
            raise e
