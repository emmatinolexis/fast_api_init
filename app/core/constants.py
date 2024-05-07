# USER ROLE CONSTANTS

CUSTOMER_USER_ROLE = "customer"
ADMIN_USER_ROLE = "admin"
THIRD_PARTY_APP_ROLE = "third_party"
ENGINE_SHUTDOWN_USERNAME = "mviad"
ENGINE_SHUTDOWN_PASSWORD = "mvipa"


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

FREE_PACKAGE = "Free Plan"

FREE_PACKAGE_ITEMS = [
    {
        "uuid": "6de8b328-9ff1-456a-a737-1fd6fef81063",
        "package_item": {
            "item_name": "1 User(s)",
            "type": "number_of_user_tracker",
            "number_of_assets": "",
            "number_of_users": 1,
        },
    },
    {
        "uuid": "6ccf4874-678c-4550-9bc7-92b4b04bea37",
        "package_item": {
            "item_name": "One Asset(s)",
            "type": "asset_quantity_tracker",
            "number_of_assets": 1,
            "number_of_users": "",
        },
    },
    {
        "uuid": "7e753dc9-8178-4c01-bbd4-883e5689e135",
        "package_item": {
            "item_name": "Live Tracking",
            "type": "",
            "number_of_assets": "",
            "number_of_users": "",
        },
    },
]
