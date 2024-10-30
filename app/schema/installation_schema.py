from pydantic import BaseModel
from uuid import UUID


class InstallationPayload(BaseModel):
    installer_uuid: UUID
    order_uuid: UUID

