from typing import Optional
from pydantic import BaseModel


class SettingPayload(BaseModel):
    primary_colour: str
    secondary_colour: Optional[str]
    button_colour: Optional[str]
    logo_url: str

    class ConfigDict:
        from_attributes = True
