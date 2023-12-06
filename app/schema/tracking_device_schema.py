from typing import Union

from pydantic import BaseModel


class TrackingDeviceCreate(BaseModel):
    data: Union[str, list, dict]
