from typing import Optional
from app.util.enums import NotificationType

from pydantic import BaseModel
from typing import Optional
from app.util.enums import NotificationType





class CreateNotificationSchema(BaseModel):
    title: str
    message: str
    user_id: str
    business_profile_uuid: Optional[str] = None


class CreateAdminNotification(BaseModel):
    notification_type: NotificationType 
    title: str
    message: str
    user_id: str

   
