from datetime import datetime, timezone
from typing import List, Union

from pydantic import BaseModel, root_validator


class TrackingDeviceCreate(BaseModel):
    data: Union[str, dict]


class MeasurementPayload(BaseModel):
    quantity: str
    value: str
    type: str
    unit: str


class DeviceReportPayload(BaseModel):
    node_id: str
    node_description: str
    master_id: str
    alert_type: str
    device_type: str
    requires_attention: bool = False
    alert_description: str
    measurements: List[MeasurementPayload]
    event_datetime: str

    @root_validator(pre=True)
    def convert_timestamp(cls, values):
        # Convert the timestamp string to a datetime object in the desired format
        if "event_datetime" in values:
            unix_timestamp = float(values["event_datetime"])
            dt = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
            # Format to '2024-07-23 11:02:21.573 +0000'
            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + " +0000"
            values["event_datetime"] = formatted_time
        return values


class SSLCertificateRequest(BaseModel):
    hostname: str
    port: int = 443


class DeviceConfigurationPayload(BaseModel):
    device_type: str
