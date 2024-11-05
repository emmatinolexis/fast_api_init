from typing import Optional

from pydantic import BaseModel


class CreateNotificationSchema(BaseModel):
    title: str
    message: str
    user_id: str
    business_profile_uuid: Optional[str] = None
