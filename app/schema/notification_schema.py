from pydantic import BaseModel
from typing import Optional





class CreateNotificationSchema(BaseModel):
    title: str
    message: str
    user_id: str
    business_profile_uuid: Optional[str] = None
   