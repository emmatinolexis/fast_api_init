from uuid import UUID

from pydantic import BaseModel


class SubscriptionPaymentPayload(BaseModel):
    subscription_uuid: UUID
    payment_uuid: UUID
    user_uuid: UUID

    class ConfigDict:
        from_attributes = True
