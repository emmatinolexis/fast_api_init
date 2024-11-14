from typing import Optional

from pydantic import BaseModel

from app.util.enums import ActivityLogClass, ActivityLogType


class ActivityLogSchema(BaseModel):
    user_uuid: str
    business_profile_uuid: Optional[str] = None
    activity_title: str
    activity_class: ActivityLogClass
    activity_type: ActivityLogType
    activity_description: str
    ip_address: str
