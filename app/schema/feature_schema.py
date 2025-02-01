from pydantic import BaseModel

from app.util.enums import ActiveStatus


class FeaturePayload(BaseModel):
    feature_name: str
    feature_description: str
    icon_url: str
    status: ActiveStatus

    class ConfigDict:
        from_attributes = True
