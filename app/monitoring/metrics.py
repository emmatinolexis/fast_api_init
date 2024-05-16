from prometheus_client import Counter

MSG_RECEIVED_TOTAL = Counter(
    "mqtt_msg_received_total",
    "Total count of received messages from MQTT.",
    ["device_type", "success"],
)
