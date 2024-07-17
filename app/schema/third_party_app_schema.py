from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.util.enums import ActiveStatus


class ThirdPartyAppPayload(BaseModel):
    app_name: str
    status: ActiveStatus = ActiveStatus.ACTIVE


class ThirdPartyAppUserPayload(BaseModel):
    first_name: str
    last_name: str
    password: str
    email: EmailStr
    phone_number: str
    third_party_app_uuid: UUID
    status: ActiveStatus = ActiveStatus.ACTIVE
