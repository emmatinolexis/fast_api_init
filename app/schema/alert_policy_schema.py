from typing import List, Optional, Union
from uuid import UUID

from pydantic import BaseModel

from app.util.enums import (
    ActiveStatus,
    AlertType,
    GeofenceShapeType,
    GeofenceType,
    MaintenanceAlertSchedule,
)


class AlertPolicyTypePayload(BaseModel):
    name: str
    description: str
    status: ActiveStatus


class AlertRecipient(BaseModel):
    phone_number: str
    alert_policy_uuids: list[UUID]


class AlertPolicyAsset(BaseModel):
    asset_uuids: list[UUID]
    alert_policy_uuid: UUID


class AlertPolicyPayload(BaseModel):
    policy_name: str
    alert_policy_type_uuid: UUID
    alert_types: list[AlertType]
    alert_recipients: list[str] = []
    alert_assets: list[UUID]
    minimum_idle_time: Optional[str] = None
    maximum_speed_limit: Optional[str] = None
    maintenance_alert_policy_type_uuid: Optional[UUID] = None
    maintenance_alert_schedule: Optional[MaintenanceAlertSchedule] = None


class AlertPolicyUpdatePayload(BaseModel):
    policy_name: Optional[str] = None
    alert_notification_types: Optional[list[str]] = None
    alert_recipients: Optional[list[str]] = None
    alert_assets: Optional[list[UUID]] = None
    minimum_idle_time: Optional[str] = None
    maximum_speed_limit: Optional[str] = None
    maintenance_alert_schedule: Optional[MaintenanceAlertSchedule] = None


class AlertPolicyUpdateInputPayload(BaseModel):
    policy_name: Optional[str] = None
    minimum_idle_time: Optional[str] = None
    maximum_speed_limit: Optional[str] = None
    maintenance_alert_schedule: Optional[MaintenanceAlertSchedule] = None


class AlertPolicyInput(BaseModel):
    policy_name: str
    alert_policy_type_uuid: UUID
    geofence_location_name: Optional[str] = None
    geofence_type: Optional[GeofenceType] = None
    minimum_idle_time: Optional[str] = None
    maximum_speed_limit: Optional[str] = None
    maintenance_alert_type_uuid: Optional[UUID] = None
    maintenance_alert_schedule: Optional[MaintenanceAlertSchedule] = None
    user_uuid: UUID
    business_profile_uuid: UUID
    status: str


class AlertPolicyNotification(BaseModel):
    alert_policy_uuid: UUID
    alert_notification_type: str


class AlertNotificationAssignment(BaseModel):
    alert_policy_uuid: UUID
    recipient: str


class AlertPolicyNotificationTypeAssignment(BaseModel):
    alert_policy_uuid: UUID
    alert_notification_type: str


class AlertPolicyAssetAssignment(BaseModel):
    alert_policy_uuid: UUID
    asset_uuid: UUID


class AlertPolicyFetch(BaseModel):
    policy_name: str
    alert_types: list[str]
    alert_reciepients: list[str]
    alert_assets: list[str]
    geofence_location_name: str
    geofence_type: str
    minimum_idle_time: str


class Coordinates(BaseModel):
    latitude: float
    longitude: float


class CircleGeofence(BaseModel):
    radius: float
    center_point: Coordinates


class GeofenceAlertPolicyPayload(BaseModel):
    policy_name: str
    alert_policy_type_uuid: UUID
    alert_types: list[AlertType]
    alert_recipients: list[str] = []
    alert_assets: list[UUID]
    geofence_location_name: Optional[str] = None
    geofence_type: GeofenceType
    geofence_shape_type: GeofenceShapeType
    geofence_coordinate_data: Optional[list[Coordinates]] = None
    circle_geofence_data: Optional[CircleGeofence] = None


class GeofenceAlertPolicyUpdatePayload(BaseModel):
    policy_name: Optional[str] = None
    alert_types: Optional[list[AlertType]] = None
    alert_recipients: Optional[list[str]] = []
    geofence_location_name: Optional[str] = None
    geofence_shape_type: Optional[GeofenceShapeType] = None
    geofence_coordinate_data: Optional[list[Coordinates]] = None
    circle_geofence_data: Optional[CircleGeofence] = None


class GeofenceAlertPolicyInput(BaseModel):
    policy_name: str
    alert_policy_type_uuid: UUID
    geofence_location_name: Optional[str] = None
    geofence_type: Optional[GeofenceType] = None
    geofence_coordinate_data: Union[List[Coordinates], CircleGeofence]
    geofence_shape_type: GeofenceShapeType
    user_uuid: UUID
    business_profile_uuid: UUID
    status: str


class GeofenceAlertPolicyUpdateInput(BaseModel):
    policy_name: Optional[str] = None
    geofence_location_name: Optional[str] = None
    geofence_type: Optional[GeofenceType] = None
    geofence_coordinate_data: Optional[Union[List[Coordinates], CircleGeofence]] = None
    geofence_shape_type: Optional[GeofenceShapeType] = None
