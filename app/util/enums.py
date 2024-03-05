from enum import Enum

from app.core.constants import ADMIN_USER_ROLE, CUSTOMER_USER_ROLE


class AccountType(str, Enum):
    BUSINESS = "business"
    INDIVIDUAL = "individual"
    ADMIN = "admin"


class ActiveStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEACTIVATED = "deactivated"


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
