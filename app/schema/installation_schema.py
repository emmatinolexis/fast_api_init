from uuid import UUID

from pydantic import BaseModel


class InstallationPayload(BaseModel):
    installer_uuid: UUID
    order_uuid: UUID
