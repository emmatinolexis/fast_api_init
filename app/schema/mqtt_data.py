from pydantic import BaseModel


class MQTTDataPayload(BaseModel):
    device_type: str
    device_uuid: str
    device_imei: str
    event_type: str
    event_description: str = None
    event_datetime: str
    valid: bool = True
    latitude: float
    longitude: float
    satellite_quality: int = None
    hdop: float = None  # Horizontal Positioning Accuracy
    speed: float = None
    course: float = None
    altitude: float = None
    milleage: int = None  # Total distance traveled
    gsm_mcc: int = None  # Mobile Network Country Code
    gsm_mnc: int = None  # Mobile Network Code
    gsm_lac: str = None  # Mobile Network Location Area Code
    gsm_signal_strength: int = None
    gps_antenna_status: bool = False  # False - disconnected; True - connected
    stop_status: bool = False  # False - move; True - stop
    armed_status: bool = False  # False - disarmed; True - armed
    rfid_login_status: bool = False  # False - logout; True - login
    protocol_version: str
