from enum import Enum

from app.core.constants import ADMIN_USER_ROLE, CUSTOMER_USER_ROLE


class AccountType(str, Enum):
    BUSINESS = "business"
    INDIVIDUAL = "individual"


class ActiveStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


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
