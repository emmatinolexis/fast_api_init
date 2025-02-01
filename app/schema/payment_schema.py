from uuid import UUID

from pydantic import BaseModel

from app.util.enums import PaymentStatus, PaymentTypes


class PaymentPayload(BaseModel):
    reference_no: str
    amount: int
    status: PaymentStatus
    payment_type: PaymentTypes
    user_uuid: UUID

    class ConfigDict:
        from_attributes = True
