from enum import Enum
from typing import Dict, List

from app.core.constants import ADMIN_USER_ROLE, CUSTOMER_USER_ROLE


class AccountType(str, Enum):
    BUSINESS = "business"
    INDIVIDUAL = "individual"
    ADMIN = "admin"


class DeviceType(str, Enum):
    TRACKING_DEVICE = "tracking_device"
    DASHCAM = "dashcam"


class FreePlan(str, Enum):
    PLAN_NAME = "Free Plan"
    DESCRIPTION = "This is the free plan"
    PACKAGE_ITEMS = [
        {
            "uuid": "6de8b328-9ff1-456a-a737-1fd6fef81063",
            "item_name": "Basic Tracking",
        },
        {
            "uuid": "6ccf4874-678c-4550-9bc7-92b4b04bea37",
            "item_name": "One Asset",
        },
        {
            "uuid": "7e753dc9-8178-4c01-bbd4-883e5689e135",
            "item_name": "One User",
        },
    ]

    @classmethod
    def get_package_items(cls) -> List[Dict[str, str]]:
        return cls.PACKAGE_ITEMS


class ActiveStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEACTIVATED = "deactivated"


class PackageItemTrackerType(str, Enum):
    ASSET_QUANTITY_TRACKER = "asset_quantity_tracker"
    NUMBER_OF_USER_TRACKER = "number_of_user_tracker"


class PaymentTypes(str, Enum):
    SUBSCRIPTION_PAYMENT = ("subscription_payment",)
    SUBSCRIPTION_UPGRADE_PAYMENT = "subscription_upgrade_payment"


class PaymentStatus(str, Enum):
    SUCCESS = "success"
    PENDING = "pending"
    FAILED = "failed"


class SubscriptionTypes(str, Enum):
    INDIVIDUAL_PACKAGE_SUBSCRIPTION = "individual_package_subscription"
    BUSINESS_PACKAGE_SUBSCRIPTION = "business_package_subscription"


class SubscriptionPeriod(str, Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"


class ContactSaleStatus(str, Enum):
    ATTENDED = "attended"
    NOT_ATTENDED = "not_attended"


class GeofenceType(str, Enum):
    ZONE_EXIT = "zone_exit"
    ZONE_ENTRY = "zone_entry"


class GeofenceTypeUuid(str, Enum):
    GEOFENCE_ALERT_POLICY = "f45e61d1-7113-40c4-8d11-d997fd0aa937"
    OVER_SPEEDING_ALERT_POLICY = "b4a7e52e-08b6-49e3-a99d-b4c1256de73b"
    IDLING_ALERT_POLICY = ("1c879d95-13a7-4331-a952-31b6397ae206",)
    MAINTENANCE_ALERT_POLICY = "98e1b367-1965-457e-8087-52b453534096"


class GeofenceShapeType(str, Enum):
    CIRCULAR = "circular"
    POLYGON = "polygon"
    RECTANGLE = "rectangle"


class AlertType(str, Enum):
    SMS = "sms"
    EMAIL = "email"
    VOICE = "voice"


class MaintenanceAlertSchedule(str, Enum):
    THIRTY_DAYS = "30 days"
    SIXTY_DAYS = "60 days"
    NINETY_DAYS = "90 days"


class AssetStatus(str, Enum):
    PENDING_INSTALLATION = "pending_installation"
    STOP = "stop"
    IDDLE = "iddle"
    MOVING = "moving"
    ACTIVE = "active"
    INACTIVE = "inactive"
    OFFLINE = "offline"


class UserRole(str, Enum):
    CUSTOMER = CUSTOMER_USER_ROLE
    ADMIN = ADMIN_USER_ROLE


class EventStatus(str, Enum):
    START_MOVING = "Start_Moving"
    STOP_MOVING = "Stop_Moving"
    IDLING_ALARM = "Idling_Alarm"
    IGNITION_OFF = "Ignition_off"
    TIME_INTERVAL_TRACKING = "Time_Interval_Tracking"


class InvitationStatus(str, Enum):
    PENDING = "Pending"
    EXPIRED = "Expired"


class AssetDeviceRequestStatus(str, Enum):
    PENDING = "Pending"
    PROCESSING = "Processing"


class EmailPurpose(str, Enum):
    EMAIL_VERIFICATION = "Verify_Token"
    EMAIL_OTP = "OTP"
    ALERT_VIOLATION = "Alert_Violation"
    INVITATION = "Invitation"
    PASSWORD_RESET = "Password_Reset"
