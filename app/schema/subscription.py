from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.util.enums import ActiveStatus, SubscriptionPeriod, SubscriptionTypes


class SubscriptionPayload(BaseModel):
    subscription_type: SubscriptionTypes
    subscription_period: SubscriptionPeriod
    start_date: date
    end_date: date
    subscription_amount: int
    user_uuid: UUID
    package_uuid: UUID
    status: ActiveStatus


class PaystackSubscriptionPayload(BaseModel):
    plan: str
    email: EmailStr
    amount: float
    callback_url: Optional[str]

    class ConfigDict:
        from_attributes = True


class UpdateUserSubscriptionPayload(BaseModel):
    business_uuid: Optional[UUID] = None
    user_uuid: UUID
    package_uuid: UUID
    payment_uuid: Optional[UUID] = None
    subscription_period: SubscriptionPeriod
    subscription_type: SubscriptionTypes
    start_date: date
    end_date: date

    class ConfigDict:
        from_attributes = True
