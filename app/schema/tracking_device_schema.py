from typing import List, Union

from pydantic import BaseModel


class TrackingDeviceCreate(BaseModel):
    data: Union[str, dict]


class MeasurementPayload(BaseModel):
    q: str
    v: str
    t: str
    u: str


class MeasurementPayloadInput(BaseModel):
    quantity: str
    value: str
    type: str
    unit: str


class DeviceReportPayload(BaseModel):
    node_id: str
    gtwy: str
    alert_type: str
    dev_type: str
    has_alert: bool = False
    alert_desc: str
    dataset: List[MeasurementPayload]
    event_datetime: str


class DeviceReportPayloadInput(BaseModel):
    node_id: str
    gateway_id: str
    alert_type: str
    device_type: str
    requires_attention: bool = False
    alert_description: str
    measurements: List[MeasurementPayloadInput]
    event_datetime: str

    # @root_validator(pre=True)
    # def convert_timestamp(cls, values):
    #     # Convert the timestamp string to a datetime object in the desired format
    #     if "event_datetime" in values:
    #         try:
    #             unix_timestamp = float(values["event_datetime"])
    #             dt = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
    #             # Format to '2024-07-23 11:02:21.573 +0000'
    #             formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + " +0000"
    #             values["event_datetime"] = formatted_time
    #         except (ValueError, TypeError):
    #             raise ValueError("Invalid event_datetime value. Must be a valid Unix timestamp.")
    #     return values


class SSLCertificateRequest(BaseModel):
    hostname: str
    port: int = 443


class DeviceConfigurationPayload(BaseModel):
    device_type: str
