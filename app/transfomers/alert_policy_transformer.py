from app.model.alert_notification_assignment import AlertNotificationAssignment
from app.model.alert_polcy_notification_type_assignment import (
    AlertPolicyNotificationTypeAssignment,
)
from app.model.alert_policy import AlertPolicy


def alert_notification_assignment_transformer(
    assignment: AlertNotificationAssignment,
) -> dict:
    return {
        "uuid": assignment.uuid,
        "recipient": assignment.recipient,
    }


def alert_policy_notification_type_assignment_transformer(
    assignment: AlertPolicyNotificationTypeAssignment,
) -> dict:
    return {
        "uuid": str(assignment.uuid),
        "alert_notification_type": assignment.alert_notification_type,
    }


def alert_policy_transformer(policy: AlertPolicy) -> dict:
    return {
        "uuid": str(policy.uuid),
        "policy_name": policy.policy_name,
        "alert_policy_type_uuid": str(policy.alert_policy_type_uuid),
        "geofence_location_name": policy.geofence_location_name,
        "geofence_type": policy.geofence_type.name if policy.geofence_type else None,
        "geofence_shape_type": policy.geofence_shape_type.name
        if policy.geofence_shape_type
        else None,
        "geofence_coordinate_data": policy.geofence_coordinate_data,
        "user_uuid": str(policy.user_uuid),
        "business_profile_uuid": str(policy.business_profile_uuid)
        if policy.business_profile_uuid
        else None,
        "minimum_idle_time": policy.minimum_idle_time,
        "maximum_speed_limit": policy.maximum_speed_limit,
        "status": policy.status,
        "maintenance_alert_schedule": policy.maintenance_alert_schedule,
        "created_at": policy.created_at.isoformat() if policy.created_at else None,
        "updated_at": policy.updated_at.isoformat() if policy.updated_at else None,
    }
