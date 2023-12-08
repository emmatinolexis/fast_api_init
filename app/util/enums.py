from enum import Enum


class AccountType(str, Enum):
    BUSINESS = "business"
    INDIVIDUAL = "individual"


class ActiveInactive(str, Enum):
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
    IDDLE = "iddle"
    STOP = "stop"
    MOVING = "moving"
    ACTIVE = "active"
    INACTIVE = "inactive"