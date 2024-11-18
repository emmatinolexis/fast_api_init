from prometheus_client import Counter

MSG_RECEIVED_TOTAL = Counter(
    "mqtt_msg_received_total",
    "Total count of received messages from MQTT.",
    ["device_type", "success"],
)

LOGIN_USERS_TOTAL = Counter(
    "login_users_total",
    "Total number of logged in users",
    ["success"]
)

DEACTIVATED_ACCOUNT_TOTAL = Counter(
    "deactivated_account_total",
    "Total number of deactivated accounts",
    ["success"]
)

ASSET_CREATION_FAILED_TOTAL = Counter(
    "asset_creation_failed_total",
    "Total number of failed asset creations",
    ["success"]
)

USER_SIGNUP_FAILED_TOTAL = Counter(
    "user_signup_failed_total",
    "Total number of failed user sign ups",
    ["success"]
)
