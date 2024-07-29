from enum import Enum
from typing import Dict, List
from uuid import UUID

from app.core.constants import ADMIN_USER_ROLE, CUSTOMER_USER_ROLE, THIRD_PARTY_APP_ROLE


class AccountType(str, Enum):
    BUSINESS = "business"
    INDIVIDUAL = "individual"
    ADMIN = ("admin",)
    POLICE = ("police",)
    DVLA = "dvla"


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


class GasCylinderMaterialType(str, Enum):
    FIBER = "fiber"
    METAL = "metal"


class DeviceStatus(str, Enum):
    ASSIGNED = "assigned"
    NOT_ASSIGNED = "not_assigned"


class ServiceStatus(str, Enum):
    SERVICED = "serviced"
    NOT_SERVICED = "not_serviced"


class FineStatus(str, Enum):
    PENDING_PAYMENT = "pending_payment"
    PAID = "paid"
    PAYMENT_OVERDUE = "payment_overdue"


class FineType(str, Enum):
    OVER_SPEEDING = "over_speeding"


class CustomerRoles(str, Enum):
    ADMIN = UUID("7d720dbf-f90f-462d-ada2-8fbf0bfba56b")


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
    IDLING_ALERT_POLICY = "1c879d95-13a7-4331-a952-31b6397ae206"
    MAINTENANCE_ALERT_POLICY = "98e1b367-1965-457e-8087-52b453534096"


class GeofenceShapeType(str, Enum):
    CIRCULAR = "circular"
    POLYGON = "polygon"
    RECTANGLE = "rectangle"


class AlertType(str, Enum):
    SMS = "sms"
    EMAIL = "email"
    VOICE = "voice"


class SmartReportType(str, Enum):
    FLEET_OVERVIEW = "fleet_overview"
    COST_ANALYSIS = "cost_analysis"
    FLEET_PERFORMANCE = "fleet_performance"


class ImmobilizerType(str, Enum):
    OFF = "off"
    ON = "on"


class ImmobilizerReason(str, Enum):
    STOLEN = "stolen"
    UNAUTHORIZED = "unauthorized"
    FAULTY = "faulty"
    PERSONAL = "personal"


class DriverType(str, Enum):
    RIDER = "rider"
    DRIVER = "driver"


class RoleType(str, Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"


class IncidentType(str, Enum):
    THEFT = "theft"


class IncidentStatus(str, Enum):
    RESOLVED = "resolved"
    UNRESOLVED = "unresolved"


class OrderStatusRtd(str, Enum):
    IN_DELIVERY = "in_delivery"
    DELIVERED = "delivered"


class OrderStatus(str, Enum):
    PROCESSING = "processing"
    READY_FOR_PICKUP = "ready_for_pickup"
    IN_DELIVERY = "in_delivery"
    DELIVERED = "delivered"


class OrderPickUpLocation(str, Enum):
    name = "MVI Tracking"
    email = "emmanuel.osabutey@sagemicrosystems.net"
    phone = "0541557459"
    lat: float = 5.7229375
    lng: float = -0.1680625


class MaintenanceAlertSchedule(str, Enum):
    THIRTY_DAYS = "30"
    SIXTY_DAYS = "60"
    NINETY_DAYS = "90"


class AssetStatus(str, Enum):
    PENDING_INSTALLATION = "pending_installation"
    STOP = "stop"
    IDDLE = "iddle"
    MOVING = "moving"
    ACTIVE = "active"
    INACTIVE = "inactive"
    OFFLINE = "offline"


class AssetCreators(str, Enum):
    USER = "user"
    DVLA = "dvla"


class AssetUsageType(str, Enum):
    INDIVIDUAL = "individual"
    COMMERCIAL = "commercial"


class UserRole(str, Enum):
    CUSTOMER = CUSTOMER_USER_ROLE
    ADMIN = ADMIN_USER_ROLE
    THIRD_PARTY_APP = THIRD_PARTY_APP_ROLE


class EventStatus(str, Enum):
    START_MOVING = "Start_Moving"
    STOP_MOVING = "Stop_Moving"
    IDLING_ALARM = "Idling_Alarm"
    IGNITION_OFF = "Ignition_off"
    TIME_INTERVAL_TRACKING = "Time_Interval_Tracking"


class InvitationStatus(str, Enum):
    PENDING = "Pending"
    EXPIRED = "Expired"
    ACCEPTED = "Accepted"


class AssetDeviceRequestStatus(str, Enum):
    PENDING = "Pending"
    PROCESSING = "Processing"


class EmailPurpose(str, Enum):
    EMAIL_VERIFICATION = "Verify_Token"
    EMAIL_OTP = "OTP"
    ALERT_VIOLATION = "Alert_Violation"
    INVITATION = "Invitation"
    PASSWORD_RESET = "Password_Reset"
    ACCOUNT_VERIFICATION = "Account_Verification"
    MAINTENANCE_ALERT = "Maintenance_Alert"


class FileFormat(str, Enum):
    PDF = "pdf"
    PNG = "png"
    JPEG = "jpeg"
    JPG = "jpg"
    CSV = "csv"


class AlertPolicy(str, Enum):
    OIL_CHANGE = "7eb7e36d-e3ef-4f7d-9d43-afaca468c15a"
    GENERAL_SERVICING = "84db7dc6-31e2-4f18-a956-bd3e1fe549ff"
    TIRE_ROTATION = "a09c4122-c84a-4f9b-9c5c-19d0fc0747fd"
    BRAKE_INSPECTION = "09c74ec5-1de6-4417-aacf-3f3431ba8a63"
    OTHER = "e50fded1-b383-46bc-ba14-41bc51a3683e"
