from enum import Enum

from app.core.constants import ADMIN_USER_ROLE, CUSTOMER_USER_ROLE


class AccountType(str, Enum):
    BUSINESS = "business"
    INDIVIDUAL = "individual"


class InvitationStatus(str, Enum):
    PENDING = "Pending"
    EXPIRED = "Expired"
    ACCEPTED = "Accepted"


class EmailPurpose(str, Enum):
    EMAIL_VERIFICATION = "Verify_Token"
    EMAIL_OTP = "OTP"
    ALERT_VIOLATION = "Alert_Violation"
    INVITATION = "Invitation"
    PASSWORD_RESET = "Password_Reset"
    ACCOUNT_VERIFICATION = "Account_Verification"
    MAINTENANCE_ALERT = "Maintenance_Alert"
    SMART_REPORT_ALERT = "Smart_Report_Alert"
    PASSWORD_CHANGE = "Password_Change"
    DEVICE_ALERTS = "Device_Alerts"
    LICENSE_EXPIRY = "License_Expiry"


class ActiveStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEACTIVATED = "deactivated"


class PaymentStatus(str, Enum):
    SUCCESS = "success"
    PENDING = "pending"
    FAILED = "failed"


class SubscriptionStatus(str, Enum):
    NON_RENEWING = "non-renewing"
    PENDING = "pending"
    ATTENTION = "attention"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class SubscriptionTypes(str, Enum):
    INDIVIDUAL_PACKAGE_SUBSCRIPTION = "individual_package_subscription"
    BUSINESS_PACKAGE_SUBSCRIPTION = "business_package_subscription"


class SubscriptionPeriod(str, Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"


class SmartReportType(str, Enum):
    FLEET_OVERVIEW = "fleet_overview"
    COST_ANALYSIS = "cost_analysis"
    FLEET_PERFORMANCE = "fleet_performance"


class RoleType(str, Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"


class PermissionType(str, Enum):
    customer = "customer"
    admin = "admin"
    all = "all"


class IncidentType(str, Enum):
    THEFT = "theft"


class UserRole(str, Enum):
    CUSTOMER = CUSTOMER_USER_ROLE
    ADMIN = ADMIN_USER_ROLE


class FileFormat(str, Enum):
    PDF = "pdf"
    PNG = "png"
    JPEG = "jpeg"
    JPG = "jpg"
    CSV = "csv"
    JSON = "json"
    SQL = "sql"
