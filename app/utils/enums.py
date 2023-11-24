from enum import Enum


class AccountType(str, Enum):
    BUSINESS = "business"
    INDIVIDUAL = "individual"


class ActiveInactive(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class TrueOrFals(str, Enum):
    TRUE = "True"
    FALSE = "False"
