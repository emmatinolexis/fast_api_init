from pydantic import BaseModel
from uuid import UUID
from datetime import date, time

class InstallationPayload(BaseModel):
    order_uuid: UUID
    date_of_installation: date
    time_of_installation: time
