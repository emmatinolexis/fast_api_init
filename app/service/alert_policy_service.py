from datetime import date, datetime
from typing import List, Optional

from app.core import messages
from app.core.exceptions import NotFoundError, UnAuthorizedError
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
    AlertPolicyUpdateInputPayload,
    AlertPolicyUpdatePayload,
    GeofenceAlertPolicyInput,
    GeofenceAlertPolicyPayload,
    GeofenceAlertPolicyUpdateInput,
    GeofenceAlertPolicyUpdatePayload,
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

    def get_all_alert_policies_by_user(
        self,
        user_uuid: str,
        page=1,
        page_size=10,
        policy_status: Optional[ActiveStatus] = None,
        policy_types: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        search: Optional[str] = None,
    ):
        try:
            return self.alert_policy_repository.read_all_alert_policies_by_user(
                user_uuid,
                page,
                page_size,
                policy_status,
                policy_types,
                start_date,
                end_date,
                search,
            )
        except Exception as e:
            raise e

    def get_all_alert_policies_by_business(
        self,
        business_uuid: str,
        page=1,
        page_size=10,
        policy_status: Optional[ActiveStatus] = None,
        policy_types: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        search: Optional[str] = None,
    ):
        try:
            return self.alert_policy_repository.read_all_alert_policies_by_business(
                business_uuid,
                page,
                page_size,
                policy_status,
                policy_types,
                start_date,
                end_date,
                search,
            )
        except Exception as e:
            raise e

    def get_all_alert_violations_by_user(
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
        try:
            return self.alert_policy_repository.read_all_alert_violations_by_user(
                user_uuid=user_uuid,
                page=page,
                page_size=page_size,
                policy_type=policy_type,
                policy_status=policy_status,
                start_date=start_date,
                end_date=end_date,
                search=search,
            )
        except Exception as e:
            raise e

    def get_all_alert_reminders(self, user_uuid: str):
        try:
            return self.alert_policy_repository.get_all_alert_reminders(user_uuid)
        except Exception as e:
            raise e

    def get_all_alert_violations_by_business(
        self,
        business_uuid: str,
        page=1,
        page_size=10,
        policy_status: str = None,
        policy_types: list = None,
        start_date: date = None,
        end_date: date = None,
        search: str = None,
    ):
        try:
            return self.alert_policy_repository.read_all_alert_violations_by_business(
                business_uuid,
                page,
                page_size,
                policy_status,
                policy_types,
                start_date,
                end_date,
                search,
            )
        except Exception as e:
            raise e

    def toggle_alert_status(self, alert_uuid: str):
        try:
            return self.alert_policy_repository.toggle_alert_status(alert_uuid)
        except Exception as e:
            raise e

    def toggle_maintenance_status(self, alert_uuid: str, date: str):
        try:
            if date:
                date = datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d")

            return self.alert_policy_repository.toggle_maintenance_alert_status(
                alert_uuid, date
            )
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
            self.assign_alert_recipients(
                alert_policy.alert_recipients, created_policy.uuid
            )
            self.assign_alert_types(alert_policy.alert_types, created_policy.uuid)
            self.assign_alert_assets(alert_policy.alert_assets, created_policy.uuid)

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
            self.assign_alert_recipients(
                alert_policy.alert_recipients, created_policy.uuid
            )
            self.assign_alert_types(alert_policy.alert_types, created_policy.uuid)
            self.assign_alert_assets(alert_policy.alert_assets, created_policy.uuid)
            return created_policy
        except Exception as e:
            raise e

    def update_geofence_alert_policy(
        self, alert_policy: GeofenceAlertPolicyUpdatePayload, alert_policy_uuid: str
    ):
        try:
            # validate alert policy
            self.check_if_alert_policy_exist(alert_policy_uuid)

            # update geofence_alert_notifications types
            if alert_policy.alert_types:
                self.remove_existing_alert_notification_types(alert_policy_uuid)
                self.assign_alert_types(alert_policy.alert_types, alert_policy_uuid)

            # update geofence alert recipients
            if alert_policy.alert_recipients:
                self.remove_existing_alert_recipients(alert_policy_uuid)
                self.assign_alert_recipients(
                    alert_policy.alert_recipients, alert_policy_uuid
                )

            # update geofence parameters
            return self.update_alert_geofence_policy(alert_policy, alert_policy_uuid)

        except Exception as e:
            raise e

    def remove_existing_alert_notification_types(self, alert_policy_uuid):
        try:
            self.alert_policy_notification_type_assignment_repository.delete_by_notification_type_by_policy_uuid(
                alert_policy_uuid
            )
        except Exception as e:
            raise e

    def remove_existing_alert_recipients(self, alert_policy_uuid):
        try:
            self.alert_notification_assignment_repository.delete_recipient_by_policy_uuid(
                alert_policy_uuid
            )
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

    def check_if_alert_policy_exist(self, alert_policy_uuid):
        if self.alert_policy_repository.read_by_uuid(alert_policy_uuid) is None:
            raise Exception("Alert policy not found")

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

    def update_alert_geofence_policy(self, alert_policy, alert_policy_uuid):
        if alert_policy.geofence_shape_type:
            if alert_policy.geofence_shape_type == GeofenceShapeType.CIRCULAR:
                alert_policy_data = GeofenceAlertPolicyUpdateInput(
                    policy_name=alert_policy.policy_name,
                    geofence_location_name=alert_policy.geofence_location_name,
                    geofence_coordinate_data=alert_policy.circle_geofence_data,
                    geofence_shape_type=alert_policy.geofence_shape_type,
                )
            else:
                geofence_data_wkt = self.create_geofence_data_wkt(alert_policy)

                alert_policy_data = GeofenceAlertPolicyUpdateInput(
                    policy_name=alert_policy.policy_name,
                    geofence_location_name=alert_policy.geofence_location_name,
                    geofence_coordinate_data=geofence_data_wkt,
                    geofence_shape_type=alert_policy.geofence_shape_type,
                )

            return self.patch_by_uuid(alert_policy_uuid, alert_policy_data)

        alert_policy_data = GeofenceAlertPolicyUpdateInput(
            policy_name=alert_policy.policy_name,
            geofence_location_name=alert_policy.geofence_location_name,
        )
        return self.patch_by_uuid(alert_policy_uuid, alert_policy_data)

    def create_geofence_data_wkt(self, alert_policy):
        geofence_data_wkt = []
        if alert_policy.geofence_shape_type is not GeofenceShapeType.CIRCULAR:
            for coordinates in alert_policy.geofence_coordinate_data:
                latitude = coordinates.latitude
                longitude = coordinates.longitude
                point = {"latitude": latitude, "longitude": longitude}

                geofence_data_wkt.append(point)
        return geofence_data_wkt

    def assign_alert_recipients(self, alert_recipients, created_policy_uuid):
        for item in alert_recipients:
            alert_recipients_data = {
                "alert_policy_uuid": created_policy_uuid,
                "recipient": item,
            }
            self.alert_notification_assignment_repository.create(
                AlertNotificationAssignment(**alert_recipients_data)
            )

    def assign_alert_types(self, alert_types, created_policy_uuid):
        for item in alert_types:
            alert_types_data = {
                "alert_policy_uuid": created_policy_uuid,
                "alert_notification_type": item,
            }
            self.alert_policy_notification_type_assignment_repository.create(
                AlertPolicyNotificationTypeAssignment(**alert_types_data)
            )

    def update_alert_types(self, created_policy, alert_policy):
        for item in alert_policy.alert_types:
            # delete previous alert types
            self.alert_policy_type_repository.read_by_uuid(item)
            alert_types_data = {
                "alert_policy_uuid": created_policy.uuid,
                "alert_notification_type": item,
            }
            self.alert_policy_notification_type_assignment_repository.create(
                AlertPolicyNotificationTypeAssignment(**alert_types_data)
            )

    def assign_alert_assets(self, alert_assets, created_policy_uuid):
        for item in alert_assets:
            alert_assets_data = {
                "alert_policy_uuid": created_policy_uuid,
                "asset_uuid": item,
            }
            self.alert_policy_asset_assignment_repository.create(
                AlertPolicyAssetAssignment(**alert_assets_data)
            )

    def _get_alert_policy(self, alert_policy_uuid: str):
        return self.alert_policy_repository.read_by_uuid(
            alert_policy_uuid, eager=["alert_notification_types", "alert_recipients"]
        )

    def _update_alert_recipients(
        self, alert_policy_uuid: str, new_recipients: List[str]
    ):
        if new_recipients:
            existing_recipients = [
                recipient.recipient
                for recipient in self.alert_notification_assignment_repository.read_all_by_alert_policy_uuid(
                    alert_policy_uuid
                )
            ]

            for recipient in new_recipients:
                if recipient not in existing_recipients:
                    alert_recipients_data = {
                        "alert_policy_uuid": alert_policy_uuid,
                        "recipient": recipient,
                    }
                    self.alert_notification_assignment_repository.create(
                        AlertNotificationAssignment(**alert_recipients_data)
                    )

            for recipient in existing_recipients:
                if recipient not in new_recipients:
                    self.alert_notification_assignment_repository.delete_by_recipient(
                        alert_policy_uuid, recipient
                    )

    def _update_alert_notification_types(
        self, alert_policy_uuid: str, new_notification_types: List[str]
    ):
        if new_notification_types:
            existing_notification_types = [
                notification.alert_notification_type
                for notification in self.alert_policy_notification_type_assignment_repository.read_all_by_alert_policy_uuid(
                    alert_policy_uuid
                )
            ]

            for notification_type in new_notification_types:
                if notification_type not in existing_notification_types:
                    alert_types_data = {
                        "alert_policy_uuid": alert_policy_uuid,
                        "alert_notification_type": notification_type,
                    }
                    self.alert_policy_notification_type_assignment_repository.create(
                        AlertPolicyNotificationTypeAssignment(**alert_types_data)
                    )

            for notification_type in existing_notification_types:
                if notification_type not in new_notification_types:
                    self.alert_policy_notification_type_assignment_repository.delete_by_notification_type(
                        alert_policy_uuid, notification_type
                    )

    def _update_alert_assets(self, alert_policy_uuid: str, new_assets: List[str]):
        if new_assets:
            existing_assets = [
                asset.uuid
                for asset in self.alert_policy_asset_assignment_repository.read_all_by_alert_policy_uuid(
                    alert_policy_uuid
                )
            ]

            for asset in new_assets:
                if asset not in existing_assets:
                    alert_assets_data = {
                        "alert_policy_uuid": alert_policy_uuid,
                        "asset_uuid": asset,
                    }
                    self.alert_policy_asset_assignment_repository.create(
                        AlertPolicyAssetAssignment(**alert_assets_data)
                    )

            for asset in existing_assets:
                if asset not in new_assets:
                    self.alert_policy_asset_assignment_repository.delete_by_asset(
                        alert_policy_uuid, asset
                    )

    def _update_policy(self, alert_policy_uuid: str, alert_policy):
        input_data = AlertPolicyUpdateInputPayload(
            policy_name=alert_policy.policy_name,
            minimum_idle_time=alert_policy.minimum_idle_time,
            maximum_speed_limit=alert_policy.maximum_speed_limit,
            maintenance_alert_schedule=alert_policy.maintenance_alert_schedule,
        )

        self.alert_policy_repository.update_by_uuid(alert_policy_uuid, input_data)

    def update_alert_policy(
        self, alert_policy_uuid: str, payload: AlertPolicyUpdatePayload
    ):
        try:
            alert_policy = self._get_alert_policy(alert_policy_uuid)
            if not alert_policy:
                raise NotFoundError(messages.ALERT_POLICY_NOT_FOUND + alert_policy_uuid)

            self._update_alert_recipients(alert_policy_uuid, payload.alert_recipients)
            self._update_alert_notification_types(
                alert_policy_uuid, payload.alert_notification_types
            )
            self._update_alert_assets(alert_policy_uuid, payload.alert_assets)
            self._update_policy(alert_policy_uuid, payload)

            policy = self.alert_policy_repository.read_by_uuid(alert_policy_uuid)
            return alert_policy_transformer(policy)
        except Exception as e:
            raise e

    def delete_alert_policy(
        self,
        alert_policy_uuid: str,
        user_uuid: str = None,
        business_profile_uuid: str = None,
    ):
        try:
            alert_policy = self.alert_policy_repository.read_by_uuid(alert_policy_uuid)
            if not alert_policy:
                raise NotFoundError(messages.ALERT_POLICY_NOT_FOUND + alert_policy_uuid)

            if user_uuid and alert_policy.user_uuid != user_uuid:
                raise UnAuthorizedError(messages.ACTION_NOT_ALLOWED)

            if (
                business_profile_uuid
                and alert_policy.business_profile_uuid != business_profile_uuid
            ):
                raise UnAuthorizedError(messages.ACTION_NOT_ALLOWED)

            self.alert_policy_repository.delete_by_uuid(alert_policy_uuid)
        except Exception as e:
            raise e
