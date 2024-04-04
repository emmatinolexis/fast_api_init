# USER ROLE CONSTANTS
CUSTOMER_USER_ROLE = "customer"
ADMIN_USER_ROLE = "admin"
ALLOWED_EVENT_TYPES = [
    "Stop_Moving",
    "Start_Moving",
    "Idling_Alarm",
    "Ignition_Off",
    "Time_Interval_Tracking",
    "Time_Interval_Tracking_Moving",
    "Time_Interval_Tracking_Stopped",
    "Time_Interval_Tracking_Idling",
]

# DEVICE UNITS
SPEED_UNIT = "KPH"
DISTANCE_UNIT = "KM"

FREE_PACKAGE = "Free Package"

FREE_PACKAGE_ITEMS = [
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
