from enum import Enum


class AccountType(str, Enum):
    BUSINESS = "business"
    INDIVIDUAL = "individual"


class ActiveInactive(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class GeofenceType(str, Enum):
    ZONE_EXIT = "zone_exit"
    ZONE_ENTRY = "zone_entry"

class AlertType(str, Enum):
    SMS = "sms"
    EMAIL = "email"
    VOICE = "voice"